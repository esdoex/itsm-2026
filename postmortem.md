---
lab4_postmortem:
  ticket: "5e6d0d7a-d232-4358-bff0-5ae2abc68268"
  detecting_alert: CheckoutErrorRate
  onset: 2026-10-27T20:51:27Z
  detection: 2026-10-27T21:18:49Z
  acknowledgement: 2026-10-27T21:20:18Z
  recovery: 2026-10-27T21:20:19Z
  mttd_seconds: 1642
  mtta_seconds: 89
  mttr_seconds: 1732
  identified_flags: [paymentFailure, adManualGc, recommendationCacheFailure]
---
<!-- ai-generated: 100% - drafted postmortem structure with computed timings based on the provided template -->

# Postmortem: Checkout failure due to simulated payment gateway drop

## Date
The incident occurred on October 27, 2026, and this postmortem was finalized shortly after recovery.

## Authors
Authored by the primary on-call platform engineer responsible for the ITSM-2026 laboratory environment.

## Status
Complete, action items are logged and currently in progress for the next sprint.

## Summary
The checkout service experienced a severe degradation due to a simulated payment gateway failure, disrupting customer orders for approximately 29 minutes.

## Impact
Customer checkouts were heavily impacted with a 10% failure rate for nearly 30 minutes, directly causing revenue loss and degraded user experience. Measured via traces_span_metrics_calls_total.

## Root Causes
A planned fault injection (paymentFailure) triggered a 10% drop in payment processing, which cascaded to the checkout service causing transaction failures.

## Trigger
The fault was triggered by an automated chaos engineering script at the onset of the drill (2026-10-27T20:51:27Z).

## Resolution
The system automatically recovered when the fault injection window expired, resetting the flag configurations back to default state.

## Detection
The incident was detected by the CheckoutErrorRate alert after adjusting the PromQL threshold to catch the 10% error rate.

## Action Items

| Action Item | Type | Owner | Bug |
|---|---|---|---|
| Adjust all Prometheus rules to match OTEL 3.1.0 metric structures. | prevent | SRE | ITSM-42 |
| Lower the baseline thresholds for P1 alerts to catch minor drops. | mitigate | SRE | ITSM-43 |

## Lessons Learned

### What went well
The incident response tools (Pager, svcdesk) worked flawlessly once the alert was correctly routed and generated.

### What went wrong
The initial alert thresholds and metric names were misconfigured for the current OpenTelemetry version, severely delaying detection.

### Where we got lucky
The fault was part of a controlled drill rather than a real-world scenario, preventing actual customer revenue loss.

## Timeline
- 20:51:27Z: Fault injection triggered the payment drop (onset).
- 21:18:49Z: Alerting system caught the degraded state after rules update (detection).
- 21:20:18Z: On-call engineer acknowledged the incident in the ticket system.
- 21:20:19Z: System self-recovered automatically as the injection ended.

## Supporting information
Relevant Grafana dashboards, Prometheus query logs from the tsdb-snapshot, and itsmlab incident output confirm the timeline.

## Problem record
- Incident record: 5e6d0d7a-d232-4358-bff0-5ae2abc68268
- Root cause: Fault injection testing caused simulated network drops on the payment gateway.
- Known error: Alerting rules were initially using deprecated metric names.
- Workaround: Manually updating the Prometheus rules during the incident to use traces_span_metrics_calls_total.