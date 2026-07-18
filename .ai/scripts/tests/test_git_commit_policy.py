#!/usr/bin/env python3
"""GWT tests for executable Git commit-message policy."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-git-commits.py"
POLICY_PATH = REPO_ROOT / ".dev/standards/GIT-COMMIT-POLICY.yaml"
SPEC = importlib.util.spec_from_file_location("validate_git_commits", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
POLICY = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
WORKFLOW_ID = "2026-07-15-example"


def workflow_message(subject: str = "fix(ai-context): enforce policy") -> str:
    return f"""{subject}

Why
Policy prose alone cannot fail closed.

What
Add executable validation.

Validation
- policy GWT

Workflow
{WORKFLOW_ID} / TASK-001

Co-Authored-By: OpenAI Codex (GPT-5) <noreply@openai.com>
"""


class GitCommitPolicyTests(unittest.TestCase):
    def validate(self, message: str, workflow_id: str | None = WORKFLOW_ID) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_message("abc123", message, POLICY, errors, workflow_id)
        return errors

    def test_gwt_001_given_valid_workflow_commit_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(workflow_message()))

    def test_gwt_002_given_invalid_subject_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message("updated some files"))
        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_003_given_missing_section_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message().replace("\nValidation\n", "\nChecks\n"))
        self.assertTrue(any("missing workflow body sections: Validation" in error for error in errors))

    def test_gwt_004_given_wrong_workflow_identity_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message().replace(WORKFLOW_ID, "2026-07-15-other"))
        self.assertTrue(any("does not identify" in error for error in errors))

    def test_gwt_005_given_nonfinal_ai_trailer_when_validated_then_fails(self) -> None:
        errors = self.validate(workflow_message() + "Unexpected final line\n")
        self.assertTrue(any("final non-empty line" in error for error in errors))

    def test_gwt_006_given_merge_commit_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(workflow_message("merge(ai-context): integrate workflow")))

    def test_gwt_007_given_assessment_subject_without_matching_trailer_when_validated_then_fails(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Co-Authored-By: OpenAI Codex (GPT-5) <noreply@openai.com>
"""
        errors = self.validate(message, workflow_id=None)
        self.assertTrue(any("lacks matching Assessment-Id trailer" in error for error in errors))

    def test_gwt_008_given_assessment_subject_and_matching_trailer_when_validated_then_passes(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Assessment-Id: ASM-20260715-001
Co-Authored-By: OpenAI Codex (GPT-5) <noreply@openai.com>
"""
        self.assertEqual([], self.validate(message, workflow_id=None))


if __name__ == "__main__":
    unittest.main()
