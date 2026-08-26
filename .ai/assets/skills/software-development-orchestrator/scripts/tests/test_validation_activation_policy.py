#!/usr/bin/env python3
"""GWT checks for the portable routine-validation activation contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[6]
PROFILE = ROOT / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"
TEMPLATE = ROOT / ".ai/assets/skills/ai-context-init/templates/project-config.template.yaml"
GITIGNORE = ROOT / ".gitignore"


class ValidationActivationPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))["orchestration_contract"]["routine_validation"]
        self.template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_gwt_001_given_template_when_read_then_defaults_are_manual_and_unconfigured(self) -> None:
        self.assertEqual("manual", self.template["validation"]["routine"]["local"]["mode"])
        self.assertEqual("unconfigured", self.template["validation"]["routine"]["ci"]["mode"])

    def test_gwt_002_given_policy_when_read_then_local_is_strict_and_monotonic(self) -> None:
        self.assertEqual(["manual", "auto-if-ready", "required"], self.profile["local_modes"])
        self.assertTrue(self.profile["local_opt_in_can_only_strengthen"])
        self.assertEqual("prohibited", self.profile["environment_override"])
        self.assertEqual("prohibited", self.profile["implicit_local_write"])
        self.assertIn("/.dev/validation.local.conf", GITIGNORE.read_text(encoding="utf-8"))

    def test_gwt_003_given_unselected_or_required_ci_when_projected_then_it_never_becomes_passed(self) -> None:
        self.assertEqual({"outcome": "not-applicable", "selection_reason": "not-run-by-policy"}, self.profile["unselected_projection"])
        self.assertEqual(["unconfigured", "advisory", "required"], self.profile["ci_modes"])
        self.assertEqual(0, self.profile["attempt_budget"]["unselected"])
        self.assertEqual(1, self.profile["attempt_budget"]["retry_after_material_change"])


if __name__ == "__main__":
    unittest.main()
