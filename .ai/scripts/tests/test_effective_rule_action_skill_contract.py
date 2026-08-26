#!/usr/bin/env python3
"""Contract tests for canonical action-skill effective-rule consumption."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SKILLS = (
    "software-development-orchestrator",
    "requirement-author",
    "spec-author",
    "problem-frame-author",
    "ddd-ca-hex-architect",
    "bdd-gwt-test-designer",
    "slice-implementer",
    "local-change-implementer",
    "code-reviewer",
    "spec-compliance-validator",
)
SECTION_KEYS = (
    "applies_when",
    "excludes",
    "resolver",
    "selectors",
    "unresolved_outcome",
    "consumption_order",
    "evidence",
    "semantic_consistency",
    "prohibitions",
)
SELECTORS = (
    "capability",
    "execution_mode",
    "technology_profile",
    "file_type",
)
EVIDENCE = (
    "resolver_outcome",
    "loaded_rule_ids",
    "baseline.framework_version",
    "target_state.digest",
    "request.capability",
    "request.execution_mode",
    "request.technology_profile",
    "request.file_type",
)
SEMANTIC_CONSISTENCY = {
    "identity": "rule_id",
    "statement_bytes": "exact UTF-8 rules[].normative_statement bytes",
    "statement_digest": "rules[].normative_statement_digest",
    "cross_consumer_requirement": (
        "the same rule_id must resolve to byte-equivalent effective semantics "
        "across consumers"
    ),
    "default_mismatch_outcome": "warning",
    "stricter_policy_owner": "target-owned",
}
PROHIBITIONS = (
    "Do not scan broad target or framework documents to discover rule semantics.",
    "Do not fall back to framework defaults.",
    "Do not select an alternate route when the exact request route is unresolved.",
    "Do not compare analyzer output as effective-rule semantics.",
    "Keep analyzer severity and warnings-as-errors separate and target-owned.",
)
CONSUMPTION_ORDER = (
    "Consume a freshness-verified task-scoped packet before reading profile "
    "references needed for the applicable action."
)


class EffectiveRuleActionSkillContractTests(unittest.TestCase):
    def spec_path(self, skill: str) -> Path:
        return ROOT / ".ai/assets/skills" / skill / "skill.yaml"

    def read_spec(self, skill: str) -> dict:
        return yaml.safe_load(self.spec_path(skill).read_text(encoding="utf-8"))

    def test_gwt_001_given_canonical_skill_specs_when_effective_rule_consumers_are_discovered_then_they_match_the_exact_action_allowlist(self) -> None:
        consumers = {
            path.parent.name
            for path in (ROOT / ".ai/assets/skills").glob("*/skill.yaml")
            if "effective_rule_consumption"
            in yaml.safe_load(path.read_text(encoding="utf-8"))
        }

        self.assertEqual(set(SKILLS), consumers)

    def test_gwt_002_given_an_allowlisted_action_skill_when_its_contract_is_read_then_the_common_packet_and_evidence_shape_is_exact(self) -> None:
        for skill in SKILLS:
            with self.subTest(skill=skill):
                contract = self.read_spec(skill)["effective_rule_consumption"]

                self.assertEqual(SECTION_KEYS, tuple(contract))
                self.assertIsInstance(contract["applies_when"], list)
                self.assertTrue(contract["applies_when"])
                self.assertIsInstance(contract["excludes"], list)
                self.assertTrue(contract["excludes"])
                self.assertEqual(
                    ".ai/scripts/resolve-effective-rule-packet.py",
                    contract["resolver"],
                )
                self.assertEqual(SELECTORS, tuple(contract["selectors"]))
                self.assertEqual("stop-applicable-action", contract["unresolved_outcome"])
                self.assertEqual(CONSUMPTION_ORDER, contract["consumption_order"])
                self.assertEqual(EVIDENCE, tuple(contract["evidence"]["required"]))
                self.assertEqual(
                    SEMANTIC_CONSISTENCY,
                    contract["semantic_consistency"],
                )
                self.assertEqual(PROHIBITIONS, tuple(contract["prohibitions"]))

    def test_gwt_003_given_the_canonical_schema_when_effective_rule_consumption_is_described_then_packet_identity_and_analyzer_separation_remain_explicit(self) -> None:
        schema = (ROOT / ".ai/assets/CANONICAL-SCHEMA.MD").read_text(
            encoding="utf-8"
        )

        self.assertIn("## Effective Rule Consumption", schema)
        self.assertIn("`.ai/scripts/resolve-effective-rule-packet.py`", schema)
        self.assertIn("`rules[].normative_statement` bytes", schema)
        self.assertIn("`rules[].normative_statement_digest`", schema)
        self.assertIn("analyzer severity and warnings-as-errors", schema)


if __name__ == "__main__":
    unittest.main()
