# AI Context Governance Skill Guide

本文件是 `ai-context-governance` 的 human-facing 使用指南。canonical skill 規則以 `.ai/assets/skills/ai-context-governance/skill.yaml` 與其 references 為準。

## 這個 Skill 可以做什麼

適合用在：

- 整理 `.ai/`、`.dev/`、`.agents/`、`.claude/` 的 AI context 邊界
- 拆分 universal AI context 與 tech-stack-specific context
- 定義或套用 AI context language policy
- 同步 canonical skill spec、runtime wrapper、human guide、index
- 建立 AI 文件整理 workflow
- 接手自檢 findings，管理 audit → remediation → post-remediation audit → closure 的完整生命週期
- 建立 remediation tasks、修正報告、續作 checkpoint 與結案證據
- 避免把純 AI 文件整理誤交給 BDD、code review、或 production implementer skill

## 不應該做什麼

不應該用它來：

- 設計 Given-When-Then scenarios
- 實作 production code
- 做正式 code review
- 重新設計 domain architecture
- 大量翻譯所有文件，除非 workflow 明確要求 translation migration
- 代替 `ai-context-auditor` 撰寫基準或修正後的獨立稽核結論

## 使用時機

當工作關鍵字包含下列意圖時，優先使用這個 skill：

- AI context cleanup
- prompt/context boundary
- language policy
- skill routing
- wrapper sync
- universal vs dotnet-backend split
- documentation governance
- AI context audit remediation / post-audit / closure

## 自檢與修正生命週期

只在對話中回覆的 transient read-only analysis 不屬於 remediation workflow，也不需要 branch、artifacts 或 commit。當使用者授權修正時，治理工作才建立 durable workflow；若基準稽核需要成為正式追蹤證據，應先由 auditor 建立 standalone assessment。

完整的 AI context 維護流程由本 skill 協調：

1. `ai-context-auditor` 產生唯讀 baseline assessment，存放於 `.dev/assessments/<assessment-id>/report.md`。
2. 本 skill 逐項分類 findings、建立 tasks 並執行已授權修正。
3. 本 skill 產生 `reports/remediation-report.md`，以 `<assessment-id>#<finding-id>` 記錄每個 finding 的處置與證據。
4. `ai-context-auditor` 獨立複檢並建立新的 verification assessment。
5. 本 skill 對照三份報告、確認 commit 與 validation，最後結案或明確 defer。

Baseline assessment 不得被修正報告或 verification assessment 覆寫或複製成第二份 truth。

## Workflow 與時間欄位

- 建立 workflow artifacts 前，先建立 `codex/<workflow-id>` 或 runtime 對應的獨立 branch。
- Workflow id 使用 `YYYY-MM-DD-topic[-NN]`，同日重複時依序使用 `-02`、`-03`。
- `.dev/workflows/<workflow-id>/workflow.yaml` 永遠保留為 locator；實際 `artifact_root` 可由本 skill 依任務特性指定。
- Locator 與 plan 記錄 `branch`、`base_branch`；workflow 不得直接在 `main` 上執行。
- `created_at`、`updated_at` 使用帶明確 offset 的 ISO 8601。
- 所有 generated artifacts 記錄 `template_source` 與 `template_version`。
- 暫停前更新 locator、plan 與 active task 的 checkpoint，包含最後完成動作、下一步、validation 與 Git state。
- 未完成時若使用者要求 merge/push，視為 checkpoint handoff：維持 active/pending 並記錄 checkpoint evidence；merge 預設 `--no-ff`。Push-only 從已推送 branch 接續，checkpoint merge 後才建立新的 continuation branch。

本 skill 的 templates 位於 `.ai/assets/skills/ai-context-governance/templates/`。

## Prompt 範本

```text
Use $ai-context-governance to classify and clean up AI context boundaries.

Focus on:
- universal AI context
- dotnet-backend-only context
- repo-specific project truth
- runtime wrappers
- human-facing guides

Do not use BDD scenario design for this task.
Return the files updated, boundary decisions, and validation performed.
```

完整整改可改用：

```text
Use $ai-context-governance to continue the AI context maintenance workflow from the baseline audit.
Create finding-level remediation tasks, keep the baseline immutable, request an independent post-remediation audit, and close only with explicit evidence for every finding.
```

## 與其他 Skill 的邊界

- `bdd-gwt-test-designer`
  - 只處理 BDD/Gherkin scenario 與 assertion 設計。
- `ddd-ca-hex-architect`
  - 處理 domain / architecture design；可協助重大 context 邊界決策。
- `repo-structure-sync`
  - 用於 template 複製到 target repo 後，依 target repo facts 重建架構入口文件。
- `slice-implementer`
  - 用於已決定的 bounded implementation slice；若是 AI context governance，應先由本 skill 定義邊界。
- `local-change-implementer`
  - 用於局部技術變更；不應用來主導 AI context governance。
