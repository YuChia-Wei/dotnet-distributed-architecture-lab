# Canonical Asset Schema

本文件定義 portable AI assets 的最小 canonical schema。

## Common Fields

所有 asset spec 至少應包含：

- `id`
- `asset_type`
- `title`
- `purpose`
- `portability`
- `audience`
- `wrapper_targets`
- `source_of_truth`
- `inputs`
- `outputs`
- `constraints`
- `references`
- `examples`
- `status`

## `skill` Spec

額外建議欄位：

- `triggers`
- `handoff_rules`
- `runtime_notes`

## `command` Spec

額外建議欄位：

- `invocation_style`
- `prompt_packages`
- `command_outputs`

## `prompt-package` Spec

額外建議欄位：

- `base_prompt`
- `shared_fragments`
- `validation_rules`

## `shared-rule` Spec

額外建議欄位：

- `consumers`
- `rule_scope`

## Portability Values

- `portable`
- `repo-portable`
- `wrapper-specific`

## Audience Values

- `agent-facing`
- `human-facing`
- `mixed`

## Source Of Truth Values

- `canonical`
- `wrapper`
- `generated`

## Wrapper Targets

目前預設支援：

- `claude`
- `codex`
- `gemini`
- `copilot`
