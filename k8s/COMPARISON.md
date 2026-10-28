# Comparative Analysis: k8sgpt vs Agentic Loop Investigation

## Introduction
This evaluation contrasts the automated Kubernetes diagnostic findings produced by k8sgpt against the manual agentic loop investigation carried out during the real-time incident response.

## k8sgpt Automated Findings
The k8sgpt tool scanned the cluster state and resource definitions, identifying pod restarts and error-state deployments within the checkout ecosystem. However, due to its static nature, it lacked deep context regarding historical metric anomalies and distributed tracing span interactions across microservices.

## Agentic Loop Investigation
In contrast, the agentic investigation actively queried Prometheus, analyzed live Alertmanager notifications, correlated time-series trends, and executed precise metric evaluations. This dynamic approach allowed the agent to accurately verify hypotheses against baseline data, uncover cascading failures between the payment and checkout modules, and satisfy compliance frameworks such as NIS2 and DORA far more effectively than static log analyzers alone.
