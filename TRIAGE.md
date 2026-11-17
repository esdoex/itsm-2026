---
lab5_triage:
  image: ghcr.io/esdoex/itsm-2026@sha256:5587029fcebf04e0eaa47875c177195ae77cddaa5758a8aad1a17d1a456e1393
  sarif_receipt: 445
---
# Triage

What the gates and the reporting scanners found on my service, and what I did about each (CI-SPEC.md P-11, P-12).
One row per rule of one tool; a row may cover several locations, and the Reason says which. Tool is the tool id of
P-15 (`trivy`, `grype`, `osv-scanner`, `gitleaks`, `semgrep`). Decision is one of `fix`, `ignore`,
`false-positive`, `accept`.

| Tool | Rule | Decision | Reason |
|---|---|---|---|
| trivy | CVE-2026-85091 | fix | Updated the Debian package set with apt-get upgrade in Dockerfile, removing fixable zlib1g CVE-2026-85091 from the runtime image |
| semgrep | dockerfile.security.missing-user.missing-user | accept | The Dockerfile has no USER instruction, so the runtime image currently starts as root; risk is accepted temporarily until container hardening is applied |
| gitleaks | jwt | false-positive | The canary finding in the gitleaks evidence is a decoy or test fixture; no credential is used outside the intentionally seeded canary set |

## Bake-off

The canary matrix reports nine defects. Semgrep found five and produced two false positives, giving TP 5, FP 2, FN 4, precision 0.7143, recall 0.5556, and F1 0.625. Trivy found four defects and produced one false positive: TP 4, FP 1, FN 5, precision 0.8000, recall 0.4444, and F1 0.5714. Gitleaks found two defects and produced one false positive: TP 2, FP 1, FN 7, precision 0.6667, recall 0.2222, and F1 0.3333. Grype and OSV-Scanner each found two dependency defects with no false positives: TP 2, FP 0, FN 7, precision 1.0000, recall 0.2222, and F1 0.3636. Trivy would be the strongest gate among these five for this set because it combines the highest aggregate detection of dependency and code findings with an F1 of 0.5714, although Semgrep remains the more useful code analyser because it has the highest recall and F1. The two dependency tools surprised me by reporting perfectly precise but low-recall results, while gitleaks was less precise than expected. The five scanners missed four of the nine labelled defects, including insecure transport, deserialization, evaluation logic, and two credential types; these are either semantic or language-level defects that do not reliably produce the scanners' existing secret, dependency, or CWE signatures. Every recall in this matrix is an upper bound because the defects were injected and intentionally detectable in a small canary set, whereas real-world vulnerabilities are less synthetic and harder to isolate.
