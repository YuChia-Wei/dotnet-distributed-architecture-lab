# Software Development Orchestrator Fallback Playbooks

Use fallback-mode when no downstream skill, project-specific standard, or reliable tool exists for a capability slot.

Fallback-mode should produce a minimum viable checklist, handoff prompt, or risk note. It must not claim the same quality as a specialist skill.

## General Fallback Rules

1. State that the stage is running in fallback-mode.
2. Name the missing capability or downstream skill.
3. Use the generic checklist for that capability.
4. Produce a handoff packet that a specialist can continue later.
5. Record residual risk in the final output.

## Capability Fallbacks

### `requirements`

Minimum checklist:

- Capture user goal, actors, constraints, assumptions, and missing decisions.
- Separate confirmed facts from inferred items.
- Recommend a target requirement path.
- Do not invent stakeholder intent.

### `specification`

Minimum checklist:

- Link each spec item back to requirement truth or code evidence.
- Define behavior, inputs, outputs, failure cases, and non-goals.
- Mark unresolved domain decisions.
- Avoid treating examples as full requirements.

### `problem-framing`

Minimum checklist:

- Identify the frame type and source evidence.
- Capture phenomena, workpieces, commands, and expected outcomes.
- Mark missing evidence before claiming validator readiness.

### `architecture`

Minimum checklist:

- Identify the architectural decision needed.
- State bounded context, aggregate, port/adapter, dependency, and data ownership assumptions.
- List tradeoffs and non-goals.
- Avoid irreversible refactors without an explicit target decision.

### `test-design`

Minimum checklist:

- Draft Given-When-Then scenarios from requirement or spec truth.
- Identify assertion points and test level.
- Mark missing fixtures, data builders, and observable outcomes.

### `implementation`

Minimum checklist:

- Confirm scope, target files, expected behavior, and validation command.
- Prefer existing project patterns.
- Keep changes bounded to the task.
- Do not redesign architecture while implementing.

### `test-execution`

Use this fallback only after target-profile commands and any separately
evaluated external skill are unavailable.

Minimum contract:

- Read target-owned commands, working directory, prerequisites, and policy from
  repository evidence or an explicit owner decision.
- Do not invent credentials, bypass enterprise controls, or escalate privileges
  implicitly.
- Select unit and integration by default; select E2E, browser, Playwright, or
  environment-dependent levels only when target policy, requirements, an
  approved plan, or the owner requires them.
- Record exactly one outcome per selected level: `passed`, `failed`,
  `blocked-by-environment`, `not-applicable`, or `deferred-with-owner`.
- Treat `blocked-by-environment` as blocked, never passed. A mandatory selected
  test keeps closeout open until target policy accepts the recorded outcome.
- Use `deferred-with-owner` only with the responsible owner and follow-up
  condition recorded.

### `refactoring`

Minimum checklist:

- Identify the refactoring target and invariant behavior.
- Define before/after boundaries.
- Run or name the narrow regression check.
- Avoid broad structural changes without architecture direction.

### `review`

Minimum checklist:

- Lead with findings ordered by severity.
- Ground each finding in file/line evidence when possible.
- Separate bugs, missing tests, design risks, and residual risk.
- Do not rewrite code unless explicitly asked.

### `compliance-validation`

Minimum checklist:

- Identify the governing spec or problem frame.
- Map implementation/test evidence to each required behavior.
- Mark pass/fail explicitly.
- When spec compliance is not explicitly selected, report `not-applicable`
  rather than pass.
- Once selected, require complete configuration and direct evidence of 100%
  coverage; partial configuration or lower coverage fails closed.
