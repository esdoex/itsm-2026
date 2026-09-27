<!-- ai-generated: 100% - created by Copilot for the svcdesk ticketing API planning research -->
# Research: svcdesk ticketing API

## Decision: Use a single REST-style service with explicit ticket lifecycle states

**Rationale:**
The service behavior described in the feature specification centers on intake, triage, and resolution. A REST-style service exposes a clear contract for create, read, and update operations and matches the repository's FastAPI/uvicorn service pattern and Docker Compose runtime.

**Alternatives considered:**
- A CLI-only workflow: rejected because the project and lab contract require a service API exposed over HTTP.
- A highly event-driven design: rejected because the feature scope is a small lifecycle system and the added orchestration would make the first version harder to validate.
- A fully database-centric design without a contract layer: rejected because the repository's initial service goal is a clear, testable API contract rather than deep persistence complexity.

## Decision: Use explicit ticket states for lifecycle management

**Rationale:**
The specification requires status tracking, triage, update history, and resolution. An explicit state model makes the service easier to validate, reduces ambiguity, and preserves auditability.

**Alternatives considered:**
- Free-text status labels only: rejected because it creates inconsistent transitions and weak enforcement.
- A hidden internal status model: rejected because operational visibility and audit requirements require states to be explicit and user-visible.

## Decision: Keep the first version single-service and single-queue

**Rationale:**
The v1 scope is limited to ticket creation, triage, and resolution. Keeping a single queue and single ticket model supports rapid validation and aligns with the service's core user value.

**Alternatives considered:**
- Multi-tenant or multi-team queue design: rejected for v1 because it introduces permissions and routing complexity not required by the specification.
- Separate analytics or alerting modules: rejected because they are out of scope and would distract from the core lifecycle flow.

## Decision: Validate through HTTP contract and lifecycle tests

**Rationale:**
The service must prove user value through measurable outcomes and testable acceptance scenarios. HTTP contract checks and integration-style validation are the most direct way to confirm create, read, update, and close flows.

**Alternatives considered:**
- UI-only validation: rejected because the project is an API/service contract and not a UI product.
- Pure unit-only validation: rejected because the core requirement is end-to-end behavior across ticket lifecycles.
