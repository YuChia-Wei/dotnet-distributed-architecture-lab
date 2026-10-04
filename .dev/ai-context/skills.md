# Active skill registry

This project-owned navigation reflects the [current framework](CURRENT-FRAMEWORK.md)
and [saved selection](../../.ai/custom/installation.json). It does not redefine
skill behavior or prove client discovery. Select one owning route from the request,
then read its installed entry and only the needed operation references.

## Managed skills

All names below are original runtime entry names. Package metadata and instructions
under `.ai/core/skills/` own their contracts.

| Skill / package | Version | Selected purpose | Runtime entries |
| --- | --- | --- | --- |
| [adr-author](../../.ai/core/skills/adr-author/SKILL.md) | 0.1.0 | Record alternatives and mapped architectural decisions. | [Codex](../../.agents/skills/adr-author/SKILL.md), [Claude](../../.claude/skills/adr-author/SKILL.md) |
| [ai-context-auditor](../../.ai/core/skills/ai-context-auditor/SKILL.md) | 0.1.0 | Read-only context assessment or before/after comparison; export only when requested. | [Codex](../../.agents/skills/ai-context-auditor/SKILL.md), [Claude](../../.claude/skills/ai-context-auditor/SKILL.md) |
| [ai-context-governance](../../.ai/core/skills/ai-context-governance/SKILL.md) | 0.1.0 | Bounded maintenance of existing context rules, ownership, precedence and navigation. | [Codex](../../.agents/skills/ai-context-governance/SKILL.md), [Claude](../../.claude/skills/ai-context-governance/SKILL.md) |
| [ai-context-init](../../.ai/core/skills/ai-context-init/SKILL.md) | 0.2.0 | Initialize missing collaboration foundations or refresh selected factual context. | [Codex](../../.agents/skills/ai-context-init/SKILL.md), [Claude](../../.claude/skills/ai-context-init/SKILL.md) |
| [bdd-gwt-test-designer](../../.ai/core/skills/bdd-gwt-test-designer/SKILL.md) | 0.2.0 | Design or review GWT scenarios; formal-test specs and test execution remain separate. | [Codex](../../.agents/skills/bdd-gwt-test-designer/SKILL.md), [Claude](../../.claude/skills/bdd-gwt-test-designer/SKILL.md) |
| [code-reviewer](../../.ai/core/skills/code-reviewer/SKILL.md) | 0.2.0 | Read-only actionable defect review of a selected artifact or diff. | [Codex](../../.agents/skills/code-reviewer/SKILL.md), [Claude](../../.claude/skills/code-reviewer/SKILL.md) |
| [ddd-ca-hex-architect](../../.ai/core/skills/ddd-ca-hex-architect/SKILL.md) | 0.2.0 | Design or review architecture against target requirements and decisions. | [Codex](../../.agents/skills/ddd-ca-hex-architect/SKILL.md), [Claude](../../.claude/skills/ddd-ca-hex-architect/SKILL.md) |
| [diagnostic-analyst](../../.ai/core/skills/diagnostic-analyst/SKILL.md) | 0.1.0 | Investigate an observed symptom and propose a bounded repair. | [Codex](../../.agents/skills/diagnostic-analyst/SKILL.md), [Claude](../../.claude/skills/diagnostic-analyst/SKILL.md) |
| [lesson-author](../../.ai/core/skills/lesson-author/SKILL.md) | 0.2.0 | Record evidence-qualified learning and actual owner acceptance. | [Codex](../../.agents/skills/lesson-author/SKILL.md), [Claude](../../.claude/skills/lesson-author/SKILL.md) |
| [local-backlog](../../.ai/core/skills/local-backlog/SKILL.md) | 0.1.0 | Maintain explicitly selected project-owned local work items. | [Codex](../../.agents/skills/local-backlog/SKILL.md), [Claude](../../.claude/skills/local-backlog/SKILL.md) |
| [local-change-implementer](../../.ai/core/skills/local-change-implementer/SKILL.md) | 0.2.0 | Implement one authorized operation on one target and immediate call sites/tests. | [Codex](../../.agents/skills/local-change-implementer/SKILL.md), [Claude](../../.claude/skills/local-change-implementer/SKILL.md) |
| [pr-author](../../.ai/core/skills/pr-author/SKILL.md) | 0.1.0 | Author PR content against an actual Git comparison; provider writes need their own authorization. | [Codex](../../.agents/skills/pr-author/SKILL.md), [Claude](../../.claude/skills/pr-author/SKILL.md) |
| [problem-frame-author](../../.ai/core/skills/problem-frame-author/SKILL.md) | 0.1.0 | Draft or review one bounded commanded-behavior frame. | [Codex](../../.agents/skills/problem-frame-author/SKILL.md), [Claude](../../.claude/skills/problem-frame-author/SKILL.md) |
| [requirement-author](../../.ai/core/skills/requirement-author/SKILL.md) | 0.1.0 | Author selected requirements from stakeholder intent and accepted source material. | [Codex](../../.agents/skills/requirement-author/SKILL.md), [Claude](../../.claude/skills/requirement-author/SKILL.md) |
| [slice-implementer](../../.ai/core/skills/slice-implementer/SKILL.md) | 0.2.0 | Implement one authorized behavior or coordinated refactor/test slice. | [Codex](../../.agents/skills/slice-implementer/SKILL.md), [Claude](../../.claude/skills/slice-implementer/SKILL.md) |
| [software-development-orchestrator](../../.ai/core/skills/software-development-orchestrator/SKILL.md) | 0.2.0 | Coordinate the needed specialist stages, handoffs and closeout. | [Codex](../../.agents/skills/software-development-orchestrator/SKILL.md), [Claude](../../.claude/skills/software-development-orchestrator/SKILL.md) |
| [spec-author](../../.ai/core/skills/spec-author/SKILL.md) | 0.1.0 | Author production, entity, adapter or formal-test specifications. | [Codex](../../.agents/skills/spec-author/SKILL.md), [Claude](../../.claude/skills/spec-author/SKILL.md) |
| [spec-compliance-validator](../../.ai/core/skills/spec-compliance-validator/SKILL.md) | 0.1.0 | Plan evidence coverage, review semantics or assess authentic runtime evidence. | [Codex](../../.agents/skills/spec-compliance-validator/SKILL.md), [Claude](../../.claude/skills/spec-compliance-validator/SKILL.md) |

