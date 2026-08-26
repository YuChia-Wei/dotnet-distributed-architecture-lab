# Delegation Rules

Use these rules after the low-cost inventory pass decides whether to stay local or escalate.

## Update Directly on the Current Pass

These are usually safe for the low-cost pass to update directly when the facts are clear:

- file and directory index tables
- stack-version tables sourced from project files
- quick-start links and doc-entry references
- wording that replaces stale repo names with current file-backed names
- simple architecture bullets that mirror confirmed project layout

## Prefer Stronger Model or Sub-Agent

These are material-value triggers only. Keep the role-execution safety gates
and direct-by-default rule in `role-execution.md`; synthesis need alone does
not authorize delegation.

Delegate these when the rewrite needs synthesis instead of substitution and
the role-execution contract permits it:

- `.dev/ARCHITECTURE.md` full narrative rewrite
- `AGENTS.md` rule sections that need architectural reinterpretation
- cross-document conflict resolution where one change affects several docs
- module or bounded-context naming normalization
- mixed-stack partitioning or multi-solution ownership explanation

## Use The Low-Cost Context Translator

After the target-specific English `AGENTS.md` is finalized, translation into
`AGENTS.zh-TW.md` is a bounded derived task. Evaluate the `context-translator`
binding and apply its loaded stage contract directly or through a genuine
delegation. Do not translate before the English rewrite is complete, and do not
fall back to the main high-cost agent when the requested low-cost runtime/model
is unavailable; record the applicable role as unavailable and defer the
translation instead.
