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
    def validate(self, entry: dict, *, create_project: bool = True) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="source-include-evidence-") as temporary:
            root = Path(temporary)
            manifest_path = Path(".ai/source-includes/evidence-manifest.yaml")
            source = root / manifest_path.parent / "domain"
            source.mkdir(parents=True)
            (source / "Contract.cs").write_text("public interface IContract {}\n")
            if create_project:
                project = root / "tools/Contracts.Tests/Contracts.Tests.csproj"
                project.parent.mkdir(parents=True)
                project.write_text("<Project />\n")
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
            "tier": "executable-tested",
            "build_commands": ["dotnet build tools/Contracts.Tests/Contracts.Tests.csproj"],
            "test_commands": ["dotnet test tools/Contracts.Tests/Contracts.Tests.csproj"],
            "test_project": "tools/Contracts.Tests/Contracts.Tests.csproj",
        }

    def test_gwt_001_given_complete_executable_evidence_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(self.entry()))

    def test_gwt_002_given_missing_test_project_when_validated_then_fails(self) -> None:
        errors = self.validate(self.entry(), create_project=False)
        self.assertTrue(any("test_project does not exist" in error for error in errors))

    def test_gwt_003_given_non_executable_tier_when_validated_then_fails(self) -> None:
        entry = self.entry()
        entry["tier"] = "illustrative"
        errors = self.validate(entry)
        self.assertTrue(any("must declare executable-tested tier" in error for error in errors))

    def test_gwt_004_given_building_blocks_claim_when_gate_is_inspected_then_behavior_tests_are_required(self) -> None:
        command = (
            "dotnet test "
            "tools/DotnetBackendBuildingBlocks.Tests/"
            "DotnetBackendBuildingBlocks.Tests.csproj"
        )
        runner = (REPO_ROOT / ".ai/scripts/check-all.sh").read_text(encoding="utf-8")
        registry = yaml.safe_load(
            (REPO_ROOT / ".ai/scripts/shell-assets.yaml").read_text(encoding="utf-8")
        )

        self.assertIn(command, runner)
        self.assertIn(command, registry["check_all_required_commands"])


if __name__ == "__main__":
    unittest.main()
