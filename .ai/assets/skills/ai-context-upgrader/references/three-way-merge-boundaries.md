# Three-Way Upgrade Boundaries

## Inputs

- **Base**: the framework commit recorded by the target manifest.
- **Incoming**: the requested published framework commit.
- **Target**: the target repository worktree at upgrade time.

The classifier compares paths and content; it does not infer semantic ownership from names alone.

## Classification

### Automatic Candidate

A changed reusable framework path may be proposed for automatic replacement only when the target copy is byte-identical to the base, the path is not target-owned, and the incoming release does not require manual migration for that path.

### Reconcile

Reconciliation is mandatory when any of these apply:

- target content differs from base;
- the manifest declares a local override or unresolved item;
- the path owns target identity, requirements, specs, ADRs, architecture, operations, project configuration, or root collaboration instructions;
- the base path is absent or source provenance is unresolved;
- both target and incoming changed relative to base;
- a migration guide flags a decision or compatibility break.

Deletion is a reconciliation item unless the target is unchanged from base and the release guide explicitly permits automatic removal.

### Exclude

Exclude source-repository state that is not distributable framework context:

- `.git/` and local tool caches;
- dated workflow instance directories and assessment instance directories such as `.dev/assessments/ASM-*/`; reusable README, policy, and templates are not excluded;
- source-repository backlog items and historical `.dev/releases/`; target catalog indexes require reconciliation rather than replacement;
- source provenance instances, temporary reports, build output, and local environment files;
- product `src/` and `tests/`.

The requested release's migration guide may add exclusions but cannot remove these safety exclusions without a newer policy decision.

## Ownership Precedence

Target-specific truth wins over reusable defaults until a user explicitly reconciles it. Canonical framework policy wins for the semantics of the incoming framework, but its presence does not authorize overwriting target facts.

External indexes can suggest paths to inspect. They cannot prove that a path is unchanged, absent, complete, or safe to replace.
