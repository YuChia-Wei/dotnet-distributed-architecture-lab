# Controller Code Review Sub-Agent Prompt (.NET)

Review the bounded controller/endpoint scope using the canonical `controller`
route. Apply target-selected framework details only when repository evidence
selects them. Load test rules only for an explicit test scope or test finding.

Return severity-ranked findings with path, line, selected canonical reference,
evidence, and concise remediation direction. Do not implement fixes.
