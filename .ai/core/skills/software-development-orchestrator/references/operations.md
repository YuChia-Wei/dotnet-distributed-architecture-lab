# Workflow public operations 0.1.0

Tool software-development-orchestrator.fs is scripts/workflow.py. Use Python
>=3.11,<4 with PyYAML >=6,<7 and jsonschema >=4.18,<5 (except explain).
No cross-skill imports, provider calls, task dispatch or command execution from
record text. Source implementation is not certification of behavior or installation.

```text
python /absolute/selected/package/scripts/workflow.py --request /absolute/request.json
python /absolute/selected/package/scripts/workflow.py --request -
```

Input is one strict UTF-8 JSON object. Common required keys: operation,
project_root, package_root. Optional common keys: project_config,local_config,
overrides,write_roots. Unknown keys fail; roots/settings follow
[configuration](configuration.md). Output is one JSON object containing operation,
outcome,mutation_state; exit 0 only for succeeded, otherwise 1. CLI usage errors
produce JSON; --help is usage, not permission or an availability claim.

| Operation | Additional required keys | Optional | Effect |
| --- | --- | --- | --- |
| explain | none | none | Effective settings/source/locks; no record mutation. |
| create | content (minimal shape below) | extensions | Exclusive publication of one new workflow. |
| inspect | reference | none | Full supported record and actual raw digest. |
| query | none | text, default empty | Case-insensitive literal title/intent matches, sorted by filename. |
| checkpoint | reference,expected_sha256,content,reason | none | Complete current authored content; retain old state, clear current retrospective. |
| transition | reference,expected_sha256,expected_state,target_state,reason | none | Workflow state/reason only, clearing terminal next_action. |
| resume | reference | none | Required continuation view, binding, history changes and next action. |
| retrospect | reference,expected_sha256,retrospective | none | Bound authored reflection/candidates only. |
| render | reference | none | Escaped inert Markdown plus record/template/body digests, result only. |
| retention-preview | mode,selection | none | [On-demand preview](retention.md); no cleanup execution. |

reference is {role:software-development-orchestrator.record,id:wf-<32 lowercase hex>}.
IDs are store-scoped. expected_sha256 is the actual raw 64-lowercase-hex digest
returned by a read; no synthetic hash/ID/time can replace an observation.
Extensions are creation-only JSON values under dotted namespace keys.

Each request/input/serialized record/result is bounded to 4 MiB. Query/retention
scans at most 10,000 direct filenames; overflow is unsupported, never silently
truncated success. Malformed/unknown/unreadable records yield partial diagnostics.
A non-atomic scan is not absence proof. Runtime evidence remains caller-attributed.

Mutation results retain changed,reference,sha256,store_root,directories_created
when available. mutation_state is none before/no publication, committed after
publication/read-back, or unknown for uncertain publication. It excludes transient
locks/parent creation. Cleanup failures override success and never imply rollback.
An unchanged authored checkpoint/retrospective is byte/time-preserving no-op.
Terminal writes are unsupported even for an otherwise identical request.

Outcomes: succeeded,invalid-input,unsupported,unavailable,blocked,conflict,failed.
No invocation must be described by the caller as not-executed, not a fabricated
tool result. Inspect labels stored observations historical. Resume exposes current
and historical candidate state; no stored command or owner string grants authority.

## Workflow states and completion

planned -> active/cancelled; active -> blocked/completed/cancelled;
blocked -> active/cancelled; completed/cancelled are immutable.
A reason and concrete current next action are required for nonterminal work.
Blocked reason/next-action owner describe the blocker; resumption reason records
the resolution. Task states/dependencies remain explicit rather than inferred.

Complete requires every task completed/deferred/cancelled, every acceptance
succeeded/not-applicable/deferred, no open decision or unresolved blocking reference,
and a retrospective bound to current content. Failed/blocked/not-executed acceptance
keeps work open. Deferred items have attributed authority, owner, reason, trigger
and follow-up. Derived completion_disposition is with-deferrals or without-deferrals,
never an aggregate verification pass. Cancellation preserves unfinished content,
records a reason and clears next_action without a completion claim.

No delete, import, conversion, store move, archive/compaction writer, generic
scheduler or provider operation exists. Schema/version/config and package updates
do not rewrite historical records. Unknown record versions remain unsupported,
unmodified and visible in partial query diagnostics.

## Rendering and resume

Template tokens are id,title,intent,scope,state,acceptance,tasks,evidence,decisions,
references,next_action,retrospective,history,storage_notice. All are required.
Reject unknown/missing/malformed tokens. Substitution is one pass, escaped
Markdown/HTML; no expression/include/eval or reverse import. Export is separately
authorized caller work. State renders both state and reason.

