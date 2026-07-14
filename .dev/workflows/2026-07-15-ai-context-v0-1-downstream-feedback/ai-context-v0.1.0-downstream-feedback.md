# AI Context v0.1.0 下游導入、自檢與實作回饋

## 文件資訊

- 目的：提供 `ai-collaboration-prompts-dotnet-backend` 後續版本規劃與發佈流程改進參考。
- 下游專案：`dotnet-mq-arch-lab`
- 已知安裝版本：source tag `v0.1.0`
- source tag commit：`69c285077708dfb96ee49bb39258aec83eb7f1a9`
- 下游導入起點：`e8e3f85bbcdfc54e832697129e3db1c4edca41d5`
- 評估範圍：從該導入 commit 到本次 repo sync、自檢、remediation、workflow closeout 的實際使用經驗。
- 評估日期：2026-07-15

## 摘要

補上 `v0.1.0` 版本資訊後，先前最重要的判斷需要調整：這不是「來源不明的 framework copy」，而是「可追溯至 v0.1.0 的舊式 raw-overlay 安裝」。因此後續不必猜測基線，可以用 tag commit 與下游 blob 做三方比對、回填 provenance，並設計明確的升級路徑。

但 `v0.1.0` tag 不是安全的可安裝 package。它是事後建立的 source snapshot/provenance anchor；其 tree 比下游當時實際匯入內容多出大量 source workflow records。若照舊版 migration guide 直接複製整棵 framework，會把來源專案的 requirements、backlog、workflows、release history 與其他 source truth 帶入 target，風險甚至高於本次實際導入。

這次下游經驗同時證明 framework 的核心方向是有效的：skill routing、workflow gate、source-of-truth boundary、runtime wrapper、analyzer-backed validation 都能支撐大型修正工作。然而，發佈封裝、版本 provenance、validator 擴充契約、exact-case path validation、workflow metadata semantics 與 commit policy automation 仍應成為下一版的主要投資方向。

## 版本資訊帶來的分析調整

### 原判斷需要修正的部分

1. 不再把 `e8e3f85` 視為 unversioned/forked fixture；它應視為 known-base `v0.1.0` downstream installation fixture。
2. 可以把 `.dev/AI-CONTEXT-SOURCE.yaml` 缺失判定為「v0.1.0 尚未具備 provenance contract 的歷史限制」，而不是下游遺失了當時已存在的必要檔案。
3. 升級策略應從已知 tag/commit 回填 provenance，再由目前 governed upgrader 做三方比對；不需要把 target 當成不可判定的未知 fork。
4. 先前 P1 中的五個 requirements 檔案應重新分類為 distribution/install leak，而不是 source content 本身錯置。它們留在 source repo 合理，出現在 target active requirements 才是問題。

### source tag 與下游導入的關係

在 root entry、`.ai/`、`.dev/`、`.agents/`、`.claude/` 範圍內：

- source `v0.1.0` 有 677 個 blobs；target `e8e3f85` 有 496 個。
- 同路徑且 blob-identical 479 個；同路徑但內容不同 11 個。
- source-only 187 個，主要包含 completed workflows。
- target-only 6 個。

因此 `e8e3f85` 高度源自 `v0.1.0` baseline，但不是 tag whole-tree snapshot。這個差異非常適合作為未來 installer/upgrader 的 regression fixture。

## 這次實際使用中表現良好的設計

### 1. Source-of-truth 邊界有實際價值

`AGENTS.md`、AI context boundary、repo-structure-sync migration boundary 讓 agent 能以 solution、project files、source、tests 與 deployment configuration 為 target truth，而不把 framework 範例當成產品事實。這個方向正確，應繼續強化成可執行驗證。

### 2. Skill ownership 與 routing 能降低跨域混用

repo sync、AI context audit、governance remediation、development implementation、code review 各自有 owner skill。即使本次流程很長，仍能清楚判定哪一類工作不應交給產品開發 skill。這種 ownership 比單純 prompt collection 更可維護。

### 3. Workflow artifacts 對長時間、多階段工作很有幫助

workflow locator、plan、task、report、resume checkpoint 讓中斷後能恢復工作，也讓 commit、merge、push 狀態有可稽核位置。這次被中斷後仍能接續完成，證明 durable workflow record 值得保留。

### 4. Analyzer-backed rules 比文字 grep 更適合 .NET 架構規則

把能形式化的 C# 規則放進 Roslyn analyzer、architecture tests 或 dotnet validation，而把設計推理留在 AI context，這個分工合理。它降低 false confidence，也保留教學與架構比較所需的 reasoning context。

### 5. Thin runtime wrappers 與 canonical asset registry 是正確方向

canonical skill spec 與 runtime wrapper 分離，使 Codex/Claude adapter 可以保持薄層；wrapper parity 與 metadata validation 也確實能抓到同步問題。

## 核心問題與來源專案改進建議

## P0：把 source snapshot、distribution package、installed state 分成三種明確概念

