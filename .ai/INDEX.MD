# .ai Index

本文件是 `.ai/` 的 agent-facing 索引。

## Core

- `README.MD`
  - `.ai/` 目錄用途與分工
- `DIRECTORY-RULES.MD`
  - `.ai/` 與 `.dev/` 的放置規則
- `SUB-AGENT-SYSTEM.MD`
  - sub-agent 系統、routing、artifact 讀寫規則
- `CODE-REVIEW-INDEX.MD`
  - code review workflow 入口

## Prompt Assets

- `assets/`
  - canonical source root for portable AI assets
- `prompts/`
  - prompt 資產根目錄
- `prompts/PROMPT-PORTABILITY-RULES.md`
  - prompt 可移植性規則
- `prompts/shared/`
  - shared prompt fragments / reusable rules
- `prompts/examples/`
  - prompt examples

## Script Assets

- `scripts/`
  - validation / review / generation scripts
- `scripts/generated/`
  - generated check scripts
- `scripts/README.md`
  - scripts 使用入口

## Supporting References

- `BUILDING-BLOCKS-CLASS-INDEX.MD`
  - BuildingBlocks 類型索引
- `FAILURE-CASES.MD`
  - 常見錯誤案例
- `COMMON-PITFALLS.MD`
  - 常見陷阱與解法
- `CODE-TEMPLATES.MD`
  - .NET 程式碼模板

## Related Human-Facing Docs

- `../.dev/guides/README.MD`
  - human-facing guides 入口
- `../.dev/guides/ai-collaboration-guides/README.MD`
  - AI collaboration guides 入口
- `../.dev/guides/ai-collaboration-guides/AI-ASSET-LOCATION-STRATEGY.md`
  - 多 agent 情境下的 skill / prompt / guide 收納策略
- `../.claude/skills/README.md`
  - repo-local skill definition 入口
