---
name: framework-pr
description: "Prepare content-bound pull request records and explicitly authorized GitHub PR operations."
---

# framework-pr

Generated development entry for `pr@0.1.0`. This entry does not prove
installation, operation execution, validation or stable publication. It is an
owned projection; change the package or adapter source and regenerate it.

Read [the installed skill](../../../.ai/core/skills/pr/SKILL.md) for its instructions. Resolve
package resources from [the installed metadata](../../../.ai/core/skills/pr/skill-package.yaml), using the
installed package directory as the explicit `package_root`.

Obtain the caller's explicit `project_root`, configuration selection and operation. This project's selected configuration convention is `.ai/custom/framework.json`; it remains project-owned and is not supplied by this entry. Pass any chosen configuration path explicitly under the installed skill's configuration contract. Do not infer settings from the current working directory.

Installed resources:

- [references/configuration.md](../../../.ai/core/skills/pr/references/configuration.md)
- [references/example.md](../../../.ai/core/skills/pr/references/example.md)
- [references/github.md](../../../.ai/core/skills/pr/references/github.md)
- [references/operations.md](../../../.ai/core/skills/pr/references/operations.md)
- [schemas/pr-record.schema.json](../../../.ai/core/skills/pr/schemas/pr-record.schema.json)
- [scripts/github.py](../../../.ai/core/skills/pr/scripts/github.py)
- [scripts/pr.py](../../../.ai/core/skills/pr/scripts/pr.py)
- [templates/pr.md](../../../.ai/core/skills/pr/templates/pr.md)

Use only the installed skill's declared operation interface. In metadata v3,
`execution: instruction` means read the declared `instructions` reference as an
agent method; it is not a command or executable. `execution: tool` means use the
declared tool and its operation contract. Metadata v1/v2 operations retain their
declared tool interface. Builders do not execute either kind of operation.

Apply runtime requirements only to their declared `for_operations`; an unavailable
requirement makes those operations unavailable. A source status of `implemented`
means the deliverable exists, not that it ran or was verified. A development
identity grants no writes, record migration or activation of another installation.
