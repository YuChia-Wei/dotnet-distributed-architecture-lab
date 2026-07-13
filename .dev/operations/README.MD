# Operations Docs

本目錄同時存放 operations 文件的作者指南，以及經目前 `src/BC-Contracts/`、Wolverine configuration 與 Docker Compose 驗證的 target-repository runtime 文件。

## Purpose

- 協助撰寫 repo-specific 的 distributed system operations 文件
- 讓作者知道每一類文件需要哪些欄位、邊界與驗證點
- 提供 template-level 的最小章節結構

## Scope

- bounded context 關係與責任劃分
- integration event ownership 與 versioning
- MQ / broker / route / retry / DLQ 規則
- incident runbook 與復原驗證步驟

## Usage

- 使用 `context-map.md`、`event-catalog.md` 與 `mq-topology.md` 理解目前已確認的 runtime relationships。
- 使用 `runbooks/inventory-reservation-failure.md` 處理 Orders-to-Inventory request/reply failure path。
- 撰寫或更新 repo-specific 文件時，必須對回 `requirement`、`specs`、`src`、contracts 與 deployment evidence。
- 這些文件描述目前 lab topology，不代表已完成 production hardening；retry、DLQ、replay 與 idempotency 的缺口仍需明確保留。
