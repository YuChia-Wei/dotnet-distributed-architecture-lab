# Codex Runtime Skill Wrapper Plan

## Goal

補上 portable canonical skills 與 Codex runtime skills 之間缺失的 adapter layer，讓 repo 內 skill 能在不複製完整內容的前提下，被 Codex 以原生 skill 方式調用。

## Problem

目前 repo 已有：

- canonical source:
  - `.ai/assets/skills/<skill-id>/skill.yaml`
- human-facing guides:
  - `.dev/guides/ai-collaboration-guides/`

但目前缺少：

- Codex runtime skill wrapper root
- Codex installable skill format
- repo-local runtime wrapper 與 `$CODEX_HOME/skills/` 的同步規則

因此本計畫聚焦在讓 Codex 可直接調用 repo-defined skills，而不是維護額外的 prompt wrapper 層。

## Target Outcome

建立一條清楚的四層鏈：

1. Canonical skill source
2. Human-facing guide
3. Codex runtime skill wrapper
4. Optional local install/sync

## Proposed Structure

```text
.ai/
  assets/
    skills/
      <skill-id>/
        skill.yaml
        references/
        examples/

.dev/
  guides/
    ai-collaboration-guides/
      ...

.codex/
  skills/
    <skill-id>/
      SKILL.md
      references/
      agents/
```

## Layer Responsibilities

### 1. Canonical Source

Location:

- `.ai/assets/skills/<skill-id>/`

Responsibilities:

- 保存單一真相
- 定義 skill purpose、inputs、outputs、constraints、handoff rules
- 保存可跨 agent 共用的 references

Must not:

- 直接使用 Codex-specific runtime metadata 當作 canonical fields

### 2. Human-Facing Guide

Location:

- `.dev/guides/ai-collaboration-guides/`

Responsibilities:

- 解釋 skill 何時用、如何用
- 提供 human prompt template 與 workflow guidance

### 3. Codex Runtime Skill Wrapper

Location:

- `.codex/skills/<skill-id>/SKILL.md`

Responsibilities:

- 提供 Codex 可辨識的 runtime skill entry
- 指向 canonical source 與 human guide
- 僅保留最小 invocation wording 與 runtime-facing instruction glue

Must not:

- 重新複製完整 canonical references
- 成為第二份 skill 真相

### 4. Local Install / Sync

Location candidates:

- `.ai/scripts/`
- `.ai/scripts/export-*`
- `.ai/scripts/sync-*`

Responsibilities:

- 將 repo-local `.codex/skills/` 同步到 `$CODEX_HOME/skills/`
- 或將 `$CODEX_HOME` 指到 repo wrapper root

## Codex Runtime Wrapper Principles

- wrapper 必須薄
- wrapper 必須明確標示 canonical source path
- wrapper 必須標示 human guide path
- wrapper 可保留 Codex runtime 所需的最小 instructions
- wrapper references 優先指回 `.ai/assets/.../references`

## Proposed Pilot

### Pilot Skill

- `ddd-ca-hex-architect`

Reason:

- 已有 canonical skill spec
- 已有 human-facing guide
- 已有 Claude skill wrapper，可作為對照

### Pilot Deliverables

- `.codex/skills/ddd-ca-hex-architect/SKILL.md`
- 如果需要：
  - `.codex/skills/ddd-ca-hex-architect/references/` 中的薄指標檔
- local install/sync guide update

## Implementation Stages

### Stage A

- 定義 `.codex/skills/` root README 與 wrapper conventions
- 定義 Codex runtime skill wrapper template

### Stage B

- 為 `ddd-ca-hex-architect` 建立第一個 Codex runtime skill wrapper
- 驗證 wrapper 是否仍維持 thin-pointer model

### Stage C

- 補 repo-local 使用方式
- 決定是否要同步到 `$CODEX_HOME/skills/`
- 補 export / sync strategy

## Open Questions

- Codex 是否要求 skill references 一律在 skill 目錄內，或可接受 wrapper 明確指向 repo 其他 canonical 路徑。
- `.codex/skills/` 應作為 repo-local runtime wrapper roots，還是直接把 `.codex/` 作為 `$CODEX_HOME`。
- 是否需要額外 template 讓 canonical skill 自動輸出 Codex `SKILL.md`。

## Recommended Decision

1. 以 `.codex/skills/` 專責 Codex runtime skills
2. 將 Codex runtime wrapper 視為 agent-specific adapter，不視為 canonical source
3. 先做單一 pilot skill，不一次遷移所有 skills
