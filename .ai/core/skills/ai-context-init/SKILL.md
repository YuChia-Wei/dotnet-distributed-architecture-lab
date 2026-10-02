---
name: ai-context-init
description: Initialize project-owned collaboration context and a suitable project documentation structure, or refresh that initialized context from repository evidence. Preserve existing AGENTS rules and custom content. Does not install, upgrade or repair framework packages.
---

# AI context initialization

Use `initialize` for a new collaboration entry and project context, including an
existing codebase that lacks them. Use `refresh` for a bounded update to those
documents. For unrelated context changes, select the target's maintenance route
when available; it is not a dependency of this package.

Read [the initialization method](references/initialize.md) for either operation.
Read [project structure guidance](references/project-structure.md) when selecting
document destinations or initializing an empty repository. The
[AGENTS seed](templates/public-root/AGENTS.md) evolves the former init baseline:
retain its collaboration intent, resolve navigation from the actual target and
derive repository facts from evidence. These are authoring resources, not files
to copy indiscriminately or schema-bound records.

The caller supplies the target, intended operation and authorized write scope.
Infer established layout and facts from permitted sources; ask only for material
choices that evidence cannot resolve. Return a proposal when writes are not
requested. An initialization request authorizes ordinary project document edits
within its scope; an already authorized edit needs no second approval gate.

No mandatory runtime, configuration, record store, framework installation or
other skill is required. Ordinary file tools author target-owned documents.
`implemented` describes these instructions, not observed agent behavior, client
discovery, target readiness, installation or release acceptance.
