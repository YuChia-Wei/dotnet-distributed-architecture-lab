#!/usr/bin/env python3
"""Contract tests for the four-skill semantic customization lifecycle."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SHARED = (
    ".ai/assets/skills/ai-context-governance/references/"
    "semantic-customization-lifecycle.md"
)
SKILLS = (
    "ai-context-governance",
    "ai-context-auditor",
    "ai-context-upgrader",
    "ai-context-init",
)


class SemanticCustomizationSkillContractTests(unittest.TestCase):
    def test_gwt_001_given_four_canonical_skills_when_routing_is_checked_then_each_directly_references_the_shared_lifecycle(self) -> None:
        for skill in SKILLS:
            spec = yaml.safe_load(
                (
                    ROOT / f".ai/assets/skills/{skill}/skill.yaml"
                ).read_text(encoding="utf-8")
            )
            self.assertIn(SHARED, spec["references"], skill)

    def test_gwt_002_given_runtime_wrappers_when_checked_then_each_has_one_level_shared_lifecycle_routing(self) -> None:
        for runtime in (".agents", ".claude"):
            for skill in SKILLS:
                text = (
                    ROOT / runtime / "skills" / skill / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn(SHARED, text, f"{runtime}/{skill}")

    def test_gwt_003_given_upgrader_contract_when_checked_then_semantic_table_and_target_validator_are_required(self) -> None:
        output = (
            ROOT
            / ".ai/assets/skills/ai-context-upgrader/references/output-contract.md"
        ).read_text(encoding="utf-8")
        playbook = (
            ROOT
            / ".ai/assets/skills/ai-context-upgrader/references/upgrade-playbook.md"
        ).read_text(encoding="utf-8")
        self.assertIn("semantic reconciliation table", output)
        self.assertIn("validate-ai-context-target.py", playbook)
        self.assertNotIn(
            "requested `.dev/releases/<version>/release.yaml`", playbook
        )

    def test_gwt_004_given_shared_schema_when_checked_then_semantic_identity_precedes_paths_and_verification_is_fail_closed(self) -> None:
        schema = yaml.safe_load(
            (
                ROOT
                / ".ai/assets/skills/ai-context-governance/templates/customizations.schema.yaml"
            ).read_text(encoding="utf-8")
        )
        required = schema["customization"]["required"]
        self.assertLess(required.index("subject"), required.index("paths"))
        self.assertIn("reason", required)
        self.assertEqual(
            "non-empty-string",
            schema["customization"]["properties"]["reason"]["type"],
        )
        template = (
            ROOT
            / ".ai/assets/skills/ai-context-upgrader/templates/customizations-template.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '#   reason: "<why-target-behavior-differs-from-or-extends-framework>"',
            template,
        )
        self.assertEqual(
            "verified",
            schema["finalization"]["retire_or_supersede_requires"][
                "post_upgrade_audit.status"
            ],
        )

    def test_gwt_005_given_downstream_projection_when_checked_then_target_validation_remains_and_source_release_tools_do_not(self) -> None:
        profile = yaml.safe_load(
            (
                ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"
            ).read_text(encoding="utf-8")
        )
        excluded = {
            pattern
            for group in profile["exclusions"]
            for pattern in group["patterns"]
        }
        self.assertIn(
            ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
            excluded,
        )
        self.assertIn(".ai/scripts/validate-ai-context-versions.py", excluded)
        self.assertNotIn(".ai/scripts/validate-ai-context-target.py", excluded)
        self.assertNotIn(".ai/scripts/ai_context_target_provenance.py", excluded)


if __name__ == "__main__":
    unittest.main()
