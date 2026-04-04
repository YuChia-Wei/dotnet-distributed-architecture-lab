# AI Collaboration Guides

本目錄放置「給人看的」AI collaboration、skill、prompt 與 AI agent 協作使用指南。

## 目的

- 說明某個 skill 或 collaboration workflow 可以做什麼
- 提供可直接複製的 prompt 範本
- 說明何時該用 skill、何時該看 `.ai/` prompt 元件
- 讓人類使用者理解 repo 內的 AI 協作方式

## 與其他目錄的分工

- `.dev/guides/ai-collaboration-guides/`: 給人看的 AI collaboration guides、workflow、prompt 與操作指南
- `.dev/workflows/`: 跨 skill workflow artifacts 的正式存放位置
- `.dev/guides/`: 一般軟體開發、架構、框架、專案使用指南
- `.ai/`: 給 agent 重用的 prompt 元件、shared rules、scripts
- `.claude/skills/`: skill 實作本體與 agent 觸發後讀取的內容

## 目前文件

- `AI-REFACTORING-SKILL-BOUNDARY-GUIDE.md`: `ddd-ca-hex-architect`、`code-reviewer`、`staged-refactor-implementer`、`tactical-refactor-implementer` 的邊界與工作流
- `AI-REFACTORING-SKILL-CONTRACTS.md`: 四個重構 skill 的最小 input / output contract 與 handoff 規則
- `AI-COLLABORATION-WORKFLOW-GUIDE.md`: requirement / spec / testing / refactor / review 的整體 AI 協作流程
- `AI-ASSET-LOCATION-STRATEGY.md`: 多 agent 情境下 skill / prompt / guide / workflow artifact 的收納策略
- `LOCAL-RUNTIME-WRAPPER-GUIDE.md`: repo wrapper 與本機 runtime 的使用方式
- `OPTIONAL-MINIMAL-WORKFLOW-MODE.md`: 可選的最小 workflow 模式與 artifact 說明
- `DDD-CA-HEX-ARCHITECT-SKILL-GUIDE.md`: `ddd-ca-hex-architect` 的使用說明與 prompt 範本
- `BDD-GWT-TEST-DESIGNER-SKILL-GUIDE.md`: `bdd-gwt-test-designer` 的使用說明與 Given-When-Then prompt 範本
- `BDD-GWT-TEST-DESIGNER-PAIR-GUIDE.md`: `bdd-gwt-test-designer` 與 test generation / review workflow 的搭配方式
- `REQUIREMENT-AND-SPEC-DESIGNER-STRATEGY.md`: requirement / spec 是否應該做成 prompt 或 skill 的邊界與採用策略
- `REQUIREMENT-DESIGNER-PROMPT-GUIDE.md`: requirement markdown 草稿與補齊工作的 prompt 範本
- `SPEC-DESIGNER-PROMPT-GUIDE.md`: use case / adapter / entity spec 整理工作的 prompt 範本
- `STAGED-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`: `staged-refactor-implementer` 的使用說明與 prompt 範本
- `TACTICAL-REFACTOR-IMPLEMENTER-SKILL-GUIDE.md`: `tactical-refactor-implementer` 的使用說明與 prompt 範本
- `AI-SKILL-GUIDE-STANDARDS.md`: 本目錄內 AI collaboration guides 的通用撰寫與分工規範

## Workflow Templates

- `AI-REFACTORING-SKILL-CONTRACTS.md`
- `templates/workflow-plan-template.md`
- `templates/review-report-template.md`
- `templates/workflow-task-template.json`

## 維護規則

- 新增 human-facing 的 AI skill 使用說明時，優先放在本目錄。
- 每個 skill 至少應有一份對應 guide，說明用途、適用情境、prompt 範本與輸出期待。
- 本目錄的文件是給人讀的，不應複製大量 `.ai/` prompt 內部細節。
- skill 實作細節仍以 `.claude/skills/<skill>/` 為準；本目錄只做人類入口與操作指南。
- 若 guide 內容與 skill 本體衝突，應同步修正並避免形成雙重真相。


