#!/usr/bin/env python3
"""Validate the downstream-applicable v0.13 code-review routing contract."""

from __future__ import annotations

import fnmatch
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
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
    for route in sorted(
        routes.values(), key=lambda item: item["priority"], reverse=True
    ):
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
        for finding in route.get("finding_rules", [])
        if finding["finding_tag"] in finding_tags
        for rule_id in finding.get("rule_ids", [])
    }


def expanded_references(manifest_path: Path) -> set[Path]:
    manifest = load_yaml(manifest_path)
    return {manifest_path, *(Path(path) for path in manifest["references"])}


def total_bytes(paths: set[Path]) -> int:
    missing = [str(path) for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"declared reference paths are missing: {missing}")
    return sum((ROOT / path).stat().st_size for path in paths)


class CodeReviewerRoutingProjectionTests(unittest.TestCase):
    def test_gwt_001_required_routes_and_references_are_complete(self) -> None:
        routes = route_map()
        self.assertEqual(
            {
                "aggregate", "domain-event", "entity", "value-object",
                "use-case", "handler", "repository", "controller", "mapper",
                "projection", "reactor", "outbox", "test", "general-csharp",
            },
            set(routes),
        )
        self.assertEqual(1, routes["general-csharp"]["priority"])
        for route_id, route in routes.items():
            with self.subTest(route_id=route_id):
                self.assertTrue(route["canonical_references"])
                for reference in route["canonical_references"]:
                    self.assertTrue((ROOT / reference).is_file(), reference)

    def test_gwt_002_routed_rules_bind_to_catalog_consumers(self) -> None:
        routing = load_yaml(ROUTING_PATH)
        catalog = load_yaml(CATALOG_PATH)
        catalog_rules = {rule["rule_id"]: rule for rule in catalog["rules"]}
        routed = {
            rule_id
            for route in routing["routes"]
            for finding in route.get("finding_rules", [])
            for rule_id in finding.get("rule_ids", [])
        }
        self.assertTrue(routed)
        self.assertTrue(routed.issubset(catalog_rules))
        routing_path = str(ROUTING_PATH).replace("\\", "/")
        for rule_id in routed:
            with self.subTest(rule_id=rule_id):
                self.assertIn(
                    routing_path,
                    catalog_rules[rule_id]["derived_consumers"],
                )

    def test_gwt_003_acceptance_fixtures_select_expected_routes_and_rules(self) -> None:
        routes = route_map()
        for case in load_yaml(FIXTURE_PATH)["cases"]:
            with self.subTest(case_id=case["case_id"]):
                route_id = select_route(case, routes)
                self.assertEqual(case["expected_route"], route_id)
                rules = selected_rule_ids(routes[route_id], case["finding_tags"])
                self.assertEqual(set(case["expected_rule_ids"]), rules)
                self.assertTrue(
                    set(case.get("forbidden_rule_ids", [])).isdisjoint(rules)
                )

        guardrails = " ".join(
            item["statement"]
            for item in load_yaml(ROUTING_PATH)["semantic_guardrails"]
        ).lower()
        self.assertIn("do not reject a repository interface merely", guardrails)
        self.assertIn("only when", guardrails)

    def test_gwt_004_skill_wrappers_and_root_guides_use_compact_entry(self) -> None:
        skill = load_yaml(SKILL_PATH)
        routing_path = str(ROUTING_PATH).replace("\\", "/")
        self.assertEqual({routing_path}, set(skill["references"]))
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
        self.assertTrue(all(phase["load_when"] for phase in phase_references.values()))

        for wrapper in (
            Path(".agents/skills/code-reviewer/SKILL.md"),
            Path(".claude/skills/code-reviewer/SKILL.md"),
        ):
            text = (ROOT / wrapper).read_text(encoding="utf-8")
            with self.subTest(wrapper=str(wrapper)):
                self.assertIn(routing_path, text)
                for forbidden in FORBIDDEN_STATIC_REFERENCES:
                    self.assertNotIn(forbidden, text)

        for guide in (Path("AGENTS.md"), Path("AGENTS.zh-TW.md")):
            text = (ROOT / guide).read_text(encoding="utf-8")
            with self.subTest(guide=str(guide)):
                self.assertIn(routing_path, text)
                self.assertNotIn(
                    ".ai/assets/tech-stacks/dotnet-backend/references/"
                    "CODE-REVIEW-INDEX.MD",
                    text,
                )

    def test_gwt_005_review_roles_do_not_require_shared_rule_bundles(self) -> None:
        route_ids = set(route_map())
        routing_path = str(ROUTING_PATH).replace("\\", "/")
        for role_name, role_path in ROLE_PATHS.items():
            manifest = load_yaml(role_path)
            references = set(manifest["references"])
            with self.subTest(role=role_name):
                self.assertTrue(FORBIDDEN_STATIC_REFERENCES.isdisjoint(references))
                self.assertIn(routing_path, references)
                self.assertEqual(
                    "selected-route-only",
                    manifest["routing"]["reference_loading"],
                )
                self.assertTrue(
                    set(manifest["routing"]["supported_route_ids"]).issubset(
                        route_ids
                    )
                )

    def test_gwt_006_compatibility_entries_route_without_duplicate_doctrine(self) -> None:
        routing = load_yaml(ROUTING_PATH)
        self.assertEqual("v0.13.x", routing["compatibility"]["migration_window"])
        for entry in routing["compatibility"]["entries"]:
            path = ROOT / entry
            text = path.read_text(encoding="utf-8")
            with self.subTest(entry=entry):
                self.assertIn("review-routing.yaml", text)
                self.assertIn("v0.13.x", text)
                self.assertLess(path.stat().st_size, 1_500)

    def test_gwt_007_route_reference_graph_is_smaller_than_baseline(self) -> None:
        wrapper = Path(".agents/skills/code-reviewer/SKILL.md")
        skill = load_yaml(SKILL_PATH)
        top_level = {
            wrapper,
            SKILL_PATH,
            *(Path(path) for path in skill["references"]),
        }
        routes = route_map()
        general_role = expanded_references(ROLE_PATHS["general"])
        measured = {
            "top-level": total_bytes(top_level),
            "general": total_bytes(
                top_level
                | general_role
                | {
                    Path(path)
                    for path in routes["general-csharp"]["canonical_references"]
                }
            ),
        }
        for role_name in ("aggregate", "controller", "reactor"):
            measured[role_name] = total_bytes(
                top_level
                | general_role
                | expanded_references(ROLE_PATHS[role_name])
                | {
                    Path(path)
                    for path in routes[role_name]["canonical_references"]
                }
            )

        for route_name, size in measured.items():
            with self.subTest(route=route_name):
                self.assertLess(size, BASELINE_BYTES[route_name])


if __name__ == "__main__":
    unittest.main()
