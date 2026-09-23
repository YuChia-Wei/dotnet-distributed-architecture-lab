# Local Backlog public filesystem operations

Tool `local-backlog.fs`: `scripts/local_backlog.py`, Python >=3.11,<4, PyYAML >=6,<7, jsonschema >=4.18,<5. Request is one strict JSON object, from an absolute file or stdin using --request. CLI usage errors return JSON; --help is usage only. Success exits 0, other outcomes exit 1. No operation imports another skill.

Common required fields: operation,project_root,package_root. Optional common fields: project_config,local_config,overrides,write_roots. Unknown fields fail. Requests/individual records/diffs are bounded at 4 MiB; query reads at most 10,000 direct matching filenames. Oversize is unsupported, never a complete truncated result.

| Operation | Additional input | Result |
| --- | --- | --- |
| explain | None | Effective settings, provenance, roots/locks; capability not-probed; no creation. |
| query | Optional literal text, default empty | Title/summary substring matches sorted by filename/ID, digest per readable record, partial and per-file diagnostics. |
| inspect | reference: {role: local-backlog.record, id} | Strictly parsed record and raw-byte SHA-256. |
| revise | reference,expected_sha256,content | Complete authored replacement under lock; preserves controlled fields/extensions; equal content is byte/time-preserving no-op. |
| render | reference | Markdown view plus raw record/template/body hashes; no persisted view. |

Output includes operation,outcome,mutation_state and diagnostics as needed. Outcomes: succeeded,invalid-input,unsupported,unavailable,blocked,conflict,failed. A caller who did not invoke a tool reports not-executed separately. Mutation state is none/committed/unknown and describes record publication, not transient lock/parent creation. Write results retain directories_created and cleanup failures. Do not infer rollback from failure. Diagnostics do not echo input payloads/exception text; explicit inspect/explain/render results intentionally contain selected data.

## Record and template rules

Record identity is store-scoped, tool-generated UUID4 hex; created_at is fixed; updated_at changes only for a material update and cannot regress. Schema version is exact 1.0.0. Unknown versions are preserved and unsupported. The owned schema is selected from metadata v2's exact readable/writable identity. Same-document definitions are supported only with bounded acyclic references; remote/file/dynamic references and schema rebasing are rejected. Actual execution calls the schema validator; mere document readability does not constitute such execution.

Extensions use dotted namespace keys. Creation can supply them; revise/transition preserves them. References remain opaque data, never instructions or automatic fetching. A GitHub Issue reference must explicitly use reference-only relationship. No import/delete/migration, two-way sync or automatic authority transfer exists.

Templates are inert UTF-8 text. Substitute each token once, escape authored Markdown/HTML and reject unknown/malformed/missing tokens. Rendering a view never accepts view edits as record truth. Export needs separate destination authority.

## Local work and transitions

Filename <id>.work-item.json; ID work-<32 lowercase hex>. Authored content is title,summary,acceptance,references; acceptance is nonempty. Optional extensions may be supplied only at create. Controlled fields are schema_version,kind,owner,id,created_at,updated_at,writable_authority,state,state_reason,completion_evidence.

Create requires content. It sets writable_authority=local, state=draft, reason "Created as candidate work." and empty completion_evidence, then exclusively publishes. Query related work before deciding to create; no semantic deduplication is claimed.

Transition requires reference,expected_sha256,expected_state,target_state,reason,completion_evidence. Expected raw digest/state are checked under the same writer lock. Reason must be nonblank. Completed needs nonempty evidence objects {source,note}; other targets need an empty array. Evidence is caller-supplied, not independently authenticated or executed.

| Current | Allowed next |
| --- | --- |
| draft | planned,cancelled |
| planned | in_progress,blocked,cancelled |
| in_progress | blocked,completed,cancelled |
| blocked | planned,in_progress,cancelled |
| completed,cancelled | None; terminal and read-only |

Revise is allowed only before terminal state and preserves lifecycle fields. A state denotes project work, not permission to start implementation or proof of a passed check. The caller/project assesses acceptance evidence. Completion changes no PR/Issue/Project. Online links point to separately owned work; no provider operation or status mirror exists.

Required template tokens: id,title,summary,state,state_reason,acceptance,completion_evidence,references.
