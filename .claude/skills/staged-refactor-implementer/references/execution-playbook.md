# Execution Playbook

This file defines how to implement one safe refactoring stage.

## Stage Template

1. Restate the stage goal
2. List in-scope files or modules
3. List explicit non-goals
4. Identify behavior that must remain stable
5. Apply the smallest coherent code change set
6. Update or add tests if needed
7. Validate
8. Record deferred items

## Preferred Slice Types

- isolate one outbound dependency behind a port
- extract one adapter concern from application/domain code
- separate command and query responsibilities
- remove one repository misuse
- protect one hot path with tests before deeper refactoring

## Maximum Stage Size

Treat the following as the largest acceptable default slice:

- one aggregate boundary cleanup
- one handler or one use case flow refactor
- one adapter extraction
- one outbound port isolation
- one repository cleanup in one module
- one targeted test-protection stage

Anything larger should be split.

## Safety Rules

- Keep each stage reviewable in isolation.
- Avoid renames, formatting churn, and behavior changes unless the stage specifically requires them.
- If new architecture decisions emerge mid-stage, stop and escalate back to `ddd-ca-hex-architect`.
- If implementation reveals hidden rule violations, note them for `code-reviewer`.
- Do not combine multiple aggregates, multiple adapters, or multiple unrelated use case flows in one stage unless the user has explicitly pre-split the work and justified the coupling.

## Prompt Family Mapping

Load only the relevant prompt family:

- aggregate: `.ai/assets/sub-agent-role-prompts/aggregate-sub-agent/sub-agent.yaml`
- command/query: `.ai/assets/sub-agent-role-prompts/command-sub-agent/sub-agent.yaml`, `.ai/assets/sub-agent-role-prompts/query-sub-agent/sub-agent.yaml`
- tests: `.ai/assets/sub-agent-role-prompts/usecase-test-sub-agent/sub-agent.yaml`, `.ai/assets/shared/testing-standards.md`
- reactor/integration: `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/sub-agent.yaml`, `.ai/assets/sub-agent-role-prompts/outbox-sub-agent/sub-agent.yaml`

