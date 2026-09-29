# Software Development Orchestrator Skill Guide

本指南說明本 target 已選定的 `software-development-orchestrator`。現行能力以 [SKILL.md](../../../.ai/core/skills/software-development-orchestrator/SKILL.md) 與其 references 為準；workflow locator、handoff、Git 與 validation 仍由本 repo 的 `.dev/standards/` 政策及 `.dev/project-config.yaml` 決定。

這個 skill 保存一項已授權工作可續作的 workflow record：任務與依賴、實際進度、決策、具歸屬的證據及下一個動作。小型專業工作可以直接進行，不必為了啟用 specialist skill 建立 workflow。它不替代 requirement、spec、architecture、test、implementation 或 review 的專業判斷，也不從既存紀錄推導新的授權。

## 現行操作

已選定的 package 提供十種操作：`explain`、`create`、`inspect`、`query`、`checkpoint`、`transition`、`resume`、`retrospect`、`render`、`retention-preview`。CLI 位於已安裝 package 的 `scripts/workflow.py`，以 `--request` 接收絕對 JSON 檔案路徑或 `-` 標準輸入。請先讀 [configuration](../../../.ai/core/skills/software-development-orchestrator/references/configuration.md) 和 [operations](../../../.ai/core/skills/software-development-orchestrator/references/operations.md)，提供明確的 project/package roots，並使用 project 選定的 store binding。CLI 的存在不表示本機執行條件已滿足；缺少 runtime 時應回報 unavailable。

`create` 從明確輸入建立最小 record；`checkpoint` 記錄實際進度與證據；`resume` 從已保存的 record 和 store binding 繼續。請讀回真正的 ID、digest、state 與依賴，不能憑範例編造 `expected_sha256`、執行結果或 approval。`retrospect` 可記錄「沒有新知識」；有候選知識時只是 handoff candidate，不會自行呼叫其他 skill。`retention-preview` 只預覽，沒有排程、封存、刪除或重寫 history 的 writer。

[workflow template](../../../.ai/core/skills/software-development-orchestrator/templates/workflow.md)、[record schema](../../../.ai/core/skills/software-development-orchestrator/schemas/workflow-record.schema.json) 和 [inert example](../../../.ai/core/skills/software-development-orchestrator/references/example.md) 說明這個 selected package 的格式；範例不是本 target 已執行的證據。Project-owned 的 [workflow locator template](../../standards/templates/workflow-locator-template.yaml) 和 [handoff checkpoint template](../../standards/templates/workflow-handoff-checkpoint-template.yaml) 適用於 repo policy 要求的 durable artifacts。

## 與 MQ 專案政策的邊界

當任務需要本 repo 的 workflow 紀錄，依 [workflow gate](../../standards/WORKFLOW-GATE-POLICY.md)、[artifact policy](../../standards/WORKFLOW-ARTIFACT-POLICY.md)、[handoff policy](../../standards/WORKFLOW-HANDOFF-POLICY.md) 與 [commit policy](../../standards/GIT-COMMIT-POLICY.md) 判斷。CLI 的 `explain` 僅解析設定，不能證明授權或能力；舊版 development task JSON、review report template 與 fallback routing 不是 RC2 selected skill 的現行介面。Target framework gate 仍依 `.dev/project-config.yaml#validation.current_framework.local` 的實際配置決定，不能由 workflow record 或本指南宣稱通過。
