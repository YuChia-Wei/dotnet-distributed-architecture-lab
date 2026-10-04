# 專案開發知識

本目錄保留 `dotnet-mq-arch-lab` 的專案事實、需求、規格、決策、操作與工作紀錄。
從 [產品 README](../README.md) 了解實驗室目的與範圍，依
[AGENTS.md](../AGENTS.md) 執行協作，再用 [專案索引](INDEX.md) 找到本次工作的權威來源。

| 工作 | 先讀 |
| --- | --- |
| 理解產品與 context 邊界 | [商務需求概覽](requirement/distributed-commerce-bounded-context-overview.md)、[架構](ARCHITECTURE.md) |
| 修改行為或測試 | [可重建行為基準](requirement/reconstructable-system-baseline.md)、[規格](specs/)、[目標工程規則](ai-context/TARGET-ENGINEERING-RULES.md) |
| 操作既有環境 | [Operations](operations/README.MD) 與該情境的具體操作指南 |
| 維護協作 context | [目前框架契約](ai-context/CURRENT-FRAMEWORK.md)、[技能索引](ai-context/skills.md)、[政策索引](standards/INDEX.MD) |
| 開始一項有限範圍工作 | [第一項工作指南](guides/first-task.md) |

`project-config.yaml` 是來源檔案與既有決策的衍生 inventory，不能取代原始碼、
專案檔、需求或接受的決策。需求、規格、ADR、operations 與 workflow 紀錄維持各自權責；
歷史通過結果只適用於其記錄的 revision 與範圍。

新版初始化重用現有產品背景和協作規則，補齊導航與第一項工作入口。
本機文件完成、框架安裝、產品執行、CI、main 整合及 push 是不同狀態；
本次結果見 [0.19.0 本機試用紀錄](workflows/2026-10-04-framework-019-init/results.md)。
