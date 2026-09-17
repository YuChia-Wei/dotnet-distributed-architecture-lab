# AGENTS.md

This is the canonical English collaboration guide for AI agents and humans in this repository. Keep repository-specific facts here concise and backed by repository evidence.

## Scope And Precedence

- A deeper `AGENTS.md` takes precedence for its subtree.
- Follow user instructions and explicit approvals before repository guidance.
- Do not invent project truth, authorization, execution, or validation. State material assumptions and unresolved decisions.
- Make the smallest coherent change that satisfies the accepted scope and verifiable completion criteria.

## Progressive Context Loading

1. Start with the request, current Git/worktree state, this file, and explicitly named artifacts.
2. When a skill applies, use `.ai/assets/skills/README.MD` to select one owning route and load its canonical entry. Runtime wrappers remain thin adapters.
3. Expand only for the current task or phase. Read `.dev/standards/WORKFLOW-GATE-POLICY.md` when multi-stage or source-of-truth work requires a mode decision.
4. Use `.ai/INDEX.MD` and `.dev/INDEX.md` for navigation when needed. Load README, architecture, configuration, or additional policies only when relevant; do not preload whole catalogs.
5. Keep target-specific facts outside reusable framework assets and verify material conclusions against current repository evidence.

## Execution And Validation

- Touch only required files, preserve unrelated changes, and use a dedicated workflow branch when the workflow gate requires it.
- Continue ordinary reversible implementation and repair within the authorized scope. Reuse existing approvals; ask only for missing authority, material scope changes, or unresolved owner decisions.
- Implementation, push, pull request, merge, Issue or Project mutation, tag, release, and publication are separate actions unless authorized together. Report their actual states separately.
- Resolve target-owned commands and working directories before validation. Run required gates and the narrowest meaningful checks; broaden or repeat only for new changes, failures, or unresolved risks.
- Record skipped, failed, and blocked checks truthfully. Do not claim completion while required gates fail or remain unverified.
- Follow `.dev/standards/GIT-COMMIT-POLICY.md` before AI-assisted commits.

## CLI Execution Routing

- After higher-priority policy selects CLI execution across shell, sandbox, host, WSL, or container boundaries, follow `.ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md` for route selection, recovery, and consent before preserving local routes.

## Repository-Specific Context

`ai-context-init` uses this section as the primary replacement zone for evidence-backed repository identity, essential entry paths, stack constraints, and local commands with their working directories. Until initialization verifies them, treat copied or placeholder facts as unresolved.

Outside this section, initialization may make only the minimal evidence-backed navigation or quick-start adjustments allowed by `.ai/assets/skills/ai-context-init/references/document-targets.md`. Preserve portable collaboration, authorization, workflow, and routing rules; link to detailed policies instead of duplicating them.
