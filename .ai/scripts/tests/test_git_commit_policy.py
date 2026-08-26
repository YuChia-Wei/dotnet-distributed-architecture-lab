#!/usr/bin/env python3
"""GWT tests for executable Git commit-message policy."""

from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

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

Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""


class GitCommitPolicyTests(unittest.TestCase):
    def validate(self, message: str, workflow_id: str | None = WORKFLOW_ID) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_message("abc123", message, POLICY, errors, workflow_id)
        return errors

    def validate_at(
        self,
        message: str,
        committed_at: str,
        workflow_id: str | None = WORKFLOW_ID,
    ) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_message(
            "abc123",
            message,
            POLICY,
            errors,
            workflow_id,
            committed_at=datetime.fromisoformat(committed_at),
        )
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

Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""
        errors = self.validate(message, workflow_id=None)
        self.assertTrue(any("lacks matching Assessment-Id trailer" in error for error in errors))

    def test_gwt_008_given_assessment_subject_and_matching_trailer_when_validated_then_passes(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Assessment-Id: ASM-20260715-001
Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""
        self.assertEqual([], self.validate(message, workflow_id=None))

    def test_gwt_009_given_standalone_assessment_in_workflow_range_when_validated_then_assessment_contract_applies(self) -> None:
        message = """docs(assessment): [ASM-20260715-001] add report

Assessment-Id: ASM-20260715-001
Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
"""
        self.assertEqual([], self.validate(message, workflow_id=WORKFLOW_ID))

    def test_gwt_010_given_workflow_range_when_selected_then_first_parent_excludes_merged_branch_history(self) -> None:
        with mock.patch.object(VALIDATOR, "git", return_value="abc123\ndef456\n") as git:
            commits = VALIDATOR.selected_commits(
                "base..HEAD",
                None,
                first_parent=True,
            )

        self.assertEqual(["abc123", "def456"], commits)
        git.assert_called_once_with(
            "rev-list",
            "--first-parent",
            "--reverse",
            "base..HEAD",
            root=VALIDATOR.ROOT,
        )

    def test_gwt_011_given_signature_without_reasoning_when_validated_then_fails(self) -> None:
        message = workflow_message().replace(
            "OpenAI Codex (gpt-5.6-sol, high)",
            "OpenAI Codex (gpt-5.6-sol)",
        )
        errors = self.validate(message)
        self.assertTrue(any("valid Co-Authored-By" in error for error in errors))

    def test_gwt_012_given_marked_subagent_contributor_when_validated_then_passes(self) -> None:
        message = workflow_message().replace(
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>",
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>\n"
            "Co-Authored-By: OpenAI Codex Sub-Agent (gpt-5.6-terra, medium) <noreply@openai.com>",
        )
        self.assertEqual([], self.validate(message))

    def test_gwt_013_given_unmarked_additional_contributor_when_validated_then_fails(self) -> None:
        message = workflow_message().replace(
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>",
            "Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>\n"
            "Co-Authored-By: Claude Code (claude-sonnet-5, extended) <noreply@anthropic.com>",
        )
        errors = self.validate(message)
        self.assertTrue(any("must mark the runtime with Sub-Agent" in error for error in errors))

    def test_gwt_014_given_provider_reasoning_label_when_validated_then_preserves_original(self) -> None:
        message = workflow_message().replace(
            "OpenAI Codex (gpt-5.6-sol, high)",
            "Claude Code (claude-sonnet-5, extended thinking)",
        ).replace("noreply@openai.com", "noreply@anthropic.com")
        self.assertEqual([], self.validate(message))

    def test_gwt_015_given_pre_policy_signature_when_validated_then_legacy_shape_passes(self) -> None:
        message = workflow_message().replace(
            "OpenAI Codex (gpt-5.6-sol, high)",
            "OpenAI Codex (GPT-5)",
        )
        errors: list[str] = []
        VALIDATOR.validate_message(
            "abc123",
            message,
            POLICY,
            errors,
            WORKFLOW_ID,
            committed_at=datetime.fromisoformat("2026-07-27T09:00:00+08:00"),
        )
        self.assertEqual([], errors)

    def test_gwt_016_given_current_issue_form_when_validated_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_at(
                workflow_message("docs(#176): clarify validation contract"),
                "2026-08-10T00:40:00+08:00",
            ),
        )

    def test_gwt_017_given_current_multiple_issue_form_when_validated_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_at(
                workflow_message("docs(#175,#176): reconcile validation boundaries"),
                "2026-08-10T00:40:00+08:00",
            ),
        )

    def test_gwt_018_given_literal_pipe_after_cutover_when_validated_then_fails(self) -> None:
        errors = self.validate_at(
            workflow_message("docs(#176|validation): reject literal pipe"),
            "2026-08-10T00:40:00+08:00",
        )
        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_019_given_literal_pipe_before_cutover_when_validated_then_passes(self) -> None:
        self.assertEqual(
            [],
            self.validate_at(
                workflow_message("docs(#176|validation): retain historical title"),
                "2026-08-10T00:39:59+08:00",
            ),
        )


if __name__ == "__main__":
    unittest.main()
