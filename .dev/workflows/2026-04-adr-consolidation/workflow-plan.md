# ADR Consolidation Refactor Plan

## Workflow ID

`2026-04-adr-consolidation`

## Problem

`.dev/adr/` 內目前同時包含：

- 仍然有效且尚未被其他 canonical 文件完全承接的 architecture decisions
- 已經被 `.dev/standards/`、`.dev/specs/`、`.dev/guides/`、`.ai/` 吸收的規則
- 偏歷史事件、單一功能、或 prompt-first 時代遺留的 ADR

若不整理，會造成：

- ADR index 過度膨脹
- 使用者無法快速知道哪些 ADR 仍是 active source of truth
- 同一規則同時存在於 ADR 與 standards，增加維護成本

## Goal

- 盤點哪些 ADR 已落地為正式 standard / guide / architecture file
- 將 ADR 分成 active、landed, historical / superseded 等狀態
- 為仍然缺少 canonical 承接文件的 active ADR 補正式落點
- 清理已明顯過時或被新流程取代的 ADR

## Stage Plan

### Stage 1: Inventory and Consolidation Assessment

- 盤點 `.dev/adr/` 現況
- 建立 first-pass consolidation report
- 分類為：
  - landed in standards
  - partially landed
  - historical / project-specific

### Stage 2: Workflow Trigger Clarification

- 檢查 AI collaboration docs 是否明確說明 workflow mode 觸發條件
- 若不足，補上可操作的 trigger checklist

### Stage 3: ADR Index Status Model

- 更新 `INDEX.md`
- 為 ADR 增加可追蹤的狀態語意
- 明確標示哪些 ADR 已被正式文件承接

### Stage 4: Canonical Standard Backfill

- 補仍缺正式承接文件的 ADR 主題
- 優先處理：
  - reactor interface rule
  - mapper serialization rule
  - 其他仍 active 但尚未 canonicalized 的規則

### Stage 5: Historical ADR Cleanup

- 清理或標記被取代、過時、或單一功能專案特例的 ADR
- 必要時更新 `README.md` / `INDEX.md`

## Current First-Pass Evidence

- `.dev/adr/ADR-CONSOLIDATION-FIRST-PASS.MD`

## Success Criteria

- 使用者可快速看出哪些 ADR 仍然 active
- 已落地的規則不再需要靠 ADR 當主要入口
- workflow trigger conditions 有明確文字規則可依循
- `.dev/adr/` 的內容更接近「有效決策紀錄」而不是歷史堆積