## Target knowledge and records

Resolve the applicable [target rules and request routes](TARGET-ENGINEERING-RULES.md)
and their saved bindings before .NET work. Installed `engineering-common` and
`dotnet-backend` knowledge support these routes; their presence does not adopt
every example or enable unavailable specialist coverage. Report missing coverage
without inventing a substitute acceptance claim.

[Framework configuration](../../.ai/custom/framework.json) owns the selected
stores for local work items, problem frames, ADRs, lessons and PR records.
Local-backlog does not replace this target's required GitHub work-item binding.
[Workflow policy](../standards/WORKFLOW-ARTIFACT-POLICY.md) and existing project
record owners continue to govern delivery evidence.

## Project-owned experimental entry and roles

[standards-promotion-experimental@0.1.1-alpha.1](../../.ai/custom/skills/standards-promotion-experimental/SKILL.md)
is an independently retained project copy, available through its
[Codex](../../.agents/skills/standards-promotion-experimental/SKILL.md) and
[Claude](../../.claude/skills/standards-promotion-experimental/SKILL.md) entries.
Use it only for an explicitly selected [trial](STANDARDS-PROMOTION-EXPERIMENT.md).
Its tool keeps the `standards-promotion` operation/config namespace and is outside
the official managed lock.

The six [custom roles](../../.ai/custom/roles/README.md) retain their project-owned
profiles. Optional managed sub-agent packages are not selected. An available
definition does not prove actual delegation, independent review or cost.

Old `adr`, `lesson`, `pr`, legacy init and `ai-context-upgrader` routes remain
retired. Initialization is a requested instruction operation, not an installation
side effect; use the [first-task guide](../guides/first-task.md) only for a later
selected bounded task.
