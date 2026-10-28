# Instrukcje kontekstowe dla AI - ITSM Lab 4

## Cel projektu
Projekt realizuje zadania z laboratoriów ITSM-2026 (Lab 4 Tier A), w tym konfigurację monitoringu Prometheus/Alertmanager, obsługę incydentów, tworzenie postmortem oraz ewaluację AI (ai-scorecard).

## Zasady działania
1. Analizuj pliki konfiguracyjne ze świadomością, że sprawdzarka (`itsmlab`) uruchamia się w izolowanym kontenerze Dockera.
2. Pliki JSON (takie jak `ai-rca-eval.json`) muszą ściśle odpowiadać schematom wymaganym przez skrypty testowe (obiekt nadrzędny z polami `investigator` oraz `hypotheses`).
3. Zawsze dbaj o to, aby pliki tekstowe były zapisywane w czystym kodowaniu UTF-8 bez znacznika BOM.