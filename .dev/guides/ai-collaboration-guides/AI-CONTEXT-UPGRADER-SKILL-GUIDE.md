# AI Context Upgrader Skill 使用指南

## 用途

`ai-context-upgrader` 用於已經匯入並初始化這套 AI context 的目標 repo。它會比對舊 framework 版本、新 framework 版本與目標 repo 現況，先產生分類與衝突清單，再依授權套用變更。

第一次把 framework 複製到專案時，請使用 `ai-context-init`；不要把 upgrader 當成初始化工具。

## 何時使用

- 目標 repo 已記錄 `.dev/ai-context/provenance.yaml` 與 customization ledger，要從一個發布版本升級到另一個版本；legacy manifest 僅作 read compatibility。
- 想先比較兩個 tag，評估 upgrade 影響但暫時不修改檔案。
- 目標 repo 有本地化的 `AGENTS.md`、requirements、ADRs 或 skill wrapper，需要避免被 framework 更新覆蓋。

如果既有專案沒有 provenance manifest，skill 會先產生 unresolved-provenance inventory，要求確認可信的來源版本；它不會猜測 base version。

## 核心流程

1. 使用 target validator 驗證 provenance、ledger 與 package 所攜帶的 immutable source identity，不要求下游擁有 source release registry 或 Git tags。
2. 以 base、incoming、target 做三方比對。
3. 將檔案分成 `automatic-candidate`、`reconcile`、`exclude`，並依 customization ID 產生 semantic reconciliation table。
4. 先交付 migration plan；未獲授權前維持唯讀。
5. 套用使用者接受的路徑並執行目標 repo 的驗證。
6. 只有 owner reconciliation、獨立 post-upgrade audit 與 target validation 全部成功後，才 finalize ledger 與 provenance；失敗時保留舊 provenance。

共同生命週期以
`.ai/assets/skills/ai-context-governance/references/semantic-customization-lifecycle.md`
為準。

`automatic-candidate` 代表技術上可安全提出自動替換，不代表已獲得寫入授權。目標專案的協作規則、requirements、specs、ADRs、architecture、operations 與 project config 預設都需要 reconciliation。

## 預設排除

- framework source repo 的已完成 workflows、assessment instances、backlog 與 release history；assessment 的 reusable README、index、policy 與 templates 不在排除範圍
- `.git/`、工具 cache、暫存報告與環境檔案
- 產品 `src/` 與 `tests/`

## Python 與本機 validation 邊界

升級時保留 target 的 Python 前置條件恢復決定；diagnostic 僅提出建議命令，
不會安裝依賴。本機 `.dev/validation.local.conf` 是 ignored、unpackaged 的
單行選擇檔，僅能強化 checked-in `validation.routine.local` policy，不能由
環境變數覆寫。source-only CLI 與 framework release publication 不屬於
downstream prerequisite contract。細節見
`PYTHON-PREREQUISITE-DIAGNOSTICS-GUIDE.zh-TW.md`。

升級同樣必須保留 `/.dev/ai-context/local/` ignore 規則，並將現有
`cli-execution-routing.yaml` 視為 ignored、unpackaged 的個人 CLI 狀態。
Upgrader 不得讀取、覆寫、封裝或隱含遷移其中的值；若新 schema 不相容，
應回報需要 owner decision。只有新的路由成功完成原操作，且使用者再次
明確同意後，才可更新本機設定。

codebase-memory-mcp、Code Graph、IDE index 等工具只能加速探索；最後的版本、檔案與內容判斷仍以 Git 和 repo 檔案為準。

## Prompt 範本

```text
使用 ai-context-upgrader，先以唯讀方式評估此 repo 從 v0.1.0 升級到 v0.3.0。
保留所有 target-owned context 與 local overrides，列出 automatic-candidate、reconcile、exclude、migration steps、validation 與 rollback boundary。
在我核准前不要套用變更，也不要 finalize
.dev/ai-context/provenance.yaml 或 customizations.yaml。
```

## 完成條件

- from/to release ID、tag、full commit 都已驗證。
- 所有 incoming changes 都有分類或明確排除理由。
- target-owned truth 未被靜默覆蓋。
- 必要驗證通過。
- provenance 只描述最後一次驗證成功的 framework 狀態。
