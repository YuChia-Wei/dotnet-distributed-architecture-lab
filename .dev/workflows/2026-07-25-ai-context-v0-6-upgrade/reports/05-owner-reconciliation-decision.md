# v0.6.0 Owner Reconciliation Decision

## Why Approval Is Required

v0.6.0 replaces schema-1 `local_overrides` with a semantic customization
ledger. The published contract forbids inferring semantic meaning during legacy
conversion. A finalized non-unresolved customization also requires explicit
owner approval.

No component-aware provenance or customization authority has been written yet.
The legacy v0.5.0 provenance remains authoritative while this decision is open.

## Proposed Decisions

### CUST-DOTNET-MQ-GOVERNANCE

- Relationship: `extends`
- Disposition: `merge`
- Proposal: retain the target-specific downstream projection, workflow,
  documentation, and boundary details that still differ; adopt 13 paths already
  equivalent to v0.6.0 and retire 6 paths replaced by `ai-context-init` or
  `software-development-orchestrator`.
- Remaining differing paths: 18.
- Incoming status: `partial`.

### CUST-DOTNET-MQ-VALIDATION

- Relationship: `deviates`
- Disposition: `supersede`
- Decision: fully adopt v0.6.0 validation behavior. The historical disabled
  ANSI color variables are not retained because the repository now standardizes
  on PowerShell 7.
- Incoming status: `equivalent-candidate`.

### CUST-DOTNET-MQ-REPO-TRUTH

- Relationship: `target-only`
- Disposition: `retain`
- Proposal: retain all 13 repository identity, catalog, configuration,
  workflow, backlog, and root-entry paths as target-owned truth.
- Incoming status: `conflicting` by design because public templates cannot
  replace initialized repository truth.
- Existing schema-1 disposition already records `retain as target-owned truth`;
  this proposal carries that decision forward without semantic expansion.

## Owner Response

Status: `approved`

- Governance: approved as proposed.
- Validation: approved with the change from `retain` to `supersede`; fully
  adopt v0.6.0.
- Repository truth: approved as proposed.
- Owner: `dotnet-mq-arch-lab maintainer`
- Decided at: `2026-07-25T07:56:49+08:00`
- Evidence: owner response in the active v0.6.0 upgrade session.
