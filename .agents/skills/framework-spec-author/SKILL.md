---
name: framework-spec-author
description: "Draft or normalize a selected production, entity, adapter or formal-test specification using caller-supplied sources, target contracts, templates and destinations. Preserve source bindings, accepted scope and unresolved choices."
---

# framework-spec-author

Generated development entry for `spec-author@0.1.0`. This entry does not prove
installation, operation execution, validation or stable publication. It is an
owned projection; change the package or adapter source and regenerate it.

Read [the installed skill](../../../.ai/core/skills/spec-author/SKILL.md) for its instructions. Resolve
package resources from [the installed metadata](../../../.ai/core/skills/spec-author/skill-package.yaml), using the
installed package directory as the explicit `package_root`.

This package declares `configuration: null`. It needs no framework configuration file or managed record store. Do not resolve or create either for this package. Obtain only the target inputs required by the selected operation.

Installed resources:

- [references/adapter-template.md](../../../.ai/core/skills/spec-author/references/adapter-template.md)
- [references/authoring.md](../../../.ai/core/skills/spec-author/references/authoring.md)
- [references/entity-template.md](../../../.ai/core/skills/spec-author/references/entity-template.md)
- [references/formal-test-template.md](../../../.ai/core/skills/spec-author/references/formal-test-template.md)
- [references/production-template.md](../../../.ai/core/skills/spec-author/references/production-template.md)

Use only the installed skill's declared operation interface. In metadata v3,
`execution: instruction` means read the declared `instructions` reference as an
agent method; it is not a command or executable. `execution: tool` means use the
declared tool and its operation contract. Metadata v1/v2 operations retain their
declared tool interface. Builders do not execute either kind of operation.

Apply runtime requirements only to their declared `for_operations`; an unavailable
requirement makes those operations unavailable. A source status of `implemented`
means the deliverable exists, not that it ran or was verified. A development
identity grants no writes, record migration or activation of another installation.
