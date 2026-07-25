#!/usr/bin/env python3
"""End-to-end deterministic acceptance for DEVWF activation and resume."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / ".ai/scripts/validate-software-development-orchestrator-acceptance.py"
FIXTURE_ROOT = (
    ROOT / ".ai/assets/skills/software-development-orchestrator/fixtures/acceptance"
)
ACTIVATION_FIXTURE = (
    FIXTURE_ROOT / "activation-high-level-pending-approval.yaml"
)
ACTIVATION_EXPECTED = (
    FIXTURE_ROOT / "activation-high-level-pending-approval.expected.yaml"
)
FRESH_BLUEPRINT = (
    FIXTURE_ROOT / "fresh-session-checkpoint-blueprint.yaml"
)
HANDOFF_POLICY = ROOT / ".dev/standards/WORKFLOW-HANDOFF-POLICY.yaml"


def run(
    command: list[str],
    *,
    cwd: Path,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and completed.returncode != 0:
        raise AssertionError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}{completed.stderr}"
        )
    return completed


def git(root: Path, *args: str) -> str:
    return run(["git", *args], cwd=root, check=True).stdout


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"Expected mapping fixture: {path}")
    return data


def materialize_workflow_id(value: Any, workflow_id: str) -> Any:
    if isinstance(value, dict):
        return {
            key: materialize_workflow_id(item, workflow_id)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [materialize_workflow_id(item, workflow_id) for item in value]
    if isinstance(value, str):
        return value.replace("<workflow-id>", workflow_id)
    return value


def build_test_task(blueprint: dict[str, Any]) -> dict[str, Any]:
    workflow = blueprint["workflow"]
    test_state = copy.deepcopy(blueprint["test_state"])
    contract = {
        "provider": test_state["provider"],
        "target_owned": {
            "working_directory": test_state["working_directory"],
            "commands": test_state["commands"],
            "prerequisites": [],
            "environment_boundary": [
                "Integration requires the target-owned environment."
            ],
            "policy": [
                "Unit and integration are required for closeout."
            ],
        },
        "selected_levels": test_state["selected_levels"],
        "required_for_closeout": test_state["required_for_closeout"],
        "conditional_selection_sources": [],
        "outcomes": test_state["outcomes"],
    }
    return {
        "template_id": "software-development-orchestrator/development-workflow-task",
        "template_version": "1.3.0",
        "template_created_at": "2026-07-10T18:25:11+08:00",
        "template_updated_at": "2026-07-24T08:10:00+08:00",
        "workflow_id": workflow["workflow_id"],
        "task_id": workflow["task_id"],
        "owner_skill": "software-development-orchestrator",
        "related_plan_id": f"development-plan-{workflow['workflow_id']}",
        "status": "in_progress",
        "created_at": "2026-07-24T08:20:00+08:00",
        "updated_at": "2026-07-24T08:31:00+08:00",
        "template_source": (
            ".ai/assets/skills/software-development-orchestrator/templates/"
            "development-workflow-task-template.json"
        ),
        "workflow_locator": workflow["locator_path"],
        "scope": {
            "goal": "Preserve target test state for fresh-session continuation.",
            "target": "DEVWF fresh-session acceptance fixture",
            "files": [workflow["task_path"]],
            "constraints": ["No hidden conversation context."],
            "non_goals": ["Execute an environment-dependent integration system."],
        },
        "inputs": {
            "requirements": [],
            "specifications": [],
            "architecture_decisions": [],
            "user_constraints": [],
        },
        "execution": {
            "capability_slot": "test-execution",
            "approval_contract": {
                "status": "not-required",
                "required_before": "",
                "authorization_source": [],
                "pending_decision": "",
            },
            "implementation_contract": None,
            "test_execution_contract": contract,
            "spec_compliance": {
                "selected": False,
                "activation_source": [],
                "expected_outcome": "not-applicable",
            },
            "steps": [
                "Preserve the passed unit result.",
                "Resolve the integration environment block and run integration.",
            ],
            "validation": [
                "validate-workflow-handoff.py --verify-repository"
            ],
            "commit_checkpoint": (
                "durable-stage: fresh-session test-execution checkpoint"
            ),
            "deferred_items": [],
        },
        "results": {
            "summary": "Unit passed; integration remains blocked by environment.",
            "files_changed": [],
            "approval_evidence": [],
            "test_execution": copy.deepcopy(test_state["outcomes"]),
            "spec_compliance": {
                "outcome": "not-applicable",
                "coverage_percent": None,
                "evidence": [],
            },
            "validation_evidence": [
                "Unit acceptance command exited 0."
            ],
            "commits": [],
            "follow_up_needed": True,
        },
    }


def build_locator(blueprint: dict[str, Any]) -> dict[str, Any]:
    repository = blueprint["repository"]
    workflow = blueprint["workflow"]
    return {
        "template_metadata": {
            "template_id": "software-development-orchestrator-workflow-locator",
            "template_version": "1.3.0",
            "created_at": "2026-07-10T18:25:11+08:00",
            "updated_at": "2026-07-24T08:10:00+08:00",
        },
        "schema_version": "1.0",
        "lifecycle_contract": "1.0",
        "workflow_id": workflow["workflow_id"],
        "workflow_kind": "software-development",
        "title": "DEVWF fresh-session acceptance",
        "owner_skill": "software-development-orchestrator",
        "status": "in_progress",
        "branch": repository["branch"],
        "base_branch": "main",
        "artifact_root": f".dev/workflows/{workflow['workflow_id']}",
        "entrypoint": "workflow-plan.md",
        "continuation": {
            "current_task_id": workflow["task_id"],
            "target_policy_refs": [workflow["target_policy_path"]],
            "handoff_checkpoint": workflow["checkpoint_path"],
        },
        "created_at": "2026-07-24T08:20:00+08:00",
        "updated_at": "2026-07-24T08:31:00+08:00",
        "template_source": (
            ".ai/assets/skills/software-development-orchestrator/templates/"
            "workflow-locator-template.yaml"
        ),
        "template_version": "1.3.0",
    }


def attribution_fixture_status(commit: str) -> list[dict[str, Any]]:
    policy = load_yaml(HANDOFF_POLICY)
    paths = policy.get("required_fixture_paths")
    if not isinstance(paths, list) or "codex-local" not in paths:
        raise AssertionError(
            "Workflow handoff policy must declare the codex-local fixture path"
        )
    statuses: list[dict[str, Any]] = []
    for path_id in paths:
        if path_id == "codex-local":
            statuses.append(
                {
                    "path_id": path_id,
                    "status": "captured",
                    "commit": commit,
                    "evidence_ref": f"git:{commit}",
                    "reason": None,
                }
            )
        else:
            statuses.append(
                {
                    "path_id": path_id,
                    "status": "blocked",
                    "commit": None,
                    "evidence_ref": "evidence/provider-research.md",
                    "reason": (
                        "No real provider-generated commit fixture is used by "
                        "this DEVWF acceptance."
                    ),
                }
            )
    return statuses


def build_checkpoint(
    root: Path,
    blueprint: dict[str, Any],
    validated_commit: str,
) -> dict[str, Any]:
    policy = load_yaml(HANDOFF_POLICY)
    repository = blueprint["repository"]
    workflow = blueprint["workflow"]
    critical = blueprint["critical_gate"]
    message = git(root, "show", "-s", "--format=%B", validated_commit)
    author = git(
        root, "show", "-s", "--format=%an <%ae>", validated_commit
    ).strip()
    committer = git(
        root, "show", "-s", "--format=%cn <%ce>", validated_commit
    ).strip()
    signature_code = git(
        root, "show", "-s", "--format=%G?", validated_commit
    ).strip()
    if signature_code != "N":
        raise AssertionError(
            f"Acceptance fixture expected an unsigned local commit, got {signature_code!r}"
        )
    output_text = "\n".join(critical["output_lines"]) + "\n"
    return {
        "schema_version": policy["checkpoint_schema_version"],
        "checkpoint_id": (
            f"{workflow['workflow_id']}-{workflow['task_id']}-handoff"
        ),
        "created_at": "2026-07-24T08:32:00+08:00",
        "repository": {
            "root": ".",
            "branch": repository["branch"],
            "validated_commit": validated_commit,
            "checkpoint_commit_source": "containing-commit",
            "dirty_state": "clean",
            "status_porcelain_sha256": hashlib.sha256(b"").hexdigest(),
        },
        "workflow": {
            "workflow_id": workflow["workflow_id"],
            "task_id": workflow["task_id"],
        },
        "resume": {
            "last_completed_action": blueprint["resume"][
                "last_completed_action"
            ],
            "exact_next_action": blueprint["resume"]["exact_next_action"],
            "hidden_context_required": False,
        },
        "critical_gate": {
            "command": critical["command"],
            "observed_at": critical["observed_at"],
            "exit_code": 0,
            "outcome": "passed",
            "output": {
                "normalization": "utf8-lf",
                "sha256": hashlib.sha256(
                    output_text.encode("utf-8")
                ).hexdigest(),
                "line_count": len(critical["output_lines"]),
                "tail": critical["output_lines"],
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
        "execution_provenance": blueprint["execution_provenance"],
        "attribution": {
            "preservation_required": True,
            "evidence_union_version": "1.0",
            "selected_evidence": {
                "kind": "repository-created-local-ai-trailer",
                "commit": validated_commit,
                "author": author,
                "committer": committer,
                "signature_status": "unsigned",
                "session_ref": None,
                "observed_trailer": repository["observed_trailer"],
                "message_sha256": hashlib.sha256(
                    message.encode("utf-8")
                ).hexdigest(),
                "fixture_ref": f"git:{validated_commit}",
            },
            "fixture_status": attribution_fixture_status(validated_commit),
        },
    }


def create_fresh_session_repository(
    root: Path,
    blueprint: dict[str, Any],
) -> tuple[str, str, str]:
    repository = blueprint["repository"]
    workflow = blueprint["workflow"]
    git(root, "init", "-b", repository["branch"])
    git(root, "config", "user.name", repository["author_name"])
    git(root, "config", "user.email", repository["author_email"])
    git(root, "config", "core.autocrlf", "false")

    policy_target = root / ".dev/standards/WORKFLOW-HANDOFF-POLICY.yaml"
    policy_target.parent.mkdir(parents=True, exist_ok=True)
    policy_target.write_text(
        HANDOFF_POLICY.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    target_policy = root / workflow["target_policy_path"]
    target_policy.write_text(
        "# DEV Workflow Acceptance Test Policy\n\n"
        "Unit and integration are required. An environment block is not a pass.\n",
        encoding="utf-8",
    )
    provider_evidence = root / "evidence/provider-research.md"
    provider_evidence.parent.mkdir(parents=True)
    provider_evidence.write_text(
        "# Provider Fixture Boundary\n\n"
        "Only the repository-created local acceptance commit is captured.\n",
        encoding="utf-8",
    )

    locator = build_locator(blueprint)
    task = build_test_task(blueprint)
    write_yaml(root / workflow["locator_path"], locator)
    write_json(root / workflow["task_path"], task)
    plan_path = (
        root
        / f".dev/workflows/{workflow['workflow_id']}/workflow-plan.md"
    )
    plan_path.write_text(
        "# DEVWF Fresh-Session Acceptance\n\n"
        "Resume from the registered checkpoint and recorded target test state.\n",
        encoding="utf-8",
    )
    write_yaml(
        root / ".dev/workflows/handoff-checkpoints.yaml",
        {
            "schema_version": "1.0",
            "checkpoints": [workflow["checkpoint_path"]],
        },
    )

    unit_result = run(
        [sys.executable, "-c", "print('unit acceptance passed')"],
        cwd=root,
        check=True,
    )
    if unit_result.stdout.strip() != "unit acceptance passed":
        raise AssertionError("Unit acceptance observation was not reproducible")

    git(root, "add", ".")
    git(
        root,
        "commit",
        "-m",
        repository["validated_commit_subject"],
        "-m",
        repository["observed_trailer"],
    )
    validated_commit = git(root, "rev-parse", "HEAD").strip()

    checkpoint = build_checkpoint(root, blueprint, validated_commit)
    write_yaml(root / workflow["checkpoint_path"], checkpoint)
    git(root, "add", workflow["checkpoint_path"])
    git(
        root,
        "commit",
        "-m",
        repository["checkpoint_commit_subject"],
        "-m",
        repository["observed_trailer"],
    )
    if git(root, "status", "--porcelain=v1") != "":
        raise AssertionError("Fresh-session acceptance repository must be clean")
    return (
        workflow["checkpoint_path"],
        workflow["locator_path"],
        workflow["task_path"],
    )


class DevWorkflowAcceptanceTests(unittest.TestCase):
    def test_gwt_001_given_preclassified_multistage_request_without_skill_names_when_oracle_runs_then_it_routes_and_pauses(self) -> None:
        completed = run(
            [
                sys.executable,
                str(VALIDATOR),
                "activation",
                "--fixture",
                str(ACTIVATION_FIXTURE),
                "--expected",
                str(ACTIVATION_EXPECTED),
            ],
            cwd=ROOT,
        )
        self.assertEqual(
            0, completed.returncode, completed.stdout + completed.stderr
        )
        self.assertIn(
            "activation -> capability routing -> approval pause",
            completed.stdout,
        )

    def test_gwt_002_given_unclassified_free_text_when_oracle_runs_then_it_refuses_a_deterministic_nlp_claim(self) -> None:
        fixture = load_yaml(ACTIVATION_FIXTURE)
        fixture["classification"]["producer"] = "deterministic-keyword-parser"
        fixture["classification"]["deterministic_boundary"] = (
            "arbitrary-natural-language"
        )
        with tempfile.TemporaryDirectory(
            prefix="devwf-activation-boundary-"
        ) as temporary:
            path = Path(temporary) / "unclassified.yaml"
            write_yaml(path, fixture)
            completed = run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "activation",
                    "--fixture",
                    str(path),
                    "--expected",
                    str(ACTIVATION_EXPECTED),
                ],
                cwd=ROOT,
            )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("model-in-loop-eval", completed.stdout)
        self.assertIn(
            "arbitrary natural-language interpretation is outside this oracle",
            completed.stdout,
        )

    def test_gwt_003_given_complete_fresh_session_checkpoint_when_repository_is_verified_then_pins_provenance_and_test_state_pass(self) -> None:
        template = load_yaml(FRESH_BLUEPRINT)
        self.assertEqual("<workflow-id>", template["workflow"]["workflow_id"])
        self.assertTrue(
            all(
                "<workflow-id>" in template["workflow"][field]
                for field in ("checkpoint_path", "locator_path", "task_path")
            )
        )
        blueprint = materialize_workflow_id(
            template,
            "2026-07-24-devwf-fresh-session-acceptance",
        )
        with tempfile.TemporaryDirectory(
            prefix="devwf-fresh-session-"
        ) as temporary:
            root = Path(temporary)
            checkpoint, locator, task = create_fresh_session_repository(
                root, blueprint
            )
            command = [
                sys.executable,
                str(VALIDATOR),
                "fresh-session",
                "--root",
                str(root),
                "--checkpoint",
                checkpoint,
                "--locator",
                locator,
                "--task",
                task,
            ]
            completed = run(command, cwd=ROOT)
            self.assertEqual(
                0, completed.returncode, completed.stdout + completed.stderr
            )
            self.assertIn(
                "Workflow handoff validation passed with repository verification",
                completed.stdout,
            )
            self.assertIn(
                "recorded test state verified",
                completed.stdout,
            )

            unexpected = root / "unexpected-dirty-state.txt"
            unexpected.write_text("dirty\n", encoding="utf-8")
            rejected = run(command, cwd=ROOT)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("repository.dirty_state", rejected.stdout)
            self.assertIn("status_porcelain_sha256", rejected.stdout)


if __name__ == "__main__":
    unittest.main()
