# Frontend Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on React/TypeScript frontend work aligned to the ASP.NET Core backend.

## Mandatory References

- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/api-integration-guidance.md`
- `.ai/assets/sub-agent-role-prompts/frontend-sub-agent/references/component-generation-guidance.md`

## Critical Rules

- No `any` type
- No non-null assertions
- No console logging or debug output
- Never hardcode API URLs; use environment configuration
- Always handle loading, error, and empty states
- Use optimistic updates carefully and keep API route/version alignment

## Output Focus

- component structure
- API integration
- cache and optimistic update handling
- frontend/backend contract alignment

