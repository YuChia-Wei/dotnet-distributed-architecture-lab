#!/usr/bin/env python3
"""GWT tests for prospective workflow lifecycle consistency."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-workflow-artifacts.py"
SPEC = importlib.util.spec_from_file_location("validate_workflow_lifecycle", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def task(status: str, summary: str = "done", finding_status: str = "resolved") -> dict:
    return {
        "status": status,
        "results": {"summary": summary, "finding_status": finding_status},
    }


class WorkflowLifecycleContractTests(unittest.TestCase):
    def validate(self, status: str, phase: str, tasks: list[tuple[str, dict]]) -> list[str]:
        errors: list[str] = []
        locator = {
            "lifecycle_contract": "1.0",
            "status": status,
            "current_phase": phase,
        }
        VALIDATOR.validate_lifecycle_contract(locator, tasks, "workflow.yaml", errors)
        return errors

    def test_gwt_001_given_one_active_task_when_workflow_in_progress_then_passes(self) -> None:
        self.assertEqual([], self.validate("in_progress", "implementation", [("T1", task("in_progress"))]))

    def test_gwt_002_given_no_active_task_when_workflow_in_progress_then_fails(self) -> None:
        errors = self.validate("in_progress", "implementation", [("T1", task("pending"))])
        self.assertTrue(any("exactly one in_progress task" in error for error in errors))

    def test_gwt_003_given_unfinished_task_when_workflow_completed_then_fails(self) -> None:
        errors = self.validate("completed", "completed", [("T1", task("pending"))])
        self.assertTrue(any("completed workflow has unfinished tasks" in error for error in errors))

    def test_gwt_004_given_completed_workflow_with_open_phase_then_fails(self) -> None:
        errors = self.validate("completed", "verification", [("T1", task("completed"))])
        self.assertTrue(any("current_phase must be completed or closed" in error for error in errors))

    def test_gwt_005_given_completed_task_without_result_then_fails(self) -> None:
        errors = self.validate("completed", "completed", [("T1", task("completed", summary=""))])
        self.assertTrue(any("non-empty results.summary" in error for error in errors))

    def test_gwt_006_given_legacy_locator_without_contract_when_validated_then_is_compatible(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_lifecycle_contract(
            {"status": "completed", "current_phase": "legacy"},
            [("T1", task("pending"))],
            "legacy/workflow.yaml",
            errors,
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
