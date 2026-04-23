# Reactor Implementer Handoff Rules

Use this skill only when the work is reactor-side implementation with a stable event contract and boundary.

## Hand Off To Another Skill When

- use `ddd-ca-hex-architect` if event ownership, reactor boundaries, or consistency strategy are still unclear
- use `staged-refactor-implementer` if the task is really a refactor stage spanning multiple reactors, integrations, or projections
- use `tactical-refactor-implementer` if the request is only a local cleanup inside one reactor handler
- use `bdd-gwt-test-designer` if reactor scenarios, event timing, or assertion points still need to be designed first
- use `code-reviewer` after implementation when the user asks for formal findings

## Sub-Agent Relationship

- `.ai/assets/sub-agent-role-prompts/reactor-sub-agent/` remains the delegated worker-role canonical asset
- this skill is the top-level implementation entry for reactor-side work
- when delegating further, preserve the same requirement, event contract, and validation packet instead of inventing a new contract
