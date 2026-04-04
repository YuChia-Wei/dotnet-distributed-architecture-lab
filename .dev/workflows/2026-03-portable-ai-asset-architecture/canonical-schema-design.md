# Canonical Schema Design

## Decision

採用 `.ai/assets/` 作為 portable AI assets 的 canonical root。

## Canonical Root Structure

```text
.ai/assets/
  README.MD
  CANONICAL-SCHEMA.MD
  skills/
  commands/
  shared/
  templates/
```

## Why This Structure

- `assets/` 比 `skills/` 更中立，可同時容納 skill、command、shared assets
- `templates/` 能讓新 asset 建立方式一致
- `shared/` 可避免 shared rules 繼續散落

## Current Decision

- 現有 `.ai/assets/` 暫時保留
- 現有 `.claude/skills/` 暫時保留
- Stage 4 起才開始將 pilot asset 遷入 `.ai/assets/`

## Schema Direction

### Canonical Spec First

- 用 YAML 定義最小 metadata
- prompt / reference 內容仍保留 Markdown

### Wrapper Later

- wrapper 不應直接發明一套新的 canonical metadata
- wrapper 儘量引用 `.ai/assets/`，而不是重複寫內容

