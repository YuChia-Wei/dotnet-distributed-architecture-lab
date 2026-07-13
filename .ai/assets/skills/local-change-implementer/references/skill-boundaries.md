# Local Change Implementer Boundaries

## Owns

- one local class/object/method/symbol technical edit;
- direct call-site updates;
- behavior-preserving local cleanup;
- small localized bug fix;
- local SQL/ORM implementation adjustment.

## Does Not Own

- planning a bounded implementation slice;
- command/query/reactor mode selection;
- architecture direction changes;
- class/interface extraction;
- dependency direction changes;
- domain language changes;
- cross-module changes.

## Handoff

- Use `slice-implementer` when the work needs a bounded multi-file slice.
- Use `ddd-ca-hex-architect` when the work needs architecture or domain-language decisions.
- Use `code-reviewer` when the local change came from review findings and needs independent verification.
