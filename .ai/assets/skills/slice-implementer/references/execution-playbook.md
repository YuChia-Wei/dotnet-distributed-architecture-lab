# Slice Implementer Execution Playbook

This file defines how to implement one safe bounded implementation slice.

## Slice Template

1. Restate the slice goal and intent.
2. Separate authorization, normative truth, and finding evidence.
3. List in-scope files, modules, or behavior plus explicit non-goals.
4. Identify behavior that must remain stable.
5. Select exactly one execution mode reference.
6. Load applicable overlays without replacing the execution mode.
7. Apply the smallest coherent change set.
8. Use `local-change-implementer` for local class/object/symbol technical edits when useful.
9. If concrete tests are in scope, make them an authorized implementation outcome of this slice; a test-only slice selects `generic` as its one primary mode and loads each applicable test-role binding.
10. Treat a BDD/GWT scenario and assertion design as an input or handoff, not as authorization to implement tests; keep target-owned test execution as a separate capability and record it separately.
11. Validate and record deferred items.

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

Anything larger should be split by `software-development-orchestrator`.

## Safety Rules

- Keep each slice reviewable in isolation.
- Avoid unrelated renames, formatting churn, and cleanup.
- Preserve existing behavior unless the intent requires behavior change.
- If new architecture decisions emerge mid-slice, stop and escalate to `ddd-ca-hex-architect`.
- If implementation reveals hidden rule violations, note them for `code-reviewer`.
- Do not combine multiple aggregates, adapters, or unrelated use case flows unless the workflow task explicitly couples them.
