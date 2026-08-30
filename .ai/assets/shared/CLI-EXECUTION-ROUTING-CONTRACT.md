# CLI Execution Routing Contract

This contract defines how an agent selects, verifies, and optionally preserves
the local command-line execution route for an operation after higher-priority
policy has selected CLI execution. It complements environment readiness:
readiness describes whether a CLI capability appears available, allowed, and
verified; routing describes where and how the authorized command executes.

This contract does not select between CLI and connectors, CI, external tasks,
agent delegation, browser automation, or other non-CLI capabilities. Those
decisions remain with their owning policies. A connector-first policy may
authorize a CLI fallback, but the local binding records only that CLI route.

## Authority Order

Resolve execution decisions in this order:

1. user instructions and explicit approvals;
2. system, enterprise, runtime, sandbox, and credential restrictions;
3. this portable contract and its schema;
4. an optional repository-local binding at
   `.dev/ai-context/local/cli-execution-routing.yaml`;
5. fresh readiness evidence;
6. the actual command receipt.

A lower layer cannot weaken a higher layer. A configured or ready route does
not prove that an operation ran or passed.

## Tracked And Local Boundaries

- Git tracks this contract, the schema, validators, agent guidance, and the
  `/.dev/ai-context/local/` ignore rule.
- Concrete host, distro, executable, shell, container, sandbox, and other
  personal CLI route values belong only in the ignored local binding.
- The local binding may exist inside the repository working directory, but it
  must be ignored and untracked before it is read as authoritative local input
  or written after consent.
- Never copy the local binding into a template, package, provenance record,
  workflow, assessment, tracked target policy, or execution receipt.
- The local binding is data only. It must not contain tokens, passwords,
  secrets, credential values, sessions, usernames, private endpoints, or raw
  approval messages.

## Route Resolution

Each CLI operation declares a stable `operation_id`, required `capability_id`,
and an ordered list of CLI route candidates. For each candidate:

1. confirm the surface and selector are permitted by higher-priority policy;
2. validate fresh readiness and any required approval;
3. execute the exact selected command route;
4. record actual execution separately from the local binding;
5. use fallback only for a schema-allowed condition.

Never silently change executable, shell, distro, container, credential
boundary, network boundary, sandbox boundary, privilege, or working directory.
A `disallowed` route is terminal and cannot trigger fallback. Do not retry the
same blocked route until a material environment fact has changed.

## Post-Recovery Persistence

When a CLI route fails and bounded diagnosis finds a different CLI route that
successfully completes the requested operation:

1. verify the requested operation succeeded;
2. determine whether the successful route is stable and reusable;
3. ask the user whether to preserve the minimal route facts locally;
4. before asking for approval, disclose:
   - the operation and capability;
   - the exact ignored local path;
   - the fields to be stored;
   - whether the write creates, merges, or replaces a binding;
   - that secret and credential values are excluded;
5. write nothing when the user declines or does not answer;
6. after explicit approval, prove the exact path is ignored and untracked,
   write only the approved minimal data, and read it back;
7. verify the saved route against current restrictions and readiness on later
   use.

If a saved route later fails and another route succeeds, ask again before
updating it. Do not offer to persist a one-off workaround that is not safe to
reuse.

## Portable Versus Local Values

The portable schema defines CLI surfaces, selectors, requirement vocabulary,
fallback conditions, consent state, and validation behavior. It intentionally
contains no populated host route. A WSL distribution name, executable path,
shell, container identity, or sandbox choice is valid only in an ignored local
record created after consent. Connector names, CI runners, task profiles, and
external-task selectors are outside this schema.

The local file is per clone. Removing it restores unconfigured route behavior.
Initialization may ensure the ignore rule and agent guidance exist, but it must
not create the local file. Upgrade must preserve the ignored file without
reading, packaging, overwriting, or migrating its personal values implicitly.

## Fail-Closed Conditions

Report `owner-decision-required`, `blocked-by-environment`, `disallowed`, or
`unavailable` and stop when any of these applies:

- no route is permitted;
- the local path is tracked, staged, not ignored, or crosses a symlink boundary;
- the local record is malformed, ambiguous, stale, or contains a forbidden field;
- persistence lacks explicit user consent;
- fallback would change a protected boundary without authorization;
- the same failed route would be retried without a material change.

## Canonical Schema And Validation

- Schema: `.ai/assets/shared/cli-execution-routing.schema.yaml`
- Local path: `.dev/ai-context/local/cli-execution-routing.yaml`
- Ignore rule: `/.dev/ai-context/local/`
- Validator: `.ai/scripts/validate-ai-context.py`

The validator checks the portable contract and any present local record. A
missing local record is valid and means that no personal execution route has
been preserved.
