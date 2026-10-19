# ArchPrecept 套件試用

## 目標與授權

- 工作項目：[Issue #32](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/32)。
- 授權：負責人於 2026-10-19 要求將可對應的部分替換成已發布套件進行試用，並明確指定先使用找到的本機版本。
- 分支：`codex/archprecept-package-trial`；base `origin/main` / `7a0bff401bea86428b5c24eab6362ef2170d20d7`，開始時為乾淨的 detached worktree。
- Owning skills：`software-development-orchestrator@0.2.0`、`slice-implementer@0.2.0` 的 `generic` 模式；由本次實作 agent 直接執行。
- 範圍：套件相依、相容型別與直接呼叫端、既有測試與 sample 的引用、產品分析器接線、必要建置設定、試用說明與實際結果。
- 外部 registry 認證由負責人另行研究；此次驗證使用 SHA-256 與發布紀錄相符的四個本機 nupkg。

## 可觀察的完成條件

1. 四個 PackageReference 固定 `0.0.1-preview`，從隔離 NuGet cache 的 metadata 確認實際還原來源。
2. 移除 16 份可由套件替代的契約原始檔；保留本專案的診斷訊息、業務整合事件、runtime adapters 與安全重播實作。
3. Solution Release build 與預設測試執行結果可查；外部服務 skip 另列。
4. 以同一份 analyzer targets 的預期違規 fixture 證明套件載入並回報 DBA1001；不得將 fixture 當產品 runtime 驗收。
5. 清楚記錄套件差異、來源認證限制、Docker 設定修改與實際未執行項目。

## 實作邊界

通用 Domain、Application、Messaging 型別由 ArchPrecept 提供，原有三個 BuildingBlocks 專案保留作為套件相依邊界與 target-owned 擴充位置，避免擴大 solution 和既有 ProjectReference 變更。`EsAggregateRoot` 保留在本專案：其 `Replay` 必須由衍生建構子呼叫，不能使用 preview 套件的基底建構子重播。套件的 `AggregateRoot`、`DomainEntity`、`IDomainEvent` 等仍直接使用。

產品 `src/` 的分析器使用上游預設 severity，不新增 suppress，不恢復已退役的本機 analyzer/runtime-validation 專案。測試與獨立 samples 不直接安裝新分析器，保留其既有分析器設定。

## 來源與規則

直接讀取 `AGENTS.md`、`.dev/TEAM-GIT-FLOW-RULES.MD`、目標工程規則、架構及需求基線；規則 hash 為 `56cf2bd6a21004c969b30c160a089fd060be029861e05f3f40aa94ea8c7ef884`。選擇檔保有 `mq-route-04` / `mq-route-17` 的 generic implementation binding；官方 lock hash 為 `9a01ef6ed16ff34e426f910aaa1c6bebcfff9e06fb0da0da73fbea5a61dc8cf2`。本次直接採用目標規則與實作方法，未執行 engine-2 installed-resource reader，因此不宣稱經該協定驗證的 optional specialist knowledge coverage 或 framework admission。

此替換需保留 AGGREGATE-ES-001、MAP-EVENTS-001、CONTRACT-SEMANTICS-001 的既有行為；沒有改變交易、ORM、broker 或 GWT / mocking 選擇。原始碼探索使用本次 worktree 的 fresh codebase-memory-mcp fast index；code graph 僅用於定位，再讀原始檔核對。該 index 有 18 個排除目錄（包含 samples、scripts 與部分文件），samples 的直接引用以 tracked-file 後備盤點補足；未保存 graph 作為規範證據。

本次不含 push、PR、merge、Issue closure、tag、發布或外部服務啟動。既有 `.ai/`、runtime entries、官方 lock 與歷史 workflow 保持其原有權威。驗證結果及下一步見 `results.md`。


## 已授權 review / commit 續行

2026-10-19 負責人要求先 review 再 commit 至目前試用分支，不 push 或合併；之後提供已設定全域 GitHub Packages 的資訊。本輪依實際全域設定完成四套件 registry restore 與 hashes read-back，保留預設本機 feed。審查保存於 `.dev/assessments/ASM-20261019-001/`，修正唯一 P2 的 test-runner NuGet.Config COPY 缺漏，並完成 Windows / Linux 的 build 與預設測試；具體結果見 results.md。交付為本機 commit，Issue/Project 與 main 不因 commit 自動變更。
