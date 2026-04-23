# Portable Transfer Checklist

把本 repo 的協作框架移植到其他專案前，請逐項確認：

## 保留

- 保留 `.ai/`
- 保留 `.dev/guides/`
- 保留 `.dev/standards/`
- 保留 `.dev/adr/` 的治理文件（template / index / 建立時機）
- 保留 `.dev/workflows/README.MD`
- 保留 `AGENTS.md`

## 重新建立或重寫

- 重寫 `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`
- 重寫 `.dev/ARCHITECTURE.MD`
- 重寫 `.dev/project-config.yaml`
- 重寫 `.dev/specs/domains/`
- 重寫 `.dev/specs/tests/`
- 重寫 `.dev/operations/context-map.md`
- 重寫 `.dev/operations/event-catalog.md`
- 重寫 `.dev/operations/mq-topology.md`
- 重寫 `.dev/operations/runbooks/`
- 重寫或刪除 `.dev/adr/` 下的舊決策紀錄

## 清理

- 刪除 `.dev/workflows/<workflow-id>/` 下已完成 workflow artifacts
- 刪除與原專案 bounded context、事件名稱、隊列名稱、服務名稱直接綁定的文件
- 刪除不再符合新專案 stack 的 script wrapper 或檢查規則

## 驗證

- 執行 `repo-structure-sync` 或等效流程，確認架構入口文件已依新 repo 結構同步
- 確認 `AGENTS.md` 的 stack rules 與新專案一致
- 確認 `.ai/scripts/README.md` 中列出的腳本仍適用
- 確認 `.dev/specs/` 與 `.dev/operations/` 沒有殘留原專案名稱
- 確認 `.dev/adr/` 不再是新專案的主規則入口
