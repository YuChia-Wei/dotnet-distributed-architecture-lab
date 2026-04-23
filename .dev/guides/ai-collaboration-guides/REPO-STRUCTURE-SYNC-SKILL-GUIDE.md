# Repo Structure Sync Skill Guide

本文件說明如何在把這個 AI agent prompts template 複製到新 repo 後，使用 `repo-structure-sync` 快速重建架構文件。

## 這個 Skill 可以做什麼

適合用在下列工作：

- 掃描新 repo 的 git 結構與 .NET project structure
- 盤點 solution、`*.csproj`、shared libraries、test projects、deploy folders
- 把複製過去後已過時的 `.dev/`、`.ai/`、`agents.md` 架構區塊改成新 repo 版本
- 區分哪些內容應保留為 portable collaboration rules，哪些必須改寫成新專案真相

## 這個 Skill 不應該做什麼

不應該拿來做：

- 直接替新 repo 補完整業務需求或 spec
- 假裝知道不存在於檔案裡的 bounded context 細節
- 把 `.ai/` 改成大量記錄專案真相的資料夾
- 大量重寫 `.dev/specs/`、`.dev/operations/` 或 workflow artifacts

## 最適合什麼時候用

建議在下列時機使用：

1. 你剛把這份 template 複製到另一個 git repo
2. 你已經刪掉明顯不適用的舊專案 artifacts
3. 你想先把架構入口文件改正，再開始撰寫 requirement / specs / operations

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
- `agents.md` 或 `.dev/ARCHITECTURE.MD` 的高品質重寫

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
- `.dev/ARCHITECTURE.MD` 或 `agents.md` 需要重寫成新的架構敘事

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
2. `Confirmed Repo Facts`
3. `P0 Hits`
4. `P1 Hits`
5. `Complexity Verdict`
6. `Safe Direct Updates`
7. `Escalation Targets`
8. `Source Packet`

這樣第二輪就能直接接手，不用重新理解上下文。

## 哪些內容可直接改，哪些應交棒

通常可直接改：

- index table
- stack version table
- quick-start links
- 根據檔案事實做的簡單架構條列
- 舊 repo 名稱或舊路徑的直接替換

通常應交給強模型或 sub-agent：

- `.dev/ARCHITECTURE.MD` 的整段重寫
- `agents.md` 涉及規則重釋的區塊
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
Use $repo-structure-sync in two phases.

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

- 先看 `.dev/PORTABLE-PACKAGING-GUIDE.MD`
- 再用 `repo-structure-sync` 重建 repo-specific architecture truth
- 完成後才進一步使用 `requirement-author`、`spec-author`、`ddd-ca-hex-architect`

## 怎麼下 Prompt

好的 prompt 至少應包含：

1. 這是剛移植完成的新 repo
2. 只更新架構入口與索引文件
3. 以檔案結構、solution、`*.csproj`、套件參考為準
4. 保留 collaboration rules，不要亂改 reusable framework guidance

## 範本 1：剛安裝完模板後做第一次同步

```text
Use $repo-structure-sync to scan this repository after the template was copied in.

Update only the repo-specific architecture sections in:
- agents.md
- .dev/ARCHITECTURE.MD
- .dev/requirement/TECH-STACK-REQUIREMENTS.MD
- .dev/README.MD
- .ai/README.MD
- .ai/INDEX.MD

Use actual repo evidence from the git tree, solution files, csproj files, and package references.
Keep portable collaboration rules unchanged unless the files clearly prove they no longer apply.
Return confirmed facts, inferred items, and the docs you updated.
```

## 範本 2：只掃描，不立刻改檔

```text
Use $repo-structure-sync to inventory the current repo structure and tell me which architecture-facing docs should be rewritten before I edit anything.

Focus on:
- top-level folder structure
- dotnet solution and project layout
- runtime hosts, tests, and shared libraries
- copied template docs that look stale

Do not edit files yet.
Return a proposed update plan with confirmed vs inferred facts.
```

## 範本 3：限制只更新 portable migration 入口文件

```text
Use $repo-structure-sync, but limit changes to the migration entry docs only:
- agents.md
- .dev/PORTABLE-PACKAGING-GUIDE.MD
- .dev/PORTABLE-TRANSFER-CHECKLIST.MD

Add guidance for how future agents should scan the target repo and refresh architecture truth after template installation.
Do not touch specs or operations docs.
```

## 範本 4：同步完之後準備交棒給其他 Skill

```text
Use $repo-structure-sync to refresh the copied architecture docs for this repo, then tell me which next skill should run:
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
