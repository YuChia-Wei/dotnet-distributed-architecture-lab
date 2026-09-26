# Frontend formal acceptance specification

created_at: 2026-09-26T06:15:44+00:00; updated_at: 2026-09-26T06:15:44+00:00

Sources: requirements.md and specifications.md v2, owner request and baseline8213a9e. All scenarios below initially not-executed. Unit/component tests isolate HTTP; only real browser/YARP/Docker checks establish integration. Test data is newly created lab product/stock/order, never deletes unrelated data. Restore both mock engines hybrid and Sandbox delay0 after controlled tests. Do not restart protected observability.

| ID | AC | Given / When / Then | Level |
| --- | --- | --- | --- |
| W01 | AC07 | Internal operations staff and existing products / browse+search+open detail / real values and filtered count, no fixtures invented | browser+real API |
| W02 | AC07 | Product and initialized stock / submit valid single-product order once / actual orderId and queried line item, stock reservation observable | browser+real API+broker |
| W03 | AC07 | Empty/failed product response or malformed order response / operate / distinct empty/error/unknown, no success/auto retry; invalid quantity sends no request | component |
| W04 | AC07 | Known and unknown order IDs / lookup / real lineItems or useful failure, no invented state; local history labeled | browser+HTTP |
| A01 | AC02 | Operator product form / create+edit+confirmed delete of test product / server readback follows each change | browser+HTTP |
| A02 | AC07 | Chosen product / explicit initialize+increase+decrease+restock / actual API semantics and refreshed quantity; failure never shown as zero | browser+HTTP |
| A03 | AC07 | REAL-001 direct quote and product / create purchase / immutable identity and actual Accepted with no receipt/stock increase | browser+HTTP |
| A04 | AC07 | Supplier post-commit delay / create then reconcile / unknown visible, original key retained, lookup resolves without automatic POST repeat | HTTP+UI state |
| A05 | AC07 | Accepted qty4 / receive2 then2 / actual partial/final states, receipts retained, overreceipt blocked; ambiguous receipt reconciles using same ID | browser+real domain |
| M01 | AC03 | WireMock reachable / select mock,proxy,hybrid / actual mappings/state and native provider response origin; logs visible and confirmed clear | browser+HTTP |
| M02 | AC03 | Microcks reachable / select three modes / stable artifact import and native dispatcher readback plus native mock/proxy response; custom/unavailable stays truthful | browser+HTTP+adapter tests |
| M03 | AC03 | Sandbox data / read orders+requests and set valid/invalid delay / actual readback, invalid blocked, restore0 | browser+HTTP |
| R01 | AC04 | Production containers / GET bare prefix,root and deep URLs then refresh / correct app/assets from YARP and usable navigation | browser+HTTP |
| R02 | AC04 | Missing JS and unknown API / request /404 or upstream failure, never200 SPA HTML; API success body staysJSON | HTTP |
| Q01 | AC05 | Desktop and390px viewport / navigate key forms with keyboard / labels/focus/alerts usable, no page horizontal overflow, tables contained | browser |
| Q02 | AC05 | One API unavailable / view related page / error+retry, unrelated navigation works, stale response cannot replace later selection | component+browser |
| Q03 | AC05 | Before/after deployment / inspect volumes and protected container identities /data retained and observability unchanged | actualDocker |
| D01 | AC06 | Reviewed final branch / createPR+merge+readback+cleanup / remote main equal, only this task removed, primary checkout deployment survives F worktree archival | provider+Git+Docker |

Existing backend limitations are visible: anonymous local lab, client-supplied Orders price snapshot, details without state/customer, no Inventory collection. No new production security/ownership promise. Four prior unrelated sample integration skips are not converted to passes. Record first failures and repaired reruns separately; no synthetic browser fixtures presented as real integration.
