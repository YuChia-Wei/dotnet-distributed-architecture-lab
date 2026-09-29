# Python 前置需求診斷指南

本指南供維護者處理 portable Python CLI 的執行前檢查。它說明如何閱讀診斷與
恢復環境；不會授權工具安裝套件、建立線上資源或發布 release。

## 前置需求與執行方式

支援的 Python CLI 需要 Python `>=3.11`。需要 YAML 的 CLI 由保留的 `.ai/scripts/python_prerequisites.py` 檢查相容的 PyYAML；本 target 不提供 source framework 的 requirements mirror。

已準備好直譯器時可直接執行 CLI：

```text
python .ai/scripts/validate-workflow-artifacts.py --help
```

需要先檢查 target-retained entrypoint 的環境時，使用保留的 preflight：

```text
python .ai/scripts/python_prerequisites.py --entrypoint validate-workflow-artifacts.py
```

只有 preflight 成功後，才依 project policy 執行所選 validator；舊 shell/PowerShell launcher 已退役。

請只傳入 `.ai/scripts/python-entrypoints.json` 所列的 target CLI。source-only CLI 不在此 target 的 prerequisite 支援範圍；framework release publication 亦不屬於本指南。

## 讀取 blocked 診斷

預設輸出是 human-readable stderr 訊息。需要機器可讀的 preflight 結果時，對保留的 prerequisite helper 加上 `--diagnostic-format json`：

```text
python .ai/scripts/python_prerequisites.py --entrypoint validate-workflow-artifacts.py --diagnostic-format json
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
