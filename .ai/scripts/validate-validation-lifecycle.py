#!/usr/bin/env python3
"""Validate validation taxonomy, content-addressed reuse, freeze, and audit records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-validation-lifecycle.py")

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / ".ai/assets/shared/validation-evidence-lifecycle.schema.yaml"
PROVIDER_POLICY = ROOT / ".dev/standards/GITHUB-WORK-MANAGEMENT-POLICY.yaml"
SHA_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]*$")
FORBIDDEN_KEYS = {"private_path", "username", "hostname", "secret", "token"}


class LifecycleError(ValueError):
    pass


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LifecycleError(f"{label} must be a mapping")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise LifecycleError(f"{label} fields are invalid")


def string_list(value: object, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise LifecycleError(f"{label} must be a non-empty string list")
    return value


def digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise LifecycleError(f"{label} must be a SHA-256 digest")
    return value


def reject_private_fields(value: object, label: str = "record") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise LifecycleError(f"{label} contains forbidden private field: {key}")
            reject_private_fields(child, label)
    elif isinstance(value, list):
        for child in value:
            reject_private_fields(child, label)


def load_record(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise LifecycleError(f"cannot read record: {exc}") from exc
    record = mapping(value, "record")
    reject_private_fields(record)
    return record


def validate_schema(schema: dict[str, Any]) -> None:
    if schema.get("schema_version") != "1.0" or schema.get("contract_id") != "validation-evidence-lifecycle":
        raise LifecycleError("validation lifecycle schema identity is invalid")
    classes = mapping(schema.get("evidence_classes"), "schema.evidence_classes")
    if list(classes) != ["identity-sensitive", "input-sensitive", "environment-sensitive", "provider-sensitive"]:
        raise LifecycleError("validation evidence taxonomy is invalid")
    if schema.get("audit_dispositions") != ["re-executed", "reused-with-proof", "blocked", "deferred", "not-applicable"]:
        raise LifecycleError("audit dispositions are invalid")
    receipt = mapping(schema.get("reuse_receipt"), "schema.reuse_receipt")
    if receipt.get("authority_dimensions") != ["runner", "manifest", "resolver", "policy", "configuration"]:
        raise LifecycleError("reuse authority dimensions are invalid")
    if receipt.get("required_fresh_gates") != ["exact-head-independent-audit", "hosted-required-contexts", "live-merge-admission"]:
        raise LifecycleError("fresh non-reusable gates are invalid")


def comparison_pair(value: object, label: str) -> tuple[str, str]:
    item = mapping(value, label)
    exact_keys(item, {"original", "current"}, label)
    return digest(item["original"], f"{label}.original"), digest(item["current"], f"{label}.current")


def resolve_bash() -> str:
    candidates = [
        Path("C:/Program Files/Git/bin/bash.exe"),
        Path("C:/Program Files/Git/usr/bin/bash.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    discovered = shutil.which("bash")
    if discovered:
        return discovered
    raise LifecycleError("canonical closure resolver requires bash")


def authoritative_closure(check_id: str, subject_sha: str) -> list[str]:
    result = subprocess.run(
        [resolve_bash(), ".ai/scripts/check-all.sh", "--resolve-input-closure", check_id, "--subject", subject_sha],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise LifecycleError("canonical dependency closure resolver failed")
    paths = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    if not paths or paths != sorted(set(paths)):
        raise LifecycleError("canonical dependency closure resolver returned invalid paths")
    for path in paths:
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise LifecycleError("canonical dependency closure escaped the repository")
    return paths


def git_object(subject_sha: str, path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"{subject_sha}:{path}"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    value = result.stdout.strip().lower()
    if result.returncode != 0 or not SHA_RE.fullmatch(value):
        raise LifecycleError("dependency path is not present at the bound subject")
    return value


def expected_reuse_decision(record: dict[str, Any], schema: dict[str, Any]) -> tuple[str, str]:
    evidence_class = record.get("evidence_class")
    profile = mapping(record.get("invocation"), "receipt.invocation").get("profile")
    if evidence_class in {"identity-sensitive", "provider-sensitive"} or profile in schema["reuse_receipt"]["terminal_profiles"]:
        return "re-executed", "fresh-gate-or-terminal-profile"
    dependencies = record.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        return "blocked", "dependency-closure-unknown"
    closure = record.get("dependency_closure")
    if not isinstance(closure, dict) or set(closure) != set(schema["reuse_receipt"]["dependency_closure"]["required"]):
        return "blocked", "dependency-closure-unknown"
    resolver_argv = closure.get("resolver_argv")
    if not isinstance(resolver_argv, list) or not resolver_argv or not all(isinstance(item, str) and item for item in resolver_argv):
        return "blocked", "dependency-closure-unknown"
    if closure.get("complete") is not True or closure.get("unknown_paths") != []:
        return "blocked", "dependency-closure-unknown"
    check_id = closure.get("check_id")
    resolver_argv = closure.get("resolver_argv")
    if not isinstance(check_id, str) or not TOKEN_RE.fullmatch(check_id) or resolver_argv != ["bash", ".ai/scripts/check-all.sh", "--resolve-input-closure", check_id]:
        return "blocked", "dependency-closure-unknown"
    subject = mapping(record.get("subject"), "receipt.subject")
    try:
        original_paths = authoritative_closure(check_id, str(subject.get("original_sha", "")))
        current_paths = authoritative_closure(check_id, str(subject.get("current_sha", "")))
    except LifecycleError:
        return "blocked", "dependency-closure-unknown"
    if original_paths != current_paths:
        return "re-executed", "dependency-closure-drift"
    seen: set[str] = set()
    for item_value in dependencies:
        item = mapping(item_value, "receipt.dependencies[]")
        if set(item) != {"path", "original_blob", "current_blob"}:
            return "blocked", "dependency-closure-unknown"
        path = item.get("path")
        if not isinstance(path, str) or not path or path in seen or path.startswith(("/", "\\")) or ".." in Path(path).parts:
            return "blocked", "dependency-closure-unknown"
        seen.add(path)
        if not SHA_RE.fullmatch(str(item.get("original_blob", ""))) or not SHA_RE.fullmatch(str(item.get("current_blob", ""))):
            return "blocked", "dependency-closure-unknown"
        try:
            if item["original_blob"] != git_object(str(subject["original_sha"]), path) or item["current_blob"] != git_object(str(subject["current_sha"]), path):
                return "blocked", "dependency-closure-unknown"
        except LifecycleError:
            return "blocked", "dependency-closure-unknown"
        if item["original_blob"] != item["current_blob"]:
            return "re-executed", "tracked-input-drift"
    ordered_paths = sorted(seen)
    if ordered_paths != original_paths:
        return "blocked", "dependency-closure-unknown"
    paths_digest = canonical_digest(ordered_paths)
    if closure.get("path_count") != len(ordered_paths):
        return "blocked", "dependency-closure-unknown"
    if closure.get("original_paths_sha256") != paths_digest or closure.get("current_paths_sha256") != paths_digest:
        return "blocked", "dependency-closure-unknown"
    closure_core = {
        "check_id": check_id,
        "resolver_argv": resolver_argv,
        "subject": subject,
        "dependencies": dependencies,
        "complete": True,
        "unknown_paths": [],
        "path_count": len(ordered_paths),
        "original_paths_sha256": paths_digest,
        "current_paths_sha256": paths_digest,
    }
    if closure.get("resolver_receipt_sha256") != canonical_digest(closure_core):
        return "blocked", "dependency-closure-unknown"
    authority = mapping(record.get("authority"), "receipt.authority")
    if set(authority) != set(schema["reuse_receipt"]["authority_dimensions"]):
        return "blocked", "authority-unknown"
    for name in schema["reuse_receipt"]["authority_dimensions"]:
        try:
            original, current = comparison_pair(authority[name], f"receipt.authority.{name}")
        except LifecycleError:
            return "blocked", "authority-unknown"
        if original != current:
            return "re-executed", f"{name}-drift"
    for name in ("command", "profile"):
        original, current = comparison_pair(record.get(f"{name}_fingerprint"), f"receipt.{name}_fingerprint")
        if original != current:
            return "re-executed", f"{name}-drift"
    environment = mapping(record.get("environment"), "receipt.environment")
    exact_keys(environment, {"original", "current"}, "receipt.environment")
    if environment["original"] != environment["current"]:
        return "re-executed", "environment-drift"
    if evidence_class not in schema["reuse_receipt"]["reusable_classes"]:
        return "blocked", "evidence-class-unknown"
    return "reused-with-proof", "complete-byte-equivalence"


def validate_reuse_receipt(record: dict[str, Any], schema: dict[str, Any]) -> None:
    required = {"schema_version", "record_type", "evidence_class", "subject", "invocation", "original_result", "dependencies", "dependency_closure", "terminal_metadata", "authority", "command_fingerprint", "profile_fingerprint", "environment", "fresh_gates", "decision", "receipt_sha256"}
    exact_keys(record, required, "receipt")
    if record["schema_version"] != "1.0" or record["record_type"] != "validation-reuse-receipt":
        raise LifecycleError("reuse receipt identity is invalid")
    subject = mapping(record["subject"], "receipt.subject")
    exact_keys(subject, {"original_sha", "current_sha"}, "receipt.subject")
    if not all(SHA_RE.fullmatch(str(subject.get(field, ""))) for field in subject):
        raise LifecycleError("reuse receipt subject SHAs are invalid")
    invocation = mapping(record["invocation"], "receipt.invocation")
    exact_keys(invocation, {"argv", "working_directory", "profile"}, "receipt.invocation")
    string_list(invocation["argv"], "receipt.invocation.argv")
    if not all(isinstance(invocation.get(field), str) and invocation[field] for field in ("working_directory", "profile")):
        raise LifecycleError("reuse receipt invocation identity is invalid")
    original = mapping(record["original_result"], "receipt.original_result")
    exact_keys(original, {"outcome", "duration_seconds", "evidence_refs", "evidence_sha256"}, "receipt.original_result")
    if original["outcome"] != "passed" or not isinstance(original["duration_seconds"], (int, float)) or isinstance(original["duration_seconds"], bool) or original["duration_seconds"] < 0:
        raise LifecycleError("reuse source must be a passing measured result")
    string_list(original["evidence_refs"], "receipt.original_result.evidence_refs")
    digest(original["evidence_sha256"], "receipt.original_result.evidence_sha256")
    terminal_metadata = mapping(record["terminal_metadata"], "receipt.terminal_metadata")
    exact_keys(terminal_metadata, {"original_sha256", "current_sha256", "excluded_from_dependency_fingerprint"}, "receipt.terminal_metadata")
    digest(terminal_metadata["original_sha256"], "receipt.terminal_metadata.original_sha256")
    digest(terminal_metadata["current_sha256"], "receipt.terminal_metadata.current_sha256")
    if terminal_metadata["excluded_from_dependency_fingerprint"] is not True:
        raise LifecycleError("terminal metadata must be excluded from dependency fingerprints")
    fresh = record["fresh_gates"]
    if not isinstance(fresh, list) or [item.get("gate") for item in fresh if isinstance(item, dict)] != schema["reuse_receipt"]["required_fresh_gates"] or not all(
        isinstance(item, dict) and item.get("required") is True and item.get("replaceable_by_reuse") is False for item in fresh
    ):
        raise LifecycleError("reuse receipt fresh gates are invalid")
    outcome, reason = expected_reuse_decision(record, schema)
    decision = mapping(record["decision"], "receipt.decision")
    if decision != {"outcome": outcome, "reason": reason}:
        raise LifecycleError(f"reuse decision must fail closed as {outcome}: {reason}")
    core = {key: record[key] for key in record if key != "receipt_sha256"}
    if digest(record["receipt_sha256"], "receipt.receipt_sha256") != canonical_digest(core):
        raise LifecycleError("reuse receipt digest is invalid")


def validate_freeze(record: dict[str, Any]) -> None:
    required = {"schema_version", "record_type", "state", "subject_sha", "clean_subject", "anticipated_tracked_mutations_complete", "terminal_declarations_before_freeze", "workflow_closeout_before_freeze", "tracked_mutations_after_freeze", "ignored_validation_artifacts_only", "identity_evidence_stale", "post_merge_source_repair_required", "record_sha256"}
    exact_keys(record, required, "freeze")
    if record["schema_version"] != "1.0" or record["record_type"] != "validation-freeze" or record["state"] not in {"active", "invalidated", "released"}:
        raise LifecycleError("freeze identity or state is invalid")
    if not SHA_RE.fullmatch(str(record["subject_sha"])):
        raise LifecycleError("freeze subject SHA is invalid")
    mutations = string_list(record["tracked_mutations_after_freeze"], "freeze.tracked_mutations_after_freeze", allow_empty=True)
    prerequisites = all(record[field] is True for field in ("clean_subject", "anticipated_tracked_mutations_complete", "terminal_declarations_before_freeze", "workflow_closeout_before_freeze"))
    if record["state"] == "active" and (not prerequisites or mutations or record["identity_evidence_stale"] is not False):
        raise LifecycleError("active freeze has incomplete sequencing or tracked drift")
    if record["state"] == "invalidated" and (not mutations or record["identity_evidence_stale"] is not True):
        raise LifecycleError("invalidated freeze must retain tracked drift and stale identity evidence")
    if record["ignored_validation_artifacts_only"] is not True or record["post_merge_source_repair_required"] is not False:
        raise LifecycleError("freeze mutation boundary is invalid")
    core = {key: record[key] for key in record if key != "record_sha256"}
    if digest(record["record_sha256"], "freeze.record_sha256") != canonical_digest(core):
        raise LifecycleError("freeze record digest is invalid")


def validate_audit(record: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "subject_sha", "gates"}, "audit")
    if record["schema_version"] != "1.0" or record["record_type"] != "exact-head-validation-audit" or not SHA_RE.fullmatch(str(record["subject_sha"])):
        raise LifecycleError("audit identity is invalid")
    gates = record["gates"]
    if not isinstance(gates, list) or not gates:
        raise LifecycleError("audit gates must be non-empty")
    seen: set[str] = set()
    for gate_value in gates:
        gate = mapping(gate_value, "audit.gates[]")
        exact_keys(gate, {"gate_id", "disposition", "evidence_refs", "reuse_receipt_sha256"}, "audit.gates[]")
        gate_id = gate["gate_id"]
        if not isinstance(gate_id, str) or not TOKEN_RE.fullmatch(gate_id) or gate_id in seen:
            raise LifecycleError("audit gate id is invalid or duplicated")
        seen.add(gate_id)
        if gate["disposition"] not in schema["audit_dispositions"]:
            raise LifecycleError("audit disposition is invalid")
        refs = string_list(gate["evidence_refs"], "audit.gates[].evidence_refs", allow_empty=True)
        receipt = gate["reuse_receipt_sha256"]
        if gate["disposition"] == "reused-with-proof":
            if not refs:
                raise LifecycleError("reused audit gate lacks evidence reference")
            digest(receipt, "audit.gates[].reuse_receipt_sha256")
        elif receipt is not None:
            raise LifecycleError("non-reused audit gate claims a reuse receipt")


def validate_required_contexts(record: dict[str, Any], provider_policy: dict[str, Any], schema: dict[str, Any]) -> None:
    exact_keys(record, {"schema_version", "record_type", "head_sha", "contexts"}, "required-contexts")
    if record["schema_version"] != "1.0" or record["record_type"] != "hosted-required-contexts" or not SHA_RE.fullmatch(str(record["head_sha"])):
        raise LifecycleError("required-context record identity is invalid")
    required = provider_policy["work_item_binding"]["merge_gate"]["required_check_contexts"]
    contexts = record["contexts"]
    if not isinstance(contexts, list) or [item.get("name") for item in contexts if isinstance(item, dict)] != required:
        raise LifecycleError("required hosted contexts are missing, reordered, or unexpected")
    terminal = set(schema["required_contexts"]["terminal_outcomes"])
    for item in contexts:
        exact_keys(mapping(item, "required-contexts.contexts[]"), {"name", "outcome", "executed", "reused", "reuse_provenance"}, "required-contexts.contexts[]")
        if item["outcome"] not in terminal or not isinstance(item["executed"], int) or not isinstance(item["reused"], int) or min(item["executed"], item["reused"]) < 0:
            raise LifecycleError("required hosted context terminal counts are invalid")
        if item["reused"] and not string_list(item["reuse_provenance"], "required-contexts.reuse_provenance"):
            raise LifecycleError("reused hosted context lacks provenance")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--reuse-receipt", type=Path)
    group.add_argument("--freeze-record", type=Path)
    group.add_argument("--audit-record", type=Path)
    group.add_argument("--required-contexts", type=Path)
    args = parser.parse_args()
    try:
        schema = mapping(yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8")), "schema")
        validate_schema(schema)
        if args.reuse_receipt:
            validate_reuse_receipt(load_record(args.reuse_receipt), schema)
        elif args.freeze_record:
            validate_freeze(load_record(args.freeze_record))
        elif args.audit_record:
            validate_audit(load_record(args.audit_record), schema)
        elif args.required_contexts:
            provider = mapping(yaml.safe_load(PROVIDER_POLICY.read_text(encoding="utf-8")), "provider policy")
            validate_required_contexts(load_record(args.required_contexts), provider, schema)
    except (LifecycleError, OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        print(f"Validation lifecycle failed closed: {exc}")
        return 1
    print("Validation lifecycle contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
