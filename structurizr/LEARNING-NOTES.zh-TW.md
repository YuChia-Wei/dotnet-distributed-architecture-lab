# Structurizr 試作與團隊應用複習筆記

整理日期：2026-10-14。來源：本次架構圖試作、後續對話，以及 [README](README.md)、[MCP 結果](evidence/mcp-results.json)、[本機檢查](evidence/final-checks.json)。

這份文件保存可傳承的觀察與討論建議，方便複習與接續工作。它是一般學習筆記，不是正式 Lesson record、ADR、團隊已採用規則或完整導入評估。使用者授權保存筆記，不代表下列流程建議已獲團隊採用。來源實作基線為 `4cca0256b96386eae76ea4e73d66cdf7cc2a5847`；這裡沒有重新執行業務測試或重驗最新產品行為。

## 1. 這次真正學到什麼

| 觀察 | 對後續工作的啟示 | 證據／適用限制 |
| --- | --- | --- |
| 同一份 DSL 可以共用元素，產生 Container 與 Dynamic 視圖。 | 系統結構與流程可以一起維護，避免不同圖對服務命名或責任描述不一致。 | [workspace.dsl](workspace.dsl)、[兩張預覽](diagrams.md)。仍需人確認模型語意。 |
| Procurement 沒有獨立 Consumer，收貨 Relay 由 API 託管。 | 依執行／部署責任建模，不把每個 project、class 或背景工作都畫成獨立服務。 | [既有架構文件](../.dev/ARCHITECTURE.md) 與 README 的 host／Compose 證據對照。 |
| 供應商接受採購不會直接增加庫存。 | 圖要表達業務事件的差別，不能只展示技術箭頭。 | 採購接受、實際收貨是兩次操作；GoodsReceived 才驅動 Inventory。 |
| 收貨提交與入庫分屬兩個本地交易，中間有非同步交付。 | 交易邊界、延遲、重送與冪等應成為設計討論重點。 | GoodsReceipt 的 T1/T2；沒有分散式 SQL 交易或全域 exactly-once 保證。 |
| Relay 的 published_at 代表 Wolverine durable-outbox 交接。 | 不拿來源標記當成 Kafka 已送達或下游完成證據。 | 必須另查 transport 與 Inventory ledger／stock；本次只核對來源。 |
| 原 code graph 回報目前 HEAD，卻缺少 Procurement 定義。 | 除了看 revision，還要抽查任務關鍵定義是否存在；不足時更新索引並回讀來源。 | 本次重建 fast index；graph 的空結果不能證明功能不存在。 |
| validate 通過，但 inspect 仍有 ERROR findings。 | 語法可解析、模型品質、業務正確、runtime 驗證應分開報告。 | 最終四項 findings 完整保存在 evidence。 |
| 本機檢視器可以獨立展示模型。 | Demo 不必啟動整套商務系統、AI 或 MCP。 | 使用者啟動後曾確認 HTTP 200；不是完整瀏覽器視覺或產品 E2E 驗收。 |

## 2. Source code + Codebase Memory 足夠嗎？

足夠開始建立第一版，但長期可信的架構文件還需要部署設定、業務語意與負責人確認。

| 資料來源 | 主要用途 | 不宜直接推論 |
| --- | --- | --- |
| Source code | 實際方法、契約、交易、事件、處理邏輯。 | 有程式碼就表示正式環境已啟用。 |
| Codebase Memory | 快速找到候選定義、依賴與呼叫線索。 | 索引一定完整／最新；空結果代表不存在。 |
| Compose／部署／環境設定 | 程序邊界、路由、資料庫、broker、profile。 | depends_on 就表示有業務呼叫；所有環境拓撲相同。 |
| 測試、需求與 ADR | 預期行為、驗收與設計理由。 | 測試存在就表示本次通過；提案已實作。 |
| Runtime／負責人確認 | 實際啟用、跨 repo 外部關係、業務責任與例外。 | 單次 HTTP 200 已證明整條交易正確。 |

可重複使用的步驟：

1. 先問圖要回答什麼工程問題，選取系統／情境與來源 revision。
2. 確認 code graph 新鮮度與相關定義覆蓋，優先透過 MCP 探索。
3. 回讀關鍵 code、設定、測試與現有文件，確認每一條重要關係。
4. 明列「已實作」「僅有設定」「提案」「未知」；未知部分保留問題。
5. 建立少量視圖，共用同一個模型，保留證據入口。
6. validate、inspect、parse，保存原始結果；需要 runtime 結論時另取 runtime 證據。

