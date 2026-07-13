# Canonical Asset Schema

This document defines canonical asset metadata schema version `1.0`. Canonical
manifests use `asset_id` as their identifier field; the legacy `id` field is not
part of this schema.

The active manifest families are currently `skill-spec` (`skill.yaml`) and
`sub-agent-role-prompt` (`sub-agent.yaml`). `command-spec` and `prompt-package`
are canonical creation templates, but they do not become active manifest
families until their discovery roots and validator coverage are registered.

## Type Notation

- `string`: a non-empty YAML string.
- `string[]`: a YAML sequence of non-empty strings. An empty sequence is valid
  unless the field says otherwise.
- `enum`: a string restricted to the listed values.
- `object`: a YAML mapping.
- `workflow-step[]`: a non-empty sequence of objects containing an integer
  `step` greater than zero and a non-empty string `description`. Step numbers
  must be unique and ascending.

Relative paths are repository-relative and use `/` separators. Unknown fields
are allowed so an asset type can add an owned contract without changing the
common schema.

## Common Fields

Every canonical asset manifest must include these fields:

| Field | Type | Allowed values or rule |
| --- | --- | --- |
| `asset_id` | `string` | Lowercase kebab-case; unique within the repository |
| `schema_version` | `string` | Exactly `"1.0"` |
| `asset_type` | `enum` | `skill-spec`, `sub-agent-role-prompt`, `command-spec`, `prompt-package` |
| `title` | `string` | Human-readable asset name |
| `purpose` | `string` | One concise statement of responsibility |
| `portability` | `enum` | `portable`, `repo-portable`, `wrapper-specific` |
| `audience` | `enum` | `agent-facing`, `human-facing`, `mixed` |
| `source_of_truth` | `enum` | `canonical`, `wrapper`, `generated` |
| `inputs` | `string[]` | Inputs accepted by the asset |
| `outputs` | `string[]` | Outputs produced by the asset |
| `constraints` | `string[]` | Mandatory operating boundaries |
| `references` | `string[]` | Repository-relative paths |
| `examples` | `string[]` | Repository-relative paths |
| `wrapper_targets` | `string[]` | Zero or more of `claude`, `codex`, `copilot` |
| `status` | `enum` | `draft`, `active`, `deprecated`, `historical` |

`source_of_truth: canonical` is required for manifests stored under
`.ai/assets/`. `wrapper` and `generated` are reserved for metadata records that
describe non-canonical projections.

## `skill-spec`

A `skill-spec` requires all common fields plus:

| Field | Type | Rule |
| --- | --- | --- |
| `triggers` | `string[]` | At least one user intent or trigger phrase |
| `workflow` | `workflow-step[]` | Ordered execution contract |
Optional skill fields include `handoff_rules`, `runtime_notes`,
`capability_slots`, `human_guide`, `workflow_artifacts`,
`workflow_templates`, and `report_template`. When present, `handoff_rules` and
`runtime_notes` are `string[]`. Paths and wrapper metadata must not make a
wrapper the canonical owner of the skill.

Every `skill-spec` also requires `wrapper_metadata`, an object whose keys
exactly match the unique values in `wrapper_targets`. Each target value is an
object with a required `wrapper_path` string. A wrapper path must:

- be repository-relative and use `/` separators;
- contain no placeholder or glob syntax;
- remain inside the repository when resolved;
- identify an existing file or directory.

`runtime_wrapper_path` is a legacy, invalid key. Runtime-specific details may
be added beside `wrapper_path`, but they do not replace it or weaken target
parity.

## `sub-agent-role-prompt`

A `sub-agent-role-prompt` requires all common fields plus:

| Field | Type | Allowed values or rule |
| --- | --- | --- |
| `role_kind` | `string` | Non-empty role taxonomy identifier |
| `triggers` | `string[]` | At least one delegation intent |
| `workflow` | `workflow-step[]` | Ordered delegated-worker contract |

`handoff_rules` is an optional `string[]` of conditions returned to the
orchestrating agent. Version `1.0` leaves `role_kind` open because the active
taxonomy contains domain-, use-case-, infrastructure-, testing-, review-, and
coordination-oriented role families. A future schema may introduce a closed
enum only after that taxonomy has its own migration decision.

The role prompt is bounded delegated behavior, not an independently routed
user-facing skill. The orchestrating agent remains responsible for integration,
validation, and final reporting.

## `command-spec`

A `command-spec` uses the common fields and additionally requires:

- `invocation_style`: enum `slash-command`, `workflow-command`, or
  `sub-agent-command`;
- `prompt_packages`: `string[]` of prompt-package asset IDs;
- `command_outputs`: `string[]` describing command-specific artifacts.

Commands are portable command contracts. Runtime spelling and wrapper-specific
argument syntax belong in `wrapper_metadata`, not in canonical command text.

## `prompt-package`

A `prompt-package` uses the common fields and additionally requires:

- `base_prompt`: repository-relative path string;
- `shared_fragments`: `string[]` of repository-relative paths;
- `validation_rules`: `string[]` of required checks;
- `consumers`: `string[]` of canonical asset IDs.

A prompt package groups reusable prompt material. It does not duplicate skill
workflow policy or wrapper invocation syntax.

## Migration and Compatibility

Schema version `1.0` intentionally standardizes `asset_id`, scalar
`source_of_truth`, enumerated `audience`, and the canonical asset-type names.
Assets that use `id`, `asset_type: skill`, `portability: universal`, free-form
audience values that are not one of the declared scalar enums, or a list-valued `source_of_truth` must be migrated before they
claim conformance to `1.0`.
