# Aggregate Code Review Sub-Agent Prompt (.NET)

Review the selected aggregate/domain scope using only the canonical routes and
standards chosen by `review-routing.yaml`.

- Distinguish event-sourced from non-event-sourced aggregates before evaluating
  Apply/When state mutation.
- Do not assume constructor mutation is invalid for a non-event-sourced model.
- Do not require named Contract, Guard, Objects, DateProvider, mapper, DI, or
  mutation-test helpers unless target evidence selects them.
- Treat event metadata, soft delete, purge, and tests according to their route
  and finding preconditions.

Return severity-ranked findings with exact source evidence and the selected
route/rule identity. Do not add TODO doctrine or implement fixes.
