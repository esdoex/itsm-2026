<!-- ai-generated: 100% - created by Copilot for the svcdesk ticketing API quickstart validation guide -->
# Quickstart: svcdesk ticketing API

## Prerequisites

- Docker Desktop or Docker Engine with Compose support
- Local access to port 8080
- A working clone of this repository

## Start the service

```bash
docker compose up --build
```

Expected result: the `svcdesk` service starts and is ready on port 8080.

## Validation scenarios

### 1. Health check

```bash
curl http://localhost:8080/health
```

Expected result: a successful response indicating the service is healthy and ready to accept requests.

### 2. Create a ticket

```bash
curl -X POST http://localhost:8080/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Printer not working",
    "description": "The office printer is offline after reboot.",
    "category": "hardware",
    "urgency": "high"
  }'
```

Expected result: a 2xx success response with a unique ticket identifier, initial status, and created timestamps.

### 3. Retrieve the ticket queue

```bash
curl http://localhost:8080/tickets
```

Expected result: a list of active tickets with enough data for operator triage.

### 4. Update the ticket status

```bash
curl -X PATCH http://localhost:8080/tickets/{ticket_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assignee_id": "ops-42",
    "note": "Engineer assigned for diagnosis"
  }'
```

Expected result: the ticket reflects the assignment and status change without losing its prior history.

### 5. Resolve the ticket

```bash
curl -X PATCH http://localhost:8080/tickets/{ticket_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution_notes": "Printer was restarted and connectivity restored.",
    "note": "Issue closed after validation"
  }'
```

Expected result: the ticket is resolved and retains the completion notes for audit and reporting.

## Expected end-to-end outcomes

- A valid ticket is accepted and assigned a unique ID.
- Operators can list and prioritize the queue.
- Ticket state changes are tracked over time.
- Resolved tickets retain final notes and completion context.
