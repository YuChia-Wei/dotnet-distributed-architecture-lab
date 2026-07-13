# Directory Rules

This file is an agent-facing operational summary. The canonical policies are:

- `.dev/standards/AI-CONTEXT-BOUNDARY.md`
- `.dev/standards/AI-CONTEXT-LANGUAGE-POLICY.md`

## Placement Rules

- Put reusable agent-facing AI context under `.ai/`.
- Put canonical reusable AI assets under `.ai/assets/`.
- Put universal shared context under `.ai/assets/shared/`.
- Put tech-stack-specific reusable context under `.ai/assets/tech-stacks/<profile>/`.
- Put canonical skill specs under `.ai/assets/skills/<skill-id>/`.
- Put canonical delegated sub-agent role prompts under `.ai/assets/sub-agent-role-prompts/<role-id>/`.
- Put human-facing guides, requirements, specs, operations docs, standards, and workflow artifacts under `.dev/`.
- Put runtime-specific wrappers under `.agents/skills/` and `.claude/skills/`.

## README And INDEX Rule

- README files explain the purpose, scope, and usage of the containing folder.
- INDEX files own file and directory inventories, including per-file or per-directory descriptions.
- Do not duplicate the same catalog in both README and INDEX.

## Decision Checklist

Before creating or moving AI context, decide:

1. Can this content be reused across non-.NET repositories without rewrite?
   - Use universal context under `.ai/assets/shared/`.
2. Is it reusable only for the current .NET backend profile?
   - Use `.ai/assets/tech-stacks/dotnet-backend/`.
3. Is it project truth, a requirement, spec, operation fact, workflow record, or decision?
   - Use `.dev/`.
4. Is it a runtime entry for a specific agent tool?
   - Use `.agents/skills/` or `.claude/skills/`.
5. Is it primarily for human onboarding or workflow usage?
   - Use `.dev/guides/`.

## Validation Hints

Use `rg -uu` when scanning hidden context directories such as `.ai`, `.dev`, `.agents`, and `.claude`.
