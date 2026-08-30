# Product Source and Projection Contract

Contract ID: `PRODUCT-SOURCE-001`

## Purpose

This contract identifies one canonical source for a portable framework product
and separates it from every derived package, staging tree, runtime wrapper, or
consumer tool. It is technology-neutral and does not select a CLI runtime,
package registry, or implementation language.

## Current Product-Source Model

The current model is **source-tree-in-place**:

1. The canonical product bytes are the regular Git-tree blobs selected by one
   distribution profile at one immutable commit or tag.
2. The profile is the canonical mapping authority for its declared component,
   source path, target path, ownership class, and exclusion. A package builder
   may read those source blobs; it does not become their owner.
3. `files.yaml`, package-envelope metadata, archives, extracted payloads,
   temporary staging directories, generated inventories, and future embedded
   CLI payloads are projections. They are never a second canonical source.
4. A distributed target receives only the declared target paths. Its
   target-owned facts, effective AI-context state, local environment snapshot,
   and execution evidence remain outside framework product authority.

The existing source tree remains in place for this contract slice. A future
`framework/` target-root mirror may be introduced only by an approved,
inventory-backed migration that names the new canonical root, compatibility
aliases, rollback, and source-versus-target path parity. Until then, creating a
hand-maintained mirror, duplicate full-text copy, or alternate canonical root
is prohibited.

## Projection Invariants

- A distributed target path resolves to exactly one declared canonical source
  blob for a selected immutable product revision. Ambiguity fails closed.
- A projection must preserve the declared source blob bytes and executable
  mode. Checkout settings, generated staging bytes, and local platform defaults
  must not redefine the product bytes.
- The product profile starts with an allowlist; exclusions are a deny boundary.
  A source-only path is not included merely because it sits beside a portable
  path.
- A package manifest and checksum prove a projection of the declared product
  revision. They do not authorize a target mutation or replace target
  provenance and customization reconciliation.
- Runtime wrappers are thin projections of their canonical assets. A wrapper,
  adapter, or consumer-specific copy cannot become a second normative owner.
- A future CLI is a control plane for an immutable, digest-verified product
  artifact. The CLI version, cache, or embedded payload cannot silently replace
  the product version or canonical product bytes.

## Source-Only Boundary

Source repository work management, release preparation and closeout, provider
reconciliation, local runtime configuration, execution history, and package
building controls are not target payload. The distribution profile declares
their exclusions; this contract does not infer portability from a path's
format, language, or apparent reusability.

The source-only `bounded-general-worker` Codex execution profile is expressly
excluded from downstream product projection. It remains a source-repository
fallback profile, not a canonical skill or canonical sub-agent role.

The generic provider-neutral capability contracts are canonical assets. Their
separate provider projection registry declares five configured Codex profile
paths for the package projection: the evolved `bounded-routine-worker` mapping
for mechanical evidence plus reconciliation, semantic governance analysis,
evidence report synthesis, and fixed-head independent audit. Those static
profiles remain runtime projections, not canonical role owners, and do not
prove current-session availability, resolved model selection, delegation, or
genuine invocation.

The generic capability package projection does not claim Claude or Copilot
runtime support. Deferred generic provider projections do not mean permanently
unsupported. The existing `context-translator` multi-provider adapter family is
separately configured and does not establish generic capability support for any
other role.

## Migration and Compatibility Boundary

- Do not move or duplicate the current source tree as part of a contract-only
  change.
- Do not rewrite an existing release, package inventory, or target provenance.
- A physical product-root migration must first inventory source paths,
  references, runtime discovery, source-only reasons, target mappings, and
  compatibility strategy. It must then prove package, reference, clean-install,
  upgrade, source-runtime, and rollback parity before the old source root loses
  authority.
- A migration is incomplete while the old and new full-text trees are both
  treated as canonical.
