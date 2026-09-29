# Current framework selection and target authority

Issue [#22](https://github.com/YuChia-Wei/dotnet-distributed-architecture-lab/issues/22) authorizes replacing the prior RC1 installation in this target. The final fixed product source is `aad927328c20b08c8445e8ad1792eadd8ecc3466`, published as `v0.19.0-rc.2` by the source repository. The selected catalog identity is `catalog:1:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:eb997697e9cd8b348092773176162dbdb564ded7d52bef663fde80b98c427d9b`; the derived MQ subset identity is `subset:3:0.19.0-rc.2:aad927328c20b08c8445e8ad1792eadd8ecc3466:8e0eb8909b9a110b86398ed3f1a87d262b0691ddccdf63e7d49689a864556b71`.

Official API2 installed the selected managed bytes. After the owner's approval of nine URL-only repairs in target rule authority (raw SHA-256 `e46c6527b6cb7bf9cd9ef5c3cb19c0f9e36c38dd8ecdeda546c5c273b87d4c08`), an official rederived MQ subset and paired API2 plan/apply updated `.ai/framework.lock` (raw SHA-256 `be0cba5c82425c1fc67755b65b7956c6333d8205f637f4cb3e48e6c45f907223`) and `.ai/custom/installation.json` (raw SHA-256 `4d74012367bd1ec4a5aedb2ed7b923880c315dd7492d32559be88f101af3a5a3`). Rebind apply reported one changed project selection and 384 unchanged managed files, `managed-bytes-consistent`, matching protected inputs and `project_readiness: not-assessed`. Static read-back found both operation markers absent and the persistent writer guard regular and empty. These are installation and static observations, not target behavioral or admission validation.

## Selected shape

- Select all eighteen skill packages, `engineering-common` and `dotnet-backend` knowledge, and both `codex` and `claude` adapters.
- Use Selection v2 `skill_naming: original`. Runtime entry directory, declared name and heading use each canonical skill ID. Old `framework-*` entries and legacy `ai-context-init/upgrader` wrappers have been retired.
- Keep `.ai/custom/framework.json` as the explicit project operation settings for its seven configured skills. Do not discover or rewrite it implicitly. `.ai/custom/installation.json` is the project-owned desired selection; `.ai/framework.lock` is installer-owned observed installation identity.
- Use official RC2 plan/apply for managed package, runtime and lock writes. Do not hand-write a lock, fabricate a receipt or infer target adoption from package availability.

## Target decisions that survive replacement

[Target engineering rules](TARGET-ENGINEERING-RULES.md) retain fourteen complete rule statements, their target predicates, twenty .NET request routes, four customizations and target Git cutovers. The installation selection must bind normative `engineering-common` and `dotnet-backend` resources to that exact target-owned authority and actual applicable project facts. Empty `bindings` would make knowledge available without adopted normative coverage. A binding hash detects drift; it is not an approval or pass. The source package's examples and templates do not change target product decisions.

Inventory uses EF Core/Npgsql; Products and Orders remain Dapper. Orders selects event sourcing. Procurement is a fourth business context; supplier systems and two frontends are current project facts. Use `.dev/ARCHITECTURE.md`, `.dev/project-config.yaml`, relevant operations, source, tests and Compose to confirm details. The project-owned seven skill operation stores in `.ai/custom/framework.json` remain separate from knowledge adoption. Existing records retain their own formats; installing a skill does not migrate them.

## Execution and validation status

The owner authorized a **one-time exception for this RC2 adoption**: skip S6, runtime and upgrade/recovery experiments. Report each as `deferred-by-owner` and do not call static parsing, link, Git or read-back checks a behavioral pass. The previous RC1 target admission and independent review do not admit RC2. No CI restoration is authorized. Current target-local automated commit validation is unconfigured after retirement of the RC1 pinned validator; the planned Issue #22 commit message receives only the coordinator-selected source validator check against its exact message file.

The target's Issue-first authorization, workflow and Git policies, LF and scoped runtime metadata rules, actual AI provenance, and unique historical trailer exception remain in force. Independent review, target acceptance, hosted contexts, push, PR, merge, Issue closure, tag and publication are separate observations. Keep every failed, blocked, deferred and not-applicable state truthful.

Historical RC1 workflows and delivery reports, where retained, document earlier observations only. Current route/discovery, selection, lock and acceptance must be read from the final installed files and this target's live evidence.
