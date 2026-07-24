#!/usr/bin/env python3
"""GWT tests for agent-language and root bilingual structural parity gates."""

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


class LanguageFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="language-policy-")
        self.root = Path(self._temporary.name)

    def close(self) -> None:
        self._temporary.cleanup()

    def write(self, path: str, text: str) -> Path:
        relative = Path(path)
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        return relative

    def write_valid_bilingual_entries(self) -> None:
        readme_table = """| Entry |
| --- |
| `README.md` |
| `README.en.md` |
"""
        self.write(
            "README.md",
            "# Repository\n\n[English](README.en.md)\n\ncanonical human entry.\n\n"
            "- `stable-id`\n\n" + readme_table,
        )
        self.write(
            "README.en.md",
            "# Repository\n\n[繁體中文](README.md)\n\ntranslation entry.\n\n"
            "- `stable-id`\n\n" + readme_table,
        )

        agent_table = """| Entry |
| --- |
| `README.md` |
| `README.en.md` |
| `AGENTS.md` |
| `AGENTS.zh-TW.md` |
| `CLAUDE.md` |
"""
        self.write(
            "AGENTS.md",
            "# Agents\n\n[Traditional Chinese](AGENTS.zh-TW.md)\n\n"
            "canonical English instructions.\n\n- `automatic-candidate`\n\n"
            + agent_table,
        )
        self.write(
            "AGENTS.zh-TW.md",
            "# Agents\n\n[English](AGENTS.md)\n\n翻譯 entry.\n\n"
            "- `automatic-candidate`\n\n" + agent_table,
        )

    def validate_language(self, path: Path) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_language(path, errors, root=self.root)
        return errors

    def validate_bilingual(self) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_bilingual_entries(errors, root=self.root)
        return errors


class AgentLanguagePolicyTests(unittest.TestCase):
    def test_gwt_001_given_ascii_agent_prose_when_validated_then_passes(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given an English-only agent-facing standard.
            path = fixture.write(".dev/standards/example.md", "# Rule\n\nUse ASCII prose.\n")

            # When the language policy runs, then no language error is reported.
            self.assertEqual([], fixture.validate_language(path))
        finally:
            fixture.close()

    def test_gwt_002_given_fullwidth_colon_when_validated_then_fails(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given English prose containing a fullwidth colon.
            path = fixture.write(".dev/standards/example.md", "Compatibility： exact.\n")

            # When validation runs, then the punctuation drift fails closed.
            errors = fixture.validate_language(path)
            self.assertTrue(any("non-ASCII punctuation" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_003_given_ideographic_stop_when_validated_then_fails(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given English prose containing an ideographic full stop.
            path = fixture.write(".dev/standards/example.md", "Commit。\n")

            # When validation runs, then the punctuation drift fails closed.
            errors = fixture.validate_language(path)
            self.assertTrue(any("non-ASCII punctuation" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_004_given_exact_routing_exception_when_validated_then_passes(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given the one exact policy-owned mixed-language routing trigger.
            path = Path(".dev/standards/WORKFLOW-GATE-POLICY.md")
            allowed = next(iter(VALIDATOR.LANGUAGE_ALLOWLIST[path]))
            fixture.write(path.as_posix(), allowed + "\n")

            # When validation runs, then the exact scoped exception passes.
            self.assertEqual([], fixture.validate_language(path))
        finally:
            fixture.close()

    def test_gwt_005_given_example_surface_when_classified_then_it_is_excluded(self) -> None:
        # Given reference-only example material under the language-policy skip tree.
        path = Path(".dev/standards/examples/usecase/example.md")

        # When surface classification runs, then examples do not become active prose.
        self.assertFalse(VALIDATOR.is_language_surface(path, set()))


class BilingualStructuralParityTests(unittest.TestCase):
    def test_gwt_006_given_aligned_root_entries_when_validated_then_passes(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given both approved bilingual root pairs have aligned structure.
            fixture.write_valid_bilingual_entries()

            # When structural parity validation runs, then it passes.
            self.assertEqual([], fixture.validate_bilingual())
        finally:
            fixture.close()

    def test_gwt_007_given_identifier_drift_when_validated_then_fails(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given the English canonical entry adds an identifier absent in zh-TW.
            fixture.write_valid_bilingual_entries()
            path = fixture.root / "AGENTS.md"
            path.write_text(
                path.read_text(encoding="utf-8") + "\n`handoff-id`\n",
                encoding="utf-8",
                newline="\n",
            )

            # When validation runs, then inline-code identifier parity fails.
            errors = fixture.validate_bilingual()
            self.assertTrue(
                any("inline-code identifier multiset" in error for error in errors)
            )
        finally:
            fixture.close()

    def test_gwt_008_given_list_shape_drift_when_validated_then_fails(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given a translated list changes from unordered to ordered.
            fixture.write_valid_bilingual_entries()
            path = fixture.root / "README.en.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "- `stable-id`", "1. `stable-id`"
                ),
                encoding="utf-8",
                newline="\n",
            )

            # When validation runs, then list-marker parity fails.
            errors = fixture.validate_bilingual()
            self.assertTrue(any("list-marker shape" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_009_given_table_shape_drift_when_validated_then_fails(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given a translated table gains a structurally unmatched column.
            fixture.write_valid_bilingual_entries()
            path = fixture.root / "README.en.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "| `README.md` |", "| `README.md` | extra |"
                ),
                encoding="utf-8",
                newline="\n",
            )

            # When validation runs, then table-column parity fails.
            errors = fixture.validate_bilingual()
            self.assertTrue(any("table-column shape" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_010_given_fence_drift_when_validated_then_fails(self) -> None:
        fixture = LanguageFixture()
        try:
            # Given only the canonical entry gains a fenced-code structure.
            fixture.write_valid_bilingual_entries()
            path = fixture.root / "README.md"
            path.write_text(
                path.read_text(encoding="utf-8") + "\n```text\nvalue\n```\n",
                encoding="utf-8",
                newline="\n",
            )

            # When validation runs, then fence-marker parity fails.
            errors = fixture.validate_bilingual()
            self.assertTrue(any("fence-marker order" in error for error in errors))
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
