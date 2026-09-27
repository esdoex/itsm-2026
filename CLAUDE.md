# Claude agent instructions

This repository is for the svcdesk ticketing service in Lab 1.

## Operating rules

- Follow the published API contract and business decisions in `DECISIONS.md`.
- Keep changes focused on the service, tests, and required lab artifacts.
- Maintain deterministic, test-backed behavior.
- Do not add unrelated features or broad refactors.
- Prefer targeted validation and avoid unapproved network access.

## Required compliance notes

- The service must continue to satisfy the contract in `API.md` and `REQUIREMENTS.md`.
- The agent policy is documented in `AGENT-POLICY.md`.
- The convergence report is kept in `CONVERGE.md`.
- The repository uses a Docker Compose service named `svcdesk` and an optional `tests` profile for local validation.
