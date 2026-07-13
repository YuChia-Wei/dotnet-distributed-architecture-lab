# Slice Implementer Execution Playbook

This file defines how to implement one safe bounded implementation slice.

## Slice Template

1. Restate the slice goal.
2. List in-scope files, modules, or behavior.
3. List explicit non-goals.
4. Identify behavior that must remain stable.
5. Select the relevant mode reference.
6. Apply the smallest coherent change set.
7. Use `local-change-implementer` for local class/object/symbol technical edits when useful.
8. Update or add tests if the slice requires it.
9. Validate and record deferred items.

## Preferred Slice Types

- command-side use case
- query-side use case
- reactor/event reaction
- one feature or fix slice across a bounded module
- one review-remediation slice
- one targeted behavior-preserving refactor slice
- one targeted test-protection stage before deeper change

## Maximum Slice Size

Treat the following as the largest acceptable default slice:

- one aggregate boundary cleanup
- one handler or one use case flow
- one adapter extraction
- one outbound port isolation
- one repository cleanup in one module
- one targeted cross-file behavior correction

Anything larger should be split by `dev-workflow`.

## Safety Rules

- Keep each slice reviewable in isolation.
- Avoid unrelated renames, formatting churn, and cleanup.
- Preserve existing behavior unless the intent requires behavior change.
- If new architecture decisions emerge mid-slice, stop and escalate to `ddd-ca-hex-architect`.
- If implementation reveals hidden rule violations, note them for `code-reviewer`.
- Do not combine multiple aggregates, adapters, or unrelated use case flows unless the workflow task explicitly couples them.
