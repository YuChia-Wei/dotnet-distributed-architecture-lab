# Claude Skills

本目錄放置 repo-local Claude skill 定義本體，以及 skill-local references、agents metadata。

## 目錄用途

- `SKILL.md`
  - skill 的核心定義與使用規則
- `references/`
  - skill 執行時會讀取的補充參考
- `agents/`
  - skill 相關的 agent metadata 或預設 prompt

## Skill Index

- `bdd-gwt-test-designer/`
  - Given-When-Then / BDD / Gherkin 測試設計 skill
- `code-reviewer/`
  - .NET code review、評分與 findings skill
- `ddd-ca-hex-architect/`
  - DDD + Clean Architecture + Hexagonal 架構設計 skill
- `spec-compliance-validator/`
  - spec compliance gate skill
- `staged-refactor-implementer/`
  - stage 級安全重構執行 skill
- `tactical-refactor-implementer/`
  - 局部、物件中心重構 skill

## 與其他目錄的分工

- `.claude/skills/`
  - agent-facing skill definitions
- `.ai/assets/`
  - portable canonical source for skills、sub-agent-role prompts、shared materials
- `.dev/guides/ai-collaboration-guides/`
  - human-facing skill guides、prompt templates、workflow guides
- `.ai/`
  - AI-facing indexes、system overviews、scripts

## Wrapper Direction

- `.claude/skills/` 只放 top-level skills
- use-case sub-agents 的 canonical source 應放在 `.ai/assets/sub-agent-role-prompts/`
- shared/supporting materials 應優先放在 `.ai/assets/shared/` 或 canonical `references/`

