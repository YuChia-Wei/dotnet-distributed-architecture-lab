---
name: ai-context-auditor
description: Audit selected AI collaboration context read-only or compare identified context subjects using project authority and evidence. Return prose by default; export or reuse a project format only when requested.
---

# AI context auditor

Use `audit` for a scoped context question and `compare` for selected before/after
evidence. Both are instruction operations in [package metadata](skill-package.yaml).
Read [the audit and comparison method](references/audit.md) for scope, evidence,
findings and caller-selected output. The audited subject stays read-only.

Supply the context scope, relevant authority, intended behavior or comparison
question, available subject evidence and any presentation/export request. This
optional package works without governance, a framework configuration, record
store, schema, script, Python runtime or another skill. Missing evidence leaves
explicit limits; ordinary feature, review and knowledge work need no prior audit.

The declared `implemented` status means the entry, metadata and method exist.
It does not establish invocation, independent review, installation or acceptance.
