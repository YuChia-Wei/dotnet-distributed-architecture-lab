#!/usr/bin/env python3
"""GWT tests for fail-closed standalone assessment artifact validation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-assessment-artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_assessment_artifacts", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class AssessmentFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="assessment-artifacts-")
        self.root = Path(self._temporary.name)
        self.assessments = self.root / ".dev/assessments"
        (self.assessments / "templates").mkdir(parents=True)
        (self.root / ".ai/assets/skills/example/templates").mkdir(parents=True)
        (self.assessments / "README.MD").write_text("# Assessments\n", encoding="utf-8")
        (self.assessments / "templates/assessment-locator-template.yaml").write_text(
            "template: assessment\n", encoding="utf-8"
        )
        (self.root / ".ai/assets/skills/example/templates/report.md").write_text(
            "# Report Template\n", encoding="utf-8"
        )
        self.write_index([])

    def close(self) -> None:
        self._temporary.cleanup()

    def manifest(self, assessment_id: str, status: str = "final") -> dict:
        return {
            "schema_version": "1.0",
            "assessment_id": assessment_id,
            "commit_search_id": assessment_id,
            "assessment_type": "test-review",
            "title": "Test Review",
            "owner_skill": "example",
            "status": status,
            "report": "report.md",
            "artifact_branch": f"codex/assessment/{assessment_id.lower()}",
            "base_branch": "main",
            "created_at": "2026-07-13T12:00:00+08:00",
            "updated_at": "2026-07-13T12:00:00+08:00",
            "template_source": ".dev/assessments/templates/assessment-locator-template.yaml",
            "template_version": "1.0.0",
            "report_template_source": ".ai/assets/skills/example/templates/report.md",
            "report_template_version": "1.0.0",
            "subject_ref": {"repository": "example/repo", "branch": "main", "commit": "a" * 40},
            "scope": {"included": [".ai/**"], "excluded": ["src/**"]},
            "relations": {
                "supersedes": [], "superseded_by": [], "related_assessments": [],
                "workflow_refs": [], "backlog_refs": [], "adr_refs": []
            },
            "resume": {"last_completed_action": "reviewed", "next_action": "", "blockers": []},
        }

    def add(self, assessment_id: str, status: str = "final") -> dict:
        directory = self.assessments / assessment_id
        directory.mkdir()
        manifest = self.manifest(assessment_id, status)
        (directory / "assessment.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
        )
        (directory / "report.md").write_text("# Report\n", encoding="utf-8")
        self.write_index([manifest])
        return manifest

    def save(self, manifest: dict) -> None:
        path = self.assessments / manifest["assessment_id"] / "assessment.yaml"
        path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    def write_index(self, manifests: list[dict], force_section: str | None = None) -> None:
        sections = {
            "Draft Assessments": [], "Final Assessments": [],
            "Superseded Or Withdrawn Assessments": []
        }
        for item in manifests:
            section = force_section or VALIDATOR.STATUS_SECTIONS[item["status"]]
            sections[section].append(
                f"| [`{item['assessment_id']}`]({item['assessment_id']}/assessment.yaml) "
                f"| {item['title']} | `{item['assessment_type']}` | `{item['owner_skill']}` "
                f"| `{item['status']}` | `{item['subject_ref']['commit']}` "
                f"| `{item['updated_at']}` | [report]({item['assessment_id']}/report.md) |"
            )
        lines = ["# Assessment Index", ""]
        for section, rows in sections.items():
            lines.extend([
                f"## {section}", "",
                "| Assessment | Title | Type | Owner | Status | Subject Commit | Updated | Report |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
                *rows, "",
            ])
        (self.assessments / "INDEX.MD").write_text("\n".join(lines), encoding="utf-8")

    def validate(self) -> list[str]:
        errors, _ = VALIDATOR.validate_assessments(self.root)
        return errors


class AssessmentArtifactValidationTests(unittest.TestCase):
    def test_gwt_001_given_empty_catalog_when_validated_then_passes(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given the assessment catalog has no instances.
            # When structural validation runs.
            errors = fixture.validate()
            # Then the empty initialized catalog is valid.
            self.assertEqual([], errors)
        finally:
            fixture.close()

    def test_gwt_002_given_valid_final_assessment_when_validated_then_passes(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given a complete final assessment and matching index row.
            fixture.add("ASM-20260713-001")
            # When structural validation runs.
            errors = fixture.validate()
            # Then the assessment passes.
            self.assertEqual([], errors)
        finally:
            fixture.close()

    def test_gwt_003_given_id_or_search_id_mismatch_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given locator identity differs from its directory and search ID.
            manifest = fixture.add("ASM-20260713-001")
            manifest["assessment_id"] = "ASM-20260713-002"
            manifest["commit_search_id"] = "ASM-20260713-003"
            path = fixture.assessments / "ASM-20260713-001/assessment.yaml"
            path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            # When structural validation runs.
            errors = fixture.validate()
            # Then both stable identity contracts fail closed.
            self.assertTrue(any("assessment_id must match" in error for error in errors))
            self.assertTrue(any("commit_search_id must equal" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_004_given_missing_report_or_index_row_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given a locator has neither its report nor index discovery row.
            fixture.add("ASM-20260713-001")
            (fixture.assessments / "ASM-20260713-001/report.md").unlink()
            fixture.write_index([])
            # When structural validation runs.
            errors = fixture.validate()
            # Then report and discovery coverage both fail.
            self.assertTrue(any("missing report.md" in error for error in errors))
            self.assertTrue(any("missing INDEX.MD row" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_005_given_invalid_subject_or_timestamp_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given the subject SHA and created timestamp are not durable evidence pointers.
            manifest = fixture.add("ASM-20260713-001")
            manifest["subject_ref"]["commit"] = "abc123"
            manifest["created_at"] = "2026-07-13T12:00:00"
            fixture.save(manifest)
            fixture.write_index([manifest])
            # When structural validation runs.
            errors = fixture.validate()
            # Then SHA width and explicit offset requirements fail.
            self.assertTrue(any("40-character Git SHA" in error for error in errors))
            self.assertTrue(any("explicit UTC offset" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_006_given_dangling_assessment_relation_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given a final assessment references a missing related assessment.
            manifest = fixture.add("ASM-20260713-001")
            manifest["relations"]["related_assessments"] = ["ASM-20260713-999"]
            fixture.save(manifest)
            # When structural validation runs.
            errors = fixture.validate()
            # Then the dangling relationship fails closed.
            self.assertTrue(any("references missing assessment" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_007_given_draft_without_resume_action_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given an interrupted draft has no exact continuation action.
            manifest = fixture.add("ASM-20260713-001", status="draft")
            manifest["resume"]["next_action"] = ""
            fixture.save(manifest)
            fixture.write_index([manifest])
            # When structural validation runs.
            errors = fixture.validate()
            # Then resume safety fails closed.
            self.assertTrue(any("requires resume.next_action" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_008_given_row_in_wrong_lifecycle_section_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given a final assessment is cataloged under draft assessments.
            manifest = fixture.add("ASM-20260713-001")
            fixture.write_index([manifest], force_section="Draft Assessments")
            # When structural validation runs.
            errors = fixture.validate()
            # Then index lifecycle parity fails.
            self.assertTrue(any("INDEX.MD row differs" in error for error in errors))
        finally:
            fixture.close()

    def test_gwt_009_given_duplicate_index_rows_when_validated_then_fails(self) -> None:
        fixture = AssessmentFixture()
        try:
            # Given the same assessment is cataloged twice.
            manifest = fixture.add("ASM-20260713-001")
            row = (
                f"| [`{manifest['assessment_id']}`]({manifest['assessment_id']}/assessment.yaml) "
                f"| {manifest['title']} | `{manifest['assessment_type']}` | `{manifest['owner_skill']}` "
                f"| `{manifest['status']}` | `{manifest['subject_ref']['commit']}` "
                f"| `{manifest['updated_at']}` | [report]({manifest['assessment_id']}/report.md) |"
            )
            index = fixture.assessments / "INDEX.MD"
            index.write_text(index.read_text(encoding="utf-8") + row + "\n", encoding="utf-8")
            # When structural validation runs.
            errors = fixture.validate()
            # Then duplicate discovery state fails closed.
            self.assertTrue(any("duplicate row" in error for error in errors))
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
