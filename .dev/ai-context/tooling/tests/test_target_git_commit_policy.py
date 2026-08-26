#!/usr/bin/env python3
"""GWT coverage for the target-owned commit-policy composition."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
VALIDATOR_PATH = (
    ROOT
    / ".dev/ai-context/tooling/git-commit-policy/validate-target-git-commits.py"
)
SPEC = importlib.util.spec_from_file_location("target_git_commit_policy", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load target validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
CONFIG = VALIDATOR.load_target_config()
EXACT_SHA = "ad194beb3fb61a18b6870093b704264746c1516b"


def assessment_message(subject: str = "docs(assessment): [ASM-20260812-002] add report") -> str:
    return f"""{subject}

Co-Authored-By: OpenAI Codex (gpt-5, provider-default) <noreply@openai.com>
"""


def workflow_message(subject: str) -> str:
    return f"""{subject}

Why:
Exercise the prospective subject boundary.

What:
Validate one exact title grammar.

Validation:
Target policy unit test.

Workflow:
2026-08-12-ai-context-v0-13-upgrade

Assessment-Id: ASM-20260813-004

Co-Authored-By: OpenAI Codex (gpt-5, provider-default) <noreply@openai.com>
"""


class TargetGitCommitPolicyTests(unittest.TestCase):
    def test_gwt_001_exact_exception_waives_only_missing_matching_trailer(self) -> None:
        self.assertEqual(
            [],
            VALIDATOR.validate_target_message(
                EXACT_SHA,
                assessment_message(),
                CONFIG,
                committed_at=datetime.fromisoformat("2026-08-12T22:20:00+08:00"),
            ),
        )

    def test_gwt_002_wrong_sha_does_not_receive_exception(self) -> None:
        errors = VALIDATOR.validate_target_message(
            "b" * 40,
            assessment_message(),
            CONFIG,
            committed_at=datetime.fromisoformat("2026-08-12T22:20:00+08:00"),
        )
        self.assertTrue(any("lacks matching Assessment-Id trailer" in error for error in errors))

    def test_gwt_003_other_errors_remain_enforced_for_exact_sha(self) -> None:
        errors = VALIDATOR.validate_target_message(
            EXACT_SHA,
            assessment_message("invalid subject"),
            CONFIG,
            committed_at=datetime.fromisoformat("2026-08-12T22:20:00+08:00"),
        )
        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_004_target_effective_boundary_preserves_legacy_signature(self) -> None:
        message = """fix(ai-context): preserve adoption boundary

Co-Authored-By: OpenAI Codex <noreply@openai.com>
"""
        self.assertEqual(
            [],
            VALIDATOR.validate_target_message(
                "c" * 40,
                message,
                CONFIG,
                committed_at=datetime.fromisoformat("2026-08-12T22:00:00+08:00"),
            ),
        )

    def test_gwt_005_unknown_waiver_fails_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["assessment_historical_exceptions"][0]["waived_error"] = "skip-all"
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(any("waived_error is unsupported" in error for error in errors))

    def test_gwt_006_wrong_assessment_id_does_not_receive_exception(self) -> None:
        errors = VALIDATOR.validate_target_message(
            EXACT_SHA,
            assessment_message().replace("ASM-20260812-002", "ASM-20260812-003"),
            CONFIG,
            committed_at=datetime.fromisoformat("2026-08-12T22:20:00+08:00"),
        )
        self.assertTrue(any("ASM-20260812-003" in error for error in errors))

    def test_gwt_007_non_list_exception_collection_fails_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["assessment_historical_exceptions"] = {}
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(any("must be a list" in error for error in errors))

    def test_gwt_008_duplicate_exception_sha_fails_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["assessment_historical_exceptions"].append(
            copy.deepcopy(config["assessment_historical_exceptions"][0])
        )
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(any("duplicate historical exception" in error for error in errors))

    def test_gwt_009_invalid_assessment_and_missing_evidence_fail_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        exception = config["assessment_historical_exceptions"][0]
        exception["assessment_id"] = "ASM-invalid"
        exception["evidence"] = ".dev/does-not-exist.yaml"
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(any("assessment_id is invalid" in error for error in errors))
        self.assertTrue(any("evidence does not exist" in error for error in errors))

    def test_gwt_010_timezone_naive_boundary_fails_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["ai_signature"]["effective_at_override"] = "2026-08-12T22:08:09"
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(any("must include a timezone" in error for error in errors))

    def test_gwt_011_framework_dependency_hash_drift_fails_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["package_validator"]["sha256"] = "0" * 64
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(any("validator hash mismatch" in error for error in errors))

    def test_gwt_012_last_legacy_commit_accepts_pipe_meta_notation(self) -> None:
        self.assertEqual(
            [],
            VALIDATOR.validate_target_message(
                "d" * 40,
                workflow_message("docs(#1|ai-context): retain legacy history"),
                CONFIG,
                workflow_id="2026-08-12-ai-context-v0-13-upgrade",
                committed_at=datetime.fromisoformat("2026-08-13T11:05:11+08:00"),
            ),
        )

    def test_gwt_013_boundary_accepts_issue_only_subject(self) -> None:
        self.assertEqual(
            [],
            VALIDATOR.validate_target_message(
                "e" * 40,
                workflow_message("chore(#1): adopt v0.12 grammar"),
                CONFIG,
                workflow_id="2026-08-12-ai-context-v0-13-upgrade",
                committed_at=datetime.fromisoformat("2026-08-13T11:05:12+08:00"),
            ),
        )

    def test_gwt_014_boundary_accepts_scope_only_subject(self) -> None:
        self.assertEqual(
            [],
            VALIDATOR.validate_target_message(
                "f" * 40,
                workflow_message("docs(ai-context): document v0.12 grammar"),
                CONFIG,
                workflow_id="2026-08-12-ai-context-v0-13-upgrade",
                committed_at=datetime.fromisoformat("2026-08-13T11:05:12+08:00"),
            ),
        )

    def test_gwt_015_boundary_rejects_pipe_subject(self) -> None:
        errors = VALIDATOR.validate_target_message(
            "1" * 40,
            workflow_message("chore(#1|ai-context): reject legacy grammar"),
            CONFIG,
            workflow_id="2026-08-12-ai-context-v0-13-upgrade",
            committed_at=datetime.fromisoformat("2026-08-13T11:05:12+08:00"),
        )
        self.assertTrue(any("subject does not match" in error for error in errors))

    def test_gwt_016_naive_subject_boundary_fails_closed(self) -> None:
        config = copy.deepcopy(CONFIG)
        config["commit_subject"]["effective_at_override"] = "2026-08-13T11:05:12"
        errors = VALIDATOR.validate_target_config(config)
        self.assertTrue(
            any(
                "commit_subject.effective_at_override must include a timezone"
                in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
