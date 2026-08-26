#!/usr/bin/env python3
"""Fail-closed contracts for Code Reviewer progressive reference loading."""

from __future__ import annotations

import fnmatch
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
import ai_context_package as PACKAGE  # noqa: E402

ROUTING_PATH = Path(
    ".ai/assets/skills/code-reviewer/references/review-routing.yaml"
)
FIXTURE_PATH = Path(
    ".ai/assets/skills/code-reviewer/fixtures/review-routing-fixtures.yaml"
)
SKILL_PATH = Path(".ai/assets/skills/code-reviewer/skill.yaml")
CATALOG_PATH = Path(
    ".ai/assets/tech-stacks/dotnet-backend/engineering-rule-catalog.yaml"
)

ROLE_PATHS = {
    "general": Path(
        ".ai/assets/sub-agent-role-prompts/code-review-sub-agent/sub-agent.yaml"
    ),
    "aggregate": Path(
        ".ai/assets/sub-agent-role-prompts/aggregate-code-review-sub-agent/sub-agent.yaml"
    ),
    "controller": Path(
        ".ai/assets/sub-agent-role-prompts/controller-code-review-sub-agent/sub-agent.yaml"
    ),
    "reactor": Path(
        ".ai/assets/sub-agent-role-prompts/reactor-code-review-sub-agent/sub-agent.yaml"
    ),
}

BASELINE_BYTES = {
    "top-level": 43_747,
    "general": 65_017,
    "aggregate": 71_120,
    "controller": 68_332,
    "reactor": 68_497,
}

