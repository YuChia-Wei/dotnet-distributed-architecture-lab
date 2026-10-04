# AI collaboration resources

This project-owned entry describes the selected framework resources. Product
facts and adopted rules belong to this repository; see the
[project guide](../AGENTS.md), [saved installation selection](custom/installation.json)
and [resource index](INDEX.MD).

- [Managed skills](core/skills/) and [knowledge](core/knowledge/) are installer-owned.
  Select an installed operation through the [Codex](../.agents/skills/) or
  [Claude](../.claude/skills/) entries and the saved installation selection.
- [Installation selection](custom/installation.json) records the selected packages,
  adapters and target knowledge bindings. [framework.lock](framework.lock) is the
  installer-generated inventory; never hand-edit it.
- [Project configuration](custom/framework.json) preserves selected artifact stores
  and write-root constraints. It is separate from the optional
  [product inventory](../.dev/project-config.yaml).
- [Custom roles](custom/roles/README.md) and the
  [experimental promotion skill](custom/skills/standards-promotion-experimental/SKILL.md)
  remain project-owned. Their presence does not prove invocation or acceptance.

The initialized root entries, indexes and guides are project-owned documents.
A framework upgrade does not automatically replace their rules or product facts.
The [0.19.0 local trial results](../.dev/workflows/2026-10-04-framework-019-init/results.md)
record the installation and init 0.2.0 trial within their original scope; they do
not establish current runtime acceptance or main integration.
