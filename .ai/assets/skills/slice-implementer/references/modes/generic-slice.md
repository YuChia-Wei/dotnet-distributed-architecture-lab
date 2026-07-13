# Generic Slice Mode

Use this mode when the slice is bounded but does not fit command, query, or reactor mode.

## Common Intents

- feature slice
- bug fix slice
- review remediation slice
- validation failure remediation
- behavior correction
- cleanup
- behavior-preserving refactor

## Rules

- Keep the slice source-truth explicit.
- Do not redesign architecture direction.
- Do not broaden the slice when adjacent issues are discovered.
- Prefer existing repository patterns.
- Record deferred work instead of mixing unrelated changes.

## Expected Output

- bounded change result;
- touched files;
- behavior compatibility notes;
- validation notes;
- deferred items.