本次採用 fresh graph 加直接來源核對，仍沒有完整 runtime 驗證。原始碼重建圖的結果應標成來源觀察，不能直接稱為正式環境現況。

### MCP 在這次工作中的角色

MCP 是讓 AI 呼叫外部工具的介面；這次的價值來自兩個 MCP server 提供的具體能力，而非 MCP 本身自動理解或決定架構。

| 工具／角色 | 本次實際工作 | 結論界線 |
| --- | --- | --- |
| Codebase Memory MCP | list_projects、index_status、index_repository 確認／重建索引；search_graph、search_code 尋找定義與程式碼；get_code_snippet 讀片段；trace_path 找呼叫線索。 | 探索加速器。索引可能缺漏，class trace 也可能沒有有效呼叫邊；空結果不代表沒有實作。 |
| 直接來源核對 | 透過本機檔案與 Git，讀取 code、Compose、YARP 設定、測試與既有架構文件。 | 支持模型中的具體關係與行為描述；沒有執行產品 runtime，不能推論正式環境行為已獲驗證。 |
| AI | 整理來源，判斷需要的抽象層級，撰寫元素責任、關係、DSL 與說明，保留不確定事項。 | 判斷必須能回溯證據；不能因工具回傳就自行補出業務事實。 |
| Structurizr MCP | validate 檢查 DSL；inspect 回報模型檢查 findings；parse 產生 workspace JSON；export_mermaid 匯出兩張視圖。 | 驗證與衍生產物工具。parse 成功不代表架構或業務正確，也不代表圖已通過視覺驗收。 |
| 本機 Structurizr Docker 檢視器 | 載入模型、提供圖頁，供使用者展示與討論。 | 檢視器與 MCP server 是不同角色；這次啟動容器的是使用者，本機命令只做後續唯讀確認。 |
| 團隊／系統負責人 | 後續確認業務責任、設計取捨、未知事項及是否採用流程建議。 | 本次保存文件不代表已完成團隊架構審查或規則採用。 |

本次工作的資料流：

```text
Codebase Memory MCP 找線索
  → 直接核對 code／設定／測試／文件
  → AI 整理責任、互動與不確定事項，撰寫 DSL
  → Structurizr MCP 驗證、檢查、解析與匯出
  → 本機檢視器展示，供人討論與確認
```

兩個值得記住的實例：

- Codebase Memory 索引回報 HEAD 相符，卻找不到已存在的 Procurement，因此更新索引並回讀來源；不能把「工具聲稱新鮮」當成完整性保證。
- Structurizr validate 為 OK，inspect 仍回報四項 ERROR，因此同時保存兩種結果；不能把語法通過縮寫成「全部驗證成功」。視圖數量由 parse 陣列計算，不靠人工數箭頭。

MCP 沒有替代既有架構權威或團隊判斷。已保存的 workspace.dsl 可以直接由 Docker 檢視；開圖、demo 與重新整理不需要 AI 或 MCP。若要更新模型，也能改用適當的本機工具，但須記錄實際做過的檢查，不能宣稱未執行的 MCP 驗證成功。

## 3. 三種討論情境，如何選圖

| 想討論的內容 | Structurizr 的適用位置 | 建議搭配 |
| --- | --- | --- |
| UX 操作流程 | 解釋使用者操作背後的系統協作，例如收貨後為何仍等待入庫。 | User flow、wireframe、互動原型，用來討論頁面、導航、回饋、表單與錯誤體驗。 |
| Domain／OOP 互動 | 描述 Container 內重要元件的責任、依賴與協作順序。 | 局部 sequence／class／state diagram，討論方法、物件、條件分支、生命週期與狀態轉移。 |
| 系統容器／服務互動 | Container 表示靜態責任／通訊，Dynamic 表示單一情境的互動順序。 | API／事件契約；環境節點、複本、網路與 failover 用 Deployment 圖補充。 |

兩個容易混淆的名詞：

- C4 Container 是應用或資料儲存的抽象，不等於 Docker container，也不等於每個 csproj。
- C4 Component 是提供一項能力的程式碼組合，不要求每個 class 都成為一個 component。類別方法細節通常用局部 UML／Mermaid 更直接。

以收貨為例，三種視角分別是：

