# ai-generated: 95% - drafted by Copilot to verify DORA metric rules and ticket event streaming
import json
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from svcdesk.dora import calculate_metrics
from svcdesk.main import app


client = TestClient(app)
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WINDOW = {
    "from": "2026-09-01T00:00:00Z",
    "to": "2026-09-22T00:00:00Z",
}


def practice_payload() -> dict[str, object]:
    fixture = REPOSITORY_ROOT / "fixtures" / "events-practice.jsonl"
    events = [json.loads(line) for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"window": WINDOW, "events": events}


def test_practice_fixture_matches_published_metrics() -> None:
    expected_path = REPOSITORY_ROOT / "fixtures" / "metrics-practice.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert calculate_metrics(practice_payload()) == expected


def test_root_metrics_file_matches_the_published_fixture() -> None:
    fixture_metrics = json.loads(
        (REPOSITORY_ROOT / "fixtures" / "metrics-practice.json").read_text(encoding="utf-8")
    )
    root_metrics = json.loads(
        (REPOSITORY_ROOT / "metrics.json").read_text(encoding="utf-8")
    )
    assert root_metrics == fixture_metrics


def test_metrics_are_order_independent_and_deduplicate_event_ids() -> None:
    payload = practice_payload()
    expected = calculate_metrics(payload)
    reversed_payload = {"window": WINDOW, "events": list(reversed(payload["events"]))}
    duplicated_payload = {
        "window": WINDOW,
        "events": payload["events"] + payload["events"],
    }
    assert calculate_metrics(reversed_payload) == expected
    assert calculate_metrics(duplicated_payload) == expected


def test_empty_log_returns_zero_counts_and_null_rates_and_medians() -> None:
    result = calculate_metrics({"window": WINDOW, "events": []})
    assert result["deployment_frequency_per_day"] == 0.0
    assert result["change_lead_time_seconds_p50"] is None
    assert result["failed_deployment_recovery_time_seconds_p50"] is None
    assert result["change_fail_rate"] is None
    assert result["deployment_rework_rate"] is None
    assert all(value == 0 for section in ("counts", "anomalies") for value in result[section].values())


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"events": []},
        {"window": WINDOW},
        {"window": WINDOW, "events": {}},
        {"window": {"from": WINDOW["to"], "to": WINDOW["from"]}, "events": []},
        {
            "window": WINDOW,
            "events": [
                {
                    "event_id": "c-1",
                    "type": "commit",
                    "at": "2026-09-01T00:00:00Z",
                    "sha": "sha-1",
                    "branch": "main",
                    "change_id": None,
                    "reverts": "missing-sha",
                }
            ],
        },
    ],
)
def test_invalid_metrics_requests_are_rejected_with_top_level_error(payload: object) -> None:
    response = client.post("/dora/metrics", json=payload)
    assert response.status_code in {400, 422}
    assert "error" in response.json()


def test_dora_metrics_endpoint_returns_published_fixture() -> None:
    response = client.post("/dora/metrics", json=practice_payload())
    assert response.status_code == 200
    assert response.json() == json.loads(
        (REPOSITORY_ROOT / "fixtures" / "metrics-practice.json").read_text(encoding="utf-8")
    )


def test_ticket_event_stream_contains_lifecycle_timestamps_in_order() -> None:
    create = client.post(
        "/tickets",
        json={
            "title": "DORA stream integration test",
            "reporter": {"name": "Test"},
            "impact": 1,
            "urgency": 1,
        },
        headers={"X-Test-Clock": "2026-10-20T10:00:00Z"},
    )
    assert create.status_code == 201
    ticket_id = create.json()["id"]
    for action, at in (
        ("ack", "2026-10-20T10:01:00Z"),
        ("start", "2026-10-20T10:02:00Z"),
        ("resolve", "2026-10-20T10:03:00Z"),
    ):
        response = client.post(
            f"/tickets/{ticket_id}/{action}",
            headers={"X-Test-Clock": at},
        )
        assert response.status_code == 200

    events_response = client.get("/dora/ticket-events")
    assert events_response.status_code == 200
    events = events_response.json()
    ticket_events = [event for event in events if event["ticket_id"] == ticket_id]
    assert [event["phase"] for event in ticket_events] == [
        "created",
        "acknowledged",
        "resolved",
    ]
    assert [event["state"] for event in ticket_events] == [
        "new",
        "acknowledged",
        "resolved",
    ]
    assert all(event["priority"] == "P1" for event in ticket_events)
    sort_keys = [
        (datetime.fromisoformat(event["at"].replace("Z", "+00:00")), event["ticket_id"])
        for event in events
    ]
    assert sort_keys == sorted(sort_keys)
