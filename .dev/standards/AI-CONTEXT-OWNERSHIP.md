# AI Context Rule Ownership

Related portable baseline contract: `ENG-IDENTITY-001`.

This standard assigns canonical ownership classifications to selected
AI-context engineering identities and defines how consumers resolve them
without creating a second semantic owner.

## Ownership Model

- `.ai/core/knowledge/engineering-common/` owns portable cross-technology framework baseline
  concepts, rules, constraints, and abstract enforcement capabilities.
- `.ai/core/knowledge/<profile>/` owns portable profile-specific defaults,
  rules, constraints, technology bindings, and bundled tooling. The canonical
  .NET binding contract is
  `.ai/core/knowledge/dotnet-backend/references/ENGINEERING-IDENTITY-BINDINGS.MD`.
- `.dev/standards/` owns source governance, rule strength and applicability
  policy, ownership classification, and the identity registry. A current
  registry record with a legacy `canonical_path` under `.dev/standards/` is
  `transitional-unmigrated` until the migration matrix reclassifies it; this
  does not make `.dev/standards/` the blanket future owner for framework
  semantics.
- `.dev/ai-context/` is target-owned effective state shared by humans and
  agents. It records adopted state, semantic deltas, target selections, tuning,
  waivers, provenance, and reconciliation evidence; it may select or change a
  declared decision slot but cannot silently remove an invariant.
- Skills own workflow behavior and output contracts, not the engineering
  semantics they consume.
- Runtime wrappers, checklists, examples, workflow records, analyzers,
  validators, providers, Diagnostics, commands, and target configuration are
  derived consumers or enforcement mechanisms. They never become normative
  semantic owners through repetition or activation.
- The selected target rules, full statements, strengths, and applicable
  customizations are recorded in `.dev/ai-context/TARGET-ENGINEERING-RULES.md`.
  The official installation selection binds their IDs to the selected
  knowledge packages and this target authority. An unresolved identity or
  authority binding fails closed.

## Governance Term Routing

The governance term routes below are an owner route index, not a glossary or
second definition authority. A consumer uses the qualified term on first use,
follows the declared canonical owner, and may use the listed shorthand only
inside the same clearly qualified section.

| Namespace | Qualified terms | Definition owner |
| --- | --- | --- |
| `source-release` | framework version candidate; release-source status validated; historical/exception release closeout | source-only release policy or closeout capability |
| `distribution` | package candidate | source-only distribution contract |
| `target-upgrade` | target upgrade `automatic-candidate` | `ai-context-upgrader` planning contract |
| `git` | repository integration | `.dev/TEAM-GIT-FLOW-RULES.MD` |
| `workflow` | workflow completion | `WORKFLOW-ARTIFACT-POLICY.md` |
| `assessment` | assessment final | `ASSESSMENT-ARTIFACT-POLICY.md` |
| `hosted-release` | hosted publication | source-only release policy |
| `source-release-validation` | framework candidate, tag, publication, and finalization validation phases | source-only release policy and version-owned phase contract |
| `governance` | governed subject lifecycle | the policy that owns the explicitly named subject |
| `capability-selection` | subject-qualified skill/provider/capability candidate | the selected subject's canonical contract |

The following separations are invariant routing rules:

- conceptual state, machine status, validation phase, migration category, and
  hosted/provider state are never interchangeable;
- repository integration is not workflow completion, assessment finality,
  source validation, or hosted publication;
- `automatic-candidate` is a target-upgrade classification and never write
  authorization;
- `candidate`, `validated`, `published`, `closeout`, `finalization`, or
  `lifecycle` without an explicit subject cannot establish an authority claim;
- existing machine literals remain unchanged until an explicit versioned
  migration says otherwise; and
- historical records retain their original wording.

Rows marked `source-only` remain non-actionable upstream context in a target
package. Portable consumers must not follow them as target procedures. The
portable version/provenance/upgrade owner deliberately excludes source release
commands, release records, tag operations, hosted credentials, and provider
mutation.

## Rule Catalogs

- `.ai/core/knowledge/engineering-common/engineering-rule-catalog.yaml` is the canonical
  portable baseline for the registered universal rules. Its complete normative
  text is an LF-normalized anchored extraction, while the source-governance
  section remains provenance and governance evidence.
- `.ai/core/knowledge/<profile>/engineering-rule-catalog.yaml` is a
  resolver-ready exact projection. For profile rules, the moved profile Markdown
  path and anchor remain the single semantic owner; the catalog is not a second
  owner and retains the exact source section, hashes, and stable selector.
- Catalogs preserve existing identities. They do not allocate a path-derived
  rule or constraint ID. A migrated profile-baseline document without a stable
  ID is explicitly `identity-allocation-required` and must remain unpacketized.
