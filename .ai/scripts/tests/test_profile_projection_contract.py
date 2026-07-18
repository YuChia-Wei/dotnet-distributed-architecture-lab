#!/usr/bin/env python3
"""Fail-closed checks for canonical profile projections."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

PROJECTION_PATHS = (
    ROOT / ".dev/standards/templates",
    ROOT / ".dev/standards/examples",
    ROOT / ".dev/guides",
    ROOT / ".ai/assets/tech-stacks/dotnet-backend/shared",
)

STALE_ENVIRONMENT_NAMES = (
    "Test-InMemory",
    "Test-Outbox",
    "test-inmemory",
    "test-outbox",
)

EXECUTABLE_SELECTOR_PATTERNS = (
    'Configuration["Profiles:Mode"]',
    'configuration["Profiles:Mode"]',
    'GetValue<string>("Repository:Mode")',
    '"Profiles": {\n    "Mode":',
)


def projection_files() -> list[Path]:
    files: list[Path] = []
    for root in PROJECTION_PATHS:
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".cs", ".json"}
        )
    return files


class ProfileProjectionContractTests(unittest.TestCase):
    def test_gwt_001_given_active_projections_when_scanned_then_stale_names_are_absent(self) -> None:
        violations: list[str] = []
        for path in projection_files():
            text = path.read_text(encoding="utf-8")
            for stale_name in STALE_ENVIRONMENT_NAMES:
                if stale_name in text:
                    violations.append(f"{path.relative_to(ROOT)}: {stale_name}")

        self.assertEqual([], violations)

    def test_gwt_002_given_active_projections_when_scanned_then_custom_selectors_are_not_executable(self) -> None:
        violations: list[str] = []
        for path in projection_files():
            text = path.read_text(encoding="utf-8")
            for pattern in EXECUTABLE_SELECTOR_PATTERNS:
                if pattern in text:
                    violations.append(f"{path.relative_to(ROOT)}: {pattern}")

        self.assertEqual([], violations)

    def test_gwt_003_given_aspnet_examples_when_checked_then_canonical_test_environment_files_exist(self) -> None:
        example_root = ROOT / ".dev/standards/examples/aspnet-core"
        self.assertTrue((example_root / "appsettings.TestInMemory.json").is_file())
        self.assertTrue((example_root / "appsettings.TestOutbox.json").is_file())
        self.assertFalse((example_root / "appsettings.Test.InMemory.json").exists())
        self.assertFalse((example_root / "appsettings.Test.Outbox.json").exists())


if __name__ == "__main__":
    unittest.main()
