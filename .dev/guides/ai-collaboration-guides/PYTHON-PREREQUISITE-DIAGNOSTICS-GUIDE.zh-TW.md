# Python 前置需求診斷指南

本指南供維護者處理 portable Python CLI 的執行前檢查。它說明如何閱讀診斷與
恢復環境；不會授權工具安裝套件、建立線上資源或發布 release。

## 前置需求與執行方式

支援的 Python CLI 需要 Python `>=3.11`。需要 YAML 的 CLI 使用已釘選的
`PyYAML==6.0.3`；以所在 repository 或 extracted package 根目錄的
`requirements.txt` 為準。

已準備好直譯器時可直接執行 CLI：

```text
python .ai/scripts/validate-ai-context.py --help
```

需要由 shell 尋找可用直譯器時，改用對應 launcher：

```text
sh .ai/scripts/run-python-entrypoint.sh .ai/scripts/validate-ai-context.py --help
pwsh -File .ai/scripts/run-python-entrypoint.ps1 .ai/scripts/validate-ai-context.py --help
```

請只傳入 registry 所列的 CLI 路徑。source-only CLI 不會隨目標 package 發送，
因此不在 extracted target 的 prerequisite 支援範圍；framework release
publication 亦不屬於本指南的執行範圍。

## 讀取 blocked 診斷

預設輸出是 human-readable stderr 訊息。需要機器可讀結果時，在 direct CLI
或 launcher 加上 `--diagnostic-format=json`：

```text
python .ai/scripts/validate-ai-context.py --diagnostic-format=json
sh .ai/scripts/run-python-entrypoint.sh .ai/scripts/validate-ai-context.py --diagnostic-format=json
```

blocked 結果的 `outcome` 是 `blocked-by-environment`。human 與 JSON 都會說明
`reason_code`、Python 下限、已觀察的 candidates、選定的 executable/version、
缺少的 requirements 與 `recovery_command`。這個 recovery command 僅供人員
評估與手動執行；preflight 本身永不安裝 Python 或 PyYAML，也不會變更 target。

恢復後重新執行原始命令並保留其真實結果。blocked、deferred、skipped 與
not-applicable 都不能當作 passed。

## Target-local validation 選擇

checked-in `.dev/project-config.yaml` 的
`validation.routine.local.mode` 預設為 `manual`。只有 target policy 已核准
模式時，才可新增 ignored 的 `.dev/validation.local.conf`；它絕不會被 package
收錄。檔案必須嚴格只有一行：

```text
validation.routine.local=<approved-mode>
```

不得加入註解、空白行或第二個設定。此檔只可把 checked-in selection 強化為
較嚴格的核准模式，不能弱化。它也不是環境變數機制，不能以 environment
variable 覆寫。

CI 選擇維持 `unconfigured`、`advisory`、`required` 三種明確狀態；未選用的
routine 應回報 `not-applicable` 與
`selection_reason: not-run-by-policy`。如需因環境變化重試，僅在有實質狀態
改變後進行一次 preflight/run/retry；不要以重複嘗試把 blocked 轉成成功。
