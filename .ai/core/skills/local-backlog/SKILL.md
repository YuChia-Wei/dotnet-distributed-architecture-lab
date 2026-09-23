---
name: local-backlog
description: Create and update project-owned local work items with explicit state and conflict checks.
---

# Local Backlog

Use this independent skill for a selected local-file work collection, including references and truthful status changes.
No workflow, ADR, Lesson, source-repository policy or other skill installation is required. Project records/settings/templates remain project-owned. Metadata says implemented because source exists; it is not runtime acceptance, availability or authorization evidence.

1. Read [configuration](references/configuration.md); select explicit project/package roots and optional config files. Explain is read-only and never discovers a fallback store.
2. Read [operations](references/operations.md); choose the smallest authorized operation. Inspect before updating; use actual returned raw-byte digests.
3. Review the selected record/content and actual result. A failed or uncertain write does not prove rollback; never blindly retry.
4. Preserve unsupported versions, extensions and unrelated files. Installation, record migration, external authority, completion and publication are separate decisions.

Entry: `python <absolute-package>/scripts/local_backlog.py --request <absolute-request.json|->`. [Schema](schemas/local-backlog-record.schema.json), [default template](templates/work-item.md), [synthetic example](references/example.md).

GitHub Issue links are reference-only. This skill never reads or writes a tracker, mirrors remote status, transfers authority or synchronizes stores.
