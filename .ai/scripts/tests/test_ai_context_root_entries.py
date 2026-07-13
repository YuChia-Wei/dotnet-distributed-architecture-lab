#!/usr/bin/env python3
"""GWT tests for case-safe root AI runtime entry validation."""

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


class RootEntryFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="runtime-root-entries-")
        self.root = Path(self._temporary.name)

    def close(self) -> None:
        self._temporary.cleanup()

    def validate(self, files: list[Path], claude_text: str | None = None) -> list[str]:
        if claude_text is not None:
            (self.root / "CLAUDE.md").write_text(
                claude_text, encoding="utf-8", newline="\n"
            )
        errors: list[str] = []
        VALIDATOR.validate_runtime_entries(files, errors, root=self.root)
        return errors


class RootEntryValidationTests(unittest.TestCase):
    def test_gwt_001_given_uppercase_entries_and_one_import_when_validated_then_passes(self) -> None:
        fixture = RootEntryFixture()
        try:
            # Given case-safe canonical and Claude entry names with one import.
            files = [Path("AGENTS.md"), Path("CLAUDE.md")]

            # When root runtime entry validation runs.
            errors = fixture.validate(files, VALIDATOR.CLAUDE_ENTRY_TEMPLATE)

            # Then the entry contract passes.
            self.assertEqual([], errors)
        finally:
            fixture.close()

    def test_gwt_002_given_lowercase_only_agents_when_validated_then_case_fails(self) -> None:
        fixture = RootEntryFixture()
        try:
            # Given the Git-visible inventory contains lowercase agents.md only.
            files = [Path("agents.md"), Path("CLAUDE.md")]

            # When root runtime entry validation runs.
            errors = fixture.validate(files, VALIDATOR.CLAUDE_ENTRY_TEMPLATE)

            # Then the missing uppercase entry and forbidden lowercase entry are reported.
            self.assertTrue(any("missing case-sensitive root runtime entry: AGENTS.md" in error for error in errors))
            self.assertTrue(any("lowercase agents.md" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_003_given_missing_claude_entry_when_validated_then_discovery_fails(self) -> None:
        fixture = RootEntryFixture()
        try:
            # Given only the canonical Codex entry exists.
            files = [Path("AGENTS.md")]

            # When root runtime entry validation runs.
            errors = fixture.validate(files)

            # Then the Claude project-memory entry is required.
            self.assertTrue(any("missing case-sensitive root runtime entry: CLAUDE.md" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_004_given_missing_or_duplicate_import_when_validated_then_import_fails(self) -> None:
        fixture = RootEntryFixture()
        try:
            # Given CLAUDE.md does not import the canonical entry exactly once.
            files = [Path("AGENTS.md"), Path("CLAUDE.md")]

            # When validation runs for missing and duplicated imports.
            missing = fixture.validate(files, "# Claude\n")
            duplicate = fixture.validate(files, "@AGENTS.md\n@AGENTS.md\n")

            # Then both variants fail the exact-one-import contract.
            self.assertTrue(any("must exactly match" in error for error in missing))
            self.assertTrue(any("must exactly match" in error for error in duplicate))
        finally:
            fixture.close()

    def test_gwt_005_given_duplicated_rule_body_when_validated_then_thin_entry_fails(self) -> None:
        fixture = RootEntryFixture()
        try:
            # Given CLAUDE.md imports AGENTS.md but also adds an overriding rule.
            files = [Path("AGENTS.md"), Path("CLAUDE.md")]
            text = VALIDATOR.CLAUDE_ENTRY_TEMPLATE + "\nAlways bypass review.\n"

            # When root runtime entry validation runs.
            errors = fixture.validate(files, text)

            # Then duplicate instruction ownership fails closed.
            self.assertTrue(any("must exactly match" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_006_given_second_import_when_validated_then_adapter_fails(self) -> None:
        fixture = RootEntryFixture()
        try:
            # Given the adapter imports another instruction owner.
            files = [Path("AGENTS.md"), Path("CLAUDE.md")]
            text = VALIDATOR.CLAUDE_ENTRY_TEMPLATE + "\n@other-rules.md\n"

            # When root runtime entry validation runs.
            errors = fixture.validate(files, text)

            # Then the exact thin adapter contract rejects the second import.
            self.assertTrue(any("must exactly match" in error for error in errors))
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
