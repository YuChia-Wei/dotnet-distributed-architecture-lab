# AI Context Auditor Skill 使用指南

`ai-context-auditor` 用來定期檢查 repository 內的 AI context 健康度，包含目錄分層、canonical ownership、規則衝突、runtime wrapper、skill routing、索引、語言政策、workflow lifecycle 與 validation integrity。

輸出分成兩種模式：若使用者只要求分析，結果可留在對話中，不建立 branch、workflow、report file 或 commit；若明確要求保存、落地或持續追蹤，才建立 durable report workflow。多階段分析或使用 sub-agent 本身不會把 transient analysis 變成 durable workflow。

## 適用情境

- 定期執行 AI context 自檢；
- 評估 prompt／skill repository 的品質；
- 檢查 `.ai`、`.dev`、`.agents`、`.claude` 是否漂移；
- 比較「一般知識獨立分析」與「套用 repo skill／policy 分析」的差異；
- 追蹤前一次 audit finding 是否仍然存在。

## 預設掃描邊界

Auditor 預設只掃描 AI context 與治理相關 surfaces，例如 root README 與 agent instructions、`.ai/**`、`.dev/**`、`.agents/**`、`.claude/**`、AI assistant 相關的 `.github/**` 文件，以及被上述文件直接引用的 context validation manifests、README 或 scripts。

預設略過：

- `src/**`；
- `tests/**`、`test/**`；
- 實際產品的 Domain、Application、Infrastructure、API 與 test implementation；
- `bin/**`、`obj/**`、`dist/**`、dependencies 與 generated output。

## 與 Code Review 的邊界

若要求包含產品 source code、test code、solution 或 implementation quality，auditor 不應自行擴大掃描。它必須說明未掃描的路徑，並建議改用 `code-reviewer`。

建議 prompt：

```text
Use $code-reviewer to review the requested .NET source and test files.
Keep the AI context audit report as background only; do not treat context findings as code findings.
```

## 標準執行方式

單次對話分析：

```text
Use $ai-context-auditor to analyze this repository AI context in transient direct mode.
Return findings in the conversation only; do not create repository artifacts or remediate findings.
```

需要落地保存時：

```text
Use $ai-context-auditor to perform a recurring AI context self-audit.

Requirements:
- first create an independent baseline using general knowledge;
- then apply repository governance skills and policies;
- compare both passes;
- exclude src and tests;
- save a baseline report under <artifact-root>/reports/01-audit-report.md;
- do not remediate findings; hand authorized remediation to ai-context-governance.
```

## 報告位置

預設使用：

```text
.dev/workflows/<YYYY-MM-DD-topic[-NN]>/workflow.yaml
<artifact-root>/reports/01-audit-report.md
```

若 governance workflow 要求修正後複檢，輸出到 `<artifact-root>/reports/03-post-remediation-audit-report.md`，不可覆寫 baseline。`workflow.yaml` 是固定 locator，即使 skill 依任務特性把 `artifact_root` 指向其他位置仍需保留。

Workflow id 使用完整日期 `YYYY-MM-DD-topic[-NN]`；同日碰撞時附加 `-02`、`-03`。所有 generated artifacts 使用帶 offset 的 ISO 8601 `created_at`、`updated_at`，並記錄 `template_source`、`template_version`。

Audit 需要 durable workflow 時，先建立獨立 branch，再建立 locator/report。Locator 記錄 `branch` 與 `base_branch`，commit 僅包含 auditor 擁有的 locator、plan、task 與 report artifacts，不得混入 audited context 修正。未完成 audit 若被要求 merge/push，維持 workflow active 並視為 checkpoint；branch 與 merge 細節依 `.dev/TEAM-GIT-FLOW-RULES.MD`。

報告與 audit workflow templates 以 `.ai/assets/skills/ai-context-auditor/templates/` 為準。

## 後續整改

Auditor 永遠對被稽核的 context 保持唯讀，不會直接修正 findings。若使用者決定整改：

- AI context ownership、language、wrapper 或 routing → `ai-context-governance`；
- findings 分流、多階段 AI context 整改、複檢協調與結案 → `ai-context-governance`；
- 產品 source code → `code-reviewer`；
- framework 複製後的 target repo truth 重建 → `repo-structure-sync`。

Auditor 對被稽核的 context 始終保持唯讀；它只能更新自己負責的 workflow metadata、audit task 與報告，這不構成修正授權。
