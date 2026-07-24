#!/usr/bin/env python3
"""GWT tests for backlog target, completion, and publication release metadata."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-workflow-artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_backlog_release", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class BacklogReleaseContractTests(unittest.TestCase):
    def validate(self, release: object, status: str = "open") -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_backlog_release(release, status, "item.yaml", errors)
        return errors

    def test_gwt_001_given_unassigned_open_item_when_validated_then_passes(self) -> None:
        errors = self.validate(
            {"target": "unassigned", "completed_in": None, "published_in": None}
        )
        self.assertEqual([], errors)

    def test_gwt_002_given_semver_target_when_validated_then_passes(self) -> None:
        errors = self.validate(
            {"target": "v0.5.0", "completed_in": None, "published_in": None}
        )
        self.assertEqual([], errors)

    def test_gwt_003_given_invalid_target_when_validated_then_fails(self) -> None:
        errors = self.validate(
            {"target": "next", "completed_in": None, "published_in": None}
        )
        self.assertTrue(any("release.target" in error for error in errors))

    def test_gwt_004_given_resolved_item_without_completion_when_validated_then_fails(self) -> None:
        errors = self.validate(
            {"target": "v0.5.0", "completed_in": None, "published_in": None},
            status="resolved",
        )
        self.assertTrue(any("requires release.completed_in" in error for error in errors))

    def test_gwt_005_given_publication_without_completion_when_validated_then_fails(self) -> None:
        errors = self.validate(
            {"target": "v0.5.0", "completed_in": None, "published_in": "v0.5.0"}
        )
        self.assertTrue(any("published_in requires" in error for error in errors))

    def test_gwt_006_given_resolved_published_item_when_validated_then_passes(self) -> None:
        errors = self.validate(
            {
                "target": "v0.1.0",
                "completed_in": "v0.1.0",
                "published_in": "v0.1.0",
            },
            status="resolved",
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
