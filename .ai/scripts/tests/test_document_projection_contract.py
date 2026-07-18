#!/usr/bin/env python3
"""Fail-closed checks for routed testing and use-case documentation."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SURFACES = (
    ROOT / ".dev/guides",
    ROOT / ".dev/standards/examples",
)

UNQUALIFIED_MOCKING = re.compile(
    r"(?im)^(?:#{1,6}\s+|-\s+|\d+\.\s+)(?:use\s+)?nsubstitute(?:\s+only|\s+for\s+mocks?)?[.!]?\s*$"
)
SYNCHRONOUS_USE_CASE = re.compile(r"\b(?:_?\w*UseCase|_useCase)\.Execute\(")


def documentation_files() -> list[Path]:
    files: list[Path] = []
    for root in SURFACES:
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".cs"}
        )
    return files


class DocumentProjectionContractTests(unittest.TestCase):
    def test_gwt_001_given_routed_testing_docs_when_scanned_then_mocking_defaults_are_qualified(self) -> None:
        violations: list[str] = []
        for path in documentation_files():
            text = path.read_text(encoding="utf-8")
            if UNQUALIFIED_MOCKING.search(text):
                violations.append(str(path.relative_to(ROOT)))

        self.assertEqual([], violations)

    def test_gwt_002_given_use_case_snippets_when_scanned_then_synchronous_execute_is_absent(self) -> None:
        violations: list[str] = []
        for path in documentation_files():
            text = path.read_text(encoding="utf-8")
            if SYNCHRONOUS_USE_CASE.search(text):
                violations.append(str(path.relative_to(ROOT)))

        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
