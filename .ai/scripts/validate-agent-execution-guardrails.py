#!/usr/bin/env python3
"""Fail-closed validation for agent packets, leases, evidence, retries, and graph freshness."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-agent-execution-guardrails.py")

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / ".ai/assets/shared/agent-execution-guardrails.schema.yaml"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_REF = re.compile(r"^(?:ignored|workflow|issue|commit|run|job|fixture|tracked):[^\s]+$")
ACTUAL_REF = re.compile(r"^(?:ignored|run|job):[^\s]+$")


class GuardrailError(ValueError):
    pass


def mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GuardrailError(f"{name} must be a mapping")
    return value


def exact_keys(value: dict[str, Any], required: set[str], name: str) -> None:
    if set(value) != required:
        raise GuardrailError(f"{name} keys must be exactly {sorted(required)}")


def string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GuardrailError(f"{name} must be a non-empty string")
    return value


def strings(value: Any, name: str, *, empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not empty and not value) or any(not isinstance(item, str) or not item for item in value):
        raise GuardrailError(f"{name} must be a list of non-empty strings")
    return value


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sealed(record: dict[str, Any], field: str) -> None:
    claimed = record.get(field)
    if not isinstance(claimed, str) or not SHA256.fullmatch(claimed):
        raise GuardrailError(f"{field} must be lowercase SHA-256")
    if claimed != digest({key: value for key, value in record.items() if key != field}):
        raise GuardrailError(f"{field} does not match canonical content")


def repo_relative_path(value: Any, name: str, *, must_exist: bool = True) -> Path:
    text = string(value, name)
    candidate = Path(text)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise GuardrailError(f"{name} must be a contained repository-relative path")
    resolved = (ROOT / candidate).resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise GuardrailError(f"{name} escapes the repository")
    if must_exist and not resolved.exists():
        raise GuardrailError(f"{name} does not exist")
    return resolved


def local_evidence_ref(value: Any, name: str) -> Path:
    ref = string(value, name)
    if not ref.startswith("ignored:"):
        raise GuardrailError(f"{name} must use an ignored repository-local evidence reference")
    return repo_relative_path(ref.split(":", 1)[1], name)


def load_workflow_authorization(value: Any, name: str) -> dict[str, Any]:
    ref = string(value, name)
    if not ref.startswith("workflow:"):
        raise GuardrailError(f"{name} must use a workflow-local authorization record")
    path = repo_relative_path(ref.split(":", 1)[1], name)
    authorization = mapping(yaml.safe_load(path.read_text(encoding="utf-8")), name)
    required = {"schema_version", "record_type", "workflow_id", "task_id", "attempt", "authorized_at", "subject_sha", "prior_failure_sha256", "decision", "consumed_by_packet_id", "scope", "non_goals", "terminal_condition", "authorization_sha256"}
    exact_keys(authorization, required, name)
    if authorization["schema_version"] != "1.0" or authorization["record_type"] != "workflow-retry-authorization" or authorization["decision"] != "authorize-retry":
        raise GuardrailError(f"{name} identity is invalid")
    if not isinstance(authorization["attempt"], int) or authorization["attempt"] < 3 or not SHA40.fullmatch(str(authorization["subject_sha"])) or not SHA256.fullmatch(str(authorization["prior_failure_sha256"])):
        raise GuardrailError(f"{name} binding is invalid")
    strings(authorization["scope"], f"{name}.scope")
    strings(authorization["non_goals"], f"{name}.non_goals")
    string(authorization["workflow_id"], f"{name}.workflow_id")
    string(authorization["task_id"], f"{name}.task_id")
    string(authorization["authorized_at"], f"{name}.authorized_at")
    string(authorization["consumed_by_packet_id"], f"{name}.consumed_by_packet_id")
    string(authorization["terminal_condition"], f"{name}.terminal_condition")
    sealed(authorization, "authorization_sha256")
    return authorization


def tracked_path(value: Any, name: str) -> Path:
    resolved = repo_relative_path(value, name)
    relative = resolved.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--", relative],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise GuardrailError(f"{name} is not Git-tracked")
    return resolved


def iso_with_offset(value: Any, name: str) -> None:
    if not isinstance(value, str):
        raise GuardrailError(f"{name} must be ISO 8601 with an offset")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GuardrailError(f"{name} must be ISO 8601 with an offset") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise GuardrailError(f"{name} must be ISO 8601 with an offset")


def lease_lock_bytes(record: dict[str, Any]) -> bytes:
    holder = mapping(record.get("holder"), "holder")
    payload = {
        "lease_id": record.get("lease_id"),
        "packet_id": holder.get("packet_id"),
        "subject_sha": record.get("subject_sha"),
    }
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def acquire_lease_lock(record: dict[str, Any]) -> None:
    if record.get("state") != "active":
        raise GuardrailError("only an active lease can acquire a lock")
    holder = mapping(record.get("holder"), "holder")
    lock_path = repo_relative_path(holder.get("lock_ref"), "holder.lock_ref", must_exist=False)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lock_path.open("xb") as stream:
            stream.write(lease_lock_bytes(record))
    except FileExistsError as exc:
        raise GuardrailError("worktree lease lock already exists; another compliant holder may be active") from exc


def reject_private(value: Any, schema: dict[str, Any], path: str = "record") -> None:
    if isinstance(value, dict):
        forbidden = set(schema["privacy_forbidden_keys"])
        for key, nested in value.items():
            if str(key).lower() in forbidden:
                raise GuardrailError(f"{path}.{key} is privacy-forbidden")
            reject_private(nested, schema, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            reject_private(nested, schema, f"{path}[{index}]")


def validate_packet(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "packet_id", "execution_kind", "owning_skill", "role", "subject", "invocation", "permissions", "ignored_artifact_roots", "terminal", "integration_owner", "stop_conditions", "retry", "packet_sha256"}, "packet")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["packet"]:
        raise GuardrailError("packet schema identity is invalid")
    string(record["packet_id"], "packet_id")
    owning_skill = string(record["owning_skill"], "owning_skill")
    if record["execution_kind"] not in schema["execution_kinds"]:
        raise GuardrailError("execution_kind is invalid")
    role = mapping(record["role"], "role")
    exact_keys(role, {"path", "applicability", "reason"}, "role")
    if not string(role["path"], "role.path").startswith(".ai/assets/sub-agent-role-prompts/") or not role["path"].endswith("/sub-agent.yaml"):
        raise GuardrailError("role.path must be canonical")
    role_path = tracked_path(role["path"], "role.path")
    role_asset = mapping(yaml.safe_load(role_path.read_text(encoding="utf-8")), "role asset")
    if role_asset.get("asset_type") != "sub-agent-role-prompt" or role_asset.get("source_of_truth") != "canonical" or role_asset.get("status") != "active":
        raise GuardrailError("role.path must resolve to an active canonical role asset")
    skill_path = tracked_path(f".ai/assets/skills/{owning_skill}/skill.yaml", "owning_skill canonical spec")
    skill = mapping(yaml.safe_load(skill_path.read_text(encoding="utf-8")), "owning skill")
    bindings = skill.get("role_bindings")
    if not isinstance(bindings, list) or not any(isinstance(item, dict) and item.get("role_path") == role["path"] for item in bindings):
        raise GuardrailError("role.path is not canonically bound by owning_skill")
    if role["applicability"] not in schema["role_applicability"]:
        raise GuardrailError("role.applicability is invalid")
    string(role["reason"], "role.reason")
    subject = mapping(record["subject"], "subject")
    exact_keys(subject, {"repository", "exact_sha"}, "subject")
    string(subject["repository"], "subject.repository")
    if not isinstance(subject["exact_sha"], str) or not SHA40.fullmatch(subject["exact_sha"]):
        raise GuardrailError("subject.exact_sha must be a lowercase 40-character SHA")
    invocation = mapping(record["invocation"], "invocation")
    exact_keys(invocation, {"argv", "cwd"}, "invocation")
    strings(invocation["argv"], "invocation.argv")
    string(invocation["cwd"], "invocation.cwd")
    permissions = mapping(record["permissions"], "permissions")
    exact_keys(permissions, {"network", "tracked_write", "provider_mutation"}, "permissions")
    if any(value not in schema["permission_modes"] for value in permissions.values()):
        raise GuardrailError("permissions must use allow or deny")
    ignored = strings(record["ignored_artifact_roots"], "ignored_artifact_roots", empty=True)
    if any(Path(item).is_absolute() or ".." in Path(item).parts for item in ignored):
        raise GuardrailError("ignored artifact roots must be contained repository-relative paths")
    terminal = mapping(record["terminal"], "terminal")
    exact_keys(terminal, {"schema_ref", "mode", "destination", "max_terminal_messages"}, "terminal")
    string(terminal["schema_ref"], "terminal.schema_ref")
    if terminal["mode"] not in schema["terminal_modes"] or terminal["max_terminal_messages"] != 1:
        raise GuardrailError("terminal transport must be one callback or event wait")
    string(terminal["destination"], "terminal.destination")
    string(record["integration_owner"], "integration_owner")
    strings(record["stop_conditions"], "stop_conditions")
    retry = mapping(record["retry"], "retry")
    exact_keys(retry, {"attempt", "budget", "authorization_refs"}, "retry")
    if not isinstance(retry["attempt"], int) or retry["attempt"] < 1 or not isinstance(retry["budget"], int) or retry["budget"] < retry["attempt"]:
        raise GuardrailError("retry attempt and budget are invalid")
    authorizations = strings(retry["authorization_refs"], "retry.authorization_refs", empty=True)
    if retry["attempt"] >= 3:
        if not authorizations or len(authorizations) != len(set(authorizations)):
            raise GuardrailError("attempt 3+ requires new owner or workflow authorization")
        for index, ref in enumerate(authorizations):
            authorization = load_workflow_authorization(ref, f"retry.authorization_refs[{index}]")
            if authorization["attempt"] != retry["attempt"] or authorization["subject_sha"] != subject["exact_sha"] or authorization["consumed_by_packet_id"] != record["packet_id"]:
                raise GuardrailError("retry authorization is not bound to this packet and attempt")
    if record["execution_kind"] in {"external", "fixed-head-audit"} and (permissions["tracked_write"] != "deny" or permissions["provider_mutation"] != "deny"):
        raise GuardrailError("external and fixed-head execution must be read-only")
    reject_private(record, schema)
    sealed(record, "packet_sha256")


def validate_lease(record: dict[str, Any], schema: dict[str, Any], *, verify_live: bool = True) -> None:
    exact_keys(record, {"schema_version", "record_type", "lease_id", "worktree", "subject_sha", "observed_snapshot", "snapshot_sha256", "state", "holder", "observed_other_tracked_writers", "ignored_artifacts", "tracked_mutations", "terminal_release", "lease_sha256"}, "lease")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["lease"]:
        raise GuardrailError("lease schema identity is invalid")
    string(record["lease_id"], "lease_id")
    worktree = repo_relative_path(record["worktree"], "worktree")
    if not isinstance(record["subject_sha"], str) or not SHA40.fullmatch(record["subject_sha"]):
        raise GuardrailError("lease subject_sha is invalid")
    if not isinstance(record["snapshot_sha256"], str) or not SHA256.fullmatch(record["snapshot_sha256"]):
        raise GuardrailError("snapshot_sha256 is invalid")
    if record["state"] not in schema["lease_states"]:
        raise GuardrailError("lease state is invalid")
    observed = mapping(record["observed_snapshot"], "observed_snapshot")
    exact_keys(observed, {"head_sha", "tracked_status"}, "observed_snapshot")
    if observed["head_sha"] != record["subject_sha"] or not isinstance(observed["tracked_status"], list) or any(not isinstance(item, str) for item in observed["tracked_status"]):
        raise GuardrailError("observed snapshot identity is invalid")
    if record["snapshot_sha256"] != digest(observed):
        raise GuardrailError("snapshot_sha256 does not bind observed snapshot")
    holder = mapping(record["holder"], "holder")
    exact_keys(holder, {"packet_id", "access", "lock_ref", "lock_sha256"}, "holder")
    string(holder["packet_id"], "holder.packet_id")
    if holder["access"] not in schema["lease_access"]:
        raise GuardrailError("holder access is invalid")
    lock_path = repo_relative_path(holder["lock_ref"], "holder.lock_ref", must_exist=record["state"] == "active" and verify_live)
    if not str(Path(holder["lock_ref"]).as_posix()).startswith(".dev/ai-context/local/") or not SHA256.fullmatch(str(holder["lock_sha256"])):
        raise GuardrailError("holder lock must be a digest-bound ignored local artifact")
    if holder["lock_sha256"] != hashlib.sha256(lease_lock_bytes(record)).hexdigest():
        raise GuardrailError("holder.lock_sha256 does not bind lease identity")
    if record["state"] == "active" and verify_live and hashlib.sha256(lock_path.read_bytes()).hexdigest() != holder["lock_sha256"]:
        raise GuardrailError("active lease lock digest is invalid")
    other_writers = strings(record["observed_other_tracked_writers"], "observed_other_tracked_writers", empty=True)
    mutations = strings(record["tracked_mutations"], "tracked_mutations", empty=True)
    artifacts = record["ignored_artifacts"]
    if not isinstance(artifacts, list):
        raise GuardrailError("ignored_artifacts must be a list")
    for item in artifacts:
        item = mapping(item, "ignored_artifact")
        exact_keys(item, {"path", "state", "sha256"}, "ignored_artifact")
        string(item["path"], "ignored_artifact.path")
        if item["state"] not in schema["artifact_states"]:
            raise GuardrailError("ignored artifact state is invalid")
        if item["sha256"] is not None and (not isinstance(item["sha256"], str) or not SHA256.fullmatch(item["sha256"])):
            raise GuardrailError("ignored artifact digest is invalid")
    terminal_release = mapping(record["terminal_release"], "terminal_release")
    exact_keys(terminal_release, {"released", "reason"}, "terminal_release")
    if not isinstance(terminal_release["released"], bool):
        raise GuardrailError("terminal_release.released must be boolean")
    string(terminal_release["reason"], "terminal_release.reason")
    if record["state"] == "active" and holder["access"] == "tracked-writer" and other_writers:
        raise GuardrailError("active lease rejects another tracked writer")
    if record["state"] == "active" and mutations:
        raise GuardrailError("active lease snapshot drifted")
    if record["state"] == "active" and observed["tracked_status"]:
        raise GuardrailError("active lease observed tracked drift")
    if record["state"] == "released" and (mutations or not terminal_release["released"] or any(item["state"] == "open" for item in artifacts)):
        raise GuardrailError("released lease requires clean tracked state and terminal artifact release")
    if record["state"] == "invalidated" and terminal_release["released"]:
        raise GuardrailError("invalidated lease cannot claim terminal release")
    if verify_live and record["state"] == "active":
        head = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"], check=True, capture_output=True, text=True, encoding="utf-8").stdout.strip()
        status = subprocess.run(["git", "-C", str(worktree), "status", "--porcelain=v1", "--untracked-files=no"], check=True, capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
        if {"head_sha": head, "tracked_status": status} != observed:
            raise GuardrailError("lease snapshot does not match live worktree state")
    reject_private(record, schema)
    sealed(record, "lease_sha256")


def validate_evidence(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "subject_sha", "entries", "human_report", "ledger_sha256"}, "evidence ledger")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["evidence"]:
        raise GuardrailError("evidence schema identity is invalid")
    if not isinstance(record["subject_sha"], str) or not SHA40.fullmatch(record["subject_sha"]):
        raise GuardrailError("evidence subject_sha is invalid")
    entries = record["entries"]
    if not isinstance(entries, list) or not entries:
        raise GuardrailError("entries must be non-empty")
    expected: dict[str, tuple[str, str]] = {}
    for entry in entries:
        entry = mapping(entry, "entry")
        exact_keys(entry, {"acceptance_id", "issue", "requires_actual_execution", "evidence_kind", "command", "profile", "subject_sha", "outcome", "evidence_refs", "evidence_sha256", "execution_receipt_ref", "execution_receipt_file_sha256", "execution_receipt"}, "entry")
        acceptance = string(entry["acceptance_id"], "acceptance_id")
        if acceptance in expected:
            raise GuardrailError("acceptance identifiers must be unique")
        if not isinstance(entry["issue"], int) or entry["issue"] <= 0 or not isinstance(entry["requires_actual_execution"], bool):
            raise GuardrailError("entry issue or actual-execution flag is invalid")
        if entry["evidence_kind"] not in schema["evidence_kinds"] or entry["outcome"] not in schema["outcomes"]:
            raise GuardrailError("entry evidence kind or outcome is invalid")
        string(entry["command"], "entry.command")
        string(entry["profile"], "entry.profile")
        if entry["subject_sha"] != record["subject_sha"]:
            raise GuardrailError("entry subject SHA must match ledger subject")
        refs = strings(entry["evidence_refs"], "entry.evidence_refs")
        if any(not SAFE_REF.fullmatch(ref) for ref in refs):
            raise GuardrailError("evidence references must use privacy-safe typed references")
        if not isinstance(entry["evidence_sha256"], str) or not SHA256.fullmatch(entry["evidence_sha256"]):
            raise GuardrailError("entry evidence_sha256 is invalid")
        if entry["requires_actual_execution"] and entry["evidence_kind"] != "actual-execution":
            raise GuardrailError("synthetic, mock, unit, or document evidence cannot satisfy actual execution")
        receipt = entry["execution_receipt"]
        if entry["evidence_kind"] == "actual-execution":
            if len(refs) != 1:
                raise GuardrailError("actual execution requires exactly one repository-local output reference")
            output_path = local_evidence_ref(refs[0], "entry.evidence_refs[0]")
            if hashlib.sha256(output_path.read_bytes()).hexdigest() != entry["evidence_sha256"]:
                raise GuardrailError("actual execution output file digest is invalid")
            receipt_path = local_evidence_ref(entry["execution_receipt_ref"], "entry.execution_receipt_ref")
            if not SHA256.fullmatch(str(entry["execution_receipt_file_sha256"])) or hashlib.sha256(receipt_path.read_bytes()).hexdigest() != entry["execution_receipt_file_sha256"]:
                raise GuardrailError("actual execution receipt file digest is invalid")
            receipt = mapping(receipt, "entry.execution_receipt")
            exact_keys(receipt, {"schema_version", "record_type", "producer", "subject_sha", "command", "profile", "started_at", "completed_at", "duration_seconds", "executed", "synthetic", "outcome", "exit_code", "evidence_refs", "evidence_sha256", "receipt_sha256"}, "entry.execution_receipt")
            if receipt["schema_version"] != schema["schema_version"] or receipt["record_type"] != "terminal-command-execution" or receipt["producer"] not in schema["execution_receipt_producers"]:
                raise GuardrailError("actual execution receipt identity is invalid")
            if receipt["subject_sha"] != entry["subject_sha"] or receipt["command"] != entry["command"] or receipt["profile"] != entry["profile"] or receipt["outcome"] != entry["outcome"]:
                raise GuardrailError("actual execution receipt does not bind the ledger entry")
            iso_with_offset(receipt["started_at"], "execution_receipt.started_at")
            iso_with_offset(receipt["completed_at"], "execution_receipt.completed_at")
            if not isinstance(receipt["duration_seconds"], (int, float)) or isinstance(receipt["duration_seconds"], bool) or receipt["duration_seconds"] < 0 or receipt["executed"] is not True or receipt["synthetic"] is not False:
                raise GuardrailError("actual execution receipt must prove a measured non-synthetic execution")
            receipt_refs = strings(receipt["evidence_refs"], "execution_receipt.evidence_refs")
            if any(not ACTUAL_REF.fullmatch(ref) for ref in receipt_refs) or receipt_refs != refs or receipt["evidence_sha256"] != entry["evidence_sha256"]:
                raise GuardrailError("actual execution receipt evidence binding is invalid")
            if receipt["outcome"] == "passed" and receipt["exit_code"] != 0:
                raise GuardrailError("passed actual execution requires exit_code zero")
            if receipt["exit_code"] is not None and (not isinstance(receipt["exit_code"], int) or isinstance(receipt["exit_code"], bool)):
                raise GuardrailError("execution receipt exit_code is invalid")
            sealed(receipt, "receipt_sha256")
            persisted_receipt = mapping(yaml.safe_load(receipt_path.read_text(encoding="utf-8")), "persisted execution receipt")
            if persisted_receipt != receipt:
                raise GuardrailError("persisted execution receipt does not match ledger receipt")
        elif receipt is not None:
            raise GuardrailError("non-actual evidence cannot carry an execution receipt")
        elif entry["execution_receipt_ref"] is not None or entry["execution_receipt_file_sha256"] is not None:
            raise GuardrailError("non-actual evidence cannot carry execution receipt file binding")
        expected[acceptance] = (entry["outcome"], entry["evidence_sha256"])
    report = mapping(record["human_report"], "human_report")
    exact_keys(report, {"entries", "report_sha256"}, "human_report")
    projected: dict[str, tuple[str, str]] = {}
    if not isinstance(report["entries"], list):
        raise GuardrailError("human_report.entries must be a list")
    for item in report["entries"]:
        item = mapping(item, "human_report entry")
        exact_keys(item, {"acceptance_id", "outcome", "evidence_sha256"}, "human_report entry")
        report_id = string(item["acceptance_id"], "human acceptance_id")
        if report_id in projected or item["outcome"] not in schema["outcomes"] or not SHA256.fullmatch(str(item["evidence_sha256"])):
            raise GuardrailError("human report entry is duplicated or invalid")
        projected[report_id] = (item["outcome"], item["evidence_sha256"])
    if projected != expected:
        raise GuardrailError("human report does not match acceptance evidence ledger")
    if report["report_sha256"] != digest(report["entries"]):
        raise GuardrailError("human report digest is invalid")
    reject_private(record, schema)
    sealed(record, "ledger_sha256")


def validate_retry(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "attempt", "failure", "prior_failure_sha256", "material_state_change_sha256", "prior_authorization_sha256", "new_authorizations", "decision", "retry_sha256"}, "retry")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["retry"]:
        raise GuardrailError("retry schema identity is invalid")
    if not isinstance(record["attempt"], int) or record["attempt"] < 1 or record["decision"] not in schema["retry_decisions"]:
        raise GuardrailError("retry attempt or decision is invalid")
    failure = mapping(record["failure"], "failure")
    exact_keys(failure, {"failure_class", "command_sha256", "subject_sha", "environment_class", "diagnostic_codes"}, "failure")
    string(failure["failure_class"], "failure_class")
    string(failure["environment_class"], "environment_class")
    strings(failure["diagnostic_codes"], "diagnostic_codes", empty=True)
    if not isinstance(failure["command_sha256"], str) or not SHA256.fullmatch(failure["command_sha256"]) or not isinstance(failure["subject_sha"], str) or not SHA40.fullmatch(failure["subject_sha"]):
        raise GuardrailError("failure identity is invalid")
    for field in ("prior_failure_sha256", "material_state_change_sha256"):
        if record[field] is not None and (not isinstance(record[field], str) or not SHA256.fullmatch(record[field])):
            raise GuardrailError(f"{field} is invalid")
    if record["prior_authorization_sha256"] is not None and not SHA256.fullmatch(str(record["prior_authorization_sha256"])):
        raise GuardrailError("prior_authorization_sha256 is invalid")
    authorizations = record["new_authorizations"]
    if not isinstance(authorizations, list):
        raise GuardrailError("new_authorizations must be a list")
    authorization_digests: set[str] = set()
    for authorization_value in authorizations:
        authorization = mapping(authorization_value, "new_authorization")
        exact_keys(authorization, {"ref", "attempt", "subject_sha", "prior_failure_sha256", "decision", "consumed_by_packet_id", "authorization_sha256"}, "new_authorization")
        if not string(authorization["ref"], "new_authorization.ref").startswith(("workflow:", "issue:")) or authorization["attempt"] != record["attempt"] or authorization["subject_sha"] != failure["subject_sha"] or authorization["prior_failure_sha256"] != record["prior_failure_sha256"] or authorization["decision"] != "authorize-retry" or not string(authorization["consumed_by_packet_id"], "new_authorization.consumed_by_packet_id"):
            raise GuardrailError("new authorization is not bound to this retry")
        persisted = load_workflow_authorization(authorization["ref"], "new_authorization.ref")
        if persisted["attempt"] != authorization["attempt"] or persisted["subject_sha"] != authorization["subject_sha"] or persisted["prior_failure_sha256"] != authorization["prior_failure_sha256"] or persisted["decision"] != authorization["decision"] or persisted["consumed_by_packet_id"] != authorization["consumed_by_packet_id"] or persisted["authorization_sha256"] != authorization["authorization_sha256"]:
            raise GuardrailError("new authorization does not match its persisted workflow record")
        if authorization["authorization_sha256"] == record["prior_authorization_sha256"] or authorization["authorization_sha256"] in authorization_digests:
            raise GuardrailError("retry authorization must be new")
        authorization_digests.add(authorization["authorization_sha256"])
    if record["decision"] == "retry" and record["attempt"] >= 2 and record["material_state_change_sha256"] is None:
        raise GuardrailError("retry without material state change is forbidden")
    if record["decision"] == "retry" and record["attempt"] >= 3 and not authorizations:
        raise GuardrailError("attempt 3+ retry requires new owner or workflow authorization")
    reject_private(record, schema)
    sealed(record, "retry_sha256")


def validate_graph(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "project", "head_sha", "indexed_sha", "index_state", "coverage", "reindex_attempted", "fallback", "fallback_paths", "absence_claim", "freshness_sha256"}, "graph freshness")
    if record["schema_version"] != schema["schema_version"] or record["record_type"] != schema["record_types"]["graph"]:
        raise GuardrailError("graph schema identity is invalid")
    string(record["project"], "project")
    if not isinstance(record["head_sha"], str) or not SHA40.fullmatch(record["head_sha"]):
        raise GuardrailError("graph head_sha is invalid")
    if record["indexed_sha"] is not None and (not isinstance(record["indexed_sha"], str) or not SHA40.fullmatch(record["indexed_sha"])):
        raise GuardrailError("graph indexed_sha is invalid")
    if record["index_state"] not in schema["graph_states"] or record["coverage"] not in schema["graph_coverage"] or record["fallback"] not in schema["graph_fallbacks"]:
        raise GuardrailError("graph freshness state is invalid")
    if not isinstance(record["reindex_attempted"], bool) or not isinstance(record["absence_claim"], bool):
        raise GuardrailError("graph booleans are invalid")
    paths = strings(record["fallback_paths"], "fallback_paths", empty=True)
    if paths:
        for index, path in enumerate(paths):
            tracked_path(path, f"fallback_paths[{index}]")
    exact_complete = record["index_state"] == "fresh" and record["coverage"] == "complete" and record["indexed_sha"] == record["head_sha"]
    tracked_fallback = record["fallback"] == "tracked-search" and bool(paths) and record["coverage"] == "complete"
    if record["index_state"] in {"stale", "missing"} and not record["reindex_attempted"] and not tracked_fallback:
        raise GuardrailError("stale or missing graph requires reindex or tracked fallback")
    if record["absence_claim"] and not (exact_complete or tracked_fallback):
        raise GuardrailError("search absence is not proof without exact complete index or tracked fallback")
    reject_private(record, schema)
    sealed(record, "freshness_sha256")


def validate_powershell_source(source: str, schema: dict[str, Any]) -> None:
    reserved = set(schema["reserved_powershell_variables"])
    assignment = re.compile(r"(?i)(?<![A-Za-z0-9_$])\$(?:global:|script:|local:)?([a-z_][a-z0-9_]*)\s*(?:=|\+=|-=|\+\+|--)")
    violations = sorted({match.group(1) for match in assignment.finditer(source) if match.group(1).lower() in reserved}, key=str.lower)
    if violations:
        raise GuardrailError(f"PowerShell reserved automatic variable assignment: {', '.join(violations)}")


def load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return mapping(value, str(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--packet", type=Path)
    group.add_argument("--lease", type=Path)
    group.add_argument("--evidence-ledger", type=Path)
    group.add_argument("--retry", type=Path)
    group.add_argument("--graph-freshness", type=Path)
    group.add_argument("--powershell-source", type=Path)
    parser.add_argument("--acquire-lock", action="store_true", help="atomically create the active lease lock before live validation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema = load(SCHEMA_PATH)
    try:
        if args.packet:
            validate_packet(load(args.packet), schema)
        elif args.lease:
            lease_record = load(args.lease)
            if args.acquire_lock:
                validate_lease(lease_record, schema, verify_live=False)
                acquire_lease_lock(lease_record)
            validate_lease(lease_record, schema)
        elif args.evidence_ledger:
            validate_evidence(load(args.evidence_ledger), schema)
        elif args.retry:
            validate_retry(load(args.retry), schema)
        elif args.graph_freshness:
            validate_graph(load(args.graph_freshness), schema)
        elif args.powershell_source:
            validate_powershell_source(args.powershell_source.read_text(encoding="utf-8"), schema)
        else:
            required = {"schema_version", "contract_id", "record_types", "execution_kinds", "role_applicability", "permission_modes", "lease_states", "lease_access", "artifact_states", "evidence_kinds", "execution_receipt_producers", "actual_execution_binding", "outcomes", "retry_decisions", "graph_states", "graph_coverage", "graph_fallbacks", "terminal_modes", "reserved_powershell_variables", "privacy_forbidden_keys"}
            exact_keys(schema, required, "schema")
        print("Agent execution guardrails passed.")
        return 0
    except (GuardrailError, OSError, yaml.YAMLError) as exc:
        print(f"Agent execution guardrails failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
