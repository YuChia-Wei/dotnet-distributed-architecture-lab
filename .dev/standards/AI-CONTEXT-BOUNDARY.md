# AI Context Boundary

This standard defines where AI collaboration context belongs and how to separate reusable context from .NET backend-specific context and repo-specific truth.

## Context Classes

| Class | Meaning | Primary Location |
| --- | --- | --- |
| Universal AI context | Agent-loading projections and execution context reusable across repositories and technology stacks. | `.ai/assets/shared/` |
| Skill context | Canonical top-level skill specs and skill references. | `.ai/assets/skills/` |
| Sub-agent context | Delegated worker role prompts and references. | `.ai/assets/sub-agent-role-prompts/` |
| Tech-stack context | Agent-loading projections and execution context tied to a specific stack profile. | `.ai/assets/tech-stacks/<profile>/` |
| Runtime wrapper context | Thin runtime entries for a specific agent tool. | `.agents/skills/`, `.claude/skills/` |
| Project truth and normative standards | Requirements, domain language, specs, operations, architecture facts, workflows, decisions, and canonical rule semantics. | `.dev/` |
| Human guide | Human-facing explanations, tutorials, and prompt usage guides. | `.dev/guides/` |

## Current Tech-Stack Profile

The current specialized profile is:

```text
dotnet-backend
```

It covers .NET backend systems using DDD, Clean Architecture, CQRS, repository patterns, persistence, message integration, testing, and backend host configuration.

It explicitly excludes Razor, Blazor, MAUI, ASP.NET MVC view rendering, and other .NET frontend UI frameworks. Those belong to a future full-stack or UI-specific template/profile.

## Placement Rules

- Put repo-agnostic agent-loading projections in `.ai/assets/shared/`.
- Put .NET backend-only agent-loading projections in `.ai/assets/tech-stacks/dotnet-backend/`.
- Put normative rule semantics and ownership declarations in `.dev/standards/`; projections cite the registered rule IDs and canonical documents.
- Put canonical skill specs in `.ai/assets/skills/<skill-id>/`.
- Put delegated worker role definitions in `.ai/assets/sub-agent-role-prompts/<role-id>/`.
- Put Codex runtime wrappers in `.agents/skills/<skill-id>/`.
- Put Claude-compatible wrappers in `.claude/skills/<skill-id>/`.
- Put project requirements, domain language, specs, operations truth, workflow artifacts, and architecture facts under `.dev/`.
- Put human-facing guides under `.dev/guides/`.

## Folder First, Metadata Second

Folder placement is the primary classification mechanism. Metadata is useful only for machine-readable canonical assets such as:

- `skill.yaml`
- `sub-agent.yaml`
- prompt package YAML files
- workflow task JSON files
- registry or schema files

Do not add frontmatter or scope metadata to every Markdown file just to classify it. Prefer moving the file to the correct folder or linking it from a clear index.

## Decision Checklist

Before creating or moving an AI context file, answer these questions:

1. Can this file be reused across non-.NET repositories without rewrite?
   - Yes: use universal AI context.
2. Is it reusable only for .NET backend repositories?
   - Yes: use `tech-stacks/dotnet-backend`.
3. Does it describe this repo's actual domains, ubiquitous language, services, queues, specs, operations, or workflow state?
   - Yes: use `.dev/`.
4. Is it only a runtime entry for a specific agent?
   - Yes: use a thin wrapper under `.agents/` or `.claude/`.
5. Is it meant primarily for humans to learn or invoke a workflow?
   - Yes: use `.dev/guides/`.

## Anti-Patterns

- Do not hide .NET backend rules in universal shared context.
- Do not duplicate canonical skill instructions in runtime wrappers.
- Do not put project-specific requirements or specs under `.ai/`.
- Do not use a frontend or full-stack folder for the current .NET backend-only profile unless a separate profile is explicitly created.
- Do not rely on metadata when folder placement can express the boundary.
- Do not let a projection, wrapper, checklist, or example become a second normative owner through repeated `MUST` language.

## Rule Ownership

See [AI Context Rule Ownership](AI-CONTEXT-OWNERSHIP.md) and its machine-readable
[registry](AI-CONTEXT-OWNERSHIP.yaml). Folder placement classifies the context;
the registry resolves normative ownership when the same rule is consumed across
multiple surfaces.