`v0.1.0` 應被明確標示為 historical source snapshot/provenance anchor，而不是可直接 whole-tree copy 的 package。建議 release metadata 增加類似：

```yaml
distribution_kind: source-snapshot-only
installable: false
```

並修改 v0.1 migration guide：

- 不再建議新 target 直接複製 tag tree。
- 新安裝導向第一個 governed package（目前規劃中的 v0.3+）。
- 若必須重建 v0.1 baseline，只能使用 allowlist/reconciliation，不能 raw overlay。
- 明列 source requirements、backlog items/index、workflows、assessments、releases 與 root truth 的 exclusions。

v0.2 guide 也應補充相同警告。它雖然已要求 inventory target truth，仍應明示 v0.2 不是具完整 package/provenance contract 的 whole-tree installable artifact。

## P0：完成 governed distribution builder 與 payload validation

目前規劃中的 v0.3 allowlist/profile 方向正確，尤其是：

- `.dev/requirement/*` 預設排除，只允許 `REQUIREMENT-GUIDE.MD`。
- 排除 source backlog items/index、workflow/assessment instances、releases 與 source root truth。
- 以 target-template seeds 產生 root entries。
- 以 ownership + SHA256 管理 replace/remove，提供 dry-run 與 deterministic build。
- 寫入 target provenance。

發佈前仍建議新增 payload-level gate：framework-managed payload 不得引用 profile 已排除的 source lifecycle path。`.ai/scripts/README.md` 中指向 `2026-05-dotnet-script-to-analyzer-transition` 的四個斷鏈就是適合的 regression fixture。

## P0：定義 validator 的擴充契約與 fail-closed 聚合契約

這次 tools/analyzer 整合顯示，新增一個 validator 不只需要新增 executable，還要同步：

- registry/manifest；
- aggregate runner 的 enforcement class；
- required-count/parity fixture；
- README 與執行命令；
- CI/local gate；
- negative tests。

目前其中一個 fail-closed fixture 仍把 required command count 寫死為 2，而 runner 已有 3 個 dotnet required commands。修正前完整 suite 為 30/31；加入本次五個 exact-case tests 後為 35/36，唯一失敗仍是同一個既存 fixture。建議把 required commands 由單一 machine-readable registry 產生，測試驗證集合與分類，不驗證容易漂移的固定數字。

## P0：把 commit policy 變成可執行 gate

本次曾出現 workflow 已完成但沒有 commit，以及 AI-authored commit 格式不符合 repo policy 的情況。這表示 commit policy 只存在文件內仍不足。建議：

- 提供 `prepare-commit-msg`/CI lint 或 repository tool。
- workflow-stage commit 驗證 `Why`、`What`、`Validation`、`Workflow` sections。
- 驗證 subject pattern 與 AI co-author trailer。
- workflow closeout 在 commit verification 未通過前不可標 completed。

## P1：移除 source lifecycle requirements 的安裝漏網之魚

以下五個 target 檔案與 source `v0.1.0` blob-identical，內容描述的是來源 framework 自身的治理、validator/skill migration lifecycle，不是 `dotnet-mq-arch-lab` 的 active requirements：

- `.dev/requirement/DOMAIN-UBIQUITOUS-LANGUAGE-REQUIREMENTS.MD`
- `.dev/requirement/DOTNET-VALIDATOR-PHASE-2-REQUIREMENTS.MD`
- `.dev/requirement/DOTNET-VALIDATOR-PHASE-3-REQUIREMENTS.MD`
- `.dev/requirement/HISTORICAL-CONTEXT-NORMALIZATION-REQUIREMENTS.MD`
- `.dev/requirement/SKILL-IMPLEMENTER-NAMING-REQUIREMENTS.MD`

正確分類是 distribution/install leak：檔案留在 source 合理，但必須被 package profile 排除。相對地：

- `REQUIREMENT-GUIDE.MD` 是可重用 authoring contract，應保留。
- `TECH-STACK-REQUIREMENTS.MD` 應由 target 重建或 reconcile，不應由 source 覆蓋。
- target-specific product requirement 應永久保持 target-owned。

## P1：補 target-truth 與 exact-case validation

Git 實際追蹤 `.dev/ARCHITECTURE.md`，但 active context 曾有 20 個 `.dev/ARCHITECTURE.MD` references，分布於 canonical skill references、guides、standards、template 與 target requirement。Windows `Path.exists()` 不分大小寫，因此既有 validator 全部通過。

validator 應以 `git ls-files` 的原始 path 建立 exact set 與 `casefold -> canonical` map，再檢查 active Markdown/backtick/link references：

- exact match：通過；
- casefold match 但字面不同：回報 exact-case mismatch；
- 完全不存在：依 reference 類型回報 missing path；
- 排除 workflow history、archive、examples、generated、URL、glob 與 placeholder。

同一個 defect 同時存在 source reusable assets 與 target-only requirement，因此修正應回饋 source，並在 target 立即修補。

