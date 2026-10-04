# AI collaboration resources

This project-owned entry describes the selected framework resources. Product
facts and adopted rules belong to this repository; see the
[project guide](../AGENTS.md), [current installation](../.dev/ai-context/CURRENT-FRAMEWORK.md)
and [resource index](INDEX.MD).

- [Managed skills](core/skills/) and [knowledge](core/knowledge/) are installer-owned.
  Select an operation through the [active skill registry](../.dev/ai-context/skills.md).
- [Installation selection](custom/installation.json) records the selected packages,
  adapters and target knowledge bindings. [framework.lock](framework.lock) is the
  installer-generated inventory; never hand-edit it.
- [Project configuration](custom/framework.json) preserves selected artifact stores
  and write-root constraints. It is separate from the optional
  [product inventory](../.dev/project-config.yaml).
- [Custom roles](custom/roles/README.md) and the
  [experimental promotion skill](custom/skills/standards-promotion-experimental/SKILL.md)
  remain project-owned. Their presence does not prove invocation or acceptance.
- [Target check scripts](scripts/README.md) have bounded purposes. They do not
  replace the unconfigured target framework admission gate.

The initialized root entries, indexes and guides are project-owned documents.
A framework upgrade does not automatically replace their rules or product facts.
