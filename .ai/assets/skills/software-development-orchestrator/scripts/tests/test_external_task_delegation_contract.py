#!/usr/bin/env python3
"""Focused regression tests for cross-task dispatch and terminal reporting."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[6]
DELEGATION_VALIDATOR_PATH = (
    ROOT
    / ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py"
)
CONTEXT_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-ai-context.py"
PROFILE = ROOT / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DELEGATION = load_module("external_task_delegation", DELEGATION_VALIDATOR_PATH)
CONTEXT = load_module("validate_ai_context_for_delegation", CONTEXT_VALIDATOR_PATH)
SCHEMA = DELEGATION.load_mapping(DELEGATION.SCHEMA_PATH)
SHA = "5" * 40


def valid_dispatch() -> dict:
    return {
        "schema_version": "1.1",
        "record_type": "external-task-dispatch",
        "delegation_id": "pr-195-hosted-gate-01",
        "task_kind": "long-running-validation",
        "source": {
            "task_id_source": "runtime-injected",
            "task_id": None,
            "final_integration_owner": "source-task",
        },
        "objective": {
            "goal": "Run the exact focused regression command and return one terminal report.",
            "non_goals": ["repair failures", "merge or mutate GitHub state"],
        },
        "subject": {
            "repository_root": "C:/repo",
            "commit_sha": SHA,
            "clean_worktree_required": True,
        },
        "execution": {
            "working_directory": "C:/repo",
            "argv": ["python", "focused-test.py", "-v"],
            "timeout_seconds": 300,
        },
        "permissions": {
            "read_scope": ["repository"],
            "write_scope": ["ignored-validation-artifacts"],
            "repair_allowed": False,
            "external_mutations": [],
            "secret_values": "prohibited",
        },
        "completion_delivery": {
            "primary": "source-task-callback",
            "fallback": "parent-event-wait",
            "destination": "source-task",
            "progress_updates": "terminal-only",
            "max_terminal_reports": 1,
            "report_schema": "same-contract#completion",
            "pre_send_validation": {
                "required": True,
                "validator_argv": [
                    "python",
                    ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py",
                    ".external-task/pr-195-hosted-gate-01-completion.yaml",
                    "--dispatch",
                    ".external-task/pr-195-hosted-gate-01-dispatch.yaml",
                ],
                "dispatch_ref": ".external-task/pr-195-hosted-gate-01-dispatch.yaml",
                "completion_ref": ".external-task/pr-195-hosted-gate-01-completion.yaml",
                "failure_action": "do-not-deliver-terminal-report",
                "payload_binding": "exact-validated-completion-record",
            },
        },
        "stop_conditions": [
            "preflight mismatch",
            "command terminal outcome",
            "execution timeout or interruption",
        ],
    }


def valid_completion() -> dict:
    return {
        "schema_version": "1.1",
        "record_type": "external-task-completion",
        "delegation_id": "pr-195-hosted-gate-01",
        "source_task_id": "source-019f",
        "delegated_task_id": "worker-019f",
        "subject": {
            "expected_commit_sha": SHA,
            "observed_commit_sha": SHA,
        },
        "preflight": {"commit_matches": True, "clean_worktree": True},
        "execution": {
            "working_directory": "C:/repo",
            "argv": ["python", "focused-test.py", "-v"],
        },
        "timing": {
            "started_at": "2026-08-12T01:00:00+08:00",
            "completed_at": "2026-08-12T01:00:02+08:00",
            "duration_seconds": 2,
        },
        "result": {
            "outcome": "passed",
            "exit_code": 0,
            "counts": {"selected": 10, "failed": 0, "blocked": 0},
        },
        "evidence": {"refs": ["runtime final"], "bounded_output": "10 passed"},
        "final_state": {"clean_worktree": True, "tracked_changes": []},
        "delivery": {
            "mode": "source-task-callback",
            "destination": "source-task",
            "terminal_report_number": 1,
            "schema_validation": {
                "outcome": "passed",
                "exit_code": 0,
                "validator_argv": [
                    "python",
                    ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py",
                    ".external-task/pr-195-hosted-gate-01-completion.yaml",
                    "--dispatch",
                    ".external-task/pr-195-hosted-gate-01-dispatch.yaml",
                ],
                "dispatch_ref": ".external-task/pr-195-hosted-gate-01-dispatch.yaml",
                "completion_ref": ".external-task/pr-195-hosted-gate-01-completion.yaml",
                "payload_binding": "exact-validated-completion-record",
            },
        },
    }


class ExternalTaskDelegationContractTests(unittest.TestCase):
    def test_gwt_001_given_canonical_schema_when_loaded_then_transport_has_callback_and_event_wait_paths(self) -> None:
        self.assertEqual([], DELEGATION.validate_schema_definition(SCHEMA))
        delivery = SCHEMA["dispatch"]["completion_delivery"]
        self.assertEqual(
            ["source-task-callback", "parent-event-wait"],
            delivery["primary_modes"],
        )
        self.assertEqual(
            "pending-awaiting-completion",
            SCHEMA["transport_semantics"]["parent_wait_timeout"],
        )
        self.assertEqual(
            "recoverable-by-one-terminal-readback",
            SCHEMA["transport_semantics"][
                "callback_failure_with_retrievable_terminal_report"
            ],
        )
        self.assertEqual(
            "BEGIN_EXTERNAL_TASK_COMPLETION",
            SCHEMA["completion_transport"]["begin_marker"],
        )
        self.assertEqual(
            "runtime-policy-owned-and-not-source-delivery",
            SCHEMA["transport_semantics"]["runtime_local_progress"],
        )

    def test_gwt_002_given_one_marked_prompt_when_parsed_then_dispatch_is_valid(self) -> None:
        record = valid_dispatch()
        prompt = (
            "Run only the bounded task below.\n"
            f"{DELEGATION.BEGIN_MARKER}\n"
            f"{yaml.safe_dump(record, sort_keys=False)}"
            f"{DELEGATION.END_MARKER}\n"
        )
        parsed = DELEGATION.extract_dispatch_from_prompt(prompt)
        self.assertEqual(record, parsed)
        self.assertEqual([], DELEGATION.validate_dispatch(parsed, SCHEMA))

    def test_gwt_003_given_duplicate_or_missing_envelope_when_parsed_then_it_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one"):
            DELEGATION.extract_dispatch_from_prompt("no envelope")
        duplicate = (
            f"{DELEGATION.BEGIN_MARKER}\n{{}}\n{DELEGATION.END_MARKER}\n"
            f"{DELEGATION.BEGIN_MARKER}\n{{}}\n{DELEGATION.END_MARKER}\n"
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            DELEGATION.extract_dispatch_from_prompt(duplicate)

    def test_gwt_004_given_callback_dispatch_when_destination_or_terminal_limit_drifts_then_it_is_rejected(self) -> None:
        record = valid_dispatch()
        record["completion_delivery"]["destination"] = "delegated-task"
        record["completion_delivery"]["max_terminal_reports"] = 2
        errors = DELEGATION.validate_dispatch(record, SCHEMA)
        self.assertTrue(any("destination must be source-task" in error for error in errors))
        self.assertTrue(any("max_terminal_reports must be 1" in error for error in errors))

    def test_gwt_005_given_runtime_without_child_callback_when_event_wait_selected_then_it_remains_valid(self) -> None:
        record = valid_dispatch()
        record["completion_delivery"].update(
            primary="parent-event-wait",
            fallback="single-terminal-readback",
        )
        self.assertEqual([], DELEGATION.validate_dispatch(record, SCHEMA))

    def test_gwt_006_given_matching_terminal_report_when_cross_checked_then_it_is_valid(self) -> None:
        dispatch = valid_dispatch()
        completion = valid_completion()
        message = (
            f"{DELEGATION.COMPLETION_BEGIN_MARKER}\n"
            f"{yaml.safe_dump(completion, sort_keys=False)}"
            f"{DELEGATION.COMPLETION_END_MARKER}\n"
        )
        self.assertEqual(completion, DELEGATION.extract_completion_from_message(message))
        self.assertEqual(
            [],
            DELEGATION.validate_completion(completion, SCHEMA, dispatch),
        )

    def test_gwt_007_given_callback_transport_failed_but_terminal_report_is_retrievable_then_one_readback_is_valid(self) -> None:
        completion = valid_completion()
        completion["delivery"]["mode"] = "single-terminal-readback"
        self.assertEqual(
            [],
            DELEGATION.validate_completion(completion, SCHEMA, valid_dispatch()),
        )

    def test_gwt_008_given_passed_report_when_subject_or_worktree_drifts_then_it_cannot_pass(self) -> None:
        completion = valid_completion()
        completion["subject"]["observed_commit_sha"] = "6" * 40
        completion["final_state"] = {
            "clean_worktree": False,
            "tracked_changes": ["tracked.txt"],
        }
        errors = DELEGATION.validate_completion(completion, SCHEMA, valid_dispatch())
        self.assertTrue(any("matching expected and observed" in error for error in errors))
        self.assertTrue(any("clean final worktree" in error for error in errors))
        self.assertTrue(any("no tracked changes" in error for error in errors))

    def test_gwt_009_given_capability_profile_1_4_when_ai_context_validator_runs_then_it_is_accepted(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        skills = {
            skill_id: {"status": "active", "capability_slots": [slot]}
            for slot, skill_id in profile["mappings"].items()
        }
        errors: list[str] = []
        CONTEXT.validate_capability_profile(skills, errors)
        self.assertEqual([], errors)

    def test_gwt_010_given_unknown_future_profile_schema_when_validated_then_it_is_rejected(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        profile["schema_version"] = "1.5"
        skills = {
            skill_id: {"status": "active", "capability_slots": [slot]}
            for slot, skill_id in profile["mappings"].items()
        }
        with tempfile.TemporaryDirectory(prefix="external-task-profile-") as temporary:
            path = Path(temporary) / "capability-profile.yaml"
            path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(CONTEXT, "CAPABILITY_PROFILE", path):
                CONTEXT.validate_capability_profile(skills, errors)
        self.assertTrue(any("schema_version must be 1.0, 1.1, 1.2, 1.3, or 1.4" in error for error in errors))

    def test_gwt_011_given_profile_1_4_without_delegation_schema_binding_when_validated_then_it_is_rejected(self) -> None:
        profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
        del profile["capability_contracts"]["test-execution"]["long_running"][
            "delegation_contract"
        ]
        skills = {
            skill_id: {"status": "active", "capability_slots": [slot]}
            for slot, skill_id in profile["mappings"].items()
        }
        with tempfile.TemporaryDirectory(prefix="external-task-profile-") as temporary:
            path = Path(temporary) / "capability-profile.yaml"
            path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
            errors: list[str] = []
            with mock.patch.object(CONTEXT, "CAPABILITY_PROFILE", path):
                CONTEXT.validate_capability_profile(skills, errors)
        self.assertTrue(any("test-execution.long_running" in error for error in errors))

    def test_gwt_012_given_dispatch_without_mandatory_pre_send_validation_when_validated_then_it_is_rejected(self) -> None:
        dispatch = valid_dispatch()
        del dispatch["completion_delivery"]["pre_send_validation"]
        errors = DELEGATION.validate_dispatch(dispatch, SCHEMA)
        self.assertTrue(
            any("pre_send_validation is required" in error for error in errors)
        )

    def test_gwt_013_given_completion_without_passing_schema_validation_when_validated_then_it_is_rejected(self) -> None:
        completion = valid_completion()
        completion["delivery"]["schema_validation"]["outcome"] = "failed"
        completion["delivery"]["schema_validation"]["exit_code"] = 1
        errors = DELEGATION.validate_completion(completion, SCHEMA, valid_dispatch())
        self.assertTrue(
            any("schema_validation.outcome must be passed" in error for error in errors)
        )
        self.assertTrue(
            any("schema_validation.exit_code must be zero" in error for error in errors)
        )

    def test_gwt_014_given_validated_completion_record_drift_when_cross_checked_then_it_is_rejected(self) -> None:
        completion = valid_completion()
        completion["delivery"]["schema_validation"]["completion_ref"] = (
            ".external-task/other-completion.yaml"
        )
        errors = DELEGATION.validate_completion(completion, SCHEMA, valid_dispatch())
        self.assertTrue(
            any(
                "schema_validation.completion_ref must match dispatch" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
