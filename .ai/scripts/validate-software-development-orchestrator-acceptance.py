#!/usr/bin/env python3
"""Validate deterministic DEVWF acceptance fixtures without claiming NLP."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    ROOT
    / ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"
)
WORKFLOW_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-workflow-artifacts.py"
HANDOFF_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-workflow-handoff.py"

INTENT_ROUTES = {
    "capture-requirements": "requirements",
    "define-specification": "specification",
    "design-architecture": "architecture",
    "implement-approved-change": "implementation",
    "execute-default-tests": "test-execution",
    "review-implementation": "review",
    "validate-selected-compliance": "compliance-validation",
}
CLASSIFIER = "model-in-loop-eval"
DETERMINISTIC_BOUNDARY = "preclassified-envelope"


def load_python_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


WORKFLOW_VALIDATOR = load_python_module(
    "validate_workflow_artifacts_for_devwf_acceptance",
    WORKFLOW_VALIDATOR_PATH,
)


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return data


def load_json_mapping(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON mapping")
    return data


def mapping(value: object, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be a mapping")
        return {}
    return value


def string_list(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        errors.append(f"{label}: must be a non-empty string list")
        return []
    return value


def route_classified_envelope(
    envelope: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Route a preclassified envelope; free-text NLP is deliberately excluded."""

    errors: list[str] = []
    if envelope.get("schema_version") != "1.0":
        errors.append("schema_version: must be 1.0")
    fixture_id = envelope.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        errors.append("fixture_id: must be a non-empty string")
        fixture_id = ""

    classification = mapping(
        envelope.get("classification"), "classification", errors
    )
    activation_contract = mapping(
        mapping(
            profile.get("orchestration_contract"),
            "profile.orchestration_contract",
            errors,
        ).get("activation"),
        "profile.orchestration_contract.activation",
        errors,
    )
    if activation_contract.get("skill_name_required") is not False:
        errors.append(
            "profile activation contract: skill_name_required must be false"
        )
    expected_routing_basis = [
        "requested-outcome",
        "current-artifacts",
        "repository-policy",
        "approval-state",
    ]
    if activation_contract.get("routing_basis") != expected_routing_basis:
        errors.append(
            "profile activation contract: routing_basis must preserve the "
            "deterministic orchestration evidence order"
        )
    intent_class = classification.get("intent_class")
    if intent_class != activation_contract.get("intent_class"):
        errors.append(
            "classification.intent_class: must match the profile activation contract"
        )
    if classification.get("producer") != CLASSIFIER:
        errors.append(
            "classification.producer: deterministic acceptance requires "
            "model-in-loop-eval"
        )
    if classification.get("deterministic_boundary") != DETERMINISTIC_BOUNDARY:
        errors.append(
            "classification.deterministic_boundary: arbitrary natural-language "
            "interpretation is outside this oracle"
        )
    evidence_ref = classification.get("evidence_ref")
    if not isinstance(evidence_ref, str) or not evidence_ref.strip():
        errors.append("classification.evidence_ref: must be a non-empty string")

    request = mapping(envelope.get("request"), "request", errors)
    summary = request.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("request.summary: must be non-empty human-review evidence")
    named_skills = request.get("named_skills")
    if not isinstance(named_skills, list) or not all(
        isinstance(item, str) and item.strip() for item in named_skills
    ):
        errors.append("request.named_skills: must be a string list")
        named_skills = []
    stage_intents = string_list(
        request.get("stage_intents"), "request.stage_intents", errors
    )
    if len(stage_intents) < 2:
        errors.append(
            "request.stage_intents: multi-stage acceptance requires at least two stages"
        )
    if len(stage_intents) != len(set(stage_intents)):
        errors.append("request.stage_intents: duplicate normalized intent token")

    mappings = mapping(profile.get("mappings"), "profile.mappings", errors)
    test_contract = mapping(
        mapping(
            profile.get("capability_contracts"),
            "profile.capability_contracts",
            errors,
        ).get("test-execution"),
        "profile.capability_contracts.test-execution",
        errors,
    )
    provider_order = string_list(
        test_contract.get("provider_order"),
        "profile.capability_contracts.test-execution.provider_order",
        errors,
    )

    routed: list[dict[str, str]] = []
    implementation_index: int | None = None
    for index, token in enumerate(stage_intents):
        capability = INTENT_ROUTES.get(token)
        if capability is None:
            errors.append(
                f"request.stage_intents[{index}]: unsupported normalized token {token!r}"
            )
            continue
        if capability == "test-execution":
            provider = provider_order[0] if provider_order else ""
        else:
            provider_value = mappings.get(capability)
            provider = provider_value if isinstance(provider_value, str) else ""
            if not provider:
                errors.append(
                    f"profile.mappings: missing provider for capability {capability}"
                )
        if capability == "implementation":
            implementation_index = len(routed)
        routed.append(
            {
                "stage_id": f"stage-{len(routed) + 1:02d}",
                "intent_token": token,
                "capability_slot": capability,
                "provider": provider,
                "state": "planned",
            }
        )

    approval = mapping(envelope.get("approval"), "approval", errors)
    approval_contract = mapping(
        mapping(
            profile.get("orchestration_contract"),
            "profile.orchestration_contract",
            errors,
        ).get("approval"),
        "profile.orchestration_contract.approval",
        errors,
    )
    transition = approval.get("transition")
    if transition != approval_contract.get("gated_transition"):
        errors.append("approval.transition: must match the profile gated transition")
    approval_status = approval.get("status")
    if approval_status not in {"awaiting-approval", "approved"}:
        errors.append("approval.status: must be awaiting-approval or approved")
    pending_decision = approval.get("pending_decision")
    if approval_status == "awaiting-approval" and (
        not isinstance(pending_decision, str) or not pending_decision.strip()
    ):
        errors.append(
            "approval.pending_decision: awaiting approval requires a decision"
        )
        pending_decision = ""

    paused = (
        approval_status == "awaiting-approval"
        and implementation_index is not None
    )
    if paused and implementation_index is not None:
        routed[implementation_index]["state"] = "blocked-awaiting-approval"
        for stage in routed[implementation_index + 1 :]:
            stage["state"] = "pending-after-approval"

    result = {
        "schema_version": "1.0",
        "fixture_id": fixture_id,
        "activated": not errors,
        "orchestrator": "software-development-orchestrator",
        "activation": {
            "intent_class": intent_class,
            "named_skills_observed": named_skills,
            "named_skill_dependency": bool(
                activation_contract.get("skill_name_required")
            ),
            "routing_basis": activation_contract.get("routing_basis"),
        },
        "classification_boundary": {
            "natural_language_understanding": CLASSIFIER,
            "deterministic_oracle_input": DETERMINISTIC_BOUNDARY,
        },
        "stages": routed,
        "approval_pause": {
            "paused": paused,
            "before_capability": "implementation",
            "transition": transition,
            "pending_decision": pending_decision if paused else "",
            "authorization_source_required": bool(
                approval_contract.get("authorization_source_required")
            ),
        },
    }
    return result, errors


