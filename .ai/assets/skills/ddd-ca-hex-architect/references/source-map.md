# Source Map

Use this file to map a user request to the smallest useful subset of the repo's existing AI prompts and architecture documents.

## Core Sources

- `.dev/ARCHITECTURE.MD`: repo-wide style and layer model
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`: stack and tool constraints
- `.dev/standards/README.md`: standards lookup index
- `.ai/SUB-AGENT-SYSTEM.MD`: prompt-family overview

## Prompt Families

### Aggregate and Domain
- `.ai/assets/sub-agent-role-prompts/aggregate-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/aggregate-test-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/sub-agent.yaml`
- `.ai/assets/shared/domain-rules.md`
- `.ai/assets/shared/dto-conventions.md`

Use for:
- aggregate boundary design
- event sourcing shape
- entity/value object placement
- domain event modeling

### Application: Command and Query
- `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/architecture-config.md`

Use for:
- command handler flow
- query projection flow
- result and DTO shape
- write/read separation

### Integration and Consistency
- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/profile-config-sub-agent/sub-agent.yaml`

Use for:
- cross-aggregate consistency
- MQ choreography
- outbox mapping
- environment/profile isolation

### API and Frontend Boundary
- `.ai/assets/sub-agent-role-prompts/controller-sub-agent/references/implementation-guidance.md`
- `.ai/assets/sub-agent-role-prompts/controller-code-review-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/controller-test-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/api-integration-guidance.md`

Use for:
- API contract shape
- controller boundary rules
- frontend/backend contract alignment

### Quality Gates
- `.ai/assets/sub-agent-role-prompts/code-review-sub-agent/sub-agent.yaml`
- `.ai/assets/sub-agent-role-prompts/reactor-code-review-sub-agent/sub-agent.yaml`
- `.ai/assets/shared/code-review-checklist.md`
- `.ai/assets/skills/spec-compliance-validator/references/spec-compliance-rules.md`
- `.ai/assets/skills/spec-compliance-validator/references/test-validation-steps.md`
- `.ai/assets/skills/spec-compliance-validator/references/validation-command-templates.md`

Use for:
- architecture review
- prompt review
- spec coverage and validation

## Decision/Rule Hotspots

Read the canonical rules/docs for these recurring areas:

- Sub-agent and prompt structure: `.ai/SUB-AGENT-SYSTEM.MD`, `SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`
- DI and configuration: `.dev/standards/coding-standards/usecase-standards.md`, `.dev/standards/coding-standards/profile-configuration-standards.md`, `.dev/standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md`
- Outbox and transaction flow: `.dev/standards/coding-standards.md`, `.dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`
- Query-side layering: `.dev/standards/coding-standards.md`, `.dev/standards/rationale/query-side-layering-rationale.MD`
- Shared project boundaries: `.dev/standards/project-structure.md`
- Docker/container packaging: `.dev/guides/implementation-guides/DOCKER-RESTORE-CACHE-GUIDE.md`

## Selection Rules

- Read the family overview first, then only the exact prompt files needed for the task.
- Prefer shared prompt fragments for stable rules and specialized prompts for task mechanics.
- If the user asks to create a reusable architect prompt or skill, treat `.ai/assets/shared/*.md` plus these decision/rule hotspots as the canonical design input.