- UX：怎麼輸入 ReceiptId／數量？送出後顯示什麼？如何避免不確定結果下盲目重送？
- Domain：哪個用例呼叫聚合？誰檢查可收狀態與剩餘數量？誰擁有交易提交？
- 系統：Procurement 如何經 Outbox／Kafka 通知 Inventory？重送怎麼不重複加庫存？

建議用同一個 story／情境名稱連結這些視圖，不必強迫一套圖形語法包辦所有問題。

參考：[C4 Container](https://c4model.com/diagrams/container)、[Component](https://c4model.com/diagrams/component)、[Dynamic](https://c4model.com/diagrams/dynamic)、[Code](https://c4model.com/diagrams/code)。

## 4. 在 Agile 開發流程中的位置

本次檢查的 [software-development-orchestrator 方法](../.ai/core/skills/software-development-orchestrator/references/orchestrate.md) 已有架構、情境設計、實作、審查與驗證接點，並允許只選需要的階段；它沒有自動要求每項需求都建立 Structurizr 圖。

| 時機 | 使用方式 | 不必做的額外工作 |
| --- | --- | --- |
| Backlog refinement | 看 Container 基線，找影響服務、資料與外部團隊。 | 每張 story 重畫全系統。 |
| 跨服務設計討論 | 畫單一情境的 Dynamic，討論交易、失敗、重送與責任。 | 為單純欄位或畫面修改增加架構階段。 |
| 技術 spike | 比較 broker、整合或拆分候選方案，標成提案。 | 把未驗證方案合併成現況。 |
| 情境／測試設計 | 用互動步驟找出成功、衝突、部分失敗與回復情境。 | 用圖或假資料替代實際測試。 |
| PR review | 檢查程式與 DSL 是否同時反映責任／互動變更。 | 每個 PR 都修改圖以湊流程。 |
| Onboarding／事故檢討 | 用圖建立共同理解，修正被新證據推翻的關係。 | 把過期圖當成可靠事實。 |

對應現有 skill 的建議分工：

- software-development-orchestrator：判斷這次需要哪些階段與輸出。
- ddd-ca-hex-architect：建立／修改／審查架構視圖與責任邊界。
- bdd-gwt-test-designer：從流程找驗收與失敗情境。
- 實作工作：維持已實作變更與圖一致；產品程式缺陷審查仍由 code-reviewer 處理，架構圖語意審查留在架構技能。
- adr-author：記錄重要選擇、替代方案與原因。
- 一般工具：執行語法檢查、匯出與計數；技能存在不等於曾執行或通過。

可先試兩個 sprint：保留一張 Container 基線；遇到跨服務／交易／非同步疑問再補 Dynamic；在 PR 問「是否影響架構圖？」；回顧圖是否縮短理解、提早暴露問題，以及維護成本是否合理。

上述是本次對話提出的試行建議，尚未修改 AGENTS、skill、CI 或團隊 Definition of Done。若日後採用，應由團隊選定責任與觸發條件。

參考：[敏捷原則](https://agilemanifesto.org/principles.html)、[C4 只選有價值的圖層](https://c4model.com/diagrams)。

## 5. Token 與 credit：本次實測應怎麼看

成本主要來自探索、讀取、核對、推理與反覆處理上下文，不能只按最後 DSL 的字數估算。首次建立基線與後續增量維護應分開量測。

本次 session 在 **2026-10-14 11:42:55（台灣時間）** 的本機 token_count 累計快照如下；數值來自本次對話中的實際讀取，不是本文件建立時重新量測。

| 類型 | Tokens | 當時 GPT-6.1 Sol Standard credits／百萬 tokens | 換算 credits |
| --- | ---: | ---: | ---: |
| 非快取輸入 | 196,871 | 50 | 9.84355 |
| 快取輸入 | 5,699,072 | 2.5 | 14.24768 |
| 輸出 | 23,580 | 250 | 5.89500 |
| 合計 | 5,919,523 | | 29.98623 |

解讀限制：

- 輸入快取比例約 96.66%。輸入總數已包含快取輸入，換算時先扣除，不能重複計費。
- reasoning_output_tokens 為輸出的子集合，本次沒有另加一次。
- 這是多次模型呼叫的上下文累計，不等於有 592 萬個不同內容 tokens。
- 包含架構試作、後續解說及該時間點前的查詢；不能當成「產生兩張圖固定要 30 credits」。
- 不含該快照之後的問答、本筆記或未列入 session 紀錄的外部工具內部 AI 費用。
- 約 30 credits 是按當時公開 Standard 費率換算，不是企業實際扣款。速度模式、方案、內含額度、合約與計費制度會影響結果；不直接換成固定台幣或美元。
- 本筆記未保存個人帳戶餘額、私密對話全文或機器上的完整 session log。

當時參考：[OpenAI 官方計價說明](https://learn.chatgpt.com/docs/pricing)。費率與方案會變，未來估算需重新查核。

控制用量的做法：

1. 保存 DSL、來源 revision、關鍵證據與未知事項，避免每次從頭理解。
2. 優先根據 PR diff 或需求影響範圍增量更新。
3. MCP 搜尋只回傳相關定義／片段；大型 parse JSON 保存為檔案，避免反覆完整輸出給模型。
4. validate、計數、render 能用一般工具完成時，不需要讓 AI 逐項重算。
5. 分別量測首次建圖、日常更新、重大重構，再估算月預算。
6. code graph 有機會減少搜尋成本，但節省幅度需實測；索引是否另耗 embedding／LLM 費用取決於實際實作，不假定免費。

已完成的本機檢視器展示不需要 LLM；查圖與重新整理頁面本身不消耗 AI tokens。

## 6. 驗證與 Demo 的實務提醒

本次 MCP 最終結果是 validate OK、parse 成功、inspect 四項 ERROR 保留，不能簡寫成全部驗證通過。缺少嵌入 documentation／decisions，以及系統外框本身無關係／未作為視圖元素，均已在 [README](README.md) 說明；沒有為消除 finding 複製既有權威文件或新增不需要的視圖。

計數取自 parse 的視圖陣列：

| View | 元素 | 關係實例 | 不同關係 ID |
| --- | ---: | ---: | ---: |
| CoreContainers | 16 | 25 | 25 |
| GoodsReceipt | 8 | 14 | 8 |

Dynamic 可以多次使用同一條模型關係；系統外框不另算元素。不要用 DSL 箭頭行數代替解析後的視圖計數。

Demo 操作以 [README 的換電腦步驟](README.md) 為準，本筆記不複製另一份完整指令：

- 本次使用 structurizr-arch-lab、127.0.0.1:8081，不占用課堂的 8080。
- 正確圖頁為 /workspace/1/diagrams；曾試過 /workspace/diagrams，回應 400，之後從首頁連結確認正確路徑。
- 使用者自行啟動 Local v2026.09.19；當時 running 且首頁／圖頁 200，這是歷史快照，不代表此刻仍在執行。
- 使用 --rm，停止後容器會移除，下次要再 run；掛載模型與 Docker image 保留。
- 根層 workspace.json 與 .structurizr/ 是檢視器工作狀態，已由局部 .gitignore 排除；evidence/workspace.json 是保留的驗證證據。
- latest 可能變動。離線匯出同一份 image 有助重現，但平台相容與離線搬移尚未實測。
- 文件／範例 PowerShell 已做語法與格式檢查，這不能替代 Docker 指令在另一台電腦成功執行。
- 在本次對話時試作檔案尚未 commit；只 clone 遠端不會取得這些新檔。未來接手先查 Git 狀態，不把這項歷史狀態當成永久事實。

## 7. 下次接續時的快速複習

先看 [兩張圖](diagrams.md)，再看 [README 的來源對照與未確認事項](README.md)。開始更新前，依這些問題縮小範圍：

1. 這次要解答 UX、類別互動、服務協作，還是實際部署問題？
2. 是現況重建、候選提案，還是已接受方案的實作更新？
3. 哪些服務、路由、資料所有權、topic 或交易／冪等語意真的改變？
4. 現有來源 revision 與 graph 是否仍適用？哪些證據需要重讀？
5. 是否只需更新一條關係或一個流程，而不是重畫整套？
6. 需要語法驗證、架構語意審查，還是實際 runtime 證據？分開記錄。
7. 圖、衍生匯出、parse 計數、inspection 與來源對照是否同步？
8. 尚未確認的部分是否仍清楚標示？是否把提案誤當成已實作？

後續若要全面導入，仍待試驗的項目包括：團隊維護責任、PR 觸發條件、原生檢視器完整視覺驗收、協作與權限、發布方式、CI 整合，以及真實工作專案的增量更新成本。本次小試作沒有完成這些採用決策。