def safe_path(root: Path, relative: str, label: str) -> Path:
    if not WORKFLOW_VALIDATOR.safe_repo_reference(relative):
        raise ValueError(f"{label}: must be a safe repository-relative path")
    path = (root / relative).resolve()
    path.relative_to(root.resolve())
    return path


def validate_fresh_session(
    fixture_root: Path,
    checkpoint_ref: str,
    locator_ref: str,
    task_ref: str,
) -> tuple[list[str], str]:
    """Run repository verification plus DEVWF continuation/test-state checks."""

    root = fixture_root.resolve()
    errors: list[str] = []
    try:
        checkpoint_path = safe_path(root, checkpoint_ref, "checkpoint")
        locator_path = safe_path(root, locator_ref, "locator")
        task_path = safe_path(root, task_ref, "task")
    except (ValueError, OSError) as exc:
        return [str(exc)], ""

    command = [
        sys.executable,
        str(HANDOFF_VALIDATOR_PATH),
        "--root",
        str(root),
        "--checkpoint",
        checkpoint_ref,
        "--verify-repository",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    handoff_output = (completed.stdout + completed.stderr).strip()
    if completed.returncode != 0:
        errors.append(
            "validate-workflow-handoff.py --verify-repository failed: "
            + handoff_output
        )

    try:
        checkpoint = load_yaml_mapping(checkpoint_path)
        locator = load_yaml_mapping(locator_path)
        task = load_json_mapping(task_path)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        errors.append(str(exc))
        return errors, handoff_output

    created = WORKFLOW_VALIDATOR.timestamp(
        locator.get("created_at"),
        f"{locator_ref} created_at",
        errors,
    )
    WORKFLOW_VALIDATOR.validate_development_continuation_contract(
        locator,
        [(task_ref, task)],
        locator_ref,
        errors,
        repo=root,
        locator_created=created,
    )
    task_created = WORKFLOW_VALIDATOR.timestamp(
        task.get("created_at"),
        f"{task_ref} created_at",
        errors,
    )
    for validator in (
        WORKFLOW_VALIDATOR.validate_development_approval_contract,
        WORKFLOW_VALIDATOR.validate_test_execution_contract,
        WORKFLOW_VALIDATOR.validate_spec_compliance_contract,
        WORKFLOW_VALIDATOR.validate_development_commit_checkpoint,
    ):
        validator(task, task_ref, errors, task_created)

    execution = mapping(task.get("execution"), f"{task_ref}.execution", errors)
    contract = mapping(
        execution.get("test_execution_contract"),
        f"{task_ref}.execution.test_execution_contract",
        errors,
    )
    results = mapping(task.get("results"), f"{task_ref}.results", errors)
    recorded = results.get("test_execution")
    outcomes = contract.get("outcomes")
    if not isinstance(recorded, list) or recorded != outcomes:
        errors.append(
            f"{task_ref}: results.test_execution must preserve the exact "
            "test_execution_contract outcomes"
        )
    if task.get("status") != "in_progress":
        errors.append(f"{task_ref}: fresh-session current task must be in_progress")
    if execution.get("capability_slot") != "test-execution":
        errors.append(
            f"{task_ref}: fresh-session fixture must record test-execution state"
        )

    critical_gate = mapping(
        checkpoint.get("critical_gate"),
        f"{checkpoint_ref}.critical_gate",
        errors,
    )
    if critical_gate.get("outcome") != "passed":
        errors.append(f"{checkpoint_ref}: critical gate must be recorded as passed")
    critical_output = mapping(
        critical_gate.get("output"),
        f"{checkpoint_ref}.critical_gate.output",
        errors,
    )
    tail = critical_output.get("tail")
    line_count = critical_output.get("line_count")
    if isinstance(tail, list) and line_count == len(tail) and all(
        isinstance(line, str) for line in tail
    ):
        complete_output = "\n".join(tail) + "\n"
        observed_digest = hashlib.sha256(
            complete_output.encode("utf-8")
        ).hexdigest()
        if critical_output.get("sha256") != observed_digest:
            errors.append(
                f"{checkpoint_ref}: complete critical-gate output digest differs"
            )
    else:
        errors.append(
            f"{checkpoint_ref}: acceptance fixture requires complete bounded "
            "critical-gate output"
        )
    provenance = mapping(
        checkpoint.get("execution_provenance"),
        f"{checkpoint_ref}.execution_provenance",
        errors,
    )
    if not provenance:
        errors.append(f"{checkpoint_ref}: execution provenance is required")
    return errors, handoff_output


def activation_command(args: argparse.Namespace) -> int:
    try:
        envelope = load_yaml_mapping(args.fixture)
        expected = load_yaml_mapping(args.expected)
        profile = load_yaml_mapping(PROFILE_PATH)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"DEVWF activation acceptance failed:\n- {exc}")
        return 1
    actual, errors = route_classified_envelope(envelope, profile)
    if actual != expected:
        errors.append(
            "activation oracle output differs from the expected deterministic fixture"
        )
    if errors:
        print("DEVWF activation acceptance failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "DEVWF activation acceptance passed: preclassified envelope -> "
        "activation -> capability routing -> approval pause."
    )
    return 0


def fresh_session_command(args: argparse.Namespace) -> int:
    errors, handoff_output = validate_fresh_session(
        args.root,
        args.checkpoint,
        args.locator,
        args.task,
    )
    if handoff_output:
        print(handoff_output)
    if errors:
        print("DEVWF fresh-session acceptance failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "DEVWF fresh-session acceptance passed: repository pins, critical gate, "
        "execution provenance, continuation, and recorded test state verified."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)

    activation = subparsers.add_parser(
        "activation",
        help="Validate a preclassified activation fixture against its oracle",
    )
    activation.add_argument("--fixture", type=Path, required=True)
    activation.add_argument("--expected", type=Path, required=True)
    activation.set_defaults(handler=activation_command)

    fresh = subparsers.add_parser(
        "fresh-session",
        help="Verify a complete receiving checkpoint and recorded DEVWF state",
    )
    fresh.add_argument("--root", type=Path, required=True)
    fresh.add_argument("--checkpoint", required=True)
    fresh.add_argument("--locator", required=True)
    fresh.add_argument("--task", required=True)
    fresh.set_defaults(handler=fresh_session_command)

    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
