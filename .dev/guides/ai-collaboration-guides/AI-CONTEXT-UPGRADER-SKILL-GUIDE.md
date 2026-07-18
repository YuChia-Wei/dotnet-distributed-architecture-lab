# AI Context Upgrader Skill 使用指南

## 用途

`ai-context-upgrader` 用於已經匯入並初始化這套 AI context 的目標 repo。它會比對舊 framework 版本、新 framework 版本與目標 repo 現況，先產生分類與衝突清單，再依授權套用變更。

第一次把 framework 複製到專案時，請使用 `repo-structure-sync`；不要把 upgrader 當成初始化工具。

## 何時使用

- 目標 repo 已記錄 `.dev/AI-CONTEXT-SOURCE.yaml`，要從一個發布版本升級到另一個版本。
- 想先比較兩個 tag，評估 upgrade 影響但暫時不修改檔案。
- 目標 repo 有本地化的 `AGENTS.md`、requirements、ADRs 或 skill wrapper，需要避免被 framework 更新覆蓋。

如果既有專案沒有 provenance manifest，skill 會先產生 unresolved-provenance inventory，要求確認可信的來源版本；它不會猜測 base version。

## 核心流程

1. 驗證來源 manifest、舊 tag、新 tag 與 release record。
2. 以 base、incoming、target 做三方比對。
3. 將路徑分成 `automatic-candidate`、`reconcile`、`exclude`。
4. 先交付 migration plan；未獲授權前維持唯讀。
5. 套用使用者接受的路徑並執行目標 repo 的驗證。
6. 只有驗證成功後才更新 provenance manifest。

`automatic-candidate` 代表技術上可安全提出自動替換，不代表已獲得寫入授權。目標專案的協作規則、requirements、specs、ADRs、architecture、operations 與 project config 預設都需要 reconciliation。

## 預設排除

- framework source repo 的已完成 workflows、assessment instances、backlog 與 release history；assessment 的 reusable README、index、policy 與 templates 不在排除範圍
- `.git/`、工具 cache、暫存報告與環境檔案
- 產品 `src/` 與 `tests/`

codebase-memory-mcp、Code Graph、IDE index 等工具只能加速探索；最後的版本、檔案與內容判斷仍以 Git 和 repo 檔案為準。

## Prompt 範本

```text
使用 ai-context-upgrader，先以唯讀方式評估此 repo 從 v0.1.0 升級到 v0.3.0。
保留所有 target-owned context 與 local overrides，列出 automatic-candidate、reconcile、exclude、migration steps、validation 與 rollback boundary。
在我核准前不要套用變更，也不要更新 .dev/AI-CONTEXT-SOURCE.yaml。
```

## 完成條件

- from/to release ID、tag、full commit 都已驗證。
- 所有 incoming changes 都有分類或明確排除理由。
- target-owned truth 未被靜默覆蓋。
- 必要驗證通過。
- provenance 只描述最後一次驗證成功的 framework 狀態。
