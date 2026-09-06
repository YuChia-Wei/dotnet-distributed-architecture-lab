# Validation Evidence Lifecycle Contract

This portable contract separates commit provenance and immutable execution
pinning from evidence validity. It preserves fail-closed review and provider
admission while allowing content-addressed reuse only when the complete
governed subject is proven equivalent.

## Evidence Taxonomy

| Class | Meaning | Reuse rule |
| --- | --- | --- |
| `identity-sensitive` | Commit-range selection, immutable execution locator, or integration identity whose behavior depends on the selected Git relationship. | Re-resolve the identity-dependent operation; a SHA change alone does not invalidate separately content-addressed evidence. |
| `input-sensitive` | Unit, integration, workflow, packaging, and source-governance behavior determined by tracked inputs. | Reuse only with an authenticated dependency/content receipt. |
| `environment-sensitive` | Benchmark, durability, platform-filesystem, or reference-host behavior. | Input proof plus exact compatible environment dimensions is required. |
| `provider-sensitive` | Hosted checks, review, PR/base/head/body, and Issue/Project state. | Live provider read-back is required; local receipts never replace it. |

`metadata-only` is not an evidence class. A change is harmless only after the
tracked dependency resolver proves that the changed bytes are outside the
selected closure and that runner, manifest, resolver, policy authority,
configuration, command, profile, and applicable environment authority are
unchanged.

## Commit Identity Boundary

A full commit SHA may be required as an immutable execution locator, Git-range
selector, provider association, or provenance fact. Those uses identify where
an operation ran or which Git/provider event is current; they do not make the
SHA the validity key for separately content-addressed evidence.

No portable rule may invalidate behavioral, independent-review, or derived
content evidence solely because two commit SHAs differ. It must instead prove
the applicable content subject equal, re-resolve an inherently identity-bound
operation, or report the subject as unknown. A history-only rewrite with equal
content uses deterministic rebinding and preserves both commit identities as
provenance.

The authoritative multi-axis decision table is
`.ai/assets/shared/validation-gate-classification.yaml`. Every local
registry gate occurs exactly once. Sensitivities are independent axes;
`reuse_eligibility` is a separate owner-controlled decision. A missing,
duplicated, or unknown gate blocks classification. The only current
`pilot-approved` gate is `multi-hop-upgrade-transaction`; every other candidate
remains disabled even when its legacy cache policy permits narrower reuse.

## Canonical Subject Manifest And Rebind

`subject-manifest/v1` binds one gate to a `subject-identity/v1` projection made
from authenticated classification, tracked-closure, invocation, authority,
runtime, and applicable-environment digests. Its `subject_digest` is the
SHA-256 of canonical UTF-8 JSON for that projection. Commit, tree, timestamp,
artifact references, runtime repository-scope identity, and provider
identifiers remain provenance and are not part of the subject digest.

The tracked-closure receipt names the authoritative
`check-all.sh --resolve-input-closure` invocation and seals the complete sorted
Git path, mode, type, and object identities. The invocation component comes
from the current validation registry. Authority includes the runner, registry,
resolver, lifecycle policy/schema, implementation, and gate-classification
bytes. Runtime identity includes the actual Python implementation, version,
ABI, and PyYAML identity. The pilot environment contract adds OS family, Git
version, and a repository-filesystem case-semantic probe without recording an
absolute path, host name, user name, or machine identity.

`subject-evidence-rebind/v1` is append-only. It accepts an original manifest
only when an immutable passing invocation seal contains that exact manifest,
its component receipts, and an executed passing evidence record for the same
gate and original commit. It then builds and validates the current manifest
freshly, requires the same approved classification and equal subject digest,
and records both commit SHAs. The truthful outcome is `reused-with-proof`: the
old evidence applies to the current subject but was not executed at the current
SHA. A known component difference requires `re-executed`; unknown
closure, authentication, runtime, environment, authority, or classification
fails closed as `blocked`.

Rebind never replaces actual-upgrade evidence, current-head review-subject
binding, required hosted contexts, live merge admission, mutable provider
state, or tag and Release binding. The current-head review binding is a cheap
digest comparison; it does not repeat an independent review when the reviewed
content subject is unchanged.

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
or small diff is not proof. Release and `nightly-full` profiles, current-head
review binding, hosted required contexts, and live admission cannot be replaced
by a behavioral receipt.

Environment equality applies to every reusable class because environment is
part of reuse authority, not only to tests labelled environment-sensitive.
Terminal workflow metadata has its own original/current digest and an explicit
`excluded_from_dependency_fingerprint` marker: its bytes may change without
self-invalidating behavioral evidence only when the complete resolver closure
proves that metadata path is outside the governed inputs. This models the #246
regression without changing any #246 historical receipt.

## Validation Freeze

Complete anticipated tracked implementation and governing authority before the
final aggregate. An active freeze pins execution to one clean immutable commit
and permits only declared ignored validation artifacts or provider overlays.
Tracked content or governing-authority drift invalidates the frozen subject;
commit-message or history-only identity drift instead requires deterministic
current-subject rebinding. Terminal binding receipts remain ignored or
provider-owned and never require an evidence-sync commit.

Provider admission and post-merge reconciliation remain live, non-mutating
overlays. They do not require a source repair commit. Historical evidence,
including #246 receipts, retains its original subject and environment and is
never relabeled as current-head execution.

## Independent Review And Hosted Contexts

An independent auditor still executes against one clean immutable commit so
its observation cannot move during the review. Its durable result is
`content-addressed-validation-audit` v2: base/head commit SHAs are provenance,
while repository identity plus base/head tree identities form the canonical
`independent-review-subject/v1` digest. Every reviewed gate is exactly one of
`re-executed`, `reused-with-proof`, `blocked`, `deferred`, or
`not-applicable`.

Admission recomputes the current review subject. Equal content yields
`reviewed-current-content` or `reused-with-proof`; unequal or unknown content
requires a new independent review. Historical exact-head v1 receipts retain
their original meaning only when validating already-retained historical records
under their original exact-head rule. They are not eligible for current or new
live admission; live admission accepts v2 only.

Every provider-required context still appears on each admitted head and reaches
a truthful terminal outcome because the provider attaches check runs to a
commit. A context may internally execute or reuse eligible behavioral evidence,
but path filtering cannot make the context disappear.
