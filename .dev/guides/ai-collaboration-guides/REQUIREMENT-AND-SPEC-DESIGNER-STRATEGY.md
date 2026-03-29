# Requirement And Spec Designer Strategy

本文件定義 `requirement-designer` 與 `spec-designer` 兩種候選能力的邊界，並說明它們應先以 prompt/template 還是直接以 skill 形式落地。

## 為什麼值得拆開

`requirement` 與 `spec` 雖然相連，但不是同一層工作。

- requirement:
  - 定義問題、目標、範圍、約束、商業規則、 acceptance criteria
- spec:
  - 把 requirement 展開成可實作、可驗證、可追蹤的結構化文件

若把兩者混成同一步，常見問題會是：

- requirement 還沒穩定就提前寫成 implementation-oriented spec
- spec 補了很多未被確認的假設
- AI 直接生成 code 時缺少一致的文件基礎

## 候選角色

### `requirement-designer`

職責：

- 將模糊需求整理成可讀的 requirement markdown
- 補齊 functional / non-functional requirements
- 明確化 scope、constraints、domain rules、acceptance criteria

不負責：

- 寫 use case spec JSON
- 決定程式模組結構
- 直接生成測試或程式碼

輸出位置：

- `.dev/requirement/`

### `spec-designer`

職責：

- 將 requirement 展開成 function spec / use case spec / adapter spec / entity spec
- 對齊 `.dev/specs/` 的目錄、命名與 JSON 欄位規範
- 明確化 aggregate、domain event、repository、output 等欄位

不負責：

- 回頭發明 requirement
- 直接做 architecture redesign
- 直接生成 implementation code

輸出位置：

- `.dev/specs/`

## 與既有 skill 的關係

建議鏈如下：

```text
requirement-designer
  -> spec-designer
  -> bdd-gwt-test-designer
  -> test generation / implementer
  -> code-reviewer
```

若過程中發現：

- bounded context 邊界不清
- aggregate 分類不清
- 命名語意衝突
- MQ / API / domain role 分工不清

則先交給 `ddd-ca-hex-architect`。

## 應先做 Prompt / Template，還是直接做 Skill

### 先做 Prompt / Template 的情況

適合先做 prompt/template，若：

- 你只是偶爾需要整理 requirement 或 spec
- 規則大致穩定，但工作流還沒完全固定
- 你目前最痛的是「很難快速寫出合格文件」
- 你想先降低使用成本，快速試幾輪

這時建議先補：

- requirement prompt template
- spec prompt template
- 最小 md / json 範本
- 欄位說明

### 直接做 Skill 的情況

適合直接做 skill，若：

- 這兩件事會跨專案反覆發生
- 每次都需要固定步驟與品質檢查
- 單靠 prompt 容易漏欄位、漏規則、漏交叉引用
- 你希望其他 agent 或未來的自己都走同一套流程

## 我對目前 repo 的建議

現階段建議：

1. 先做 `requirement-designer` prompt / guide
2. 再做 `spec-designer` prompt / guide
3. 等實際使用幾輪後，再決定是否升級成 skill

理由：

- `.dev/requirement/requirement-guide.md` 已有明確 markdown 結構
- `.dev/specs/SPEC-GUIDE.md` 與 `.dev/specs/SPEC-ORGANIZATION-GUIDE.md` 已有明確格式與目錄規範
- 你目前缺的更像是「如何把模糊想法快速整理成合格文件」，這通常先用 prompt/template 就能解決

## 升級判斷點

當你觀察到以下情況時，就值得升級成 skill：

- requirement 常漏 acceptance criteria 或 non-functional constraints
- spec 常漏必要 JSON keys 或 aggregate 歸屬
- 需要反覆做 requirement -> spec 的轉換
- 多個 agent 對文件格式理解不一致

## 下一步建議

最小可行方案：

1. 先建立一份 human-facing guide，說明 requirement / spec 各自怎麼下 prompt
2. 補兩份 prompt templates
3. 實際用幾輪後，再決定是否建立正式 skill
