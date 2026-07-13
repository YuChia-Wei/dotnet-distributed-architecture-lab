# .NET Backend Architecture and Coding Standards

This folder owns normative framework and repository standards. Reusable `.ai`
documents load concise projections of these rules for agents; they do not become
independent normative owners.

DDD / Clean Architecture / CQRS boundaries are normative. Database, ORM, event store, message broker, test package, and runtime versions are selected by each target repository from file-backed evidence.

EF Core, Dapper, Npgsql, WolverineFx, RabbitMQ, Kafka, and NSubstitute documents are conditional/reference guidance unless target repository configuration explicitly adopts them. For tests, Given-When-Then is the framework-wide minimum and Arrange-Act-Assert is not an allowed substitute. xUnit + BDDfy is the default; a target team may explicitly decline BDDfy, but its C# tests must still preserve GWT structure. Gherkin `.feature` files and their runners remain optional.

## Structure

- `ASPNET-CORE-CONFIGURATION-CHECKLIST.md`
  - ASP.NET Core configuration checklist
- `AI-CONTEXT-BOUNDARY.md`
  - AI context ownership and folder placement policy
- `AI-CONTEXT-OWNERSHIP.md` / `AI-CONTEXT-OWNERSHIP.yaml`
  - normative rule ownership, strength, precedence, and machine registry
- `AI-CONTEXT-LANGUAGE-POLICY.md`
  - language policy for agent-facing and human-facing context
- `CODE-REVIEW-CHECKLIST.md`
  - code review checklist and review criteria
- `GIT-COMMIT-POLICY.md`
  - commit title, body, and timing policy for agent-assisted work
- `WORKFLOW-GATE-POLICY.md`
  - rules for when agents should create workflow artifacts
- `anti-patterns.md`
  - anti-patterns and prohibited practices
- `best-practices.md`
  - recommended practices
- `coding-guide.md`
  - legacy Todo/Wolverine profile example; not active product truth or a new-project entry point
- `coding-standards.md`
  - coding style and implementation-level rules
- `project-structure.md`
  - conditional .NET backend target structure profile; architecture invariants are normative, while physical paths and names require target evidence or explicit adoption
- `rationale/`
  - rationale for portable pattern choices
- `README.md`
  - standards entry guidance

Operational guides, setup walkthroughs, FAQs, and troubleshooting documents have moved to `.dev/guides/`.

## Belongs Here

- normative documents
- checklist
- anti-pattern / best-practice
- conditional target project structure profiles with clearly separated invariants and examples
- stable standards entry points intended for long-term reference
- AI context governance, commit policy, and workflow gate policy

## Do Not Put Here

- setup guide
- quick start walkthrough
- FAQ
- troubleshooting / solution note
- one-off refactoring proposals or work records
- AI skill/prompt/workflow guide

Place these materials in the appropriate locations:

- `.dev/guides/implementation-guides/`
- `.dev/guides/design-guides/`
- `.dev/guides/learning-guides/`
- `.dev/guides/ai-collaboration-guides/`
- `.dev/workflows/`

## Notes
- ezDDD/ezSpec concepts must be preserved even without direct .NET packages.
- If no .NET equivalent exists, keep the rule and mark TODO rather than deleting it.
- `standards/` should not accumulate setup guides, troubleshooting guides, or FAQ-style documents.

