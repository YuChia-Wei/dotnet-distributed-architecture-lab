# AI Context Version Policy

## Purpose

This policy defines how this reusable AI context framework is versioned, released, identified in target repositories, and upgraded. It applies to reusable collaboration context under `.ai/`, runtime wrappers, and framework governance that affects how agents interpret or execute that context.

## Version Identity

- Published versions use SemVer tags in the form `vMAJOR.MINOR.PATCH`.
- The stable release identifier is `REL-vMAJOR.MINOR.PATCH`. It remains searchable even if a commit SHA changes before publication.
- Every published release records both the annotated tag and the full 40-character commit SHA. Neither identifier replaces the other.
- Tags are immutable after publication. Never move, recreate, delete, or reuse a published version tag.
- A branch name, workflow ID, date, or mutable Git ref such as `main` is not a version identity.

## SemVer Meaning

| Change | Version impact |
| --- | --- |
| Removes or incompatibly changes a stable collaboration entry, manifest schema, skill input/output contract, or required target integration | major |
| Adds a backward-compatible skill, rule, validation, runtime route, or target migration capability | minor |
| Corrects wording, links, metadata, or implementation defects without intentionally changing a public contract | patch |

While the framework remains below `v1.0.0`, a minor release may contain breaking changes. Such a release must set `compatibility.breaking_changes: true`, list the affected contracts, and provide an explicit migration guide. Patch releases must not intentionally break a published contract.

Version impact is determined by the highest-impact included change. Repository history size and number of changed files do not determine the version.

## Release Lifecycle

1. **Planned**: create or update a version candidate record and migration material on a dedicated workflow branch. The candidate has no tag or published commit.
2. **Validated**: all required repository gates pass and release notes describe compatibility, migrations, and known limitations.
3. **Merged**: merge the workflow with `--no-ff` into `main`. Re-run release validation against the merge commit.
4. **Published**: the user creates an annotated immutable tag on the validated `main` commit. The tag-triggered publication automation validates that tag, builds the package from it, and publishes the release artifacts and notes.

The merge commit should use `release` scope and mention the candidate version. The annotated tag message must include the release identifier, compatibility summary, and `AI-Model` line when AI assisted the release preparation.

Do not describe a candidate as published, and do not create a final tag from an unmerged workflow branch. Publication automation must never create, move, recreate, or choose a version tag; the user owns tag timing and version selection.

## Release Artifacts

Each governed version uses `.dev/releases/<version>/`:

- `release.yaml`: machine-readable identity, lifecycle, compatibility, and evidence locator.
- `release-notes.md`: human-readable changes, compatibility, validation, and known limitations.
- `migration-guide.md`: source-version-aware target migration actions. Use “no action required” explicitly when appropriate.

`.dev/releases/INDEX.MD` is the release catalog. `release.yaml` is the lifecycle source of truth for one version. Historical records created after the tag must declare `record_origin: retrospective` and must not imply that their metadata existed at publication time.

The annotated tag object and its resolved commit are the publication identity. A retrospective record is read from the current trusted framework release registry and is supplemental governance evidence; it is not required to exist inside the older tagged tree. For a governed release, the tagged tree contains the validated candidate notes and migrations, while the trusted registry may finalize the published commit afterward without moving the tag.

## Target Provenance

An initialized target repository records its installed framework source in `.dev/AI-CONTEXT-SOURCE.yaml`, created from the canonical upgrader template. The manifest records:

- source repository, published version, and full commit;
- import and last-upgrade timestamps;
- manifest schema version;
- target-owned overrides with paths, reasons, and disposition;
- the last completed migration and any unresolved reconciliation items.

The source framework repository stores the template, not a self-referential target manifest. `repo-structure-sync` creates initial target provenance; `ai-context-upgrader` updates it only after a successful upgrade.

## Upgrade Safety

An upgrade compares three states:

1. the previous published framework version recorded by the target;
2. the requested published framework version;
3. the target repository's current files and declared overrides.

Classify changes before writing:

- `automatic-candidate`: reusable framework content unchanged locally and safe to replace;
- `reconcile`: target-owned, locally changed, missing provenance, or semantically ambiguous content;
- `exclude`: source-repository runtime history or artifacts that do not belong in a target.

Completed `.dev/workflows/`, assessment instance directories, source-repository backlog and release history, Git metadata, and tool caches are excluded by default. Reusable assessment README, index, policy, and templates remain normal framework candidates. Product `src/` and `tests/` are outside AI context upgrade scope. External knowledge graphs may accelerate discovery but are never evidence of completeness or file truth.

No automatic application may proceed while required inputs are absent, Git refs are unresolved, or reconciliation items remain unacknowledged.

## Validation And Publication Gate

A governed release must verify:

- version, release ID, tag, commit, and lifecycle consistency;
- resolvable published tag and exact commit target;
- parseable release and provenance YAML;
- required release notes and migration guide;
- compatibility declarations for breaking changes;
- repository AI-context and workflow validation;
- required Git commit body and AI co-author trailer policy.

Tag creation, remote publication, and target upgrade execution each require explicit authorization appropriate to that action.

For the configured automated publication path, pushing a user-created release tag is the publication authorization. Candidate or pull-request automation may build and retain validation artifacts, but it must not create a GitHub Release or mutate tags.
