# Controller Test Sub-Agent Playbook

Use this delegated worker role when the main agent needs concrete controller or API-boundary tests for one bounded HTTP surface.

## Mandatory References

- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

## Focus Areas

- HTTP status codes
- response DTO shape
- route and contract verification
- integration-level test setup through `WebApplicationFactory`

## Output Structure

- `src/tests/Api/Controllers/<Aggregate>/`

## Relationship To Top-Level Skill

- `bdd-gwt-test-designer` designs scenarios and assertion intent
- this sub-agent implements controller-focused test code from that design

