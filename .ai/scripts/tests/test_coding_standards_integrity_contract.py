#!/usr/bin/env python3
"""GWT source-contract tests for truthful coding-standards structural checks."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / ".ai/scripts/check-coding-standards.sh"
RUNNER = ROOT / ".ai/scripts/check-all.sh"


class CodingStandardsIntegrityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def test_gwt_001_given_structural_checker_when_success_text_is_inspected_then_no_semantic_completeness_is_claimed(self) -> None:
        self.assertNotIn("complete and well-organized", self.source)
        self.assertIn("does not assert C# semantic compliance", self.source)
        self.assertIn("Structural Integrity", self.runner)

    def test_gwt_002_given_retired_prompt_folder_when_configured_paths_are_inspected_then_it_is_not_required(self) -> None:
        self.assertNotIn("PROMPTS_DIR", self.source)
        self.assertIn("INDEX_FILE", self.source)
        self.assertIn("SHARED_CONTEXT_DIR", self.source)

    def test_gwt_003_given_focused_standard_catalog_when_required_files_are_inspected_then_omitted_profiles_are_covered(self) -> None:
        self.assertIn('"reactor-standards.md"', self.source)
        self.assertIn('"profile-configuration-standards.md"', self.source)
        self.assertIn("Missing exact catalog route in INDEX.MD", self.source)


if __name__ == "__main__":
    unittest.main()
