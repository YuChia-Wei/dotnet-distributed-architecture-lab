# Reactor Code Review Sub-Agent Playbook

Use this role for bounded event-handler, reactor or adopted integration-boundary
review. No particular broker, DI container, retry library or repository is assumed.

1. Apply the common route and only applicable installed technology extensions.
2. Trace event identity, conversion, side effects and the target's registration
   or subscription mechanism. Assess delivery, ordering and idempotency only
   where the supplied event contract requires them.
3. Compare collaboration and data access with the boundaries the target adopted.
   Do not invent a ban on queries that the target contract permits.
4. Check exception propagation and cleanup against the actual retry/recovery
   policy; deliberate propagation for retry is not automatically a defect.
5. Report evidence-backed findings and any missing contract or specialist coverage.

The role follows `.ai/assets/skills/code-reviewer/references/core-review-playbook.md`
and does not own a duplicate set of technology rules.
