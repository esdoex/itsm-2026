---
lab2_edge_cases:
  E1: {rule: R-08, count: 3}
  E2: {rule: R-06, count: 2}
  E3: {rule: R-09, count: 4}
  E4: {rule: R-10, count: 4}
  E5: {rule: R-12, count: 1}
  E6: {rule: R-13, count: 11}
---
<!-- ai-generated: 95% - drafted by Copilot from METRIC-SPEC edge cases and measured fixture anomalies -->
# DORA metric edge cases

Counts below are the service's measured anomaly or failure counts for the published practice fixture.

## E1 - clock skew produces a negative lead time

- What the log contains: Three shipped commit timestamps occur after the successful deployment that carries them.

- What a default definition would have done: It would report negative durations or drop pairs, misleading readers about delivery speed.

- Why the rule is defensible: Clock skew is observable data, so clamping to zero preserves the pairs and exposes the anomaly.

## E2 - a revert of a revert

- What the log contains: Two commits have non-null `reverts` references and inherit their original changes.

- What a default definition would have done: It could count each revert as new work, inflating the change count shown to readers.

- Why the rule is defensible: Transitive ancestry assigns reverted work to its original change and prevents double counting.

## E3 - a hotfix that never touched `main`

- What the log contains: Four distinct production-carried commit SHAs use a branch other than `main`.

- What a default definition would have done: It could filter out hotfixes and make readers think less work reached production.

- Why the rule is defensible: Production delivery, not branch naming, determines whether a commit reached users.

## E4 - a deployment with zero linked commits

- What the log contains: Four in-window production deployments contain an empty commit list.

- What a default definition would have done: It could omit empty releases and understate cadence for people reading the dashboard.

- Why the rule is defensible: Each production deployment remains an operational event even when its payload is empty.

## E5 - a deployment that failed and never recovered

- What the log contains: One in-window failed production deployment has no covering incident with a resolved phase.

- What a default definition would have done: It could invent a recovery time and reassure readers while production remains failed.

- Why the rule is defensible: Open failures remain in the fail-rate numerator but have no invented recovery time.

## E6 - overlapping incidents

- What the log contains: Eleven unordered pairs of distinct incident intervals intersect in the observation window.

- What a default definition would have done: It could merge distinct incidents, obscuring readers' view of separate deployments' recovery.

- Why the rule is defensible: Counting each intersecting pair while recovering each failure independently preserves incident identity.

## Gaming demonstration

I improved `deployment_frequency_per_day` by applying R-11 and adding empty production deployments. A real team
facing a frequency target could split a release into more recorded deployments without delivering additional
changes. The dashboard would reward the release operator or team for the higher count, while users would see no
corresponding increase in delivered work; delaying two base deployments also reduces delivered changes.
