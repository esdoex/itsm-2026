# Agent policy

This repository is a controlled coding workspace for the svcdesk service. The default behavior is to follow the repository plan, preserve the verified FastAPI contract, and avoid unreviewed automation.

## Required rules

- Do not exfiltrate secrets or private data.
- Do not modify the service contract or business decisions without updating the relevant specification artifacts.
- Keep changes minimal, test-backed, and consistent with the course requirements.
- Respect the existing docker-compose and API contract for the service.
- Prefer targeted validation over broad, unrelated changes.

## Denylist

The following behaviors are not allowed:

- WebFetch: External web fetching is outside the repository-bound agent's scope.
- WebSearch: External web searches are unnecessary for this repository-only service work.
- NotebookEdit: Notebook editing is unrelated to the svcdesk API and its validation workflow.
- deleting or rewriting verified implementation history without explicit instruction
- broad refactors unrelated to the current lab task
- unapproved network egress or external service calls during build/test execution
- bypassing the documented service contract or ignoring required business rules

This policy is justified because the lab requires a deterministic service desk implementation, reproducible validation, and adherence to the published contract.
