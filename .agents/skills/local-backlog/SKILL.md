---
name: local-backlog
description: "Create and update project-owned local work items with explicit state and conflict checks."
---

# local-backlog

Codex runtime entry for `local-backlog@0.1.0`. This generated projection does not
prove installation, operation execution, validation or runtime discovery.
Regenerate it from the selected package and verified Codex adapter.

Read [the installed skill](../../../.ai/core/skills/local-backlog/SKILL.md) for its declared operations.
Resolve [the installed metadata](../../../.ai/core/skills/local-backlog/skill-package.yaml) with the installed skill
directory as the explicit `package_root`.

Obtain the caller's explicit `project_root`, configuration selection and operation. The project-owned `.ai/custom/framework.json` is not supplied by this entry. Pass the chosen configuration path explicitly under the installed skill's contract; do not infer it from the current working directory.

Selected installed skill members:

- [references/configuration.md](../../../.ai/core/skills/local-backlog/references/configuration.md)
- [references/example.md](../../../.ai/core/skills/local-backlog/references/example.md)
- [references/operations.md](../../../.ai/core/skills/local-backlog/references/operations.md)
- [schemas/local-backlog-record.schema.json](../../../.ai/core/skills/local-backlog/schemas/local-backlog-record.schema.json)
- [scripts/local_backlog.py](../../../.ai/core/skills/local-backlog/scripts/local_backlog.py)
- [templates/work-item.md](../../../.ai/core/skills/local-backlog/templates/work-item.md)

For metadata version 4, `knowledge_consumption` declares exact knowledge package
versions, operations and resource IDs. Follow the installed skill's selected
binding to access knowledge. An optional missing package or resource makes the
named coverage unavailable; do not assume it was installed or promise that
coverage. Required dependencies must be present before the operation is used.

For metadata versions 1–3, follow the declared operation and runtime contracts.
An instruction operation means read its declared instructions; a tool operation
uses its declared tool. This entry does not supply methods or provider calls.
