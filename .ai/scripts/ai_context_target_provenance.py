#!/usr/bin/env python3
"""Downstream AI context provenance and semantic customization contracts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Iterable

import yaml

from ai_context_effective_rules import (
    EFFECTIVE_STATE_PATH,
    PROVENANCE_EFFECTIVE_RULES_LINKAGE,
    build_effective_state_and_packets,
    is_profile_slug,
    validate_effective_rule_state,
    write_effective_state_and_packets,
)


VERSION_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CUSTOMIZATION_ID_RE = re.compile(r"^CUST-[A-Z0-9][A-Z0-9._-]*$")
ASSESSMENT_ID_RE = re.compile(r"^ASM-\d{8}-\d{3}$")
SUBJECT_KINDS = {"capability", "rule", "contract"}
RELATIONSHIPS = {"extends", "replaces", "deviates", "target-only"}
EQUIVALENCE = {"absent", "partial", "equivalent-candidate", "conflicting"}
DISPOSITIONS = {"retain", "merge", "supersede", "retire", "unresolved"}
PENDING_APPLY_RECEIPT = ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
EFFECTIVE_PACKET_DIRECTORY = ".dev/ai-context/effective-rule-packets"
COMMIT_SUBJECT_GRAMMAR_POLICY_ID = "git-commit-subject/v2"
COMMIT_SUBJECT_GRAMMAR_POLICY_PATH = ".dev/standards/GIT-COMMIT-POLICY.yaml"
REMEDIATION_PACKET_PATH = "remediation-packet.json"
REMEDIATION_REPORT_PATH = "remediation-report.md"
REMEDIATION_DECISION_PATH = "remediation-decision.json"
INCOMING_VALIDATION_RECEIPT_PATH = "incoming-validation-receipt.json"
TARGET_VALIDATION_RECEIPT_PATH = "target-validation-receipt.json"
TARGET_VALIDATION_OUTPUT_PATH = "target-validation-output.log"
TERMINAL_RECEIPT_PATH = "terminal-receipt.json"
REMEDIATION_PACKET_SCHEMA = "upgrade-remediation-packet/v1"
REMEDIATION_DECISION_SCHEMA = "upgrade-remediation-decision/v1"
TARGET_VALIDATION_RECEIPT_SCHEMA = "target-validation-receipt/v1"
TERMINAL_RECEIPT_SCHEMA = "upgrade-remediation-terminal-receipt/v1"
MULTI_HOP_ROUTE_DIRECTORY = "ai-context-multi-hop-upgrade"
MULTI_HOP_ROUTE_INTENT_SCHEMA = "ai-context-multi-hop-upgrade-intent/v1"
MULTI_HOP_ROUTE_JOURNAL_SCHEMA = "ai-context-multi-hop-upgrade-journal/v1"
MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA = "ai-context-multi-hop-upgrade-checkpoint/v1"
MULTI_HOP_RESOLVER_RESULT_PATH = "resolver-result.json"
MULTI_HOP_RESOLVER_RESULT_SCHEMA = "ai-context-multi-hop-upgrade-resolver-result/v1"
MULTI_HOP_ROUTE_CONTEXT_SCHEMA = "ai-context-multi-hop-checkpoint-context/v1"
MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA = "ai-context-multi-hop-initial-route-context/v1"
MULTI_HOP_PREPARED_HOP_SCHEMA = "multi-hop-prepared-hop/v1"
MULTI_HOP_VALIDATOR_EXECUTION_SCHEMA = "multi-hop-edge-validator-execution/v1"
MULTI_HOP_PACKAGE_KEYS = {
    "archive_path",
    "archive_sha256",
    "checksum_sha256",
    "migration_artifact_sha256",
    "validator_path",
    "validator_artifact_sha256",
    "extracted_root",
    "package_id",
    "package_version",
    "package_manifest_sha256",
    "migration_sha256",
    "files_manifest_sha256",
}
MULTI_HOP_VALIDATOR_EXECUTION_KEYS = {
    "record_path",
    "record_sha256",
    "stdout_path",
    "stdout_sha256",
}
MULTI_HOP_VALIDATOR_RECORD_KEYS = {
    "schema_version",
    "hop_index",
    "edge_id",
    "validator_argv",
    "validator_sha256",
    "expected_output_sha256",
    "stdout_sha256",
    "stderr_sha256",
    "return_code",
    "outcome",
}
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
SEALED_OPERATION_KEYS = {
    "id",
    "kind",
    "path",
    "from_path",
    "ownership",
    "component_id",
    "action",
    "reason",
}
RESERVED_APPLY_PATHS = {
    ".dev/AI-CONTEXT-SOURCE.yaml",
    PENDING_APPLY_RECEIPT,
    ".dev/ai-context/provenance.yaml",
    ".dev/ai-context/customizations.yaml",
}


class TargetValidationError(ValueError):
    """A fail-closed target provenance violation."""


def load_mapping(path: Path, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{path}: cannot parse YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: root must be a mapping")
        return None
    return value


def iso_with_offset(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def iso_interval_is_ordered(started_at: object, completed_at: object) -> bool:
    if not iso_with_offset(started_at) or not iso_with_offset(completed_at):
        return False
    assert isinstance(started_at, str)
    assert isinstance(completed_at, str)
    return datetime.fromisoformat(completed_at) >= datetime.fromisoformat(started_at)


def safe_repo_reference(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    raw_path = value.split("#", 1)[0]
    raw_segments = raw_path.split("/")
    path = PurePosixPath(raw_path)
    return (
        bool(raw_path)
        and ":" not in raw_path
        and all(raw_segments)
        and not path.is_absolute()
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def safe_target_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(
        part not in {"", ".", ".."} for part in path.parts
    )


def is_reparse_point(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except (FileNotFoundError, OSError):
        return False
    return bool(
        stat.S_ISLNK(metadata.st_mode)
        or getattr(metadata, "st_file_attributes", 0)
        & FILE_ATTRIBUTE_REPARSE_POINT
    )


def target_path_without_links(root: Path, relative: str) -> Path:
    if not safe_target_path(relative):
        raise TargetValidationError(f"unsafe target path: {relative!r}")
    candidate = root
    for part in PurePosixPath(relative).parts:
        candidate /= part
        if candidate.is_symlink() or is_reparse_point(candidate):
            raise TargetValidationError(
                f"target path crosses a symlink or reparse boundary: {relative}"
            )
    return candidate


def checked_target_path(
    root: Path, relative: str, label: str, errors: list[str]
) -> Path | None:
    try:
        return target_path_without_links(root, relative)
    except TargetValidationError as exc:
        errors.append(f"{label}: {exc}")
        return None


def current_target_head(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise TargetValidationError(f"cannot inspect target HEAD: {exc}") from exc
    head = result.stdout.strip()
    if result.returncode != 0 or not SHA_RE.fullmatch(head):
        detail = result.stderr.strip()
        raise TargetValidationError(
            f"cannot inspect target HEAD: {detail or result.returncode}"
        )
    return head


def selected_component_ids(selection: object) -> set[str] | None:
    if not isinstance(selection, dict):
        return None
    mandatory = selection.get("mandatory_components")
    profiles = selection.get("profiles")
    providers = selection.get("providers")
    if (
        not isinstance(mandatory, list)
        or not all(isinstance(item, str) and item for item in mandatory)
        or not isinstance(profiles, list)
        or not all(isinstance(item, str) and item for item in profiles)
        or not isinstance(providers, dict)
    ):
        return None
    selected = set(mandatory) | set(profiles)
    for provider_id, provider in providers.items():
        if (
            not isinstance(provider_id, str)
            or not provider_id
            or not isinstance(provider, dict)
            or type(provider.get("enabled")) is not bool
        ):
            return None
        if provider["enabled"]:
            selected.add(provider_id)
    return selected


def validate_sealed_operations(
    plan: dict, plan_path: Path, errors: list[str]
) -> list[dict] | None:
    operations = plan.get("operations")
    selected = selected_component_ids(plan.get("selection"))
    if not isinstance(operations, list) or selected is None:
        errors.append(f"{plan_path}: sealed transaction operation evidence is invalid")
        return None
    allowed_actions = {
        "add": {"add", "reconcile", "unresolved"},
        "replace": {"replace", "reconcile", "unresolved"},
        "remove": {"remove", "noop", "reconcile", "unresolved"},
        "rename": {"rename", "reconcile", "unresolved"},
        "reconcile": {"reconcile", "unresolved"},
    }
    ids: list[str] = []
    touched: set[str] = set()
    valid = True
    for item in operations:
        if not isinstance(item, dict) or set(item) != SEALED_OPERATION_KEYS:
            valid = False
            continue
        operation_id = item.get("id")
        kind = item.get("kind")
        path = item.get("path")
        source = item.get("from_path")
        ownership = item.get("ownership")
        component_id = item.get("component_id")
        action = item.get("action")
        if (
            not isinstance(operation_id, str)
            or not operation_id
            or kind not in allowed_actions
            or action not in allowed_actions.get(kind, set())
            or not safe_target_path(path)
            or not isinstance(item.get("reason"), str)
            or not item.get("reason")
            or ownership
            not in {"framework-managed", "target-template", "target-owned"}
            or (
                component_id is not None
                and (
                    not isinstance(component_id, str)
                    or not component_id
                    or component_id not in selected
                )
            )
        ):
            valid = False
            continue
        if kind == "rename":
            if not safe_target_path(source) or source == path:
                valid = False
                continue
        elif source is not None:
            valid = False
            continue
        if (
            (kind in {"replace", "remove", "rename"} and ownership != "framework-managed")
            or (ownership == "target-template" and kind not in {"add", "reconcile"})
            or (ownership == "target-owned" and kind != "reconcile")
        ):
            valid = False
            continue
        operation_paths = [path] + ([source] if source is not None else [])
        if any(
            candidate in RESERVED_APPLY_PATHS
            or candidate == EFFECTIVE_STATE_PATH
            or candidate == EFFECTIVE_PACKET_DIRECTORY
            or candidate.startswith(f"{EFFECTIVE_PACKET_DIRECTORY}/")
            or candidate in touched
            for candidate in operation_paths
        ):
            valid = False
            continue
        touched.update(operation_paths)
        ids.append(operation_id)
    if (
        not valid
        or len(ids) != len(operations)
        or len(ids) != len(set(ids))
        or ids != sorted(ids, key=lambda value: value.encode("utf-8"))
    ):
        errors.append(f"{plan_path}: sealed transaction operation evidence is invalid")
        return None
    return operations


def transaction_staging_records(
    transaction_id: str, operations: list[dict]
) -> list[dict[str, str]]:
    destinations = {PENDING_APPLY_RECEIPT}
    for item in operations:
        if item.get("action") in {"add", "replace", "remove", "rename"}:
            destinations.add(item["path"])
            if item.get("from_path"):
                destinations.add(item["from_path"])
    records: list[dict[str, str]] = []
    for destination in sorted(destinations, key=lambda value: value.encode("utf-8")):
        destination_path = PurePosixPath(destination)
        digest = hashlib.sha256(
            f"{transaction_id}\0{destination}".encode("utf-8")
        ).hexdigest()
        records.append(
            {
                "destination": destination,
                "path": (
                    destination_path.parent
                    / f".ai-context-apply-{digest}.staging"
                ).as_posix(),
            }
        )
    return records


def git_ignore_rule(root: Path, path: str) -> dict[str, object] | None:
    """Return the exact target Git ignore rule for one untracked path."""
    if not safe_target_path(path):
        raise TargetValidationError(f"unsafe target path for Git ignore check: {path!r}")
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-z", "-v", "--stdin"],
            cwd=root,
            check=False,
            capture_output=True,
            input=f"{path}\0".encode("utf-8"),
        )
    except OSError as exc:
        raise TargetValidationError(f"cannot inspect target Git ignore rules: {exc}") from exc
    if result.returncode == 1:
        return None
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise TargetValidationError(
            f"cannot inspect target Git ignore rules for {path}: {detail or result.returncode}"
        )
    values = result.stdout.split(b"\0")
    if values and values[-1] == b"":
        values.pop()
    if len(values) != 4:
        raise TargetValidationError(
            f"cannot parse target Git ignore rule for {path}"
        )
    source, line, pattern, matched_path = (
        value.decode("utf-8", errors="surrogateescape") for value in values
    )
    if matched_path != path or not line.isdecimal() or not source or not pattern:
        raise TargetValidationError(
            f"cannot parse target Git ignore rule for {path}"
        )
    return {"source": source, "line": int(line), "pattern": pattern}


def framework_managed_ignore_message(
    path: str, component_id: str, rule: dict[str, object]
) -> str:
    return (
        f"target Git ignore rule excludes framework-managed path {path} "
        f"(component {component_id}; ownership framework-managed): "
        f"{rule['source']}:{rule['line']}:{rule['pattern']}"
    )


def target_enforces_filemode(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "config", "--bool", "core.filemode"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise TargetValidationError(f"cannot inspect target Git core.filemode: {exc}") from exc
    value = result.stdout.strip()
    if result.returncode != 0 or value not in {"true", "false"}:
        raise TargetValidationError("cannot inspect target Git core.filemode")
    return value == "true"


def canonical_json_digest(value: object) -> str:
    content = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def git_eol_projection_matches(root: Path, path: str, content: bytes, expected_sha: str) -> bool:
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all", "--", path],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        index = subprocess.run(
            ["git", "show", f":{path}"], cwd=root, check=False, capture_output=True
        )
        attributes = subprocess.run(
            [
                "git",
                "check-attr",
                "filter",
                "ident",
                "working-tree-encoding",
                "--",
                path,
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    if status.returncode != 0 or status.stdout or index.returncode != 0 or attributes.returncode != 0:
        return False
    attribute_values = [
        line.rsplit(": ", 1)[1]
        for line in attributes.stdout.splitlines()
        if ": " in line
    ]
    return (
        len(attribute_values) == 3
        and all(value == "unspecified" for value in attribute_values)
        and hashlib.sha256(index.stdout).hexdigest() == expected_sha
        and content != index.stdout
        and content.replace(b"\r\n", b"\n") == index.stdout
    )


def apply_transaction_directory(root: Path) -> Path | None:
    try:
        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "--path-format=absolute",
                "--git-path",
                "ai-context-package-apply",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise TargetValidationError(f"cannot inspect package apply transactions: {exc}") from exc
    if result.returncode != 0 or not result.stdout.strip():
        return None
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else (root / value).resolve()


def multi_hop_route_directory(root: Path) -> Path | None:
    try:
        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "--path-format=absolute",
                "--git-path",
                MULTI_HOP_ROUTE_DIRECTORY,
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise TargetValidationError(
            f"cannot inspect multi-hop route transactions: {exc}"
        ) from exc
    if result.returncode != 0 or not result.stdout.strip():
        return None
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else (root / value).resolve()


def route_regular_bytes(path: Path, label: str, errors: list[str]) -> bytes | None:
    if path.is_symlink() or is_reparse_point(path) or not path.is_file():
        errors.append(f"{path}: {label} must be a regular file")
        return None
    try:
        return path.read_bytes()
    except OSError as exc:
        errors.append(f"{path}: cannot read {label}: {exc}")
        return None


def route_canonical_json(path: Path, label: str, errors: list[str]) -> tuple[dict, bytes] | None:
    raw = route_regular_bytes(path, label, errors)
    if raw is None:
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: {label} is not canonical JSON: {exc}")
        return None
    encoded = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    if not isinstance(value, dict) or raw != encoded:
        errors.append(f"{path}: {label} is not canonical JSON")
        return None
    return value, raw


def route_deterministic_yaml(path: Path, label: str, errors: list[str]) -> dict | None:
    raw = route_regular_bytes(path, label, errors)
    if raw is None:
        return None
    try:
        value = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{path}: {label} cannot be parsed: {exc}")
        return None
    encoded = yaml.safe_dump(value, sort_keys=True, allow_unicode=True).encode("utf-8")
    if not isinstance(value, dict) or raw != encoded:
        errors.append(f"{path}: {label} is not deterministic YAML")
        return None
    return value


def route_mapping(path: Path, label: str, errors: list[str]) -> dict | None:
    raw = route_regular_bytes(path, label, errors)
    if raw is None:
        return None
    try:
        value = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{path}: {label} cannot be parsed: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: {label} must be a mapping")
        return None
    return value


def route_sha(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def route_safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def route_edge_identity(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value)
        == {"edge_id", "order", "from_version", "to_version", "identity_sha256"}
        and isinstance(value.get("edge_id"), str)
        and bool(value["edge_id"])
        and type(value.get("order")) is int
        and value["order"] >= 1
        and isinstance(value.get("from_version"), str)
        and bool(VERSION_RE.fullmatch(value["from_version"]))
        and isinstance(value.get("to_version"), str)
        and bool(VERSION_RE.fullmatch(value["to_version"]))
        and route_sha(value.get("identity_sha256"))
    )


def route_full_edge_identity(value: object) -> dict | None:
    """Project one canonical full S1 edge into its sealed compact identity."""
    if not isinstance(value, dict):
        return None
    try:
        identity = {
            "edge_id": value["edge_id"],
            "order": value["order"],
            "from_version": value["from_version"],
            "to_version": value["to_version"],
            "identity_sha256": canonical_json_digest(value),
        }
    except (KeyError, TypeError, ValueError):
        return None
    return identity if route_edge_identity(identity) else None


def sealed_multi_hop_resolver_edges(
    route_root: Path, intent: object, errors: list[str]
) -> list[dict] | None:
    """Load the durable full S1 selection bound by one outer route intent.

    A route transaction retains raw matrix bytes for identity, but it does not
    copy the source matrix's surrounding asset tree.  Re-running the S1 asset
    resolver from that Git-admin directory would therefore turn a valid sealed
    transaction into a false failure.  Instead, begin-time S1 resolution is
    retained once as a canonical, path-free full-edge result.  This helper
    proves its raw bytes, identity, and compact-intent projection before any
    target-side promoted-hop evidence is accepted.
    """
    prefix = f"{route_root}: multi-hop sealed resolver result"
    if not isinstance(intent, dict):
        errors.append(f"{prefix} intent is invalid")
        return None
    matrix = intent.get("matrix")
    reference = intent.get("resolver_result")
    route = intent.get("route")
    if (
        not isinstance(matrix, dict)
        or set(matrix) != {"path", "sha256", "byte_length"}
        or matrix.get("path") != "route-matrix.yaml"
        or not route_sha(matrix.get("sha256"))
        or type(matrix.get("byte_length")) is not int
        or matrix["byte_length"] < 0
        or not isinstance(reference, dict)
        or set(reference) != {"path", "sha256", "byte_length"}
        or reference.get("path") != MULTI_HOP_RESOLVER_RESULT_PATH
        or not route_sha(reference.get("sha256"))
        or type(reference.get("byte_length")) is not int
        or reference["byte_length"] < 0
        or not isinstance(route, dict)
        or set(route) != {"route_id", "edges"}
        or not isinstance(route.get("route_id"), str)
        or not route["route_id"]
        or not isinstance(route.get("edges"), list)
        or not all(route_edge_identity(item) for item in route["edges"])
    ):
        errors.append(f"{prefix} identity is invalid")
        return None
    matrix_raw = route_regular_bytes(route_root / matrix["path"], "multi-hop route matrix", errors)
    if (
        matrix_raw is None
        or len(matrix_raw) != matrix["byte_length"]
        or sha256_bytes(matrix_raw) != matrix["sha256"]
    ):
        errors.append(f"{prefix} matrix bytes differ")
        return None
    loaded = route_canonical_json(
        route_root / reference["path"], "multi-hop sealed resolver result", errors
    )
    if loaded is None:
        return None
    result, result_raw = loaded
    if (
        len(result_raw) != reference["byte_length"]
        or sha256_bytes(result_raw) != reference["sha256"]
    ):
        errors.append(f"{prefix} bytes differ")
        return None
    selected = result.get("selected_route") if isinstance(result, dict) else None
    result_matrix = result.get("matrix") if isinstance(result, dict) else None
    if (
        not isinstance(result, dict)
        or set(result)
        != {"schema_version", "origin", "target", "matrix", "route_kind", "selected_route"}
        or result.get("schema_version") != MULTI_HOP_RESOLVER_RESULT_SCHEMA
        or result.get("origin") != intent.get("origin")
        or result.get("target") != intent.get("target")
        or result.get("route_kind") != "orchestrated-multi-hop"
        or not isinstance(result_matrix, dict)
        or set(result_matrix) != {"matrix_id", "sha256", "byte_length"}
        or not isinstance(result_matrix.get("matrix_id"), str)
        or not result_matrix["matrix_id"]
        or result_matrix.get("sha256") != matrix["sha256"]
        or result_matrix.get("byte_length") != matrix["byte_length"]
        or not isinstance(selected, dict)
        or set(selected) != {"route_id", "edge_count", "edges"}
        or selected.get("route_id") != route["route_id"]
        or type(selected.get("edge_count")) is not int
        or not isinstance(selected.get("edges"), list)
        or selected["edge_count"] != len(selected["edges"])
        or len(selected["edges"]) < 2
    ):
        errors.append(f"{prefix} fields differ from route intent")
        return None
    compact: list[dict] = []
    for index, full_edge in enumerate(selected["edges"]):
        identity = route_full_edge_identity(full_edge)
        if identity is None:
            errors.append(f"{prefix} full edge {index} identity is invalid")
            return None
        compact.append(identity)
    if compact != route["edges"] or [item["order"] for item in compact] != list(
        range(1, len(compact) + 1)
    ):
        errors.append(f"{prefix} full edges differ from compact route intent")
        return None
    return [dict(edge) for edge in selected["edges"]]


ROUTE_TARGET_STATE_KEYS = {
    "exists",
    "sha256",
    "mode",
    "git_sha256",
    "normalized_text_sha256",
    "tracked",
    "dirty",
    "git_eol_only",
}


def route_target_state(root: Path, relative: str, errors: list[str]) -> dict | None:
    """Reconstruct the exact package-apply checkpoint state record read-only."""
    candidate = checked_target_path(root, relative, "multi-hop checkpoint target path", errors)
    if candidate is None:
        return None
    if not candidate.exists():
        return {
            "exists": False,
            "sha256": None,
            "mode": None,
            "git_sha256": None,
            "normalized_text_sha256": None,
            "tracked": False,
            "dirty": False,
            "git_eol_only": False,
        }
    if candidate.is_symlink() or is_reparse_point(candidate) or not candidate.is_file():
        errors.append(f"{candidate}: multi-hop checkpoint target path must be a regular file")
        return None
    try:
        content = candidate.read_bytes()
        stage = subprocess.run(
            ["git", "ls-files", "--stage", "--", relative],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all", "--", relative],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        errors.append(f"{candidate}: cannot inspect multi-hop checkpoint target state: {exc}")
        return None
    if stage.returncode != 0 or status.returncode != 0:
        errors.append(f"{candidate}: cannot inspect multi-hop checkpoint Git state")
        return None
    modes = {line.split(" ", 1)[0] for line in stage.stdout.splitlines() if line}
    if len(modes) > 1 or any(mode not in {"100644", "100755"} for mode in modes):
        errors.append(f"{candidate}: multi-hop checkpoint target Git mode is invalid")
        return None
    tracked = bool(modes)
    dirty = bool(status.stdout)
    index_content: bytes | None = None
    if tracked:
        try:
            indexed = subprocess.run(
                ["git", "show", f":{relative}"],
                cwd=root,
                check=False,
                capture_output=True,
            )
        except OSError as exc:
            errors.append(f"{candidate}: cannot read multi-hop checkpoint index bytes: {exc}")
            return None
        if indexed.returncode != 0:
            errors.append(f"{candidate}: cannot read multi-hop checkpoint index bytes")
            return None
        index_content = indexed.stdout
    try:
        normalized = hashlib.sha256(
            content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        ).hexdigest()
    except UnicodeDecodeError:
        normalized = None
    git_eol_only = False
    if tracked and index_content is not None and content != index_content and content.replace(b"\r\n", b"\n") == index_content:
        try:
            attributes = subprocess.run(
                ["git", "check-attr", "filter", "ident", "working-tree-encoding", "--", relative],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            errors.append(f"{candidate}: cannot inspect multi-hop checkpoint attributes: {exc}")
            return None
        values = [line.rsplit(": ", 1)[1] for line in attributes.stdout.splitlines() if ": " in line]
        git_eol_only = (
            attributes.returncode == 0
            and len(values) == 3
            and all(value == "unspecified" for value in values)
        )
    return {
        "exists": True,
        "sha256": hashlib.sha256(content).hexdigest(),
        "mode": (
            "0755" if tracked and not dirty and next(iter(modes)) == "100755"
            else "0644" if tracked and not dirty
            else "0755" if candidate.stat().st_mode & stat.S_IXUSR else "0644"
        ),
        "git_sha256": hashlib.sha256(index_content).hexdigest() if index_content is not None else None,
        "normalized_text_sha256": normalized,
        "tracked": tracked,
        "dirty": dirty,
        "git_eol_only": git_eol_only,
    }


def route_target_surface(root: Path, errors: list[str]) -> dict[str, dict] | None:
    changed: set[str] = set()
    for arguments in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        try:
            result = subprocess.run(
                ["git", *arguments], cwd=root, check=False, capture_output=True
            )
        except OSError as exc:
            errors.append(f"cannot inspect multi-hop checkpoint surface: {exc}")
            return None
        if result.returncode != 0:
            errors.append("cannot inspect multi-hop checkpoint surface")
            return None
        changed.update(
            value.decode("utf-8", errors="surrogateescape")
            for value in result.stdout.split(b"\0")
            if value
        )
    result: dict[str, dict] = {}
    for relative in sorted(changed, key=lambda value: value.encode("utf-8")):
        # The receipt is proven by the checkpoint archive rather than the
        # target surface, and is intentionally absent once a hop is sealed.
        if relative == PENDING_APPLY_RECEIPT:
            continue
        if not route_safe_relative(relative):
            errors.append(f"unsafe multi-hop checkpoint surface path: {relative!r}")
            return None
        state = route_target_state(root, relative, errors)
        if state is None:
            return None
        result[relative] = state
    return result


def route_target_surface_valid(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    for relative, state in value.items():
        if not route_safe_relative(relative) or not isinstance(state, dict) or set(state) != ROUTE_TARGET_STATE_KEYS:
            return False
        if type(state.get("exists")) is not bool or type(state.get("tracked")) is not bool or type(state.get("dirty")) is not bool or type(state.get("git_eol_only")) is not bool:
            return False
        if state["exists"]:
            if state.get("mode") not in {"0644", "0755"} or not route_sha(state.get("sha256")):
                return False
            if state["tracked"] and not route_sha(state.get("git_sha256")):
                return False
            if not state["tracked"] and state.get("git_sha256") is not None:
                return False
            if state.get("normalized_text_sha256") is not None and not route_sha(state.get("normalized_text_sha256")):
                return False
        elif state != {
            "exists": False,
            "sha256": None,
            "mode": None,
            "git_sha256": None,
            "normalized_text_sha256": None,
            "tracked": False,
            "dirty": False,
            "git_eol_only": False,
        }:
            return False
    return True


def route_child_context_matches(
    value: object,
    *,
    route_transaction_id: str,
    route_intent_sha256: str,
    edges: list[dict],
    hop_index: int,
    predecessor_checkpoint_sha256: str | None,
    predecessor_of_predecessor_checkpoint_sha256: str | None,
) -> bool:
    if not 0 <= hop_index < len(edges):
        return False
    edge = edges[hop_index]
    if hop_index == 0:
        return value == {
            "schema_version": MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA,
            "route_transaction_id": route_transaction_id,
            "route_intent_sha256": route_intent_sha256,
            "next_hop_index": 0,
            "edge_id": edge["edge_id"],
            "edge_order": edge["order"],
            "from_version": edge["from_version"],
            "to_version": edge["to_version"],
        }
    return value == {
        "schema_version": MULTI_HOP_ROUTE_CONTEXT_SCHEMA,
        "route_transaction_id": route_transaction_id,
        "route_intent_sha256": route_intent_sha256,
        "checkpoint_index": hop_index - 1,
        "checkpoint_sha256": predecessor_checkpoint_sha256,
        "checkpoint_predecessor_sha256": predecessor_of_predecessor_checkpoint_sha256,
        "next_hop_index": hop_index,
        "edge_id": edge["edge_id"],
        "edge_order": edge["order"],
        "from_version": edge["from_version"],
        "to_version": edge["to_version"],
    }


def route_relative_path(
    route_root: Path, relative: object, label: str, errors: list[str]
) -> Path | None:
    """Resolve one retained route-admin path without crossing link boundaries."""
    if not route_safe_relative(relative):
        errors.append(f"{route_root}: {label} path is unsafe")
        return None
    assert isinstance(relative, str)
    candidate = route_root
    for part in PurePosixPath(relative).parts:
        candidate /= part
        if candidate.is_symlink() or is_reparse_point(candidate):
            errors.append(f"{candidate}: {label} crosses a symlink or reparse boundary")
            return None
    return candidate


def route_checksum_binds_archive(
    checksum_raw: bytes, archive_raw: bytes, archive_name: str
) -> bool:
    """Accept only the two standard sha256sum separators retained by S1."""
    try:
        match = re.fullmatch(
            r"(?P<sha256>[0-9a-f]{64}) (?P<marker>[ *])(?P<filename>[^/\\\r\n]+)\n",
            checksum_raw.decode("utf-8"),
        )
    except UnicodeDecodeError:
        return False
    return (
        match is not None
        and match.group("sha256") == sha256_bytes(archive_raw)
        and match.group("filename") == archive_name
    )


def validate_promoted_multi_hop_evidence(
    route_root: Path,
    hop_index: int,
    edge: dict,
    full_edge: object,
    expected_package: object,
    expected_execution: object | None,
    expected_plan_sha256: object,
    errors: list[str],
) -> tuple[dict, dict, Path] | None:
    """Validate the one promoted hop tree used by active and sealed route state.

    The outer journal and checkpoint reference this tree; they must never be
    able to replace its archive, extraction, validator execution, or semantic
    plan identity with merely self-consistent mappings.
    """
    error_start = len(errors)
    prefix = f"{route_root}: multi-hop promoted hop {hop_index}"
    full_identity = route_full_edge_identity(full_edge)
    if (
        type(hop_index) is not int
        or hop_index < 0
        or not route_edge_identity(edge)
        or full_identity != edge
        or not isinstance(full_edge, dict)
    ):
        errors.append(f"{prefix} identity is invalid")
        return None
    full_artifacts = full_edge.get("artifacts")
    full_validation = full_edge.get("validation")
    if (
        not isinstance(full_artifacts, dict)
        or not isinstance(full_validation, dict)
        or not isinstance(full_artifacts.get("archive"), dict)
        or not isinstance(full_artifacts.get("checksum"), dict)
        or not isinstance(full_artifacts.get("manifest"), dict)
        or not isinstance(full_artifacts.get("validator"), dict)
        or not isinstance(full_validation.get("validator_argv"), list)
        or not full_validation["validator_argv"]
        or not all(
            isinstance(item, str) and item for item in full_validation["validator_argv"]
        )
        or not isinstance(full_validation.get("output"), dict)
        or not route_sha(full_artifacts["archive"].get("sha256"))
        or not route_sha(full_artifacts["checksum"].get("sha256"))
        or not route_sha(full_artifacts["manifest"].get("sha256"))
        or not route_sha(full_artifacts["validator"].get("sha256"))
        or not route_sha(full_validation["output"].get("sha256"))
    ):
        errors.append(f"{prefix} sealed full edge contract is invalid")
        return None
    hop_name = f"{hop_index:04d}"
    hop_root = route_root / "hops" / hop_name
    if hop_root.is_symlink() or is_reparse_point(hop_root) or not hop_root.is_dir():
        errors.append(f"{prefix} evidence root is missing or unsafe")
        return None
    evidence_loaded = route_canonical_json(
        hop_root / "evidence.json", "multi-hop prepared-hop evidence", errors
    )
    if evidence_loaded is None:
        return None
    evidence, _evidence_raw = evidence_loaded
    if (
        set(evidence)
        != {
            "schema_version",
            "hop_index",
            "edge",
            "package",
            "validator_execution",
            "plan_sha256",
        }
        or evidence.get("schema_version") != MULTI_HOP_PREPARED_HOP_SCHEMA
        or evidence.get("hop_index") != hop_index
        or evidence.get("edge") != edge
        or not route_sha(evidence.get("plan_sha256"))
        or evidence.get("plan_sha256") != expected_plan_sha256
        or not isinstance(evidence.get("package"), dict)
        or not isinstance(evidence.get("validator_execution"), dict)
    ):
        errors.append(f"{prefix} prepared evidence identity differs")
        return None
    package = evidence["package"]
    execution = evidence["validator_execution"]
    if package != expected_package:
        errors.append(f"{prefix} prepared package differs from route state")
    if expected_execution is not None and execution != expected_execution:
        errors.append(f"{prefix} prepared validator execution differs from route state")
    if (
        set(package) != MULTI_HOP_PACKAGE_KEYS
        or not all(
            route_sha(package.get(key))
            for key in {
                "archive_sha256",
                "checksum_sha256",
                "migration_artifact_sha256",
                "validator_artifact_sha256",
                "package_manifest_sha256",
                "migration_sha256",
                "files_manifest_sha256",
            }
        )
        or not isinstance(package.get("package_id"), str)
        or not package.get("package_id")
        or not isinstance(package.get("package_version"), str)
        or not package.get("package_version")
    ):
        errors.append(f"{prefix} package identity is invalid")
        return None
    archive_relative = package["archive_path"]
    archive_parts = (
        tuple(PurePosixPath(archive_relative).parts)
        if route_safe_relative(archive_relative)
        else ()
    )
    extracted_relative = package["extracted_root"]
    extracted_parts = (
        tuple(PurePosixPath(extracted_relative).parts)
        if route_safe_relative(extracted_relative)
        else ()
    )
    if (
        len(archive_parts) != 3
        or archive_parts[:2] != ("hops", hop_name)
        or not archive_parts[2]
        or len(extracted_parts) != 4
        or extracted_parts[:3] != ("hops", hop_name, "extracted")
        or not extracted_parts[3]
    ):
        errors.append(f"{prefix} package paths are invalid")
        return None
    validator_relative = package["validator_path"]
    validator_parts = (
        tuple(PurePosixPath(validator_relative).parts)
        if route_safe_relative(validator_relative)
        else ()
    )
    if validator_parts != ("hops", hop_name, "validator.asset"):
        errors.append(f"{prefix} validator asset path is invalid")
        return None
    archive_path = route_relative_path(route_root, archive_relative, "multi-hop archive", errors)
    extracted_root = route_relative_path(
        route_root, extracted_relative, "multi-hop extracted package", errors
    )
    checksum_path = route_relative_path(
        route_root, f"hops/{hop_name}/checksum.sha256", "multi-hop checksum", errors
    )
    migration_artifact_path = route_relative_path(
        route_root, f"hops/{hop_name}/migration.yaml", "multi-hop migration artifact", errors
    )
    validator_asset_path = route_relative_path(
        route_root, validator_relative, "multi-hop retained validator asset", errors
    )
    if extracted_root is None or extracted_root.is_symlink() or is_reparse_point(extracted_root) or not extracted_root.is_dir():
        errors.append(f"{prefix} extracted package root is missing or unsafe")
    archive_raw = (
        route_regular_bytes(archive_path, "multi-hop package archive", errors)
        if archive_path is not None
        else None
    )
    checksum_raw = (
        route_regular_bytes(checksum_path, "multi-hop package checksum", errors)
        if checksum_path is not None
        else None
    )
    migration_artifact_raw = (
        route_regular_bytes(
            migration_artifact_path, "multi-hop migration artifact", errors
        )
        if migration_artifact_path is not None
        else None
    )
    validator_asset_raw = (
        route_regular_bytes(
            validator_asset_path, "multi-hop retained validator asset", errors
        )
        if validator_asset_path is not None
        else None
    )
    if archive_raw is not None and sha256_bytes(archive_raw) != package["archive_sha256"]:
        errors.append(f"{prefix} archive digest differs")
    if checksum_raw is not None and sha256_bytes(checksum_raw) != package["checksum_sha256"]:
        errors.append(f"{prefix} checksum digest differs")
    if (
        checksum_raw is not None
        and archive_raw is not None
        and not route_checksum_binds_archive(checksum_raw, archive_raw, archive_parts[2])
    ):
        errors.append(f"{prefix} checksum does not bind the retained archive")
    if (
        migration_artifact_raw is not None
        and sha256_bytes(migration_artifact_raw) != package["migration_artifact_sha256"]
    ):
        errors.append(f"{prefix} migration artifact digest differs")
    if (
        validator_asset_raw is not None
        and sha256_bytes(validator_asset_raw) != package["validator_artifact_sha256"]
    ):
        errors.append(f"{prefix} retained validator asset digest differs")
    if (
        package.get("archive_sha256") != full_artifacts["archive"].get("sha256")
        or package.get("checksum_sha256") != full_artifacts["checksum"].get("sha256")
        or package.get("migration_artifact_sha256")
        != full_artifacts["manifest"].get("sha256")
        or package.get("validator_artifact_sha256")
        != full_artifacts["validator"].get("sha256")
    ):
        errors.append(f"{prefix} package differs from sealed full edge artifacts")

    package_document: dict | None = None
    package_manifest_sha: str | None = None
    if extracted_root is not None and extracted_root.is_dir() and not extracted_root.is_symlink() and not is_reparse_point(extracted_root):
        try:
            import ai_context_package_apply as package_apply

            package_document, _incoming, _migration, package_manifest_sha = (
                package_apply.validate_package_root(extracted_root)
            )
        except (ImportError, OSError, ValueError) as exc:
            errors.append(f"{prefix} extracted package is invalid: {exc}")
    migration_path = route_relative_path(
        route_root,
        f"{extracted_relative}/metadata/migration.yaml",
        "multi-hop extracted migration",
        errors,
    )
    files_path = route_relative_path(
        route_root,
        f"{extracted_relative}/metadata/files.yaml",
        "multi-hop extracted files manifest",
        errors,
    )
    migration_raw = (
        route_regular_bytes(migration_path, "multi-hop extracted migration", errors)
        if migration_path is not None
        else None
    )
    files_raw = (
        route_regular_bytes(files_path, "multi-hop extracted files manifest", errors)
        if files_path is not None
        else None
    )
    if (
        package_document is None
        or package_manifest_sha is None
        or package.get("package_id") != package_document.get("package_id")
        or package.get("package_version") != package_document.get("version")
        or package.get("package_manifest_sha256") != package_manifest_sha
        or migration_raw is None
        or package.get("migration_sha256") != sha256_bytes(migration_raw)
        or migration_artifact_raw is None
        or migration_raw != migration_artifact_raw
        or files_raw is None
        or package.get("files_manifest_sha256") != sha256_bytes(files_raw)
    ):
        errors.append(f"{prefix} extracted package identity differs")

    if set(execution) != MULTI_HOP_VALIDATOR_EXECUTION_KEYS or not all(
        route_sha(execution.get(key)) for key in {"record_sha256", "stdout_sha256"}
    ):
        errors.append(f"{prefix} validator execution identity is invalid")
        return None
    record_relative = execution["record_path"]
    stdout_relative = execution["stdout_path"]
    if (
        tuple(PurePosixPath(record_relative).parts)
        if route_safe_relative(record_relative)
        else ()
    ) != ("hops", hop_name, "validator-execution.json") or (
        tuple(PurePosixPath(stdout_relative).parts)
        if route_safe_relative(stdout_relative)
        else ()
    ) != ("hops", hop_name, "validator.stdout.log"):
        errors.append(f"{prefix} validator execution paths are invalid")
        return None
    record_path = route_relative_path(route_root, record_relative, "multi-hop validator record", errors)
    stdout_path = route_relative_path(route_root, stdout_relative, "multi-hop validator stdout", errors)
    stderr_path = route_relative_path(
        route_root, f"hops/{hop_name}/validator.stderr.log", "multi-hop validator stderr", errors
    )
    record_loaded = (
        route_canonical_json(record_path, "multi-hop validator record", errors)
        if record_path is not None
        else None
    )
    stdout = (
        route_regular_bytes(stdout_path, "multi-hop validator stdout", errors)
        if stdout_path is not None
        else None
    )
    stderr = (
        route_regular_bytes(stderr_path, "multi-hop validator stderr", errors)
        if stderr_path is not None
        else None
    )
    if record_loaded is not None:
        record, record_raw = record_loaded
        if (
            set(record) != MULTI_HOP_VALIDATOR_RECORD_KEYS
            or record.get("schema_version") != MULTI_HOP_VALIDATOR_EXECUTION_SCHEMA
            or record.get("hop_index") != hop_index
            or record.get("edge_id") != edge.get("edge_id")
            or not isinstance(record.get("validator_argv"), list)
            or not record.get("validator_argv")
            or not all(isinstance(item, str) and item for item in record["validator_argv"])
            or not route_sha(record.get("validator_sha256"))
            or record.get("validator_sha256") != package.get("validator_artifact_sha256")
            or record.get("validator_sha256")
            != full_artifacts["validator"].get("sha256")
            or not route_sha(record.get("expected_output_sha256"))
            or record.get("expected_output_sha256")
            != full_validation["output"].get("sha256")
            or not route_sha(record.get("stdout_sha256"))
            or not route_sha(record.get("stderr_sha256"))
            or type(record.get("return_code")) is not int
            or record.get("return_code") != 0
            or record.get("outcome") != "passed"
            or record.get("validator_argv") != full_validation["validator_argv"]
            or sha256_bytes(record_raw) != execution.get("record_sha256")
            or stdout is None
            or sha256_bytes(stdout) != execution.get("stdout_sha256")
            or record.get("stdout_sha256") != execution.get("stdout_sha256")
            or record.get("expected_output_sha256") != execution.get("stdout_sha256")
            or stderr is None
            or stderr != b""
            or record.get("stderr_sha256") != sha256_bytes(stderr)
        ):
            errors.append(f"{prefix} validator execution evidence differs")
    if len(errors) != error_start:
        return None
    assert isinstance(extracted_root, Path)
    return package, execution, extracted_root


def validate_transient_bound_multi_hop_proposal(
    route_root: Path,
    child_directory: Path,
    journal: dict,
    active: dict,
    active_plan: dict,
    edges: list[dict],
    intent_raw: bytes,
    checkpoint_shas: list[str],
    checkpoint_predecessors: list[str | None],
    promoted: tuple[dict, dict, Path] | None,
    errors: list[str],
) -> None:
    """Read-only acceptance of the one post-bind/pre-unlink crash residue."""
    transaction = active.get("child_transaction_id")
    index = active.get("hop_index")
    if not isinstance(transaction, str) or type(index) is not int:
        return
    proposal_path = route_root / "hops" / f"{index:04d}" / "preparation.json"
    if proposal_path.is_symlink() or is_reparse_point(proposal_path):
        errors.append(f"{route_root}: bound multi-hop proposal path is unsafe")
        return
    if not proposal_path.exists():
        return
    if journal.get("state") not in {"awaiting-target-validation", "finalizing"}:
        errors.append(f"{route_root}: bound multi-hop proposal is stale outside its crash state")
        return
    proposal_loaded = route_canonical_json(
        proposal_path, "bound multi-hop proposal plan", errors
    )
    if proposal_loaded is None:
        return
    proposal, proposal_raw = proposal_loaded
    expected_child_state = (
        "awaiting-target-validation"
        if journal["state"] == "awaiting-target-validation"
        else "validated"
    )
    child_journal = route_mapping(
        child_directory / transaction / "journal.yaml",
        "bound child package apply journal",
        errors,
    )
    if (
        sha256_bytes(proposal_raw) != active.get("proposal_plan_sha256")
        or proposal.get("schema_version") != "2.2.0"
        or proposal.get("plan_sha256") != transaction
        or canonical_json_digest(
            {key: value for key, value in proposal.items() if key != "plan_sha256"}
        )
        != transaction
        or proposal != active_plan
        or not route_child_context_matches(
            proposal.get("multi_hop_checkpoint_context"),
            route_transaction_id=route_root.name,
            route_intent_sha256=sha256_bytes(intent_raw),
            edges=edges,
            hop_index=index,
            predecessor_checkpoint_sha256=(
                checkpoint_shas[index - 1] if index and len(checkpoint_shas) >= index else None
            ),
            predecessor_of_predecessor_checkpoint_sha256=(
                checkpoint_predecessors[index - 1]
                if index and len(checkpoint_predecessors) >= index
                else None
            ),
        )
        or (
            promoted is not None
            and proposal.get("package_root") != str(promoted[2])
        )
        or (
            promoted is not None
            and proposal.get("package_manifest_sha256")
            != promoted[0]["package_manifest_sha256"]
        )
        or (
            promoted is not None
            and proposal.get("migration_sha256") != promoted[0]["migration_sha256"]
        )
        or child_journal is None
        or child_journal.get("state") != expected_child_state
    ):
        errors.append(f"{route_root}: bound multi-hop proposal differs from child evidence")


def validate_multi_hop_route_transactions(
    root: Path,
    errors: list[str],
    *,
    git_snapshot: dict[str, object] | None = None,
) -> None:
    """Validate retained S2 checkpoints without treating them as target authority.

    The only copied byte is the pending receipt archived before its global
    clearance.  All package/remediation/validation/terminal records remain
    referenced at the existing child package-apply transaction path.
    """
    snapshot_surface: dict[str, dict] | None = None
    if git_snapshot is None:
        try:
            route_directory = multi_hop_route_directory(root)
            child_directory = apply_transaction_directory(root)
        except TargetValidationError as exc:
            errors.append(str(exc))
            return
        target_head: str | None = None
    else:
        if set(git_snapshot) != {
            "head",
            "apply_transaction_directory",
            "multi_hop_route_directory",
            "target_surface",
        }:
            errors.append("multi-hop route Git snapshot fields are invalid")
            return
        route_directory = git_snapshot.get("multi_hop_route_directory")
        child_directory = git_snapshot.get("apply_transaction_directory")
        target_head = git_snapshot.get("head")
        surface_value = git_snapshot.get("target_surface")
        if (
            not isinstance(route_directory, Path)
            or not route_directory.is_absolute()
            or not isinstance(child_directory, Path)
            or not child_directory.is_absolute()
            or not isinstance(target_head, str)
            or not SHA_RE.fullmatch(target_head)
            or not route_target_surface_valid(surface_value)
        ):
            errors.append("multi-hop route Git snapshot identity is invalid")
            return
        snapshot_surface = {
            relative: dict(state)
            for relative, state in surface_value.items()
        }
    if route_directory is None or not route_directory.exists():
        return
    if target_head is None:
        try:
            target_head = current_target_head(root)
        except TargetValidationError as exc:
            errors.append(str(exc))
            return
    if route_directory.is_symlink() or is_reparse_point(route_directory) or not route_directory.is_dir():
        errors.append(f"{route_directory}: multi-hop route directory is unsafe")
        return
    if child_directory is not None and (
        child_directory.is_symlink()
        or is_reparse_point(child_directory)
        or (child_directory.exists() and not child_directory.is_dir())
    ):
        errors.append("multi-hop route package-apply transaction directory is unsafe")
        return
    for route_root in sorted(route_directory.iterdir(), key=lambda item: item.name):
        if route_root.name == "transaction.lock" and route_root.is_file():
            continue
        # A process can crash after creating the private atomic-promotion
        # directory but before it has a route intent.  It is not executable
        # route state.  Safely recognize only the exact tempfile namespace so
        # it cannot permanently block validation of an admitted route.
        if re.fullmatch(r"\.[0-9a-f]{64}\.preparing-[A-Za-z0-9_-]+", route_root.name):
            if (
                route_root.is_symlink()
                or is_reparse_point(route_root)
                or not route_root.is_dir()
            ):
                errors.append(f"{route_root}: multi-hop preparation residue is unsafe")
            continue
        if (
            route_root.is_symlink()
            or is_reparse_point(route_root)
            or not route_root.is_dir()
            or not re.fullmatch(r"[0-9a-f]{64}", route_root.name)
        ):
            errors.append(f"{route_root}: multi-hop route transaction directory is invalid")
            continue
        intent_loaded = route_canonical_json(
            route_root / "route-intent.json", "multi-hop route intent", errors
        )
        journal = route_deterministic_yaml(
            route_root / "journal.yaml", "multi-hop route journal", errors
        )
        if intent_loaded is None or journal is None:
            continue
        intent, intent_raw = intent_loaded
        intent_required = {
            "schema_version", "route_transaction_id", "target_root", "target_starting_commit",
            "origin", "target", "matrix", "resolver_result", "route",
        }
        if set(intent) != intent_required or intent.get("schema_version") != MULTI_HOP_ROUTE_INTENT_SCHEMA:
            errors.append(f"{route_root}: multi-hop route intent fields are invalid")
            continue
        seed = dict(intent)
        transaction_id = seed.pop("route_transaction_id", None)
        if transaction_id != route_root.name or canonical_json_digest(seed) != route_root.name:
            errors.append(f"{route_root}: multi-hop route transaction identity differs")
            continue
        if (
            intent.get("target_root") != str(root.resolve())
            or intent.get("target_starting_commit") != target_head
        ):
            errors.append(f"{route_root}: multi-hop route target identity differs")
        matrix = intent.get("matrix")
        if (
            not isinstance(matrix, dict)
            or set(matrix) != {"path", "sha256", "byte_length"}
            or matrix.get("path") != "route-matrix.yaml"
            or not route_sha(matrix.get("sha256"))
            or type(matrix.get("byte_length")) is not int
            or matrix["byte_length"] < 0
        ):
            errors.append(f"{route_root}: multi-hop route matrix identity is invalid")
            continue
        matrix_raw = route_regular_bytes(route_root / "route-matrix.yaml", "multi-hop route matrix", errors)
        if matrix_raw is None or len(matrix_raw) != matrix["byte_length"] or sha256_bytes(matrix_raw) != matrix["sha256"]:
            errors.append(f"{route_root}: multi-hop route matrix bytes differ")
            continue
        route = intent.get("route")
        edges = route.get("edges") if isinstance(route, dict) else None
        if (
            not isinstance(route, dict)
            or set(route) != {"route_id", "edges"}
            or not isinstance(route.get("route_id"), str)
            or not route["route_id"]
            or not isinstance(edges, list)
            or len(edges) < 2
            or not all(route_edge_identity(edge) for edge in edges)
            or [edge["order"] for edge in edges] != list(range(1, len(edges) + 1))
        ):
            errors.append(f"{route_root}: multi-hop ordered edge identities are invalid")
            continue
        full_edges = sealed_multi_hop_resolver_edges(route_root, intent, errors)
        if full_edges is None:
            continue
        journal_required = {
            "schema_version", "route_transaction_id", "route_intent_sha256", "target_root",
            "target_starting_commit", "state", "next_hop_index", "last_checkpoint_index",
            "last_checkpoint_sha256", "active_hop",
        }
        if (
            set(journal) != journal_required
            or journal.get("schema_version") != MULTI_HOP_ROUTE_JOURNAL_SCHEMA
            or journal.get("route_transaction_id") != route_root.name
            or journal.get("route_intent_sha256") != sha256_bytes(intent_raw)
            or journal.get("target_root") != intent.get("target_root")
            or journal.get("target_starting_commit") != intent.get("target_starting_commit")
            or journal.get("state") not in {
                "planned", "awaiting-owner-decision", "applying", "awaiting-target-validation",
                "validating", "finalizing", "checkpointing", "checkpointed", "rolling-back",
                "completed", "rolled-back",
            }
            or type(journal.get("next_hop_index")) is not int
            or not 0 <= journal["next_hop_index"] <= len(edges)
        ):
            errors.append(f"{route_root}: multi-hop route journal identity is invalid")
            continue
        last_index = journal.get("last_checkpoint_index")
        last_sha = journal.get("last_checkpoint_sha256")
        if (last_index is None) != (last_sha is None) or (
            last_index is not None
            and (type(last_index) is not int or not 0 <= last_index < len(edges) or not route_sha(last_sha))
        ):
            errors.append(f"{route_root}: multi-hop route journal checkpoint binding is invalid")
            continue
        expected_count = 0 if last_index is None else last_index + 1
        if journal["state"] in {"checkpointed", "completed"} and (
            journal.get("active_hop") is not None or journal["next_hop_index"] != expected_count
        ):
            errors.append(f"{route_root}: checkpointed multi-hop route journal progress is invalid")
        if journal["state"] == "completed" and journal["next_hop_index"] != len(edges):
            errors.append(f"{route_root}: completed multi-hop route does not cover every edge")
        previous_sha: str | None = None
        checkpoint_shas: list[str] = []
        checkpoint_predecessors: list[str | None] = []
        last_checkpoint: dict | None = None
        child_ids: set[str] = set()
        for index in range(expected_count):
            checkpoint_loaded = route_canonical_json(
                route_root / "checkpoints" / f"{index:04d}.json",
                "multi-hop route checkpoint",
                errors,
            )
            if checkpoint_loaded is None:
                continue
            checkpoint, checkpoint_raw = checkpoint_loaded
            checkpoint_sha = sha256_bytes(checkpoint_raw)
            unsigned = dict(checkpoint)
            declared = unsigned.pop("digest", None)
            required_checkpoint = {
                "schema_version", "route_transaction_id", "route_intent_sha256", "checkpoint_index",
                "predecessor_checkpoint_sha256", "edge", "package", "child_transaction",
                "pending_receipt", "authority", "target_surface", "digest",
            }
            if (
                set(checkpoint) != required_checkpoint
                or checkpoint.get("schema_version") != MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA
                or checkpoint.get("route_transaction_id") != route_root.name
                or checkpoint.get("route_intent_sha256") != sha256_bytes(intent_raw)
                or checkpoint.get("checkpoint_index") != index
                or checkpoint.get("predecessor_checkpoint_sha256") != previous_sha
                or checkpoint.get("edge") != edges[index]
                or declared != canonical_json_digest(unsigned)
            ):
                errors.append(f"{route_root}: multi-hop checkpoint {index} identity differs")
                continue
            previous_sha = checkpoint_sha
            checkpoint_shas.append(checkpoint_sha)
            checkpoint_predecessors.append(checkpoint.get("predecessor_checkpoint_sha256"))
            last_checkpoint = checkpoint
            child = checkpoint.get("child_transaction")
            package = checkpoint.get("package")
            pending = checkpoint.get("pending_receipt")
            authority = checkpoint.get("authority")
            target_surface = checkpoint.get("target_surface")
            child_required = {
                "transaction_id", "plan_sha256", "evidence_path", "package_manifest_sha256",
                "migration_sha256", "remediation_packet_sha256", "remediation_decision_sha256",
                "incoming_validation_receipt_sha256", "target_validation_receipt_sha256",
                "terminal_receipt_sha256",
            }
            if (
                not isinstance(child, dict)
                or set(child) != child_required
                or not all(route_sha(child.get(key)) for key in child_required if key != "evidence_path")
                or child.get("plan_sha256") != child.get("transaction_id")
                or child.get("evidence_path") != f"ai-context-package-apply/{child.get('transaction_id')}"
                or child.get("transaction_id") in child_ids
            ):
                errors.append(f"{route_root}: multi-hop checkpoint {index} child evidence is invalid")
                continue
            child_ids.add(child["transaction_id"])
            if (
                not isinstance(pending, dict)
                or set(pending) != {"path", "sha256", "archive_path"}
                or pending.get("path") != PENDING_APPLY_RECEIPT
                or not route_sha(pending.get("sha256"))
                or not route_safe_relative(pending.get("archive_path"))
                or not isinstance(authority, dict)
                or set(authority) != {"provenance_sha256", "customizations_sha256"}
                or not all(route_sha(authority.get(key)) for key in authority)
                or not isinstance(target_surface, dict)
                or set(target_surface) != {"starting_commit", "paths"}
                or target_surface.get("starting_commit") != intent.get("target_starting_commit")
                or not route_target_surface_valid(target_surface.get("paths"))
            ):
                errors.append(f"{route_root}: multi-hop checkpoint {index} receipt or target evidence is invalid")
                continue
            promoted = validate_promoted_multi_hop_evidence(
                route_root,
                index,
                edges[index],
                full_edges[index],
                package,
                None,
                child["plan_sha256"],
                errors,
            )
            archive = route_root / Path(*PurePosixPath(pending["archive_path"]).parts)
            archived = route_regular_bytes(archive, "checkpointed pending receipt archive", errors)
            if archived is None or sha256_bytes(archived) != pending["sha256"]:
                errors.append(f"{route_root}: multi-hop checkpoint {index} archived pending receipt differs")
            if child_directory is None or not child_directory.is_dir():
                errors.append(f"{route_root}: multi-hop checkpoint {index} has no child transaction directory")
                continue
            child_root = child_directory / child["transaction_id"]
            child_journal = route_mapping(child_root / "journal.yaml", "child package apply journal", errors)
            child_plan_loaded = route_canonical_json(child_root / "plan.json", "child package apply plan", errors)
            terminal_loaded = route_canonical_json(child_root / TERMINAL_RECEIPT_PATH, "child terminal receipt", errors)
            if child_journal is None or child_plan_loaded is None or terminal_loaded is None:
                continue
            child_plan, child_plan_raw = child_plan_loaded
            terminal, terminal_raw = terminal_loaded
            if (
                child_plan.get("schema_version") != "2.2.0"
                or canonical_json_digest(
                    {key: value for key, value in child_plan.items() if key != "plan_sha256"}
                ) != child["plan_sha256"]
                or child_plan.get("plan_sha256") != child["plan_sha256"]
                or child_plan.get("package_manifest_sha256") != child["package_manifest_sha256"]
                or child_plan.get("migration_sha256") != child["migration_sha256"]
                or not route_child_context_matches(
                    child_plan.get("multi_hop_checkpoint_context"),
                    route_transaction_id=route_root.name,
                    route_intent_sha256=sha256_bytes(intent_raw),
                    edges=edges,
                    hop_index=index,
                    predecessor_checkpoint_sha256=(checkpoint_shas[index - 1] if index and len(checkpoint_shas) >= index else None),
                    predecessor_of_predecessor_checkpoint_sha256=(checkpoint_predecessors[index - 1] if index and len(checkpoint_predecessors) >= index else None),
                )
                or child_journal.get("schema_version")
                not in {
                    "ai-context-package-apply-journal/v4",
                    "ai-context-package-apply-journal/v5",
                }
                or child_journal.get("state") != "finalized"
                or child_journal.get("terminal_receipt_sha256") != child["terminal_receipt_sha256"]
                or sha256_bytes(terminal_raw) != child["terminal_receipt_sha256"]
                or child_journal.get("remediation_packet_sha256") != child["remediation_packet_sha256"]
                or child_journal.get("remediation_decision_sha256") != child["remediation_decision_sha256"]
                or child_journal.get("incoming_validation_receipt_sha256") != child["incoming_validation_receipt_sha256"]
                or child_journal.get("target_validation_receipt_sha256") != child["target_validation_receipt_sha256"]
                or terminal.get("transaction_id") != child["transaction_id"]
                or terminal.get("plan_sha256") != child["plan_sha256"]
                or terminal.get("pending_receipt_sha256") != pending["sha256"]
                or terminal.get("target_validation_receipt_sha256") != child["target_validation_receipt_sha256"]
                or terminal.get("provenance_sha256") != authority["provenance_sha256"]
                or terminal.get("customizations_sha256") != authority["customizations_sha256"]
            ):
                errors.append(f"{route_root}: multi-hop checkpoint {index} child terminal evidence differs")
            if promoted is not None:
                _promoted_package, _promoted_execution, package_root = promoted
                if (
                    child_plan.get("package_root") != str(package_root)
                    or child_plan.get("package_manifest_sha256")
                    != package["package_manifest_sha256"]
                    or child_plan.get("migration_sha256") != package["migration_sha256"]
                ):
                    errors.append(
                        f"{route_root}: multi-hop checkpoint {index} child package evidence differs"
                    )
            historical_error_start = len(errors)
            validate_historical_finalized_upgrade_transaction(
                root,
                child["transaction_id"],
                child_journal,
                errors,
                transaction_base=child_directory,
            )
            if len(errors) != historical_error_start:
                errors.append(
                    f"{route_root}: multi-hop checkpoint {index} sealed child evidence differs"
                )
        if expected_count and previous_sha != last_sha:
            errors.append(f"{route_root}: multi-hop route journal last checkpoint digest differs")
        active_states = {
            "awaiting-owner-decision",
            "applying",
            "awaiting-target-validation",
            "validating",
            "finalizing",
            "checkpointing",
            "rolling-back",
        }
        active = journal.get("active_hop")
        if journal["state"] in active_states:
            base_active_keys = {
                "hop_index",
                "edge",
                "package",
                "validator_execution",
                "plan_sha256",
                "proposal_plan_sha256",
                "child_transaction_id",
            }
            child_active_keys = base_active_keys | {
                "pending_receipt_sha256",
                "child_evidence_path",
            }
            if (
                not isinstance(active, dict)
                or (set(active) != base_active_keys and set(active) != child_active_keys)
                or type(active.get("hop_index")) is not int
                or active["hop_index"] != journal["next_hop_index"]
                or not 0 <= active["hop_index"] < len(edges)
                or active.get("edge") != edges[active["hop_index"]]
                or not route_sha(active.get("plan_sha256"))
                or not route_sha(active.get("proposal_plan_sha256"))
                or not isinstance(active.get("package"), dict)
                or not isinstance(active.get("validator_execution"), dict)
            ):
                errors.append(f"{route_root}: active multi-hop route evidence is invalid")
            else:
                transaction = active.get("child_transaction_id")
                index = active["hop_index"]
                hop_root = route_root / "hops" / f"{index:04d}"
                promoted = validate_promoted_multi_hop_evidence(
                    route_root,
                    index,
                    edges[index],
                    full_edges[index],
                    active.get("package"),
                    active.get("validator_execution"),
                    active.get("plan_sha256"),
                    errors,
                )
                if transaction is None:
                    if set(active) != base_active_keys or journal["state"] not in {
                        "awaiting-owner-decision",
                        "applying",
                    }:
                        errors.append(f"{route_root}: active multi-hop route child identity is invalid")
                    proposal_loaded = route_canonical_json(
                        hop_root / "preparation.json",
                        "active multi-hop proposal plan",
                        errors,
                    )
                    if proposal_loaded is not None:
                        proposal, proposal_raw = proposal_loaded
                        if (
                            sha256_bytes(proposal_raw)
                            != active.get("proposal_plan_sha256")
                            or proposal.get("schema_version") != "2.2.0"
                            or proposal.get("plan_sha256") != active.get("plan_sha256")
                            or canonical_json_digest(
                                {
                                    key: value
                                    for key, value in proposal.items()
                                    if key != "plan_sha256"
                                }
                            )
                            != active.get("plan_sha256")
                            or (
                                promoted is not None
                                and proposal.get("package_root")
                                != str(promoted[2])
                            )
                            or (
                                promoted is not None
                                and proposal.get("package_manifest_sha256")
                                != promoted[0]["package_manifest_sha256"]
                            )
                            or (
                                promoted is not None
                                and proposal.get("migration_sha256")
                                != promoted[0]["migration_sha256"]
                            )
                            or not route_child_context_matches(
                                proposal.get("multi_hop_checkpoint_context"),
                                route_transaction_id=route_root.name,
                                route_intent_sha256=sha256_bytes(intent_raw),
                                edges=edges,
                                hop_index=index,
                                predecessor_checkpoint_sha256=(
                                    checkpoint_shas[index - 1]
                                    if index and len(checkpoint_shas) >= index
                                    else None
                                ),
                                predecessor_of_predecessor_checkpoint_sha256=(
                                    checkpoint_predecessors[index - 1]
                                    if index and len(checkpoint_predecessors) >= index
                                    else None
                                ),
                            )
                        ):
                            errors.append(
                                f"{route_root}: active multi-hop proposal plan differs"
                            )
                elif (
                    not route_sha(transaction)
                    or set(active) != child_active_keys
                    or active.get("plan_sha256") != transaction
                    or not route_sha(active.get("pending_receipt_sha256"))
                    or active.get("child_evidence_path") != f"ai-context-package-apply/{transaction}"
                    or child_directory is None
                    or not (child_directory / transaction).is_dir()
                ):
                    errors.append(f"{route_root}: active multi-hop route child binding is invalid")
                else:
                    active_plan_loaded = route_canonical_json(
                        child_directory / transaction / "plan.json",
                        "active child package apply plan",
                        errors,
                    )
                    if active_plan_loaded is not None:
                        active_plan, active_plan_raw = active_plan_loaded
                        index = active["hop_index"]
                        if (
                            canonical_json_digest(
                                {key: value for key, value in active_plan.items() if key != "plan_sha256"}
                            ) != transaction
                            or active_plan.get("plan_sha256") != transaction
                            or (
                                promoted is not None
                                and active_plan.get("package_root") != str(promoted[2])
                            )
                            or (
                                promoted is not None
                                and active_plan.get("package_manifest_sha256")
                                != promoted[0]["package_manifest_sha256"]
                            )
                            or (
                                promoted is not None
                                and active_plan.get("migration_sha256")
                                != promoted[0]["migration_sha256"]
                            )
                            or not route_child_context_matches(
                                active_plan.get("multi_hop_checkpoint_context"),
                                route_transaction_id=route_root.name,
                                route_intent_sha256=sha256_bytes(intent_raw),
                                edges=edges,
                                hop_index=index,
                                predecessor_checkpoint_sha256=(checkpoint_shas[index - 1] if index and len(checkpoint_shas) >= index else None),
                                predecessor_of_predecessor_checkpoint_sha256=(checkpoint_predecessors[index - 1] if index and len(checkpoint_predecessors) >= index else None),
                            )
                        ):
                            errors.append(f"{route_root}: active multi-hop child route context differs")
                        validate_transient_bound_multi_hop_proposal(
                            route_root,
                            child_directory,
                            journal,
                            active,
                            active_plan,
                            edges,
                            intent_raw,
                            checkpoint_shas,
                            checkpoint_predecessors,
                            promoted,
                            errors,
                        )
        elif active is not None:
            errors.append(f"{route_root}: inactive multi-hop route retains active-hop evidence")
        if journal["state"] in {"checkpointed", "completed"} and last_checkpoint is not None:
            current_surface = (
                route_target_surface(root, errors)
                if snapshot_surface is None
                else {
                    relative: dict(state)
                    for relative, state in snapshot_surface.items()
                }
            )
            authority = last_checkpoint.get("authority")
            target_surface = last_checkpoint.get("target_surface")
            provenance = route_regular_bytes(
                root / ".dev/ai-context/provenance.yaml",
                "current multi-hop checkpoint provenance",
                errors,
            )
            customizations = route_regular_bytes(
                root / ".dev/ai-context/customizations.yaml",
                "current multi-hop checkpoint customizations",
                errors,
            )
            if (
                current_surface is None
                or not isinstance(authority, dict)
                or not isinstance(target_surface, dict)
                or current_surface != target_surface.get("paths")
                or provenance is None
                or customizations is None
                or hashlib.sha256(provenance).hexdigest() != authority.get("provenance_sha256")
                or hashlib.sha256(customizations).hexdigest() != authority.get("customizations_sha256")
            ):
                errors.append(f"{route_root}: final multi-hop checkpoint surface or authority differs")


def validate_v5_progress_log(
    transaction: Path, journal: dict, errors: list[str]
) -> None:
    if journal.get("schema_version") != "ai-context-package-apply-journal/v5":
        return
    initial_error_count = len(errors)
    path_value = journal.get("progress_log_path")
    count = journal.get("progress_record_count")
    tail = journal.get("progress_tail_sha256")
    if (
        path_value != "progress.jsonl"
        or type(count) is not int
        or count < 0
        or (count == 0 and tail is not None)
        or (
            count > 0
            and (
                not isinstance(tail, str)
                or not re.fullmatch(r"[0-9a-f]{64}", tail)
            )
        )
    ):
        errors.append(f"{transaction / 'journal.yaml'}: v5 progress binding is invalid")
        return
    progress_path = transaction / "progress.jsonl"
    if progress_path.is_symlink() or is_reparse_point(progress_path):
        errors.append(f"{progress_path}: v5 progress log is unsafe")
        return
    if not progress_path.exists():
        if count != 0:
            errors.append(f"{progress_path}: v5 progress log is missing")
            return
        raw = b""
    else:
        if not progress_path.is_file():
            errors.append(f"{progress_path}: v5 progress log is unsafe")
            return
        try:
            raw = progress_path.read_bytes()
        except OSError as exc:
            errors.append(f"{progress_path}: cannot read v5 progress log: {exc}")
            return
    framed = raw[: raw.rfind(b"\n") + 1] if raw and not raw.endswith(b"\n") else raw
    records: list[dict] = []
    previous: str | None = None
    for sequence, line in enumerate(framed.splitlines(keepends=True), start=1):
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"{progress_path}: v5 progress log cannot be parsed")
            return
        canonical = (
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            + b"\n"
            if isinstance(record, dict)
            else b""
        )
        if canonical != line:
            errors.append(f"{progress_path}: v5 progress record is not canonical")
            return
        phase = record.get("phase")
        common = {
            "schema_version",
            "sequence",
            "phase",
            "previous_record_sha256",
            "transition_sequence",
            "record_sha256",
        }
        expected_keys = (
            common | {"operation_index", "operation_id"}
            if phase == "apply"
            else common | {"rollback_index", "path"}
            if phase == "rollback"
            else set()
        )
        unsigned = dict(record)
        declared = unsigned.pop("record_sha256", None)
        if (
            not expected_keys
            or set(record) != expected_keys
            or record.get("schema_version") != "ai-context-package-apply-progress/v1"
            or type(record.get("sequence")) is not int
            or record.get("sequence") != sequence
            or record.get("previous_record_sha256") != previous
            or type(record.get("transition_sequence")) is not int
            or record["transition_sequence"] < 0
            or (
                phase == "apply"
                and (
                    type(record.get("operation_index")) is not int
                    or not isinstance(record.get("operation_id"), str)
                )
            )
            or (
                phase == "rollback"
                and (
                    type(record.get("rollback_index")) is not int
                    or not isinstance(record.get("path"), str)
                )
            )
            or not isinstance(declared, str)
            or canonical_json_digest(unsigned) != declared
        ):
            errors.append(f"{progress_path}: v5 progress record is invalid")
            return
        previous = declared
        records.append(record)
    if count > len(records) or (count and records[count - 1]["record_sha256"] != tail):
        errors.append(f"{progress_path}: v5 progress snapshot binding differs")
    elif journal.get("state") in {
        "awaiting-target-validation",
        "validated",
        "rejected",
        "rolled-back",
        "finalized",
    } and count != len(records):
        errors.append(f"{progress_path}: terminal v5 progress is not fully compacted")
    if len(errors) != initial_error_count:
        return

    # Reuse the recovery implementation's semantic replay so target admission
    # cannot accept a digest-valid log that package recovery would reject.
    plan_path = transaction / "plan.json"
    if (
        not plan_path.is_file()
        or plan_path.is_symlink()
        or is_reparse_point(plan_path)
    ):
        errors.append(
            f"{progress_path}: v5 progress semantics cannot bind a safe sealed plan"
        )
        return
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(
            f"{progress_path}: v5 progress semantics cannot read sealed plan: {exc}"
        )
        return
    if not isinstance(plan, dict):
        errors.append(
            f"{progress_path}: v5 progress semantics require a sealed plan mapping"
        )
        return
    unsigned_plan = dict(plan)
    declared_plan_sha = unsigned_plan.pop("plan_sha256", None)
    if (
        declared_plan_sha != transaction.name
        or canonical_json_digest(unsigned_plan) != transaction.name
    ):
        errors.append(
            f"{progress_path}: v5 progress semantics cannot bind the sealed plan identity"
        )
        return
    try:
        import ai_context_package_apply as package_apply

        effective_journal = package_apply.replay_journal_progress(
            transaction, plan, journal
        )
        package_apply.validate_journal_progress(plan, effective_journal)
    except (ImportError, OSError, KeyError, TypeError, ValueError) as exc:
        errors.append(
            f"{progress_path}: v5 progress semantics differ from sealed plan: {exc}"
        )


def validate_apply_transaction_journals(
    root: Path,
    receipt: dict | None,
    errors: list[str],
    *,
    enforce_terminal_invariants: bool = True,
) -> None:
    try:
        transaction_directory = apply_transaction_directory(root)
    except TargetValidationError as exc:
        errors.append(str(exc))
        return
    if transaction_directory is None:
        if receipt is not None and receipt.get("schema_version") == "2.0.0":
            errors.append("schema 2.0.0 pending receipt has no durable transaction evidence")
        return
    if transaction_directory.is_symlink() or is_reparse_point(transaction_directory):
        errors.append(f"{transaction_directory}: transaction directory is unsafe")
        return
    if not transaction_directory.exists():
        if receipt is not None and receipt.get("schema_version") == "2.0.0":
            errors.append("schema 2.0.0 pending receipt has no durable transaction evidence")
        return
    if not transaction_directory.is_dir():
        errors.append(f"{transaction_directory}: transaction directory is unsafe")
        return
    receipt_transaction = receipt.get("transaction_id") if receipt is not None else None
    matched_receipt = False
    for child in sorted(transaction_directory.iterdir(), key=lambda path: path.name):
        if not re.fullmatch(r"[0-9a-f]{64}", child.name):
            continue
        if child.is_symlink() or is_reparse_point(child) or not child.is_dir():
            errors.append(f"{child}: transaction root is unsafe")
            continue
        journal_path = child / "journal.yaml"
        journal = (
            load_mapping(journal_path, errors)
            if journal_path.is_file()
            and not journal_path.is_symlink()
            and not is_reparse_point(journal_path)
            else None
        )
        if journal is None:
            errors.append(f"{child}: transaction journal is missing or invalid")
            continue
        state = journal.get("state")
        journal_schema = journal.get("schema_version")
        if journal_schema not in {
            "ai-context-package-apply-journal/v1",
            "ai-context-package-apply-journal/v2",
            "ai-context-package-apply-journal/v3",
            "ai-context-package-apply-journal/v4",
            "ai-context-package-apply-journal/v5",
        } or journal.get("transaction_id") != child.name or journal.get("plan_sha256") != child.name:
            errors.append(f"{journal_path}: transaction identity is invalid")
            continue
        validate_v5_progress_log(child, journal, errors)
        if state in {"planned", "applying", "interrupted", "rolling-back"}:
            errors.append(f"{journal_path}: package apply transaction is {state}")
        elif state not in {
            "awaiting-target-validation",
            "validated",
            "rejected",
            "rolled-back",
            "finalized",
        }:
            errors.append(f"{journal_path}: package apply transaction state is invalid")
        if state == "rejected":
            if journal_schema not in {
                "ai-context-package-apply-journal/v4",
                "ai-context-package-apply-journal/v5",
            }:
                errors.append(f"{journal_path}: rejected transaction journal schema is unsupported")
            else:
                validate_rejected_upgrade_transaction(root, child.name, journal, errors)
            continue
        if (
            journal_schema
            in {
                "ai-context-package-apply-journal/v4",
                "ai-context-package-apply-journal/v5",
            }
            and state == "finalized"
            and child.name != receipt_transaction
        ):
            validate_historical_finalized_upgrade_transaction(
                root, child.name, journal, errors
            )
            continue
        if (
            journal_schema
            in {
                "ai-context-package-apply-journal/v4",
                "ai-context-package-apply-journal/v5",
            }
            and state in {"awaiting-target-validation", "validated"}
            and child.name != receipt_transaction
        ):
            errors.append(
                f"{journal_path}: unresolved upgrade transaction is not the pending receipt transaction"
            )
            continue
        if child.name == receipt_transaction:
            matched_receipt = True
            expected_states = (
                {"finalized"}
                if journal_schema == "ai-context-package-apply-journal/v3"
                else {"awaiting-target-validation", "validated", "finalized"}
            )
            if state not in expected_states:
                errors.append(f"{journal_path}: pending receipt transaction state is invalid")
                continue
            if journal_schema not in {
                "ai-context-package-apply-journal/v3",
                "ai-context-package-apply-journal/v4",
                "ai-context-package-apply-journal/v5",
            }:
                errors.append(
                    f"{journal_path}: pending receipt transaction journal schema is unsupported"
                )
                continue
            expected_plan_schema = (
                "2.1.0"
                if journal_schema == "ai-context-package-apply-journal/v3"
                else "2.2.0"
            )
            receipt_path = root / PENDING_APPLY_RECEIPT
            try:
                receipt_path = target_path_without_links(root, PENDING_APPLY_RECEIPT)
                actual_receipt_sha = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            except (TargetValidationError, OSError) as exc:
                errors.append(f"{receipt_path}: pending receipt boundary is invalid: {exc}")
                continue
            if journal.get("final_receipt_sha256") != actual_receipt_sha:
                errors.append(f"{journal_path}: finalized receipt SHA-256 differs")
            plan_path = child / "plan.json"
            if plan_path.is_symlink() or is_reparse_point(plan_path):
                errors.append(f"{plan_path}: sealed transaction plan boundary is unsafe")
                continue
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"{plan_path}: sealed transaction plan is invalid: {exc}")
                continue
            if not isinstance(plan, dict):
                errors.append(f"{plan_path}: sealed transaction plan must be a mapping")
                continue
            unsigned = dict(plan)
            declared_plan_sha = unsigned.pop("plan_sha256", None)
            if declared_plan_sha != child.name or canonical_json_digest(unsigned) != child.name:
                errors.append(f"{plan_path}: sealed transaction plan identity differs")
                continue
            expected_receipt_state = (
                "awaiting-target-validation"
                if journal_schema
                in {
                    "ai-context-package-apply-journal/v4",
                    "ai-context-package-apply-journal/v5",
                }
                and plan.get("previous_version") is not None
                else "finalized"
            )
            if receipt is not None and receipt.get("transaction_state") != expected_receipt_state:
                errors.append(
                    f"{journal_path}: pending receipt transaction state differs"
                )
            sealed_target = plan.get("target_root")
            sealed_head = plan.get("target_starting_commit")
            try:
                target_matches = (
                    isinstance(sealed_target, str)
                    and Path(sealed_target).is_absolute()
                    and Path(sealed_target).resolve() == root.resolve()
                )
                head_matches = (
                    isinstance(sealed_head, str)
                    and bool(SHA_RE.fullmatch(sealed_head))
                    and current_target_head(root) == sealed_head
                )
            except (OSError, TargetValidationError):
                target_matches = False
                head_matches = False
            if not target_matches:
                errors.append(f"{plan_path}: sealed target root differs from current target")
            if not head_matches:
                errors.append(f"{plan_path}: sealed target starting commit differs from current HEAD")
            operation_items = validate_sealed_operations(plan, plan_path, errors)
            operations_valid = operation_items is not None
            operation_items = operation_items or []
            active_operations = [
                item
                for item in operation_items
                if isinstance(item, dict)
                and item.get("action") in {"add", "replace", "remove", "rename"}
            ]
            active_ids = [item.get("id") for item in active_operations]
            if operations_valid:
                expected_staging = transaction_staging_records(
                    child.name, active_operations
                )
                staging_valid = (
                    journal.get("target_staging_paths") == expected_staging
                )
                if staging_valid:
                    for item in expected_staging:
                        try:
                            staging_path = target_path_without_links(
                                root, item["path"]
                            )
                        except TargetValidationError as exc:
                            errors.append(
                                f"{journal_path}: transaction staging boundary is invalid: {exc}"
                            )
                            break
                        if staging_path.exists():
                            errors.append(
                                f"{journal_path}: transaction staging path remains: {item['path']}"
                            )
                            break
                else:
                    errors.append(
                        f"{journal_path}: transaction staging path evidence is invalid"
                    )
            post_state_records = plan.get("operation_post_states")
            post_state_valid = (
                plan.get("schema_version") == expected_plan_schema
                and operations_valid
                and isinstance(post_state_records, list)
                and len(post_state_records) == len(active_operations)
                and all(
                    isinstance(item.get("id"), str)
                    and bool(item.get("id"))
                    and safe_target_path(item.get("path"))
                    and (
                        item.get("action") != "rename"
                        or safe_target_path(item.get("from_path"))
                    )
                    for item in active_operations
                )
                and len(active_ids) == len(set(active_ids))
            )
            if post_state_valid:
                for operation, record in zip(
                    active_operations, post_state_records, strict=True
                ):
                    expected_paths = [operation.get("path")]
                    if operation.get("action") == "rename":
                        expected_paths.append(operation.get("from_path"))
                    paths = record.get("paths") if isinstance(record, dict) else None
                    if (
                        not isinstance(record, dict)
                        or record.get("operation_id") != operation.get("id")
                        or not isinstance(paths, list)
                        or [
                            item.get("path") if isinstance(item, dict) else None
                            for item in paths
                        ]
                        != expected_paths
                    ):
                        post_state_valid = False
                        break
                    for path_index, item in enumerate(paths):
                        state_record = item.get("state")
                        if not isinstance(state_record, dict) or set(state_record) != {
                            "exists",
                            "sha256",
                            "mode",
                        }:
                            post_state_valid = False
                            break
                        if state_record.get("exists") is True:
                            if (
                                operation.get("action") == "remove"
                                or (
                                    operation.get("action") == "rename"
                                    and path_index == 1
                                )
                                or not isinstance(
                                    state_record.get("sha256"), str
                                )
                                or not re.fullmatch(
                                    r"[0-9a-f]{64}", state_record["sha256"]
                                )
                                or state_record.get("mode") not in {"0644", "0755"}
                            ):
                                post_state_valid = False
                                break
                        elif (
                            state_record.get("exists") is not False
                            or operation.get("action") in {"add", "replace"}
                            or (
                                operation.get("action") == "rename"
                                and path_index == 0
                            )
                            or state_record
                            != {
                                "exists": False,
                                "sha256": None,
                                "mode": None,
                            }
                        ):
                            post_state_valid = False
                            break
                    if not post_state_valid:
                        break
            if not post_state_valid:
                errors.append(
                    f"{plan_path}: sealed transaction post-state evidence is invalid"
                )
            expected_operation_order_sha = canonical_json_digest(active_ids)
            transition_sequence = journal.get("transition_sequence")
            minimum_sequence = len(active_ids) + 2
            if journal_schema in {
                "ai-context-package-apply-journal/v4",
                "ai-context-package-apply-journal/v5",
            }:
                expected_transition_sequence = expected_terminal_transition_sequence(
                    plan, state, len(active_ids)
                )
                transition_sequence_valid = (
                    type(transition_sequence) is int
                    and transition_sequence == expected_transition_sequence
                )
            else:
                transition_sequence_valid = (
                    type(transition_sequence) is int
                    and transition_sequence >= minimum_sequence
                    and (transition_sequence - minimum_sequence) % 2 == 0
                )
            finalized_progress_valid = (
                type(journal.get("next_apply_index")) is int
                and journal.get("next_apply_index") == len(active_ids)
                and journal.get("completed_operation_ids") == active_ids
                and journal.get("operation_order_sha256")
                == expected_operation_order_sha
                and transition_sequence_valid
                and type(journal.get("rollback_next_index")) is int
                and journal.get("rollback_next_index") == 0
                and journal.get("rollback_completed_paths") == []
                and journal.get("rollback_start_state") is None
            )
            if not finalized_progress_valid:
                errors.append(
                    f"{journal_path}: finalized transaction progress is invalid"
                )
            post_state_by_operation = (
                {
                    record.get("operation_id"): {
                        item.get("path"): item.get("state")
                        for item in record.get("paths", [])
                        if isinstance(item, dict)
                    }
                    for record in post_state_records
                }
                if post_state_valid
                else {}
            )
            expected_artifacts = [
                (
                    item.get("id"),
                    item.get("path"),
                    post_state_by_operation.get(item.get("id"), {})
                    .get(item.get("path"), {})
                    .get("sha256"),
                    post_state_by_operation.get(item.get("id"), {})
                    .get(item.get("path"), {})
                    .get("mode"),
                )
                for item in active_operations
                if item.get("action") in {"add", "replace", "rename"}
            ]
            receipt_artifacts = (
                receipt.get("applied_artifacts") if receipt is not None else None
            )
            actual_artifacts = [
                (
                    item.get("operation_id"),
                    item.get("path"),
                    item.get("raw_sha256"),
                    item.get("git_mode"),
                )
                for item in receipt_artifacts
                if isinstance(item, dict)
            ] if isinstance(receipt_artifacts, list) else []
            expected_removed = [
                (
                    item.get("id"),
                    item.get("from_path")
                    if item.get("action") == "rename"
                    else item.get("path"),
                )
                for item in active_operations
                if item.get("action") in {"remove", "rename"}
            ]
            receipt_removed = (
                receipt.get("removed_paths") if receipt is not None else None
            )
            actual_removed = [
                (item.get("operation_id"), item.get("path"), item.get("result"))
                for item in receipt_removed
                if isinstance(item, dict)
            ] if isinstance(receipt_removed, list) else []
            expected_removed = [(*item, "absent") for item in expected_removed]
            if (
                receipt is None
                or not isinstance(receipt_artifacts, list)
                or not isinstance(receipt_removed, list)
                or receipt.get("plan_sha256") != child.name
                or receipt.get("operation_order") != active_ids
                or receipt.get("applied_operation_ids") != active_ids
                or receipt.get("required_framework_paths")
                != plan.get("required_framework_paths")
                or receipt.get("selected_input_proof")
                != plan.get("package_selected_input_proof")
                or receipt.get("package_id") != plan.get("package_id")
                or receipt.get("package_version") != plan.get("package_version")
                or receipt.get("package_manifest_sha256")
                != plan.get("package_manifest_sha256")
                or receipt.get("migration_sha256") != plan.get("migration_sha256")
                or receipt.get("target_starting_commit")
                != plan.get("target_starting_commit")
                or receipt.get("selection") != plan.get("selection")
                or actual_artifacts != expected_artifacts
                or actual_removed != expected_removed
            ):
                errors.append(f"{receipt_path}: receipt differs from the sealed transaction plan")
            if (
                journal_schema
                in {
                    "ai-context-package-apply-journal/v4",
                    "ai-context-package-apply-journal/v5",
                }
                and plan.get("upgrade_remediation_required") is True
            ):
                upgrade_errors: list[str] = []
                upgrade_evidence = validate_upgrade_finalization_evidence(
                    root, None, None, upgrade_errors
                )
                errors.extend(upgrade_errors)
                if upgrade_evidence is not None and enforce_terminal_invariants:
                    validate_terminal_receipt_invariant(root, upgrade_evidence, errors)
    validate_multi_hop_route_transactions(root, errors)
    if receipt is not None and receipt.get("schema_version") == "2.0.0" and not matched_receipt:
        errors.append("schema 2.0.0 pending receipt transaction evidence does not match")


def validate_pending_apply_receipt(
    root: Path, errors: list[str], *, enforce_terminal_invariants: bool = True
) -> None:
    """Validate selected managed bytes and ignore state carried by a new receipt."""
    root = root.resolve()
    receipt_path = checked_target_path(
        root, PENDING_APPLY_RECEIPT, "pending apply receipt", errors
    )
    if receipt_path is None:
        return
    if not receipt_path.is_file():
        validate_apply_transaction_journals(
            root,
            None,
            errors,
            enforce_terminal_invariants=enforce_terminal_invariants,
        )
        return
    receipt = load_mapping(receipt_path, errors)
    if receipt is None:
        return
    validate_apply_transaction_journals(
        root,
        receipt,
        errors,
        enforce_terminal_invariants=enforce_terminal_invariants,
    )
    schema_version = receipt.get("schema_version")
    if schema_version not in {"1.0.0", "1.1.0", "2.0.0"}:
        errors.append(f"{receipt_path}: unsupported pending apply receipt schema")
        return
    enforce_filemode = True
    schema2_results_by_path: dict[str, dict] = {}
    if schema_version == "2.0.0":
        try:
            enforce_filemode = target_enforces_filemode(root)
        except TargetValidationError as exc:
            errors.append(str(exc))
        if receipt.get("status") != "pending-validation":
            errors.append(f"{receipt_path}: schema 2.0.0 status must be pending-validation")
        if receipt.get("transaction_state") not in {
            "finalized",
            "awaiting-target-validation",
        }:
            errors.append(
                f"{receipt_path}: schema 2.0.0 transaction_state is invalid"
            )
        transaction_id = receipt.get("transaction_id")
        plan_sha = receipt.get("plan_sha256")
        if not isinstance(transaction_id, str) or not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
            errors.append(f"{receipt_path}: transaction_id must be a lowercase SHA-256")
        if plan_sha != transaction_id:
            errors.append(f"{receipt_path}: plan_sha256 must equal transaction_id")
        selected_proof = receipt.get("selected_input_proof")
        if selected_proof is not None and (
            not isinstance(selected_proof, dict)
            or selected_proof.get("path") != "metadata/selected-inputs.json"
            or not isinstance(selected_proof.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", selected_proof["sha256"])
        ):
            errors.append(f"{receipt_path}: selected_input_proof is invalid")
        operation_order = receipt.get("operation_order")
        applied_ids = receipt.get("applied_operation_ids")
        if not isinstance(operation_order, list) or not all(
            isinstance(value, str) and value for value in operation_order
        ):
            errors.append(f"{receipt_path}: operation_order must be a string list")
        elif operation_order != applied_ids or len(operation_order) != len(set(operation_order)):
            errors.append(
                f"{receipt_path}: operation_order must be unique and equal applied_operation_ids"
            )
        declared_results = receipt.get("selected_managed_path_results")
        if isinstance(declared_results, list):
            schema2_results_by_path = {
                item.get("path"): item
                for item in declared_results
                if isinstance(item, dict) and isinstance(item.get("path"), str)
            }
    required = receipt.get("required_framework_paths")
    if required is None:
        if receipt.get("schema_version") == "1.1.0":
            errors.append(
                f"{receipt_path}: schema 1.1.0 requires required_framework_paths"
            )
        return
    if not isinstance(required, list):
        errors.append(f"{receipt_path}: required_framework_paths must be a list")
        return
    seen: set[str] = set()
    ordered: list[str] = []
    for index, item in enumerate(required):
        label = f"{receipt_path}: required_framework_paths[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        path = item.get("path")
        component_id = item.get("component_id")
        expected_sha = item.get("sha256")
        expected_mode = item.get("mode")
        if not safe_target_path(path):
            errors.append(f"{label}.path must be a safe POSIX target path")
            continue
        if path in seen:
            errors.append(f"{receipt_path}: required framework paths must be unique")
            continue
        seen.add(path)
        ordered.append(path)
        if not isinstance(component_id, str) or not component_id:
            errors.append(f"{label}.component_id must be non-empty")
        if item.get("ownership") != "framework-managed":
            errors.append(f"{label}.ownership must be framework-managed")
        if not isinstance(expected_sha, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_sha
        ):
            errors.append(f"{label}.sha256 must be a lowercase SHA-256")
        if schema_version == "2.0.0" and expected_mode not in {"0644", "0755"}:
            errors.append(f"{label}.mode must be 0644 or 0755")
        candidate = checked_target_path(root, path, label, errors)
        if candidate is None:
            continue
        if not candidate.is_file():
            errors.append(f"required framework-managed path is absent: {path}")
            continue
        if isinstance(expected_sha, str) and re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            actual_sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_sha != expected_sha:
                result_record = schema2_results_by_path.get(path, {})
                if not (
                    schema_version == "2.0.0"
                    and result_record.get("match_basis") == "git-eol-canonical"
                    and result_record.get("observed_raw_sha256") == actual_sha
                    and git_eol_projection_matches(
                        root, path, candidate.read_bytes(), expected_sha
                    )
                ):
                    errors.append(
                        f"required framework-managed path bytes differ: {path}"
                    )
        if schema_version == "2.0.0" and enforce_filemode and expected_mode in {"0644", "0755"}:
            actual_mode = "0755" if candidate.stat().st_mode & stat.S_IXUSR else "0644"
            if actual_mode != expected_mode:
                errors.append(f"required framework-managed path mode differs: {path}")
        if isinstance(component_id, str) and component_id:
            try:
                rule = git_ignore_rule(root, path)
            except TargetValidationError as exc:
                errors.append(str(exc))
            else:
                if rule is not None:
                    errors.append(
                        framework_managed_ignore_message(path, component_id, rule)
                    )
    if ordered != sorted(ordered, key=lambda value: value.encode("utf-8")):
        errors.append(
            f"{receipt_path}: required framework paths must use UTF-8 bytewise order"
        )
    if schema_version != "2.0.0":
        return
    required_by_path = {
        item.get("path"): item for item in required if isinstance(item, dict)
    }
    artifacts = receipt.get("applied_artifacts")
    if not isinstance(artifacts, list):
        errors.append(f"{receipt_path}: applied_artifacts must be a list")
    else:
        artifact_paths: list[str] = []
        for index, item in enumerate(artifacts):
            label = f"{receipt_path}: applied_artifacts[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} must be a mapping")
                continue
            path = item.get("path")
            raw_sha = item.get("raw_sha256")
            git_mode = item.get("git_mode")
            if not safe_target_path(path):
                errors.append(f"{label}.path must be a safe POSIX target path")
                continue
            artifact_paths.append(path)
            candidate = checked_target_path(root, path, label, errors)
            if candidate is None:
                continue
            if not candidate.is_file():
                errors.append(f"applied artifact is absent: {path}")
                continue
            if not isinstance(raw_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", raw_sha):
                errors.append(f"{label}.raw_sha256 must be a lowercase SHA-256")
            elif hashlib.sha256(candidate.read_bytes()).hexdigest() != raw_sha:
                errors.append(f"applied artifact bytes differ: {path}")
            if git_mode not in {"0644", "0755"}:
                errors.append(f"{label}.git_mode must be 0644 or 0755")
            elif enforce_filemode:
                actual_mode = "0755" if candidate.stat().st_mode & stat.S_IXUSR else "0644"
                if actual_mode != git_mode:
                    errors.append(f"applied artifact mode differs: {path}")
        if len(artifact_paths) != len(set(artifact_paths)):
            errors.append(f"{receipt_path}: applied artifact paths must be unique")
    removed = receipt.get("removed_paths")
    if not isinstance(removed, list):
        errors.append(f"{receipt_path}: removed_paths must be a list")
    else:
        for index, item in enumerate(removed):
            label = f"{receipt_path}: removed_paths[{index}]"
            if not isinstance(item, dict) or not safe_target_path(item.get("path")) or item.get("result") != "absent":
                errors.append(f"{label} must bind a safe absent path")
                continue
            candidate = checked_target_path(root, item["path"], label, errors)
            if candidate is None:
                continue
            if candidate.exists():
                errors.append(f"removed path is present: {item['path']}")
    results = receipt.get("selected_managed_path_results")
    if not isinstance(results, list):
        errors.append(f"{receipt_path}: selected_managed_path_results must be a list")
    else:
        result_paths = [item.get("path") for item in results if isinstance(item, dict)]
        if result_paths != ordered:
            errors.append(
                f"{receipt_path}: selected managed results must exactly match required paths"
            )
        for index, item in enumerate(results):
            if not isinstance(item, dict):
                continue
            required_item = required_by_path.get(item.get("path"))
            candidate = None
            if safe_target_path(item.get("path")):
                candidate = checked_target_path(
                    root,
                    item["path"],
                    f"{receipt_path}: selected_managed_path_results[{index}]",
                    errors,
                )
            observed_sha = (
                hashlib.sha256(candidate.read_bytes()).hexdigest()
                if candidate is not None and candidate.is_file() and not candidate.is_symlink()
                else None
            )
            basis = item.get("match_basis")
            identity_matches = (
                required_item is not None
                and item.get("expected_raw_sha256") == required_item.get("sha256")
                and item.get("observed_raw_sha256") == observed_sha
                and item.get("expected_git_mode") == required_item.get("mode")
                and item.get("observed_git_mode") == required_item.get("mode")
                and item.get("disposition") == "package-identical"
                and (
                    (basis == "raw" and observed_sha == required_item.get("sha256"))
                    or (
                        basis == "git-eol-canonical"
                        and candidate is not None
                        and git_eol_projection_matches(
                            root,
                            item["path"],
                            candidate.read_bytes(),
                            required_item.get("sha256"),
                        )
                    )
                )
            )
            if not identity_matches:
                errors.append(
                    f"{receipt_path}: selected_managed_path_results[{index}] identity differs"
                )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def transaction_artifact_path(
    transaction: Path, name: str, label: str, errors: list[str]
) -> Path | None:
    """Resolve one fixed transaction artifact without accepting a redirected path."""
    candidate = transaction / name
    if (
        candidate.is_symlink()
        or is_reparse_point(candidate)
        or not candidate.is_file()
    ):
        errors.append(f"{label}: required transaction artifact is missing or unsafe")
        return None
    return candidate


def read_transaction_json(
    transaction: Path, name: str, label: str, errors: list[str]
) -> tuple[dict, str, Path] | None:
    path = transaction_artifact_path(transaction, name, label, errors)
    if path is None:
        return None
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: {label} is invalid: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: {label} must be a mapping")
        return None
    canonical = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    if raw != canonical:
        errors.append(f"{path}: {label} must use canonical JSON bytes")
        return None
    return value, sha256_bytes(raw), path


def canonical_document_digest(
    document: dict, label: str, errors: list[str]
) -> str | None:
    declared = document.get("canonical_digest")
    if not isinstance(declared, str) or not re.fullmatch(r"[0-9a-f]{64}", declared):
        errors.append(f"{label}: canonical_digest is invalid")
        return None
    unsigned = dict(document)
    unsigned.pop("canonical_digest", None)
    actual = canonical_json_digest(unsigned)
    if declared != actual:
        errors.append(f"{label}: canonical_digest differs")
        return None
    return actual


def journal_artifact_path(
    journal: dict, key: str, expected: str, label: str, errors: list[str]
) -> str:
    declared = journal.get(key)
    if declared != expected:
        errors.append(f"{label}: journal {key} differs")
    return expected


def journal_artifact_digest_matches(
    journal: dict,
    key: str,
    expected: str,
    alternate: str | None,
    label: str,
    errors: list[str],
) -> None:
    declared = journal.get(key)
    allowed = {expected}
    if alternate is not None:
        allowed.add(alternate)
    if declared not in allowed:
        errors.append(f"{label}: journal {key} differs")


def derived_remediation_report_bytes(
    packet: dict, packet_digest: str, errors: list[str]
) -> bytes | None:
    """Re-render the deterministic human projection from sealed packet fields."""
    target = packet.get("target")
    package = packet.get("package")
    proposal = packet.get("automatic_proposal")
    conflicts = packet.get("unresolved_conflicts")
    validation = package.get("validation") if isinstance(package, dict) else None
    execution = validation.get("execution") if isinstance(validation, dict) else None
    apply_ids = proposal.get("apply_operation_ids") if isinstance(proposal, dict) else None
    reconciliation_ids = (
        proposal.get("reconciliation_ids") if isinstance(proposal, dict) else None
    )
    if (
        not isinstance(target, dict)
        or not isinstance(package, dict)
        or not isinstance(apply_ids, list)
        or not isinstance(reconciliation_ids, list)
        or not isinstance(conflicts, list)
        or not all(isinstance(value, str) and value for value in [*apply_ids, *reconciliation_ids])
        or not isinstance(execution, dict)
        or not isinstance(execution.get("outcome"), str)
    ):
        errors.append("upgrade remediation packet cannot render its derived report")
        return None
    try:
        report = "\n".join(
            [
                f"derived_from_packet_digest: {packet_digest}",
                "# Upgrade remediation report",
                "",
                f"- Transaction: `{packet['transaction_id']}`",
                f"- Target HEAD: `{target['starting_commit']}`",
                f"- Package: `{package['id']}` / `{package['version']}`",
                f"- Automatic operations: {', '.join(apply_ids) or '(none)'}",
                f"- Reconciliation decisions: {', '.join(reconciliation_ids) or '(none)'}",
                f"- Unresolved conflicts: {len(conflicts)}",
                f"- Incoming validation: {execution['outcome']}",
                "",
            ]
        )
    except KeyError:
        errors.append("upgrade remediation packet cannot render its derived report")
        return None
    return report.encode("utf-8")


def active_operation_ids(plan: dict, plan_path: Path, errors: list[str]) -> list[str]:
    operations = validate_sealed_operations(plan, plan_path, errors)
    if operations is None:
        return []
    return [
        str(item["id"])
        for item in operations
        if item.get("action") in {"add", "replace", "remove", "rename"}
    ]


def expected_terminal_transition_sequence(
    plan: dict, state: object, active_operation_count: int
) -> int | None:
    """Return the only valid semantic sequence for a supported terminal state."""
    if state == "awaiting-target-validation":
        return active_operation_count + 2
    if state == "validated":
        return active_operation_count + 3
    if state == "finalized":
        return active_operation_count + (
            4 if plan.get("previous_version") is not None else 2
        )
    return None


def current_authority_digest(root: Path, relative: str, errors: list[str]) -> str | None:
    path = checked_target_path(root, relative, relative, errors)
    if path is None:
        return None
    if not path.exists():
        return None
    if not path.is_file():
        errors.append(f"{path}: authority path is not a regular file")
        return None
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        errors.append(f"{path}: cannot read authority bytes: {exc}")
        return None


def current_authority_identity(
    root: Path, relative: str, errors: list[str]
) -> tuple[str | None, str | None]:
    """Return the raw and canonical-document identity of one target authority."""
    path = checked_target_path(root, relative, relative, errors)
    if path is None:
        return None, None
    if not path.exists():
        return None, None
    if not path.is_file():
        errors.append(f"{path}: authority path is not a regular file")
        return None, None
    document = load_mapping(path, errors)
    if document is None:
        return None, None
    try:
        return sha256_bytes(path.read_bytes()), canonical_json_digest(document)
    except OSError as exc:
        errors.append(f"{path}: cannot read authority bytes: {exc}")
        return None, None


def candidate_authority(
    decision: dict, label: str, errors: list[str]
) -> dict[str, str] | None:
    value = decision.get("candidate_authority")
    if not isinstance(value, dict) or set(value) != {
        "provenance_sha256",
        "customizations_sha256",
    }:
        errors.append(f"{label}: candidate_authority is invalid")
        return None
    if not all(
        isinstance(value.get(key), str)
        and re.fullmatch(r"[0-9a-f]{64}", value[key])
        for key in ("provenance_sha256", "customizations_sha256")
    ):
        errors.append(f"{label}: candidate_authority digest is invalid")
        return None
    return {key: value[key] for key in ("provenance_sha256", "customizations_sha256")}


def candidate_authority_matches_documents(
    authority: dict[str, str], provenance: dict, ledger: dict, errors: list[str]
) -> bool:
    actual = {
        "provenance_sha256": canonical_json_digest(provenance),
        "customizations_sha256": canonical_json_digest(ledger),
    }
    if actual != authority:
        errors.append("upgrade remediation decision candidate authority differs from finalization candidates")
        return False
    return True


def validate_candidate_upgrade_binding(
    provenance: dict, packet: dict, errors: list[str]
) -> None:
    """Bind the approved candidate authority to the sealed upgrade identities."""
    package = packet.get("package")
    migration = packet.get("migration")
    package_source = package.get("source") if isinstance(package, dict) else None
    predecessor = packet.get("provenance")
    predecessor_source = (
        predecessor.get("source") if isinstance(predecessor, dict) else None
    )
    selected_input = (
        migration.get("selected_input") if isinstance(migration, dict) else None
    )
    version = package.get("version") if isinstance(package, dict) else None
    previous_version = (
        selected_input.get("previous_version")
        if isinstance(selected_input, dict)
        else None
    )
    if (
        not isinstance(package_source, dict)
        or not isinstance(version, str)
        or not version
        or not isinstance(previous_version, str)
        or not previous_version
    ):
        errors.append("upgrade candidate package or migration identity is invalid")
        return
    expected_version = f"v{version}"
    expected_previous_version = f"v{previous_version}"
    source = provenance.get("source")
    previous_source = provenance.get("previous_source")
    installation = provenance.get("installation")
    last_migration = provenance.get("last_migration")
    if (
        not isinstance(source, dict)
        or source.get("repository") != package_source.get("repository")
        or source.get("commit") != package_source.get("commit")
        or source.get("version") != expected_version
        or source.get("tag") != expected_version
        or source.get("release_id") != f"REL-{expected_version}"
    ):
        errors.append("upgrade candidate source differs from sealed package identity")
    if (
        not isinstance(previous_source, dict)
        or previous_source != predecessor_source
        or previous_source.get("version") != expected_previous_version
    ):
        errors.append(
            "upgrade candidate previous source differs from sealed predecessor authority"
        )
    if provenance.get("selection") != packet.get("selection"):
        errors.append("upgrade candidate selection differs from sealed packet")
    if (
        not isinstance(installation, dict)
        or not iso_with_offset(installation.get("last_upgraded_at"))
    ):
        errors.append("upgrade candidate last_upgraded_at is invalid")
    if (
        not isinstance(last_migration, dict)
        or last_migration.get("status") != "completed"
        or last_migration.get("from_version") != expected_previous_version
        or last_migration.get("to_version") != expected_version
        or not iso_with_offset(last_migration.get("completed_at"))
        or not safe_repo_reference(last_migration.get("evidence"))
    ):
        errors.append("upgrade candidate migration differs from sealed route")


def packet_authority_digest(
    value: object,
    label: str,
    expected_path: str,
    expected: str | None,
    errors: list[str],
) -> None:
    """Require the packet to bind the exact old authority bytes or their absence."""
    declared = value.get("sha256") if isinstance(value, dict) else value
    if (
        not isinstance(value, dict)
        or value.get("path") != expected_path
        or declared != expected
    ):
        errors.append(f"{label}: prior authority digest differs")


def validate_target_validation_profile(
    root: Path,
    packet: dict,
    errors: list[str],
    *,
    require_current_target: bool = True,
    require_executable_profile: bool = False,
) -> tuple[dict, str] | None:
    initial_error_count = len(errors)
    profile = packet.get("target_validation_profile")
    if not isinstance(profile, dict) or set(profile) != {
        "path",
        "sha256",
        "argv",
        "snapshot",
    }:
        errors.append("upgrade remediation packet: target_validation_profile is invalid")
        return None
    path = profile.get("path")
    argv = profile.get("argv")
    expected_sha = profile.get("sha256")
    if not safe_target_path(path):
        errors.append("upgrade remediation packet: target validation profile path is invalid")
    argv_is_valid = isinstance(argv, list) and all(
        isinstance(item, str) and item for item in argv
    )
    sha_is_valid = isinstance(expected_sha, str) and re.fullmatch(
        r"[0-9a-f]{64}", expected_sha
    )
    if require_executable_profile:
        if not argv_is_valid or not argv or not sha_is_valid:
            errors.append(
                "upgrade finalization requires a present executable target validation profile"
            )
    else:
        if not argv_is_valid:
            errors.append("upgrade remediation packet: target validation profile argv is invalid")
        if expected_sha is not None and not sha_is_valid:
            errors.append("upgrade remediation packet: target validation profile SHA-256 is invalid")
    if not isinstance(profile.get("snapshot"), dict):
        errors.append("upgrade remediation packet: target validation profile snapshot is invalid")
    if len(errors) != initial_error_count:
        return None
    profile_digest = canonical_json_digest(profile)
    if packet.get("target_validation_profile_digest") != profile_digest:
        errors.append("upgrade remediation packet: target validation profile digest differs")
        return None
    if not require_current_target:
        return profile, profile_digest
    profile_path = checked_target_path(root, str(path), "target validation profile", errors)
    if profile_path is None:
        return None
    if expected_sha is None:
        if profile_path.exists():
            errors.append("upgrade remediation packet: target validation profile absence differs")
            return None
        if argv != [] or profile.get("snapshot") != {"status": "absent"}:
            errors.append("upgrade remediation packet: absent target validation profile differs")
            return None
        return profile, profile_digest
    if not profile_path.is_file():
        errors.append("upgrade remediation packet: target validation profile is absent")
        return None
    try:
        actual_sha = sha256_bytes(profile_path.read_bytes())
    except OSError as exc:
        errors.append(f"{profile_path}: cannot read target validation profile: {exc}")
        return None
    if actual_sha != expected_sha:
        errors.append("upgrade remediation packet: target validation profile SHA-256 differs")
        return None
    return profile, profile_digest


def validate_incoming_validation_receipt(
    transaction: Path,
    journal: dict,
    packet: dict,
    packet_validation_profile: dict,
    validation_profile_digest: str,
    plan: dict,
    root: Path,
    errors: list[str],
) -> tuple[str, Path] | None:
    journal_artifact_path(
        journal,
        "incoming_validation_receipt_path",
        INCOMING_VALIDATION_RECEIPT_PATH,
        "incoming validation receipt",
        errors,
    )
    loaded = read_transaction_json(
        transaction,
        INCOMING_VALIDATION_RECEIPT_PATH,
        "incoming validation receipt",
        errors,
    )
    if loaded is None:
        return None
    receipt, raw_digest, path = loaded
    journal_artifact_digest_matches(
        journal,
        "incoming_validation_receipt_sha256",
        raw_digest,
        None,
        "incoming validation receipt",
        errors,
    )
    target = packet.get("target")
    package = packet.get("package")
    required = {
        "authority",
        "outcome",
        "transaction_id",
        "plan_sha256",
        "packet_sha256",
        "target",
        "package",
        "target_validation_profile",
        "target_validation_profile_digest",
        "validator",
    }
    if not isinstance(receipt, dict) or not required.issubset(receipt):
        errors.append(f"{path}: incoming validation receipt is incomplete")
        return None
    if receipt.get("authority") != "incoming-candidate" or receipt.get("outcome") != "passed":
        errors.append(f"{path}: incoming candidate validation did not pass")
    if receipt.get("transaction_id") != packet.get("transaction_id") or receipt.get(
        "plan_sha256"
    ) != packet.get("plan_sha256"):
        errors.append(f"{path}: incoming validation receipt transaction identity differs")
    expected_target = (
        {
            "root": target.get("root"),
            "starting_commit": target.get("starting_commit"),
            "observed_prestate_sha256": target.get("observed_prestate_sha256"),
        }
        if isinstance(target, dict)
        else None
    )
    expected_package = (
        {
            "id": package.get("id"),
            "version": package.get("version"),
            "manifest_sha256": package.get("manifest_sha256"),
            "migration_sha256": package.get("migration_sha256"),
        }
        if isinstance(package, dict)
        else None
    )
    if receipt.get("target") != expected_target or receipt.get("package") != expected_package:
        errors.append(f"{path}: incoming validation receipt target or package identity differs")
    if receipt.get("target_validation_profile") != packet_validation_profile or receipt.get(
        "target_validation_profile_digest"
    ) != validation_profile_digest:
        errors.append(f"{path}: incoming validation receipt profile evidence differs")
    if not isinstance(package, dict) or receipt.get("validator") != package.get(
        "validation"
    ):
        errors.append(f"{path}: incoming validation receipt validator identity differs")
    if receipt.get("packet_sha256") != packet.get("canonical_digest"):
        errors.append(f"{path}: incoming validation receipt packet digest differs")
    if not isinstance(target, dict) or target.get("root") != str(root):
        errors.append(f"{path}: incoming validation receipt target root differs")
    if packet.get("plan_sha256") != plan.get("plan_sha256"):
        errors.append(f"{path}: incoming validation receipt plan differs")
    return raw_digest, path


def validate_target_validation_receipt(
    transaction: Path,
    journal: dict,
    packet: dict,
    packet_digest: str,
    decision_raw_digest: str,
    packet_validation_profile: dict,
    validation_profile_digest: str,
    plan: dict,
    root: Path,
    pending_receipt_sha256: str,
    errors: list[str],
) -> tuple[str, Path] | None:
    """Validate the post-write target-owned record sealed by the transaction."""
    journal_artifact_path(
        journal,
        "target_validation_receipt_path",
        TARGET_VALIDATION_RECEIPT_PATH,
        "target validation receipt",
        errors,
    )
    loaded = read_transaction_json(
        transaction,
        TARGET_VALIDATION_RECEIPT_PATH,
        "target validation receipt",
        errors,
    )
    if loaded is None:
        return None
    receipt, raw_digest, path = loaded
    journal_artifact_digest_matches(
        journal,
        "target_validation_receipt_sha256",
        raw_digest,
        None,
        "target validation receipt",
        errors,
    )
    required = {
        "schema_version",
        "transaction_id",
        "plan_sha256",
        "packet_sha256",
        "decision_sha256",
        "target",
        "target_validation_profile",
        "target_validation_profile_digest",
        "pending_receipt",
        "execution",
    }
    if set(receipt) != required:
        errors.append(f"{path}: target validation receipt fields are incomplete or unexpected")
        return None
    if receipt.get("schema_version") != TARGET_VALIDATION_RECEIPT_SCHEMA:
        errors.append(f"{path}: target validation receipt schema is invalid")
    if receipt.get("transaction_id") != packet.get("transaction_id") or receipt.get(
        "plan_sha256"
    ) != packet.get("plan_sha256") or packet.get("plan_sha256") != plan.get("plan_sha256"):
        errors.append(f"{path}: target validation receipt transaction identity differs")
    if receipt.get("packet_sha256") != packet_digest:
        errors.append(f"{path}: target validation receipt packet digest differs")
    if receipt.get("decision_sha256") != decision_raw_digest:
        errors.append(f"{path}: target validation receipt decision digest differs")
    target = packet.get("target")
    expected_target = (
        {
            "root": target.get("root"),
            "starting_commit": target.get("starting_commit"),
            "observed_prestate_sha256": target.get("observed_prestate_sha256"),
        }
        if isinstance(target, dict)
        else None
    )
    if receipt.get("target") != expected_target or not isinstance(target, dict) or target.get(
        "root"
    ) != str(root):
        errors.append(f"{path}: target validation receipt target identity differs")
    if receipt.get("target_validation_profile") != packet_validation_profile or receipt.get(
        "target_validation_profile_digest"
    ) != validation_profile_digest:
        errors.append(f"{path}: target validation receipt profile evidence differs")
    if receipt.get("pending_receipt") != {
        "path": PENDING_APPLY_RECEIPT,
        "sha256": pending_receipt_sha256,
    }:
        errors.append(f"{path}: target validation receipt pending receipt identity differs")
    execution = receipt.get("execution")
    if not isinstance(execution, dict) or set(execution) != {
        "argv",
        "outcome",
        "exit_code",
        "started_at",
        "completed_at",
        "output_sha256",
        "evidence",
    }:
        errors.append(f"{path}: target validation receipt execution evidence is invalid")
    else:
        transaction_id = str(packet.get("transaction_id"))
        expected_evidence = (
            f".git/ai-context-package-apply/{transaction_id}/"
            f"{TARGET_VALIDATION_OUTPUT_PATH}"
        )
        evidence_path = transaction / TARGET_VALIDATION_OUTPUT_PATH
        if (
            execution.get("argv") != packet_validation_profile.get("argv")
            or execution.get("outcome") != "passed"
            or execution.get("exit_code") != 0
            or not iso_interval_is_ordered(
                execution.get("started_at"), execution.get("completed_at")
            )
            or not isinstance(execution.get("output_sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", execution["output_sha256"])
            or not safe_repo_reference(execution.get("evidence"))
            or execution.get("evidence") != expected_evidence
            or not evidence_path.is_file()
            or evidence_path.is_symlink()
            or is_reparse_point(evidence_path)
            or sha256_bytes(evidence_path.read_bytes())
            != execution.get("output_sha256")
        ):
            errors.append(
                f"{path}: target validation receipt execution evidence bytes differ"
            )
    return raw_digest, path


def validate_upgrade_finalization_evidence(
    root: Path,
    candidate_provenance: dict | None,
    candidate_ledger: dict | None,
    errors: list[str],
    *,
    expected_status: str = "approved",
    transaction_id: str | None = None,
    historical: bool = False,
    transaction_base: Path | None = None,
) -> dict[str, object] | None:
    """Validate the package-owned upgrade proof before provenance can advance.

    This is intentionally isolated from package-apply execution: it consumes
    only sealed transaction bytes and returns immutable identities needed for
    approved terminal finalization or retained rejected evidence.
    """
    if expected_status not in {"approved", "rejected"}:
        errors.append("upgrade transaction expected status is invalid")
        return None
    receipt_path: Path | None = None
    receipt: dict | None = None
    if expected_status == "approved" and not historical:
        receipt_path = checked_target_path(
            root, PENDING_APPLY_RECEIPT, "pending apply receipt", errors
        )
        if receipt_path is None or not receipt_path.is_file():
            errors.append("upgrade finalization requires a finalized pending apply receipt")
            return None
        receipt = load_mapping(receipt_path, errors)
        if receipt is None or receipt.get("schema_version") != "2.0.0":
            errors.append("upgrade finalization requires schema 2.0.0 pending apply receipt")
            return None
        transaction_id = receipt.get("transaction_id")
        if not isinstance(transaction_id, str) or not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
            errors.append("upgrade finalization pending receipt transaction_id is invalid")
            return None
    else:
        if not isinstance(transaction_id, str) or not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
            errors.append("upgrade transaction_id is invalid")
            return None
        if expected_status == "rejected":
            receipt_path = checked_target_path(
                root, PENDING_APPLY_RECEIPT, "pending apply receipt", errors
            )
            if receipt_path is None:
                return None
            if receipt_path.exists():
                current_receipt = load_mapping(receipt_path, errors)
                if isinstance(current_receipt, dict) and current_receipt.get(
                    "transaction_id"
                ) == transaction_id:
                    errors.append(
                        "rejected upgrade transaction must not retain its pending apply receipt"
                    )
                    return None
                receipt_path = None
    transactions = transaction_base
    if transactions is None:
        try:
            transactions = apply_transaction_directory(root)
        except TargetValidationError as exc:
            errors.append(str(exc))
            return None
    if (
        transactions is None
        or transactions.is_symlink()
        or is_reparse_point(transactions)
        or not transactions.is_dir()
    ):
        errors.append("upgrade finalization transaction directory is missing or unsafe")
        return None
    transaction = transactions / transaction_id
    if (
        transaction.is_symlink()
        or is_reparse_point(transaction)
        or not transaction.is_dir()
    ):
        errors.append("upgrade finalization transaction is missing or unsafe")
        return None
    journal_path = transaction / "journal.yaml"
    journal = (
        load_mapping(journal_path, errors)
        if journal_path.is_file() and not journal_path.is_symlink() and not is_reparse_point(journal_path)
        else None
    )
    if not isinstance(journal, dict):
        errors.append("upgrade finalization transaction journal is missing or invalid")
        return None
    expected_journal_states = (
        (
            {"finalized"}
            if historical
            else {"awaiting-target-validation", "validated", "finalized"}
        )
        if expected_status == "approved"
        else {"rejected"}
    )
    if (
        journal.get("schema_version")
        not in (
            {"ai-context-package-apply-journal/v4", "ai-context-package-apply-journal/v5"}
            if historical
            else {"ai-context-package-apply-journal/v5"}
        )
        or journal.get("state") not in expected_journal_states
    ):
        errors.append(
            "upgrade transaction journal state differs from the required v5 lifecycle"
        )
        return None
    plan_loaded = read_transaction_json(transaction, "plan.json", "sealed transaction plan", errors)
    packet_loaded = read_transaction_json(
        transaction, REMEDIATION_PACKET_PATH, "upgrade remediation packet", errors
    )
    decision_loaded = read_transaction_json(
        transaction, REMEDIATION_DECISION_PATH, "upgrade remediation decision", errors
    )
    report_path = transaction_artifact_path(
        transaction, REMEDIATION_REPORT_PATH, "upgrade remediation report", errors
    )
    if (
        plan_loaded is None
        or packet_loaded is None
        or decision_loaded is None
        or report_path is None
    ):
        return None
    plan, _, plan_path = plan_loaded
    packet, packet_raw_digest, _ = packet_loaded
    decision, decision_raw_digest, _ = decision_loaded
    unsigned_plan = dict(plan)
    declared_plan_sha = unsigned_plan.pop("plan_sha256", None)
    if (
        plan.get("schema_version") != "2.2.0"
        or declared_plan_sha != transaction_id
        or canonical_json_digest(unsigned_plan) != transaction_id
    ):
        errors.append("upgrade remediation sealed plan identity differs")
    if plan.get("upgrade_remediation_required") is not True:
        errors.append("upgrade remediation evidence is attached to a clean-install plan")
    packet_digest = canonical_document_digest(packet, "upgrade remediation packet", errors)
    decision_digest = decision_raw_digest
    try:
        report_raw = report_path.read_bytes()
    except OSError as exc:
        errors.append(f"{report_path}: upgrade remediation report is invalid: {exc}")
        return None
    report_digest = sha256_bytes(report_raw)
    if packet.get("schema_version") != REMEDIATION_PACKET_SCHEMA:
        errors.append("upgrade remediation packet schema is invalid")
    if decision.get("schema_version") != REMEDIATION_DECISION_SCHEMA:
        errors.append("upgrade remediation decision schema is invalid")
    if packet.get("transaction_id") != transaction_id or packet.get("plan_sha256") != transaction_id:
        errors.append("upgrade remediation packet transaction identity differs")
    if decision.get("transaction_id") != transaction_id or decision.get("plan_sha256") != transaction_id:
        errors.append("upgrade remediation decision transaction identity differs")
    if packet_digest is not None and decision.get("packet_sha256") != packet_digest:
        errors.append("upgrade remediation decision packet digest differs")
    if packet.get("owner_decision") is not None:
        errors.append("upgrade remediation packet owner decision must remain unsealed")
    if decision.get("status") != expected_status:
        errors.append(f"upgrade remediation decision is not {expected_status}")
    if not isinstance(decision.get("owner"), str) or not decision["owner"].strip():
        errors.append("upgrade remediation decision owner is invalid")
    if not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
        errors.append("upgrade remediation decision reason is invalid")
    if not iso_with_offset(decision.get("decided_at")) or not safe_repo_reference(
        decision.get("evidence")
    ):
        errors.append("upgrade remediation decision evidence is invalid")
    historical_terminal: dict | None = None
    if historical and expected_status == "approved":
        terminal_loaded = read_transaction_json(
            transaction, TERMINAL_RECEIPT_PATH, "terminal receipt", errors
        )
        if terminal_loaded is not None:
            historical_terminal = terminal_loaded[0]
    approved_authority: dict[str, str] | None = None
    if expected_status == "approved":
        approved_authority = candidate_authority(
            decision, "upgrade remediation decision", errors
        )
    elif decision.get("candidate_authority") is not None:
        errors.append("rejected upgrade remediation decision must not carry candidate authority")
    if (
        approved_authority is not None
        and candidate_provenance is not None
        and candidate_ledger is not None
    ):
        candidate_authority_matches_documents(
            approved_authority, candidate_provenance, candidate_ledger, errors
        )
        validate_candidate_upgrade_binding(candidate_provenance, packet, errors)
    target = packet.get("target")
    package = packet.get("package")
    if not isinstance(target, dict) or not isinstance(package, dict):
        errors.append("upgrade remediation packet target or package identity is invalid")
        return None
    proposal = packet.get("automatic_proposal")
    if not isinstance(proposal, dict):
        errors.append("upgrade remediation packet automatic proposal is invalid")
        return None
    if (
        target.get("root") != str(root)
        or target.get("starting_commit") != plan.get("target_starting_commit")
        or (
            receipt is not None
            and target.get("starting_commit") != receipt.get("target_starting_commit")
        )
    ):
        errors.append("upgrade remediation packet target identity differs")
    prestate_digest = target.get("observed_prestate_sha256")
    if not isinstance(prestate_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", prestate_digest):
        errors.append("upgrade remediation packet observed prestate digest is invalid")
    elif plan.get("target_observed_prestate_sha256") != prestate_digest or journal.get(
        "target_observed_prestate_sha256"
    ) != prestate_digest:
        errors.append("upgrade remediation packet observed prestate identity differs")
    for packet_key, plan_key in (
        ("id", "package_id"),
        ("version", "package_version"),
        ("manifest_sha256", "package_manifest_sha256"),
        ("migration_sha256", "migration_sha256"),
        ("selected_input_proof", "package_selected_input_proof"),
    ):
        if package.get(packet_key) != plan.get(plan_key):
            errors.append(f"upgrade remediation packet package {packet_key} differs")
    for packet_key, plan_key in (
        ("root", "package_root"),
        ("source", "package_source"),
        ("validation", "incoming_package_validation"),
    ):
        if package.get(packet_key) != plan.get(plan_key):
            errors.append(f"upgrade remediation packet package {packet_key} differs")
    migration = packet.get("migration")
    if not isinstance(migration, dict):
        errors.append("upgrade remediation packet migration identity is invalid")
    else:
        if migration.get("contract") != plan.get("migration_contract"):
            errors.append("upgrade remediation packet migration contract differs")
        if migration.get("selected_input") != plan.get("migration_selected_input"):
            errors.append("upgrade remediation packet migration selected input differs")
    packet_provenance = packet.get("provenance")
    if (
        not isinstance(packet_provenance, dict)
        or packet_provenance.get("source")
        != plan.get("target_provenance_source")
    ):
        errors.append("upgrade remediation packet predecessor source differs")
    if packet.get("selection") != plan.get("selection"):
        errors.append("upgrade remediation packet selection differs")
    current_provenance_raw: str | None = None
    current_provenance_canonical: str | None = None
    current_ledger_raw: str | None = None
    current_ledger_canonical: str | None = None
    if not historical:
        current_provenance_raw, current_provenance_canonical = current_authority_identity(
            root, ".dev/ai-context/provenance.yaml", errors
        )
        current_ledger_raw, current_ledger_canonical = current_authority_identity(
            root, ".dev/ai-context/customizations.yaml", errors
        )
    authority_already_advanced = (
        not historical
        and approved_authority is not None
        and current_provenance_canonical == approved_authority["provenance_sha256"]
        and current_ledger_canonical == approved_authority["customizations_sha256"]
    )
    if not historical and not authority_already_advanced:
        packet_authority_digest(
            packet.get("provenance"),
            "upgrade remediation packet provenance",
            ".dev/ai-context/provenance.yaml",
            current_provenance_raw,
            errors,
        )
        packet_authority_digest(
            packet.get("semantic_customizations"),
            "upgrade remediation packet customizations",
            ".dev/ai-context/customizations.yaml",
            current_ledger_raw,
            errors,
        )
    operation_ids = active_operation_ids(plan, plan_path, errors)
    proposal_operation_ids = proposal.get("apply_operation_ids")
    proposal_reconciliation_ids = proposal.get("reconciliation_ids")
    if proposal_operation_ids != operation_ids:
        errors.append("upgrade remediation packet operation proposal differs")
    if expected_status == "approved" and decision.get(
        "accepted_operation_ids"
    ) != proposal_operation_ids:
        errors.append("upgrade remediation decision accepted operations differ")
    if expected_status == "rejected" and decision.get("accepted_operation_ids") != []:
        errors.append("rejected upgrade remediation decision accepted operations differ")
    reconciliation_ids = decision.get("reconciliation_ids")
    if not isinstance(reconciliation_ids, list) or not all(
        isinstance(value, str) and value for value in reconciliation_ids
    ) or len(reconciliation_ids) != len(set(reconciliation_ids)):
        errors.append("upgrade remediation decision reconciliation ids are invalid")
    elif expected_status == "approved" and reconciliation_ids != proposal_reconciliation_ids:
        errors.append("upgrade remediation decision reconciliation ids differ")
    elif expected_status == "rejected" and reconciliation_ids != []:
        errors.append("rejected upgrade remediation decision reconciliation ids differ")
    if (
        expected_status == "approved"
        and candidate_provenance is not None
        and decision.get("policy_adoptions") != candidate_provenance.get("policy_adoptions")
    ):
        errors.append("upgrade remediation decision policy adoptions differ from candidate provenance")
    if expected_status == "rejected" and decision.get("policy_adoptions") is not None:
        errors.append("rejected upgrade remediation decision policy adoptions differ")
    journal_artifact_path(
        journal, "remediation_packet_path", REMEDIATION_PACKET_PATH, "upgrade remediation packet", errors
    )
    journal_artifact_path(
        journal, "remediation_report_path", REMEDIATION_REPORT_PATH, "upgrade remediation report", errors
    )
    journal_artifact_path(
        journal, "remediation_decision_path", REMEDIATION_DECISION_PATH, "upgrade remediation decision", errors
    )
    journal_artifact_digest_matches(
        journal, "remediation_packet_sha256", packet_digest or "", packet_raw_digest,
        "upgrade remediation packet", errors
    )
    journal_artifact_digest_matches(
        journal, "remediation_report_sha256", report_digest, None,
        "upgrade remediation report", errors
    )
    journal_artifact_digest_matches(
        journal, "remediation_decision_sha256", decision_digest or "", decision_raw_digest,
        "upgrade remediation decision", errors
    )
    expected_report = (
        derived_remediation_report_bytes(packet, packet_digest, errors)
        if packet_digest is not None
        else None
    )
    if expected_report is not None and report_raw != expected_report:
        errors.append("upgrade remediation report packet digest differs")
    profile = validate_target_validation_profile(
        root,
        packet,
        errors,
        require_current_target=not historical,
        require_executable_profile=expected_status == "approved" and not historical,
    )
    incoming = (
        validate_incoming_validation_receipt(
            transaction, journal, packet, profile[0], profile[1], plan, root, errors
        )
        if profile is not None
        else None
    )
    pending_receipt_sha256 = (
        sha256_bytes(receipt_path.read_bytes())
        if receipt_path is not None and receipt is not None
        else (
            historical_terminal.get("pending_receipt_sha256")
            if isinstance(historical_terminal, dict)
            else None
        )
    )
    target_validation = (
        validate_target_validation_receipt(
            transaction,
            journal,
            packet,
            packet_digest,
            decision_raw_digest,
            profile[0],
            profile[1],
            plan,
            root,
            pending_receipt_sha256,
            errors,
        )
        if (
            expected_status == "approved"
            and profile is not None
            and packet_digest is not None
            and pending_receipt_sha256 is not None
        )
        else None
    )
    if (
        errors
        or packet_digest is None
        or decision_digest is None
        or incoming is None
        or (expected_status == "approved" and target_validation is None)
        or (expected_status == "approved" and approved_authority is None)
    ):
        return None
    return {
        "transaction": transaction,
        "transaction_id": transaction_id,
        "plan_sha256": transaction_id,
        "plan": plan,
        "journal": journal,
        "packet_digest": packet_digest,
        "decision_digest": decision_digest,
        "pending_receipt_sha256": pending_receipt_sha256,
        "incoming_validation_receipt_sha256": incoming[0],
        "target_validation_receipt_sha256": (
            target_validation[0] if target_validation is not None else None
        ),
        "candidate_authority": approved_authority,
        "authority_already_advanced": authority_already_advanced,
        "historical": historical,
        "journal_path": journal_path,
    }


def validate_rejected_upgrade_transaction(
    root: Path, transaction_id: str, journal: dict, errors: list[str]
) -> None:
    """Accept retained rejection evidence only when it cannot represent a write."""
    evidence_errors: list[str] = []
    evidence = validate_upgrade_finalization_evidence(
        root,
        None,
        None,
        evidence_errors,
        expected_status="rejected",
        transaction_id=transaction_id,
        historical=True,
    )
    errors.extend(evidence_errors)
    if evidence is None:
        return
    plan = evidence.get("plan")
    if not isinstance(plan, dict):
        errors.append("rejected upgrade transaction sealed plan is invalid")
        return
    plan_path = Path(str(evidence.get("transaction", ""))) / "plan.json"
    active_ids = active_operation_ids(plan, plan_path, errors)
    expected_staging = transaction_staging_records(
        transaction_id,
        [
            operation
            for operation in (validate_sealed_operations(plan, plan_path, errors) or [])
            if operation.get("action") in {"add", "replace", "remove", "rename"}
        ],
    )
    progress_is_zero = (
        type(journal.get("transition_sequence")) is int
        and journal.get("transition_sequence") == 0
        and journal.get("next_apply_index") == 0
        and journal.get("completed_operation_ids") == []
        and journal.get("rollback_next_index") == 0
        and journal.get("rollback_completed_paths") == []
        and journal.get("rollback_start_state") is None
        and (
            journal.get("schema_version") == "ai-context-package-apply-journal/v4"
            or (
                journal.get("progress_log_path") == "progress.jsonl"
                and journal.get("progress_record_count") == 0
                and journal.get("progress_tail_sha256") is None
            )
        )
        and journal.get("final_receipt_sha256") is None
        and journal.get("terminal_receipt_path") is None
        and journal.get("terminal_receipt_sha256") is None
        and journal.get("target_validation_receipt_path") is None
        and journal.get("target_validation_receipt_sha256") is None
        and journal.get("operation_order_sha256") == canonical_json_digest(active_ids)
        and journal.get("target_staging_paths") == expected_staging
    )
    if not progress_is_zero:
        errors.append("rejected upgrade transaction progress is not zero")
    for staging in expected_staging:
        relative = staging.get("path") if isinstance(staging, dict) else None
        if not safe_target_path(relative):
            errors.append("rejected upgrade transaction staging evidence is invalid")
            break
        try:
            if target_path_without_links(root, relative).exists():
                errors.append("rejected upgrade transaction retains target staging")
                break
        except TargetValidationError as exc:
            errors.append(f"rejected upgrade transaction staging boundary is invalid: {exc}")
            break
    transaction = evidence.get("transaction")
    if isinstance(transaction, Path) and (transaction / TARGET_VALIDATION_RECEIPT_PATH).exists():
        errors.append("rejected upgrade transaction must not retain target validation receipt")


def is_historical_upgrade_transaction(
    transaction: Path, journal: dict, errors: list[str]
) -> bool:
    """Classify a retained transaction without applying upgrade rules to clean installs."""
    plan_loaded = read_transaction_json(
        transaction, "plan.json", "sealed transaction plan", errors
    )
    if plan_loaded is None:
        return False
    plan, _, _ = plan_loaded
    remediation_keys = (
        "remediation_packet_path",
        "remediation_packet_sha256",
        "remediation_report_path",
        "remediation_report_sha256",
        "remediation_decision_path",
        "remediation_decision_sha256",
        "incoming_validation_receipt_path",
        "incoming_validation_receipt_sha256",
        "target_validation_receipt_path",
        "target_validation_receipt_sha256",
        "target_observed_prestate_sha256",
    )
    required = plan.get("upgrade_remediation_required") is True
    if not required and any(journal.get(key) is not None for key in remediation_keys):
        errors.append("clean-install transaction has unexpected remediation evidence")
    return required


def validate_historical_finalized_upgrade_transaction(
    root: Path,
    transaction_id: str,
    journal: dict,
    errors: list[str],
    *,
    transaction_base: Path | None = None,
) -> bool:
    """Validate a retained completed upgrade without treating later authority as drift."""
    transaction = transaction_base
    if transaction is None:
        try:
            transaction = apply_transaction_directory(root)
        except TargetValidationError as exc:
            errors.append(str(exc))
            return False
    if transaction is None:
        errors.append("historical upgrade transaction directory is missing")
        return False
    transaction = transaction / transaction_id
    if not is_historical_upgrade_transaction(transaction, journal, errors):
        return False
    evidence_errors: list[str] = []
    evidence = validate_upgrade_finalization_evidence(
        root,
        None,
        None,
        evidence_errors,
        transaction_id=transaction_id,
        historical=True,
        transaction_base=transaction_base,
    )
    errors.extend(evidence_errors)
    if evidence is not None:
        validate_terminal_receipt_invariant(
            root, evidence, errors, require_current_authority=False
        )
    return True


def write_terminal_receipt(
    evidence: dict[str, object], provenance_sha256: str, customizations_sha256: str
) -> tuple[Path, str, bool]:
    """Create one immutable finalization receipt, or prove a prior identical one."""
    transaction = evidence["transaction"]
    if not isinstance(transaction, Path):
        raise TargetValidationError("upgrade finalization transaction evidence is invalid")
    receipt_path = transaction / TERMINAL_RECEIPT_PATH
    if receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise TargetValidationError("terminal receipt path is unsafe")
    unsigned = {
        "schema_version": TERMINAL_RECEIPT_SCHEMA,
        "transaction_id": evidence["transaction_id"],
        "plan_sha256": evidence["plan_sha256"],
        "packet_digest": evidence["packet_digest"],
        "decision_digest": evidence["decision_digest"],
        "pending_receipt_sha256": evidence["pending_receipt_sha256"],
        "target_validation_receipt_sha256": evidence[
            "target_validation_receipt_sha256"
        ],
        "provenance_sha256": provenance_sha256,
        "customizations_sha256": customizations_sha256,
        "outcome": "finalized",
    }
    document = {**unsigned, "digest": canonical_json_digest(unsigned)}
    encoded = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    if receipt_path.exists():
        try:
            existing_bytes = receipt_path.read_bytes()
            existing = json.loads(existing_bytes.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TargetValidationError(f"terminal receipt is invalid: {exc}") from exc
        if existing_bytes != encoded or existing != document:
            raise TargetValidationError("terminal receipt differs from finalization evidence")
        return receipt_path, sha256_bytes(existing_bytes), False
    descriptor: int | None = None
    try:
        descriptor = os.open(
            receipt_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        return write_terminal_receipt(evidence, provenance_sha256, customizations_sha256)
    except OSError as exc:
        raise TargetValidationError(f"cannot write terminal receipt: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    return receipt_path, sha256_bytes(encoded), True


def link_terminal_receipt_in_journal(
    evidence: dict[str, object], terminal_sha256: str
) -> None:
    """Finalize the validated journal while binding immutable terminal evidence."""
    journal_path = evidence.get("journal_path")
    if not isinstance(journal_path, Path):
        raise TargetValidationError("upgrade finalization journal evidence is invalid")
    errors: list[str] = []
    journal = load_mapping(journal_path, errors)
    if journal is None:
        raise TargetValidationError("; ".join(errors))
    current_path = journal.get("terminal_receipt_path")
    current_sha = journal.get("terminal_receipt_sha256")
    if current_path == TERMINAL_RECEIPT_PATH and current_sha == terminal_sha256:
        if journal.get("state") != "finalized":
            raise TargetValidationError("terminal receipt journal state differs")
        return
    if current_path is not None or current_sha is not None:
        raise TargetValidationError("terminal receipt journal binding differs")
    if journal.get("state") != "validated":
        raise TargetValidationError("terminal receipt requires a validated upgrade transaction")
    journal["terminal_receipt_path"] = TERMINAL_RECEIPT_PATH
    journal["terminal_receipt_sha256"] = terminal_sha256
    journal["state"] = "finalized"
    journal["transition_sequence"] = int(journal.get("transition_sequence", 0)) + 1
    candidate = journal_path.with_name(f".{journal_path.name}.terminal.candidate")
    try:
        candidate.write_text(
            yaml.safe_dump(journal, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )
        os.replace(candidate, journal_path)
    except OSError as exc:
        raise TargetValidationError(f"cannot bind terminal receipt in journal: {exc}") from exc
    finally:
        if candidate.exists():
            candidate.unlink()


def validate_terminal_receipt_invariant(
    root: Path,
    evidence: dict[str, object],
    errors: list[str],
    *,
    require_current_authority: bool = True,
) -> None:
    """Validate the immutable terminal record for current or retained upgrades."""
    transaction = evidence.get("transaction")
    journal = evidence.get("journal")
    authority = evidence.get("candidate_authority")
    if not isinstance(transaction, Path) or not isinstance(journal, dict) or not isinstance(
        authority, dict
    ):
        errors.append("upgrade terminal receipt evidence is invalid")
        return
    if journal.get("state") != "finalized":
        errors.append("upgrade terminal receipt journal state is not finalized")
    terminal_path_value = journal.get("terminal_receipt_path")
    terminal_digest = journal.get("terminal_receipt_sha256")
    provenance_raw: str | None = None
    customizations_raw: str | None = None
    if require_current_authority:
        provenance_raw, provenance_canonical = current_authority_identity(
            root, ".dev/ai-context/provenance.yaml", errors
        )
        customizations_raw, customizations_canonical = current_authority_identity(
            root, ".dev/ai-context/customizations.yaml", errors
        )
        expected_provenance = authority.get("provenance_sha256")
        expected_customizations = authority.get("customizations_sha256")
        advanced_provenance = provenance_canonical == expected_provenance
        advanced_customizations = customizations_canonical == expected_customizations
        if not advanced_provenance and not advanced_customizations:
            if terminal_path_value is not None or terminal_digest is not None:
                errors.append("upgrade terminal receipt is bound before authority advancement")
            return
        if not advanced_provenance or not advanced_customizations:
            errors.append("upgrade authority advancement is partial")
            return
    if terminal_path_value != TERMINAL_RECEIPT_PATH or not isinstance(
        terminal_digest, str
    ) or not re.fullmatch(r"[0-9a-f]{64}", terminal_digest):
        errors.append("upgrade authority advancement lacks terminal receipt journal binding")
        return
    loaded = read_transaction_json(
        transaction, TERMINAL_RECEIPT_PATH, "terminal receipt", errors
    )
    if loaded is None:
        return
    terminal, raw_digest, path = loaded
    if raw_digest != terminal_digest:
        errors.append(f"{path}: terminal receipt journal SHA-256 differs")
    required = {
        "schema_version",
        "transaction_id",
        "plan_sha256",
        "packet_digest",
        "decision_digest",
        "pending_receipt_sha256",
        "target_validation_receipt_sha256",
        "provenance_sha256",
        "customizations_sha256",
        "outcome",
        "digest",
    }
    if set(terminal) != required:
        errors.append(f"{path}: terminal receipt fields are incomplete or unexpected")
        return
    unsigned = dict(terminal)
    declared_digest = unsigned.pop("digest", None)
    if declared_digest != canonical_json_digest(unsigned):
        errors.append(f"{path}: terminal receipt digest differs")
    expected = {
        "schema_version": TERMINAL_RECEIPT_SCHEMA,
        "transaction_id": evidence.get("transaction_id"),
        "plan_sha256": evidence.get("plan_sha256"),
        "packet_digest": evidence.get("packet_digest"),
        "decision_digest": evidence.get("decision_digest"),
        "pending_receipt_sha256": evidence.get("pending_receipt_sha256"),
        "target_validation_receipt_sha256": evidence.get(
            "target_validation_receipt_sha256"
        ),
        "outcome": "finalized",
    }
    if any(terminal.get(key) != value for key, value in expected.items()):
        errors.append(f"{path}: terminal receipt finalization identity differs")
    if require_current_authority:
        if (
            terminal.get("provenance_sha256") != provenance_raw
            or terminal.get("customizations_sha256") != customizations_raw
        ):
            errors.append(f"{path}: terminal receipt authority bytes differ")
    elif not all(
        isinstance(terminal.get(key), str)
        and re.fullmatch(r"[0-9a-f]{64}", terminal[key])
        for key in ("provenance_sha256", "customizations_sha256")
    ):
        errors.append(f"{path}: terminal receipt authority bytes are invalid")


def has_pending_v5_upgrade_transaction(root: Path) -> bool:
    """Detect the one resumable v5 finalization boundary without treating it as valid."""
    errors: list[str] = []
    receipt_path = checked_target_path(
        root, PENDING_APPLY_RECEIPT, "pending apply receipt", errors
    )
    if receipt_path is None or not receipt_path.is_file():
        return False
    receipt = load_mapping(receipt_path, errors)
    transaction_id = receipt.get("transaction_id") if isinstance(receipt, dict) else None
    if not isinstance(transaction_id, str) or not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
        return False
    try:
        transactions = apply_transaction_directory(root)
    except TargetValidationError:
        return False
    if transactions is None:
        return False
    transaction = transactions / transaction_id
    journal_path = transaction / "journal.yaml"
    journal = (
        load_mapping(journal_path, errors)
        if journal_path.is_file()
        and not journal_path.is_symlink()
        and not is_reparse_point(journal_path)
        else None
    )
    plan_path = transaction / "plan.json"
    if (
        not plan_path.is_file()
        or plan_path.is_symlink()
        or is_reparse_point(plan_path)
    ):
        return False
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(plan, dict):
        return False
    unsigned = dict(plan)
    declared_digest = unsigned.pop("plan_sha256", None)
    plan_is_upgrade = (
        declared_digest == transaction_id
        and canonical_json_digest(unsigned) == transaction_id
        and plan.get("schema_version") == "2.2.0"
        and plan.get("upgrade_remediation_required") is True
        and isinstance(plan.get("previous_version"), str)
        and bool(plan.get("previous_version"))
    )
    return (
        isinstance(journal, dict)
        and journal.get("schema_version") == "ai-context-package-apply-journal/v5"
        and journal.get("state")
        in {"awaiting-target-validation", "validated", "finalized"}
        and plan_is_upgrade
    )


def validate_string_references(
    values: object, label: str, errors: list[str], allow_empty: bool = True
) -> list[str]:
    if not isinstance(values, list) or (
        not allow_empty and not values
    ) or not all(safe_repo_reference(value) for value in values):
        errors.append(f"{label} must be a safe repository-relative reference list")
        return []
    if len(values) != len(set(values)):
        errors.append(f"{label} must not contain duplicates")
    return list(values)


def validate_source(source: object, label: str, errors: list[str]) -> str | None:
    if not isinstance(source, dict):
        errors.append(f"{label}: source must be a mapping")
        return None
    version = source.get("version")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        errors.append(f"{label}: source.version must be vMAJOR.MINOR.PATCH")
        return None
    if source.get("release_id") != f"REL-{version}":
        errors.append(f"{label}: source.release_id must be REL-{version}")
    if source.get("tag") != version:
        errors.append(f"{label}: source.tag must equal source.version")
    if not isinstance(source.get("repository"), str) or not source["repository"].strip():
        errors.append(f"{label}: source.repository is required")
    if not isinstance(source.get("commit"), str) or not SHA_RE.fullmatch(
        source["commit"]
    ):
        errors.append(f"{label}: source.commit must be a full lowercase Git SHA")
    return version


def validate_selection(selection: object, label: str, errors: list[str]) -> None:
    if not isinstance(selection, dict):
        errors.append(f"{label}: selection must be a mapping")
        return
    if selection.get("release_model") != "single-versioned-componentized-release":
        errors.append(f"{label}: selection.release_model is invalid")
    if set(selection.get("mandatory_components", [])) != {
        "software-development-core",
        "ai-context-lifecycle-core",
    }:
        errors.append(
            f"{label}: selection.mandatory_components must contain both mandatory cores"
        )
    profiles = selection.get("profiles")
    if (
        not isinstance(profiles, list)
        or not profiles
        or len(profiles) != len(set(profiles))
        or not all(is_profile_slug(item) for item in profiles)
    ):
        errors.append(
            f"{label}: selection.profiles must be unique lowercase single-segment slugs"
        )
    providers = selection.get("providers")
    backlog = providers.get("repo-backlog") if isinstance(providers, dict) else None
    if (
        not isinstance(backlog, dict)
        or not isinstance(backlog.get("enabled"), bool)
        or backlog.get("preservation") != "preserve-existing-if-recorded"
    ):
        errors.append(f"{label}: selection.providers.repo-backlog is invalid")


def validate_unresolved(items: object, label: str, errors: list[str]) -> None:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return
    ids: set[str] = set()
    for index, item in enumerate(items):
        item_label = f"{label}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_label} must be a mapping")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id or item_id in ids:
            errors.append(f"{item_label}.id must be unique and non-empty")
        else:
            ids.add(item_id)
        if not isinstance(item.get("reason"), str) or not item["reason"]:
            errors.append(f"{item_label}.reason is required")
        if "legacy_evidence" in item and item.get("reason") != "legacy-local-override":
            errors.append(
                f"{item_label}: legacy evidence requires reason legacy-local-override"
            )
        if item.get("reason") == "legacy-local-override" and not isinstance(
            item.get("legacy_evidence"), dict
        ):
            errors.append(
                f"{item_label}: legacy-local-override requires preserved legacy evidence"
            )
        validate_string_references(
            item.get("paths"), f"{item_label}.paths", errors, allow_empty=False
        )


def commit_subject_grammar_adoption(
    provenance: object, label: str, errors: list[str]
) -> dict | None:
    """Validate the optional provenance record without making it authority yet."""
    if not isinstance(provenance, dict):
        return None
    adoptions = provenance.get("policy_adoptions")
    if adoptions is None:
        return None
    if not isinstance(adoptions, dict) or set(adoptions) != {
        "commit_subject_grammar"
    }:
        errors.append(f"{label}: policy_adoptions is invalid")
        return None
    adoption = adoptions.get("commit_subject_grammar")
    if not isinstance(adoption, dict) or set(adoption) != {
        "policy_id",
        "legacy_history_tip",
        "adopted_at",
        "incoming_policy_sha256",
        "decision_evidence",
    }:
        errors.append(f"{label}: commit subject grammar adoption is invalid")
        return None
    if adoption.get("policy_id") != COMMIT_SUBJECT_GRAMMAR_POLICY_ID:
        errors.append(f"{label}: commit subject grammar adoption policy_id differs")
    if not isinstance(adoption.get("legacy_history_tip"), str) or not SHA_RE.fullmatch(
        adoption["legacy_history_tip"]
    ):
        errors.append(
            f"{label}: commit subject grammar adoption legacy_history_tip is invalid"
        )
    if not iso_with_offset(adoption.get("adopted_at")):
        errors.append(
            f"{label}: commit subject grammar adoption adopted_at must use ISO 8601 with an offset"
        )
    if not isinstance(adoption.get("incoming_policy_sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", adoption["incoming_policy_sha256"]
    ):
        errors.append(
            f"{label}: commit subject grammar adoption incoming_policy_sha256 is invalid"
        )
    if not safe_repo_reference(adoption.get("decision_evidence")):
        errors.append(
            f"{label}: commit subject grammar adoption decision_evidence is invalid"
        )
    return adoption


def validate_commit_subject_grammar_adoption_target(
    root: Path, provenance: object, label: str, errors: list[str]
) -> None:
    """Bind structurally valid prospective adoption to installed bytes and history."""
    adoption = commit_subject_grammar_adoption(provenance, label, errors)
    if adoption is None:
        return
    policy_path = checked_target_path(
        root,
        COMMIT_SUBJECT_GRAMMAR_POLICY_PATH,
        "commit subject grammar policy",
        errors,
    )
    if policy_path is None:
        return
    if not policy_path.is_file():
        errors.append(
            f"{label}: commit subject grammar policy is absent at {COMMIT_SUBJECT_GRAMMAR_POLICY_PATH}"
        )
    elif hashlib.sha256(policy_path.read_bytes()).hexdigest() != adoption.get(
        "incoming_policy_sha256"
    ):
        errors.append(
            f"{label}: commit subject grammar adoption incoming policy SHA-256 differs"
        )
    tip = adoption.get("legacy_history_tip")
    if not isinstance(tip, str) or not SHA_RE.fullmatch(tip):
        return
    try:
        resolved = subprocess.run(
            ["git", "rev-parse", "--verify", f"{tip}^{{commit}}"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        reachable = subprocess.run(
            ["git", "merge-base", "--is-ancestor", tip, "HEAD"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        errors.append(
            f"{label}: cannot inspect commit subject grammar adoption history: {exc}"
        )
        return
    if resolved.returncode != 0:
        errors.append(
            f"{label}: commit subject grammar adoption legacy_history_tip does not resolve"
        )
    elif reachable.returncode != 0:
        errors.append(
            f"{label}: commit subject grammar adoption legacy_history_tip is not reachable from target HEAD"
        )


def validate_manifest(path: Path, errors: list[str]) -> None:
    data = load_mapping(path, errors)
    if data is None:
        return
    if data.get("schema_version") != "2.0":
        errors.append(f"{path}: schema_version must be 2.0")
        return
    version = validate_source(data.get("source"), str(path), errors)
    commit_subject_grammar_adoption(data, str(path), errors)
    installation = data.get("installation")
    if not isinstance(installation, dict) or not iso_with_offset(
        installation.get("imported_at")
    ):
        errors.append(
            f"{path}: installation.imported_at must use ISO 8601 with an offset"
        )
    validate_selection(data.get("selection"), str(path), errors)
    customizations = data.get("customizations")
    if (
        not isinstance(customizations, dict)
        or customizations.get("ledger") != ".dev/ai-context/customizations.yaml"
        or customizations.get("schema_version") != "1.0"
    ):
        errors.append(f"{path}: customizations ledger contract is invalid")
    effective_rules = data.get("effective_rules")
    if effective_rules is not None and effective_rules != PROVENANCE_EFFECTIVE_RULES_LINKAGE:
        errors.append(f"{path}: effective_rules linkage is invalid")
    reconciliation = data.get("reconciliation")
    if not isinstance(reconciliation, dict):
        errors.append(f"{path}: reconciliation must be a mapping")
    else:
        validate_unresolved(
            reconciliation.get("unresolved"),
            f"{path}: reconciliation.unresolved",
            errors,
        )
    migration = data.get("last_migration")
    if (
        not isinstance(migration, dict)
        or migration.get("status") != "completed"
        or migration.get("to_version") != version
        or not iso_with_offset(migration.get("completed_at"))
        or not isinstance(migration.get("evidence"), str)
        or not migration["evidence"].strip()
    ):
        errors.append(
            f"{path}: completed last_migration must match source and retain evidence"
        )


def validate_audit(
    value: object,
    label: str,
    errors: list[str],
    require_verified: bool,
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be a mapping")
        return
    status = value.get("status")
    if status not in {"verified", "finding", "not-run"}:
        errors.append(f"{label}.status is invalid")
    assessment = value.get("assessment_id")
    if assessment is not None and (
        not isinstance(assessment, str) or not ASSESSMENT_ID_RE.fullmatch(assessment)
    ):
        errors.append(f"{label}.assessment_id is invalid")
    evidence = value.get("evidence")
    if status == "verified" and (
        assessment is None or not safe_repo_reference(evidence)
    ):
        errors.append(f"{label}: verified audit requires assessment and evidence")
    if require_verified and status != "verified":
        errors.append(f"{label}: finalized customization requires verified audit")


def validate_customizations(
    path: Path, errors: list[str], require_finalized: bool = True
) -> None:
    data = load_mapping(path, errors)
    if data is None:
        return
    if data.get("schema_version") != "1.0":
        errors.append(f"{path}: schema_version must be 1.0")
    entries = data.get("customizations")
    if not isinstance(entries, list):
        errors.append(f"{path}: customizations must be a list")
        return
    ids = {
        item.get("id")
        for item in entries
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    seen: set[str] = set()
    for index, item in enumerate(entries):
        label = f"{path}: customizations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        customization_id = item.get("id")
        if (
            not isinstance(customization_id, str)
            or not CUSTOMIZATION_ID_RE.fullmatch(customization_id)
            or customization_id in seen
        ):
            errors.append(f"{label}.id must be a unique stable CUST-* ID")
        else:
            seen.add(customization_id)
        keys = list(item)
        if "subject" not in keys or "paths" not in keys or keys.index("subject") > keys.index(
            "paths"
        ):
            errors.append(f"{label}: subject identity must appear before paths")
        subject = item.get("subject")
        if (
            not isinstance(subject, dict)
            or subject.get("kind") not in SUBJECT_KINDS
            or not isinstance(subject.get("id"), str)
            or not subject["id"].strip()
        ):
            errors.append(f"{label}.subject must identify a capability, rule, or contract")
        if item.get("relationship") not in RELATIONSHIPS:
            errors.append(f"{label}.relationship is invalid")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append(f"{label}.reason must be a non-empty string")
        validate_string_references(
            item.get("paths"), f"{label}.paths", errors, allow_empty=False
        )
        base = item.get("base_framework")
        if not isinstance(base, dict):
            errors.append(f"{label}.base_framework must be a mapping")
        else:
            if not isinstance(base.get("version"), str) or not VERSION_RE.fullmatch(
                base["version"]
            ):
                errors.append(f"{label}.base_framework.version is invalid")
            if not isinstance(base.get("commit"), str) or not SHA_RE.fullmatch(
                base["commit"]
            ):
                errors.append(f"{label}.base_framework.commit is invalid")
            validate_string_references(
                base.get("evidence"),
                f"{label}.base_framework.evidence",
                errors,
                allow_empty=False,
            )
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, dict):
            errors.append(f"{label}.dependencies must be a mapping")
        else:
            dependency_ids = dependencies.get("customization_ids")
            if not isinstance(dependency_ids, list) or not all(
                isinstance(value, str) for value in dependency_ids
            ):
                errors.append(f"{label}.dependencies.customization_ids must be a list")
            else:
                for dependency_id in dependency_ids:
                    if dependency_id == customization_id:
                        errors.append(f"{label}: customization cannot depend on itself")
                    elif dependency_id not in ids:
                        errors.append(
                            f"{label}: missing customization dependency {dependency_id}"
                        )
            subject_refs = dependencies.get("subject_refs")
            if not isinstance(subject_refs, list) or not all(
                isinstance(value, str)
                and re.fullmatch(r"(?:capability|rule|contract):[^:\s]+", value)
                for value in subject_refs
            ):
                errors.append(
                    f"{label}.dependencies.subject_refs must use kind:identity"
                )
        decision = item.get("decision_evidence")
        decision_refs: list[str] = []
        if not isinstance(decision, dict):
            errors.append(f"{label}.decision_evidence must be a mapping")
        else:
            for field in ("requirements", "adrs", "workflows"):
                decision_refs.extend(
                    validate_string_references(
                        decision.get(field),
                        f"{label}.decision_evidence.{field}",
                        errors,
                    )
                )
        if not decision_refs:
            errors.append(
                f"{label}.decision_evidence requires a requirement, ADR, or workflow"
            )
        owner = item.get("owner_reconciliation")
        owner_status = owner.get("status") if isinstance(owner, dict) else None
        if not isinstance(owner, dict) or owner_status not in {
            "approved",
            "pending",
            "rejected",
        }:
            errors.append(f"{label}.owner_reconciliation is invalid")
        elif not {"status", "owner", "decided_at", "evidence"}.issubset(owner):
            errors.append(f"{label}.owner_reconciliation is incomplete")
        elif not isinstance(owner.get("owner"), str) or not owner["owner"].strip():
            errors.append(f"{label}.owner_reconciliation.owner is required")
        elif owner_status in {"approved", "rejected"}:
            if (
                not iso_with_offset(owner.get("decided_at"))
                or not safe_repo_reference(owner.get("evidence"))
            ):
                errors.append(
                    f"{label}: decided owner reconciliation requires time and evidence"
                )
        disposition = item.get("disposition")
        if disposition not in DISPOSITIONS:
            errors.append(f"{label}.disposition is invalid")
        finalized = require_finalized and disposition != "unresolved"
        validate_audit(
            item.get("active_context_audit"),
            f"{label}.active_context_audit",
            errors,
            finalized,
        )
        incoming = item.get("incoming")
        if (
            not isinstance(incoming, dict)
            or not isinstance(incoming.get("version"), str)
            or not VERSION_RE.fullmatch(incoming["version"])
            or incoming.get("status") not in EQUIVALENCE
            or not safe_repo_reference(incoming.get("evidence"))
        ):
            errors.append(f"{label}.incoming is invalid")
        validate_audit(
            item.get("post_upgrade_audit"),
            f"{label}.post_upgrade_audit",
            errors,
            finalized or disposition in {"retire", "supersede"},
        )
        if (
            finalized or disposition in {"retire", "supersede"}
        ) and owner_status != "approved":
            errors.append(
                f"{label}: finalized, retired, or superseded customization requires approved owner reconciliation"
            )
        validation = item.get("validation")
        if not isinstance(validation, list) or not validation or not all(
            isinstance(value, str) and value.strip() for value in validation
        ):
            errors.append(f"{label}.validation must be non-empty")


def legacy_override_reconciliation(manifest: dict) -> list[dict]:
    if manifest.get("schema_version") != "1.0":
        raise TargetValidationError("legacy conversion requires schema_version 1.0")
    overrides = manifest.get("local_overrides")
    if not isinstance(overrides, list):
        raise TargetValidationError("legacy local_overrides must be a list")
    unresolved: list[dict] = []
    for index, override in enumerate(overrides):
        if not isinstance(override, dict):
            raise TargetValidationError(f"legacy local_overrides[{index}] is invalid")
        if not isinstance(override.get("id"), str) or not override["id"]:
            raise TargetValidationError(
                f"legacy local_overrides[{index}].id is invalid"
            )
        paths = override.get("paths")
        if not isinstance(paths, list) or not paths or not all(
            safe_repo_reference(path) for path in paths
        ):
            raise TargetValidationError(
                f"legacy local_overrides[{index}].paths is invalid"
            )
        unresolved.append(
            {
                "id": override.get("id"),
                "reason": "legacy-local-override",
                "paths": list(paths),
                "legacy_evidence": {
                    key: override.get(key)
                    for key in ("owner", "reason", "disposition")
                    if key in override
                },
            }
        )
    return unresolved


def validate_target(
    root: Path,
    manifest: Path | None = None,
    require_finalized: bool = True,
    require_effective_rules: bool = False,
) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    validate_pending_apply_receipt(root, errors)
    provenance = root / ".dev/ai-context/provenance.yaml"
    legacy = root / ".dev/AI-CONTEXT-SOURCE.yaml"
    if provenance.is_file() and legacy.is_file():
        errors.append(
            f"{root}: provenance.yaml and AI-CONTEXT-SOURCE.yaml cannot both be active"
        )
    selected = manifest or (provenance if provenance.is_file() else None)
    if selected is None:
        errors.append(f"{root}: expected .dev/ai-context/provenance.yaml")
        return errors
    validate_manifest(selected, errors)
    selected_provenance = load_mapping(selected, errors)
    if selected_provenance is not None:
        validate_commit_subject_grammar_adoption_target(
            root, selected_provenance, str(selected), errors
        )
    ledger = root / ".dev/ai-context/customizations.yaml"
    if not ledger.is_file():
        errors.append(f"{root}: provenance schema 2 requires customizations.yaml")
    else:
        validate_customizations(ledger, errors, require_finalized)
    effective_state = root / EFFECTIVE_STATE_PATH
    if effective_state.is_file() and not effective_state.is_symlink():
        errors.extend(validate_effective_rule_state(root, require_packets=True))
    elif effective_state.is_symlink() or effective_state.exists():
        errors.append(
            f"{root}: target effective state path exists but is not a regular file"
        )
    elif require_effective_rules:
        errors.append(f"{root}: action-ready target requires {EFFECTIVE_STATE_PATH}")
    return errors


def effective_rule_readiness(root: Path) -> dict[str, object]:
    """Report whether routine actions may consume target-effective rule packets.

    Structural provenance initialization deliberately does not fabricate an empty
    effective state.  This derived result makes that unresolved state visible
    without turning a valid legacy/provenance-only target into a false success
    for an action skill.
    """
    root = root.resolve()
    state = root / EFFECTIVE_STATE_PATH
    if state.is_symlink() or not state.is_file():
        return {
            "action_ready": False,
            "status": "unresolved",
            "reason": "effective-rule-state-missing",
            "path": EFFECTIVE_STATE_PATH,
        }
    errors = validate_effective_rule_state(root, require_packets=True)
    if errors:
        return {
            "action_ready": False,
            "status": "stale",
            "reason": "effective-rule-state-invalid",
            "path": EFFECTIVE_STATE_PATH,
            "errors": errors,
        }
    return {
        "action_ready": True,
        "status": "ready",
        "path": EFFECTIVE_STATE_PATH,
    }


def credible_source(source: object) -> bool:
    errors: list[str] = []
    validate_source(source, "initialization", errors)
    return not errors


def build_initialization_documents(
    source: dict,
    selection: dict,
    imported_at: str,
) -> tuple[dict, dict]:
    errors: list[str] = []
    version = validate_source(source, "initialization", errors)
    validate_selection(selection, "initialization", errors)
    if not iso_with_offset(imported_at):
        errors.append("initialization: imported_at must use ISO 8601 with an offset")
    if errors or version is None:
        raise TargetValidationError("; ".join(errors))
    provenance = {
        "schema_version": "2.0",
        "source": source,
        "installation": {
            "initialized_by": "ai-context-init",
            "imported_at": imported_at,
            "last_upgraded_at": None,
        },
        "selection": selection,
        "customizations": {
            "ledger": ".dev/ai-context/customizations.yaml",
            "schema_version": "1.0",
        },
        "effective_rules": dict(PROVENANCE_EFFECTIVE_RULES_LINKAGE),
        "previous_source": None,
        "reconciliation": {"unresolved": []},
        "last_migration": {
            "status": "completed",
            "from_version": None,
            "to_version": version,
            "completed_at": imported_at,
            "evidence": "credible-source-evidence",
        },
    }
    return provenance, {"schema_version": "1.0", "customizations": []}


def finalize_context(
    root: Path,
    provenance: dict,
    ledger: dict,
    require_finalized: bool = True,
    allow_existing: bool = True,
    effective_state_candidate: dict | None = None,
    effective_resolver_evidence: list[str] | None = None,
) -> dict:
    root = root.resolve()
    for relative in (
        ".dev/AI-CONTEXT-SOURCE.yaml",
        ".dev/ai-context/provenance.yaml",
        ".dev/ai-context/customizations.yaml",
        EFFECTIVE_STATE_PATH,
        ".dev/ai-context/effective-rule-packets",
    ):
        target_path_without_links(root, relative)
    context = root / ".dev/ai-context"
    legacy = root / ".dev/AI-CONTEXT-SOURCE.yaml"
    provenance_path = context / "provenance.yaml"
    ledger_path = context / "customizations.yaml"
    if legacy.is_file():
        raise TargetValidationError("legacy provenance must be reconciled before finalization")
    if provenance_path.exists() and not allow_existing:
        raise TargetValidationError("component-aware provenance already exists")
    existing_provenance: dict | None = None
    if provenance_path.is_file():
        existing_errors: list[str] = []
        existing_provenance = load_mapping(provenance_path, existing_errors)
        if existing_provenance is None:
            raise TargetValidationError("; ".join(existing_errors))
    existing_ledger: dict | None = None
    if ledger_path.is_file():
        existing_errors = []
        existing_ledger = load_mapping(ledger_path, existing_errors)
        if existing_ledger is None:
            raise TargetValidationError("; ".join(existing_errors))
    elif ledger_path.exists():
        raise TargetValidationError("semantic customizations authority is not a regular file")
    if (effective_state_candidate is None) != (effective_resolver_evidence is None):
        raise TargetValidationError(
            "effective state candidate and resolver evidence must be supplied together"
        )
    existing_effective_state = root / EFFECTIVE_STATE_PATH
    if existing_effective_state.exists() or existing_effective_state.is_symlink():
        if effective_state_candidate is None:
            raise TargetValidationError(
                "finalization with existing effective state requires regeneration candidate and resolver evidence"
            )
    if effective_state_candidate is not None:
        existing_linkage = provenance.get("effective_rules")
        if (
            existing_linkage is not None
            and existing_linkage != PROVENANCE_EFFECTIVE_RULES_LINKAGE
        ):
            raise TargetValidationError("effective_rules linkage is invalid")
        provenance = {
            **provenance,
            "effective_rules": dict(PROVENANCE_EFFECTIVE_RULES_LINKAGE),
        }
    requires_upgrade_evidence = (
        existing_provenance is not None
        and (
            existing_provenance.get("source") != provenance.get("source")
            or existing_provenance.get("policy_adoptions")
            != provenance.get("policy_adoptions")
            or has_pending_v5_upgrade_transaction(root)
        )
    )
    pending_errors: list[str] = []
    validate_pending_apply_receipt(
        root, pending_errors, enforce_terminal_invariants=False
    )
    if pending_errors:
        raise TargetValidationError("; ".join(pending_errors))
    upgrade_evidence: dict[str, object] | None = None
    if requires_upgrade_evidence:
        upgrade_errors: list[str] = []
        upgrade_evidence = validate_upgrade_finalization_evidence(
            root, provenance, ledger, upgrade_errors
        )
        if upgrade_errors or upgrade_evidence is None:
            raise TargetValidationError(
                "; ".join(upgrade_errors)
                if upgrade_errors
                else "upgrade finalization evidence is incomplete"
            )
    context.mkdir(parents=True, exist_ok=True)
    temporary_paths: list[Path] = []
    try:
        documents = ((provenance_path, provenance), (ledger_path, ledger))
        for destination, document in documents:
            handle = tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                delete=False,
                dir=context,
                prefix=f".{destination.name}.",
                suffix=".candidate",
            )
            with handle:
                yaml.safe_dump(document, handle, sort_keys=False, allow_unicode=True)
            temporary_paths.append(Path(handle.name))
        errors: list[str] = []
        validate_manifest(temporary_paths[0], errors)
        validate_customizations(temporary_paths[1], errors, require_finalized)
        validate_commit_subject_grammar_adoption_target(
            root, provenance, str(provenance_path), errors
        )
        if errors:
            raise TargetValidationError("; ".join(errors))
        previous = {
            path: path.read_bytes() if path.is_file() else None
            for path in (provenance_path, ledger_path)
        }
        terminal_path: Path | None = None
        terminal_created = False
        try:
            authority_already_advanced = bool(
                upgrade_evidence is not None
                and upgrade_evidence.get("authority_already_advanced") is True
            )
            if not authority_already_advanced:
                os.replace(temporary_paths[1], ledger_path)
                os.replace(temporary_paths[0], provenance_path)
            if effective_state_candidate is not None:
                state, packets = build_effective_state_and_packets(
                    root,
                    effective_state_candidate,
                    resolver_evidence=effective_resolver_evidence or [],
                )
                # Terminal receipt and journal binding are still pending.  Keep the
                # complete effective-publication surface in this transaction's
                # in-process rollback set, including routes that did not exist
                # before publication.
                for relative in (
                    EFFECTIVE_STATE_PATH,
                    *sorted(packets, key=lambda value: value.encode("utf-8")),
                ):
                    path = target_path_without_links(root, relative)
                    if path.is_file():
                        previous[path] = path.read_bytes()
                    elif not path.exists():
                        previous[path] = None
                write_effective_state_and_packets(root, state, packets)
            if upgrade_evidence is not None:
                terminal_path, terminal_sha256, terminal_created = write_terminal_receipt(
                    upgrade_evidence,
                    sha256_bytes(provenance_path.read_bytes()),
                    sha256_bytes(ledger_path.read_bytes()),
                )
                link_terminal_receipt_in_journal(upgrade_evidence, terminal_sha256)
        except Exception:
            if terminal_created and terminal_path is not None and terminal_path.exists():
                terminal_path.unlink()
            for path, content in previous.items():
                if content is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.write_bytes(content)
            raise
    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()
    result = {
        "status": "finalized",
        "effective_rule_readiness": effective_rule_readiness(root),
    }
    if upgrade_evidence is not None:
        result["terminal_receipt"] = {
            "path": TERMINAL_RECEIPT_PATH,
            "transaction_id": upgrade_evidence["transaction_id"],
            "packet_digest": upgrade_evidence["packet_digest"],
            "decision_digest": upgrade_evidence["decision_digest"],
        }
    return result


def initialize_context(
    root: Path,
    source: object,
    selection: dict,
    imported_at: str,
    effective_state_candidate: dict | None = None,
    effective_resolver_evidence: list[str] | None = None,
) -> dict:
    if not credible_source(source):
        return {
            "status": "unresolved",
            "reason": "credible-source-evidence-required",
            "written": [],
            "effective_rule_readiness": {
                "action_ready": False,
                "status": "unresolved",
                "reason": "effective-rule-state-missing",
                "path": EFFECTIVE_STATE_PATH,
            },
        }
    root = root.resolve()
    if (effective_state_candidate is None) != (effective_resolver_evidence is None):
        raise TargetValidationError(
            "effective state candidate and resolver evidence must be supplied together"
        )
    pending_errors: list[str] = []
    validate_pending_apply_receipt(root, pending_errors)
    if pending_errors:
        return {
            "status": "unresolved",
            "reason": "required-framework-managed-path-validation-failed",
            "written": [],
            "effective_rule_readiness": {
                "action_ready": False,
                "status": "unresolved",
                "reason": "effective-rule-state-missing",
                "path": EFFECTIVE_STATE_PATH,
            },
        }
    provenance, ledger = build_initialization_documents(
        dict(source), selection, imported_at
    )
    dev_root = root / ".dev"
    context = dev_root / "ai-context"
    legacy = dev_root / "AI-CONTEXT-SOURCE.yaml"
    if legacy.is_file() or context.exists():
        raise TargetValidationError(
            "initialization requires no active legacy or component-aware authority"
        )
    dev_root.mkdir(parents=True, exist_ok=True)
    candidate = Path(
        tempfile.mkdtemp(prefix=".ai-context.candidate.", dir=dev_root)
    )
    try:
        provenance_path = candidate / "provenance.yaml"
        ledger_path = candidate / "customizations.yaml"
        provenance_path.write_text(
            yaml.safe_dump(provenance, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )
        ledger_path.write_text(
            yaml.safe_dump(ledger, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )
        errors: list[str] = []
        validate_manifest(provenance_path, errors)
        validate_customizations(ledger_path, errors, require_finalized=True)
        if errors:
            raise TargetValidationError("; ".join(errors))
        os.replace(candidate, context)
        if effective_state_candidate is not None:
            try:
                state, packets = build_effective_state_and_packets(
                    root,
                    effective_state_candidate,
                    resolver_evidence=effective_resolver_evidence or [],
                )
                write_effective_state_and_packets(root, state, packets)
            except Exception:
                # Context did not exist at initialization entry, so this removes only
                # this failed in-process initialization attempt and no unrelated target truth.
                shutil.rmtree(context)
                raise
    finally:
        if candidate.exists():
            shutil.rmtree(candidate)
    written = [
        ".dev/ai-context/provenance.yaml",
        ".dev/ai-context/customizations.yaml",
    ]
    if effective_state_candidate is not None:
        written.append(EFFECTIVE_STATE_PATH)
        written.extend(
            sorted(
                f".dev/ai-context/effective-rule-packets/{route['route_id']}.yaml"
                for route in state["routing"]
            )
        )
    return {
        "status": "initialized",
        "written": written,
        "effective_rule_readiness": effective_rule_readiness(root),
    }
