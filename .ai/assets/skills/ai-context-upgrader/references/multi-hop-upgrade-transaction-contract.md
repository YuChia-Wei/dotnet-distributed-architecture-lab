# Multi-Hop Upgrade Transaction Contract

## Purpose And Boundary

`ai-context-multi-hop-upgrade` is the outer target-local transaction for one
resolver-selected multi-hop route. Its durable outer state lives only under the
target repository Git-admin directory:

```text
<target-git-dir>/ai-context-multi-hop-upgrade/<route-transaction-id>/
  route-matrix.yaml
  resolver-result.json
  route-intent.json
  journal.yaml
  hops/0000/
    <archive-file-name>
    checksum.sha256
    migration.yaml
    validator.asset
    extracted/<single-archive-envelope>/
    validator.stdout.log
    validator.stderr.log
    validator-execution.json
    preparation.json                     # temporary, pre-child only
    evidence.json                        # canonical promoted-hop binding
  checkpoints/0000.pending-receipt.yaml
  checkpoints/0000.json
  .preparing-hops/0000-<opaque-attempt>/ # non-authoritative staging only
  failed-preparations/0000-<opaque-attempt>/
    failure.json                         # retained non-authoritative failure
    hops/0000/                           # partial attempt bytes, if any

<target-git-dir>/ai-context-package-apply/<child-transaction-id>/
  plan.json
  journal.yaml
  remediation-packet.json
  remediation-decision.json
  incoming-validation-receipt.json
  target-validation-receipt.json
  terminal-receipt.json
```

The outer transaction coordinates the existing child package-apply
transaction; it does not replace or reimplement it. A child plan remains
schema `2.2.0` and a child journal remains
`ai-context-package-apply-journal/v5`. The child transaction plan and journal
remain only at `ai-context-package-apply/<child-transaction-id>/`; neither is
duplicated into the outer route transaction. The short-lived canonical
`hops/NNNN/preparation.json` uses the plan schema as a pre-decision proposal,
but it is not child transaction evidence and must be removed when the child
transaction has been created.

The v5 child journal binds an append-only `progress.jsonl` digest chain. Each
completed child operation or rollback path is fsynced before the next mutation;
snapshot writes compact lifecycle state and bind the applied record count/tail
without rewriting the completed prefix after every operation. Route recovery
never uses a v4 child journal.

The formal machine contract is
`templates/multi-hop-upgrade-transaction.schema.yaml`; start from
`templates/multi-hop-upgrade-transaction.template.yaml`.

## Sealed Resolver Result, Intent, Matrix, And Indexes

The raw matrix is retained exactly once at the fixed path `route-matrix.yaml`.
Begin also writes one immutable canonical JSON `resolver-result.json`, schema
`ai-context-multi-hop-upgrade-resolver-result/v1`. Its exact top-level fields
are `schema_version`, `origin`, `target`, `matrix`, `route_kind`, and
`selected_route`. `matrix` has exactly `matrix_id`, `sha256`, and
`byte_length`; `route_kind` is exactly `orchestrated-multi-hop`; and
`selected_route` has exactly `route_id`, `edge_count`, and the complete,
ordered selected S1 `edges` mappings. The full edges retain the selected
matrix-relative artifact and validation identities needed to prove promoted
hop evidence; they are not an alternate raw matrix.

The retained resolver result is path-free with respect to the external source:
it contains no external matrix root, absolute source path, source locator, or
provider/credential state. Matrix-defined safe relative asset paths inside a
full selected edge are not an external source root. The outer transaction
therefore has durable S1 selection evidence without retaining a local machine
path that later validation could accidentally trust.

The immutable canonical JSON `route-intent.json` binds the fixed raw-matrix
path, raw digest, and byte length; target root and starting commit; resolver
origin/target; a `resolver_result` identity with exact
`path: resolver-result.json`, raw canonical-byte SHA-256, and byte length; and
the selected route's compact ordered edge identities. The compact intent route
ID and each compact edge identity must project exactly from the retained full
result. It never copies raw matrix content, full resolver-result content,
package artifact records, validator records, remediation packets, owner
decisions, or future child transaction IDs.

