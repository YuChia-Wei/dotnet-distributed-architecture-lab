# Domain Ubiquitous Language

本目錄用來收納目標 repo 的 domain ubiquitous language 文件。

它的目的不是建立技術詞彙表，也不是保存這個 context framework 來源 repo 的產品真相；它只提供新專案或既有專案整理領域詞彙時的文件位置與範本。

## 定位

- 放置 bounded context、aggregate、domain event、command/query/reaction 等與領域語意有關的統一詞彙。
- 內容應以目標 repo 的需求、規格、程式碼、事件、API、UI 文案或 domain expert 決策作為來源。
- 若本 framework 被複製到另一個 repo，已填寫的 domain language 文件必須依目標 repo facts 重寫。
- 技術詞彙、架構模式詞彙、工具詞彙暫不放在這裡。

## 建議結構

```text
.dev/domain-language/
  README.MD
  templates/
    bounded-context-language-template.md
    aggregate-vocabulary-template.md
    domain-event-language-template.md
```

當目標 repo 需要實際文件時，建議複製 templates 到明確命名的文件，例如：

```text
.dev/domain-language/<bounded-context-id>.md
.dev/domain-language/<bounded-context-id>/<aggregate-id>.md
.dev/domain-language/<bounded-context-id>/events.md
```

## 文件規則

- 使用繁體中文台灣用語撰寫人讀說明。
- domain term 可保留英文、中文或雙語，但必須在文件中定義同義詞與禁用詞。
- 不要把未確認的猜測寫成既定 domain truth。
- 不要把 DDD / CA / Hexagonal Architecture 的技術定義混入 domain vocabulary。
- 若命名變更會影響 DTO、API、event、database schema、message contract 或 bounded context，應回到需求、規格或架構決策流程。

## 與其他文件的關係

- `.dev/requirement/`: 保存需求來源與業務問題。
- `.dev/specs/`: 保存行為規格與驗收條件。
- `.dev/operations/`: 保存 runtime event catalog、MQ topology、runbook 等營運事實。
- `.dev/domain-language/`: 保存領域語言本身與命名決策。

## 非目標

- 不建立技術詞彙表。
- 不建立 terminology skill。
- 不保存本 repo 過往專案的 domain truth。
