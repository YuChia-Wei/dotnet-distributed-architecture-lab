# AI Context Init Skill Guide

本文件說明如何在把這套 AI context framework 複製到既有 repo 或全新空 repo 後，使用 `ai-context-init` 進行 repo init 與架構入口文件同步。

`ai-context-init` 應被視為 template 安裝後第一個使用的 skill。它的責任不是設計產品功能，而是先判斷目標 repo 的真實狀態，清掉或改寫從來源 template 帶過來的過時專案資訊。

安裝套件提供的 root 文件是 target-owned seed，不是來源 repo 現況的複本。先依 target evidence 完成英文 `AGENTS.md`，若需要繁中閱讀版，再以低成本 `context-translator` sub-agent 產生 `AGENTS.zh-TW.md`；不得把預先翻譯但尚未 target-specific 的版本當作公版範本。

## 這個 Skill 可以做什麼

適合用在下列工作：

- 掃描新 repo 的 git 結構與 .NET project structure
- 判斷目標 repo 是空 repo、既有 repo，還是已混入 template 舊資訊的 repo
- 盤點 solution、`*.csproj`、shared libraries、test projects、deploy folders
- 把複製過去後已過時的 root README、`.dev/`、`.ai/`、`AGENTS.md` 架構區塊改成新 repo 版本
- 依 repo evidence 產生或更新 `.dev/project-config.yaml`
- 只有在 repository、release、version、tag、full commit、selection 與 import time 都有可信證據時，才原子建立 `.dev/ai-context/provenance.yaml` 與 `customizations.yaml`；證據不足時不寫入並回報 unresolved
- 區分哪些內容應保留為 reusable collaboration rules，哪些必須改寫成新專案真相

初始化的共同契約見
`.ai/assets/skills/ai-context-governance/references/semantic-customization-lifecycle.md`；
legacy 與 schema-2 provenance 不得同時存在。

## 這個 Skill 不應該做什麼

不應該拿來做：

- 直接替新 repo 補完整業務需求或 spec
- 假裝知道不存在於檔案裡的 bounded context 細節
- 在空 repo 中發明產品名稱、API endpoint、message broker、database、package version 或部署拓撲
- 從來源 template 複製 credentials、connection strings、ports、queue names 或 bounded contexts
- 把 `.ai/` 改成大量記錄專案真相的資料夾
- 大量重寫 `.dev/specs/`、`.dev/operations/` 或 workflow artifacts

## 最適合什麼時候用

建議在下列時機使用：

1. 你剛把這套 AI context framework 複製到另一個 git repo
2. 你剛在空 repo 中加入這套 context
3. 你尚未確認哪些 README / agents / `.dev` 內容是 template 舊資訊
4. 你想先把架構入口文件改正，再開始撰寫 requirement / specs / operations

## Repo Init 模式判斷

先判斷目標 repo 屬於哪一種：

| 模式 | 判斷依據 | 處理方式 |
| --- | --- | --- |
| 空 repo / 近似空 repo | 尚無 solution、src、tests、產品文件 | 保留 collaboration framework，將產品架構標示為尚未初始化，不要補假資料 |
| 既有 repo | 已有 source、tests、package、infra、README 或 docs | 依檔案證據重建 repo-specific truth |
| template copied repo | 已有 `.ai` / `.dev` / agents，但混有來源 repo 名稱、domain、endpoint、service | 保留 framework-level rules，改寫或移除來源 repo 專案真相 |

## Project Config 產生規則

`ai-context-init` 是 `.dev/project-config.yaml` 的產生與同步入口。

它也是目標 repo 第一次原子建立 `.dev/ai-context/provenance.yaml` 與
`.dev/ai-context/customizations.yaml` 的入口，但只有在匯入來源的
published tag、full commit、component selection 與匯入時間都有可信證據時
才可建立。若來源不明，必須回報 unresolved provenance 且不寫入這兩個
authority，不能猜測版本；後續已初始化 repo 的版本升級交給
`ai-context-upgrader`。舊 `.dev/AI-CONTEXT-SOURCE.yaml` 只作為 legacy
reconciliation 輸入，不能與 schema-2 provenance 同時存在。

