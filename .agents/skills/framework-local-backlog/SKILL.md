---
name: framework-local-backlog
description: "Create and update project-owned local work items with explicit state and conflict checks."
---

# framework-local-backlog

Generated development entry for `local-backlog@0.1.0`. This entry does not prove
installation, operation execution, validation or stable publication. It is an
owned projection; change the package or adapter source and regenerate it.

Read [the installed skill](../../../.ai/core/skills/local-backlog/SKILL.md) for its instructions. Resolve
package resources from [the installed metadata](../../../.ai/core/skills/local-backlog/skill-package.yaml), using the
installed package directory as the explicit `package_root`.

Obtain the caller's explicit `project_root`, configuration selection and operation. This project's selected configuration convention is `.ai/custom/framework.json`; it remains project-owned and is not supplied by this entry. Pass any chosen configuration path explicitly under the installed skill's configuration contract. Do not infer settings from the current working directory.

Installed resources:

- [references/configuration.md](../../../.ai/core/skills/local-backlog/references/configuration.md)
- [references/example.md](../../../.ai/core/skills/local-backlog/references/example.md)
- [references/operations.md](../../../.ai/core/skills/local-backlog/references/operations.md)
- [schemas/local-backlog-record.schema.json](../../../.ai/core/skills/local-backlog/schemas/local-backlog-record.schema.json)
- [scripts/local_backlog.py](../../../.ai/core/skills/local-backlog/scripts/local_backlog.py)
- [templates/work-item.md](../../../.ai/core/skills/local-backlog/templates/work-item.md)

Use only the installed skill's declared operation interface. In metadata v3,
`execution: instruction` means read the declared `instructions` reference as an
agent method; it is not a command or executable. `execution: tool` means use the
declared tool and its operation contract. Metadata v1/v2 operations retain their
declared tool interface. Builders do not execute either kind of operation.

Apply runtime requirements only to their declared `for_operations`; an unavailable
requirement makes those operations unavailable. A source status of `implemented`
means the deliverable exists, not that it ran or was verified. A development
identity grants no writes, record migration or activation of another installation.
