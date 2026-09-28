# Operations Docs

本目錄存放 operations 文件的作者指南、模板約定與本 repository 的實際操作文件。

作者指南不能取代 runtime truth；目前可讀的實際文件包括 `context-map.md`、`event-catalog.md`、`mq-topology.md`、`procurement-supplier-lab.md` 與 `commerce-frontend.md`。使用前仍須將內容對回 `requirement`、`specs`、`src`、contract source 與 Compose 設定。

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

- 只在專案需要具體 operations 文件時參考這裡
- 先寫成 repo-specific 文件，再補齊實際 truth
- 不要把這裡當成部署手冊或 production on-call 平台說明
