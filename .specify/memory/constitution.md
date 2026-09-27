<!--
Sync Impact Report:
- Version change: 0.1.0 -> 1.0.0
- Modified principles: initial constitution draft from template into project-specific governance
- Added sections: none (section structure preserved)
- Removed sections: none
- Deferred items: RATIFICATION_DATE unresolved; use TODO(RATIFICATION_DATE): original adoption date not recorded in repo; set at first formal approval
-->

# svcdesk Constitution

## Core Principles

### I. Service-First Delivery
Every change must deliver a clear, user-visible capability for the svcdesk service or improve an existing contract without altering the service's purpose. A feature is not complete until its behavior is observable through the service interface, documentation, or a defined operational contract, and no undocumented behavior is accepted as part of the runtime.

Rationale: A service that cannot clearly state what it does and how it behaves creates drift between implementation and operator expectations. Explicit contracts make change safe, testable, and explainable.

### II. Evidence-Driven Change
All non-trivial changes must be validated before merge with the smallest relevant automated test, reproducible verification, or published checker run. A change cannot be considered complete when the required proof is missing, and bug fixes must include evidence that the previously failing behavior is resolved.

Rationale: In a service environment, unverified changes become production risk. Proof-based delivery turns assumptions into measurable outcomes and prevents silent regressions.

### III. Secure and Minimal Design
The service must minimize its attack surface, validate all external inputs, avoid hard-coded secrets, and keep configuration in explicit environment variables or approved configuration files. No sensitive personal or operational data may be committed to the repository, and code must favor the smallest necessary implementation over broad abstractions.

Rationale: Security and simplicity are enablers of maintainability. A small, validated surface is easier to audit, deploy, and reason about under operational pressure.

### IV. Contract Stability and Compatibility
Public interfaces, request/response schemas, and operational assumptions must be explicit and backward compatible unless a major version is declared. Breaking changes require a migration note, a compatibility statement, and clear communication to consumers before release.

Rationale: Service consumers depend on stable expectations. Compatibility protects both runtime reliability and the team's ability to evolve the product without hidden breakage.

### V. Operational Clarity and Observability
The service must expose enough runtime information for operators to determine health, identify failure, and diagnose problems without reading unexplained implementation details. Errors, logs, and status outputs must be structured, actionable, and consistent with the service's documented behavior.

Rationale: A system is only as reliable as its ability to explain itself during failure. Operational clarity reduces incident time and improves trust in the product.

## Additional Requirements

The repository must remain aligned with the course lab contract: the service is expected to run through Docker Compose or the project-defined entrypoint, maintain a public repository with no personal data, and keep configuration and generated artifacts out of version control unless explicitly required by the project.

Implementation decisions must be recorded in the project's decision artifact and supported by versioned specifications when behavior changes. The checklist is not optional: the team must keep specs, implementation, and operational evidence consistent.

## Development Workflow

The project must follow a review-first workflow: each change is tied to a requirement or issue, validated with the appropriate tests or checker evidence, and reviewed before merge. The project maintains a single source of truth for intent through specification and decision artifacts; implementation details that materially affect behavior must be reflected there.

Rationale: Governance is effective only when it is enforced throughout the lifecycle. Review and evidence reduce drift between request, implementation, and runtime behavior.

## Governance

This Constitution supersedes ad hoc practices and defines the minimum standards for service development in this repository. Any proposal to change behavior, tooling, or review requirements must be documented, discussed, and explicitly approved before it is applied to the project.

Amendments must preserve the project-specific intent of this constitution while updating the governing rules or principles. Each amendment requires a version bump, a summary of the changes, and evidence that the new rules remain consistent with the repository's operational constraints.

The project must review compliance at the same time as major deliverables and before release. A reviewer must verify that the implementation, tests, and documentation remain aligned with the applicable principles and that any deviations are documented and approved.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not recorded in repo; set at first formal approval | **Last Amended**: 2026-09-27
