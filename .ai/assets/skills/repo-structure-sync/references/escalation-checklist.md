# Escalation Checklist

Use this checklist after the low-cost inventory pass.

## Decision Rule

- Stay on the low-cost model when no `P0` trigger is present and there is at most one `P1` trigger.
- Escalate when any `P0` trigger is present.
- Escalate when two or more `P1` triggers are present.
- Escalate when one `P1` trigger is present and the user explicitly wants architecture-grade rewriting instead of a light sync.

## `P0` Triggers

- the repo has multiple solutions with overlapping or unclear ownership
- the repo mixes major stacks and the .NET portion is not the only primary structure
- local docs materially conflict with `*.csproj`, package references, or startup projects
- the requested update requires nontrivial architectural interpretation, not just fact sync
- the target docs need a fresh architecture narrative rather than direct section replacement

## `P1` Triggers

- more than one executable host type exists, such as API plus worker plus consumer
- module boundaries are implied by folders but not clearly confirmed by project names
- there are several shared libraries and their ownership is ambiguous
- deployment topology is spread across multiple folders or tools
- test projects exist but mapping from tests to modules is not obvious
- copied template docs contain many stale names that do not map cleanly to current repo files
