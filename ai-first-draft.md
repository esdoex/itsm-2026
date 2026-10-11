---
lab3_first_draft:
  source: ai
  tool: "GitHub Copilot, 11 October 2026"
  ladder: [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2.5, 5, 10]
  verdict: refuted
  evidence: {p99_seconds: 0.201, bucket: [0.2, 0.3], relative_width: 0.498}
lab3_flawed_ladder:
  verdict: refuted
  evidence: {p99_seconds: 0.201, bucket: [0.04, 0.5], relative_width: 2.289}
---
<!-- ai-generated: 100% - This file was fully assembled using AI logic based on the required templates -->

# The assistant's first draft, and two verdicts

## Prompt
Jesteś inżynierem SRE. Zaprojektuj mi tablicę granic kubełków w sekundach (le buckets) dla histogramu HTTP Request Duration w Prometheusie dla endpointu GET /kb/search. Wygeneruj mi też przykładową regułę alarmową powiadamiającą, że ten sam endpoint rzuca błędy (availability).

## Answer
> Granice kubełków
> Dla interaktywnego endpointu wyszukiwania proponuję granice:
> [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2.5, 5, 10] sekund
> Gęstsze kubełki poniżej 500 ms pomagają ocenić typowe czasy odpowiedzi, a wyższe pokazują długi ogon opóźnień.
> 
> Reguła alarmowa dostępności
> (Przykładowa reguła z thresholdem 0.05 wzięta bezpośrednio od asystenta).

## Verdict on the draft ladder
My measured p99 is 0.201s. In the draft ladder, this falls into the bucket (0.2, 0.3], which is 0.1s wide. Its relative width is 0.1 / 0.201 = 0.498. Because this is far above the 0.20 maximum allowed width, histogram_quantile would report highly inaccurate results. The verdict is refuted.

## The draft alert rule
The assistant suggested a threshold of 5% errors over 5 minutes. I will use a multi-burn-rate approach derived from my actual SLO objective instead, but the general PromQL structure (errors divided by total requests) provided by the AI is useful as a foundation for `alerts.yml`.

## Verdict on the instructor's flawed ladder
In the instructor's flawed ladder, my p99 of 0.201s falls into the bucket (0.04, 0.5], which is 0.46s wide. The relative width is 0.46 / 0.201 = 2.289. This bucket is more than twice as wide as the p99 itself, completely failing to resolve the narrow latency band where the p99 lives. The verdict is refuted.