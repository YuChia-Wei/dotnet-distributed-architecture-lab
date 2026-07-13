# Cross-Domain Test Specs

This directory contains test specifications spanning bounded contexts.

Suitable content:

- Collaboration flows between `<ContextA>` and `<ContextB>`
- MQ flows involving multiple domains
- Eventual-consistency verification paths
- Scenarios involving compensation, retries, or duplicate delivery

Unsuitable content:

- Aggregate or use-case tests that can be fully described within one domain
- Pure UI journeys; place complete-journey specifications under `../e2e/`
