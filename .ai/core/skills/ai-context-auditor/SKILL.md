---
name: ai-context-auditor
description: Assess selected AI collaboration context for evidence-backed findings or compare identified before/after subjects while keeping the subject read-only. Use for context assessment, not initialization or maintenance edits; export a report only when requested.
---

# AI context auditor

Choose this skill when the requested result is findings, coverage or a comparison.
Creating missing context belongs to initialization; changing existing project-owned
rules, responsibilities or navigation belongs to authorized maintenance. An audit
can recommend that work without performing it. Neither initialization nor a direct
maintenance edit needs a prior audit unless the target's actual policy requires it;
other context skills are optional, not installation prerequisites.

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
