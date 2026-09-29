# Agent-facing AI context

This target keeps selected RC2 skill and knowledge packages under `.ai/core/`, explicit project settings and desired selection under `.ai/custom/`, and the installer-owned `.ai/framework.lock`. Read the [index](INDEX.MD) and [current target contract](../.dev/ai-context/CURRENT-FRAMEWORK.md) before treating any package as installed or effective.

Project architecture, operations, specifications, workflows and effective engineering decisions live in `.dev/` and product source. Codex and Claude discovery entries live under `.agents/skills/` and `.claude/skills/`; they are projections, not independent authority. The previous `.ai/assets` tree has been retired. `.ai/scripts/` retains only the four checks called by current target policy and their prerequisite closure; the current-framework admission gate remains unconfigured.
