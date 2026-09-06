# Upgrade Route Support Policy

## Purpose

`upgrade-route-matrix.yaml` is the finite, evidence-bound source of truth for
read-only upgrade-route selection to one framework target release. It does not
plan target changes, establish target provenance, or authorize package apply.

The resolver accepts only an explicit matrix file, origin version, and target
version. It reads the matrix's raw bytes and only the exact relative asset paths
declared by that matrix. It never scans an archive directory, discovers another
release, remembers a default route, invokes package apply, or writes target
bytes.

## Required Matrix Evidence

Source releases from v0.16.0 require direct support for v0.6.0, v0.9.0 and
the immediate previous governed package. Each must have one exact source-specific
edge to the incoming archive, with actual target apply, semantic reconciliation,
validation, finalization and recovery evidence. An intermediate release chain or
an archive-only validator cannot establish this support. The general resolver
retains historical multi-hop capability; source release admission enforces the
prospective direct-only requirement. Retained origins are removed only through an
explicit owner-approved versioned deprecation.

The canonical contract is
`.ai/assets/skills/ai-context-upgrader/templates/upgrade-route-matrix.schema.yaml`; start from
`templates/upgrade-route-matrix.template.yaml`.

- The target binds its version, release ID, full commit, manifest identity, and
  canonical package identity: `package_id`, `release_id`, and
  `payload_fingerprint`.
- The governed origin roles are exactly `immediate-predecessor`, `v0.9.0`, and
  `v0.6.0`. Each role must appear exactly once, either as a retained origin
  binding version, release ID, full commit, and manifest identity, or as a
  complete explicit deprecation.
- A route declares its exact, one-based ordered edge sequence from origin to
  target. A route kind is deliberately not stored; one edge can become
  `direct`, while two or more can become `orchestrated-multi-hop` only after
  verification.
- Every edge binds the package identity materialized by its `to_version`, four
  asset identities (`archive`, `checksum`, `manifest`, and `validator`), a
  non-empty `validator_argv`, canonical validation receipt, and separate raw
  validation-output identity. The final edge package identity equals the matrix
  target identity; intermediate edges bind their own package rather than the
  final target package. The validator identity is the
  exact executable asset and `validator_argv` must name its exact
  matrix-relative path exactly once, while preserving any interpreter and
  option tokens. An identity has `asset_id`, a safe matrix-relative POSIX
  `path`, and a raw SHA-256. The resolver checks every byte identity without
  executing it.
- A checksum sidecar is evidence, not just a hashed file. Its verified UTF-8
  bytes must be exactly one standard `sha256sum` record whose digest and
  filename match the verified archive bytes and archive basename. Updating the
  sidecar identity after putting a wrong archive digest in it remains unsafe.
- An edge validation receipt uses `upgrade-edge-validation/v2` canonical UTF-8
  JSON. It must bind the exact
  edge ID, `from_version`, `to_version`, all four edge identities, validator
  argv, and the ordered edge semantic-cutover claims after the matrix-level
  `required` value has been bound into each `{cutover_id, required, state}`
  record, plus `passed` outcome, integer exit code `0`, and the output SHA-256.
  That output digest must equal both the declared output identity and separately
  retained raw output bytes. The matrix validation state cannot disagree with
  the receipt. Relabelling a matrix edge or adding a cutover claim without a
  corresponding immutable receipt is reconciliation-required. The receipt also
  records `incoming-package-validation/v1`: the exact archive-declared
  incoming-candidate manifest path and SHA-256, validator path/SHA-256/argv,
  passed exit code and output digest, and the archive's package ID, release ID,
  and payload fingerprint. The receipt package identity must equal the current
  edge package identity, whose release ID names that edge's `to_version`.
  Reusing the same package/release identity for a
  different payload fingerprint is a fail-closed identity conflict.
- Semantic cutovers are declared once at matrix level. A required cutover must
  have a `passed` record in at least one ordered edge of a selected route.
- A deprecation is valid only with `complete: true`, `unsupported` disposition,
  a reason, and exact notice, owner-decision, validator-receipt, and output
  identities. Notice and owner decision are strict typed UTF-8 JSON or YAML and
  cross-bind deprecation ID, role, origin, and target. The owner decision must
  have `status: approved`, `approved: true`, a non-empty owner, and an ISO-8601
  decision timestamp with a numeric UTC offset. The validator receipt is
  canonical JSON that cross-binds notice and decision identities, a passed
  outcome, exit code `0`, and retained output bytes. Missing, malformed, or
  tampered deprecation evidence invalidates the matrix; it does not create a
  weaker unsupported fallback.

## Deterministic Selection

After structural validation and deprecation-evidence verification, the resolver
uses only these four result kinds:

1. `direct` — exactly one safe direct candidate exists. It is preferred over
   multi-hop candidates only when it covers every required semantic cutover.
2. `orchestrated-multi-hop` — no safe direct route exists and exactly one safe
   complete chain of two or more edges exists.
3. `reconciliation-required` — the requested origin is retained but has no
   complete safe route, has missing/tampered assets, failed validation,
   `deferred-with-owner` validation, a missing required cutover, or more than
   one complete safe candidate. Deferred evidence is never promoted to passed.
4. `unsupported` — the requested target is outside the matrix, the origin is
   outside the retained inventory, or the origin has fully explicit and valid
   deprecation evidence.

The result includes deterministic diagnostics. A direct candidate that skips a
required cutover is diagnosed and cannot suppress a unique safe multi-hop
route. Ambiguity is never broken by route order, version proximity, or a
remembered preference.

## Evidence Output

`plan-ai-context-upgrade.py` emits one compact sorted JSON object with a
terminal newline. Every successful object includes the explicit origin and
target, the selected route and ordered edge IDs when applicable, diagnostics,
and the complete ordered selected edges with their exact asset, validator,
checksum, cutover, and validation identities, plus the matrix raw byte length
and SHA-256. No timestamp or environment state is added, so identical inputs
produce identical evidence bytes.

Invalid matrix syntax, unsafe paths, invalid identity shape, or incomplete or
tampered deprecation evidence is a fail-closed command error rather than a new
route kind. Missing, malformed, tampered, legacy-v1,
portable-validation-incomplete, or cross-mismatched in-scope edge
evidence instead produces `reconciliation-required`; no resolver path executes
an asset, changes a target, or creates a fifth result kind.

## Historical Package Validator Boundary

A source-repository archive validator, release-phase command, or successful
hosted publication is not automatically an upgrade-edge validator. An edge may
name a validator only when the matrix binds the exact executable bytes and its
edge proof executes the archive-declared incoming-candidate validator, records
its exact authority and result, and binds its package identity to the package
materialized by that edge. The resolver verifies that immutable receipt
without re-executing package code. A legacy `1.0` matrix remains parseable only
to produce `reconciliation-required`; it cannot obtain a passing route without
the new proof.

Published v0.7.0 through v0.13.0 packages predate the portable
incoming-candidate validator contract: they contain the package-apply planner
but do not contain or declare a per-package validator path and argv. Those
historical edges therefore remain `reconciliation-required` until a later
candidate explicitly supplies, binds, and proves a compatible validator. The
source-only archive and release-state validators must not be substituted or
represented as portable execution evidence.

## Package-Integration Boundary

This resolver is a pre-apply planner only. A later package-integration stage
must consume the selected evidence, independently validate the selected
archive/manifest/validator identities, bind it to target provenance and owner
reconciliation, and retain its own apply and target-validation receipts. It
must not treat route selection as package-apply authorization.
