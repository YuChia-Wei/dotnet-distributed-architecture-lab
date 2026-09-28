# 文件交付驗收與覆核

建立／更新：2026-09-28T23:32:07+08:00。Workflow：`2026-09-28-external-api-team-guide`；[Issue #20](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/20)。

本報告覆核文件成品；基準為 `f2bb5750fb01b4508cdae8328becc6581212a4ab` 的程式與部署設定。三個製作工作由 GPT-6 Sol / high 執行，各自使用獨立 worktree；整合與覆核由目前 session 的 GPT-6 Astra / ultra 執行。模型名稱是實際執行歸屬，並非效能或成本評比。

## 交付與驗收

| 條件 | 文件凍結時結果 | 證據 |
| --- | --- | --- |
| AC01 簡報 | 通過 | [17 頁可編輯 PPTX、PDF 閱讀版與講者筆記](../../presentations/external-api-testing/README.md)；原生文字／圖形及 17 份投影片備註 |
| AC02 圖解 | 通過 | [架構與 7 張時序圖](../../guides/external-api-testing/diagrams/README.md)，共 8 張；每張提供 Mermaid、SVG、PNG 與離線圖庫 |
| AC03 文件補漏 | 通過 | README 雙語、架構、41 個專案清單、context map、event catalog、MQ topology、操作入口與規格索引；[目前系統擴充邊界](../../specs/current-system-extension.md) 明示舊 reconstruction 範圍 |
| AC04 文件檢查 | 通過（限定本次文件） | [產物檢查摘要與 SHA-256](artifact-validation.json)；逐頁渲染與人工檢視、來源／路徑／清單核對 |
| AC05 遠端交付與清理 | 文件凍結時待執行 | 已獲授權的 PR、merge、Issue close、branch/worktree cleanup 由 root 接續執行；實際結果以 Issue 關聯 PR、GitHub 狀態及當次終端讀回為準，不預寫成功 |

工作狀態 `completed` 表示 T001–T003 的文件製作與覆核已完成；不把尚未發生的 GitHub 整合或清理當成完成證據。GitHub delivery 仍屬同一 workflow 的授權交付步驟，無新需求或交接流程。

## 已執行的檢查

- 8 張 Mermaid 使用 11.12.0 與 headless Edge 渲染成功；圖庫檔案存在、Mermaid 區塊與 MMD 一致、SVG SHA-256 符合 manifest。
- 17 張投影片由 artifact-tool 渲染，PowerPoint ZIP／原生投影片結構與版面檢查各 0 finding；最終 PPTX hash 與 finalizer 收據一致。PDF 為同組渲染圖的 17 頁閱讀副本；PDF 文字是影像，搜尋與修改請使用 PPTX 或 Markdown 筆記。
- Root 已逐頁檢視簡報，並覆核架構與重要時序圖。沒有使用桌面 PowerPoint／LibreOffice 執行驗證，因此不宣稱原生 Office 字型或動畫相容性已驗收。
- 文件檢查涵蓋相對檔案連結（不包含網頁／Markdown anchor 可用性）、YAML、solution inventory 與本次 locator。清單與 `MQArchLab.slnx` 的 41 個 project 完全一致：27 個 src、5 個 samples、9 個 tests。
- 本次未修改 `src/`、`samples/`、`tests/`、部署設定、套件、`.ai/`、`.agents/`、`.claude/`、`.dev/ai-context/` 或 AGENTS；未啟停 Docker、清除資料或影響 observability。因是文件交付，未重跑產品 .NET、npm 或外部整合測試。

## 覆核後已修正

- 明確區分瀏覽器執行 Vue API 呼叫、Nginx 提供靜態檔案；控制面回應經自製 facade 回到管理後台。
- WireMock 自製控制頁與原生 Admin API 分開說明；Microcks fallback 限於匯入的已知 operation，不宣稱未知路徑有全域 proxy。
- 固定 POST 範例要匹配完整身分與內容；報價 GET 沒有 clientRequestId，展示需隔離操作並核對 SKU、origin 與原始請求，不能只用計數歸因。
- 提交未知結果保留原 provider／key；收貨 source outbox 的 `published_at` 表示持久化交接至 Wolverine，不能等同 Kafka 已消費。銷售庫存保留另走訊息 request/reply。
- 簡報時序圖補上方向箭頭，業務回應與事後日誌查詢分開；統一展示筆記的完整 YARP 路徑。

## 未通過與保留的限制

1. `python -B .ai/scripts/validate-workflow-artifacts.py` 仍以 exit 1 結束：既有採購／前端 locator 共用 `.dev/workflows-v2`，且該舊驗證器以 locator 資料夾拼 entrypoint，未依兩者宣告的外置 artifact_root 判讀 index。已修正前端 locator 缺少的 template metadata 和缺漏索引；保留能實際開啟的連結、舊 v2 記錄與證據，沒有為迎合驗證器改成不存在的路徑。本次 locator 的欄位與入口另經限定檢查通過。
2. `validate-current-framework.py --binding-sha256 <actual binding hash> --git-range <base>..HEAD` 的觀察結果仍是 exit 1：保留規則、managed member/discovery/resolution 檢查通過，但其 Git 呼叫硬綁 pilot workflow ID，與本次文件 workflow 不符；獨立 admission 仍未成立。依使用者明確同意的單一文件交付例外繼續，Issue #15 與 framework gate 完全保留。此結果不能寫成框架驗收通過。
3. 正確 workflow ID 的 target Git commit policy 會對提交後實際範圍另外執行，記錄於 PR／交付讀回；不以 package check 代替 target overlay，也不把 commit/push 當成服務驗收。

## 授權交付步驟

將同一文件分支推送、建立包含上述限制的 PR，以 merge commit 保留本次可整體回復的交付單位；讀回 PR 與 origin/main 後關閉 Issue #20、同步本機 main。保存需要的忽略檔 QA 收據後，封存本次四個 managed worktree，再刪除任務分支。Docker compose 與既有資料維持原狀。
