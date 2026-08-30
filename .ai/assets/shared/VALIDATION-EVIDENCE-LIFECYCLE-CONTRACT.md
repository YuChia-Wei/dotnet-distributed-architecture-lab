# Validation Evidence Lifecycle Contract

This portable contract separates exact-head identity freshness from behavioral
evidence applicability. It preserves fail-closed review and provider admission
while allowing content-addressed reuse only when the complete governed input
closure is proven byte-equivalent.

## Evidence Taxonomy

| Class | Meaning | Reuse rule |
| --- | --- | --- |
| `identity-sensitive` | Exact-head audit, review, and admission identity. | Re-execute after every tracked head change. |
| `input-sensitive` | Unit, integration, workflow, packaging, and source-governance behavior determined by tracked inputs. | Reuse only with an authenticated dependency/content receipt. |
| `environment-sensitive` | Benchmark, durability, platform-filesystem, or reference-host behavior. | Input proof plus exact compatible environment dimensions is required. |
| `provider-sensitive` | Hosted checks, review, PR/base/head/body, and Issue/Project state. | Live provider read-back is required; local receipts never replace it. |

`metadata-only` is not an evidence class. A change is harmless only after the
tracked dependency resolver proves that the changed bytes are outside the
selected closure and that runner, manifest, resolver, policy authority,
configuration, command, profile, and applicable environment authority are
unchanged.

## Deterministic Reuse

The machine contract is `validation-evidence-lifecycle.schema.yaml`; the
repository validator is `.ai/scripts/validate-validation-lifecycle.py`.
Every reusable receipt binds original and current commit SHAs, exact argv and
working-directory contract, profile, original outcome and immutable evidence,
the canonical dependency set with original/current Git blob identities, and
all authority digests. The resolver must also seal a complete sorted path-set
digest, exact count, resolver argv, and an empty unknown-path set; a non-empty
subset cannot declare itself complete. The receipt's own digest covers
canonical JSON bytes.
The resolver argv names the supported
`check-all.sh --resolve-input-closure <check-id> --subject <sha>` surface. The
validator executes that resolver for both subjects, requires the exact sorted
path set, and reads every claimed object identity back from Git as
`<sha>:<path>`. A nonexistent path, arbitrary subset, unsupported resolver
flag, or self-computed path-set digest fails closed.

Unknown dependencies, missing blobs, duplicate paths, unrecognized fields, or
runner, manifest, resolver, policy, configuration, command, profile, or
environment drift fail closed. A cache hit, filename, extension, path filter,
or small diff is not proof. Release and `nightly-full` profiles, fresh
exact-head audit, hosted required contexts, review, and live admission cannot
be replaced by a behavioral receipt.

Environment equality applies to every reusable class because environment is
part of reuse authority, not only to tests labelled environment-sensitive.
Terminal workflow metadata has its own original/current digest and an explicit
`excluded_from_dependency_fingerprint` marker: its bytes may change without
self-invalidating behavioral evidence only when the complete resolver closure
proves that metadata path is outside the governed inputs. This models the #246
regression without changing any #246 historical receipt.

## Validation Freeze

Complete anticipated tracked implementation, workflow closeout, terminal
declarations, indexes, and governance metadata before the final aggregate.
An active freeze binds one clean immutable subject and permits only declared
ignored validation artifacts or provider overlays. A required tracked repair
invalidates the freeze and every identity-sensitive receipt for that subject;
the workflow reclassifies impact before validation resumes.

Provider admission and post-merge reconciliation remain live, non-mutating
overlays. They do not require a source repair commit. Historical evidence,
including #246 receipts, retains its original subject and environment and is
never relabeled as current-head execution.

## Audit And Hosted Contexts

A fresh exact-head independent auditor reports each gate as exactly one of
`re-executed`, `reused-with-proof`, `blocked`, `deferred`, or
`not-applicable`. Reuse names its receipt; it is never described as execution.
Every provider-required context appears on each admitted head and reaches a
truthful terminal outcome. A context may internally execute or reuse eligible
behavioral evidence, but path filtering cannot make the context disappear.
