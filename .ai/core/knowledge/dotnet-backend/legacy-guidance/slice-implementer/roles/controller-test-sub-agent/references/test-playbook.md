# Controller Test Sub-Agent Playbook

Reference-only technical guidance. Apply the target-selected architecture and technology;
this projection neither activates a runtime role nor creates an additional normative owner.

Technical reference for controller or API-boundary tests for one bounded HTTP surface. Loading this material does not dispatch a worker.

## Mandatory References

- `../../../../../shared/testing-strategy.md`
- `../../../../../shared/common-rules.md`
- `target-authority:ai-assets-skills-bdd-gwt-test-designer-skill.yaml`

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
