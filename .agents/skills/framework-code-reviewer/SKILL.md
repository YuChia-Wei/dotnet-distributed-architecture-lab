---
name: framework-code-reviewer
description: "Review a bounded code or implementation-guidance scope for actionable defects using intended behavior, target-owned rules and evidence; report uncertainty and coverage without applying fixes."
---

# framework-code-reviewer

Generated development entry for `code-reviewer@0.1.0`. This entry does not prove
installation, operation execution, validation or stable publication. It is an
owned projection; change the package or adapter source and regenerate it.

Read [the installed skill](../../../.ai/core/skills/code-reviewer/SKILL.md) for its instructions. Resolve
package resources from [the installed metadata](../../../.ai/core/skills/code-reviewer/skill-package.yaml), using the
installed package directory as the explicit `package_root`.

This package declares `configuration: null`. It needs no framework configuration file or managed record store. Do not resolve or create either for this package. Obtain only the target inputs required by the selected operation.

Installed resources:

- [references/review.md](../../../.ai/core/skills/code-reviewer/references/review.md)

Use only the installed skill's declared operation interface. In metadata v3,
`execution: instruction` means read the declared `instructions` reference as an
agent method; it is not a command or executable. `execution: tool` means use the
declared tool and its operation contract. Metadata v1/v2 operations retain their
declared tool interface. Builders do not execute either kind of operation.

Apply runtime requirements only to their declared `for_operations`; an unavailable
requirement makes those operations unavailable. A source status of `implemented`
means the deliverable exists, not that it ran or was verified. A development
identity grants no writes, record migration or activation of another installation.
