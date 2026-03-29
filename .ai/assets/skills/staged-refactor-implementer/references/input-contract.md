# Input Contract

Normalize the task into this structure before implementing.

## Minimum Input

- `stage_goal`: the concrete result for this stage
- `scope`: target files, module, aggregate, or bounded context slice
- `architecture_target`: expected direction from `ddd-ca-hex-architect`, if any
- `findings`: concrete issues from `code-reviewer`, if any
- `constraints`: compatibility, testing, rollout, or sequencing constraints

At least one of these must also be true:

- `architecture_target` is explicit enough to prevent architectural guessing
- `findings` are concrete enough to define a safe implementation slice
- the user-provided `stage_goal` and `scope` are already narrow and behavior-preserving

## Example

```text
stage_goal:
  Extract query-only logic out of Product command handler.

scope:
  Product command handler and related query service.

architecture_target:
  Commands mutate state only; queries return DTO/projections only.

findings:
  Handler mixes read-model lookup and write-model mutation.

constraints:
  Preserve current API behavior.
  Keep stage limited to Product module.
  Add tests only for changed behavior boundaries.
```

## Escalation Triggers

Send the task back to planning instead of guessing when:

- the target architecture is contradictory or missing
- the requested stage crosses too many unrelated modules
- behavior-changing requirements are unclear
- the scope is broad but no prior architect/reviewer input exists
- the task would require deciding the architecture direction during implementation
