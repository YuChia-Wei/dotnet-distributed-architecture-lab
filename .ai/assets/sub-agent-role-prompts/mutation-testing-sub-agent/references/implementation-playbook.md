# Mutation Testing Sub-Agent Implementation Playbook

Use this delegated sub-agent role when the main agent needs a worker focused on improving mutation coverage.

## Mandatory References

- `.ai/assets/shared/common-rules.md`
- `.ai/assets/shared/testing-strategy.md`

## Critical Rules

- Never change business logic just to kill mutants
- Always run existing tests before changes
- Always improve mutation score incrementally
- Keep assertion-free tests free of explicit assertions

## Expected Flow

- baseline test run
- baseline mutation run
- incremental contract and test strengthening
- final mutation verification

