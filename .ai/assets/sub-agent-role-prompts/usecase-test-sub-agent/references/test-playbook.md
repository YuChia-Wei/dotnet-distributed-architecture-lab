# Use Case Test Sub-Agent Playbook

Use this delegated worker role when the main agent needs concrete test implementation for one bounded use case.

## Mandatory References

- `.ai/assets/shared/testing-strategy.md`
- `.ai/assets/shared/common-rules.md`
- `.ai/assets/skills/bdd-gwt-test-designer/skill.yaml`

## Working Model

- Prefer scenario and assertion plans from `bdd-gwt-test-designer`
- If no scenario plan exists, derive one conservatively from specs or existing behavior
- Keep each acceptance criterion mapped to explicit assertions

## Output Structure

- `src/tests/Application/<Aggregate>/UseCases/`

## Relationship To Top-Level Skill

- `bdd-gwt-test-designer` designs scenarios
- this sub-agent implements concrete use case tests from that design

