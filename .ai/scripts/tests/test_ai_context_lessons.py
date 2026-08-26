#!/usr/bin/env python3
"""GWT tests for the source-repository lesson knowledge contract."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location("validate_ai_context_lessons", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class LessonFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="ai-context-lessons-")
        self.root = Path(self._temporary.name)
        self.lesson_id = "LESSON-ENV-001"
        self.lesson_name = "LESSON-ENV-001-shell-path.md"
        self.write(".dev/INDEX.md", "| `lessons/README.MD` | contract |\n| `lessons/INDEX.MD` | index |\n| `lessons/environment/` | category |\n")
        self.write(
            ".dev/lessons/README.MD",
            "# Lessons\n\n"
            + "\n\n".join(VALIDATOR.LESSON_README_HEADINGS)
            + "\n",
        )
        self.write(
            ".dev/lessons/INDEX.MD",
            "# Lessons Index\n\n## Lesson Catalog\n\n"
            "| Path | Lesson ID | Lesson | Category | Lifecycle | Origin | Target |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            f"| `environment/{self.lesson_name}` | `{self.lesson_id}` | [Shell path](environment/{self.lesson_name}) | `environment` | `active` | evidence | `none` |\n",
        )
        self.write(
            ".dev/lessons/environment/INDEX.MD",
            "# Environment Lessons\n\n"
            "| Path | Lesson ID | Lesson | Lifecycle | Origin |\n"
            "| --- | --- | --- | --- | --- |\n"
            f"| `{self.lesson_name}` | `{self.lesson_id}` | [Shell path]({self.lesson_name}) | `active` | evidence |\n",
        )
        self.write(
            ".dev/lessons/templates/lesson-template.md",
            self.template_text(),
        )
        self.write(
            f".dev/lessons/environment/{self.lesson_name}",
            self.lesson_text(),
        )

    def close(self) -> None:
        self._temporary.cleanup()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def files(self) -> list[Path]:
        return sorted(
            path.relative_to(self.root)
            for path in self.root.rglob("*")
            if path.is_file()
        )

    def template_text(self) -> str:
        fields = (
            "Lesson ID",
            "Category",
            "Lifecycle",
            "Normative Authority",
            "Origin Evidence",
            "Promotion Target",
            "Supersedes",
            "Superseded By",
        )
        table = "\n".join(f"| {field} | value |" for field in fields)
        return "# LESSON-<ID>: <Title>\n\n" + table + "\n\n" + "\n\n".join(VALIDATOR.LESSON_REQUIRED_SECTIONS) + "\n"

    def lesson_text(self, lifecycle: str = "active", promotion: str = "`none`") -> str:
        table = f"""| Field | Value |
| --- | --- |
| Lesson ID | `{self.lesson_id}` |
| Category | `environment` |
| Lifecycle | `{lifecycle}` |
| Normative Authority | `none` |
| Origin Evidence | evidence |
| Promotion Target | {promotion} |
| Supersedes | `none` |
| Superseded By | `none` |
"""
        return (
            f"# {self.lesson_id}: Shell Path\n\n"
            + table
            + "\n"
            + "\n\n".join(VALIDATOR.LESSON_REQUIRED_SECTIONS)
            + "\n"
        )

    def validate(self) -> tuple[int, list[str]]:
        errors: list[str] = []
        count = VALIDATOR.validate_lesson_contract(self.files(), errors, root=self.root)
        return count, errors


class LessonContractTests(unittest.TestCase):
    def test_gwt_001_given_complete_lesson_packet_when_validated_then_passes(self) -> None:
        fixture = LessonFixture()
        try:
            count, errors = fixture.validate()
            self.assertEqual(1, count)
            self.assertEqual([], errors)
        finally:
            fixture.close()

    def test_gwt_002_given_required_entry_is_missing_when_validated_then_fails(self) -> None:
        fixture = LessonFixture()
        try:
            (fixture.root / ".dev/lessons/templates/lesson-template.md").unlink()
            _, errors = fixture.validate()
            self.assertTrue(any("missing required lesson contract path" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_003_given_unknown_lifecycle_when_cataloged_then_fails_closed(self) -> None:
        fixture = LessonFixture()
        try:
            index = fixture.root / ".dev/lessons/INDEX.MD"
            index.write_text(index.read_text(encoding="utf-8").replace("`active`", "`archived`"), encoding="utf-8", newline="\n")
            _, errors = fixture.validate()
            self.assertTrue(any("invalid lesson catalog row" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_004_given_promoted_lesson_without_target_when_validated_then_fails(self) -> None:
        fixture = LessonFixture()
        try:
            root_index = fixture.root / ".dev/lessons/INDEX.MD"
            root_index.write_text(root_index.read_text(encoding="utf-8").replace("`active`", "`promoted`"), encoding="utf-8", newline="\n")
            category_index = fixture.root / ".dev/lessons/environment/INDEX.MD"
            category_index.write_text(category_index.read_text(encoding="utf-8").replace("`active`", "`promoted`"), encoding="utf-8", newline="\n")
            fixture.write(f".dev/lessons/environment/{fixture.lesson_name}", fixture.lesson_text(lifecycle="promoted"))
            _, errors = fixture.validate()
            self.assertTrue(any("promoted lesson requires Promotion Target" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_005_given_lesson_section_is_missing_when_validated_then_fails(self) -> None:
        fixture = LessonFixture()
        try:
            lesson = fixture.root / ".dev/lessons/environment" / fixture.lesson_name
            lesson.write_text(lesson.read_text(encoding="utf-8").replace("## Verification\n", ""), encoding="utf-8", newline="\n")
            _, errors = fixture.validate()
            self.assertTrue(any("missing lesson section ## Verification" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_006_given_unindexed_lesson_document_when_validated_then_fails(self) -> None:
        fixture = LessonFixture()
        try:
            fixture.write(
                ".dev/lessons/environment/LESSON-ENV-002-unindexed.md",
                fixture.lesson_text().replace(fixture.lesson_id, "LESSON-ENV-002"),
            )
            _, errors = fixture.validate()
            self.assertTrue(any("lesson document is missing" in error for error in errors))
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
