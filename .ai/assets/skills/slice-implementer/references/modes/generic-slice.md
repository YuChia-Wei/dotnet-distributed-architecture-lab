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
- concrete test implementation when no command, query, or reactor behavior is
  the slice's primary mode

## Rules

- Keep authorization, normative truth, and finding evidence explicitly separated.
- Do not redesign architecture direction. A class/interface extraction with a
  fully accepted design can be implemented here; adding a type alone does not
  require repeating architecture approval.
- Do not broaden the slice when adjacent issues are discovered.
- Prefer existing repository patterns.
- Record deferred work instead of mixing unrelated changes.
- A test-only slice uses this mode and loads each applicable concrete-test role
  binding. BDD/GWT design is an input to the slice, not implementation
  authority; target-owned test execution remains a distinct stage.
- When the slice implements GWT scenarios, consume
  `.ai/assets/shared/GWT-TEST-HANDOFF-CONTRACT.md` and return the concrete
  scenario-to-test/step/assertion mapping with truthful execution status.

## Expected Output

- bounded change result;
- touched files;
- behavior compatibility notes;
- validation notes;
- deferred items.
