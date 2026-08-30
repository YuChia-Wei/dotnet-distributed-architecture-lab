# Delegation Run Contract

This contract records one per-independent-run delegation choice for
`ai-context-upgrader`. It composes with the shared `role_execution` contract;
it does not replace a role binding, alter route or transaction evidence, or
prove a child invocation.

## Scope And Record Boundary

- Create one record before stage execution for each independent run.
- Retain the record only with workflow execution evidence or, for direct
  conversation work, in the bounded execution evidence. It never enters target
  provenance, target customizations, a package, or a retained downstream
  transaction.
- A static projection is not current-run support or invocation evidence. An
  unknown support state remains unknown until exact evidence is retained.
- Deterministic tools and validators remain the mechanical authority. A role
  result only supplies its bounded evidence to the owning upgrader.

## Portable Execution Intent

The portable contract expresses only capability intent: root work may prefer a
`frontier` capability, bounded delegated work may prefer `balanced` capability,
and a run may be `quality-first`, `optional`, `quota-sensitive`, and require a
`disclosed` fallback. These are selection semantics, not availability,
invocation, or runtime-setting claims.

## Modes

Each record carries `selection.mode`, `selection.eligible_role_asset_ids`, and
`selection.terminal_independent_auditor_auto_selected`. Together they are the
mechanical, fail-closed mode boundary; eligibility is not an invocation claim.

| Mode | Exact eligible role IDs | Required execution meaning |
| --- | --- | --- |
| `none` | `[]` | `max_concurrent_workers` is `0`; no role is evaluated or delegated and every canonical stage is root-sequential. |
| `analysis-only` | `semantic-governance-analyst`, `fixed-head-independent-auditor` | Only the listed read-only roles may be considered. The independent auditor still needs an explicit terminal-or-high-risk selection; it is never automatic. Mechanical evidence, checksum, copy, planner, apply, receipt, build, test, and Git work remain root-driven deterministic authority. |
| `full-recommended` | all five canonical upgrader role bindings | At most two workers may be evaluated concurrently. The independent auditor remains explicitly selected only; the mode never starts it automatically. |

The mode is a run choice, not availability evidence. All modes retain the same
canonical stages in the same order:

1. `route-and-evidence-discovery`
2. `three-way-classification-and-reconciliation`
3. `semantic-customization-and-governance-analysis`
4. `plan-report-handoff-or-feedback-synthesis`
5. `terminal-fixed-head-independent-audit`

A root-sequential path satisfies the same stage obligations. A role that does
not apply is recorded through its bounded role-execution result; it is never a
silent stage omission.

## Prompt And Resume

- Ask at most once for an independent run.
- An explicit owner choice sets `decision_source: explicit-owner-choice`,
  `prompt.count: 0`, and `prompt.disposition:
  suppressed-by-explicit-choice`.
- A prompted owner choice records exactly one prompt and its decision evidence.
- A resumed run reuses the existing record and must set
  `resume.repeat_prompt: false`. It does not ask again.

## Support And Fallback Evidence

`execution_support.state` is `unknown`, `verified-available`, or
`verified-unavailable`. The latter two require exact evidence references;
`unknown` has no evidence reference and never authorizes an invocation claim.

Every fallback record has the exact fields `requested`, `observed`, `selected`,
and `owner_consent`, in addition to its authorization evidence, retained
evidence references, and preserved canonical stages. `owner_consent` exactly
matches the run's decision source. A fallback cannot be inferred from a root
path, an unavailable static projection, or a result summary.

- A `role-evaluation` fallback records `requested:
  delegation-evaluation`, `observed: delegation-support-unavailable`, and
  `selected: root-sequential`; it preserves all five stages.
- A `terminal-independent-audit` fallback records `requested:
  terminal-independent-audit`, `observed:
  primary-independent-auditor-unavailable`, and `selected:
  fresh-independent-context`; it preserves only the terminal stage.

Neither fallback is accepted silently. The record does not erase earlier
role-execution attempts or their invocation evidence.

## Terminal Independent Audit

The terminal audit is always required for a terminal release or high-risk gate,
but it is selected only by an explicit terminal-or-high-risk basis. Routine
work, a static profile, and the selected mode do not start it automatically.

Its result is fail closed: only `passed`, bound to one exact clean subject and
retained evidence, can satisfy the terminal audit gate. `pending`, `failed`,
and `blocked` do not pass it. A fallback audit remains fresh and independent.

## Projection Boundary

Runtime-specific preferences live only in their own projection. They are
advisory, do not change the portable run record, and cannot block an otherwise
valid root-sequential path solely because a static preference differs. Deferred
projections remain deferred rather than being treated as permanent rejection.
