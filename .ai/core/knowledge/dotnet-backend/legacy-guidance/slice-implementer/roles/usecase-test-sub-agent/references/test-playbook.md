# Use Case Test Sub-Agent Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for test implementation for one bounded use case. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/testing-strategy.md`
- `../../../../../shared/common-rules.md`
- `target-authority:ai-assets-skills-bdd-gwt-test-designer-skill.yaml`

## Working Model

- Prefer scenario and assertion plans from `bdd-gwt-test-designer`
- If no scenario plan exists, derive one conservatively from specs or existing behavior
- Keep each acceptance criterion mapped to explicit assertions

## Output Structure

- `src/tests/Application/<Aggregate>/UseCases/`

## Relationship To Top-Level Skill

- `bdd-gwt-test-designer` designs scenarios
- this sub-agent implements concrete use case tests from that design
