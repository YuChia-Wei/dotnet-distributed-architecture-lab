# Aggregate Code Review Sub-Agent Playbook

Use this role when the target adopts aggregates or event sourcing for the
reviewed scope, or when domain invariants need a bounded review.

1. Apply the common route. Select technology routes only when their component
   and reviewed partition match; test rules require tests or test-quality scope.
2. Trace invariant preservation through construction, state transitions and
   failure paths. Compare boundaries with adopted target contracts.
3. For an explicitly event-sourced model, check event application, replay and
   invariant behavior. Do not require Apply/When method names or event sourcing
   itself unless the target or selected extension establishes that contract.
4. Apply delete, contract and helper conventions only under their declared
   preconditions. A custom port or different valid API is not itself a defect.
5. Report findings and evidence. Leave architecture decisions and repairs to
   the parent; do not infer selected technology from a familiar class name.

The role follows `.ai/assets/skills/code-reviewer/references/core-review-playbook.md`
and does not own a duplicate set of technology rules.
