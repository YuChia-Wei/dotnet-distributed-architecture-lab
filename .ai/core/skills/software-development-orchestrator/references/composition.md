# Retrospective and public specialist handoff

Retrospective owns a reflection and optional semantic candidates in the workflow
record. No-new-knowledge is useful: retain actual outcome, observations, limits
and rationale, with an empty candidate list. Do not invent a Lesson or ADR to
complete a checklist.

A candidate names an exact destination/version, operation, evidence IDs,
applicability, missing inputs and concrete next action. The workflow has empty
required/optional dependencies and never imports, loads or calls a foreign package.
The user/agent selects an installed specialist and checks its own public contract,
configuration, runtime and actual task permission. Missing capability preserves the
candidate and workflow; it is not a failed primary write or a fabricated artifact.

| Destination | Obtain through its public contract before an authorized operation |
| --- | --- |
| lesson@0.2.0 / create | Content title, observation, evidence, conclusion, applies_when, does_not_apply_when, confidence, follow_up; actual related query text/status selection, query digest and caller decision. |
| adr@0.1.0 / create | Title, context, decision_drivers, at least two distinct options with benefits/costs, consequences, evidence and applicability; actual related-query digest/decision. |
| standards-promotion@0.1.0 / propose | Actual query/decision binding; configured existing target/read roots; target_id and expected actual target digest, complete replacement text, rationale, applicability/conflicts, exact source descriptors/digests and actual bytes. |
| local-backlog@0.1.0 / create | Title, summary, observable acceptance and reference-only workflow link. No Issue sync or execution authorization follows. |
| pr@0.1.0 / prepare | Actual repository and base/head selection, title/summary and real validation dispositions. The PR owner measures the actual Git subject. |

The three knowledge packages bind new-identity decisions to an actual related
query. Their decision contains action=new, actual query_sha256, reason and
acknowledge_partial where appropriate; placeholders are not usable evidence.
Do not generate an executable request until all their required inputs are actually
available. Semantic candidate text never substitutes an invented digest, approval,
source file, target baseline or decision result.

Lesson create yields a candidate; ADR create yields a draft. Their later accept/
decide operations require separate actual decision evidence. Promotion has no apply
operation: proposal, owner adoption, observed rule bytes and effect are different.
PR prepare does not imply GitHub create/update, publication, merge or checks.

Candidate state open requires next_action. Handed-off requires actual returned
reference IDs already in workflow content; the record still labels those
caller-supplied, not independently authenticated. Declined explains why in summary.
No label means accepted, adopted, effective or published.

Content changes clear the current retrospective and retain it in history.
Historical open candidates remain visible/protected unless an explicit later
retrospective dispositions the same identity. Retrospective identities cannot
silently change destination, operation, source evidence or applicability.
A terminal workflow is immutable even with open knowledge candidates. Continue
through a new linked workflow or specialist record. Such a link alone never releases
the old workflow's retention protections; a cleanup owner must reconcile them.
