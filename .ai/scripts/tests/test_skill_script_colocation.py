#!/usr/bin/env python3
"""Regression tests for canonical skill-owned script placement."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


class SkillScriptColocationTests(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_gwt_001_given_single_owner_scripts_when_inventory_is_checked_then_canonical_files_are_colocated(self) -> None:
        canonical_paths = (
            ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
            ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
            ".ai/assets/skills/software-development-orchestrator/scripts/tests/test_software_development_orchestrator_acceptance.py",
            ".ai/assets/skills/software-development-orchestrator/scripts/tests/test_software_development_orchestrator_capability_contract.py",
            ".ai/assets/skills/software-development-orchestrator/scripts/tests/test_workflow_implementation_contract.py",
        )

        for path in canonical_paths:
            with self.subTest(path=path):
                self.assertTrue((REPO_ROOT / path).is_file())

        self.assertFalse((REPO_ROOT / ".ai/scripts/compare-ai-context-versions.py").exists())

    def test_gwt_002_given_published_python_commands_when_colocated_then_thin_compatibility_entrypoints_remain(self) -> None:
        wrappers = {
            ".ai/scripts/validate-software-development-orchestrator-acceptance.py": (
                "Compatibility entrypoint",
                "assets/skills/software-development-orchestrator/scripts/",
            ),
            ".ai/scripts/tests/test_software_development_orchestrator_acceptance.py": (
                "Compatibility entrypoint",
                "assets/skills/software-development-orchestrator/scripts/tests/",
            ),
            ".ai/scripts/tests/test_software_development_orchestrator_capability_contract.py": (
                "Compatibility entrypoint",
                "assets/skills/software-development-orchestrator/scripts/tests/",
            ),
            ".ai/scripts/tests/test_workflow_implementation_contract.py": (
                "Compatibility entrypoint",
                "assets/skills/software-development-orchestrator/scripts/tests/",
            ),
        }

        for path, required_fragments in wrappers.items():
            with self.subTest(path=path):
                content = self.read(path)
                for fragment in required_fragments:
                    self.assertIn(fragment, content)

    def test_gwt_003_given_active_routing_when_colocated_then_canonical_paths_are_authoritative(self) -> None:
        orchestrator_spec = self.read(
            ".ai/assets/skills/software-development-orchestrator/skill.yaml"
        )
        upgrader_spec = self.read(".ai/assets/skills/ai-context-upgrader/skill.yaml")
        distribution_profile = self.read(".ai/distribution/profiles/dotnet-backend.yaml")
        aggregate_runner = self.read(".ai/scripts/check-all.sh")

        self.assertIn(
            ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
            orchestrator_spec,
        )
        self.assertIn(
            ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
            upgrader_spec,
        )
        self.assertIn(
            ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
            distribution_profile,
        )
        self.assertNotIn(".ai/scripts/compare-ai-context-versions.py", distribution_profile)
        self.assertNotIn(
            "python .ai/scripts/tests/test_software_development_orchestrator_acceptance.py -v",
            aggregate_runner,
        )

    def test_gwt_004_given_script_ownership_policy_when_documented_then_single_owner_and_shared_boundaries_are_explicit(self) -> None:
        registry = self.read(".ai/assets/skills/README.MD")

        self.assertIn("exactly one canonical", registry)
        self.assertIn("Keep multi-skill, provider, release, package, workflow", registry)


if __name__ == "__main__":
    unittest.main()