- canonical shape：`.ai/assets/skills/ai-context-init/templates/project-config.template.yaml`
- 先完成 inventory，再填入有檔案證據或使用者確認的欄位。
- 未知值保持 `null` 或空集合。
- 空 repo 可不建立 project config，或使用 `generationStatus: not-initialized`。
- 不得沿用來源 repo 的 credentials、connection strings、ports、產品名稱、bounded contexts、queue 或 deployment topology。
- 產生後將主要證據路徑記錄在 `evidence.files`。

## 建議模型策略

建議採用兩階段：

1. 先用低成本模型做第一輪 inventory
2. 只有在結構複雜或文件衝突時，才升級到更強模型或 sub-agent

低成本模型適合處理：

- 掃描 repo tree
- 讀取 `*.sln`、`*.csproj`、套件參考
- 盤點 host、library、test project
- 標記哪些文件已經過時

較強模型或 sub-agent 比較適合處理：

- 多 solution 或 mixed-stack repo
- README 與實際專案檔互相衝突
- bounded context 邊界不明
- `AGENTS.md` 或 `.dev/ARCHITECTURE.md` 的高品質重寫

繁中翻譯是另一個獨立的 bounded handoff：英文內容定稿後，指定 source `AGENTS.md`、output `AGENTS.zh-TW.md`，交給 runtime 的低成本 `context-translator`。若該 runtime 無法使用指定的低成本模型，應將翻譯標記為 deferred，不得自行改用主模型完成。

## 升級判斷規則

可直接用這個 gate：

- 沒有 `P0`，且 `P1` 最多只有 1 個: 留在低成本模型
- 任何 1 個 `P0`: 升級
- `P1` 達 2 個以上: 升級
- `P1` 只有 1 個，但你要的不只是同步，而是高品質架構重寫: 升級

### `P0` 代表高風險複雜度

- 多個 solution，而且模組歸屬不清楚
- repo 是 mixed stack，不是單純 .NET 主體
- README / 文件與 `*.csproj`、套件參考、startup project 明顯衝突
- 任務本身要求架構判讀，不只是同步文件
- `.dev/ARCHITECTURE.md` 或 `AGENTS.md` 需要重寫成新的架構敘事

### `P1` 代表中度複雜度

- 有多種 host 類型，例如 API + worker + consumer
- folder 看起來像多模組，但 project 命名無法明確對應
- shared library 很多，但責任邊界不清楚
- deployment 設定分散在多個目錄或多種工具
- test project 和主模組的對應不清楚
- 複製過來的模板文件殘留很多舊名稱，無法直接替換

## 可以怎麼搭配 sub-agent

若第一輪 inventory 已經完成，可以把進階工作拆開：

- 一個 agent 專門整理 tech stack 與 project inventory
- 一個 agent 專門比對文件衝突
- 一個 agent 專門重寫 architecture-facing docs

這樣可以避免強模型把時間花在重複掃描 repo。

## 建議執行模式

實務上可以這樣下：

1. 先要求 low-cost pass 只做 inventory、標記 `P0/P1`
2. 如果沒命中升級條件，就直接同步文件
3. 如果命中升級條件，再把第一輪 inventory 當 source packet 交給強模型或 sub-agent

## Phase 1 固定輸出格式

第一輪最好固定回傳這幾段：

1. `Evidence Used`
2. `Target Repository Mode`
3. `Confirmed Repo Facts`
4. `Project Config Decision`
5. `Copied or Stale Template Facts`
6. `P0 Hits`
7. `P1 Hits`
8. `Complexity Verdict`
9. `Safe Direct Updates`
10. `Escalation Targets`
11. `Source Packet`

這樣第二輪就能直接接手，不用重新理解上下文。

## 哪些內容可直接改，哪些應交棒

通常可直接改：

- index table
- stack version table
- quick-start links
- root README 的 repo identity 與明顯過時資訊
- 根據檔案事實做的簡單架構條列
- 舊 repo 名稱或舊路徑的直接替換

