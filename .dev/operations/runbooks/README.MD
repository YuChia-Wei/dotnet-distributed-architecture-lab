# Runbooks

本目錄放置 incident-oriented 的維運處置文件。

來源庫的發布程序是 source-only 治理，不會隨 portable payload 提供。下游發布
流程若需要 runbook，必須依自己的 provider、權限與復原條件另行建立及驗證。

建議一份 runbook 對應一類可識別的問題，例如：

- inventory reservation message failure
- order placed event not consumed
- duplicate stock decrease handling
- dead-letter backlog growth

撰寫格式請遵守 [`RUNBOOK-GUIDE.MD`](../RUNBOOK-GUIDE.MD)。
