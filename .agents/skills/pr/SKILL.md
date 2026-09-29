---
name: pr
description: "Prepare content-bound pull request records and explicitly authorized GitHub PR operations."
---

# pr

Codex runtime entry for `pr@0.1.0`. This generated projection does not
prove installation, operation execution, validation or runtime discovery.
Regenerate it from the selected package and verified Codex adapter.

Read [the installed skill](../../../.ai/core/skills/pr/SKILL.md) for its declared operations.
Resolve [the installed metadata](../../../.ai/core/skills/pr/skill-package.yaml) with the installed skill
directory as the explicit `package_root`.

Obtain the caller's explicit `project_root`, configuration selection and operation. The project-owned `.ai/custom/framework.json` is not supplied by this entry. Pass the chosen configuration path explicitly under the installed skill's contract; do not infer it from the current working directory.

Selected installed skill members:

- [references/configuration.md](../../../.ai/core/skills/pr/references/configuration.md)
- [references/example.md](../../../.ai/core/skills/pr/references/example.md)
- [references/github.md](../../../.ai/core/skills/pr/references/github.md)
- [references/operations.md](../../../.ai/core/skills/pr/references/operations.md)
- [schemas/pr-record.schema.json](../../../.ai/core/skills/pr/schemas/pr-record.schema.json)
- [scripts/github.py](../../../.ai/core/skills/pr/scripts/github.py)
- [scripts/pr.py](../../../.ai/core/skills/pr/scripts/pr.py)
- [templates/pr.md](../../../.ai/core/skills/pr/templates/pr.md)

For metadata version 4, `knowledge_consumption` declares exact knowledge package
versions, operations and resource IDs. Follow the installed skill's selected
binding to access knowledge. An optional missing package or resource makes the
named coverage unavailable; do not assume it was installed or promise that
coverage. Required dependencies must be present before the operation is used.

For metadata versions 1–3, follow the declared operation and runtime contracts.
An instruction operation means read its declared instructions; a tool operation
uses its declared tool. This entry does not supply methods or provider calls.
