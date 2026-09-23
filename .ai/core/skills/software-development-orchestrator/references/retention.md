# On-demand retention previews

retention-preview accepts mode compact/archive/purge and 1-100 exact workflow IDs.
It never schedules work, mutates a record, writes an archive/summary, deletes,
rewrites Git history, generates a cleanup script or grants cleanup permission.
A successful operation means a preview was returned; protected items are not safe
to dispose of.

Each preview binds selected record raw digests, revision/schema, actual observation
time, the chosen age threshold and same-store reference observations. Age starts at
the terminal transition's updated_at; terminal records cannot subsequently mutate.
Null disables the selected mode. Age eligibility is only a filter, not safety proof.

Scan at most 10,000 direct workflow filenames in the selected store. Preserve
unreadable/unsupported/malformed-file diagnostics and partial state. Scans are
non-atomic; selected record bytes are re-read after scanning. Other writers and
external inbound references remain outside the claim. Never follow opaque links
or treat a single store scan as proof that no outside consumer exists.

## Protected meaning

The following block a proposed cleanup: active/planned/blocked workflow; pending,
active,failed,blocked,deferred task; failed/blocked/unexecuted/deferred acceptance;
open decision; unresolved/blocking reference; open current or historical candidate;
unknown/irreplaceable evidence value; incomplete reference scan; selected drift;
or inability to fit required summary meaning. Source-removing modes also protect
known same-store inbound targets. A later linked workflow or caller string is not
a preserved exact-byte copy or reconciled reference.

Each supported record's summary includes identity/store/schema/revision/digest,
intent/scope, acceptance, all task outcomes/dependencies, failures and deferrals,
decisions, references/evidence uniqueness, retrospective/current and historical
candidates, exact next action or terminal reason, tracking/durability uncertainty
and history changes including reversed decisions. The summary retains values before
and after changes. Unchanged historical data need not be repeated; omitted_history
does not hide a change. resume_budget_chars bounds this whole summary. If mandatory
meaning exceeds it, return a protected result with a limit diagnostic, never a
successful truncated summary. Inspect can supply the full bounded original.

## Mode results

- Compact: a closed eligible fully understood record may receive
  summary-available-original-retained. This is a result-only presentation;
  the original record/history remains authoritative and untouched.
- Archive: protected or needs-owner-reconciliation. Name required exact-byte durable
  copy, digest/read-back, destination reader, recovery and reference/resume continuity.
  No destination is silently selected and no archive backend is implemented.
- Purge: protected or needs-owner-reconciliation, never safe-to-delete. Explain loss
  of record/history/sole evidence and missing owner, retention, backup and external
  reference reconciliation. A claimed replaceable reference or matching hash alone
  is not a retained copy.

Actual cleanup requires a separately scoped owner process. This package has no
compact/archive/purge writer, global reference registry or external archive backend.
