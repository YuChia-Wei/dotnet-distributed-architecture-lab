# Command Use Case Implementer Handoff Rules

Use this skill only when the work is command-side implementation with a stable boundary.

## Hand Off To Another Skill When

- use `ddd-ca-hex-architect` if aggregate boundaries, command semantics, or integration responsibilities are still unclear
- use `staged-refactor-implementer` if the task is really a stage-sized refactor instead of a single bounded command implementation
- use `tactical-refactor-implementer` if the request is only a local cleanup inside one class or handler
- use `bdd-gwt-test-designer` if acceptance scenarios or assertion points still need to be designed before implementation
- use `code-reviewer` after implementation when the user asks for formal findings

## Sub-Agent Relationship

- `.ai/assets/sub-agent-role-prompts/command-sub-agent/` remains the delegated worker-role canonical asset
- this skill is the top-level implementation entry for command-side work
- when delegating further, preserve the same requirement, spec, and validation packet instead of inventing a new contract
