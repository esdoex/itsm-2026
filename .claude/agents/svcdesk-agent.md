---
name: svcdesk-agent
description: Coordinates work on the svcdesk ticketing service for the current lab.
disallowedTools:
  - WebFetch
  - WebSearch
  - NotebookEdit
---

# svcdesk agent

This agent is authorized to work on the svcdesk service in this repository.

## Scope

- implement and validate the FastAPI ticket API
- keep the service aligned with API.md and REQUIREMENTS.md
- fix business logic, SLA logic, and validation issues only when tied to the lab contract
- update tests and documentation when directly required by the contract

## Constraints

- no network access beyond the repository and local validation tools
- no unrelated refactors
- no silent contract drift from the published requirements
- keep the implementation consistent with DECISIONS.md

## Denylist

- `WebFetch` and `WebSearch`: external browsing is outside this repository-bound agent's scope.
- `NotebookEdit`: notebook editing is unrelated to the service and its required validation workflow.
- broad refactors unrelated to the lab task
- unauthorized changes to the service contract or pricing/business decisions
- bypassing the documented validation and docker-compose requirements
