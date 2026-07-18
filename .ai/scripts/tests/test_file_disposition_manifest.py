#!/usr/bin/env python3
"""GWT regression tests for file-disposition manifest validation."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = ROOT / ".ai/scripts/validate-file-disposition-manifest.py"
SPEC = importlib.util.spec_from_file_location("file_disposition_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def valid_manifest() -> dict:
    return {
        "contract": {"allowed_dispositions": sorted(VALIDATOR.ALLOWED_DISPOSITIONS)},
        "coverage": {
            "base_commit": "a" * 40,
            "included_roots": [".ai/", ".dev/standards/"],
        },
        "entries": [
            {
                "path": ".ai/kept.md",
                "disposition": "kept",
                "destination": None,
                "change_summary": "Keep the canonical path.",
                "target_migration": "three-way",
            },
            {
                "path": ".dev/standards/old.md",
                "disposition": "moved-to",
                "destination": ".dev/standards/new.md",
                "change_summary": "Move the standard.",
                "target_migration": "reconcile-move",
            },
        ],
    }


class FileDispositionManifestTests(unittest.TestCase):
    def validate(
        self,
        data: dict,
        *,
        changed: set[str] | None = None,
    ) -> list[str]:
        return VALIDATOR.validate_manifest_data(
            data,
            current_paths={".ai/kept.md", ".dev/standards/new.md"},
            base_paths={".ai/kept.md", ".dev/standards/old.md"},
            changed_paths=changed or {".ai/kept.md", ".dev/standards/old.md"},
        )

    def test_gwt_001_given_complete_exact_case_manifest_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(valid_manifest()))

    def test_gwt_002_given_changed_path_without_disposition_when_validated_then_fails(self) -> None:
        errors = self.validate(valid_manifest(), changed={".ai/uncovered.md"})
        self.assertIn("coverage missing changed path: .ai/uncovered.md", errors)

    def test_gwt_003_given_move_without_existing_destination_when_validated_then_fails(self) -> None:
        data = valid_manifest()
        data["entries"][1]["destination"] = ".dev/standards/Missing.md"
        errors = self.validate(data)
        self.assertTrue(any("destination does not exist" in error for error in errors))

    def test_gwt_004_given_retired_path_absent_from_base_when_validated_then_fails(self) -> None:
        data = valid_manifest()
        data["entries"][1]["disposition"] = "retired"
        data["entries"][1]["destination"] = None
        data["entries"][1]["path"] = ".dev/standards/unknown.md"
        errors = self.validate(data, changed={".dev/standards/unknown.md"})
        self.assertTrue(any("absent from the coverage base commit" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
