# Reactor Code Review Sub-Agent Playbook

Use this role for bounded reactor/event-handler and cross-aggregate integration
review.

1. Select the `reactor` route from `review-routing.yaml`.
2. Add `domain-event` or `test` only when those files/findings are in scope.
3. Review event conversion, collaboration boundary, redelivery/idempotency, and
   target-proven registration against the selected canonical standards.
4. Report evidence-backed findings without assuming a DI, retry, bus, or
   repository technology the target did not select.

The role prompt is execution guidance, not a semantic owner.
