# Controller Code Review Sub-Agent Playbook

Use this role for bounded HTTP controller, endpoint, transport-data boundary
or HTTP-contract review, in any implementation technology.

1. Apply the common route and only the selected extension's matching routes.
2. Compare input validation, status codes, response shape, error behavior and
   relevant access boundaries with the supplied HTTP and target contracts.
3. Assess delegation and business-logic placement against the architecture the
   target adopted. Do not require an unselected controller pattern or framework.
4. Examine boundary mapping and relevant tests; do not load unrelated test rules.
5. Report actionable failures with triggers and evidence, while preserving
   acceptable alternative endpoint designs and declaring missing specialist checks.

The role follows `.ai/assets/skills/code-reviewer/references/core-review-playbook.md`
and does not own a duplicate set of technology rules.
