# Project-owned agent roles

These six role definitions and their required references are project-owned custom
context, separate from installer-managed skills and knowledge. Read an exact role
manifest and its references only when a parent selects that role with bounded
scope, permissions, expected output and stop conditions. Profile presence does
not prove invocation or a validation pass.

The Codex profiles under `.codex/agents/` retain their existing reasoning efforts
and role permissions. The bounded routine worker, evidence report synthesizer,
fixed-head independent auditor, reconciliation worker and semantic governance
analyst explicitly select `gpt-6.1-sol`. The context translator explicitly selects
`gpt-6-luna` with `max` reasoning to retain its low-cost runtime requirement.
Verify the resolved model when invoking a role; configuration changes do not
prove that an already running child changed models.
See [Codex custom-agent configuration](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

The translator manifest lists its retained Codex and Claude adapters. The removed
Copilot adapter is no longer declared. Claude model and dispatch settings remain
with their own adapter. Shared execution and guardrail contracts still apply;
examples referring to retired skill paths are historical illustrations.
