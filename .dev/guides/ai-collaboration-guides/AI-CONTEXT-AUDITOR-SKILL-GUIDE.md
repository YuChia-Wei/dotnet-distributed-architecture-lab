# AI Context Auditor Skill 使用指南

`ai-context-auditor` 用來定期檢查 repository 內的 AI context 健康度，包含目錄分層、canonical ownership、規則衝突、runtime wrapper、skill routing、索引、語言政策、workflow lifecycle 與 validation integrity。

輸出分成兩種持久性模式：若使用者只要求分析，結果可留在對話中，不建立 branch、assessment、workflow、report file 或 commit；若明確要求保存或落地但未授權 remediation，建立 standalone assessment。多階段分析或使用 sub-agent 本身不會把 transient analysis 變成 durable artifact。

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
- allocate an ASM-YYYYMMDD-NNN assessment ID;
- save the report under .dev/assessments/<assessment-id>/report.md;
- do not remediate findings; hand authorized remediation to ai-context-governance.
```

## 報告位置

Standalone audit 預設使用：

```text
.dev/assessments/<ASM-YYYYMMDD-NNN>/assessment.yaml
.dev/assessments/<ASM-YYYYMMDD-NNN>/report.md
```

若 governance workflow 要求修正後複檢，建立新的 verification assessment，不可覆寫 baseline。Assessment locator 記錄 baseline、workflow 與 verification 關係。

Assessment id 使用 `ASM-YYYYMMDD-NNN`；同日依目前未使用的三位序號配置。所有 generated artifacts 使用帶 offset 的 ISO 8601 `created_at`、`updated_at`，並記錄 locator 與 report 的 `template_source`、`template_version`。

Standalone audit 先建立 `codex/assessment/<lowercase-assessment-id>` 或 runtime 對應 branch，再建立 locator/report。Commit 僅包含 assessment-owned artifacts 與 assessment index，不得混入 audited context 修正。Draft locator 的 resume 欄位負責中斷續作。若 audit 已屬於授權中的 governance workflow，使用該 workflow branch，不另外建立 assessment branch。

Assessment locator 以 `.dev/assessments/templates/` 為準；report template 以 `.ai/assets/skills/ai-context-auditor/templates/` 為準。舊 audit workflow templates 僅保留給 historical workflow 的 `template_source`。

## 後續整改

Auditor 永遠對被稽核的 context 保持唯讀，不會直接修正 findings。若使用者決定整改：

- AI context ownership、language、wrapper 或 routing → `ai-context-governance`；
- findings 分流、多階段 AI context 整改、複檢協調與結案 → `ai-context-governance`；
- 產品 source code → `code-reviewer`；
- framework 複製後的 target repo truth 重建 → `repo-structure-sync`。

Auditor 對被稽核的 context 始終保持唯讀；它只能更新自己負責的 assessment locator、report、evidence 與 assessment index，這不構成修正授權。
