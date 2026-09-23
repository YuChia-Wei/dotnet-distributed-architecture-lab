# Synthetic example; not execution evidence

Assume an existing project parent notes and an explicitly selected package root. No example below is an actual record, grant or validation receipt. Replace every path/digest/commit placeholder with real inputs; do not invent a hash.

Optional project JSON:

```json
{"config_version":2,"skills":{"local-backlog":{"store":{"root":"notes/work-items","tracking":"tracked"}},"example.other":{"inert":"not consumed"}}}
```

No config is also valid and selects package defaults. An ignored store uses tracking=ignored; the project establishes its own Git policy. A selected local config in Git must already be ignored/untracked.

Create content can be {title: "Document timeout behavior", summary: "Describe the timeout response.", acceptance: ["Documented response matches implementation."], references: []}. A real create returns a new work UUID and raw digest. Inspect before revise/transition. Draft -> planned -> in_progress -> completed uses actual expected states/digests and real completion evidence; no online Issue is required or changed.
