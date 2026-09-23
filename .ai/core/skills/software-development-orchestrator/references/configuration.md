# Workflow configuration v2

Explicit absolute project_root/package_root must exist. Optional project_config and
local_config paths are absolute or project-relative. Omitted files mean defaults;
explicitly missing files fail. No cwd/upward search, environment interpolation,
credential access, source-policy loading or configuration write.

Project JSON is {config_version:2, skills?, constraints?}; local JSON is
{config_version:2, skills?} only. Exact integer 2 is required, not boolean/float.
Each namespace is a valid dotted lowercase package ID mapped to an object.
Strict JSON rejects duplicate keys, invalid Unicode and nonfinite numbers.
Only software-development-orchestrator settings/constraints are deeply validated.
Other namespaces are inert objects; explain lists names, never values or capability
claims. Config v1/unknown is unsupported and preserved; no conversion exists.

## Defaults and precedence

Metadata v2 has exactly store/template defaults. The owned script's
OPERATIONAL_DEFAULTS is the sole execution authority for retention/resume defaults;
this table describes it. Explain reports each effective value and its actual source
(package-metadata, owned-executable, project, local or invocation).

| Setting | Default and accepted values |
| --- | --- |
| store.kind | filesystem only |
| store.root | notes/workflows, relative to project_root |
| store.tracking | tracked; tracked or ignored, intent only |
| template | {origin:package,path:templates/workflow.md}; origin package or project |
| retention.compact_after_days | 30; null disables, otherwise integer 1..36500 |
| retention.archive_after_days | 90; same type/range |
| retention.purge_after_days | null; same type/range |
| resume_budget_chars | 12000; exact integer 2000..64000; also bounds each retention summary |

Precedence: invocation overrides > local > project > defaults. Store and retention
leaves merge; template replaces atomically; budget replaces as one value.
Unknown selected fields, partial templates or null except age thresholds fail.
No setting schedules or authorizes cleanup.

Project constraints in this namespace permit write_roots (nonempty string array)
and locked_fields from store.root, store.tracking, template, retention,
resume_budget_chars. A lock preserves the project-effective exact value.
Caller write_roots only narrows project bounds. Default bounds are the
project/default store before overrides. No permission union across namespaces.
Absolute external stores require explicit project write_roots plus actual caller
authority. Configuration never supplies that authority by itself.

A selected local config inside a Git project must already be ignored and untracked.
Git is a conditional read-only dependency for that observation. No tool changes
ignore rules, stages files, commits, configures Git or verifies record durability.
Tracking, sharing, backup and export remain project decisions.

## Frozen paths and storage

Freeze selected package resources, config bytes, template and paths per invocation,
then re-read before record publication. Reject links/reparse points even when
contained, traversal, drive-relative/device/UNC paths, ambiguous Windows names,
volume-root stores and overlap with package/config/template. Project templates
stay in project_root; package templates must be the declared owned resource.
Records are direct files of the chosen store, with no mandatory external index.

Only permitted contained store parents may be created. With default roots,
provision notes separately; the tool cannot create an ungranted parent. Created
empty directories remain and are reported after a failed write. Changing the root
does not move records. Keep the selected binding when sharing a store-scoped ID.

Writes support only observed Windows local fixed/RAM NTFS and Linux local
ext2/ext3/ext4/xfs/btrfs/tmpfs/ramfs. The platform check reads information about the
selected store's existing ancestor; it neither discovers a replacement disk nor
creates test files. Other platforms/backends are unsupported. Reads obey path
bounds without claiming network write semantics. Platform behavior is not certified.

One cooperating store writer owns .workflow-write.lock and its temporary file.
An existing lock is conflict; no automatic stale-lock recovery. Expected digest
checks are not filesystem CAS against uncoordinated editors. One record is published
by exclusive hard link for creation or same-directory atomic replacement for update;
no cross-file/provider transaction or power-loss durability is promised. Only verified
invocation-owned transient files are cleaned; cleanup failures remain visible.
