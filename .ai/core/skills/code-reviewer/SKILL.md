---
name: code-reviewer
description: Review a bounded code or implementation-guidance scope for actionable defects using intended behavior, target-owned rules and evidence; report uncertainty and coverage without applying fixes.
---

# Code reviewer

Use the `review` instruction operation in [package metadata](skill-package.yaml).
Read [the common review method](references/review.md), establish the subject and
applicable target authority, then trace behavior and return evidence-backed prose
findings. Review is read-only; a request to review does not authorize repair or
external writes.

This package supplies common review reasoning. It ships no technology extension,
including no .NET specialist checks. Name unavailable requested coverage and retain
any target-required specialist gate. Do not imply that common review satisfies it.

No framework configuration, managed record store, schema, script, dependency or
Python runtime is required for this instruction. The caller supplies the intended
behavior, permitted target evidence and any target-specific rules. Use only the
permissions and environment actually available for those inputs. Return findings
in the conversation; export prose only when a destination and write are authorized.

The declared `implemented` status means these instructions exist in the package.
It is not evidence of invocation, independent review, correctness or acceptance.
