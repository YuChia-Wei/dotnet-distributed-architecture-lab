# Optional Minimal Workflow Mode

本文件定義四個重構 skill 的「可選的最小 workflow 模式」。

## 為什麼是可選的

這四個 skill 預設都應該可以直接使用。

也就是：

- 使用者直接呼叫 skill
- skill 自己判斷是否在邊界內
- 如果越界，再提醒改用其他 skill

只有在下列情況，才建議啟用 workflow mode：

- 這次工作會跨多個 skill 接力
- 你希望保留重構決策與交接資訊
- 你希望 reviewer、architect、implementer 之間有穩定 handoff
- 你要把這套流程帶去另一個專案使用

## 什麼時候不用 workflow mode

下列情況通常可直接呼叫 skill，不需要額外 artifact：

- 單次 code review
- 局部抽方法
- 單一小範圍 rename
- 已知目標的一個 safe slice
- 不需要跨 skill 傳遞上下文

## 什麼時候建議用 workflow mode

下列情況建議啟用：

- 先 architect，再 review，再 staged implement，再 review
- 要保留每一輪 stage 的上下文
- 要把 architecture decision 與 implementation scope 對齊
- 要避免每輪都重新解釋需求與邊界

## 最小 Artifact 集

只使用三個 artifact：

1. `workflow-plan.md`
2. `review-report.md`
3. `tasks/<task-id>.json`

這是最小集合，不額外新增更多流程文件。

最小欄位定義與 handoff 規則見：

- `AI-REFACTORING-SKILL-CONTRACTS.md`

預設存放位置：

- `.dev/workflows/<workflow-id>/`

## Artifact 角色

### `workflow-plan.md`

由 `ddd-ca-hex-architect` 建立或更新。

用途：

- 記錄問題診斷
- 記錄目標方向
- 定義 stages
- 定義每個 stage 的非目標與風險

### `review-report.md`

由 `code-reviewer` 建立或更新。

用途：

- 記錄正式 review 結果
- 記錄 architecture-level / implementation-level / document-level / workflow-level findings
- 記錄嚴重度
- 記錄 review decision
- 建議下一個 skill

### `tasks/<task-id>.json`

由 `staged-refactor-implementer` 或 `tactical-refactor-implementer` 建立或更新。

用途：

- 記錄這一輪要執行的具體工作
- 綁定 plan 與 review 的輸入
- 記錄狀態、限制、結果、驗證

## 建議工作流

```text
1. ddd-ca-hex-architect
   需要時建立 workflow-plan.md

2. code-reviewer
   需要時建立 review-report.md

3. staged-refactor-implementer / tactical-refactor-implementer
   需要時建立對應的 `tasks/<task-id>.json`

4. code-reviewer
   對本輪結果再次 review
```

## 啟用原則

### Direct Mode

若任務小、單純、單 skill 可完成：

- 不建立 artifact
- 直接使用 skill

### Workflow Mode

若任務跨 skill、跨 stage、或需要保存決策：

- 建立最小 artifact
- 由 skill 之間透過 artifact handoff
- artifact 預設放在 `.dev/workflows/<workflow-id>/`
- 實作進行中要維持 commit discipline；每個已完成且有最小驗證的 bounded slice 都應先 commit，再進下一個 slice

## 不要做的事

- 不要為了小任務強制建立 workflow artifact
- 不要把 workflow mode 變成每次都要跑的重流程
- 不要讓 artifact 取代 skill 的判斷
- 不要讓 artifact 數量繼續膨脹
- 不要把整個 workflow 的程式碼與文件修改累積到最後一個超大 commit

## 相關模板

- `AI-REFACTORING-SKILL-CONTRACTS.md`
- `../workflows/README.MD`
- `../../workflows/templates/workflow-plan-template.md`
- `../../workflows/templates/review-report-template.md`
- `../../workflows/templates/workflow-task-template.json`


