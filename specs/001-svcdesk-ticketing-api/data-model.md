<!-- ai-generated: 100% - created by Copilot for the svcdesk ticketing API data model -->
# Data Model: svcdesk ticketing API

## Core entities

### Ticket

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique ticket identifier | Required, immutable, unique |
| title | string | Short summary of the issue | Required, 1-200 characters |
| description | string | Full problem description | Required, non-empty |
| category | string | Request type or functional area | Required, known category value |
| urgency | string | Priority classification | Required, enum-like value such as low, medium, high, urgent |
| status | string | Lifecycle state of the ticket | Required, valid state transition |
| requester_id | string | Reference to the submitting user or system | Required |
| assignee_id | string | Operator assigned to handle the issue | Optional |
| created_at | datetime | Time the ticket was first created | Required |
| updated_at | datetime | Time of the most recent update | Required |
| resolved_at | datetime | Time the ticket was resolved or closed | Optional |
| resolution_notes | string | Summary of the final outcome | Optional |

### Requester

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique identifier for the requester | Required |
| name | string | Requester display name | Optional |
| email | string | Contact address for follow-up | Optional, valid format when provided |
| contact_preferences | string | Preferred follow-up method | Optional |

### Operator

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Unique operator identifier | Required |
| name | string | Display name | Required |
| role | string | Job function or team assignment | Optional |

### TicketUpdate

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| id | string | Update event identifier | Required |
| ticket_id | string | Ticket the event belongs to | Required |
| actor_id | string | User or system that made the update | Required |
| change_type | string | Type of change such as status, assignee, note, priority | Required |
| previous_value | string | Previous field value before the change | Optional |
| new_value | string | New field value after the change | Optional |
| note | string | Human-readable explanation | Optional |
| created_at | datetime | Time the update was recorded | Required |

## Relationships

- A requester can submit many tickets.
- An operator can own many tickets and can update multiple ticket records.
- A ticket can have many associated TicketUpdate records.
- Each ticket has one current status and a timeline of status changes.

## State transitions

- new -> in_progress
- new -> resolved
- in_progress -> resolved
- in_progress -> blocked
- blocked -> in_progress
- resolved -> closed
- any non-terminal state may be reopened depending on operational policy

## Validation rules

- Ticket title and description must be present for a valid submission.
- Urgency must be one of the supported values.
- Status changes must follow defined transitions to avoid invalid ticket states.
- A ticket must not be updated after it is deleted or after an invalid identifier is supplied.
- Resolution notes are required before a ticket can be marked resolved or closed.
