# Retired v2 workflow record store

The three tracked records formerly stored here were relocated on `2026-09-29T22:11:55+08:00` without modifying their JSON bytes:

- `wf-0fa43e8dc60f4683ae1036abde90494b` → `.dev/workflows/2026-09-26-commerce-frontend/evidence/v2-source.workflow.json`
- `wf-28ef2d2ffe044802a4ddba263d5e5471` → `.dev/workflows/2026-09-26-procurement-supplier-lab/evidence/v2-source.workflow.json`
- `wf-a20ba85ce6cf4449a03d0dffacac867d` → `.dev/workflows/2026-09-23-framework-rc1-pilot/evidence/record-store-pilot-v2-source.workflow.json`

The first two now use their existing topic directories as the primary workflow records. The third remains supporting RC1 pilot evidence. Each topic contains an ID map or migration note. Git history also retains the former paths.

The installed RC2 `software-development-orchestrator` configuration still selects this store. Its future removal or rebinding belongs to the separately authorized framework upgrade; this record migration does not claim RC3 installation or change managed packages/lock.
