#!/usr/bin/env python3
"""GWT checks for development contract fields and local fail-closed rules.

End-to-end activation and fresh-session acceptance live in
test_software_development_orchestrator_acceptance.py.
"""

from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
PROFILE = ROOT / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"
VALIDATOR_PATH = ROOT / ".ai/scripts/validate-workflow-artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_workflow_artifacts", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
CREATED = VALIDATOR.DEVELOPMENT_ACCEPTANCE_CONTRACT_AT


def valid_task(*, status: str = "in_progress", slot: str = "review") -> dict:
    return {
        "task_id": "DEV-001",
        "template_source": VALIDATOR.DEV_TASK_TEMPLATE,
        "template_version": "1.3.0",
        "owner_skill": "code-reviewer",
        "status": status,
        "inputs": {},
        "execution": {
            "capability_slot": slot,
            "approval_contract": {
                "status": "not-required",
                "required_before": "",
                "authorization_source": [],
                "pending_decision": "",
            },
            "implementation_contract": None,
            "test_execution_contract": None,
            "spec_compliance": {
                "selected": False,
                "activation_source": [],
                "expected_outcome": "not-applicable",
            },
            "commit_checkpoint": "coherent-batch: DEV-001",
        },
        "results": {
            "summary": "Validated task.",
            "test_execution": [],
            "spec_compliance": {
                "outcome": "not-applicable",
                "coverage_percent": None,
                "evidence": [],
            },
            "commits": ["containing-commit"] if status == "completed" else [],
        },
    }


def valid_implementation_task() -> dict:
    task = valid_task(slot="implementation")
    task["owner_skill"] = "slice-implementer"
    task["execution"]["approval_contract"] = {
        "status": "approved",
        "required_before": "implementation",
        "authorization_source": ["owner approval in workflow#DEV-001"],
        "pending_decision": "",
    }
    task["execution"]["implementation_contract"] = {
        "intent": "feature",
        "execution_mode": "command",
        "overlays": [],
        "authorization_source": ["owner approval in workflow#DEV-001"],
        "normative_truth": [".dev/specs/example.md"],
        "finding_evidence": [],
        "subject_revision": "",
        "acceptance_criteria": ["The bounded behavior is implemented."],
    }
    return task


def valid_test_task(*, status: str = "completed") -> dict:
    task = valid_task(status=status, slot="test-execution")
    task["owner_skill"] = "software-development-orchestrator"
    task["execution"]["test_execution_contract"] = {
        "provider": "target-profile-commands",
        "target_owned": {
            "working_directory": ".",
            "commands": [
                {"level": "unit", "command": "python -m unittest unit"},
                {"level": "integration", "command": "python -m unittest integration"},
            ],
            "prerequisites": [],
            "environment_boundary": [],
            "policy": ["Both default levels are required for closeout."],
        },
        "selected_levels": ["unit", "integration"],
        "required_for_closeout": ["unit", "integration"],
        "conditional_selection_sources": [],
        "outcomes": [
            {
                "level": "unit",
                "outcome": "passed",
                "evidence": ["unit: exit 0"],
                "deferral_owner": "",
                "follow_up": "",
            },
            {
                "level": "integration",
                "outcome": "passed",
                "evidence": ["integration: exit 0"],
                "deferral_owner": "",
                "follow_up": "",
            },
        ],
    }
    return task


def validate_task(task: dict) -> list[str]:
    errors: list[str] = []
    for validator in (
        VALIDATOR.validate_development_approval_contract,
        VALIDATOR.validate_test_execution_contract,
        VALIDATOR.validate_spec_compliance_contract,
        VALIDATOR.validate_development_commit_checkpoint,
    ):
        validator(task, "task.json", errors, CREATED)
    return errors


class DevWorkflowCapabilityContractGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))

    def test_gwt_001_given_test_execution_when_profile_loaded_then_it_is_optional_and_unmapped(self) -> None:
        self.assertEqual("1.2", self.profile["schema_version"])
        self.assertIn("test-execution", self.profile["allowed_slots"])
        self.assertNotIn("test-execution", self.profile["required_slots"])
        self.assertNotIn("test-execution", self.profile["mappings"])

    def test_gwt_002_given_no_dedicated_test_skill_when_provider_order_checked_then_target_truth_precedes_fallback(self) -> None:
        contract = self.profile["capability_contracts"]["test-execution"]
        self.assertEqual(
            ["target-profile-commands", "evaluated-external-skill", "fallback-contract"],
            contract["provider_order"],
        )
        self.assertEqual(["unit", "integration"], contract["default_levels"])

    def test_gwt_003_given_test_outcomes_when_closeout_classifies_results_then_blocked_is_not_passed(self) -> None:
        outcomes = self.profile["capability_contracts"]["test-execution"]["outcomes"]
        self.assertEqual(
            [
                "passed",
                "failed",
                "blocked-by-environment",
                "not-applicable",
                "deferred-with-owner",
            ],
            outcomes,
        )
        self.assertNotEqual("passed", "blocked-by-environment")

    def test_gwt_004_given_specialized_tests_when_profile_loaded_then_they_are_conditional(self) -> None:
        conditional = self.profile["capability_contracts"]["test-execution"]["conditional_levels"]
        self.assertEqual(
            ["e2e", "browser", "playwright", "environment-dependent"],
            conditional,
        )

    def test_gwt_005_given_profile_is_loaded_then_it_declares_the_preclassified_activation_contract(self) -> None:
        activation = self.profile["orchestration_contract"]["activation"]
        self.assertEqual(
            "high-level-multi-stage-software-development",
            activation["intent_class"],
        )
        self.assertFalse(activation["skill_name_required"])
        self.assertEqual(
            ["requested-outcome", "current-artifacts", "repository-policy", "approval-state"],
            activation["routing_basis"],
        )

    def test_gwt_006_given_approval_is_pending_when_implementation_is_created_then_it_fails_closed(self) -> None:
        task = valid_implementation_task()
        task["execution"]["approval_contract"] = {
            "status": "awaiting-approval",
            "required_before": "implementation",
            "authorization_source": [],
            "pending_decision": "Owner must approve the specification.",
        }
        errors = validate_task(task)
        self.assertTrue(any("blocks creation or execution" in error for error in errors))

        approved = valid_implementation_task()
        self.assertEqual([], validate_task(approved))
        approved["execution"]["approval_contract"]["authorization_source"] = []
        self.assertTrue(
            any("requires authorization_source evidence" in error for error in validate_task(approved))
        )

    def test_gwt_007_given_specialized_test_selection_when_source_is_missing_then_it_fails(self) -> None:
        task = valid_test_task()
        contract = task["execution"]["test_execution_contract"]
        contract["selected_levels"].append("e2e")
        contract["required_for_closeout"].append("e2e")
        contract["target_owned"]["commands"].append(
            {"level": "e2e", "command": "python -m unittest e2e"}
        )
        contract["outcomes"].append(
            {
                "level": "e2e",
                "outcome": "passed",
                "evidence": ["e2e: exit 0"],
                "deferral_owner": "",
                "follow_up": "",
            }
        )
        errors = validate_task(task)
        self.assertTrue(any("require conditional_selection_sources" in error for error in errors))
        contract["conditional_selection_sources"] = ["approved plan#e2e"]
        self.assertEqual([], validate_task(task))

    def test_gwt_008_given_required_test_is_blocked_when_task_is_completed_then_it_is_not_passed(self) -> None:
        task = valid_test_task()
        task["execution"]["test_execution_contract"]["outcomes"][1].update(
            outcome="blocked-by-environment",
            evidence=["enterprise network denied the integration dependency"],
        )
        errors = validate_task(task)
        self.assertTrue(any("required test level integration must pass" in error for error in errors))

    def test_gwt_008a_given_selected_non_applicable_level_when_no_command_exists_then_the_contract_can_record_it_without_false_execution(self) -> None:
        task = valid_test_task(status="in_progress")
        contract = task["execution"]["test_execution_contract"]
        contract["target_owned"]["commands"] = [
            command
            for command in contract["target_owned"]["commands"]
            if command["level"] != "integration"
        ]
        integration = next(
            outcome
            for outcome in contract["outcomes"]
            if outcome["level"] == "integration"
        )
        integration["outcome"] = "not-applicable"
        integration["evidence"] = ["target has no integration boundary"]
        contract["required_for_closeout"] = ["unit"]
        self.assertEqual([], validate_task(task))

    def test_gwt_009_given_compliance_selection_when_completed_then_100_percent_evidence_is_required(self) -> None:
        unselected = valid_task(status="completed")
        self.assertEqual([], validate_task(unselected))

        selected = valid_task(status="completed")
        selected["execution"]["spec_compliance"] = {
            "selected": True,
            "activation_source": ["owner selected the problem-frame gate"],
            "expected_outcome": "100-percent-pass",
        }
        selected["results"]["spec_compliance"] = {
            "outcome": "100-percent-pass",
            "coverage_percent": 99,
            "evidence": ["validator output"],
        }
        self.assertTrue(any("requires 100 percent" in error for error in validate_task(selected)))
        selected["results"]["spec_compliance"]["coverage_percent"] = 100
        self.assertEqual([], validate_task(selected))

    def test_gwt_010_given_two_small_completed_tasks_when_they_share_one_batch_commit_then_both_pass(self) -> None:
        first = valid_task(status="completed")
        second = copy.deepcopy(first)
        second["task_id"] = "DEV-002"
        second["execution"]["commit_checkpoint"] = "coherent-batch: DEV-001 + DEV-002"
        first["execution"]["commit_checkpoint"] = "coherent-batch: DEV-001 + DEV-002"
        first["results"]["commits"] = ["a" * 40]
        second["results"]["commits"] = ["a" * 40]
        self.assertEqual([], validate_task(first))
        self.assertEqual([], validate_task(second))
        second["results"]["commits"] = []
        self.assertTrue(
            any("requires commit evidence" in error for error in validate_task(second))
        )

    def test_gwt_011_given_local_continuation_metadata_when_validated_then_checkpoint_links_and_hidden_context_shape_are_checked(self) -> None:
        self.assertFalse(VALIDATOR.safe_repo_reference("C:/outside.md"))
        self.assertFalse(
            VALIDATOR.safe_repo_reference(".dev//standards/TEST-POLICY.md")
        )
        with tempfile.TemporaryDirectory(prefix="devwf-resume-") as temporary:
            repo = Path(temporary)
            checkpoint_ref = ".dev/workflows/example/handoff.yaml"
            checkpoint_path = repo / checkpoint_ref
            checkpoint_path.parent.mkdir(parents=True)
            (repo / ".dev/standards").mkdir(parents=True)
            (repo / ".dev/standards/TEST-POLICY.md").write_text(
                "# Target Test Policy\n", encoding="utf-8"
            )
            checkpoint_path.write_text(
                yaml.safe_dump(
                    {
                        "workflow": {
                            "workflow_id": "2026-07-24-example",
                            "task_id": "DEV-001",
                        },
                        "resume": {
                            "exact_next_action": "Run the target-owned integration test.",
                            "hidden_context_required": False,
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            registry = repo / ".dev/workflows/handoff-checkpoints.yaml"
            registry.write_text(
                yaml.safe_dump(
                    {"schema_version": "1.0", "checkpoints": [checkpoint_ref]},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            locator = {
                "workflow_id": "2026-07-24-example",
                "status": "in_progress",
                "template_source": VALIDATOR.DEV_LOCATOR_TEMPLATE,
                "continuation": {
                    "current_task_id": "DEV-001",
                    "target_policy_refs": [".dev/standards/TEST-POLICY.md"],
                    "handoff_checkpoint": checkpoint_ref,
                },
            }
            task = valid_task()
            errors: list[str] = []
            VALIDATOR.validate_development_continuation_contract(
                locator,
                [("tasks/DEV-001.json", task)],
                "workflow.yaml",
                errors,
                repo=repo,
                locator_created=CREATED,
            )
            self.assertEqual([], errors)

            checkpoint = yaml.safe_load(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["resume"]["hidden_context_required"] = True
            checkpoint["resume"]["exact_next_action"] = ""
            checkpoint_path.write_text(
                yaml.safe_dump(checkpoint, sort_keys=False),
                encoding="utf-8",
            )
            errors = []
            VALIDATOR.validate_development_continuation_contract(
                locator,
                [("tasks/DEV-001.json", task)],
                "workflow.yaml",
                errors,
                repo=repo,
                locator_created=CREATED,
            )
            self.assertTrue(any("hidden_context_required must be false" in error for error in errors))
            self.assertTrue(any("exact_next_action must be non-empty" in error for error in errors))

    def test_gwt_012_given_pre_adoption_task_when_new_fields_are_absent_then_it_remains_compatible(self) -> None:
        legacy = {
            "template_source": VALIDATOR.DEV_TASK_TEMPLATE,
            "status": "completed",
        }
        errors: list[str] = []
        for validator in (
            VALIDATOR.validate_development_approval_contract,
            VALIDATOR.validate_test_execution_contract,
            VALIDATOR.validate_spec_compliance_contract,
            VALIDATOR.validate_development_commit_checkpoint,
        ):
            validator(
                legacy,
                "legacy-task.json",
                errors,
                CREATED - timedelta(seconds=1),
            )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
