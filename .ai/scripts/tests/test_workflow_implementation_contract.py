#!/usr/bin/env python3
"""GWT tests for fail-closed development implementation task contracts."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-workflow-artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_workflow_artifacts", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
CREATED = datetime.fromisoformat("2026-07-14T21:14:55+08:00")


def valid_task() -> dict:
    return {
        "template_source": VALIDATOR.DEV_TASK_TEMPLATE,
        "owner_skill": "slice-implementer",
        "inputs": {},
        "execution": {
            "capability_slot": "implementation",
            "implementation_contract": {
                "intent": "review-remediation",
                "execution_mode": "command",
                "overlays": ["remediation"],
                "authorization_source": ["workflow#TASK-001"],
                "normative_truth": [".dev/specs/feature.md"],
                "finding_evidence": ["ASM-20260714-001#CR-001"],
                "subject_revision": "a" * 40,
                "acceptance_criteria": ["The finding no longer reproduces."],
            },
        },
    }


def validate(task: dict) -> list[str]:
    errors: list[str] = []
    VALIDATOR.validate_implementation_contract(task, "task.json", errors, CREATED)
    return errors


class WorkflowImplementationContractTests(unittest.TestCase):
    def test_gwt_001_given_non_implementation_task_when_validated_then_contract_is_not_required(self) -> None:
        task = valid_task()
        task["owner_skill"] = "code-reviewer"
        task["execution"] = {"capability_slot": "review", "implementation_contract": None}
        self.assertEqual([], validate(task))

    def test_gwt_002_given_valid_remediation_contract_when_validated_then_passes(self) -> None:
        self.assertEqual([], validate(valid_task()))

    def test_gwt_003_given_implementation_task_without_contract_when_validated_then_fails(self) -> None:
        task = valid_task()
        task["execution"]["implementation_contract"] = None
        self.assertTrue(any("requires implementation_contract" in error for error in validate(task)))

    def test_gwt_004_given_remediation_as_execution_mode_when_validated_then_fails(self) -> None:
        task = valid_task()
        task["execution"]["implementation_contract"]["execution_mode"] = "remediation"
        self.assertTrue(any("execution_mode must be" in error for error in validate(task)))

    def test_gwt_005_given_remediation_without_findings_or_overlay_when_validated_then_fails(self) -> None:
        task = valid_task()
        task["execution"]["implementation_contract"]["overlays"] = []
        task["execution"]["implementation_contract"]["finding_evidence"] = []
        errors = validate(task)
        self.assertTrue(any("requires remediation overlay" in error for error in errors))
        self.assertTrue(any("requires finding_evidence" in error for error in errors))

    def test_gwt_006_given_deprecated_collapsed_sources_when_validated_then_fails(self) -> None:
        task = valid_task()
        task["inputs"] = {"source_truth": ["workflow task"], "source_findings": ["CR-001"]}
        errors = validate(task)
        self.assertTrue(any("deprecated inputs.source_truth" in error for error in errors))
        self.assertTrue(any("deprecated inputs.source_findings" in error for error in errors))

    def test_gwt_007_given_pre_adoption_task_when_validated_then_is_legacy_compatible(self) -> None:
        task = copy.deepcopy(valid_task())
        task["execution"] = {"capability_slot": "implementation"}
        created = datetime.fromisoformat("2026-07-13T12:00:00+08:00")
        errors: list[str] = []
        VALIDATOR.validate_implementation_contract(task, "task.json", errors, created)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