Resume preserves the full current content, raw record identity, retrospective,
last known historical candidates, state changes/decision reversals and evidence.
resume_budget_chars bounds the full summary. If meaning cannot fit, return
unsupported with a limit diagnostic; inspect remains available for the full
bounded original. No mandatory lifecycle metadata is silently truncated.

## Record shape

The owned [schema](../schemas/workflow-record.schema.json) and semantic rules below
define exact record fields. Schema checks do not authenticate reports or authority.

## Controlled envelope

| Field | Shape / ownership |
| --- | --- |
| schema_version | Exact string 1.0.0 |
| kind / owner | workflow / project |
| id | Tool UUID4: wf- followed by 32 lowercase hex; filename <id>.workflow.json |
| revision | Exact integer >=1; increments once per material mutation |
| created_at / updated_at | Actual RFC3339 with seconds/offset; created fixed, updated nonregressing |
| state / state_reason | planned/active/blocked/completed/cancelled; reason nonblank |
| content | Authored object below; mutation through checkpoint only |
| retrospective | null or object below; mutation through retrospect only |
| history | Ordered former-state entries; empty initially |
| extensions | Optional object; dotted namespace keys, JSON values; creation only, preserved |

Identity plus resolved store is the logical reference. A caller must retain the project/config/store binding with a reference when handing it across sessions; an ID alone is insufficient. Operations use reference={role: software-development-orchestrator.record, id: ...}. No external fetch is triggered by record text.

Each history entry is {from_revision, operation, recorded_at, reason, previous_sha256, previous_state}. previous_state is the typed object {state,state_reason,content,retrospective}. It excludes envelope/history/extensions. Entries are contiguous from 1 through revision-1 and preserve former evidence, failures, scope, decisions and retrospective. prior digest is over actual old bytes, not a promise the old serialization can be reconstructed. No history compaction/write/import edge exists. A material checkpoint clears the current retrospective after saving it in history; transition alone does not invalidate its content binding. Equal authored input is a byte/time-preserving no-op.

## Authored content

All fields below are required in a checkpoint replacement. Create expands the smaller semantic request into them deterministically.

| Field | Shape |
| --- | --- |
| title / intent | Nonblank strings |
| scope | {included: nonempty string array, excluded: string array} |
| acceptance | Nonempty array of {id,criterion,disposition,evidence_ids,reason,deferral} |
| tasks | Nonempty array of task objects below; IDs unique, existing IDs cannot disappear |
| evidence | Array of evidence objects below; append-only immutable IDs/entries |
| decisions | Array of {id,question,state,owner,resolution,source_refs,next_action}; state open/resolved |
| references | Array of reference objects below; IDs unique; referenced entries cannot disappear |
| next_action | {task_id,owner,action,condition} or null |

Acceptance IDs are stable path-safe strings. Dispositions: planned,not-executed,succeeded,failed,blocked,deferred,not-applicable. Succeeded/failed require nonempty evidence_ids pointing to compatible outcome/subject evidence; those remain attributed claims. Not-applicable needs reason; deferred needs deferral. Deferral is null except for a deferred item; then it is {reason,owner,trigger,next_action,authority_ref}, all nonblank. authority_ref is an inert attribution, never authenticated permission. Criterion changes get new IDs; old criteria remain with truthful disposition/reason. Closure permits only succeeded,not-applicable,deferred, with no global pass inferred. A later checkpoint may record a new disposition but former failures remain in immutable evidence/history.

Task = {id,title,action,completion_condition,depends_on,state,reason,result,evidence_ids,deferral}. IDs match T plus 3-6 digits; create produces T001; caller chooses nonreused later IDs. depends_on is a unique array of existing task IDs. reason/result may be empty only in pending/active initial progress; terminal/failure/blocked/deferred states need explanatory reason. Completed additionally needs result and evidence_ids. deferral matches the acceptance deferral shape only when state=deferred. A dependency must be completed before its dependent task becomes active/completed; deferral/cancellation does not satisfy it. Altering edges on a completed task is unsupported. Other dependency changes require a reason and preserve the prior plan in history.

| Current task state | Allowed next task state through checkpoint |
| --- | --- |
| pending | active, blocked, deferred, cancelled |
| active | completed, failed, blocked, deferred, cancelled |
| failed | active, blocked, deferred, cancelled |
| blocked | active, deferred, cancelled |
| deferred | pending, cancelled |
| completed, cancelled | none |

Same-state progress updates are permitted if invariants hold. Retry is recorded, never dispatched or authorized by state. New tasks must start pending. No active/completed task may have an unmet dependency. Terminal task action/condition/result/evidence/deferral remains immutable; later correction is a new linked task and historical explanation. A workflow checkpoint cannot mutate terminal workflows.