`route_transaction_id` means exactly SHA-256 of canonical route-intent JSON
after omitting only its `route_transaction_id` field. It is not the raw intent
file digest. `route_intent_sha256` is the raw canonical intent file digest and
is recorded by the outer journal and every checkpoint. Because the unsigned
intent includes the `resolver_result` identity, its transaction ID binds the
sealed result raw bytes without making a self-referential digest.

`edges[*].order` is one-based for human-facing reporting. `next_hop_index`,
`checkpoint_index`, and checkpoint filenames are zero-based: the first edge is
index `0`, has report order `1`, and its checkpoint is
`checkpoints/0000.json`. A next edge is planned only after the preceding
checkpoint is sealed.

After begin, loading or target-side validation proves only the retained
`resolver-result.json` against its intent identity, matrix bytes, origin,
target, route ID, and compact projection. It does not re-resolve from a
remembered or retained external source root. Preparation is the sole phase
that accepts a caller-supplied external `matrix_root`: it re-resolves the
sealed raw `route-matrix.yaml` there and requires the fresh full S1 selection
to exactly equal the sealed full edges and the intent route ID. Missing,
changed, or mismatched source assets fail preparation; they never revise the
sealed result or select another route.

## Outer Journal And Child Binding

`journal.yaml` is the only mutable outer progress record. Before the child
exists, `active_hop` binds the selected edge, materialized package, exact
validator execution, exact child plan semantic identity, and temporary proposal
raw-byte identity. `plan_sha256` is the semantic digest stored in the
proposal's `plan_sha256` field; it is the child transaction ID and the child
plan/checkpoint identity. `proposal_plan_sha256` is instead SHA-256 of the
entire canonical `hops/NNNN/preparation.json` byte stream. These are different
representations with different purposes: no equality relation is required or
valid between them, and neither may substitute for the other.

While the proposal file exists, `evidence.json.plan_sha256`,
`active_hop.plan_sha256`, and the proposal document's `plan_sha256` must bind
the same semantic plan identity. Separately,
`active_hop.proposal_plan_sha256` must bind the exact raw canonical proposal
bytes. Preparation/reuse, apply-before-child-creation, and
awaiting-owner-decision resume re-check both bindings. Once the child exists,
the semantic plan digest cross-binds the derived child transaction ID and the
child plan; the child remains the durable plan authority.

The temporary proposal is durably removed only after the exact child transaction
has been created (including a retained owner-rejected child result). Its raw
digest remains in the active outer journal while that active hop exists, but is
not copied into the child transaction or a finalized checkpoint. A sealed
checkpoint therefore binds only the child semantic plan identity and the child
evidence it actually retains.

Those retained package and validator paths are all rooted at the promoted
`hops/<zero-based-index>/` directory; they never point into staging or failure
retention directories.
After the child exists, it also binds the derived child transaction ID, the
fixed Git-admin-relative child evidence root
`ai-context-package-apply/<child-transaction-id>`, and the pending target
validation receipt digest.

The journal contains only the latest checkpoint index and raw digest; it never
embeds or rewrites a checkpoint body. Its states distinguish planning, waiting
for the owner decision, applying, external target validation, finalization,
checkpointing, checkpointed continuation, rollback, and completion. A missing
or cross-bound package, validator, plan/proposal digest, owner decision, or
receipt is a failure, not a fallback.

## Per-Hop Staging, Promotion, And Failed Retention

The only candidate prepared-hop evidence for index `N` is the promoted,
safe, regular-directory tree `hops/NNNN/`. It contains the exact archive,
checksum, migration artifact, retained `validator.asset`, extracted package
envelope, validator stdout and stderr logs, canonical `validator-execution.json`,
temporary `preparation.json`, and canonical `evidence.json`. The evidence record binds
the hop index, compact edge identity, full materialized package identity,
validator-execution identity, and plan digest. It is written before promotion
and is accepted only when the retained validator record reports `passed` with
the exact declared validator argv, the `validator.asset` digest, expected
output digest, stdout digest, and zero stderr bytes. For a passing record,
the retained `validator.stdout.log` bytes have the expected-output digest;
there is no separately retained expected-output file.

