# Requirement Designer Prompt Guide

本文件說明如何用 prompt 讓 AI 協助整理 requirement 文件。

目前它不是正式 skill，而是 human-facing prompt guide，目標是讓你能快速把模糊想法整理成符合 `.dev/requirement/` 規範的 markdown 文件。

## 適合用在什麼情況

- 需求還是討論稿
- 只有零散筆記、會議結論、口頭想法
- 需要先整理出 functional / non-functional requirements
- 需要補齊 acceptance criteria、constraints、business rules

## 不適合用在什麼情況

- 已經進入 use case / adapter / entity JSON spec 階段
- 問題其實是 aggregate / bounded context 邊界不清
- 你要直接產生程式碼或測試碼

## 參考規範

- `.dev/requirement/requirement-guide.md`
- `.dev/requirement/TECH-STACK-REQUIREMENTS.MD`

## 輸出目標

理想輸出應該包含：

1. Metadata
2. Context & Goals
3. Personas
4. Functional Requirements
5. Non-Functional Requirements
6. Constraints & Assumptions
7. Domain / Business Rules
8. Acceptance Criteria
9. References

## Prompt 撰寫重點

至少提供：

1. 背景與目標
2. 目前已知的需求或討論筆記
3. 你希望 AI 幫你補齊哪些段落
4. 是否要輸出成完整 markdown
5. 不確定的地方是否要顯式標記 assumptions

## 範本 1：從討論筆記整理 requirement

```text
Help me draft a requirement document that follows `.dev/requirement/requirement-guide.md`.

Context:
- Topic: [topic]
- Current notes: [notes]
- Goal: convert these rough notes into a structured requirement document

Focus on:
- functional requirements
- non-functional requirements
- constraints and assumptions
- domain/business rules
- acceptance criteria

Return:
1. a complete markdown requirement draft
2. explicit assumptions
3. missing information that still needs clarification
```

## 範本 2：補齊缺失欄位

```text
Review this draft requirement and complete the missing sections according to `.dev/requirement/requirement-guide.md`.

Context:
- Existing draft: [paste draft]
- Keep the original intent
- Mark uncertain parts clearly

Focus on:
- missing metadata
- non-functional requirements
- business rules
- acceptance criteria

Return:
1. revised markdown draft
2. list of assumptions added
3. questions that still need stakeholder confirmation
```

## 範本 3：先做 requirement 骨架

```text
Create a requirement skeleton for this topic using `.dev/requirement/requirement-guide.md`.

Context:
- Topic: [topic]
- Known scope: [scope]
- Known goals: [goals]

Return:
1. markdown skeleton with all required sections
2. suggested content bullets under each section
3. missing information checklist
```

## 什麼情況要先交給 Architect

若你發現：

- bounded context 邊界不清
- domain language 衝突
- MQ / API / aggregate 責任不清

先交給 `ddd-ca-hex-architect`，再回來整理 requirement。
