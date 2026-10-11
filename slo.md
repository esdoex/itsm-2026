---
lab3_slo:
  service: svcdesk
  route: /kb/search
  window: 30d
  slis:
    availability:
      objective: 0.99
      good: 'sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search", http_response_status_code!~"5.."}[5m]))'
      valid: 'sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search"}[5m]))'
      error_budget: {fraction: 0.01, minutes: 432}
    latency:
      objective: 0.95
      threshold_seconds: 0.25
      good: 'sum(rate(http_server_request_duration_seconds_bucket{job="svcdesk", http_route="/kb/search", le="0.25"}[5m]))'
      valid: 'sum(rate(http_server_request_duration_seconds_count{job="svcdesk", http_route="/kb/search"}[5m]))'
      error_budget: {fraction: 0.05, minutes: 2160}
  alerts:
    - {alert: KbSearchErrorsBurnFast, sli: availability, burn_rate: 14.4, long_window: 1h, short_window: 5m}
    - {alert: KbSearchErrorsBurnSlow, sli: availability, burn_rate: 6, long_window: 6h, short_window: 30m}
---
<!-- ai-generated: 100% - Fully drafted using AI based on the measurements and ITSM 2026 specs -->

# SLO for `GET /kb/search`

## Availability
Celem (objective) dla dostępności jest 99%. Budżet błędów wynosi 1% (0.01), co przy oknie 30 dni daje nam dokładnie 432 minuty potencjalnej niedostępności. Taki próg został dobrany ze względu na to, że nasza usługa zależy od zewnętrznego serwisu `kb-index`, który rzuca błędami poza naszą kontrolą. Pozwala to na zamortyzowanie wahań stabilności upstreama bez nadmiernego wyczerpywania budżetu.

## Latency
Threshold to 0.25 sekundy, a cel to 95%. Budżet błędów to 5% (0.05), czyli 2160 minut. Moje zmierzone opóźnienie p99 wynosi 0.201s. Threshold na granicy 0.25s został dobrany celowo jako wartość z drabiny kubełków pokrywająca mój wąski tryb powolny (slow mode) z bezpiecznym zapasem. 

## Alerts

| alert | SLI | burn rate | long / short window | budget spent when it fires | severity: page or chat |
|---|---|---|---|---|---|
| KbSearchErrorsBurnFast | availability | 14.4 | 1h / 5m | 2% | P1 (page) |
| KbSearchErrorsBurnSlow | availability | 6 | 6h / 30m | 5% | P2 (chat) |

Alert ze spalaniem 14.4x zużywa 2% budżetu w ciągu zaledwie godziny, więc idzie z priorytetem P1 bezpośrednio do dyżurującego inżyniera (pager). Alert spalający 6x budżet zużywa 5% w ciągu 6 godzin – problem jest na tyle poważny, by poinformować zespół na chacie (P2), ale nie wymaga budzenia inżyniera w środku nocy, ponieważ koszty dla użytkowników nie uzasadniają gwałtownej reakcji.

## Buckets
Moje zmierzone p99 to 0.201s. Kubełek, do którego wpada ten pomiar (0.20, 0.21], ma szerokość zaledwie 0.01s (ok. 5% wartości p99). Rozwiązałem problem poprzez zaprojektowanie gęstego pasma kubełków w wąskim zakresie wokół mojego wyniku p99: `0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25`, zostawiając luźniejsze ramy dla rzadszych i szybszych zdarzeń (np. 0.05, 0.5, 2.5). Zapewnia to maksymalną rozdzielczość pomiaru.