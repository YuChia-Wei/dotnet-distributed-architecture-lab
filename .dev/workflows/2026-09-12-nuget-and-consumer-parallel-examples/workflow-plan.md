# NuGet 更新與 Consumer 並行範例

## Workflow Metadata
- workflow_id: `2026-09-12-nuget-and-consumer-parallel-examples`
- plan_id: `development-plan-2026-09-12-nuget-and-consumer-parallel-examples`
- owner_skill: `software-development-orchestrator`
- branch: `codex/2026-09-12-nuget-and-consumer-parallel-examples`
- base_branch: `main`
- status: active
- created_at: `2026-09-12T13:52:33+08:00`
- updated_at: `2026-09-12T13:52:33+08:00`
- template_source: `.ai/assets/skills/software-development-orchestrator/templates/development-workflow-plan-template.md`
- template_version: `1.4.0`

## 授權與交付範圍
使用者於 2026-09-12 授權開立 GitHub Issue 與本機實作。Issue #10、#11 已開立並回讀。main 與 origin/main 起點均為 `57b1f2150b6f306e8d784fb6d81133ebc7d7437b`。

三個實質工作共用更新後的 Wolverine 與回歸驗證，因此保留一個 workflow/branch；套件與兩種範例各自有可續作的 task。工作流程保留主要版本升級及兩個執行模型的分階段驗證/恢復狀態。push、PR、merge、發佈未授權。

## Development Stages
| Task | Outcome | Dependencies | Status |
| --- | --- | --- | --- |
| DEV-001 | 全部直接套件相容更新、xUnit v3 遷移及版本矩陣 | none | pending |
| DEV-002 | Task.WhenAll 並行範例與隔離 scope、失敗/取消測試 | DEV-001 | in_progress |
| DEV-003 | 原始外部 MQ 事件觸發兩個獨立 handler 與真實 Kafka 路由/重試測試 | DEV-001, DEV-002 | pending |

## Architecture And Acceptance
Consumer 範例屬 lab diagnostics，不創造新業務 aggregate。使用者修正：兩個 handler 都必須處理原始外部 MQ 事件，不能改成另一種本機事件。WhenAll 版本等待兩項工作，各分支使用獨立 scope。另一版本利用 Wolverine 6.36.0 MultipleHandlerBehavior.Separated 與兩個 sticky local queues；單一外部 listener 收到原始事件，內建 FanoutMessageHandler 把同一事件派送到兩個原始事件型別 handler。沒有應用程式自訂轉發 handler、衍生事件或第二個 Kafka consumer group。內部 local queues 是 framework 的執行隔離机制，事件來源仍為 Kafka。

依使用者補充要求，正式回歸與 E2E 使用既有 mqarchlab-pr5-integration Compose 專案；暫存 Kafka 已停止。外部測試在同一 Compose network 使用既有 Kafka broker，真實 MQ 測試必須驗證入站 fanout、兩分支重疊、scope 隔離及單分支失敗重試。記憶體測試只屬輔助。每分支示範程序內冪等，不宣稱重啟持久化保證。

Upstream V6.36.0 evidence: src/Wolverine/Runtime/Handlers/HandlerGraph.cs, FanoutMessageHandler.cs, and src/Transports/RabbitMQ/Wolverine.RabbitMQ.Tests/fanout_from_external_to_separated_local_handlers.cs at https://github.com/JasperFx/wolverine/tree/V6.36.0 . These guide implementation; local Kafka execution remains the acceptance authority.

## Validation Strategy
- .NET 10 restore/build、五個現有測試專案、NuGet outdated/deprecated/vulnerable（含 transitive）檢查。
- 真實 Kafka broker 與 Wolverine host 的原始外部事件派送測試；既有 consumer failure policy 與 request/reply 回歸。
- 外部 PostgreSQL/Kafka 測試僅按既有 opt-in 規則執行；skip 不列為 passed。
- Spec compliance 未選用，not-applicable。routine validation local=manual，不隱式改設定；明確執行必要的 workflow 與 target closeout gates。
- 子代理僅進行唯讀套件/API 證據研究；主要代理為唯一 tracked writer。skill role 實作直接執行並保留紀錄。

## Progress And Handoff
目前 DEV-002。兩個模型與套件遷移已實作，先前 focused 測試已通過，正式 Compose 回歸與 E2E 尚待完成。若中斷，先讀 task、Git diff 與 evidence 再續作；不從 Issue 狀態推論完成。
