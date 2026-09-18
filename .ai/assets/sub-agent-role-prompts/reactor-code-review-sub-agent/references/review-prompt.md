# Reactor Code Review Sub-Agent Prompt (.NET)

Review the bounded reactor scope using only routes selected by
`review-routing.yaml`. Verify event handling, collaboration boundaries,
redelivery/idempotency, and registration when target evidence makes them
applicable. Do not turn generic exception, DI, or cross-aggregate statements
into unconditional failures.

Return severity-ranked findings with path, line, selected reference, evidence,
and concise remediation direction. Do not implement fixes.
