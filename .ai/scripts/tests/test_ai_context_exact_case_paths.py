#!/usr/bin/env python3
"""GWT tests for Git exact-case validation of active AI-context references."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location("validate_ai_context_exact_case", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ExactCaseReferenceValidationTests(unittest.TestCase):
    def validate(
        self,
        reference: str,
        *,
        source: Path = Path(".ai/README.MD"),
        rendered: str | None = None,
    ) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="ai-context-exact-case-") as temporary:
            root = Path(temporary)
            architecture = Path(".dev/ARCHITECTURE.md")
            (root / architecture).parent.mkdir(parents=True)
            (root / source).parent.mkdir(parents=True)
            (root / architecture).write_text("# Architecture\n", encoding="utf-8")
            (root / source).write_text(rendered or f"See `{reference}`.\n", encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.validate_exact_case_references([architecture, source], errors, root=root)
            return errors

    def test_gwt_001_given_wrong_git_path_case_when_validated_then_fails(self) -> None:
        errors = self.validate(".dev/ARCHITECTURE.MD")
        self.assertTrue(any("exact-case mismatch" in error for error in errors))
        self.assertTrue(any(".dev/ARCHITECTURE.md" in error for error in errors))

    def test_gwt_002_given_exact_git_path_case_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(".dev/ARCHITECTURE.md"))

    def test_gwt_003_given_wrong_case_markdown_link_when_validated_then_fails(self) -> None:
        errors = self.validate(
            ".dev/ARCHITECTURE.MD",
            rendered="[Architecture](.dev/ARCHITECTURE.MD)\n",
        )
        self.assertTrue(any("exact-case mismatch" in error for error in errors))

    def test_gwt_004_given_wrong_case_relative_link_when_validated_then_fails(self) -> None:
        errors = self.validate(
            "../../ARCHITECTURE.MD",
            source=Path(".dev/standards/coding-standards/README.md"),
            rendered="[Architecture](../../ARCHITECTURE.MD)\n",
        )
        self.assertTrue(any("exact-case mismatch" in error for error in errors))

    def test_gwt_005_given_historical_workflow_reference_when_validated_then_ignored(self) -> None:
        errors = self.validate(
            ".dev/ARCHITECTURE.MD",
            source=Path(".dev/workflows/legacy/report.md"),
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
