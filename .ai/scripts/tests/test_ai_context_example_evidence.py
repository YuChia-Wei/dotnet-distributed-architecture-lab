#!/usr/bin/env python3
"""GWT tests for machine-readable example evidence tiers."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_example_evidence", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ExampleEvidenceContractTests(unittest.TestCase):
    def validate(
        self,
        manifest: dict,
        *,
        readme: str = "# Examples\n",
        create_validator: bool = False,
        create_versions: bool = False,
    ) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="example-evidence-contract-") as temporary:
            root = Path(temporary)
            examples = root / ".dev/standards/examples"
            examples.mkdir(parents=True)
            (examples / "sample").mkdir()
            (examples / "README.md").write_text(readme, encoding="utf-8")
            if create_versions:
                (examples / ".versions.json").write_text("{}\n", encoding="utf-8")
            if create_validator:
                validator = root / ".ai/scripts/validate-sample.py"
                validator.parent.mkdir(parents=True)
                validator.write_text("# validator\n", encoding="utf-8")

            schema = {
                "allowed_tiers": [
                    "executable-tested",
                    "structure-validated",
                    "illustrative",
                    "reference-only",
                    "historical",
                ],
                "default_allowed_tiers": ["illustrative", "historical"],
                "required_entry_fields": [
                    "path",
                    "tier",
                    "claim",
                    "reason",
                    "validators",
                    "build_commands",
                    "test_commands",
                ],
                "tier_requirements": {
                    "executable-tested": {
                        "required_nonempty": ["build_commands", "test_commands"]
                    },
                    "structure-validated": {"required_nonempty": ["validators"]},
                    "illustrative": {"required_nonempty": []},
                    "reference-only": {"required_nonempty": []},
                    "historical": {"required_nonempty": []},
                },
            }
            manifest_path = Path(".dev/standards/examples/evidence-manifest.yaml")
            schema_path = Path(".dev/standards/examples/evidence-schema.yaml")
            (root / manifest_path).write_text(
                yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
            )
            (root / schema_path).write_text(
                yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.validate_example_evidence_contract(
                errors,
                root=root,
                manifest_path=manifest_path,
                schema_path=schema_path,
            )
            return errors

    @staticmethod
    def entry(tier: str = "illustrative") -> dict:
        return {
            "path": "sample/",
            "tier": tier,
            "claim": "Sample",
            "reason": "Test fixture",
            "validators": [],
            "build_commands": [],
            "test_commands": [],
        }

    def test_gwt_001_given_illustrative_manifest_when_validated_then_passes(self) -> None:
        manifest = {"default_tier": "historical", "entries": [self.entry()]}
        self.assertEqual([], self.validate(manifest))

    def test_gwt_002_given_structure_tier_without_validator_when_validated_then_fails(self) -> None:
        manifest = {
            "default_tier": "historical",
            "entries": [self.entry("structure-validated")],
        }
        errors = self.validate(manifest)
        self.assertTrue(any("requires non-empty validators" in error for error in errors))

    def test_gwt_003_given_upward_default_when_validated_then_fails(self) -> None:
        manifest = {"default_tier": "executable-tested", "entries": [self.entry()]}
        errors = self.validate(manifest)
        self.assertTrue(any("default_tier must be illustrative or historical" in error for error in errors))

    def test_gwt_004_given_stale_sync_metadata_when_validated_then_fails(self) -> None:
        manifest = {"default_tier": "historical", "entries": [self.entry()]}
        errors = self.validate(manifest, create_versions=True)
        self.assertTrue(any("stale source-sync metadata" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
