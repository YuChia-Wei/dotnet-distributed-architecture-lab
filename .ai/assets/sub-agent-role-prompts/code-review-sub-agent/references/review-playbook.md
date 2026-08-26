# Code Review Sub-Agent Playbook

Use this role for one bounded general .NET review slice. The top-level
`code-reviewer` skill owns severity, final findings, and any durable assessment.

## Review Flow

1. Read `.ai/assets/skills/code-reviewer/references/review-routing.yaml`.
2. Select routes by explicit scope, then type hierarchy, then path; use the
   fallback only when no specific route matches.
3. Load only the selected routes' canonical references and applicable finding
   rules. De-duplicate references across multi-file scopes.
4. Compare the code with those rules and report evidence-backed findings with
   file and line references.
5. Keep analyzer/test output as supporting evidence, not semantic ownership.

Do not load the legacy index, monolithic checklist, or shared review summaries
as additional rule sources.

## Output

- findings ordered as `CRITICAL`, `MUST FIX`, then `SHOULD FIX`;
- architecture-level and code-level findings separated;
- positive evidence and skipped/blocked validation stated after findings.
