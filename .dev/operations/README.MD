# Operations Docs

本目錄存放 operations 文件的作者指南與模板約定。

這裡的內容不宣稱任何現成的 runtime truth 檔案已存在。當專案真的需要 context map、event catalog、MQ topology 或 runbook 時，先依這些指南建立對應文件，再把內容對回 `requirement`、`specs`、`src` 或 contract source。

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
