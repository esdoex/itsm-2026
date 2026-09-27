---
svcdesk_decisions:
  C1: wallclock      # wallclock | business
  C2: immutable      # reopen | immutable
  C3: vip            # matrix | vip
---
<!-- ai-generated: 100% - w pełni wygenerowane przy pomocy Github Copilot -->

# Decisions


## C1 - SLA clock for P1

**Decision:** Czas SLA dla zgłoszeń o najwyższym priorytecie P1 jest odliczany w czasie rzeczywistym (wallclock), przez 24 godziny na dobę, 7 dni w tygodniu.

**Rejected alternative:** Odrzucono wariant, w którym czas rozwiązania dla zgłoszeń P1 byłby wstrzymywany na noc i weekendy, ograniczając się tylko do godzin biznesowych.

**Reason:** Priorytet P1 oznacza krytyczną awarię (np. brak dostępu do głównego serwera). Wstrzymywanie zegara na weekend fałszowałoby faktyczny czas przestoju systemów i opóźniałoby reakcję.

**Service owner:** Główny Kierownik IT (IT Operations Manager) – odpowiada za ciągłość działania kluczowej infrastruktury i raportowanie dostępności usług.

**Customer outcome:** Organizacja zyskuje pewność, że krytyczne incydenty zgłoszone poza godzinami pracy zostaną podjęte natychmiast, minimalizując straty biznesowe.

## C2 - Closed tickets and reopening

**Decision:** Bilety, które osiągnęły ostateczny stan zamknięcia (closed), są całkowicie niemutowalne i nie mogą zostać ponownie otwarte pod żadnym pozorem.

**Rejected alternative:** Odrzucono możliwość ponownego otwierania przez użytkowników zamkniętych zgłoszeń w regulaminowym oknie 7 dni.

**Reason:** Stan "closed" oznacza obustronne potwierdzenie, że problem zniknął. Zezwalanie na powrót do starych biletów po zamknięciu zaburzyłoby statystyki rozwiązywalności przy pierwszym kontakcie (First Call Resolution).

**Service owner:** Menedżer Service Desku (Service Desk Manager) – jego rolą jest dbanie o wiarygodność statystyk zespołu i spójność bazy historycznej.

**Customer outcome:** Wymusza to na użytkownikach dokładniejszą weryfikację poprawek przed ostatecznym zamknięciem, a w razie nawrotu wymaga otwarcia nowego zgłoszenia, co zachowuje pełny kontekst audytowy.

## C3 - VIP reporters and the priority matrix

**Decision:** Zgłoszenia pochodzące od użytkowników oznaczonych flagą VIP są automatycznie windowane do poziomu minimum P2, niezależnie od bazowej matrycy wpływu i pilności.

**Rejected alternative:** Odrzucono sztywne trzymanie się matrycy priorytetów (impact i urgency) dla wszystkich pracowników bez robienia wyjątków.

**Reason:** Awarie sprzętu u kadry zarządzającej, nawet te o niskim obiektywnym wpływie, blokują kluczowe procesy decyzyjne w firmie. Ich czas jest zbyt cenny na standardowe 72 godziny oczekiwania.

**Service owner:** Dyrektor ds. Relacji z Biznesem (Business Relationship Manager) – odpowiada za relacje działu IT z zarządem i realizację celów biznesowych.

**Customer outcome:** Kluczowi decydenci otrzymują błyskawiczną pomoc techniczną, co pozwala im uniknąć frustracji i w pełni skupić się na strategicznym zarządzaniu organizacją.