## P1：讓 workflow metadata 表達真實狀態，而非只滿足 schema

建議強化：

- `status`、`current_phase`、task finding status 之間的 state transition validation。
- `updated_at` 必須隨內容變更更新，並能檢查不合理倒退。
- post-audit finding reconciliation 與 closure decision 必須可追溯。
- checkpoint merge/push 與 continuation branch 必須明確記錄。
- no-commit handoff 應維持 `in_progress`，不能因檔案修完就假設 workflow completed。

## P1：建立 codebase knowledge graph freshness contract

本次 codebase-memory MCP 能快速定位 validator functions 與呼叫關係，對大型 repo 很有價值；但 graph 可能落後於 working tree。建議：

- index artifact 記錄 source commit、dirty-state fingerprint、建立時間與 indexing mode。
- query 回應顯示 freshness/staleness。
- material edits 後提供 bounded incremental re-index。
- validation/review 工作若 graph commit 與 checkout 不符，必須提示 agent 以 file-backed truth 驗證。

## P2：改善文件索引與 generated inventory 的 drift 訊號

README 應解釋 purpose/scope/usage，INDEX 擁有 catalog；generated inventory 應標示生成來源、時間與不可覆蓋 primary evidence 的規則。這些原則目前已逐步形成，建議在 source template 與 validators 中一致化。

## 建議的來源專案 roadmap

### 第一優先：v0.3 發佈安全

1. 完成 deterministic distribution builder、manifest、ownership hashes 與 provenance。
2. 修正 package 內任何指向 excluded source lifecycle paths 的 reference。
3. 加入 payload allowlist/exclusion/reference-integrity tests。
4. 將 v0.1/v0.2 標為 historical source snapshots，不再建議 whole-tree install。

### 第二優先：下游升級與 reconciliation

1. 使用 v0.1 tag commit 作 known base。
2. 支援 target local modifications 的三方比對。
3. hash-matched remove 僅移除未被 target 修改的 legacy framework files。
4. 對 source lifecycle requirements/backlog/workflows 提供明確清理計畫。
5. 產生 dry-run report，區分 replace、preserve、remove、conflict、manual review。

### 第三優先：governance automation

1. exact-case internal reference validation。
2. validator registry 與 fail-closed runner parity。
3. workflow semantic state machine/timestamp validation。
4. commit-message/trailer lint 與 closeout gate。
5. knowledge graph freshness metadata。

## 建議納入的 regression fixtures

1. `base = v0.1.0`, `target = e8e3f85-style installation`。
2. 驗證五個 source lifecycle requirements 永不進入 package/target active requirements。
3. 驗證九個 source backlog items、source backlog index、completed workflows、assessments、releases 永不進 payload。
4. 驗證 `REQUIREMENT-GUIDE.MD` 與 backlog governance README 可保留。
5. 驗證 `TECH-STACK-REQUIREMENTS.MD` 被分類為 target-owned/reconcile。
6. 驗證 package 內不存在指向 excluded paths 的 backlinks。
7. 在 Windows/core.ignorecase=true 情境驗證 `.dev/ARCHITECTURE.MD` 對 `.dev/ARCHITECTURE.md` 仍 fail closed。
8. 驗證 dirty target 與 hash mismatch 時 installer 不覆蓋、不刪除並輸出 conflict。

## 本次下游 remediation

本次已在未 commit 狀態完成：

- 移除五個 source lifecycle requirement leaks。
- 移除 `.ai/scripts/README.md` 的 source workflow 斷鏈。
- 修正 20 個 active `.dev/ARCHITECTURE.MD` references 為 Git exact case `.dev/ARCHITECTURE.md`。
- 新 validator 首次執行後另外找出並修正 11 個 requirement/spec guide exact-case mismatches。
- 為 `validate-ai-context.py` 增加 exact-case reference gate 與 regression tests。

## Git phantom diff 說明

曾出現四個檔案在 `git status` 顯示 modified，但 GUI 與各種 diff 都沒有內容。逐一比較 working-tree `git hash-object`、index blob 與 HEAD blob，三者完全相同；`git diff --raw`、`--numstat`、`--word-diff` 也都是空的。這不是內容變更，而是 Windows/CRLF/mtime 造成的 index stat cache drift。

對相同 blobs 執行 `git add` 只刷新 index cache，沒有建立 staged content diff，之後 status 恢復 clean。這比重寫檔案或 checkout 更保守，且沒有動到使用者內容。

## 結論

`v0.1.0` 資訊讓這次案例從「難以判定的舊 copy」升級為可重現、可做三方比對的 migration fixture，這是重要利多。同時，它也明確揭露 source snapshot 與 installable distribution 不能混為一談。

來源專案下一版最值得優先完成的不是再增加更多 context 文件，而是把已經形成的 governance principles落成可驗證的 package、provenance、upgrade、exact-case、workflow semantics 與 commit gates。這會直接降低下游 sync 成本，也會讓 AI agent 在長流程工作中更少依賴人工提醒。
