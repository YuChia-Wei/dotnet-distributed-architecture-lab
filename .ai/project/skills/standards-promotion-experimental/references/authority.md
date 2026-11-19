# Proposal, adoption, rule bytes and effect

A proposal is project-owned review material, never a permission grant. Its tool
owns ONLY proposal JSON. It never writes a rule file or creates the evidence used
to adopt/activate its own proposal. Actual user authority and the project's owner
process remain separate from path configuration and local record data.

## Four facts

| Fact | Evidence and meaning |
| --- | --- |
| Proposal | Exact selected source snapshots, existing rule baseline and full replacement text. Stored content can be rendered/reviewed. |
| Owner adoption | A configured project-local JSON source maps subject digest, target ID, after digest, allowed actor, adopt/reject/revoke and actual decision time. |
| Actual rule content | Independently read exact target bytes and compare to the proposed replacement digest. |
| Declared effect | A separate mapped source binds proposal, target, replacement, raw adoption-source digest, applicability and active/inactive state with actual effective time. |

Configuration must explicitly select allowed evidence roots/pointers/actors.
Mapped actor IDs are strings, not authenticated identities. The trust basis is
`project-owned-local-evidence`: the project's ownership/access process must make
those local files credible. If that basis is insufficient, do not configure the
adapter; report unresolved. No generated flag, filename, record annotation or
requested file selection substitutes for the actual matching evidence.
No signature verification, provider adapter or network access is implied.

## Independent observation dimensions

`reconcile` rereads inputs and appends three dispositions with snapshots:

- Adoption: adopted / rejected / revoked / unresolved. Match every subject/target/
  replacement/actor field and an actual decision time no later than observation.
- Rule content: matches-proposal / drifted / missing. A target with different bytes
  is drifted even if adoption matches. An inaccessible/unsafe/non-UTF-8 target makes
  the invocation fail; it cannot claim a completed byte observation.
- Effect: effective / inactive / unresolved. Inactive needs a matching inactive
  declaration and matching adoption evidence. Effective additionally needs adopted,
  actual matching target bytes and active declaration with exact applicability.
  Effect time must be >= adoption decision time and <= observation time. Effective
  means observed project-declared effect; no runtime consumption/enforcement proof.

These dimensions do not overwrite one another. Matching adoption remains adopted
when target bytes drift, effect evidence is absent or conflicts are unresolved.
Unresolved conflict dispositions prevent effective; they do not erase adoption.
Missing selected evidence yields unresolved with a diagnostic; malformed JSON or
mapping retains the raw snapshot and unresolved dimension. A missing adapter or
omitted selection is unresolved. Unsafe/unreadable/oversized/non-UTF-8 input or an
expected-digest mismatch fails without publishing a new observation; other historical
observations remain untouched. Earlier observations do not become fresh evidence.

The record schema reserves rule_content=unresolved, but this filesystem operation
fails a read it cannot safely establish rather than fabricating an unresolved
snapshot. A successful observation uses matches-proposal, drifted or missing.
Inspect/render report historical state only. New reconcile means a new real
observation, not automatic reapplication or retry of another action.

## Identity and conflict correction

A proposal subject binds full captured target/config, source bytes/metadata/times,
baseline/replacement, applicability and authored conflict dispositions. The raw
record digest is a separate concurrency identity. Changes to observation/history
leave the proposal subject unchanged. A material unadopted revision changes the
subject and clears current observation while retaining it in history.

An EVER-observed adoption freezes revision even after later rejection/revocation.
Resolve remaining conflicts through a NEW proposal identity with current baseline
and new matching owner adoption. Do not revise the adopted proposal, rewrite its
history or reuse old adoption for a different subject. Changed target/config/
baseline also needs a new proposal. No global rule inventory or conflict-freedom
claim is made; reviewed scope is explicit in sources/rationale/conflict entries.

Withdraw/supersede changes a proposal only. Neither removes an effective rule nor
adopts its successor. Supersession pins same-target successor evidence without
writing the successor. Rule editing, owner decisions and effect declaration happen
through the project's existing process with their own actual authority.

## Custody and limits

Before publication the tool rechecks all selected package/config/evidence/target
bytes and absence observations. A changed accepted config binding conflicts even
if unrelated config text caused the change. No cross-file transaction is claimed;
external editors can race outside the cooperating writer model. Snapshots/history
remain within 4 MiB; overflow fails without silently pruning evidence. Snapshot
paths and exact file text are intentionally retained project data; use appropriate
project access controls and review exports. Diagnostics do not echo that data.
