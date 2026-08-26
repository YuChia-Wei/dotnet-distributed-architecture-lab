# AI Collaboration Guides

本目錄放置「給人看的」AI collaboration、skill、prompt 與 AI agent 協作使用指南。

## 目的

- 說明某個 skill 或 collaboration workflow 可以做什麼
- 提供可直接複製的 prompt 範本
- 說明何時該用 skill、何時該看 `.ai/` prompt 元件
- 讓人類使用者理解 repo 內的 AI 協作方式

## 與其他目錄的分工

- `.dev/guides/ai-collaboration-guides/`: 給人看的 AI collaboration guides、workflow、prompt 與操作指南
- `.dev/workflows/`: 跨 skill workflow artifacts 的正式存放位置
- `.dev/guides/`: 一般軟體開發、架構、框架、專案使用指南
- `.ai/`: 給 agent 重用的 prompt 元件、shared rules、scripts
- `.ai/assets/skills/`: canonical skill specs 與完整 skill registry
- `.agents/skills/` / `.claude/skills/`: thin runtime wrappers

## 導航

文件目錄由 [INDEX.MD](INDEX.MD) 維護。

## Workflow Templates

- `AI-REFACTORING-SKILL-CONTRACTS.md`
- Workflow templates are owned by the canonical skill that creates that workflow kind.
- Shared discovery and metadata rules are defined by `../../standards/WORKFLOW-ARTIFACT-POLICY.md`.
- Development templates are under `.ai/assets/skills/software-development-orchestrator/templates/`.
- AI context maintenance and audit templates are under their respective canonical skill directories.

## Feature And Use Case Requests

The retired legacy standards prompt examples are not prompt sources. Use the
current capability routes instead:

- multi-stage product work: `software-development-orchestrator`;
- bounded-context, Aggregate, port, or use-case design:
  `ddd-ca-hex-architect`;
- one accepted command/query/reactor/documentation slice:
  `slice-implementer`;
- one local symbol or call-site change: `local-change-implementer`;
- requirement or spec drafting: `requirement-author` or `spec-author`.

The corresponding guides in this directory provide copyable invocation
examples. Canonical execution rules remain under `.ai/assets/skills/`.

## 維護規則

- 新增 human-facing 的 AI skill 使用說明時，優先放在本目錄。
- 每個 skill 至少應有一份對應 guide，說明用途、適用情境、prompt 範本與輸出期待。
- 本目錄的文件是給人讀的，不應複製大量 `.ai/` prompt 內部細節。
- canonical skill 規則仍以 `.ai/assets/skills/<skill>/skill.yaml` 與其 references 為準；wrapper 只保留薄入口。
- 若 guide 內容與 canonical skill spec 衝突，應同步修正並避免形成雙重真相。


