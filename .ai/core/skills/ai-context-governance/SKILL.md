---
name: ai-context-governance
description: Maintain existing project-owned AI context by proposing or applying bounded changes to rules, document responsibilities, precedence and navigation. Use for ongoing context maintenance and conflict reconciliation; preserve custom content and protected managed files.
---

# AI context governance

Choose this skill by default for ongoing maintenance of existing project-owned
context, including reconciling contradictory rules or changing document ownership.
Establishing missing context foundations belongs to initialization; read-only
findings or before/after comparison belong to audit. A specifically requested
factual refresh of initialized context may remain with `ai-context-init`; this
skill can also maintain those facts within an authorized context edit. Select by
the requested outcome and target route, not by which skill first created a file.
These adjacent capabilities are optional and need not be installed.

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
