# Spec Designer Prompt Guide

本文件說明如何用 prompt 讓 AI 協助整理 spec 文件。

目前它不是正式 skill，而是 human-facing prompt guide，目標是讓你能快速把 requirement 轉成符合 `.dev/specs/` 規範的 markdown / json spec。

目前 `.dev/specs/` 已分成：

- `.dev/specs/domains/`
- `.dev/specs/tests/`

## 適合用在什麼情況

- 已有 requirement，需要展開成 use case / adapter / entity spec
- 已知道主要 aggregate，但還沒整理成正確的 spec 結構
- 想先建立最小 JSON spec，再交給後續流程使用

## 不適合用在什麼情況

- requirement 還很模糊
- aggregate 邊界還沒確認
- 你其實要的是測試 scenario，而不是 implementation spec

若你要的是測試 scenario、Given-When-Then 或 BDD/TDD test intent：

- production spec 放 `.dev/specs/domains/`
- test spec 放 `.dev/specs/tests/`
- test spec 依測試目標放到 `aggregate/`、`use-cases/`、`integration/`、`cross-domain/` 或 `e2e/`
- scenario 設計優先交給 `bdd-gwt-test-designer`

## 參考規範

- `.dev/specs/SPEC-GUIDE.MD`
- `.dev/specs/SPEC-ORGANIZATION-GUIDE.MD`

## 輸出目標

依 spec 類型輸出：

- use case spec JSON
- adapter / controller spec JSON
- entity / value object spec markdown 或 JSON

並且要對齊：

- aggregate 目錄位置
- 命名規則
- 必要欄位
- cross references

## Prompt 撰寫重點

至少提供：

1. 來源 requirement 或需求摘要
2. spec 類型
3. 主要 aggregate
4. 預期輸出格式
5. 是否要維持最小 spec 或補 recommended fields

## 範本 1：從 requirement 產生 use case spec

```text
Create a use case spec JSON from this requirement, following `.dev/specs/SPEC-GUIDE.md` and `.dev/specs/SPEC-ORGANIZATION-GUIDE.md`.

Context:
- Requirement: [paste or summarize]
- Aggregate: [aggregate]
- Spec type: use case
- Output only the JSON content

Focus on:
- required keys
- aggregate placement
- consistent naming
- domain event and repository references

Return:
1. the JSON spec
2. recommended file path
3. assumptions or missing fields
```

## 範本 2：建立 controller spec

```text
Create an adapter/controller spec JSON based on this requirement and use case.

Context:
- Requirement: [summary]
- Use case: [use case]
- Aggregate: [aggregate]
- Base path expectation: [path]

Focus on:
- `spec.basePath`
- `spec.endpoints`
- validation and error mapping
- DTO and policy notes

Return:
1. the JSON spec
2. recommended file path
3. assumptions and open questions
```

## 範本 3：審查並修正既有 spec

```text
Review and normalize this spec so it matches `.dev/specs/SPEC-GUIDE.md` and `.dev/specs/SPEC-ORGANIZATION-GUIDE.md`.

Context:
- Existing spec: [paste JSON or markdown]
- Intended aggregate: [aggregate]
- Keep the behavior intent unchanged

Focus on:
- missing required fields
- wrong aggregate placement
- naming consistency
- cross references

Return:
1. revised spec
2. recommended file path
3. issues found and assumptions made
```

## 什麼情況要先交給 Architect

若你發現：

- 不確定 use case 應屬於哪個 aggregate
- 不確定這是 command / query / reactor 哪一類
- 不確定 MQ、API、domain event 的責任分配

先交給 `ddd-ca-hex-architect`，再回來整理 spec。
