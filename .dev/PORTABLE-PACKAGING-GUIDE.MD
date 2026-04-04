# Portable Packaging Guide

本文件定義如何把本 repo 的 `.dev/`、`.ai/`、`AGENTS.md` 與相關協作資產移植到既有 legacy 專案。

## 目標

- 讓協作框架可直接複製到其他專案
- 保留可重用的 workflow、guide、skill routing、standards
- 移除或重寫只屬於當前專案的 source of truth

## 可直接保留的內容

- `.ai/`
  - canonical AI assets、scripts、shared rules、sub-agent definitions
- `.dev/guides/`
  - human-facing guides、workflow guides、skill usage guides
- `.dev/standards/`
  - 結構規範、review checklist、組織原則
- `.dev/adr/README.md`
  - ADR 使用規則
- `.dev/workflows/README.MD`
  - workflow artifact contract
- `AGENTS.md`
  - repo-level collaboration baseline

## 必須刪除或重寫的內容

- `.dev/requirement/` 中的專案需求與 bounded context truth
- `.dev/specs/` 中的 domain/use-case/test specs
- `.dev/operations/` 中的 context map、event catalog、mq topology、runbooks
- `.dev/workflows/<workflow-id>/`
  - 已完成 workflow 的 plan、task、review artifacts
- `.dev/adr/ADR-*.md`
  - 若內容描述的是當前專案的既有決策，而非新專案的決策

## 移植流程

1. 複製 `.ai/`、`.dev/`、`AGENTS.md` 與必要 agent wrapper 檔案。
2. 清空或刪除新專案不適用的 project-specific truth。
3. 重新建立新專案的：
   - `.dev/requirement/`
   - `.dev/specs/`
   - `.dev/operations/`
   - `.dev/adr/ADR-*.md`
4. 依新專案技術棧調整 `AGENTS.md` 與 `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`。
5. 若保留 `.ai/scripts/`，應確認腳本檢查目標仍符合新 repo 結構。

具體操作清單見 `PORTABLE-TRANSFER-CHECKLIST.MD`，各子目錄的保留/重寫規則見對應的 `PORTABILITY-NOTES.MD`。

## 判斷原則

- 若文件描述的是「這個框架怎麼協作」，通常可保留。
- 若文件描述的是「這個專案現在長什麼樣」，通常應重寫。
- 若文件同時含有框架規則與專案真相，應拆開，不要把兩者混在同一檔。

## 與 `.ops/` 的關係

- 目前 portable baseline 仍使用 `.dev/operations/`
- 只有當新專案的 ops 治理已經明顯獨立，才考慮升級成根層 `.ops/`

