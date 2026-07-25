# AGENTS.md

This is the canonical English collaboration guide for AI agents and humans in this repository. Keep repository-specific facts here concise and backed by files in the repository.

## Scope And Precedence

- A deeper `AGENTS.md` takes precedence for its subtree.
- Follow user and approval instructions before repository guidance.
- Do not invent project truth. State material assumptions and unresolved decisions.
- Make the smallest coherent change that satisfies explicit acceptance criteria.

## AI Context Quick Start

1. Read `README.md`, `.dev/README.MD`, and any repository architecture or project configuration documents that exist.
2. Read `.dev/standards/WORKFLOW-GATE-POLICY.md` before multi-stage or source-of-truth work.
3. Use `.ai/assets/skills/README.MD` to select the owning skill; treat `.ai/assets/skills/` as canonical when a runtime wrapper differs.
4. Use `.ai/INDEX.MD` for reusable agent-facing assets and `.dev/INDEX.md` for human-facing project knowledge.
5. Keep runtime wrappers thin and keep target-specific facts outside reusable framework assets.

## Execution And Validation

- Establish verifiable completion criteria before editing.
- Touch only files required by the task and preserve unrelated user changes.
- Use a dedicated workflow branch when the workflow gate requires it.
- Run the narrowest meaningful validation, record skipped checks, and do not claim completion while required gates fail.
- Follow `.dev/standards/GIT-COMMIT-POLICY.md` for AI-assisted commits.

## Repository-Specific Context

`ai-context-init` replaces this section with evidence-backed repository identity, navigation, stack facts, and local commands. Until that synchronization completes, treat copied or placeholder project facts as unresolved.
