<!-- ai-generated: 100% - created by Copilot for the svcdesk ticketing API contract -->
# Ticket API Contract

## Overview

This contract defines the core HTTP interface for the ticketing API used by requesters and service desk operators.

## Endpoints

### POST /tickets

Creates a new ticket.

**Request body**

```json
{
  "title": "Printer not working",
  "description": "The office printer is offline after reboot.",
  "category": "hardware",
  "urgency": "high",
  "requester_id": "user-123"
}
```

**Success response**

```json
{
  "id": "TCK-1001",
  "status": "new",
  "created_at": "2026-09-27T12:00:00Z",
  "updated_at": "2026-09-27T12:00:00Z"
}
```

**Error response**

```json
{
  "error": "validation_failed",
  "details": [
    "title is required",
    "description is required"
  ]
}
```

### GET /tickets

Returns the current list of tickets for operator triage.

**Success response**

```json
[
  {
    "id": "TCK-1001",
    "title": "Printer not working",
    "status": "new",
    "urgency": "high",
    "category": "hardware"
  }
]
```

### GET /tickets/{ticket_id}

Returns a single ticket with detail and metadata.

### PATCH /tickets/{ticket_id}

Updates the ticket state or metadata.

**Request body**

```json
{
  "status": "in_progress",
  "assignee_id": "ops-42",
  "note": "Engineer assigned for diagnosis"
}
```

**Success response**

```json
{
  "id": "TCK-1001",
  "status": "in_progress",
  "assignee_id": "ops-42",
  "updated_at": "2026-09-27T12:05:00Z"
}
```

### Error handling

- 400: invalid request body or invalid transition
- 404: ticket not found
- 409: status transition conflict
- 500: unexpected server error

## Contract constraints

- Ticket creation must assign a unique identifier.
- Status transitions must be explicit and valid.
- Response bodies must use consistent field names and timestamps.
- Resolution notes must be retained for closed tickets.