通常應交給強模型或 sub-agent：

- `.dev/ARCHITECTURE.md` 的整段重寫
- `AGENTS.md` 涉及規則重釋的區塊
- 多份文件之間互相牽動的衝突修正
- 多 solution / mixed stack 的架構敘事整理

## Source Packet 至少要包含什麼

如果要交棒，第一輪至少要整理出：

- top-level folders
- solution / project list
- package-reference summary
- host types
- stale-doc conflicts
- 哪些目標檔案需要重寫

## 範本 5：先做升級判斷再決定是否交棒

```text
Use $ai-context-init in two phases.

Phase 1:
- use a low-cost model
- scan the repo tree, solution files, csproj files, and package references
- classify complexity with P0/P1 triggers
- do not rewrite major docs yet

Phase 2:
- only if the escalation gate is hit, hand off the architecture rewrite to a stronger model or sub-agent
- reuse the phase-1 inventory instead of rescanning

Return:
1. confirmed repo facts
2. P0/P1 triggers
3. whether escalation is needed
4. which files can be updated directly now
5. which files should be delegated
6. the source packet for delegation
```

## 它和其他文件的關係

- `ai-context-init` 內建 migration boundary rules，見 `.ai/assets/skills/ai-context-init/references/migration-boundaries.md`
- 先用這個 skill 重建 repo-specific architecture truth
- 完成後才進一步使用 `requirement-author`、`spec-author`、`ddd-ca-hex-architect`

## 怎麼下 Prompt

好的 prompt 至少應包含：

1. 這是剛移植完成或剛加入 AI context framework 的 repo
2. 先判斷是空 repo、既有 repo，或 template copied repo
3. 只更新 README、agents、架構入口與索引文件
4. 以檔案結構、solution、`*.csproj`、套件參考為準
5. 保留 collaboration rules，不要亂改 reusable framework guidance

## 範本 1：剛安裝完模板後做第一次同步

```text
Use $ai-context-init to scan this repository after the template was copied in.

First classify the target repository mode:
- empty or near-empty repo
- existing repo
- copied-template repo with stale source-project facts

Update only the repo-specific entry and architecture sections in:
- README.md
- README.en.md
- AGENTS.md
- .dev/ARCHITECTURE.md
- .dev/project-config.yaml
- .dev/requirement/TECH-STACK-REQUIREMENTS.MD
- .dev/README.MD
- .ai/README.MD
- .ai/INDEX.MD

Use actual repo evidence from the git tree, solution files, csproj files, and package references.
Keep reusable collaboration rules unchanged unless the files clearly prove they no longer apply.
Return confirmed facts, inferred items, and the docs you updated.
```

## 範本 2：只掃描，不立刻改檔

```text
Use $ai-context-init to inventory the current repo structure and tell me which architecture-facing docs should be rewritten before I edit anything.

Focus on:
- top-level folder structure
- dotnet solution and project layout
- runtime hosts, tests, and shared libraries
- copied template docs that look stale

Do not edit files yet.
Return a proposed update plan with confirmed vs inferred facts.
```

## 範本 3：限制只更新 migration boundary 入口文件

```text
Use $ai-context-init, but limit changes to migration boundary guidance and entry docs only:
- AGENTS.md
- .ai/assets/skills/ai-context-init/references/migration-boundaries.md
- .dev/guides/ai-collaboration-guides/AI-CONTEXT-INIT-SKILL-GUIDE.md

Add guidance for how future agents should scan the target repo and refresh architecture truth after template installation.
Do not touch specs or operations docs.
```

## 範本 4：同步完之後準備交棒給其他 Skill

```text
Use $ai-context-init to refresh the copied architecture docs for this repo, then tell me which next skill should run:
- requirement-author
- spec-author
- ddd-ca-hex-architect

Base the recommendation on what is still missing after the repo structure sync.
```

## 典型輸出

你通常應該期待它回傳：

- 掃描了哪些檔案與資料夾
- 確認的 stack / project structure / host types
- 哪些文件已更新
- 哪些資訊仍然是推測
- 下一步應補哪一類文檔