FORBIDDEN_STATIC_REFERENCES = {
    ".ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD",
    ".ai/assets/skills/code-reviewer/references/checklist-reference.md",
    ".ai/assets/tech-stacks/dotnet-backend/standards/CODE-REVIEW-CHECKLIST.md",
    ".ai/assets/tech-stacks/dotnet-backend/shared/code-review-checklist.md",
    ".ai/assets/tech-stacks/dotnet-backend/shared/common-rules.md",
    ".ai/assets/tech-stacks/dotnet-backend/shared/testing-strategy.md",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def route_map() -> dict[str, dict]:
    return {
        route["route_id"]: route
        for route in load_yaml(ROUTING_PATH)["routes"]
    }


def matches(value: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(value.replace("\\", "/"), pattern)


def select_route(case: dict, routes: dict[str, dict]) -> str:
    ordered = sorted(
        routes.values(), key=lambda route: route["priority"], reverse=True
    )
    for route in ordered:
        selectors = route["selectors"]
        path_match = any(
            matches(case["path"], pattern)
            for pattern in selectors.get("path_globs", [])
        )
        type_match = any(
            matches(actual, pattern)
            for actual in case.get("type_signals", [])
            for pattern in selectors.get("type_signals", [])
        )
        if path_match or type_match:
            return route["route_id"]
    raise AssertionError(f"no review route matched fixture {case['case_id']}")


def selected_rule_ids(route: dict, finding_tags: list[str]) -> set[str]:
    return {
        rule_id
        for rule in route.get("finding_rules", [])
        if rule["finding_tag"] in finding_tags
        for rule_id in rule.get("rule_ids", [])
    }


def expand_manifest_references(manifest_path: Path) -> set[Path]:
    manifest = load_yaml(manifest_path)
    return {manifest_path, *(Path(path) for path in manifest["references"])}


def total_bytes(paths: set[Path]) -> int:
    missing = [str(path) for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"declared reference paths are missing: {missing}")
    return sum((ROOT / path).stat().st_size for path in paths)


class CodeReviewerRoutingContractTests(unittest.TestCase):
    def test_gwt_001_given_routing_contract_when_loaded_then_required_routes_are_complete(self) -> None:
        routes = route_map()
        self.assertEqual(
            {
                "aggregate",
                "domain-event",
                "entity",
                "value-object",
                "use-case",
                "handler",
                "repository",
                "controller",
                "mapper",
                "projection",
                "reactor",
                "outbox",
                "test",
                "general-csharp",
            },
            set(routes),
        )
        self.assertEqual(1, routes["general-csharp"]["priority"])
        for route_id, route in routes.items():
            with self.subTest(route_id=route_id):
                self.assertTrue(route["canonical_references"])
                for reference in route["canonical_references"]:
                    self.assertTrue((ROOT / reference).is_file(), reference)

    def test_gwt_002_given_rule_ids_when_routed_then_catalog_identity_and_consumers_match(self) -> None:
        routing = load_yaml(ROUTING_PATH)
        catalog = load_yaml(CATALOG_PATH)
        catalog_rules = {rule["rule_id"]: rule for rule in catalog["rules"]}
        routed_rule_ids = {
            rule_id
            for route in routing["routes"]
            for finding in route.get("finding_rules", [])
            for rule_id in finding.get("rule_ids", [])
        }
        self.assertTrue(routed_rule_ids)
        self.assertTrue(routed_rule_ids.issubset(catalog_rules))
        for rule_id in routed_rule_ids:
            with self.subTest(rule_id=rule_id):
                self.assertIn(
                    str(ROUTING_PATH).replace("\\", "/"),
                    catalog_rules[rule_id]["derived_consumers"],
                )

    def test_gwt_003_given_acceptance_fixtures_when_selected_then_routes_and_rules_do_not_drift(self) -> None:
        routes = route_map()
        fixtures = load_yaml(FIXTURE_PATH)["cases"]
        for case in fixtures:
            with self.subTest(case_id=case["case_id"]):
                route_id = select_route(case, routes)
                self.assertEqual(case["expected_route"], route_id)
                rules = selected_rule_ids(routes[route_id], case["finding_tags"])
                self.assertEqual(set(case["expected_rule_ids"]), rules)
                self.assertTrue(
                    set(case.get("forbidden_rule_ids", [])).isdisjoint(rules)
                )

        guardrail_text = " ".join(
            item["statement"]
            for item in load_yaml(ROUTING_PATH)["semantic_guardrails"]
        ).lower()
        self.assertIn("do not reject a repository interface merely", guardrail_text)
        self.assertIn("only when", guardrail_text)

    def test_gwt_004_given_skill_and_wrappers_when_read_then_only_compact_entry_references_are_eager(self) -> None:
        skill = load_yaml(SKILL_PATH)
        expected = {
            str(ROUTING_PATH).replace("\\", "/"),
        }
        self.assertEqual(expected, set(skill["references"]))
        self.assertTrue(FORBIDDEN_STATIC_REFERENCES.isdisjoint(skill["references"]))

        phase_references = load_yaml(ROUTING_PATH)["phase_references"]
        self.assertEqual(
            {
                ".ai/assets/skills/code-reviewer/references/role-execution.md",
                ".ai/assets/skills/code-reviewer/references/output-contract.md",
            },
            {
                reference
                for phase in phase_references.values()
                for reference in phase["references"]
            },
        )
        self.assertTrue(
            all(phase["load_when"] for phase in phase_references.values())
        )

        for wrapper in (
            Path(".agents/skills/code-reviewer/SKILL.md"),
            Path(".claude/skills/code-reviewer/SKILL.md"),
        ):
            text = (ROOT / wrapper).read_text(encoding="utf-8")
            with self.subTest(wrapper=str(wrapper)):
                self.assertIn(str(ROUTING_PATH).replace("\\", "/"), text)
                for forbidden in FORBIDDEN_STATIC_REFERENCES:
                    self.assertNotIn(forbidden, text)

        for root_guide in (Path("AGENTS.md"), Path("AGENTS.zh-TW.md")):
            text = (ROOT / root_guide).read_text(encoding="utf-8")
            with self.subTest(root_guide=str(root_guide)):
                self.assertIn(str(ROUTING_PATH).replace("\\", "/"), text)
                self.assertNotIn(
                    ".ai/assets/tech-stacks/dotnet-backend/references/CODE-REVIEW-INDEX.MD",
                    text,
                )

    def test_gwt_005_given_review_roles_when_loaded_then_shared_rule_bundles_are_not_mandatory(self) -> None:
        route_ids = set(route_map())
        for role_name, role_path in ROLE_PATHS.items():
            manifest = load_yaml(role_path)
            references = set(manifest["references"])
            with self.subTest(role=role_name):
                self.assertTrue(FORBIDDEN_STATIC_REFERENCES.isdisjoint(references))
                self.assertIn(str(ROUTING_PATH).replace("\\", "/"), references)
                self.assertEqual("selected-route-only", manifest["routing"]["reference_loading"])
                self.assertTrue(
                    set(manifest["routing"]["supported_route_ids"]).issubset(
                        route_ids
                    )
                )

    def test_gwt_006_given_compatibility_entries_when_read_then_they_route_without_duplicate_doctrine(self) -> None:
        entries = load_yaml(ROUTING_PATH)["compatibility"]["entries"]
        self.assertEqual("v0.13.x", load_yaml(ROUTING_PATH)["compatibility"]["migration_window"])
        for entry in entries:
            path = Path(entry)
            text = (ROOT / path).read_text(encoding="utf-8")
            with self.subTest(entry=entry):
                self.assertIn("review-routing.yaml", text)
                self.assertIn("v0.13.x", text)
                self.assertLess((ROOT / path).stat().st_size, 1_500)

    def test_gwt_007_given_declared_reference_graph_when_measured_then_every_route_is_smaller_than_baseline(self) -> None:
        wrapper = Path(".agents/skills/code-reviewer/SKILL.md")
        skill = load_yaml(SKILL_PATH)
        top_level = {wrapper, SKILL_PATH, *(Path(path) for path in skill["references"])}
        routes = route_map()
        general_role = expand_manifest_references(ROLE_PATHS["general"])

        measured: dict[str, int] = {"top-level": total_bytes(top_level)}
        measured["general"] = total_bytes(
            top_level
            | general_role
            | {Path(path) for path in routes["general-csharp"]["canonical_references"]}
        )
        for role_name in ("aggregate", "controller", "reactor"):
            measured[role_name] = total_bytes(
                top_level
                | general_role
                | expand_manifest_references(ROLE_PATHS[role_name])
                | {
                    Path(path)
                    for path in routes[role_name]["canonical_references"]
                }
            )

        for route_name, size in measured.items():
            with self.subTest(route=route_name, measured_bytes=size):
                self.assertLess(size, BASELINE_BYTES[route_name])

    def test_gwt_008_given_committed_profile_when_projected_then_routing_and_compatibility_entries_ship(self) -> None:
        tree = PACKAGE.git_tree(ROOT, "HEAD")
        profile = yaml.safe_load(
            (
                ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"
            ).read_text(encoding="utf-8")
        )
        payload = {
            item.path: item
            for item in PACKAGE.collect_payload(ROOT, tree, profile)
        }
        required = {
            str(ROUTING_PATH).replace("\\", "/"),
            str(FIXTURE_PATH).replace("\\", "/"),
            ".ai/assets/skills/code-reviewer/skill.yaml",
            *(str(path).replace("\\", "/") for path in ROLE_PATHS.values()),
            *load_yaml(ROUTING_PATH)["compatibility"]["entries"],
        }
        self.assertTrue(required.issubset(payload))
        for entry in load_yaml(ROUTING_PATH)["compatibility"]["entries"]:
            with self.subTest(entry=entry):
                self.assertIn(b"review-routing.yaml", payload[entry].content)
                self.assertLess(len(payload[entry].content), 1_500)


if __name__ == "__main__":
    unittest.main()