Evidence = {id,task_id,summary,disposition,subject,source_refs,reported_by,observed_at,basis}. task_id is an existing ID or null for workflow-level evidence. disposition uses the acceptance vocabulary. subject is a nonblank bounded description of the exact examined input/commit/artifact; a source digest belongs in a reference when available. source_refs points to existing reference IDs. succeeded/failed requires at least one source ref and observed_at; other dispositions may use null observed_at. reported_by is attribution, not authentication. basis is always caller-supplied. Observed_at is caller-reported RFC3339, no later than actual record write time; this is a chronology check, not proof of observation. The tool never executes a command copied into summary, trusts an arbitrary log as permission, or manufactures a success from a status. Correct bad evidence with a new ID and explanatory new observation; retain the old entry.

Reference = {id,kind,target,schema,sha256,resolution,blocking,evidence_value,note}. kind is same-store-workflow or opaque. target is an exact wf-ID for same-store-workflow; otherwise an inert nonblank locator. schema and sha256 can be null; a supplied sha256 must be 64 lowercase hex. resolution is unverified/resolved/missing/stale and remains caller-attributed; a digest string does not prove resolution. blocking is boolean; evidence_value is irreplaceable/replaceable/unknown. note records the basis/limitations. Retention may report a new direct same-store observation separately but never rewrites this reference. No global absence claim can arise.

Decisions retain stable IDs/questions. An open decision needs owner and next_action; resolution may be null. Resolved requires nonblank resolution and nonempty source_refs, and next_action=null. Owner/source attribution is not a grant. Deleting decisions is unsupported; corrections preserve history.

next_action is required non-null for planned/active/blocked, with an existing task_id or null for an owner decision. It states who does exactly what and under which condition. A nonterminal checkpoint cannot set it null: when substantive work is ready, the next action names retrospective or the explicit terminal decision. Transition to completed/cancelled sets next_action=null itself and preserves the former state. Retrospective binding below uses content with next_action normalized to null so this controlled terminal change is not content drift.

## Retrospective

Authored request: {outcome,reflection,rationale,candidates}. outcome is no-new-knowledge or candidates. reflection is {actual_outcome,observations,limitations}; strings are nonblank; rationale explains the conclusion. no-new-knowledge requires []; candidates requires nonempty candidates.

Candidate = {id,destination,operation,summary,source_evidence_ids,applicability,missing_inputs,next_action,state,result_refs}. Destination is one of the exact five identities in composition.md; operation is their selected public create/propose/prepare operation. state is open/handed-off/declined. Candidate IDs are stable. Open needs next_action; handed-off needs actual result_refs (existing reference IDs); declined needs a reason in summary. An artifact request alone is not handed-off evidence. This record never means accepted/adopted/published.

The tool adds basis=caller-supplied, actual recorded_at and content_sha256. Hash the current content with next_action replaced by null, sorted JSON keys, indent=2, ensure_ascii=false, LF termination and UTF-8 bytes. Arrays retain order. This is a retrospective input binding, not an execution receipt. Other content drift invalidates the retrospective and checkpoint clears it; old versions remain in history. Retrospect can update candidates before workflow completion, preserving old retrospective. A terminal record is immutable; later knowledge follow-up uses a successor workflow or the specialist directly.

Completion outcome is derived at read time as with-deferrals or without-deferrals from acceptance/tasks. Neither is a verification aggregate. Resume must display all failed observations and unresolved candidates even if workflow completed. Open knowledge candidates may remain at completion because they are optional follow-up, but they protect cleanup until disposition is reconciled.

## Minimal create expansion

Input content={title,intent,scope,acceptance:[{id,criterion}],first_action:{action,completion_condition,owner}}. No caller ID/time/state/history is accepted. The initial task title equals first_action.action; T001 pending; all dependencies/evidence_ids empty, reason/result empty, deferral=null. Acceptance starts not-executed with reason "Not executed by this tool.", empty evidence_ids and deferral=null. Evidence/decisions/references empty; next_action points to T001 with supplied owner/action and condition "After actual task authorization." State planned. No retrospective, task completion or runtime availability is fabricated.


All stable reference IDs and their kind/target/schema/digest are retained; changing a target or digest needs a new reference ID. Resolution, evidence-value and explanatory observations may change with retained history. All old task/acceptance/decision/reference IDs remain present. Terminal tasks are fully immutable, not just their state. Completed tasks need reported success evidence tied to that task or workflow-level evidence. Semantic subject accuracy remains the caller responsibility.

Historical candidate meaning is retained across content changes that invalidate the current retrospective. Open candidates remain visible to resume/retention even when no current retrospective exists. Neither a link nor a summary resolves them.
