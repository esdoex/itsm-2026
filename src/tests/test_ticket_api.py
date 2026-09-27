# ai-generated: 90% - contract tests for the svcdesk ticket lifecycle

from fastapi.testclient import TestClient

from svcdesk.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.json()['service'] == 'svcdesk'


def test_create_ticket_success_and_priority_matrix():
    response = client.post(
        '/tickets',
        json={
            'title': 'Printer on floor 2 is down',
            'description': 'Nobody on the floor can print.',
            'reporter': {'name': 'Anna Nowak', 'email': 'anna.nowak@example.com', 'vip': False},
            'impact': 2,
            'urgency': 1,
            'related_to': None,
        },
        headers={'X-Test-Clock': '2026-10-14T10:00:00Z'},
    )
    assert response.status_code == 201
    body = response.json()
    assert body['priority'] == 'P2'
    assert body['state'] == 'new'
    assert body['created_at'] == '2026-10-14T10:00:00+00:00'
    assert body['sla']['ack_due_at'] == '2026-10-14T11:00:00+00:00'
    assert body['sla']['resolve_due_at'] == '2026-10-15T10:00:00+00:00'


def test_unknown_ticket_and_route():
    assert client.get('/tickets/does-not-exist-9f3c').status_code == 404
    assert client.get('/this-route-does-not-exist-9f3c').status_code == 404


def test_validation_errors():
    bad = client.post('/tickets', json={'reporter': {'name': 'A'}, 'impact': 5, 'urgency': 1})
    assert bad.status_code == 422
    body = bad.json()
    assert 'error' in body


def test_list_filters_and_acks():
    create_p1 = client.post(
        '/tickets',
        json={
            'title': 'Critical outage',
            'reporter': {'name': 'Ops', 'vip': False},
            'impact': 1,
            'urgency': 1,
        },
        headers={'X-Test-Clock': '2026-10-14T10:00:00Z'},
    )
    p1_id = create_p1.json()['id']
    create_p4 = client.post(
        '/tickets',
        json={
            'title': 'Cosmetic issue',
            'reporter': {'name': 'User', 'vip': False},
            'impact': 3,
            'urgency': 3,
        },
        headers={'X-Test-Clock': '2026-10-14T10:00:00Z'},
    )
    p4_id = create_p4.json()['id']
    listing = client.get('/tickets?priority=P1')
    ids = [t['id'] for t in listing.json()]
    assert p1_id in ids and p4_id not in ids

    ack = client.post(f'/tickets/{p1_id}/ack', headers={'X-Test-Clock': '2026-10-14T10:05:00Z'})
    assert ack.status_code == 200
    assert ack.json()['state'] == 'acknowledged'

    start = client.post(f'/tickets/{p1_id}/start', headers={'X-Test-Clock': '2026-10-14T10:10:00Z'})
    assert start.status_code == 200
    assert start.json()['state'] == 'in_progress'

    resolve = client.post(f'/tickets/{p1_id}/resolve', headers={'X-Test-Clock': '2026-10-14T11:00:00Z'})
    assert resolve.status_code == 200
    assert resolve.json()['state'] == 'resolved'

    close = client.post(f'/tickets/{p1_id}/close', headers={'X-Test-Clock': '2026-10-14T12:00:00Z'})
    assert close.status_code == 200
    assert close.json()['state'] == 'closed'


def test_sla_and_vip_and_reopen_rules():
    vip = client.post(
        '/tickets',
        json={
            'title': 'VIP issue',
            'reporter': {'name': 'Executive', 'vip': True},
            'impact': 3,
            'urgency': 3,
        },
        headers={'X-Test-Clock': '2026-10-14T10:00:00Z'},
    )
    assert vip.status_code == 201
    assert vip.json()['priority'] == 'P2'

    ticket = client.post(
        '/tickets',
        json={
            'title': 'Late ack',
            'reporter': {'name': 'Alice', 'vip': False},
            'impact': 3,
            'urgency': 1,
        },
        headers={'X-Test-Clock': '2026-10-16T13:30:00Z'},
    )
    ticket_id = ticket.json()['id']
    sla = client.get(f'/tickets/{ticket_id}/sla', headers={'X-Test-Clock': '2026-10-19T09:31:00Z'})
    assert sla.status_code == 200
    payload = sla.json()
    assert payload['ack_breached'] is True
    assert payload['paused'] is False

    reopen = client.post(f'/tickets/{ticket_id}/reopen', headers={'X-Test-Clock': '2026-10-17T10:00:00Z'})
    assert reopen.status_code == 409
