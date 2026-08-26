#!/usr/bin/env python3
"""Validate the target-owned v0.9 effective-rule decision candidate."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
DECISIONS_PATH = (
    ROOT
    / ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/evidence/v0.9.0/"
    "effective-rule-decisions.yaml"
)


def route_id(selector: dict[str, str]) -> str:
    payload = json.dumps(
        selector,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload = (payload + "\n").encode("utf-8")
    return "ROUTE-" + hashlib.sha256(payload).hexdigest().upper()


class EffectiveRuleDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = yaml.safe_load(DECISIONS_PATH.read_text(encoding="utf-8"))
        cls.candidate = cls.document["state_candidate"]

    def test_gwt_001_all_thirteen_catalog_rules_have_explicit_verified_baselines(self) -> None:
        dispositions = self.candidate["rule_dispositions"]
        self.assertEqual(13, len(dispositions))
        self.assertEqual(
            sorted(item["rule_id"] for item in dispositions),
            [item["rule_id"] for item in dispositions],
        )
        for disposition in dispositions:
            with self.subTest(rule_id=disposition["rule_id"]):
                self.assertEqual("baseline-effective", disposition["effective_disposition"])
                self.assertTrue(disposition["baseline_acceptance"]["explicit"])
                self.assertEqual(
                    "verified",
                    disposition["baseline_acceptance"]["verification"]["status"],
                )
                for evidence in disposition["evidence"]:
                    self.assertTrue((ROOT / evidence).exists(), evidence)

    def test_gwt_002_twenty_exact_routes_have_digest_ids_and_complete_rule_sets(self) -> None:
        routes = self.candidate["routing"]
        rule_ids = sorted(
            disposition["rule_id"]
            for disposition in self.candidate["rule_dispositions"]
        )
        self.assertEqual(20, len(routes))
        self.assertEqual(
            sorted(route["route_id"] for route in routes),
            [route["route_id"] for route in routes],
        )
        selectors: set[tuple[str, str, str, str]] = set()
        for route in routes:
            selector = route["selector"]
            with self.subTest(route_id=route["route_id"]):
                self.assertEqual(route_id(selector), route["route_id"])
                self.assertEqual(rule_ids, route["required_rule_ids"])
                self.assertEqual([], route["reported_not_applicable_rule_ids"])
                key = (
                    selector["capability"],
                    selector["execution_mode"],
                    selector["technology_profile"],
                    selector["file_type"],
                )
                self.assertNotIn(key, selectors)
                selectors.add(key)

    def test_gwt_003_bddfy_and_physical_delete_choices_are_not_hidden_as_exceptions(self) -> None:
        dispositions = {
            item["rule_id"]: item for item in self.candidate["rule_dispositions"]
        }
        self.assertEqual(
            "baseline-effective",
            dispositions["TEST-BDDFY-001"]["effective_disposition"],
        )
        self.assertEqual(
            "baseline-effective",
            dispositions["DELETE-PURGE-001"]["effective_disposition"],
        )
        self.assertIn(
            "plain xUnit",
            self.document["technology_decisions"]["testing_bdd_runner"],
        )


if __name__ == "__main__":
    unittest.main()
