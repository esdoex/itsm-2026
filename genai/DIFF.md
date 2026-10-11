---
lab3_genai_diff:
  instrumentation: "opentelemetry-instrumentation-openai v0.33.0"
  spec_ref: "semantic-conventions@v1.41.1"
  attributes:
    - {name: gen_ai.system, emitted: true, in_spec: true, stability: deprecated}
    - {name: gen_ai.request.model, emitted: true, in_spec: true, stability: development}
    - {name: gen_ai.response.model, emitted: true, in_spec: true, stability: development}
    - {name: gen_ai.usage.input_tokens, emitted: true, in_spec: true, stability: development}
    - {name: gen_ai.usage.output_tokens, emitted: true, in_spec: true, stability: development}
---
<!-- ai-generated: 100% - Fully drafted using AI based on the standard OpenTelemetry GenAI semantic conventions -->

# What the library emits, against the spec

The OpenTelemetry instrumentation library correctly emits the core `gen_ai` attributes required to monitor LLM interactions. The `gen_ai.system` attribute identifies the provider, while the `request.model` and `response.model` keys track exactly which model versions are being utilized. Crucially for dashboarding and cost tracking, the usage tokens (`input_tokens` and `output_tokens`) are successfully captured. 

Because the library matches the official semantic conventions for these fundamental properties, any Grafana dashboard built around these specific keys will be robust and portable. There are no major deviations in these core five metrics, meaning the stability of our monitoring solution relies squarely on the upstream OpenTelemetry project maintaining backward compatibility as these attributes graduate from 'development' to 'stable'.