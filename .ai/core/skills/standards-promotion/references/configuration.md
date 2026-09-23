# Standards Promotion configuration

The caller supplies absolute `project_root` and `package_root`, and optional
explicit `project_config` / `local_config` paths. Relative config, store and
read-evidence paths resolve against the project root, never the config directory.
No upward search, cwd inference, environment substitution or fallback directory.
Explicitly named missing config is an error; no selected config means defaults
without decision or promotion authority. The tool never edits configuration.

## Namespace and precedence

Project JSON has exact integer `config_version: 2`, optional `skills` and optional
`constraints`. Local JSON permits only `config_version` and `skills`; constraints
are forbidden even for another namespace. Each namespace matches
`[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)*` and contains an object. Parse the full JSON
syntax/envelope, then validate only this package's settings/constraints. Foreign
objects remain inert; their values grant no permission and are never returned by
`explain`. Unknown own fields, duplicate JSON keys, invalid Unicode, nonfinite
values, bool/float versions and explicit null settings fail. Selected project and
local files must use the same version. No automatic conversion is provided.

Values resolve invocation > local > project > package defaults. `overrides`
contains only this package's settings object. Merge store leaves; replace the
whole template object. Absent values inherit; arrays are never concatenated.

| Setting | Default / accepted value |
| --- | --- |
| `store.kind` | `filesystem` only |
| `store.root` | `notes/promotions`; nonempty project-relative or explicit absolute path |
| `store.tracking` | `tracked`; alternatively `ignored`; intent only, no Git edits |
| `template` | `{origin: package, path: templates/promotion.md}`; atomic object; origin may be `project` |

Project-only `constraints.standards-promotion` supports `write_roots` (nonempty unique path
array) and `locked_fields` (unique values from `store.root`, `store.tracking`,
`template`). Omitted write roots allow the project/default store selected BEFORE
local/invocation overrides. Locks compare against project/default values; changing
a locked value fails. Caller `write_roots` can narrow that scope; permissions are
never unioned across namespaces or expanded by overrides. Actual task authority
is required in addition to a path binding. Evidence adapters below are project
constraints, never local/invocation settings.

## Paths, resources and storage

Roots must exist. Package resources are explicitly declared in metadata and
contained in package root. The running executable must belong to that package.
Project templates stay within project root; package templates must select the
declared resource. Reject volume-root stores, parent traversal, all symlinks,
junctions/reparse points, drive-relative/device/UNC paths and ambiguous Windows
segments. A store cannot overlap package, selected config or template content.
An external absolute store requires explicit project write roots and actual task
authority. There is no disk discovery, relocation or migration fallback.

A new identity may provision missing store directories only if EVERY created
parent is within project and caller write roots. With default `notes/promotions`, prepare
`notes` separately or explicitly allow that parent. Created directories remain on
failure and are reported; no recursive rollback. A changed store selects another
collection without moving any records. Persist the store binding with a durable
logical reference. Selected package/config/schema/template inputs are frozen and
rechecked before publication. Identity drift, appearance of an input previously
observed absent or changed input bytes produce conflict.

A selected local config within a Git project must already be ignored and untracked.
The tool uses read-only Git with bounded calls and removes ambient Git variables;
it does not change ignore rules. Missing required Git yields `unavailable`, and
unproven ignored state yields `blocked`. No local config means no Git subprocess.
The filesystem requirement includes this conditional capability.

`explain` returns effective settings, winning leaf sources, locks, allowed roots,
selected config version, ignored namespace NAMES and authority binding identifiers.
It creates no store. `runtime_capability: not-probed` and `tracking: intent-only`
are deliberate limits; successful explanation does not prove write availability.
Do not put secrets in configs, retained evidence or templates.

## Project proposal and observation bindings

`constraints.standards-promotion.source_read_roots` is a unique path array (at
least one root needed to propose). `targets` is an array of
`{id, path, applicability, allowed_actors, adoption_source, effect_source}`.
IDs are nonblank/unique; canonical target aliases are rejected. Target paths are
project-contained files, outside this store/package/config/template. Propose reads
an existing UTF-8 target; reconcile can record a missing target. Applicability is
one nonblank string matched exactly. Actors are a nonempty unique string array.

Each source adapter is null (unavailable) or `{root, pointers}`. Evidence read
roots cannot overlap protected content or the target. Roots are not write authority.
Adoption pointers map subject_sha256, target_id, after_sha256, actor, decision,
decided_at. Effect pointers map subject_sha256, target_id, after_sha256,
adoption_sha256, applicability, state, effective_at. Pointers are distinct,
non-root literal JSON Pointers; no invalid escapes, expressions or fetching.
Source files are explicitly selected per reconcile with
`{binding_id, path, expected_sha256}`; binding_id equals target ID.

Missing selected sources or null adapters yield unresolved observations. Unsafe,
unreadable, oversized, non-UTF-8 or changed-digest input fails that invocation;
malformed JSON/mapped evidence retains its exact snapshot with unresolved diagnostics.
See [authority](authority.md). No automatic decision/effect-file creation is allowed.
