# ai-generated: 95% - implemented by Copilot from METRIC-SPEC.md rules R-01 through R-18
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import TypeAlias


RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
JsonObject: TypeAlias = dict[str, object]


@dataclass(frozen=True)
class Commit:
    event_id: str
    at: datetime
    sha: str
    branch: str
    change_id: str | None
    reverts: str | None


@dataclass(frozen=True)
class Deployment:
    event_id: str
    at: datetime
    deployment_id: str
    environment: str
    outcome: str
    commits: tuple[str, ...]
    unplanned: bool
    caused_by: str | None


@dataclass(frozen=True)
class Incident:
    event_id: str
    at: datetime
    incident_id: str
    phase: str
    deployments: tuple[str, ...]


Event: TypeAlias = Commit | Deployment | Incident


def _fail(message: str) -> ValueError:
    return ValueError(message)


def _object(value: object, name: str) -> JsonObject:
    if not isinstance(value, dict):
        raise _fail(f"{name} must be an object")
    return value


def _string(value: object, name: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value:
        raise _fail(f"{name} must be a non-empty string")
    return value


def _instant(value: object, name: str) -> datetime:
    raw = _string(value, name)
    assert raw is not None
    if RFC3339.fullmatch(raw) is None:
        raise _fail(f"{name} must be an RFC 3339 instant with an offset")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _fail(f"{name} must be a valid RFC 3339 instant") from exc
    if parsed.tzinfo is None:
        raise _fail(f"{name} must include a timezone offset")
    return parsed.astimezone(timezone.utc)


def _string_list(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise _fail(f"{name} must be an array")
    result: list[str] = []
    for item in value:
        parsed = _string(item, name)
        assert parsed is not None
        result.append(parsed)
    return tuple(result)


def _required(data: JsonObject, name: str) -> object:
    if name not in data:
        raise _fail(f"{name} is required")
    return data[name]


def _parse_event(raw: object) -> Event:
    data = _object(raw, "event")
    event_id = _string(data.get("event_id"), "event_id")
    event_type = _string(data.get("type"), "type")
    at = _instant(data.get("at"), "at")
    assert event_id is not None and event_type is not None
    if len(event_id) > 64:
        raise _fail("event_id must be at most 64 characters")

    if event_type == "commit":
        sha = _string(data.get("sha"), "sha")
        branch = data.get("branch")
        if not isinstance(branch, str):
            raise _fail("branch must be a string")
        change_id = _string(_required(data, "change_id"), "change_id", nullable=True)
        reverts = _string(_required(data, "reverts"), "reverts", nullable=True)
        if (reverts is None) != (change_id is not None):
            raise _fail("change_id must be present exactly when reverts is null")
        assert sha is not None
        return Commit(event_id, at, sha, branch, change_id, reverts)

    if event_type == "deployment":
        deployment_id = _string(data.get("deployment_id"), "deployment_id")
        environment = _string(data.get("environment"), "environment")
        outcome = _string(data.get("outcome"), "outcome")
        commits = _string_list(data.get("commits"), "commits")
        unplanned = data.get("unplanned")
        caused_by = _string(_required(data, "caused_by"), "caused_by", nullable=True)
        if outcome not in {"success", "failure"}:
            raise _fail("outcome must be success or failure")
        if not isinstance(unplanned, bool):
            raise _fail("unplanned must be a boolean")
        assert deployment_id is not None and environment is not None and outcome is not None
        return Deployment(
            event_id, at, deployment_id, environment, outcome, commits, unplanned, caused_by
        )

    if event_type == "incident":
        incident_id = _string(data.get("incident_id"), "incident_id")
        phase = _string(data.get("phase"), "phase")
        deployments = _string_list(data.get("deployments"), "deployments")
        if phase not in {"opened", "resolved"}:
            raise _fail("phase must be opened or resolved")
        assert incident_id is not None and phase is not None
        return Incident(event_id, at, incident_id, phase, deployments)

    raise _fail("type must be commit, deployment, or incident")


def _deduplicate_events(raw_events: list[object]) -> list[Event]:
    events: list[Event] = []
    seen_ids: set[str] = set()
    for raw in raw_events:
        data = _object(raw, "event")
        event_id = _string(data.get("event_id"), "event_id")
        assert event_id is not None
        if len(event_id) > 64:
            raise _fail("event_id must be at most 64 characters")
        if event_id in seen_ids:
            continue
        seen_ids.add(event_id)
        events.append(_parse_event(data))
    return events


def _validate_log(events: list[Event]) -> dict[str, Commit]:
    commits: dict[str, Commit] = {}
    deployments: dict[str, Deployment] = {}
    incident_phases: dict[str, dict[str, Incident]] = {}

    for event in events:
        if isinstance(event, Commit):
            if event.sha in commits:
                raise _fail(f"duplicate commit sha: {event.sha}")
            commits[event.sha] = event
        elif isinstance(event, Deployment):
            if event.deployment_id in deployments:
                raise _fail(f"duplicate deployment_id: {event.deployment_id}")
            deployments[event.deployment_id] = event
        else:
            phases = incident_phases.setdefault(event.incident_id, {})
            if event.phase in phases:
                raise _fail(f"duplicate {event.phase} event for incident {event.incident_id}")
            phases[event.phase] = event

    for commit in commits.values():
        if commit.reverts is not None and commit.reverts not in commits:
            raise _fail(f"reverts references unknown sha: {commit.reverts}")
    for deployment in deployments.values():
        if any(sha not in commits for sha in deployment.commits):
            raise _fail("deployment commits references an unknown sha")
        if deployment.caused_by is not None and deployment.caused_by not in incident_phases:
            raise _fail(f"caused_by references unknown incident: {deployment.caused_by}")
    for incident_id, phases in incident_phases.items():
        if "resolved" in phases and "opened" not in phases:
            raise _fail(f"resolved incident {incident_id} has no opened event")
        for incident in phases.values():
            if any(deployment_id not in deployments for deployment_id in incident.deployments):
                raise _fail("incident deployments references an unknown deployment_id")

    return commits


def _round_half_up(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _seconds(delta: timedelta) -> Decimal:
    return (
        Decimal(delta.days * 86400 + delta.seconds)
        + Decimal(delta.microseconds) / Decimal(1_000_000)
    )


def _duration(start: datetime, end: datetime) -> tuple[Decimal, bool]:
    value = _seconds(end - start)
    return (Decimal(0), True) if value < 0 else (value, False)


def _median(values: list[Decimal]) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        value = ordered[middle]
    else:
        value = (ordered[middle - 1] + ordered[middle]) / Decimal(2)
    return _round_half_up(value)


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    value = (Decimal(numerator) / Decimal(denominator)).quantize(
        Decimal("0.000001"), rounding=ROUND_HALF_UP
    )
    return float(value)


def calculate_metrics(payload: object) -> dict[str, object]:
    body = _object(payload, "request body")
    window = _object(body.get("window"), "window")
    window_from_raw = _string(window.get("from"), "window.from")
    window_to_raw = _string(window.get("to"), "window.to")
    assert window_from_raw is not None and window_to_raw is not None
    window_from = _instant(window_from_raw, "window.from")
    window_to = _instant(window_to_raw, "window.to")
    if window_to <= window_from:
        raise _fail("window.to must be after window.from")

    raw_events = body.get("events")
    if not isinstance(raw_events, list):
        raise _fail("events must be an array")
    events = _deduplicate_events(raw_events)
    commits = _validate_log(events)

    changes_by_sha: dict[str, str] = {}
    resolving: set[str] = set()

    def resolve_change(sha: str) -> str:
        if sha in changes_by_sha:
            return changes_by_sha[sha]
        if sha in resolving:
            raise _fail("revert chain contains a cycle")
        resolving.add(sha)
        commit = commits[sha]
        change_id = commit.change_id if commit.reverts is None else resolve_change(commit.reverts)
        assert change_id is not None
        resolving.remove(sha)
        changes_by_sha[sha] = change_id
        return change_id

    for sha in commits:
        resolve_change(sha)

    production_window = sorted(
        (
            event
            for event in events
            if isinstance(event, Deployment)
            and event.environment == "production"
            and window_from <= event.at < window_to
        ),
        key=lambda deployment: (deployment.at, deployment.deployment_id.encode("utf-8")),
    )
    incidents: dict[str, dict[str, Incident]] = {}
    for event in events:
        if isinstance(event, Incident):
            incidents.setdefault(event.incident_id, {})[event.phase] = event

    lead_times: list[Decimal] = []
    seen_successful_shas: set[str] = set()
    negative_lead_pairs = 0
    deployments_without_commits = 0
    successful_deployments = 0
    failed_deployments = 0
    recovered_failures = 0
    open_failures = 0
    recovery_times: list[Decimal] = []
    rework_deployments = 0
    delivered_change_times: dict[str, datetime] = {}
    first_commit_by_change: dict[str, datetime] = {}

    for sha, commit in commits.items():
        change_id = changes_by_sha[sha]
        current_first = first_commit_by_change.get(change_id)
        if current_first is None or commit.at < current_first:
            first_commit_by_change[change_id] = commit.at

    for deployment in production_window:
        if not deployment.commits:
            deployments_without_commits += 1
        if deployment.unplanned and deployment.caused_by is not None:
            rework_deployments += 1
        if deployment.outcome == "success":
            successful_deployments += 1
            for sha in deployment.commits:
                if sha in seen_successful_shas:
                    continue
                seen_successful_shas.add(sha)
                lead_time, was_negative = _duration(commits[sha].at, deployment.at)
                lead_times.append(lead_time)
                negative_lead_pairs += int(was_negative)
                change_id = changes_by_sha[sha]
                first_delivered = delivered_change_times.get(change_id)
                if first_delivered is None or deployment.at < first_delivered:
                    delivered_change_times[change_id] = deployment.at
        else:
            failed_deployments += 1
            covering = [
                phases
                for phases in incidents.values()
                if "opened" in phases
                and deployment.deployment_id in phases["opened"].deployments
            ]
            covering.sort(
                key=lambda phases: (
                    phases["opened"].at,
                    phases["opened"].incident_id.encode("utf-8"),
                )
            )
            if not covering or "resolved" not in covering[0]:
                open_failures += 1
            else:
                recovered_failures += 1
                recovery_time, _ = _duration(deployment.at, covering[0]["resolved"].at)
                recovery_times.append(recovery_time)

    true_change_lead_times: list[Decimal] = []
    for change_id, deployed_at in delivered_change_times.items():
        lead_time, _ = _duration(first_commit_by_change[change_id], deployed_at)
        true_change_lead_times.append(lead_time)

    overlaps = 0
    opened_incidents = [
        phases for phases in incidents.values() if "opened" in phases
    ]
    for index, left in enumerate(opened_incidents):
        left_open = left["opened"]
        left_end = left["resolved"].at if "resolved" in left else window_to
        for right in opened_incidents[index + 1:]:
            right_open = right["opened"]
            right_end = right["resolved"].at if "resolved" in right else window_to
            if left_open.at < right_end and right_open.at < left_end:
                overlaps += 1

    window_days = _seconds(window_to - window_from) / Decimal(86400)
    frequency = (Decimal(len(production_window)) / window_days).quantize(
        Decimal("0.000001"), rounding=ROUND_HALF_UP
    )
    changes = set(changes_by_sha.values())
    commits_never_on_main = {
        sha
        for deployment in production_window
        for sha in deployment.commits
        if commits[sha].branch != "main"
    }
    return {
        "spec_version": "1.0.0",
        "window": {"from": window_from_raw, "to": window_to_raw},
        "deployment_frequency_per_day": float(frequency),
        "change_lead_time_seconds_p50": _median(lead_times),
        "failed_deployment_recovery_time_seconds_p50": _median(recovery_times),
        "change_fail_rate": _ratio(failed_deployments, len(production_window)),
        "deployment_rework_rate": _ratio(rework_deployments, len(production_window)),
        "counts": {
            "deployments": len(production_window),
            "successful_deployments": successful_deployments,
            "failed_deployments": failed_deployments,
            "recovered_failures": recovered_failures,
            "open_failures": open_failures,
            "rework_deployments": rework_deployments,
            "lead_time_pairs": len(lead_times),
            "changes": len(changes),
        },
        "anomalies": {
            "negative_lead_time_pairs": negative_lead_pairs,
            "deployments_without_commits": deployments_without_commits,
            "commits_never_on_main": len(commits_never_on_main),
            "revert_chains_collapsed": sum(
                commit.reverts is not None for commit in commits.values()
            ),
            "overlapping_incident_pairs": overlaps,
        },
        "ground_truth": {
            "changes_delivered": len(delivered_change_times),
            "true_change_lead_time_seconds_p50": _median(true_change_lead_times),
        },
    }
