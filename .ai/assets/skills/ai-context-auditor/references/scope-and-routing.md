# AI Context Audit Scope And Routing

## Default Included Surfaces

Start from an allowlist instead of a whole-repository recursive scan:

- root collaboration entries such as `AGENTS.md`, `CLAUDE.md`, translated entry companions, and repository README files;
- `.ai/**`;
- `.dev/**` governance, standards, guides, requirements, specs, operations, and workflows;
- `.agents/**` and `.claude/**` runtime wrappers;
- `.github/**` files that declare AI assistant instructions, prompts, or collaboration behavior;
- other context roots explicitly declared by repository instructions or indexes;
- context validation scripts and tool manifests when directly referenced by AI context documentation.

Inspect linked files outside these roots only when necessary to verify a context claim. Prefer manifests, configuration, README files, and indexes over implementation source.

## Default Exclusions

Do not scan these as part of an AI context audit:

- `src/**`;
- `tests/**` and `test/**`;
- `app/**` and `apps/**` when they contain product implementation;
- product feature, domain, application, infrastructure, adapter, or test implementation trees;
- generated output such as `bin/**`, `obj/**`, `dist/**`, `build/**`, and coverage output;
- dependency or vendor trees such as `node_modules/**`, `packages/**`, and `vendor/**`;
- `.git/**` contents, except read-only Git metadata commands needed for repository state.

Repository-specific instructions may add exclusions. Do not remove these code exclusions merely because the audit request says "scan everything"; clarify the boundary first.

## Code Review Handoff Gate

Stop before scanning code when any of these is true:

- the user names a C#, source, test, project, solution, feature, handler, controller, aggregate, repository, or other implementation target;
- the requested outcome is code quality, implementation architecture compliance, bugs, security, performance, or test adequacy;
- answering would require reading product implementation rather than context metadata or documentation.

Respond with:

1. the AI context audit boundary;
2. the source or test paths that were not scanned;
3. the recommended review skill, normally `code-reviewer` for this repository;
4. a suggested invocation or handoff prompt.

Do not silently run both audits. Use another skill only after the user authorizes or explicitly requests the code review.

## Related Skill Boundaries

| Need | Route |
| --- | --- |
| Conversation-only read-only AI context health, drift, or structure analysis | `ai-context-auditor` in transient direct mode |
| Read-only AI context audit with a repository-persisted report | `ai-context-auditor` in standalone assessment mode |
| AI context cleanup, moves, language changes, wrapper sync, or policy changes | `ai-context-governance` |
| Product .NET source or test review | `code-reviewer` |
| Audit finding triage, multi-stage AI context remediation, post-audit coordination, and closure | `ai-context-governance` |
| Target repo initialization after copying the framework | `repo-structure-sync` |
