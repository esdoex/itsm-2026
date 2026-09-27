<!-- ai-generated: 100% - created by Copilot for the svcdesk ticketing API tasks -->
# Tasks: svcdesk ticketing API

**Input**: Design documents from `/specs/001-svcdesk-ticketing-api/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and service foundation for the ticketing API.

- [ ] T001 Create service structure under src/app, src/tests, and the feature contract folders in `src/app/api/`, `src/app/models/`, `src/app/services/`, and `src/tests/contract/`
- [ ] T002 [P] Initialize the Python HTTP service entrypoint and package wiring in `src/app/main.py` and `src/app/__init__.py`
- [ ] T003 [P] Configure core app dependencies and environment settings for the Docker Compose service in `src/app/config.py` and the repository runtime configuration files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure that MUST be complete before user story implementation.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

- [ ] T004 Define the `Ticket` data model and constraints in `src/app/models/ticket.py` with required fields `title`, `description`, `category`, `urgency`, `status`, `created_at`, and `updated_at`, and required validation for non-empty title and description
- [ ] T005 [P] Define request and response schemas for ticket create and update flow in `src/app/models/schemas.py`, including valid urgency values and explicit state transitions
- [ ] T006 [P] Implement the in-memory ticket repository and id generation logic in `src/app/services/ticket_repository.py` with support for create, list, get-by-id, and patch operations
- [ ] T007 Implement ticket state validation and transition rules in `src/app/services/ticket_service.py` so only valid transitions are accepted and resolution notes are required before final close
- [ ] T008 Create shared API error handling and validation responses in `src/app/api/errors.py` and `src/app/api/dependencies.py` for 400, 404, 409, and 500 cases
- [ ] T009 [P] Wire the service router and endpoint registration in `src/app/api/router.py` so create, list, read, and patch flows are mounted under the HTTP contract

---

## Phase 3: User Story 1 - Submit a service request (Priority: P1) 🎯 MVP

**Goal**: Allow requesters to submit valid service tickets and receive a confirmation with a unique identifier and initial status.

**Independent Test**: Verify a valid submission creates a ticket, stores the required metadata, and returns a success response with a ticket id and initial status.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement ticket creation endpoint in `src/app/api/tickets.py` for `POST /tickets` using the contract in `specs/001-svcdesk-ticketing-api/contracts/ticket-api.md`
- [ ] T011 [P] [US1] Add request validation for required fields and invalid payload handling in `src/app/api/tickets.py` so missing title, description, category, or urgency produce a clear validation error
- [ ] T012 [US1] Add create flow orchestration in `src/app/services/ticket_service.py` to assign a unique identifier, initial status `new`, and timestamps on valid requests
- [ ] T013 [US1] Persist and return the created ticket record in `src/app/services/ticket_repository.py` with the fields required by the contract and historical metadata
- [ ] T014 [US1] Add logging and response details for successful creation in `src/app/api/tickets.py` and `src/app/services/ticket_service.py` to keep the operation observable and auditable

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Review and triage incoming work (Priority: P1)

**Goal**: Allow staff to retrieve the active queue with ticket priority, status, and category so triage can begin quickly.

**Independent Test**: Verify the operator can list active tickets and fetch a single ticket to assess state and ownership without manual data export.

### Implementation for User Story 2

- [ ] T015 [P] [US2] Implement list endpoint in `src/app/api/tickets.py` for `GET /tickets` so all active tickets can be retrieved in a triage-friendly format
- [ ] T016 [P] [US2] Implement single-ticket lookup in `src/app/api/tickets.py` for `GET /tickets/{ticket_id}` and return a clear not-found error when the record is absent
- [ ] T017 [US2] Add queue and entity filtering logic in `src/app/services/ticket_service.py` to support status, category, and urgency-based review while preserving the core lifecycle data
- [ ] T018 [US2] Update the repository query layer in `src/app/services/ticket_repository.py` to expose list and lookup operations consistent with the contract output fields
- [ ] T019 [US2] Add operator-visible response metadata in `src/app/api/tickets.py` so the ticket payload includes id, status, urgency, category, and essential audit fields

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Resolve a ticket and close the loop (Priority: P2)

**Goal**: Allow service desk operators to update ticket state and record the final resolution while retaining the full change history.

**Independent Test**: Verify a ticket can move from active work to a resolved or closed state with notes retained and prior updates preserved.

### Implementation for User Story 3

- [ ] T020 [P] [US3] Implement patch endpoint in `src/app/api/tickets.py` for `PATCH /tickets/{ticket_id}` with support for status, assignee, and note updates
- [ ] T021 [US3] Add status transition enforcement and final-resolution validation in `src/app/services/ticket_service.py` so `resolved` and `closed` states cannot be reached without final notes and valid transition rules
- [ ] T022 [US3] Record ticket update history in `src/app/services/ticket_repository.py` and tie each patch event to the relevant ticket record, preserving previous values and timestamps
- [ ] T023 [US3] Add business-rule handling for invalid transitions and missing tickets in `src/app/api/errors.py` and `src/app/services/ticket_service.py` to return clear 400 and 404 responses
- [ ] T024 [US3] Ensure final ticket records retain resolution notes and audit information in `src/app/models/ticket.py` and `src/app/services/ticket_repository.py` for later reporting and operator review

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full feature and align the service with the quickstart validation guide.

- [ ] T025 [P] Run the ticket lifecycle validation flows from `specs/001-svcdesk-ticketing-api/quickstart.md` against the local service in Docker Compose and confirm create, list, update, resolve, and error scenarios behave as expected
- [ ] T026 [P] Review contract coverage against `specs/001-svcdesk-ticketing-api/contracts/ticket-api.md` and ensure response and error shapes match the agreed contract
- [ ] T027 [P] Add final documentation and comment updates to `src/README.md` or feature-local docs only where they clarify how the service is intended to run and validate
- [ ] T028 Clean up repository structure, confirm import paths, and ensure all new application code is organized under `src/app/` using the service plan from `specs/001-svcdesk-ticketing-api/plan.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 depends on no previous work.
- Phase 2 depends on Phase 1 completion and blocks all user stories.
- Phase 3 depends on Phase 2 completion.
- Phase 4 depends on Phase 2 completion and can run in parallel with Phase 3 if staffing allows.
- Phase 5 depends on Phase 2 completion and should follow the core triage flow after the first two stories are valid.
- Phase 6 depends on completion of all desired stories and contract validation.

### User Story Dependencies

- User Story 1 (P1): depends on foundational setup and can operate independently.
- User Story 2 (P1): depends on the same foundation and should be independently testable once the queue logic is in place.
- User Story 3 (P2): depends on foundational setup and should be capable of running independently after the service lifecycle rules are implemented.

### Parallel Opportunities

- T002, T003, T005, T006, T009 can run in parallel after setup begins.
- T010, T011, T012, T013, T014 are parallelizable within User Story 1 when different modules are being authored.
- T015, T016, T017, T018, T019 are parallelizable within User Story 2.
- T020, T021, T022, T023, T024 are parallelizable within User Story 3.
- Final validation tasks in Phase 6 can run in parallel once user story work is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Implement User Story 1 end-to-end.
3. Validate create-request flow and confirmation output.
4. Stop and confirm the ticket creation experience is stable before moving to triage or closure work.

### Incremental Delivery

1. Deliver ticket intake and confirmation flow.
2. Add queue and ticket lookup so operators can triage work.
3. Add update and resolution flow so the service desk can close work with proper notes.
4. Validate the entire ticket lifecycle against the spec and contract before final cleanup.
