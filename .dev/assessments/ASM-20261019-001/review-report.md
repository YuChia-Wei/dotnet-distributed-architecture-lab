# ArchPrecept 套件替換相容性審查

## 審查身分與範圍

- Assessment ID：`ASM-20261019-001`。
- 日期：2026-10-19（Asia/Taipei）。
- Work item：[Issue #32](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/32)。
- 來源：`main` / `origin/main` 的 `7a0bff401bea86428b5c24eab6362ef2170d20d7` 到 `codex/archprecept-package-trial` 的本次工作區差異；初始 127 個路徑的內容 hashes 保存於本機 `artifacts/archprecept-review/initial-subject.json`。修正後 subject 由同工作區的實際 diff 與本機 commit 確定。
- Reviewer：Codex，`gpt-6.1-sol` / `xhigh`；與實作為相同 agent，這是已明確執行的 code review，並非獨立審查。
- 使用專案安裝的 `code-reviewer@0.2.0` common method、目標工程規則與實際 C# / NuGet / Docker 契約證據。該 skill 沒有內建 .NET specialist extension；未宣稱 engine-2 optional knowledge reader 或完整 specialist gate 已通過。
- 範圍含三組契約取代、直接使用端、保留的 EsAggregateRoot、analyzer 傳遞邊界、NuGet 設定、Docker build context 與既有測試。外部 broker/database runtime、非本次變更的既有問題與 release/CI 不在本次通過結論內。
- 審查階段唯讀；以下修正由原套件試用實作授權與後續「review 後 commit」要求下的 slice continuation 完成，不是 reviewer 指令自行授權修改。

## R1 — P2：test-runner 未複製根目錄 NuGet 設定

**位置**：`docker-compose/Dockerfile.tests:3`；新增的根目錄 `NuGet.Config`。

**觸發與影響**：乾淨 Linux test-runner 會 COPY solution、src、samples、tests，卻沒有根目錄 NuGet.Config。產品 src 可讀 src/NuGet.Config，但 tests 與 samples 無法取得 ArchPrecept feed。實際 image build 的 restore 對多個 tests / EF sample 回報 NU1101，僅向 nuget.org 尋找三個 Contracts 套件，無法完成既有容器驗證入口。這是此次套件相依改變後未同步調整的建置相容性問題。

**證據**：`artifacts/archprecept-review/docker-tests-initial.log`，實際 docker build exit 1；不是靜態推測。

**修正**：COPY 清單加入 NuGet.Config，使 root-context tests / samples 與產品共用正確來源設定。修正沒有搬移憑證、改變來源或放寬 source mapping。

**狀態**：已修正並完成重驗。乾淨 Linux image 成功 restore/build，容器預設測試為 155 passed / 0 failed / 46 skipped；原始失敗日誌仍保留。

## 其餘相容性檢查

- 16 份原始契約從 base commit 擷取，在 ignored probe 編譯；與實際還原的發布 DLL 比對 20 個公開型別，包含建構子可見性、方法/參數/預設值、generic constraints、variance、繼承介面與公開/保護成員。扣除刻意的 namespace migration 後 API shape 一致。EsAggregateRoot 明確排除直接替換。
- 58 項 API / 行為 assertion 通過，包括 Result/PageResult/Delivery JSON、nullable Result、實體事件清單/重複移除、ValueObject equality/hash、25 組 messaging profile/config 結果與預設 Publisher overload 僅派送一次。這是一次性的相容性驗證，沒有新增維護用 solution test project。
- Orders repository 的事件型別儲存使用業務事件 `Name` 與原有 event map，JSON 使用實際事件型別；沒有將這次變動的基底介面 assembly-qualified name 寫入資料。業務事件本身的名稱、namespace、assembly、payload 欄位及交易程式不變。
- 保留的 EsAggregateRoot 只更換 AggregateRoot / IDomainEvent 的來源。Replay 由衍生建構子執行、無 pending events；Apply 先 When 再加入 pending；版本確認失敗保留狀態。既有 Orders 測試覆蓋相關行為，沒有直接採用 preview 套件的基底建構子重播。
- PackageReference 版本固定，Contracts 從原 BuildingBlocks project 傳遞；analyzer 僅由 src/Directory.Build.targets 加入且 PrivateAssets=all。沒有加入 suppress，沒有復活退役的 target-local analyzer/runtime-validation 專案。
- 以全域 `github-yuchia` 來源實際還原至新 cache：四個 metadata 的 source 均為 GitHub Packages endpoint，四個 nupkg SHA-256 均與發布紀錄一致；沒有讀出或複製 credential 值。根目錄與 src 的預設來源仍為明確選用的本機 feed。
- 本次是 repository 內所有直接使用端一起重新編譯的 namespace migration，不宣稱對未重編譯的外部 binary consumer 保持 ABI 相容。

## 結論與限制

除 R1 外，檢視範圍內未發現其他有具體證據的相容性缺陷。R1 已修正並重驗，沒有未解決的相容性發現阻擋本次本機 commit。Windows registry 套件 build/tests 與 Linux 本機 feed 的 test-runner build/tests 都已通過，各為 155 passed / 0 failed / 46 skipped。零 DBA 診斷不等於完整架構合規，預設測試 skip 不等於外部服務通過，registry 還原不等於容器 registry 認證或 publication。驗證與本機 commit 狀態見 [workflow results](../../workflows/2026-10-19-archprecept-trial/results.md)。
