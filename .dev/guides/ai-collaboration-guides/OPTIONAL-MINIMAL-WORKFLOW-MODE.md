# Optional Minimal Workflow Mode

本文件定義 architecture / review / implementer 協作時的「可選的最小 workflow 模式」。

## 為什麼是可選的

相關 skill 預設都應該可以直接使用。

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

- 先 architect，再 review，再 slice implement，再 review
- 要保留每一輪 stage 的上下文
- 要把 architecture decision 與 implementation scope 對齊
- 要避免每輪都重新解釋需求與邊界

## 最小 Artifact 集

固定保留一個 discovery locator，再依 development workflow 需要使用最多三類 artifacts：

1. `.dev/workflows/<workflow-id>/workflow.yaml`（固定 locator）
2. `workflow-plan.md`
3. `tasks/<task-id>.json`
4. `review-report.md`（只有正式 development review 時需要）

這是 development workflow 的精簡集合，不是所有 workflow kind 的萬用格式。AI context audit 與 remediation 使用其 owner skills 的 templates 和 report layout。

最小欄位定義與 handoff 規則見：

- `AI-REFACTORING-SKILL-CONTRACTS.md`

預設存放位置：

- `.dev/workflows/<workflow-id>/`

新 workflow 使用 `YYYY-MM-DD-<topic>[-NN]`。Locator 和 task 必須記錄帶時區的 ISO 8601 `created_at`、`updated_at`；artifact body 需記錄 `template_source` 與 `template_version`。

進入 workflow mode 時，先建立獨立 branch，再建立 locator。Locator/plan 記錄 `branch`、`base_branch` 與 checkpoint history；workflow merge 預設 `--no-ff`。未完成時的 merge/push 只算 checkpoint；push-only 從已推送 branch 接續，checkpoint merge 後才改由新的 continuation branch 接續。

## Artifact 角色

### `workflow.yaml`

由 `dev-workflow` 建立並維護 locator metadata。即使 development artifact root 改到其他 repository-relative 位置，locator 仍留在 `.dev/workflows/<workflow-id>/`。

### `workflow-plan.md`

由 `dev-workflow` 使用自有 template 建立；`ddd-ca-hex-architect` 可更新已授權的 architecture sections。

用途：

- 記錄問題診斷
- 記錄目標方向
- 定義 stages
- 定義每個 stage 的非目標與風險

### `review-report.md`

由 `code-reviewer` 建立或更新。

用途：

- 記錄正式 review 結果
- 記錄 architecture-level / implementation-level / development-document / workflow-level findings
- 記錄嚴重度
- 記錄 review decision
- 建議下一個 skill

### `tasks/<task-id>.json`

由 `slice-implementer` 或 `local-change-implementer` 建立或更新。

用途：

- 記錄這一輪要執行的具體工作
- 綁定 plan 與 review 的輸入
- 記錄狀態、限制、結果、驗證

## 建議工作流

```text
1. dev-workflow
   建立 workflow.yaml、workflow-plan.md 與初始 task

2. ddd-ca-hex-architect
   更新已授權的 architecture sections

3. code-reviewer
   需要時建立 review-report.md

4. slice-implementer / local-change-implementer
   需要時建立對應的 `tasks/<task-id>.json`

5. code-reviewer
   對本輪結果再次 review
```

## 啟用原則

### Direct Mode

若任務小、單純、單 skill 可完成：

- 不建立 artifact
- 直接使用 skill

### Workflow Mode

若任務跨 skill、跨 stage、或需要保存決策：

- 建立 locator 與必要 development artifacts
- 由 skill 之間透過 artifact handoff
- artifact 預設放在 `.dev/workflows/<workflow-id>/`，替代 root 必須由 locator 宣告

## 不要做的事

- 不要為了小任務強制建立 workflow artifact
- 不要把 workflow mode 變成每次都要跑的重流程
- 不要讓 artifact 取代 skill 的判斷
- 不要讓 artifact 數量繼續膨脹

## 相關模板

- `AI-REFACTORING-SKILL-CONTRACTS.md`
- `../workflows/README.MD`
- `../../../.ai/assets/skills/dev-workflow/templates/development-workflow-plan-template.md`
- `../../../.ai/assets/skills/dev-workflow/templates/development-review-report-template.md`
- `../../../.ai/assets/skills/dev-workflow/templates/development-workflow-task-template.json`