- A routine consumer selects records by stable ID from the selected catalog
  and freshness-validated target authority binding. It does not scan a directory of Markdown files
  to reconstruct semantics.

## Identity Model

The registry distinguishes these kinds. Existing `rule_id` values remain
stable; the model does not require a bulk renaming migration.

| Kind | Field and stable form | Canonical owner | Required relationships |
| --- | --- | --- | --- |
| Engineering concept | `concept_id`: `CONCEPT-...` | cross-technology baseline record under `.ai/core/knowledge/engineering-common/` | may support one or more rules |
| Normative rule | `rule_id`: existing registered format or new `RULE-...` | classified baseline record under `.ai/core/knowledge/engineering-common/` or `.ai/core/knowledge/<profile>/` | references one or more concepts; may yield constraints |
| Observable constraint | `constraint_id`: `CONSTRAINT-...` | classified baseline record under `.ai/core/knowledge/engineering-common/` or `.ai/core/knowledge/<profile>/` | references a rule; may be enforced by capabilities and bindings |
| Abstract enforcement capability | `capability_id`: `CAPABILITY-...` | cross-technology baseline capability record under `.ai/core/knowledge/engineering-common/` | may enforce one or more constraints |
| Technology binding | `binding_id`: `BINDING-...` | selected profile record under `.ai/core/knowledge/<profile>/` | references exactly one constraint and capability; may name provider or Diagnostic details |

Concepts, rules, and constraints are semantic subjects. Abstract capabilities
and technology bindings are enforcement records: they can be changed for a
selected profile without being treated as a semantic customization when the
engineering meaning is unchanged. A target's semantic customization therefore
names a concept, rule, or constraint; enforcement tuning or a tooling waiver
names the affected constraint plus its capability/binding evidence.

## Referential Integrity

- A reference has an explicit `kind` and `id`; a bare path, Diagnostic ID,
  package name, command, or provider name is never a semantic reference.
- A referenced ID must resolve to exactly one registered record of the declared
  kind. Duplicate IDs across kinds, missing records, type-invalid edges,
  self-references, and path-derived identities are unresolved.
- A consumer that receives an unresolved identity, missing target-effective
  state, stale digest, or incompatible profile must fail closed and report the
  reason. It must not select a similarly named default or silently use the
  framework baseline.
- An identity remains stable across relocations, projection rewrites,
  provider swaps, Diagnostic changes, and package upgrades. A semantic change
  requires an explicit owner-approved `supersedes` relationship; compatibility
  and migration records reference the existing identity rather than creating a
  temporary alternate ID.
- The selected knowledge catalog and installation bindings resolve the
  canonical baseline path, selector, and target authority for each adopted
  rule. Consumers cite the same stable ID; no alternate normative statement
  is implied. Missing or stale binding evidence remains unresolved.

## Rule Strength

| Strength | Meaning | Override policy |
| --- | --- | --- |
| `invariant` | Framework minimum that remains active for every adopting target. | Forbidden; a conflict must be reported as a waiver request. |
| `profile-default` | Default selected by an adopted profile. | May change only through explicit target-repository evidence. |
| `conditional` | Active only when its declared applicability predicate is satisfied. | Becomes not applicable when the predicate is false. |
| `example` | Illustrative material with no normative force. | Not applicable. |
| `historical` | Retained provenance that is not active guidance. | Not applicable. |

Do not use an unqualified `mandatory` or `default` when the applicable strength is not clear.

## Precedence

1. User approval and the applicable `AGENTS.md` procedural instructions.
2. Explicit target-repository facts and decisions for declared decision slots.
3. Framework `invariant` rules. Target conflicts are reported; they are not silent overrides.
4. Adopted `profile-default` rules.
5. Applicable `conditional` rules.
6. Derived projections of a canonical baseline, runtime wrappers, and checklists.
7. Examples.
8. Historical records.

Target evidence may select technologies or replace a profile default. It cannot silently remove a framework invariant.

Technology defaults and overrides use
[Target Technology Selection Policy](TECHNOLOGY-SELECTION-POLICY.md) and one
generic target-owned selection record. Do not invent a separate override
mechanism for each package family.

## Consumer Contract

Every registered derived consumer must:

- identify the canonical rule with `Rule IDs:` or an equivalent explicit source declaration;
- link to the selected knowledge owner and target authority binding instead of independently redefining ownership;
- preserve the registered strength and applicability when it summarizes the rule;
- keep examples clearly illustrative.

A selected-rule consumer uses the catalog record and target authority binding;
it does not treat a derived consumer, copied summary, or a directory scan as a
competing normative source.

The validator selected by `.dev/project-config.yaml#validation.current_framework.local` must check selected binding and catalog structure, paths, anchors, IDs, strength/override compatibility, applicability, and declared consumer references. While it is `unconfigured`, this check is blocked and cannot be reported as passed. Semantic parity remains a review responsibility.
