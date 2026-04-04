# Stage 2 Canonical Schema

本階段定義 portable AI assets 的 canonical source schema 與目錄結構。

## Directory Decision

canonical source 根目錄定義為：

- `.ai/assets/`

原因：

- 比 `.ai/skills/` 更中立
- 可同時容納 skills、commands、shared packages
- 不與既有 `.ai/assets/` 的歷史用途混淆

## Canonical Asset Types

### `skill-spec`

用途：

- 描述一個中立的 skill 定義
- 不依賴單一 agent runtime

最小欄位：

- `asset_id`
- `asset_type`
- `title`
- `purpose`
- `triggers`
- `inputs`
- `outputs`
- `constraints`
- `workflow`
- `references`
- `examples`
- `human_guide`
- `wrapper_targets`
- `wrapper_metadata`

### `command-spec`

用途：

- 描述一個中立的 command / slash command / workflow command

最小欄位：

- `asset_id`
- `asset_type`
- `title`
- `purpose`
- `kind`
- `triggers`
- `inputs`
- `outputs`
- `constraints`
- `prompt_packages`
- `references`
- `examples`
- `wrapper_targets`
- `wrapper_metadata`

### `prompt-package`

用途：

- 將 prompts、shared rules、examples 打包成可被 skill 或 command 消費的中立單位

最小欄位：

- `asset_id`
- `asset_type`
- `title`
- `purpose`
- `files`
- `shared_rules`
- `examples`
- `consumers`
- `portability_notes`

## Directory Structure

```text
.ai/assets/
  skills/
    <skill-id>/
      skill.yaml
      prompts/
      references/
      examples/
  commands/
    <command-id>/
      command.yaml
      prompts/
      examples/
  shared/
    rules/
    contracts/
    prompt-packages/
    examples/
  templates/
    skill-spec.template.yaml
    command-spec.template.yaml
    prompt-package.template.yaml
```

## Schema Decisions

### Decision 1

`wrapper_metadata` 必須存在，但保持 agent-specific 可選欄位。  
原因是 wrapper schema 差異很大，不能強迫所有 agent 使用相同欄位集合。

### Decision 2

`human_guide` 只在 `skill-spec` 中作為可選單一路徑引用。  
human-facing 內容仍以 `.dev/guides/ai-collaboration-guides/` 為準。

### Decision 3

shared canonical assets 不直接等於 `.ai/assets/shared/` 的現況。  
本階段只是建立 canonical destination，後續 migration 再決定哪些既有檔案要搬或映射。

## Stage 2 Output

本階段已完成：

- 建立 `.ai/assets/` canonical root
- 建立 `skills/`、`commands/`、`shared/`、`templates/` 結構
- 建立三份 canonical spec templates

本階段尚未處理：

- 既有 skill / prompts 的實際 migration
- wrapper mapping
- generated wrapper strategy

