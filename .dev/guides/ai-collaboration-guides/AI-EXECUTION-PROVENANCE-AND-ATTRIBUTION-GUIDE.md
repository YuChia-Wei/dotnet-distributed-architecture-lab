# AI 執行來源與 Git 署名指南

本指南說明如何在不同 AI 工具中取得或推定實際使用的模型與思考深度，
以及何時使用工具原生署名、何時由 repository 產生一致格式的
`Co-Authored-By` trailer。

## Repository 的共同格式

由 repository 工作流程建立的本機 AI commit 使用：

```text
Co-Authored-By: <AI runtime> (<model>, <reasoning_effort>) <noreply@provider-domain>
```

模型與思考深度依序取自：

1. 當次 runtime 或 provider 顯示的有效值；
2. 當次生效的設定預設值；
3. provider 官方文件記載的內建預設值。

使用 fallback 不會阻擋工作，但必須明確標示資料來源，不得宣稱為當次
runtime 已驗證的值。保留 provider 原始名稱，例如 `xhigh`、
`extended thinking` 或其他原值，不跨工具改寫成自訂等級。

只有 sub-agent 實際產生本次 commit 所包含的內容時，才增加另一筆 AI
共同作者；runtime 名稱必須以 `Sub-Agent` 結尾。一般工具呼叫、搜尋或
只提供意見，不構成額外共同作者。

## Codex CLI 與 ChatGPT Desktop 的 Codex 模式

Codex 可在個人 `~/.codex/config.toml` 或受信任專案的 `.codex/config.toml`
設定 `model` 與 `model_reasoning_effort`。執行中以 `/status` 確認工作階段，
需要追查設定來源時使用 `/debug-config`。

目前官方 Codex 文件沒有提供等同 Claude Code `attribution` 或 Copilot CLI
`includeCoAuthoredBy` 的 commit 署名設定。因此，這個 repository 由 Git
commit 政策與提交者產生共同格式 trailer；不能只靠 `AGENTS.md` 保證
Codex client 自動注入署名。

若 Desktop 畫面沒有提供當次模型或思考深度，就使用該 task 生效的 Codex
設定預設值，並將來源記為 `configured-default`。這是 fallback 證據，不是
runtime 回報。

## Claude Code 與 Claude Desktop

Claude Code 的 `~/.claude/settings.json`、專案 `.claude/settings.json` 或
本機 `.claude/settings.local.json` 可設定 `model` 與 `effortLevel`；也能用
`/model`、`/effort` 或啟動參數做當次覆寫。工作階段標頭會顯示目前模型與
effort，可作為當次值的觀察來源。

Claude Code 官方支援 `attribution.commit`，預設 commit trailer 會反映
當次模型，也允許自訂或停用。不過官方文件沒有保證自訂文字能動態插入
當次 effort，因此 provider-native commit 原樣保留；若 repository 自行
建立 commit，才使用共同格式。

Claude Desktop 一般對話不等於 Claude Code 的 Git 提交流程。除非 Desktop
實際透過可驗證的 coding runtime 建立 commit，否則不把它推定為
provider-native commit 署名來源。

## GitHub Copilot CLI、IDE 與 coding agent

Copilot CLI 的使用者設定支援 `model`、`effortLevel` 與
`includeCoAuthoredBy`；repository 的 `.github/copilot/settings.json` 也能
固定這三項。`includeCoAuthoredBy` 預設為 `true`，但官方文件只承諾加入
共同作者 trailer，沒有承諾 trailer 會同時包含有效 effort。

因此 Copilot CLI 原生建立的 commit 保留原樣；repository 自行建立的
commit 才使用共同格式。Copilot IDE chat 與 GitHub coding agent 是不同
執行表面，不應套用 CLI 設定或假設其 Author、Committer、簽章與 trailer
相同。

## 驗證與證據邊界

- 對 repository-created commit，執行 `validate-git-commits.py`。
- 對 provider-native commit，保留原始 Author、Committer、簽章與 trailer；
  不為了統一格式而 amend 或重建 commit。
- 只有實際取得 provider 產生的 commit object，才把該 fixture 標為
  `captured`；官方文件能證明功能存在，但不能取代實際 fixture。
- 設定檔只負責該工具本身，不建立跨 Codex、Claude、Copilot 的自訂共同
  設定檔，也不把工具清單加入 task 或 commit trailer。

## 官方參考

- OpenAI Codex configuration: <https://developers.openai.com/codex/config-basic>
- OpenAI Codex slash commands: <https://developers.openai.com/codex/cli/slash-commands>
- Claude Code settings and attribution: <https://code.claude.com/docs/en/settings>
- Claude Code model and effort: <https://code.claude.com/docs/en/model-config>
- GitHub Copilot CLI configuration: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference>
