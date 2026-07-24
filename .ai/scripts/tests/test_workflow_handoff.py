#!/usr/bin/env python3
"""GWT tests for fail-closed workflow receiving checkpoints."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-workflow-handoff.py"
SPEC = importlib.util.spec_from_file_location("validate_workflow_handoff", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
POLICY = VALIDATOR.load_policy()
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
COMMIT = "a" * 40
DIGEST = "b" * 64


def valid_checkpoint() -> dict:
    return {
        "schema_version": "1.0",
        "checkpoint_id": "2026-07-21-example-TASK-001-handoff",
        "created_at": "2026-07-21T12:00:00+08:00",
        "repository": {
            "root": ".",
            "branch": "codex/2026-07-21-example",
            "validated_commit": COMMIT,
            "checkpoint_commit_source": "containing-commit",
            "dirty_state": "clean",
            "status_porcelain_sha256": EMPTY_SHA,
        },
        "workflow": {
            "workflow_id": "2026-07-21-example",
            "task_id": "TASK-001",
        },
        "resume": {
            "last_completed_action": "Committed the bounded implementation.",
            "exact_next_action": "Run the release phase check.",
            "hidden_context_required": False,
        },
        "critical_gate": {
            "command": "bash .ai/scripts/check-all.sh --critical",
            "observed_at": "2026-07-21T12:01:00+08:00",
            "exit_code": 0,
            "outcome": "passed",
            "output": {
                "normalization": "utf8-lf",
                "sha256": DIGEST,
                "line_count": 2,
                "tail": ["Required Failed: 0", "All required checks passed."],
            },
        },
        "continuation": {
            "allowed": True,
            "mode": "normal",
            "reason": "Critical gate passed.",
            "repair_task_id": None,
            "failure_ids": [],
        },
        "release_handoff": False,
        "release_phase_check": None,
        "execution_provenance": {
            "runtime": "OpenAI Codex",
            "model": "GPT 5.6 sol",
            "reasoning_effort": "極高",
            "model_source": "user-declared",
            "evidence_ref": "owner declaration in the active task",
        },
        "attribution": {
            "preservation_required": True,
            "evidence_union_version": "1.0",
            "selected_evidence": {
                "kind": "repository-created-local-ai-trailer",
                "commit": COMMIT,
                "author": "Example <example@example.test>",
                "committer": "Example <example@example.test>",
                "signature_status": "unsigned",
                "session_ref": None,
                "observed_trailer": (
                    "Co-Authored-By: OpenAI Codex "
                    "(gpt-5.6-sol, xhigh) <noreply@openai.com>"
                ),
                "message_sha256": DIGEST,
                "fixture_ref": "git:" + COMMIT,
            },
            "fixture_status": [
                {
                    "path_id": "codex-local",
                    "status": "captured",
                    "commit": COMMIT,
                    "evidence_ref": "git:" + COMMIT,
                    "reason": None,
                },
                {
                    "path_id": "copilot-cli",
                    "status": "blocked",
                    "commit": None,
                    "evidence_ref": "evidence/provider-research.md",
                    "reason": "No real provider-generated commit fixture is available.",
                },
                {
                    "path_id": "copilot-cloud-agent",
                    "status": "blocked",
                    "commit": None,
                    "evidence_ref": "evidence/provider-research.md",
                    "reason": "No real provider-generated commit fixture is available.",
                },
                {
                    "path_id": "claude",
                    "status": "blocked",
                    "commit": None,
                    "evidence_ref": "evidence/provider-research.md",
                    "reason": "No real provider-generated commit fixture is available.",
                },
            ],
        },
    }


class WorkflowHandoffTests(unittest.TestCase):
    def validate(self, data: dict) -> list[str]:
        return VALIDATOR.validate_checkpoint_data(data, POLICY)

    def test_gwt_001_given_complete_checkpoint_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(valid_checkpoint()))

    def test_gwt_002_given_missing_repository_pin_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["repository"]["validated_commit"] = "<40-character-git-sha>"
        errors = self.validate(data)
        self.assertTrue(any("placeholder must be resolved" in error for error in errors))

    def test_gwt_003_given_red_critical_gate_when_normal_continuation_then_fails(self) -> None:
        data = valid_checkpoint()
        data["critical_gate"].update(exit_code=1, outcome="failed")
        errors = self.validate(data)
        self.assertTrue(any("failed critical gate must block" in error for error in errors))

    def test_gwt_004_given_red_gate_and_exact_repair_task_when_validated_then_passes(self) -> None:
        data = valid_checkpoint()
        data["critical_gate"].update(exit_code=1, outcome="failed")
        data["continuation"].update(
            allowed=True,
            mode="repair-only",
            reason="Only repair FAIL-GATE-001.",
            repair_task_id="TASK-001",
            failure_ids=["FAIL-GATE-001"],
        )
        self.assertEqual([], self.validate(data))

    def test_gwt_005_given_unbounded_output_tail_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["critical_gate"]["output"]["line_count"] = 41
        data["critical_gate"]["output"]["tail"] = ["line"] * 41
        errors = self.validate(data)
        self.assertTrue(any("exceeds 40 lines" in error for error in errors))

    def test_gwt_006_given_user_declared_model_when_labels_missing_then_fails(self) -> None:
        data = valid_checkpoint()
        data["execution_provenance"]["model"] = None
        errors = self.validate(data)
        self.assertTrue(any("execution_provenance.model" in error for error in errors))

    def test_gwt_007_given_release_handoff_without_phase_check_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["release_handoff"] = True
        errors = self.validate(data)
        self.assertTrue(any("release_phase_check" in error for error in errors))

    def test_gwt_008_given_unowned_release_command_when_validated_then_fails_closed(self) -> None:
        data = valid_checkpoint()
        data["release_handoff"] = True
        data["release_phase_check"] = copy.deepcopy(data["critical_gate"])
        data["release_phase_check"]["phase"] = "candidate"
        data["release_phase_check"]["command"] = (
            "python .ai/scripts/validate-ai-context-release-state.py "
            "--release v0.5.0 --phase candidate"
        )
        errors = self.validate(data)
        self.assertTrue(any("REL-owned release phase contract is unavailable" in error for error in errors))

    def test_gwt_009_given_blocked_fixture_without_reason_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["attribution"]["fixture_status"][1]["reason"] = ""
        errors = self.validate(data)
        self.assertTrue(any("reason: must be a non-empty string" in error for error in errors))

    def test_gwt_010_given_native_authorship_without_signature_or_session_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        selected = data["attribution"]["selected_evidence"]
        selected["kind"] = "provider-native-authorship-or-signed-session"
        selected["observed_trailer"] = None
        selected["signature_status"] = "unsigned"
        selected["session_ref"] = None
        errors = self.validate(data)
        self.assertTrue(any("verified signature or session_ref" in error for error in errors))

    def test_gwt_011_given_git_write_command_when_validator_api_called_then_rejects(self) -> None:
        allowlist = set(POLICY["git_read_allowlist"])
        for command in ("commit", "rebase", "reset", "tag", "push"):
            with self.subTest(command=command):
                with self.assertRaisesRegex(ValueError, "not read-only allowlisted"):
                    VALIDATOR.git_read(REPO_ROOT, allowlist, command)

    def test_gwt_012_given_clean_state_with_nonempty_digest_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["repository"]["status_porcelain_sha256"] = DIGEST
        errors = self.validate(data)
        self.assertTrue(any("clean state requires" in error for error in errors))

    def test_gwt_013_given_selected_fixture_bound_to_another_commit_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["attribution"]["fixture_status"][0]["commit"] = "c" * 40
        errors = self.validate(data)
        self.assertTrue(any("must match a captured fixture" in error for error in errors))

    def test_gwt_014_given_required_provider_path_missing_when_validated_then_fails(self) -> None:
        data = valid_checkpoint()
        data["attribution"]["fixture_status"] = data["attribution"]["fixture_status"][:-1]
        errors = self.validate(data)
        self.assertTrue(any("missing required fixture paths" in error for error in errors))

    def test_gwt_015_given_registered_real_instance_when_all_validates_then_it_is_checked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="handoff-registry-") as temporary:
            root = Path(temporary)
            (root / ".dev/workflows/checkpoints").mkdir(parents=True)
            (root / ".dev/releases").mkdir()
            (root / ".ai/distribution").mkdir(parents=True)
            checkpoint_path = ".dev/workflows/checkpoints/TASK-001.yaml"
            (root / checkpoint_path).write_text(
                yaml.safe_dump(valid_checkpoint(), sort_keys=False),
                encoding="utf-8",
            )
            (root / ".dev/workflows/handoff-checkpoints.yaml").write_text(
                yaml.safe_dump(
                    {"schema_version": "1.0", "checkpoints": [checkpoint_path]},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            checked, errors, available = VALIDATOR.validate_registered_checkpoints(
                root, POLICY
            )

            self.assertTrue(available)
            self.assertEqual(1, checked)
            self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
