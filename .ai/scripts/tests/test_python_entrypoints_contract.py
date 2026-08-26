#!/usr/bin/env python3
"""Contract tests for the portable Python entrypoint registry and package projection."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / ".ai/scripts/python-entrypoints.json"
PROFILE_PATH = ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"

SHARED_RUNTIME_ASSETS = {
    ".ai/scripts/python-entrypoints.json",
    ".ai/scripts/python_prerequisites.py",
    ".ai/scripts/run-python-entrypoint.sh",
    ".ai/scripts/run-python-entrypoint.ps1",
}

EXPECTED_PORTABLE_PATHS = {
    ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
    ".ai/scripts/plan-ai-context-package-apply.py",
    ".ai/scripts/resolve-effective-rule-packet.py",
    ".ai/scripts/validate-ai-context-target.py",
    ".ai/scripts/validate-ai-context.py",
    ".ai/scripts/validate-assessment-artifacts.py",
    ".ai/scripts/validate-dependency-versions.py",
    ".ai/scripts/validate-file-disposition-manifest.py",
    ".ai/scripts/validate-git-commits.py",
    ".ai/scripts/validate-shell-assets.py",
    ".ai/scripts/validate-software-development-orchestrator-acceptance.py",
    ".ai/scripts/validate-workflow-artifacts.py",
    ".ai/scripts/validate-workflow-handoff.py",
}

EXPECTED_STDLIB_ONLY_PATHS = {
    ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
    ".ai/scripts/validate-dependency-versions.py",
}


class PythonEntrypointContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.entrypoints = cls.registry["entrypoints"]

    def test_gwt_001_given_governed_registry_when_counted_then_portable_dependency_contract_is_complete(self) -> None:
        self.assertEqual("1.0", self.registry["schema_version"])
        self.assertEqual("3.11", self.registry["python_floor"])
        self.assertEqual(31, len(self.entrypoints))
        portable = [item for item in self.entrypoints if item["portable"]]
        pyyaml = [item for item in self.entrypoints if item["dependency_profile"] == ["PyYAML"]]
        stdlib = [item for item in self.entrypoints if not item["dependency_profile"]]
        self.assertEqual(13, len(portable))
        self.assertEqual(29, len(pyyaml))
        self.assertEqual(2, len(stdlib))
        self.assertEqual("6.0.3", self.registry["governed_requirements"]["PyYAML"]["version"])
        self.assertEqual("requirements.txt", self.registry["governed_requirements"]["PyYAML"]["requirements_path"])
        self.assertEqual(len(self.entrypoints), len({item["path"] for item in self.entrypoints}))
        self.assertEqual(EXPECTED_PORTABLE_PATHS, {item["path"] for item in portable})
        self.assertEqual(
            EXPECTED_STDLIB_ONLY_PATHS,
            {item["path"] for item in self.entrypoints if not item["dependency_profile"]},
        )
        self.assertEqual(
            {
                ".ai/scripts/plan-ai-context-package-apply.py",
                ".ai/scripts/validate-immutable-history.py",
            },
            {item["path"] for item in self.entrypoints if item["prerequisite_exit_code"] == 2},
        )
        self.assertEqual(
            {".ai/scripts/ai_context_release_closeout.py"},
            {item["path"] for item in self.entrypoints if item["prerequisite_exit_code"] == 3},
        )
        self.assertTrue(
            all(
                item["prerequisite_exit_code"] == 1
                for item in self.entrypoints
                if item["path"]
                not in {
                    ".ai/scripts/plan-ai-context-package-apply.py",
                    ".ai/scripts/validate-immutable-history.py",
                    ".ai/scripts/ai_context_release_closeout.py",
                }
            )
        )
        for item in self.entrypoints:
            self.assertTrue((ROOT / item["path"]).is_file(), item["path"])
            self.assertIn(item["prerequisite_exit_code"], (1, 2, 3), item["path"])

    def test_gwt_002_given_dotnet_profile_when_resolved_then_shared_runtime_and_portable_cli_assets_are_projected(self) -> None:
        profile = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
        runtime_entry = next(item for item in profile["entries"] if item["id"] == "ai-runtime-scripts")
        self.assertEqual(".ai/scripts/**", runtime_entry["source"])
        self.assertEqual("software-development-core", runtime_entry["component_id"])
        projected = {item["path"] for item in self.entrypoints if item["portable"]}
        self.assertEqual(13, len(projected))
        for path in SHARED_RUNTIME_ASSETS | projected:
            self.assertTrue(path.startswith(".ai/scripts/") or path.startswith(".ai/assets/skills/"), path)
        self.assertIn(
            ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
            projected,
        )

    def test_gwt_003_given_portable_direct_commands_when_help_is_requested_then_each_remains_callable(self) -> None:
        for item in self.entrypoints:
            if not item["portable"]:
                continue
            with self.subTest(entrypoint=item["path"]):
                result = subprocess.run(
                    [sys.executable, str(ROOT / item["path"]), "--help"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_004_given_machine_local_validation_opt_in_when_profile_is_read_then_it_is_source_only(self) -> None:
        profile = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))
        local_state = next(
            item
            for item in profile["exclusions"]
            if item["id"] == "repository-and-local-runtime-state"
        )
        self.assertEqual("source-only", local_state["classification"])
        self.assertIn(".dev/validation.local.conf", local_state["patterns"])


if __name__ == "__main__":
    unittest.main()
