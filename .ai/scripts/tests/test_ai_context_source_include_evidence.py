#!/usr/bin/env python3
"""GWT tests for executable-tested source-include evidence."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_source_include_evidence", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SourceIncludeEvidenceTests(unittest.TestCase):
    def validate(self, entry: dict) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="source-include-evidence-") as temporary:
            root = Path(temporary)
            manifest_path = Path(".ai/source-includes/evidence-manifest.yaml")
            source = root / manifest_path.parent / "domain"
            source.mkdir(parents=True)
            (source / "Contract.cs").write_text("public interface IContract {}\n")
            (root / manifest_path).write_text(
                yaml.safe_dump({"entries": [entry]}, sort_keys=False),
                encoding="utf-8",
            )

            errors: list[str] = []
            VALIDATOR.validate_source_include_evidence(
                errors, root=root, manifest_path=manifest_path
            )
            return errors

    @staticmethod
    def entry() -> dict:
        return {
            "path": "domain/",
            "tier": "reference-only",
            "claim": "Bounded source reference.",
            "reason": "The framework does not select a target SDK.",
            "validators": [],
            "build_commands": [],
            "test_commands": [],
            "target_validation": {
                "required": True,
                "responsibility": "Target owns compilation and behavior evidence.",
            },
        }

    def test_gwt_001_given_complete_reference_evidence_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(self.entry()))

    def test_gwt_002_given_executable_tier_when_validated_then_fails(self) -> None:
        entry = self.entry()
        entry["tier"] = "executable-tested"
        errors = self.validate(entry)
        self.assertTrue(any("must declare reference-only tier" in error for error in errors))

    def test_gwt_003_given_framework_build_claim_when_validated_then_fails(self) -> None:
        entry = self.entry()
        entry["build_commands"] = ["dotnet build tools/Contracts.Tests/Contracts.Tests.csproj"]
        entry["test_project"] = "tools/Contracts.Tests/Contracts.Tests.csproj"
        errors = self.validate(entry)
        self.assertTrue(any("requires empty build_commands" in error for error in errors))
        self.assertTrue(any("must not declare test_project" in error for error in errors))

    def test_gwt_004_given_current_source_include_when_gate_is_inspected_then_target_owns_validation(self) -> None:
        manifest = yaml.safe_load(
            (REPO_ROOT / ".ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml").read_text(
                encoding="utf-8"
            )
        )
        runner = (REPO_ROOT / ".ai/scripts/check-all.sh").read_text(encoding="utf-8")
        registry = yaml.safe_load(
            (REPO_ROOT / ".ai/scripts/shell-assets.yaml").read_text(encoding="utf-8")
        )

        entry = manifest["entries"][0]
        self.assertEqual("reference-only", entry["tier"])
        self.assertTrue(entry["target_validation"]["required"])
        self.assertEqual([], entry["build_commands"])
        self.assertEqual([], entry["test_commands"])
        self.assertNotIn("DotnetBackendBuildingBlocks.Tests", runner)
        self.assertFalse(
            any("DotnetBackendBuildingBlocks.Tests" in command for command in registry["check_all_required_commands"])
        )


if __name__ == "__main__":
    unittest.main()
