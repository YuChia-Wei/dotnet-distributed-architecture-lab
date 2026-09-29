# Source Map

Use this file to map a user request to the smallest useful subset of the repo's existing AI prompts and architecture documents.

## Core Sources

- `target-authority:dev-ARCHITECTURE.md`: repo-wide style and layer model
- `target-authority:dev-requirement-TECH-STACK-REQUIREMENTS.MD`: stack and tool constraints
- `target-authority:dev-standards-INDEX.MD`: standards lookup index
- `target-authority:dev-standards-README.md`: standards purpose and placement boundary
- `target-authority:ai-SUB-AGENT-SYSTEM.MD`: prompt-family overview

## Prompt Families

### Aggregate and Domain
- `../legacy-guidance/slice-implementer/roles/aggregate-sub-agent/sub-agent.yaml`
- `../legacy-guidance/slice-implementer/roles/aggregate-test-sub-agent/sub-agent.yaml`
- `../legacy-guidance/code-reviewer/roles/aggregate-code-review-sub-agent/sub-agent.yaml`
- `../shared/domain-rules.md`
- `../shared/dto-conventions.md`

Use for:
- aggregate boundary design
- event sourcing shape
- entity/value object placement
- domain event modeling

### Application: Command and Query
- `../legacy-guidance/slice-implementer/roles/command-sub-agent/sub-agent.yaml`
- `../legacy-guidance/slice-implementer/roles/query-sub-agent/sub-agent.yaml`
- `../legacy-guidance/slice-implementer/roles/usecase-test-sub-agent/sub-agent.yaml`
- `../shared/common-rules.md`
- `../shared/architecture-config.md`

Use for:
- command handler flow
- query projection flow
- result and DTO shape
- write/read separation

### Integration and Consistency
- `../legacy-guidance/slice-implementer/roles/reactor-sub-agent/sub-agent.yaml`
- `../legacy-guidance/slice-implementer/roles/outbox-sub-agent/sub-agent.yaml`
- `../legacy-guidance/slice-implementer/roles/profile-config-sub-agent/sub-agent.yaml`

Use for:
- cross-aggregate consistency
- MQ choreography
- outbox mapping
- environment/profile isolation

### API Boundary
- `../legacy-guidance/slice-implementer/roles/controller-sub-agent/references/implementation-guidance.md`
- `../legacy-guidance/code-reviewer/roles/controller-code-review-sub-agent/sub-agent.yaml`
- `../legacy-guidance/slice-implementer/roles/controller-test-sub-agent/sub-agent.yaml`

Use for:
- API contract shape
- controller boundary rules

### Quality Gates
- `../legacy-guidance/code-reviewer/roles/code-review-sub-agent/sub-agent.yaml`
- `../legacy-guidance/code-reviewer/roles/reactor-code-review-sub-agent/sub-agent.yaml`
- `target-authority:ai-assets-skills-code-reviewer-references-review-routing.yaml`
- `../legacy-guidance/spec-compliance-validator/references/spec-compliance-rules.md`
- `../legacy-guidance/spec-compliance-validator/references/test-validation-steps.md`
- `../legacy-guidance/spec-compliance-validator/references/validation-command-templates.md`

Use for:
- architecture review
- prompt review
- spec coverage and validation

## Decision/Rule Hotspots

Read the canonical rules/docs for these recurring areas:

- Sub-agent and prompt structure: `target-authority:ai-SUB-AGENT-SYSTEM.MD`, `SKILL-AND-SUB-AGENT-TAXONOMY-GUIDE.md`
- DI and configuration: `../standards/coding-standards/usecase-standards.md`, `../standards/coding-standards/profile-configuration-standards.md`, `../standards/ASPNET-CORE-CONFIGURATION-CHECKLIST.md`
- Outbox and transaction flow: `../standards/coding-standards.md`, `../guides/FRAMEWORK-API-INTEGRATION-GUIDE.md`
- Query-side layering: `../standards/coding-standards.md`, `../references/rationale/query-side-layering-rationale.MD`
- Conditional physical project layout and shared-project profile: `../standards/project-structure.md`; confirm target adoption and use canonical architecture standards for invariants
- Docker/container packaging: `../guides/DOCKER-RESTORE-CACHE-GUIDE.md`

## Selection Rules

- Read the family overview first, then only the exact prompt files needed for the task.
- Prefer shared prompt fragments for stable rules and specialized prompts for task mechanics.
- If the user asks to create a reusable architect prompt or skill, treat `selected engineering-common resources` plus these decision/rule hotspots as the canonical design input.
