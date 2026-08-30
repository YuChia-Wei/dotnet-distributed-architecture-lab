# Agent Execution Guardrails Contract

## Purpose

This contract binds delegated, external, and fixed-head agent work to an exact
subject, explicit authority, exclusive tracked-writer ownership, and evidence
that cannot be upgraded from a synthetic substitute. It complements, rather
than replaces, `ROLE-EXECUTION-CONTRACT.md` and the external-task terminal
transport contract.

## Pre-dispatch packet

Every delegated, external, or fixed-head execution must validate one
`agent-execution-packet` before dispatch. The packet identifies the owning
skill, canonical role path and applicability, exact repository SHA, complete
argv and working directory, permissions, ignored artifact roots, terminal
schema and one-shot callback/event-wait transport, integration owner, stop
conditions, retry budget, and current attempt authorization.

The validator resolves the owning skill's tracked canonical `skill.yaml`,
requires the named role to be an active tracked canonical role asset, and
requires that exact role path to appear in the skill's `role_bindings`.
External dispatch additionally loads the contained packet, validates its
internal canonical seal, binds the exact packet file-byte digest, and compares
subject, argv, cwd, and integration owner. A path-shaped assertion is not a
packet binding.

Static role availability is not invocation evidence. Fixed-head auditors and
external validators are read-only. Attempt three or later requires a new owner
or workflow authorization reference that was not consumed by an earlier
attempt.

## Worktree snapshot lease

A machine-readable lease binds one worktree snapshot and packet holder. An
active tracked-writer lease rejects any other observed tracked writer. Read-only
agents may coexist, and validation may write only beneath declared ignored
artifact roots. A terminal lease is `released` only after ignored output is
sealed or released and no tracked drift exists; otherwise it is `invalidated`.
The snapshot digest is derived from the observed HEAD and tracked status and is
checked against live Git state. An active holder uses a digest-bound ignored
lock whose canonical validator acquisition uses create-new semantics; an
existing lock fails before execution.

## Acceptance and report parity

An acceptance ledger maps each Issue acceptance identifier independently to
its evidence kind, exact command/profile/subject, outcome, evidence references,
and digest. The human report projection must contain the same identifiers,
outcomes, and digests. An acceptance marked `requires_actual_execution` may be
satisfied only by `actual-execution`; mock, fixture, synthetic, or unit evidence
remains supporting evidence and cannot be relabeled.
Every `actual-execution` entry carries a separately sealed terminal command
receipt with matching subject, command, profile, timing, outcome, exit code,
and evidence digest. It must state `executed: true` and `synthetic: false`;
fixture-only references are rejected as actual execution.
The entry must also name contained ignored receipt and output files. The
validator loads both files, verifies their exact byte digests, compares the
persisted receipt with the ledger copy, and rejects a missing or path-shaped
reference. A self-sealed mapping without those repository artifacts is not
actual execution evidence.

## Retry and failure identity

Failure fingerprints contain only stable metadata: failure class, command
digest, subject SHA, environment class, and bounded diagnostic codes. A retry
requires a material state-change digest. Attempt three or later additionally
requires fresh owner or workflow authorization. Repeating an unchanged failure
is a stopped attempt, not new validation.
Fresh authorizations are individually sealed and bind the exact attempt,
subject, prior failure, and authorize-retry decision; their digests must differ
from prior authorization.
Attempt-three packets and retry records load the referenced workflow-local
authorization, validate its canonical seal, and require its attempt, subject,
prior failure, and single consuming packet identity to match. A prefix or an
unresolved reference is not authorization.

## Code graph freshness

Graph discovery records the index SHA, head SHA, and coverage. A stale, missing,
partial, or unknown graph must be reindexed or replaced by a tracked-file
fallback over explicit paths. Search absence is evidence only from an exact-head
complete index or such a tracked fallback; graph search alone is never proof of
absence.
Fallback paths must be contained repository-relative paths with tracked content;
an absolute or untracked search root is rejected.

## PowerShell safety

Scripts and generated snippets must not assign to PowerShell automatic or
reserved variables, case-insensitively. Use purpose-specific names such as
`$taskHost`, never `$Host`, `$PID`, `$HOME`, `$Error`, or `$Matches`.
