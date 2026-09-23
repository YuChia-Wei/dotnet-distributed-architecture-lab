---
name: ai-context-governance
description: Propose or apply a bounded authorized change to project-owned AI context. Preserve semantic authority, custom content and protected managed files; optionally hand useful candidates to project-selected knowledge tools.
---

# AI context governance

Use `propose` for reviewable changes and `apply` for an authorized proposal or
bounded direct edit. Both are instruction operations in
[package metadata](skill-package.yaml). Read [the maintenance method](references/maintenance.md)
for ownership, current-byte checks, semantic state and optional knowledge handoffs.

Supply the problem or direct request, selected files, ownership, relevant
authority and intended behavior. An already-authorized edit needs no separate
proposal or repeated permission gate. Audit, assessment, workflow and other
skills are not package prerequisites; actual project requirements still apply.

This independently optional package needs an instruction reader and permitted
project access. It requires no framework configuration, record store, schema,
script, Python runtime or other skill. Ordinary feature, review and knowledge
work need no prior maintenance. `implemented` means these source instructions
exist, not that they were invoked, installed, independently reviewed or accepted.
