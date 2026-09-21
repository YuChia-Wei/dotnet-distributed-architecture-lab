# Complete AI collaboration framework v0.18.0 upgrade implementation

## Template Metadata
- template_id: ai-context-governance-maintenance-workflow-plan
- template_version: 1.2.0
- created_at: 2026-09-18T06:21:54+08:00
- updated_at: 2026-09-20T11:56:05+08:00

## Workflow Metadata
- workflow_id: 2026-09-18-ai-context-v0-18-upgrade
- workflow_kind: ai-context-maintenance
- owner_skill: ai-context-governance
- branch: codex/2026-09-18-ai-context-v0-18-upgrade
- base_branch: codex/2026-09-17-efcore-wolverine-sample
- status: completed
- current_phase: completed
- artifact_root: .dev/workflows/2026-09-18-ai-context-v0-18-upgrade
- template_source: .ai/assets/skills/ai-context-governance/templates/ai-context-maintenance-workflow-plan-template.md
- template_version: 1.2.0

## Objective And Authority
Complete the owner-authorized v0.18.0 upgrade implementation for PR #13 under Issue #12. The owner authorized PR #13 to merge into `codex/2026-09-17-efcore-wolverine-sample` only after final admission; that authorization does not include sample-branch integration into `main`.

## Scope
Preserve product files, repository truth, target validation selections, and the four semantic customization identities. The Candidate11 package-adoption evidence now binds the admitted target package to the verified public v0.18.0 release; final PR admission remains separate.

## Completed Implementation
- Candidate11 build `0e5fbfc4a4a69ecd9da543751d53edfd311f93fb` and archive `51c550f974ab32581f1b02d4966bd84e6e5ac76bb7bd6b77fd5da2ce9ef84070` were retained.
- The public annotated tag object `cc7db483baa37d301056ec236706718fccdecb1f`, later equal-payload source commit `284bf9f2b0ab76f28df1bbf355e3909de956d1bd`, published asset `ai-collaboration-framework-v0.18.0.zip`, and publication receipt `7866392b97f64bb40d58f873d71e643e872126092608ef2fd9525f8718abba7b` were rebound to the target evidence.
- Attempt 14 remains bound to transaction `d7cd4592bd38778952b9261ff38b2aa30505ebfb7c46f5f7bd0965250033e990`, target receipt `d97d5dafb6c45d82e5cc71f142c98f9b339e44d11abea2dd18197c99c21e8c7b`, terminal receipt `78cc9511372d09b9eab62b5add5d3b68fa44f92090f2c929cb461e8bfb943d3f`, finalized target commit `4bf63f1701931c5d6d76dd51c82640412d5ad628`, and audit subject `43586065b014b241a5b81c1e442dfa60da13a15c`.
- `CUST-DOTNET-MQ-GOVERNANCE`, `CUST-DOTNET-MQ-VALIDATION`, `CUST-DOTNET-MQ-REPO-TRUTH`, and `CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION` remain preserved with their target-owned validation selections.

## Historical Checkpoint
The earlier v0.17.0 disposable-trial checkpoint, its incomplete receipt, and prior timeout, rollback, format-recovery, and hosted Project-preflight failure evidence remain historical and non-passing. Hosted run `35487203277` remains failed; the owner accepted a manual publication closeout exception and a separate follow-up Issue remains pending.

## Final Admission Still Required
1. Run the final target-owned gate once on the exact clean PR head:

   ```powershell
   python -B .dev/ai-context/tooling/validate-target-ai-context.py `
     --require-effective-rules `
     --commit-range codex/2026-09-17-efcore-wolverine-sample..HEAD `
     --workflow-id 2026-09-18-ai-context-v0-18-upgrade
   ```

2. Freeze that tracked tree and obtain a fresh fixed-head independent audit outside it, binding the exact subject, criteria, report, invocation, and authority hashes.
3. Re-read live PR review, checks, and branch-protection state before the separately authorized merge into the sample branch.

## Resume
This workflow's implementation content is complete. The final target gate, fixed-head audit, PR review/check read-back, and PR-to-sample merge are external admission and delivery work; none is recorded as passed here.