Preparation begins beneath `.preparing-hops/NNNN-<opaque-attempt>/`; a valid
`hops/NNNN/` subtree is atomically promoted from that one staging attempt to
the outer transaction root. A staging directory, a stray staging subtree, or
an incomplete proposal is never active-hop evidence, never a retry input, and
never a directory-scan candidate. A later retry either validates the exact
already-promoted `hops/NNNN/` evidence or creates a new staging attempt; it
does not recover bytes from another staging attempt.

If materialization, validator execution, or proposal construction fails, the
attempt is retained at
`failed-preparations/NNNN-<opaque-attempt>/` with canonical
`failure.json` having exactly `schema_version`
`multi-hop-preparation-failure/v1`, `exception_type`, and `message`. Partial
package, extraction, validator log, record, proposal, or even
success-looking evidence bytes may remain underneath that failed attempt for
diagnosis. They are non-authoritative: they must never satisfy validation,
resume, owner-decision, child-binding, checkpoint, or rollback checks. The
transaction runtime performs no automatic reuse, replacement, or cleanup of
failed-preparation evidence; separate retention cleanup is outside the route
transaction and cannot alter journal, promoted-hop, child, or checkpoint truth.

Every promoted, staging, or failed path consumed by the route runtime must
reject symlinks and platform reparse points. Validator execution uses only the
explicitly selected matrix asset and exact argv; a timeout, OS failure, non-zero
exit, stderr bytes, unexpected stdout, changed validator asset, changed
expected-output asset, or missing/corrupt retained record is failed
preparation, never a fallback or promotable hop.

## Immutable Checkpoints And Finalization

`checkpoints/<index>.json` is canonical JSON and write-once. It is created
only after the active child has passed its exact target validation and the
target provenance/customizations authority has been finalized. It binds:

- the selected edge and predecessor checkpoint raw digest;
- the materialized package identity;
- the child transaction ID, plan digest, fixed child evidence root, package and
  migration digests, remediation-packet/decision identities, incoming and
  target validation identities, and terminal receipt identity;
- byte-identical pending-receipt evidence archived at
  `checkpoints/<index>.pending-receipt.yaml` before the target-side pending
  receipt is cleared;
- finalized provenance/customizations authority digests and the target surface.

Its `digest` is SHA-256 of canonical checkpoint JSON after omitting only the
`digest` field. Checkpoint `0` has a null predecessor; each later checkpoint
binds the preceding checkpoint's raw SHA-256. Replacement, truncation,
deletion, reordering, or any raw/digest mismatch invalidates the transaction.
The outer journal cannot reopen a sealed checkpoint.

The complete evidence chain is result-to-intent-to-hop-to-checkpoint-to-target:
the target validator first proves the retained full resolver result and its
raw identity from `route-intent.json`; each promoted hop proves its compact
edge, materialized archive/checksum/migration/retained validator asset, and
validator record against that full edge; each checkpoint binds the same compact
edge, package, child plan and raw intent digest; and target provenance
validation accepts a checkpoint only after those bindings and the child
transaction evidence hold. A checkpoint intentionally does not copy the full
resolver result or an external matrix root, so it cannot become a divergent
route authority.

## No Fallbacks, Resume, And Rollback

Only a resolver-selected `orchestrated-multi-hop` route starts this S2 outer
transaction. A `direct`, `reconciliation-required`, or `unsupported` result is
not silently remapped to multi-hop execution. No stage may directory-scan for
another matrix, remember a route default, or substitute an archive, checksum,
manifest, validator executable/argv, validation receipt, remediation packet,
or owner decision.

Owner decisions remain separate from automatic proposals. A missing, stale,
rejected, or cross-bound decision cannot become inferred approval, and a later
hop cannot reuse a previous hop's decision.

Resume re-reads the exact raw matrix, path-free sealed resolver result,
unsigned intent transaction ID, raw intent digest, selected ordered edges,
journal, checkpoint chain, target surface, target authority digests, and active
child evidence. Any drift fails closed. Rollback is limited to the active
unfinalized child hop, using its exact child transaction, package, retained
validator asset and record, plan, journal, and decision. It cannot cross a
sealed checkpoint or reopen a finalized hop; a changed finalized route or target
history requires a new governed operation and owner decision.
