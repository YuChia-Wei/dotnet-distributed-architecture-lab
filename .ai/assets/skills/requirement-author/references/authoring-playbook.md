# Requirement Authoring Playbook

## Goal

Turn rough notes, existing drafts, or codebase facts into a requirement document that matches `.dev/requirement/REQUIREMENT-GUIDE.MD`.

## Workflow

1. Identify the topic and intended scope.
2. Read `.dev/requirement/REQUIREMENT-GUIDE.MD`.
3. Draft these sections:
   - Metadata
   - Context & Goals
   - Personas
   - Functional Requirements
   - Non-Functional Requirements
   - Constraints & Assumptions
   - Domain / Business Rules
   - Acceptance Criteria
   - References
4. Mark missing stakeholder truth as assumptions or open questions.
5. Recommend whether the next handoff should be `spec-author`, `ddd-ca-hex-architect`, or neither yet.

## Use Code Carefully

Codebase facts can help recover current bounded contexts, integrations, and constraints, but they do not override explicit requirement truth.
