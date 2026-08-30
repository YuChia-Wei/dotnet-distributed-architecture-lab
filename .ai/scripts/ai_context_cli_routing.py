#!/usr/bin/env python3
"""Portable validation for ignored per-clone CLI execution routes."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path, PurePosixPath

import yaml


CONTRACT_PATH = Path(".ai/assets/shared/CLI-EXECUTION-ROUTING-CONTRACT.md")
SCHEMA_PATH = Path(".ai/assets/shared/cli-execution-routing.schema.yaml")
LOCAL_PATH = Path(".dev/ai-context/local/cli-execution-routing.yaml")
IGNORE_RULE = "/.dev/ai-context/local/"

OPERATION_ID = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")
CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)*$")
ROUTE_ID = re.compile(r"^[a-z][a-z0-9-]*$")

SURFACES = {
    "sandboxed-cli",
    "host-cli",
    "wsl-cli",
    "container-cli",
}
SANDBOX_VALUES = {"inside", "outside", "runtime-default", "not-applicable"}
WORKING_DIRECTORY_VALUES = {
    "repository-root",
    "current-directory",
    "explicit-local-path",
}
SELECTOR_FIELDS = {
    "distribution",
    "shell",
    "executable",
    "container",
}
REQUIREMENT_VALUES = {
    "network": {"forbidden", "allowed", "required"},
    "credential_boundary": {
        "none",
        "runtime-managed",
        "host-managed",
    },
    "filesystem_write": {"none", "repository", "ignored-local", "external"},
    "privilege": {"standard", "elevated-owner-approved"},
    "approval": {"not-required", "required-before-execution"},
}
FALLBACK_CONDITIONS = {
    "unavailable",
    "blocked-by-environment",
    "stale",
}
FORBIDDEN_FIELDS = {
    "token",
    "password",
    "secret",
    "credential",
    "credential_value",
    "session",
    "username",
    "endpoint",
    "private_endpoint",
    "approval_message",
}


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )


def _unique_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) for item in value)
        and len(value) == len(set(value))
    )


def _load_yaml(path: Path, label: Path, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{label}: cannot read YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: root must be a mapping")
        return None
    return value


def _validate_contract(root: Path, errors: list[str], contract_path: Path, schema_path: Path) -> set[str]:
    contract_file = root / contract_path
    if not contract_file.is_file():
        errors.append(f"{contract_path}: missing CLI execution-routing contract")
    else:
        try:
            contract = contract_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{contract_path}: cannot read contract: {exc}")
        else:
            for heading in (
                "## Authority Order",
                "## Tracked And Local Boundaries",
                "## Route Resolution",
                "## Post-Recovery Persistence",
                "## Fail-Closed Conditions",
            ):
                if heading not in contract:
                    errors.append(f"{contract_path}: missing required heading {heading}")

    schema = _load_yaml(root / schema_path, schema_path, errors)
    if schema is None:
        return FORBIDDEN_FIELDS

    for key, expected in {
        "schema_version": "1.0",
        "contract_id": "cli-execution-routing",
        "record_type": "cli-execution-routing-local",
    }.items():
        if schema.get(key) != expected:
            errors.append(f"{schema_path}: {key} must equal {expected!r}")

    storage = schema.get("storage")
    expected_storage = {
        "default_local_path": LOCAL_PATH.as_posix(),
        "gitignore_rule": IGNORE_RULE,
        "tracked_instance": "prohibited",
        "packaged_instance": "prohibited",
        "create_or_update_requires": "explicit-user-consent-after-successful-recovery",
        "missing_record": "valid-unconfigured",
    }
    if not isinstance(storage, dict):
        errors.append(f"{schema_path}: storage must be a mapping")
    else:
        for key, expected in expected_storage.items():
            if storage.get(key) != expected:
                errors.append(f"{schema_path}: storage.{key} must equal {expected!r}")

    candidate_schema = schema.get("candidates")
    surface_values = None
    if isinstance(candidate_schema, dict):
        record = candidate_schema.get("record")
        if isinstance(record, dict) and isinstance(record.get("surface"), dict):
            surface_values = record["surface"].get("values")
    if not isinstance(surface_values, list) or set(surface_values) != SURFACES:
        errors.append(f"{schema_path}: candidates.record.surface.values is incomplete")

    forbidden = schema.get("forbidden_fields")
    if not isinstance(forbidden, list) or not all(
        isinstance(item, str) and item for item in forbidden
    ):
        errors.append(f"{schema_path}: forbidden_fields must be a list of strings")
        return FORBIDDEN_FIELDS
    forbidden_set = set(forbidden)
    if not FORBIDDEN_FIELDS <= forbidden_set:
        errors.append(f"{schema_path}: forbidden_fields is missing sensitive names")
    return forbidden_set


def _validate_ignore_boundary(root: Path, errors: list[str], local_path: Path) -> bool:
    ignore_file = root / ".gitignore"
    try:
        ignore_lines = ignore_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f".gitignore: cannot verify local route ignore contract: {exc}")
        return False
    if IGNORE_RULE not in ignore_lines:
        errors.append(f".gitignore: missing exact {IGNORE_RULE} rule")

    relative = local_path.as_posix()
    ignored = _run_git(root, "check-ignore", "--no-index", "-q", "--", relative)
    if ignored.returncode != 0:
        errors.append(f"{local_path}: exact local binding path is not Git-ignored")
        return False
    return True


def _validate_file_boundary(root: Path, errors: list[str], local_path: Path) -> bool:
    current = root
    for part in PurePosixPath(local_path.as_posix()).parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"{local_path}: symlink boundary is not allowed")
            return False
    local_file = root / local_path
    if not local_file.is_file() or local_file.is_symlink():
        errors.append(f"{local_path}: local binding must be a regular non-symlink file")
        return False
    return True


def _validate_untracked(root: Path, errors: list[str], local_path: Path) -> None:
    relative = local_path.as_posix()
    tracked = _run_git(root, "ls-files", "--error-unmatch", "--", relative)
    if tracked.returncode == 0:
        errors.append(f"{local_path}: personal local binding must not be Git-tracked")
    staged = _run_git(root, "diff", "--cached", "--name-only", "--", relative)
    if staged.returncode != 0:
        errors.append(f"{local_path}: cannot inspect staged state")
    elif staged.stdout.strip():
        errors.append(f"{local_path}: personal local binding must not be staged")


def _find_forbidden(value: object, location: str, forbidden: set[str], local_path: Path, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.casefold() in forbidden:
                errors.append(f"{local_path}: forbidden field {location}.{key_text}")
            _find_forbidden(child, f"{location}.{key_text}", forbidden, local_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _find_forbidden(child, f"{location}[{index}]", forbidden, local_path, errors)
    elif isinstance(value, str) and "://" in value:
        errors.append(f"{local_path}: URI values are prohibited at {location}")


def _validate_candidate(candidate: object, location: str, route_ids: list[object], local_path: Path, errors: list[str]) -> None:
    if not isinstance(candidate, dict):
        errors.append(f"{local_path}: {location} must be a mapping")
        return
    allowed_fields = {
        "route_id",
        "surface",
        "sandbox",
        "selectors",
        "working_directory",
        "requirements",
        "fallback",
    }
    required_fields = allowed_fields - {"selectors", "working_directory"}
    if not required_fields <= set(candidate) or not set(candidate) <= allowed_fields:
        errors.append(f"{local_path}: {location} has invalid fields")

    route_id = candidate.get("route_id")
    if not isinstance(route_id, str) or not ROUTE_ID.fullmatch(route_id):
        errors.append(f"{local_path}: {location}.route_id is invalid")
    if candidate.get("surface") not in SURFACES:
        errors.append(f"{local_path}: {location}.surface is invalid")
    if candidate.get("sandbox") not in SANDBOX_VALUES:
        errors.append(f"{local_path}: {location}.sandbox is invalid")
    if "working_directory" in candidate and candidate.get("working_directory") not in WORKING_DIRECTORY_VALUES:
        errors.append(f"{local_path}: {location}.working_directory is invalid")

    selectors = candidate.get("selectors", {})
    if not isinstance(selectors, dict) or not set(selectors) <= SELECTOR_FIELDS:
        errors.append(f"{local_path}: {location}.selectors has invalid fields")
    elif not all(
        isinstance(value, str)
        and bool(value.strip())
        and "\n" not in value
        and "\r" not in value
        for value in selectors.values()
    ):
        errors.append(f"{local_path}: {location}.selectors values must be non-empty single-line strings")

    requirements = candidate.get("requirements")
    if not isinstance(requirements, dict) or set(requirements) != set(REQUIREMENT_VALUES):
        errors.append(f"{local_path}: {location}.requirements fields are invalid")
    else:
        for key, allowed in REQUIREMENT_VALUES.items():
            if requirements.get(key) not in allowed:
                errors.append(f"{local_path}: {location}.requirements.{key} is invalid")

    fallback = candidate.get("fallback")
    fallback_fields = {"on", "to", "retry", "max_attempts"}
    if not isinstance(fallback, dict) or set(fallback) != fallback_fields:
        errors.append(f"{local_path}: {location}.fallback fields are invalid")
        return
    fallback_on = fallback.get("on")
    fallback_to = fallback.get("to")
    if not _unique_string_list(fallback_on) or not set(fallback_on) <= FALLBACK_CONDITIONS:
        errors.append(f"{local_path}: {location}.fallback.on is invalid")
    valid_route_ids = {item for item in route_ids if isinstance(item, str)}
    if not _unique_string_list(fallback_to) or not set(fallback_to) <= valid_route_ids:
        errors.append(f"{local_path}: {location}.fallback.to is invalid")
    if isinstance(fallback_to, list) and route_id in fallback_to:
        errors.append(f"{local_path}: {location}.fallback.to cannot reference itself")
    if fallback.get("retry") != "material-change-only":
        errors.append(f"{local_path}: {location}.fallback.retry is invalid")
    if fallback.get("max_attempts") != 1:
        errors.append(f"{local_path}: {location}.fallback.max_attempts must equal 1")


def _validate_route(route: object, index: int, local_path: Path, errors: list[str]) -> None:
    location = f"routes[{index}]"
    if not isinstance(route, dict):
        errors.append(f"{local_path}: {location} must be a mapping")
        return
    route_fields = {"operation_id", "capability_id", "candidates", "persistence"}
    if set(route) != route_fields:
        errors.append(f"{local_path}: {location} fields must equal {sorted(route_fields)}")
    operation_id = route.get("operation_id")
    capability_id = route.get("capability_id")
    if not isinstance(operation_id, str) or not OPERATION_ID.fullmatch(operation_id):
        errors.append(f"{local_path}: {location}.operation_id is invalid")
    if not isinstance(capability_id, str) or not CAPABILITY_ID.fullmatch(capability_id):
        errors.append(f"{local_path}: {location}.capability_id is invalid")

    candidates = route.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append(f"{local_path}: {location}.candidates must be non-empty")
    else:
        route_ids = [
            candidate.get("route_id") if isinstance(candidate, dict) else None
            for candidate in candidates
        ]
        if not _unique_string_list(route_ids):
            errors.append(f"{local_path}: {location}.route_id values must be unique")
        for candidate_index, candidate in enumerate(candidates):
            _validate_candidate(
                candidate,
                f"{location}.candidates[{candidate_index}]",
                route_ids,
                local_path,
                errors,
            )

    persistence = route.get("persistence")
    persistence_fields = {"consent", "reason", "recorded_at", "change"}
    if not isinstance(persistence, dict) or set(persistence) != persistence_fields:
        errors.append(f"{local_path}: {location}.persistence fields are invalid")
        return
    if persistence.get("consent") != "explicit":
        errors.append(f"{local_path}: {location}.persistence.consent must be explicit")
    if persistence.get("reason") not in {"post-recovery-success", "owner-requested"}:
        errors.append(f"{local_path}: {location}.persistence.reason is invalid")
    if persistence.get("change") not in {"create", "merge", "replace"}:
        errors.append(f"{local_path}: {location}.persistence.change is invalid")
    recorded_at = persistence.get("recorded_at")
    try:
        parsed = datetime.fromisoformat(recorded_at) if isinstance(recorded_at, str) else None
    except ValueError:
        parsed = None
    if parsed is None or parsed.utcoffset() is None:
        errors.append(f"{local_path}: {location}.persistence.recorded_at must include an offset")


def validate_cli_execution_routing(
    errors: list[str],
    *,
    root: Path,
    contract_path: Path = CONTRACT_PATH,
    schema_path: Path = SCHEMA_PATH,
    local_path: Path = LOCAL_PATH,
) -> int:
    """Validate the portable contract and an optional ignored local binding."""
    forbidden = _validate_contract(root, errors, contract_path, schema_path)
    _validate_ignore_boundary(root, errors, local_path)

    local_file = root / local_path
    if not local_file.exists():
        return 0
    if not _validate_file_boundary(root, errors, local_path):
        return 0
    _validate_untracked(root, errors, local_path)

    document = _load_yaml(local_file, local_path, errors)
    if document is None:
        return 0
    expected_top_level = {"schema_version", "record_type", "routes"}
    if set(document) != expected_top_level:
        errors.append(f"{local_path}: top-level fields must equal {sorted(expected_top_level)}")
    if document.get("schema_version") != "1.0":
        errors.append(f"{local_path}: schema_version must equal '1.0'")
    if document.get("record_type") != "cli-execution-routing-local":
        errors.append(f"{local_path}: record_type must equal 'cli-execution-routing-local'")
    _find_forbidden(document, "root", forbidden, local_path, errors)

    routes = document.get("routes")
    if not isinstance(routes, list) or not routes:
        errors.append(f"{local_path}: routes must be a non-empty list")
        return 0
    operation_ids = [
        route.get("operation_id") if isinstance(route, dict) else None
        for route in routes
    ]
    if not _unique_string_list(operation_ids):
        errors.append(f"{local_path}: operation_id values must be unique strings")
    elif operation_ids != sorted(operation_ids):
        errors.append(f"{local_path}: routes must be ordered by operation_id")
    for index, route in enumerate(routes):
        _validate_route(route, index, local_path, errors)
    return len(routes)
