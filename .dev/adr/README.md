# .NET ADRs (Single Source of Truth)

This folder is the **authoritative ADR set for .NET work**. All ADRs that matter to current .NET delivery live here. The goal is **no back-and-forth** to `.dev/adr/`.

## Policy
- **Translate**: Architecture/DDD/CQRS/testing/process ADRs that need .NET adaptation.
- **Copy**: Tech‑neutral ADRs that still govern the product.
- **Discard**: Java‑only legacy decisions with no .NET value (listed below).
- **No missing ADRs**: If an ADR exists in `.dev/adr/`, it must be copied/translated here unless explicitly discarded.

## Stack Mappings (for translated ADRs)
- **DI/Config**: ASP.NET Core DI + Options Pattern
- **Outbox**: WolverineFx (Outbox) + EF Core + PostgreSQL
- **Testing**: xUnit + BDDfy (Gherkin‑style naming only; no `.feature`)
- **Mutation Testing**: Stryker.NET
- **Profiles**: `appsettings.{Environment}.json`

## Discarded / Not Applicable
- `ADR-022-ezddd-gateway-version-upgrade.md` — Java‑only legacy upgrade; no .NET value.

## How to Use
- When working on .NET tasks, **only reference ADRs in this folder**.
- If a new decision is made, create it here and (optionally) mirror to `.dev/adr/` for historical context.
