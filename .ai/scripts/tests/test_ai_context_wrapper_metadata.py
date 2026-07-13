#!/usr/bin/env python3
"""GWT tests for canonical skill wrapper metadata validation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location("validate_ai_context", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class WrapperMetadataFixture:
    """Own a disposable wrapper tree and invoke only the bounded validator."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="aicr003-wrapper-metadata-")
        self.root = Path(self._temporary.name)
        (self.root / ".agents/skills/example").mkdir(parents=True)
        (self.root / ".claude/skills/example").mkdir(parents=True)
        self.path = Path(".ai/assets/skills/example/skill.yaml")

    def close(self) -> None:
        self._temporary.cleanup()

    def validate(self, data: dict) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_wrapper_metadata(self.path, data, errors, root=self.root)
        return errors

    @staticmethod
    def valid_data() -> dict:
        return {
            "wrapper_targets": ["claude", "codex"],
            "wrapper_metadata": {
                "claude": {"wrapper_path": ".claude/skills/example/"},
                "codex": {"wrapper_path": ".agents/skills/example/"},
            },
        }


class WrapperMetadataValidationTests(unittest.TestCase):
    def test_gwt_001_given_matching_existing_wrapper_paths_when_validated_then_passes(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given metadata exactly covers all declared targets with existing paths.
            data = fixture.valid_data()

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then the canonical-to-runtime contract passes.
            self.assertEqual([], errors)
        finally:
            fixture.close()

    def test_gwt_002_given_target_drift_when_validated_then_parity_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given one declared target is missing and one undeclared target is present.
            data = fixture.valid_data()
            data["wrapper_metadata"] = {
                "codex": data["wrapper_metadata"]["codex"],
                "copilot": {"wrapper_path": ".github/prompts/example/"},
            }

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then exact target parity fails closed with both differences.
            self.assertTrue(any("target parity mismatch" in error for error in errors))
            self.assertTrue(any("missing=['claude']" in error for error in errors))
            self.assertTrue(any("extra=['copilot']" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_003_given_non_mapping_target_when_validated_then_shape_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given a target's metadata is a scalar instead of a mapping.
            data = fixture.valid_data()
            data["wrapper_metadata"]["codex"] = ".agents/skills/example/"

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then the per-target mapping requirement fails closed.
            self.assertTrue(any("wrapper_metadata.codex must be a mapping" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_004_given_legacy_only_key_when_validated_then_contract_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given Codex metadata uses only the retired key.
            data = fixture.valid_data()
            data["wrapper_metadata"]["codex"] = {
                "runtime_wrapper_path": ".agents/skills/example/"
            }

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then both the legacy-key and required-key violations are visible.
            self.assertTrue(any("runtime_wrapper_path is legacy" in error for error in errors))
            self.assertTrue(any("wrapper_path must be a non-empty string" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_005_given_placeholder_path_when_validated_then_path_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given a canonical manifest defers its runtime path to a placeholder.
            data = fixture.valid_data()
            data["wrapper_metadata"]["codex"]["wrapper_path"] = ".agents/skills/<skill-id>/"

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then placeholder syntax is rejected before existence is considered.
            self.assertTrue(any("without placeholders or globs" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_006_given_escaping_path_when_validated_then_boundary_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given a relative path resolves outside the repository root.
            data = fixture.valid_data()
            data["wrapper_metadata"]["codex"]["wrapper_path"] = "../outside/"

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then repository-boundary validation fails closed.
            self.assertTrue(any("escapes the repository" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_007_given_missing_wrapper_when_validated_then_existence_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given the declared wrapper path is syntactically valid but absent.
            data = fixture.valid_data()
            data["wrapper_metadata"]["codex"]["wrapper_path"] = ".agents/skills/missing/"

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then the missing runtime projection fails closed.
            self.assertTrue(any("wrapper_path does not exist" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_008_given_scalar_metadata_when_validated_then_mapping_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given wrapper_metadata is a scalar instead of the required mapping.
            data = fixture.valid_data()
            data["wrapper_metadata"] = ".agents/skills/example/"

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then the top-level shape fails closed.
            self.assertTrue(any("wrapper_metadata must be a mapping" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_009_given_non_string_target_key_when_validated_then_key_fails(self) -> None:
        fixture = WrapperMetadataFixture()
        try:
            # Given YAML metadata contains a non-string target key.
            data = fixture.valid_data()
            data["wrapper_metadata"][1] = {"wrapper_path": ".agents/skills/example/"}

            # When wrapper metadata validation runs.
            errors = fixture.validate(data)

            # Then validation reports the invalid key without raising an exception.
            self.assertTrue(any("wrapper_metadata keys must be strings" in error for error in errors))
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
