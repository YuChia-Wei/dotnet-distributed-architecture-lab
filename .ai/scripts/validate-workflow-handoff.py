#!/usr/bin/env python3
"""Validate a machine-readable workflow handoff checkpoint without mutation."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CHECKPOINT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PLACEHOLDER_RE = re.compile(r"^<[^<>]+>$")
SIGNATURE_STATUS = {"verified", "unverified", "unsigned", "unavailable"}


def load_mapping(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{label}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: root must be a mapping")
        return None
    return value


def load_policy(root: Path = ROOT) -> dict[str, Any]:
    value = yaml.safe_load(
        (root / ".dev/standards/WORKFLOW-HANDOFF-POLICY.yaml").read_text(
            encoding="utf-8"
        )
    )
    if not isinstance(value, dict):
        raise RuntimeError("workflow handoff policy must be a mapping")
    return value


def mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be a mapping")
        return {}
    return value


def non_empty_string(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: must be a non-empty string")
        return ""
    if PLACEHOLDER_RE.fullmatch(value.strip()):
        errors.append(f"{label}: placeholder must be resolved")
    return value


def single_line_string(value: Any, label: str, errors: list[str]) -> str:
    text = non_empty_string(value, label, errors)
    if "\n" in text or "\r" in text:
        errors.append(f"{label}: must contain exactly one line")
    return text


def timestamp(value: Any, label: str, errors: list[str]) -> None:
    text = non_empty_string(value, label, errors)
    if not text:
        return
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        errors.append(f"{label}: must be ISO 8601")
        return
    if parsed.tzinfo is None:
        errors.append(f"{label}: must include an explicit UTC offset")


def sha256(value: Any, label: str, errors: list[str]) -> str:
    text = non_empty_string(value, label, errors)
    if text and not SHA256_RE.fullmatch(text):
        errors.append(f"{label}: must be a lowercase SHA-256")
    return text


def git_sha(value: Any, label: str, errors: list[str]) -> str:
    text = non_empty_string(value, label, errors)
    if text and not GIT_SHA_RE.fullmatch(text):
        errors.append(f"{label}: must be a 40-character lowercase Git SHA")
    return text


def bounded_output(
    value: Any,
    label: str,
    policy: dict[str, Any],
    errors: list[str],
) -> None:
    data = mapping(value, label, errors)
    output_policy = mapping(policy.get("output"), "policy.output", errors)
    expected_normalization = output_policy.get("normalization")
    if data.get("normalization") != expected_normalization:
        errors.append(
            f"{label}.normalization: must be {expected_normalization!r}"
        )
    sha256(data.get("sha256"), f"{label}.sha256", errors)
    line_count = data.get("line_count")
    if not isinstance(line_count, int) or isinstance(line_count, bool) or line_count < 1:
        errors.append(f"{label}.line_count: must be a positive integer")
        line_count = 0
    tail = data.get("tail")
    max_lines = int(output_policy.get("max_tail_lines", 0))
    max_characters = int(output_policy.get("max_tail_line_characters", 0))
    if not isinstance(tail, list) or not tail:
        errors.append(f"{label}.tail: must be a non-empty list")
        return
    if len(tail) > max_lines:
        errors.append(f"{label}.tail: exceeds {max_lines} lines")
    if line_count and len(tail) > line_count:
        errors.append(f"{label}.tail: cannot exceed line_count")
    for index, line in enumerate(tail):
        item_label = f"{label}.tail[{index}]"
        if not isinstance(line, str) or not line:
            errors.append(f"{item_label}: must be a non-empty string")
            continue
        if "\n" in line or "\r" in line:
            errors.append(f"{item_label}: must contain exactly one line")
        if len(line) > max_characters:
            errors.append(
                f"{item_label}: exceeds {max_characters} characters"
            )


def observed_gate(
    value: Any,
    label: str,
    policy: dict[str, Any],
    errors: list[str],
    *,
    critical: bool,
) -> tuple[int | None, str]:
    gate = mapping(value, label, errors)
    command = non_empty_string(gate.get("command"), f"{label}.command", errors)
    if critical and command:
        pattern = re.compile(str(policy.get("critical_command_pattern", "")))
        if not pattern.fullmatch(command):
            errors.append(
                f"{label}.command: must invoke .ai/scripts/check-all.sh --critical"
            )
    timestamp(gate.get("observed_at"), f"{label}.observed_at", errors)
    exit_code = gate.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool) or exit_code < 0:
        errors.append(f"{label}.exit_code: must be a non-negative integer")
        exit_code = None
    outcome = gate.get("outcome")
    if outcome not in {"passed", "failed"}:
        errors.append(f"{label}.outcome: must be passed or failed")
        outcome = ""
    if exit_code is not None and outcome:
        expected = "passed" if exit_code == 0 else "failed"
        if outcome != expected:
            errors.append(
                f"{label}: outcome {outcome!r} disagrees with exit_code {exit_code}"
            )
    bounded_output(gate.get("output"), f"{label}.output", policy, errors)
    return exit_code, str(outcome)


def validate_provenance(
    value: Any, policy: dict[str, Any], errors: list[str]
) -> None:
    data = mapping(value, "execution_provenance", errors)
    non_empty_string(data.get("runtime"), "execution_provenance.runtime", errors)
    source = data.get("model_source")
    if source not in set(policy.get("model_sources", [])):
        errors.append(
            "execution_provenance.model_source: must use the policy vocabulary"
        )
    evidence_ref = non_empty_string(
        data.get("evidence_ref"), "execution_provenance.evidence_ref", errors
    )
    model = data.get("model")
    effort = data.get("reasoning_effort")
    if source == "unavailable":
        if model is not None or effort is not None:
            errors.append(
                "execution_provenance: unavailable source requires null model and reasoning_effort"
            )
    else:
        non_empty_string(model, "execution_provenance.model", errors)
        non_empty_string(
            effort, "execution_provenance.reasoning_effort", errors
        )
    if (
        source in {"runtime-reported", "provider-reported", "user-declared"}
        and not evidence_ref
    ):
        errors.append(
            "execution_provenance.evidence_ref: reported or declared values require evidence"
        )


def validate_attribution(
    value: Any,
    policy: dict[str, Any],
    validated_commit: str,
    errors: list[str],
) -> None:
    data = mapping(value, "attribution", errors)
    if data.get("preservation_required") is not True:
        errors.append("attribution.preservation_required: must be true")
    if data.get("evidence_union_version") != "1.0":
        errors.append("attribution.evidence_union_version: must be 1.0")
    selected = mapping(
        data.get("selected_evidence"), "attribution.selected_evidence", errors
    )
    kind = selected.get("kind")
    if kind not in set(policy.get("attribution_kinds", [])):
        errors.append("attribution.selected_evidence.kind: unsupported evidence kind")
    commit = git_sha(
        selected.get("commit"), "attribution.selected_evidence.commit", errors
    )
    if commit and validated_commit and commit != validated_commit:
        errors.append(
            "attribution.selected_evidence.commit: must equal repository.validated_commit"
        )
    non_empty_string(
        selected.get("author"), "attribution.selected_evidence.author", errors
    )
    non_empty_string(
        selected.get("committer"), "attribution.selected_evidence.committer", errors
    )
    signature = selected.get("signature_status")
    if signature not in SIGNATURE_STATUS:
        errors.append(
            "attribution.selected_evidence.signature_status: unsupported status"
        )
    sha256(
        selected.get("message_sha256"),
        "attribution.selected_evidence.message_sha256",
        errors,
    )
    selected_fixture_ref = non_empty_string(
        selected.get("fixture_ref"),
        "attribution.selected_evidence.fixture_ref",
        errors,
    )
    trailer = selected.get("observed_trailer")
    if kind in {
        "repository-created-local-ai-trailer",
        "provider-native-coauthor-trailer",
    }:
        trailer_text = non_empty_string(
            trailer, "attribution.selected_evidence.observed_trailer", errors
        )
        if trailer_text and not trailer_text.startswith("Co-Authored-By: "):
            errors.append(
                "attribution.selected_evidence.observed_trailer: "
                "must be an exact Co-Authored-By trailer"
            )
    elif trailer is not None:
        errors.append(
            "attribution.selected_evidence.observed_trailer: "
            "must be null for native authorship/session evidence"
        )
    if kind == "provider-native-authorship-or-signed-session":
        session_ref = selected.get("session_ref")
        if signature != "verified" and not (
            isinstance(session_ref, str) and session_ref.strip()
        ):
            errors.append(
                "attribution.selected_evidence: native authorship requires "
                "a verified signature or session_ref"
            )

    fixtures = data.get("fixture_status")
    if not isinstance(fixtures, list) or not fixtures:
        errors.append("attribution.fixture_status: must be a non-empty list")
        return
    seen: set[str] = set()
    captured_bindings: set[tuple[str, str]] = set()
    allowed_statuses = set(policy.get("fixture_statuses", []))
    for index, fixture_value in enumerate(fixtures):
        label = f"attribution.fixture_status[{index}]"
        fixture = mapping(fixture_value, label, errors)
        path_id = non_empty_string(fixture.get("path_id"), f"{label}.path_id", errors)
        if path_id in seen:
            errors.append(f"{label}.path_id: duplicate {path_id!r}")
        seen.add(path_id)
        status = fixture.get("status")
        if status not in allowed_statuses:
            errors.append(f"{label}.status: unsupported fixture status")
        evidence_ref = non_empty_string(
            fixture.get("evidence_ref"), f"{label}.evidence_ref", errors
        )
        reason = fixture.get("reason")
        fixture_commit = fixture.get("commit")
        if status == "captured":
            captured_commit = git_sha(fixture_commit, f"{label}.commit", errors)
            if reason is not None:
                errors.append(f"{label}.reason: captured fixture requires null reason")
            if captured_commit and evidence_ref:
                captured_bindings.add((captured_commit, evidence_ref))
        elif status == "blocked":
            if fixture_commit is not None:
                errors.append(f"{label}.commit: blocked fixture requires null commit")
            non_empty_string(reason, f"{label}.reason", errors)
        if not evidence_ref:
            errors.append(f"{label}.evidence_ref: fixture evidence is required")
    required_paths = set(str(item) for item in policy.get("required_fixture_paths", []))
    missing_paths = sorted(required_paths - seen)
    if missing_paths:
        errors.append(
            "attribution.fixture_status: missing required fixture paths "
            + ", ".join(missing_paths)
        )
    if commit and selected_fixture_ref and (commit, selected_fixture_ref) not in captured_bindings:
        errors.append(
            "attribution.selected_evidence.fixture_ref: must match a captured "
            "fixture for the selected commit"
        )


def validate_checkpoint_data(
    data: dict[str, Any],
    policy: dict[str, Any] | None = None,
    release_contract: dict[str, Any] | None = None,
) -> list[str]:
    policy = policy or load_policy()
    errors: list[str] = []
    if data.get("schema_version") != policy.get("checkpoint_schema_version"):
        errors.append("schema_version: does not match workflow handoff policy")
    checkpoint_id = non_empty_string(data.get("checkpoint_id"), "checkpoint_id", errors)
    if checkpoint_id and not CHECKPOINT_ID_RE.fullmatch(checkpoint_id):
        errors.append("checkpoint_id: must be path-safe")
    timestamp(data.get("created_at"), "created_at", errors)

    repository = mapping(data.get("repository"), "repository", errors)
    if repository.get("root") != ".":
        errors.append("repository.root: must be '.'")
    non_empty_string(repository.get("branch"), "repository.branch", errors)
    validated_commit = git_sha(
        repository.get("validated_commit"), "repository.validated_commit", errors
    )
    if repository.get("checkpoint_commit_source") != "containing-commit":
        errors.append(
            "repository.checkpoint_commit_source: must be containing-commit"
        )
    dirty_state = repository.get("dirty_state")
    if dirty_state not in {"clean", "dirty"}:
        errors.append("repository.dirty_state: must be clean or dirty")
    status_digest = sha256(
        repository.get("status_porcelain_sha256"),
        "repository.status_porcelain_sha256",
        errors,
    )
    if dirty_state == "clean" and status_digest:
        empty_digest = hashlib.sha256(b"").hexdigest()
        if status_digest != empty_digest:
            errors.append(
                "repository.status_porcelain_sha256: clean state requires "
                "SHA-256 of empty output"
            )

    workflow = mapping(data.get("workflow"), "workflow", errors)
    non_empty_string(workflow.get("workflow_id"), "workflow.workflow_id", errors)
    task_id = non_empty_string(workflow.get("task_id"), "workflow.task_id", errors)
    resume = mapping(data.get("resume"), "resume", errors)
    non_empty_string(
        resume.get("last_completed_action"), "resume.last_completed_action", errors
    )
    single_line_string(
        resume.get("exact_next_action"), "resume.exact_next_action", errors
    )
    if resume.get("hidden_context_required") is not False:
        errors.append("resume.hidden_context_required: must be false")

    _, critical_outcome = observed_gate(
        data.get("critical_gate"), "critical_gate", policy, errors, critical=True
    )
    continuation = mapping(data.get("continuation"), "continuation", errors)
    allowed = continuation.get("allowed")
    if not isinstance(allowed, bool):
        errors.append("continuation.allowed: must be a boolean")
    mode = continuation.get("mode")
    if mode not in set(policy.get("continuation_modes", [])):
        errors.append("continuation.mode: unsupported mode")
    non_empty_string(continuation.get("reason"), "continuation.reason", errors)
    repair_task_id = continuation.get("repair_task_id")
    failure_ids = continuation.get("failure_ids")
    if not isinstance(failure_ids, list) or not all(
        isinstance(item, str) and item.strip() for item in failure_ids
    ):
        errors.append("continuation.failure_ids: must be a string list")
        failure_ids = []
    if critical_outcome == "passed":
        if not allowed or mode != "normal":
            errors.append(
                "continuation: passed critical gate requires allowed normal continuation"
            )
        if repair_task_id is not None or failure_ids:
            errors.append(
                "continuation: passed critical gate cannot declare repair scope"
            )
    elif critical_outcome == "failed":
        repair_allowed = (
            allowed is True
            and mode == "repair-only"
            and repair_task_id == task_id
            and bool(failure_ids)
        )
        blocked = allowed is False and mode == "blocked"
        if not repair_allowed and not blocked:
            errors.append(
                "continuation: failed critical gate must block or name the "
                "current repair task and failure IDs"
            )

    release_handoff = data.get("release_handoff")
    if not isinstance(release_handoff, bool):
        errors.append("release_handoff: must be a boolean")
    phase_check = data.get("release_phase_check")
    if release_handoff is True:
        phase = mapping(phase_check, "release_phase_check", errors).get("phase")
        if phase not in set(policy.get("release_phases", [])):
            errors.append("release_phase_check.phase: unsupported release phase")
        phase_command = mapping(phase_check, "release_phase_check", errors).get(
            "command"
        )
        if release_contract is None:
            errors.append(
                "release_phase_check: REL-owned release phase contract is unavailable"
            )
        else:
            phases = mapping(
                release_contract.get("phases"),
                "release phase contract.phases",
                errors,
            )
            phase_record = mapping(
                phases.get(phase),
                f"release phase contract.phases.{phase}",
                errors,
            )
            expected_command = phase_record.get("command")
            if (
                not isinstance(expected_command, str)
                or not expected_command.strip()
                or phase_command != expected_command
            ):
                errors.append(
                    "release_phase_check.command: must equal the REL-owned "
                    "sanctioned phase command"
                )
        _, release_outcome = observed_gate(
            phase_check, "release_phase_check", policy, errors, critical=False
        )
        if release_outcome != "passed":
            errors.append(
                "release_phase_check: release handoff requires a passing phase check"
            )
    elif phase_check is not None:
        errors.append(
            "release_phase_check: must be null when release_handoff is false"
        )

    validate_provenance(data.get("execution_provenance"), policy, errors)
    validate_attribution(data.get("attribution"), policy, validated_commit, errors)
    return errors


def git_read(root: Path, allowlist: set[str], *args: str) -> str:
    if not args or args[0] not in allowlist:
        raise ValueError(f"Git command is not read-only allowlisted: {' '.join(args)}")
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def signature_label(code: str) -> str:
    if code in {"G", "U"}:
        return "verified"
    if code in {"B", "X", "Y", "R", "E"}:
        return "unverified"
    if code == "N":
        return "unsigned"
    return "unavailable"


def verify_repository(
    root: Path,
    checkpoint_path: Path,
    data: dict[str, Any],
    policy: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    allowlist = set(str(value) for value in policy.get("git_read_allowlist", []))
    repository = mapping(data.get("repository"), "repository", errors)
    attribution = mapping(data.get("attribution"), "attribution", errors)
    selected = mapping(
        attribution.get("selected_evidence"), "attribution.selected_evidence", errors
    )
    commit = str(repository.get("validated_commit", ""))
    branch = str(repository.get("branch", ""))
    try:
        current_branch = git_read(
            root, allowlist, "symbolic-ref", "--quiet", "--short", "HEAD"
        ).strip()
        if current_branch != branch:
            errors.append(
                f"repository.branch: expected {branch!r}, observed {current_branch!r}"
            )
        git_read(root, allowlist, "rev-parse", "--verify", f"{commit}^{{commit}}")
        relative = checkpoint_path.resolve().relative_to(root.resolve()).as_posix()
        containing = git_read(
            root, allowlist, "log", "-1", "--format=%H", "--", relative
        ).strip()
        if not containing:
            errors.append("repository.checkpoint_commit_source: checkpoint is not committed")
        head = git_read(root, allowlist, "rev-parse", "HEAD").strip()
        if containing and head != containing:
            errors.append(
                "repository.checkpoint_commit_source: checkpoint containing "
                "commit is not current HEAD"
            )
        if containing:
            git_read(
                root, allowlist, "merge-base", "--is-ancestor", commit, containing
            )
        status = git_read(root, allowlist, "status", "--porcelain=v1")
        observed_state = "dirty" if status else "clean"
        if observed_state != repository.get("dirty_state"):
            errors.append(
                f"repository.dirty_state: expected "
                f"{repository.get('dirty_state')!r}, observed {observed_state!r}"
            )
        status_digest = hashlib.sha256(status.encode("utf-8")).hexdigest()
        if status_digest != repository.get("status_porcelain_sha256"):
            errors.append(
                "repository.status_porcelain_sha256: current worktree status "
                "digest differs"
            )

        message = git_read(root, allowlist, "show", "-s", "--format=%B", commit)
        message_digest = hashlib.sha256(message.encode("utf-8")).hexdigest()
        if message_digest != selected.get("message_sha256"):
            errors.append(
                "attribution.selected_evidence.message_sha256: pinned commit "
                "message differs"
            )
        trailer = selected.get("observed_trailer")
        if isinstance(trailer, str) and trailer not in message.splitlines():
            errors.append(
                "attribution.selected_evidence.observed_trailer: not present "
                "verbatim in pinned commit"
            )
        observed_author = git_read(
            root, allowlist, "show", "-s", "--format=%an <%ae>", commit
        ).strip()
        if observed_author != selected.get("author"):
            errors.append("attribution.selected_evidence.author: pinned commit differs")
        observed_committer = git_read(
            root, allowlist, "show", "-s", "--format=%cn <%ce>", commit
        ).strip()
        if observed_committer != selected.get("committer"):
            errors.append(
                "attribution.selected_evidence.committer: pinned commit differs"
            )
        signature = git_read(
            root, allowlist, "show", "-s", "--format=%G?", commit
        ).strip()
        if signature_label(signature) != selected.get("signature_status"):
            errors.append(
                "attribution.selected_evidence.signature_status: pinned commit differs"
            )
    except (RuntimeError, ValueError, OSError) as exc:
        errors.append(f"repository verification failed: {exc}")
    return errors


def load_release_contract(
    root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    relative = policy.get("release_phase_contract_path")
    if not isinstance(relative, str) or not relative:
        errors.append("policy.release_phase_contract_path: must be a non-empty string")
        return None
    path = root / relative
    if not path.is_file():
        return None
    contract = load_mapping(path, relative, errors)
    if contract is not None and contract.get("schema_version") != "1.0":
        errors.append(f"{relative}: schema_version must be 1.0")
    return contract


def validate_registered_checkpoints(
    root: Path,
    policy: dict[str, Any],
) -> tuple[int, list[str], bool]:
    errors: list[str] = []
    relative = policy.get("checkpoint_registry_path")
    if not isinstance(relative, str) or not relative:
        return 0, ["policy.checkpoint_registry_path: must be a non-empty string"], False
    registry_path = root / relative
    source_context = (root / ".dev/releases").is_dir() and (
        root / ".ai/distribution"
    ).is_dir()
    if not registry_path.is_file():
        if source_context:
            errors.append(f"{relative}: required in the source repository")
        return 0, errors, False
    registry = load_mapping(registry_path, relative, errors)
    if registry is None:
        return 0, errors, True
    if registry.get("schema_version") != "1.0":
        errors.append(f"{relative}: schema_version must be 1.0")
    values = registry.get("checkpoints")
    if not isinstance(values, list) or not all(
        isinstance(item, str) and item.strip() for item in values
    ):
        errors.append(f"{relative}: checkpoints must be a string list")
        return 0, errors, True
    if len(values) != len(set(values)):
        errors.append(f"{relative}: checkpoints must not contain duplicates")
    release_contract = load_release_contract(root, policy, errors)
    checked = 0
    for value in values:
        path = (root / value).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{relative}: checkpoint escapes repository: {value}")
            continue
        checkpoint = load_mapping(path, value, errors)
        if checkpoint is None:
            continue
        checked += 1
        errors.extend(
            f"{value}: {error}"
            for error in validate_checkpoint_data(
                checkpoint,
                policy,
                release_contract,
            )
        )
    return checked, errors, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--checkpoint", type=Path)
    selector.add_argument(
        "--all",
        action="store_true",
        help="Validate every checkpoint in the repository handoff registry",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--verify-repository",
        action="store_true",
        help="Verify current branch, containing commit, worktree, and pinned attribution",
    )
    args = parser.parse_args()
    if args.all and args.verify_repository:
        parser.error("--verify-repository requires one --checkpoint")
    root = args.root.resolve()
    policy = load_policy(root)
    if args.all:
        checked, errors, available = validate_registered_checkpoints(root, policy)
        if errors:
            print("Workflow handoff validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        if not available:
            print("Workflow handoff registry not applicable in this target.")
            return 0
        print(
            f"Workflow handoff registry validation passed for {checked} checkpoint(s)."
        )
        return 0
    assert args.checkpoint is not None
    checkpoint_path = (
        args.checkpoint
        if args.checkpoint.is_absolute()
        else root / args.checkpoint
    )
    errors: list[str] = []
    data = load_mapping(checkpoint_path, str(args.checkpoint), errors)
    release_contract = load_release_contract(root, policy, errors)
    if data is not None:
        errors.extend(validate_checkpoint_data(data, policy, release_contract))
        if args.verify_repository:
            errors.extend(verify_repository(root, checkpoint_path, data, policy))
    if errors:
        print("Workflow handoff validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    mode = " with repository verification" if args.verify_repository else ""
    print(f"Workflow handoff validation passed{mode}: {args.checkpoint}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
