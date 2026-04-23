# AI Skill Guide Standards

本文件定義 `.dev/guides/ai-collaboration-guides/` 的通用規範，避免 AI collaboration 文件散落或與 skill 本體重疊。

## 目標

本目錄只處理 human-facing 的內容：

- 某個 skill 可以做什麼
- 什麼情況應該使用它
- 怎麼下 prompt
- 預期會得到什麼輸出
- 它和 repo 其他 AI 資產的關係

不在本目錄存放：

- 給 agent 直接重用的 prompt building blocks
- skill 觸發後才需要讀的內部 references
- scripts、template assets、shared rules 實作細節

## 目錄分工

| 路徑 | 主要讀者 | 用途 |
| :--- | :--- | :--- |
| `.dev/guides/ai-collaboration-guides/` | Human | skill 使用說明、prompt 範本、workflow、採用建議 |
| `.dev/guides/` | Human | 一般開發、架構、框架指南 |
| `.ai/` | Agent | prompts、shared rules、scripts |
| `.ai/assets/skills/` | Agent | canonical skill specs、references、registry |
| `.agents/skills/` / `.claude/skills/` | Agent | thin runtime wrappers、runtime metadata |

## 何時應新增到 `.dev/guides/ai-collaboration-guides/`

符合任一條件就應考慮新增或更新 guide：

- 新增一個可被人直接調用的 skill
- skill 的用途或操作方式對使用者不直觀
- skill 需要多種 prompt 範本來應對不同任務
- skill 已經演進到有明確輸出格式、採用建議、限制條件
- repo 內已有多位使用者或多個 agent 需要共同理解此 skill 的使用方式

## 每份 Guide 建議結構

每份 guide 至少包含以下內容：

1. Skill 名稱與用途
2. 適用情境
3. 不適用情境或邊界
4. Prompt 撰寫方式
5. 2 到 6 個可直接複製的 prompt 範本
6. 預期輸出或回傳格式
7. 與 `.ai/`、`.ai/assets/skills/`、runtime wrappers、`.dev/` 其他文件的關係

## 撰寫原則

- 從使用者角度寫，不從 skill 實作者角度寫。
- 用語要偏操作說明，而不是內部 prompt 組裝細節。
- 範例 prompt 要能直接複製後稍作修改即用。
- 避免把 `.ai/` 內部共享規則整份複製過來。
- 若需要引用內部細節，使用路徑連結，不在 guide 內重複維護完整副本。

## 單一真相規則

- Human-facing 的正式說明以 `.dev/guides/ai-collaboration-guides/` 為主。
- Canonical skill 規則以 `.ai/assets/skills/<skill>/skill.yaml` 與其 references 為主。
- `.agents/skills/<skill>/SKILL.md` 與 `.claude/skills/<skill>/SKILL.md` 只保留薄入口與 runtime metadata。

## 命名建議

- 目錄索引：`README.MD`
- 通用規範：`AI-SKILL-GUIDE-STANDARDS.md`
- 單一 skill 指南：`<SKILL-NAME>-SKILL-GUIDE.md`
- 若有一組成對工作流，可使用：`<TOPIC>-AGENT-PAIR-GUIDE.md`

## 維護流程

1. 新增或調整 skill
2. 決定是否需要新增或更新 human-facing guide
3. 更新 `.dev/guides/ai-collaboration-guides/README.MD`
4. 更新 `.dev/INDEX.md` 或其他必要索引
5. 確認 guide 與 skill 本體沒有雙重真相
