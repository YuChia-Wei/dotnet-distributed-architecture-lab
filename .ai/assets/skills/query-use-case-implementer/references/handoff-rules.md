# Query Use Case Implementer Handoff Rules

Use this skill only when the work is query-side implementation with a stable DTO and read-model boundary.

## Hand Off To Another Skill When

- use `ddd-ca-hex-architect` if projection ownership, query boundaries, or API responsibility are still unclear
- use `staged-refactor-implementer` if the task is really a refactor stage spanning multiple handlers or read models
- use `tactical-refactor-implementer` if the request is only a local cleanup inside one query handler or mapper
- use `bdd-gwt-test-designer` if query scenarios, filters, or assertion points still need to be designed first
- use `code-reviewer` after implementation when the user asks for formal findings

## Sub-Agent Relationship

- `.ai/assets/sub-agent-role-prompts/query-sub-agent/` remains the delegated worker-role canonical asset
- this skill is the top-level implementation entry for query-side work
- when delegating further, preserve the same requirement, spec, DTO, and validation packet instead of inventing a new contract
