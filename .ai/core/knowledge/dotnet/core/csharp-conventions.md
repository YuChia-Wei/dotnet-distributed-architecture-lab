# C# conventions

Use the target's accepted public contract, `.editorconfig`, formatter and
applicable compiler or analyzer settings. The presence of a C# file supplies a
language signal. It supplies no evidence of an adopted architecture or style
profile. Follow established conventions in surrounding code where target policy
leaves room for judgment.

## Retained style profile

Where the target adopted the existing `dotnet-backend` style rules, prefer
`this.` for member access, use plural folder names within projects, and include
Traditional Chinese (Taiwan terminology) XML summaries for public APIs. Apply
those rules within the adopted scope. This reference does not select them for
other C# code or prescribe XML comments on private implementation details.

## Implementation and evidence

Keep language and nullable annotations consistent with the actual project.
Preserve public signatures and observable failure behavior in a refactor. For
operations that perform asynchronous work, propagate cancellation according to
the accepted API contract and await the operation before using its result.
Treat formatter and analyzer results as evidence for their configured checks.
Select executable checks according to the target's affected behavior and rules.
