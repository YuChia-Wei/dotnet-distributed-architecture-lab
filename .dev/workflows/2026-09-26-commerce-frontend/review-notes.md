# Review observations

created_at: 2026-09-26T06:20:30+00:00; updated_at: 2026-09-26T07:08:02+00:00

Scope: Issue18 frontends, fixed SupplierMock adapter, YARP/Compose, and the minimal Product SaveAsync repair. Root independently reviewed Sol output with the generic code-reviewer method and selected retained .NET mixed-review packet. Worker self-review and cross-review are attributed support, not independent terminal admission of the framework installation.

| ID | Severity / source | Finding and disposition |
| --- | --- | --- |
| SPEC-01 | Parent specification | Initial Inventory restock wording said absolute; Sol traced additive behavior before implementation. Parent corrected v2; domain unchanged. |
| REV-01 | MUST FIX / parent | Floating money equality rejected19.99 and response body stream failures escaped uncertain-result handling. Repaired with focused Web tests; actual19.99 sale passed. |
| REV-02 | MUST FIX / parent | Receipt request identity and stale GET could cross route or overwrite newer mutation. Repaired order binding, cancellation and serialization; Web component cases and real two-stage receiving passed. |
| REV-03 | MUST FIX / parent | Non-object native Microcks JSON escaped intended unavailable result. Repaired guards and in-memory transport tests. |
| REV-04 | MUST FIX / parent | Admin rejected nullable native dispatcher metadata. Repaired parser and tests; real custom mode remained visible. |
| REV-05 | SHOULD FIX / parent | Product uncertain creation and raw backend errors needed friendly readback guidance. Repaired. Actual empty-description500 rendered bounded uncertainty, not stack trace. |
| REV-06 | MUST FIX / parent | Frontend Dockerfile app-relative COPY disagreed with repository-root context. Contexts fixed; actual Docker builds passed. |
| REV-07 | MUST FIX / parent | Bare-prefix redirect could expose internal Nginx origin; missing Admin assets could fall through. Relative redirect and asset404 guard fixed; actual YARP routing passed. |
| RUN-01 | MUST FIX / actual Docker | Web Nginx unquoted regex quantifier failed startup. Quoted regex and build-time nginx-t added; rebuilt container and200 entrypoint passed. |
| BACKEND-01 | MUST FIX / actual UI+SQL | Existing Product SaveAsync referenced nonexistent productsales after UPDATE, rolling back edits. Removed only orphan SQL; aggregate/schema/transaction and Dapper choice unchanged. Actual PUT,GET and soft-delete succeeded. |
| RUN-02 | MUST FIX / actual UI | Description was presented optional but Product domain requires nonblank. Parent baseline also omitted this fact. Sol repaired required label, trimmed field validation/focus and create/update test; deployed form blocks blank description. |
| REV-08 | MUST FIX / Sol platform review, parent confirmed | Web missing ico/jpg fallback violated resource404. Extended guard, actual404 for js/ico/jpg confirmed; extensionless routes remain200. |
| RUN-03 | MUST FIX / actual native Microcks | Main artifact reimport left old POST dispatcher. Initial native PUT implementation followed current guide but actual1.15 requires query parameters; initial fix returned400. Retain both failures. Native 1.15 query parameter and ancillary-field preservation repair passed 9 in-memory tests, then all three modes and mock/proxy origins passed actual Docker/UI rerun. |
| REV-09 | MUST FIX / Sol cross-review, parent confirmed | Sandbox submit was enabled before first GET; readback comparison could compare refreshed input with itself. Gate on loaded state and compare immutable requested value; repaired; 19 Admin tests and actual deployed delay1->0 readback passed. |

## Scoped checklist comparison

| Selected check | Assessment |
| --- | --- |
| Domain boundaries and factual APIs | Vue calls existing domain APIs; no invented Order status/list or Inventory collection. Products/Orders Dapper and Inventory EF retained. |
| External outcomes and identity | No automatic mutation retry; frozen purchase identity; original receipt identity bound to order; 202 unknown and reconciliation explicit. |
| .NET adapter routing and contracts | Fixed origin/presets only; bounded timeout, serialized mode change, explicit live native readback; native 1.15 contract and actual three-mode verification passed. |
| Aggregate repository / SQL | Scope removes nonexistent child-table SQL only. No new port, domain behavior, commit owner, ORM or schema. Real database edit/read/delete verified. |
| Input/errors/accessibility | Numeric/UUID/required fields and bounded errors checked; confirm dialog keyboard trap/Escape; responsive390px and desktop, no page overflow in inspected views. Not a WCAG certification. |
| Deployment/data | Five-file composition; production Nginx, YARP same origin and prefixes. Protected9container IDs/start/status/mount identities unchanged at observed comparison. |
| Tests | Worker unit/DOM evidence and actual Docker/browser evidence kept distinct. No generic unit pass claimed as database/broker acceptance. |

## Environment and validation limitations

- Owner instructed avoiding unattended network-access prompts. Newly added adapter tests use in-memory HTTP; node tests use DOM fixtures; real integration uses existing Docker. No firewall or approval prompt was self-approved. Existing host-listener test cases excluded after the instruction.
- F: RAM disk build contexts worked, but Docker Desktop file bind mounts failed. During integration, gateway config is staged on C: via ignored override. Required durable main redeployment remains pending before worktree cleanup.
- First Compose build omitted verification overlay and failed; corrected five-file composition passed. First framework resolver invocation used relative root and failed provenance lookup; absolute-root call passed. First protected snapshot comparison included extra after-only fields; explicit baseline-field comparison passed all9.
- Original browser native confirm locked one temporary tab. Replaced new Admin browser-native confirmation calls with accessible in-page dialogs; actual cancel/Escape and confirmed deletion/mode actions passed.
- Specifications/source can require repairs even with detailed planning. Current documentation endpoint example did not match pinned Microcks1.15 request parameters; authentic native execution remained necessary.
