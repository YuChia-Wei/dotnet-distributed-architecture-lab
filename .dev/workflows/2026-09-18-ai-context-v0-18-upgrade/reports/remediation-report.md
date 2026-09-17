# Upgrade checkpoint evidence

This draft preserves the byte-exact v0.17.0 prerequisite projection and four reviewed target-gate corrections. It is an intermediate checkpoint toward v0.18.0, not a ready-to-merge upgrade.

The isolated applied snapshot `60e8f2aff84418b4a0a37ef7fbd4e88110c993f3` passed 52 target-context tests in 17.715 seconds. That receipt belongs to its original transaction and is historical evidence here; this checkout does not claim to have repeated or finalized that execution.

The prior transaction cannot finalize because its sealed decision bound the old provenance candidate. A separate clean replay is preparing correct authorities. Earlier audit-format, environment, timeout and rollback failures remain non-passing. v0.18.0 Candidate 04 passed archive and source-binding checks but has not been released or adopted here.

No product source, product tests or sample code is changed by this upgrade diff. The PR base retains the owner's existing EF Core/Wolverine sample commit.
