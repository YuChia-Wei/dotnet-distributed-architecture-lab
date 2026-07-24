# 外部 AI 討論與回饋回收指南

本指南提供一個可在 ChatGPT 線上聊天、work-style 對話、Claude Fable 5
或其他外部 AI 環境中進行長時間討論，再把結果安全帶回 repository 的
方法。外部對話負責提供不同觀點；repository 端負責固定版本、重現主張、
建立穩定 finding ID 與決定是否採用。

## 核心邊界

- 外部 AI 不必遵守本 repository 的 assessment 或 workflow 格式。
- 外部回覆是 attributed evidence，不是 canonical truth 或寫入授權。
- 每輪討論都必須固定完整 Git commit，不能只寫「目前 main」。
- 不依賴線上對話的隱藏記憶；每輪都要有可重新附上的 discussion packet。
- standards 必須按主題切分，不把整個 standards corpus 一次塞進同一輪。
- 回收後先建立 repo-native assessment，再由 owner 選擇是否進入 workflow。

## Roundtrip

### 1. 在 repository 建立 bounded packet

由 owning workflow 建立一份 `brief.md`，至少包含：

```markdown
# Discussion Brief

- Round ID:
- Repository:
- Branch:
- Full commit:
- Topic:
- Included files:
- Explicit exclusions:
- Existing invariants:
- Known validators:
- Decision questions:
- Desired feedback:
- Non-authority notice:
  This discussion is advisory and does not authorize repository changes.
```

一輪只處理一個問題，例如：

- 哪些規則是 normative，哪些只是 explanation；
- 範例是否應搬到 progressive-disclosure 路徑；
- validator 已涵蓋哪些規則，哪些仍只能依靠 prose；
- 某一組 standards 是否存在重複、衝突或 tech-stack boundary 問題；
- 精簡後會如何影響低成本模型、fresh session 與 downstream repository。

### 2. 在 ChatGPT 或 Fable 5 進行討論

把 `brief.md` 與其中列出的必要檔案附加或貼入對話。不要假設 reviewer
能存取 repository、其他聊天或前一輪的隱藏狀態。

可使用以下起始提示：

```text
請把附加的 Discussion Brief 視為本輪唯一的 repository 狀態契約。
這是一輪獨立諮詢，不是寫入授權。請先確認 subject commit、範圍與排除項，
再針對 Decision questions 討論。若需要更多檔案，請列出精確路徑與原因，
不要推測未提供的 repository truth。
```

長對話應定期要求階段性 synthesis，避免接近平台額度時只留下零散訊息。
每個 synthesis 至少保留：已同意、仍有分歧、需要證據、下一輪問題。

### 3. 要求可攜式最終回覆

討論結束時，要求一份可複製或下載的 Markdown 結果。建議但不強制包含：

```markdown
# External Discussion Result

## Subject And Scope
## Assumptions
## Retain
## Simplify Or Move
## Validator Consequences
## Compatibility And Migration Risks
## Options And Tradeoffs
## Decision Ledger
## Unresolved Questions
## Evidence Or Commands To Reproduce
```

如果 reviewer 使用自己的格式，仍可原樣回收；接收端不能為了符合模板而
改寫其原始意見。

### 4. 帶回 repository

把最終回覆、必要的 conversation export、原始 brief 與 reviewer/日期資訊
交給 repository agent。接收端依
[`ASSESSMENT-ARTIFACT-POLICY.md`](../../standards/ASSESSMENT-ARTIFACT-POLICY.md)
執行：

1. 建立新的 repo-native assessment；
2. 在 `evidence/<source-id>/` 原樣保留外部材料；
3. 固定並驗證 subject commit；
4. 以 repository-native evidence 重現 material claims；
5. 記錄 confirmed、added、downgraded、overturned 與 unresolved claims；
6. 配發穩定 finding IDs；
7. 只有 owner 選中的 findings 才能建立 backlog 或 remediation workflow。

## Standards 專用討論策略

`STD-001` 應將 standards 討論拆成多輪，而不是嘗試在單一 agent session
完成所有細節。建議順序：

1. 分類：normative rule、example、explanation、human guide、validator rule。
2. 事實：建立重複、衝突、引用與 validator coverage inventory。
3. 設計：比較保留原位、progressive disclosure、抽取、合併與移除方案。
4. 風險：檢查開發行為、skill routing、下游 upgrade 與版本相容性。
5. 決策：形成 owner-reviewed decision ledger。
6. 排程：最後才決定併入既有版本或建立 standards 專屬版本。

## 不接受的捷徑

- 只帶回一段摘要，卻無法確認討論使用的 commit 或輸入檔案。
- 直接把 ChatGPT 或 Fable 的建議貼入 canonical standards。
- 用 repository 總字數代替實際 context-load 或 token evidence。
- 在 validator 尚未承接規則前刪除唯一的 prose enforcement。
- 為了趕上 v0.6.0 而預先限制 standards 討論深度或版本邊界。
