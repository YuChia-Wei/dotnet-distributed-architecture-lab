# Aggregate Code Review Sub-Agent Playbook

Use this role only when the selected scope includes an aggregate, domain event,
entity, value object, or their tests.

## Review Flow

1. Select `aggregate`, `domain-event`, `entity`, `value-object`, and/or `test`
   routes from `review-routing.yaml`.
2. Load the aggregate standard once for the selected domain routes. Load the
   test standard only when tests or test-quality findings are in scope.
3. Apply `AGGREGATE-ES-001` only when type hierarchy or an explicit target
   contract proves the aggregate is event-sourced.
4. Apply contract, delete, and helper rules only under their declared target or
   finding preconditions.
5. Report bounded findings; leave target architecture and implementation to the
   owning workflow.

Role text is execution guidance, not a second aggregate checklist.
