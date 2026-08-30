#!/usr/bin/env python3
"""Portable, fail-closed validation for an extracted AI-context package."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CHECKSUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)$")
EXPECTED_VALIDATOR_PATH = ".ai/scripts/validate-ai-context-payload.py"
ENTRYPOINT_REGISTRY_PATH = ".ai/scripts/python-entrypoints.json"
EXPECTED_VALIDATOR_ARGV = [
    "python",
    "payload/.ai/scripts/validate-ai-context-payload.py",
    "--package-root",
    ".",
]
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_PACKAGE_KEYS = {
    "schema_version",
    "package_id",
    "profile_id",
    "version",
    "release_id",
    "selection",
    "user_view",
    "source",
    "created_at",
    "source_date_epoch",
    "payload",
    "identity",
    "compatibility",
    "validation",
}
SEMVER_RE = re.compile(r"^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
PAYLOAD_USER_VIEW_CLASSIFICATIONS = {
    "markdown_local_links": "required-local-navigation",
    "markdown_anchors": "required-local-anchor",
    "component_cross_links": "navigation-only-not-activation",
    "fenced_code": "non-actionable-example-unless-command",
    "inline_code": "non-actionable-reference-unless-command",
    "templates_and_placeholders": "non-actionable-template",
    "external_urls": "external-not-validated",
    "actionable_local_commands": "required-local-target",
}
TARGET_OWNED_REFERENCE_PATTERNS = (
    ".dev/AI-CONTEXT-SOURCE.yaml",
    ".dev/ai-context/provenance.yaml",
    ".dev/ai-context/customizations.yaml",
    ".dev/ai-context/effective-rules.yaml",
    ".dev/ai-context/effective-rule-packets/**",
    ".dev/ai-context/local/**",
    ".dev/validation.local.conf",
)


class PackageValidationError(ValueError):
    """The extracted incoming package does not satisfy its portable contract."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise PackageValidationError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _fail(message: str) -> None:
    raise PackageValidationError(message)


def _safe_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a non-empty POSIX relative path")
    if "\\" in value:
        _fail(f"{label} must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        _fail(f"{label} is not a safe relative path: {value!r}")
    if path.as_posix() != value:
        _fail(f"{label} is not normalized: {value!r}")
    return value


def _path_matches(path: str, pattern: str) -> bool:
    """Match package profile globs with ** crossing directories and * not crossing them."""

    expression = re.escape(pattern)
    expression = expression.replace(r"\*\*", ".*")
    expression = expression.replace(r"\*", "[^/]*")
    expression = expression.replace(r"\?", "[^/]")
    return re.fullmatch(expression, path) is not None


def _semver_key(value: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(value)
    if match is None:
        _fail(f"invalid semantic version: {value!r}")
    return tuple(int(item) for item in match.groups())


def _path_under(root: Path, relative: str, label: str) -> Path:
    _safe_relative_path(relative, label)
    candidate = root.joinpath(*PurePosixPath(relative).parts)
    try:
        candidate.relative_to(root)
    except ValueError as exc:  # Defensive: PurePosix validation above should prevent this.
        raise PackageValidationError(f"{label} escapes package root") from exc
    return candidate


def _require_mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        _fail(f"{label} must be a mapping with string keys")
    return value


def _require_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{label} must be a list")
    return value


def _read_regular(path: Path, label: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        _fail(f"{label} must be a regular non-symlink file: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PackageValidationError(f"cannot read {label}: {path}") from exc


def _load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        document = yaml.load(_read_regular(path, label), Loader=_UniqueKeyLoader)
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise PackageValidationError(f"invalid {label} YAML") from exc
    return _require_mapping(document, label)


def _reject_duplicate_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise PackageValidationError(f"duplicate JSON key: {key!r}")
        document[key] = value
    return document


def _load_json_object(content: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            content.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_pairs
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"invalid {label} JSON") from exc
    return _require_mapping(value, label)


def _validate_json_value(value: object, label: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        _fail(f"{label} must not contain floating-point values")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{label}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                _fail(f"{label} contains a non-string JSON key")
            _validate_json_value(item, f"{label}.{key}")
        return
    _fail(f"{label} contains an unsupported JSON value")


def canonical_json_bytes(document: dict[str, Any]) -> bytes:
    """Encode the package's selected-input proof canonical JSON bytes."""

    _validate_json_value(document, "canonical JSON")
    return json.dumps(
        document, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _walk_regular_files(root: Path) -> dict[str, Path]:
    if not root.is_dir() or root.is_symlink():
        _fail(f"package root must be a regular directory: {root}")
    files: dict[str, Path] = {}

    def walk(current: Path) -> None:
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.encode("utf-8"))
        except OSError as exc:
            raise PackageValidationError(f"cannot enumerate package path: {current}") from exc
        for child in children:
            relative = child.relative_to(root).as_posix()
            _safe_relative_path(relative, "extracted envelope path")
            if child.is_symlink():
                _fail(f"extracted envelope contains a symlink: {relative}")
            if child.is_dir():
                walk(child)
            elif child.is_file():
                if relative in files:
                    _fail(f"duplicate extracted envelope path: {relative}")
                files[relative] = child
            else:
                _fail(f"extracted envelope contains a non-regular member: {relative}")

    walk(root)
    _require_casefold_unique(files, "extracted envelope paths")
    return files


def _require_casefold_unique(paths: object, label: str) -> None:
    seen: dict[str, str] = {}
    for path in paths:
        if not isinstance(path, str):
            _fail(f"{label} contain a non-string path")
        folded = path.casefold()
        previous = seen.get(folded)
        if previous is not None and previous != path:
            _fail(f"{label} have a case-fold collision: {previous!r} and {path!r}")
        seen[folded] = path


def _parse_checksums(content: bytes) -> dict[str, str]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageValidationError("SHA256SUMS.txt is not UTF-8") from exc
    if not text.endswith("\n") or text.endswith("\n\n") or "\r" in text:
        _fail("SHA256SUMS.txt must use LF and exactly one terminal LF")
    records: dict[str, str] = {}
    for index, line in enumerate(text.splitlines(), 1):
        match = CHECKSUM_LINE_RE.fullmatch(line)
        if match is None:
            _fail(f"invalid SHA256SUMS line {index}")
        digest, relative = match.groups()
        _safe_relative_path(relative, f"SHA256SUMS line {index} path")
        if relative == "metadata/SHA256SUMS.txt":
            _fail("SHA256SUMS.txt must not checksum itself")
        if relative in records:
            _fail(f"duplicate SHA256SUMS entry: {relative}")
        records[relative] = digest
    _require_casefold_unique(records, "SHA256SUMS paths")
    return records


def _validate_checksum_coverage(package_root: Path) -> dict[str, Path]:
    files = _walk_regular_files(package_root)
    sums_path = "metadata/SHA256SUMS.txt"
    if sums_path not in files:
        _fail("missing metadata/SHA256SUMS.txt")
    checksums = _parse_checksums(_read_regular(files[sums_path], sums_path))
    expected_paths = set(files) - {sums_path}
    if set(checksums) != expected_paths:
        missing = sorted(expected_paths - set(checksums), key=lambda item: item.encode("utf-8"))
        extra = sorted(set(checksums) - expected_paths, key=lambda item: item.encode("utf-8"))
        _fail(f"SHA256SUMS coverage mismatch: missing={missing!r}; extra={extra!r}")
    for relative, expected in checksums.items():
        actual = _sha256(_read_regular(files[relative], relative))
        if actual != expected:
            _fail(f"SHA256SUMS digest mismatch: {relative}")
    return files


def _record_paths(records: list[Any], label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(records):
        record = _require_mapping(raw, f"{label}[{index}]")
        path = _safe_relative_path(record.get("path"), f"{label}[{index}].path")
        if path in indexed:
            _fail(f"duplicate {label} path: {path}")
        indexed[path] = record
    _require_casefold_unique(indexed, label)
    return indexed


def _require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{label} must be a non-empty string")
    return value


def _validate_selection(
    value: object, components: dict[str, dict[str, Any]] | None = None
) -> tuple[dict[str, Any], set[str]]:
    selection = _require_mapping(value, "package.yaml selection")
    if set(selection) != {
        "release_model",
        "mandatory_components",
        "profiles",
        "providers",
    }:
        _fail("package.yaml selection fields do not match the schema authority")
    if selection.get("release_model") != "single-versioned-componentized-release":
        _fail("package.yaml selection release_model is invalid")
    mandatory = _require_list(
        selection.get("mandatory_components"),
        "package.yaml selection mandatory_components",
    )
    if len(mandatory) != len(set(mandatory)) or set(mandatory) != {
        "software-development-core",
        "ai-context-lifecycle-core",
    }:
        _fail("package.yaml selection must contain exactly both mandatory cores")
    profiles = _require_list(selection.get("profiles"), "package.yaml selection profiles")
    if not profiles or len(profiles) != len(set(profiles)) or not all(
        isinstance(item, str) and item for item in profiles
    ):
        _fail("package.yaml selection profiles must be unique component IDs")
    providers = _require_mapping(
        selection.get("providers"), "package.yaml selection providers"
    )
    selected = {*mandatory, *profiles}
    for component_id, raw in providers.items():
        provider = _require_mapping(raw, f"package.yaml provider {component_id}")
        if set(provider) != {"enabled", "preservation"}:
            _fail(f"package.yaml provider contract has unexpected fields: {component_id}")
        if not isinstance(provider.get("enabled"), bool):
            _fail(f"package.yaml provider enabled flag is invalid: {component_id}")
        if provider.get("preservation") != "preserve-existing-if-recorded":
            _fail(f"package.yaml provider preservation is invalid: {component_id}")
        if provider["enabled"]:
            selected.add(component_id)
    if components is not None:
        unknown = sorted(selected - set(components))
        if unknown:
            _fail(f"package.yaml selection refers to unknown components: {unknown!r}")
        for component_id in selected:
            missing = sorted(set(components[component_id]["requires"]) - selected)
            if missing:
                _fail(
                    f"package.yaml selection is not closed under {component_id} dependencies: "
                    f"{missing!r}"
                )
    return selection, selected


def _validate_user_view(
    package: dict[str, Any],
    records: dict[str, dict[str, Any]],
) -> None:
    contract = _require_mapping(package.get("user_view"), "package.yaml user_view")
    if set(contract) != {
        "schema_version",
        "classifications",
        "reference_integrity",
        "components",
        "supported_selections",
        "capabilities",
    }:
        _fail("package.yaml user_view fields do not match the schema authority")
    if contract.get("schema_version") != "1.0.0":
        _fail("package.yaml user_view must use schema 1.0.0")
    if contract.get("classifications") != PAYLOAD_USER_VIEW_CLASSIFICATIONS:
        _fail("package.yaml user_view classifications are missing or weakened")
    reference = _require_mapping(
        contract.get("reference_integrity"), "package.yaml user_view reference_integrity"
    )
    if set(reference) != {
        "text_extensions",
        "forbidden_source_lifecycle_patterns",
        "target_owned_reference_patterns",
    }:
        _fail("package.yaml user_view reference_integrity fields are invalid")
    extensions = _require_list(
        reference.get("text_extensions"), "package.yaml user_view text_extensions"
    )
    forbidden = _require_list(
        reference.get("forbidden_source_lifecycle_patterns"),
        "package.yaml user_view forbidden_source_lifecycle_patterns",
    )
    target_owned = _require_list(
        reference.get("target_owned_reference_patterns"),
        "package.yaml user_view target_owned_reference_patterns",
    )
    if not extensions or not all(isinstance(item, str) and item.startswith(".") for item in extensions):
        _fail("package.yaml user_view text_extensions are invalid")
    if not forbidden or not all(isinstance(item, str) and item for item in forbidden):
        _fail("package.yaml user_view forbidden lifecycle patterns are invalid")
    if target_owned != list(TARGET_OWNED_REFERENCE_PATTERNS):
        _fail(
            "package.yaml user_view target_owned_reference_patterns must use the "
            "canonical exact allowlist"
        )

    components: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(
        _require_list(contract.get("components"), "package.yaml user_view components")
    ):
        component = _require_mapping(raw, f"package.yaml user_view components[{index}]")
        component_id = _require_string(
            component.get("component_id"),
            f"package.yaml user_view components[{index}].component_id",
        )
        requires = _require_list(
            component.get("requires"),
            f"package.yaml user_view components[{index}].requires",
        )
        allowed = {"component_id", "classification", "required", "requires", "default_enabled"}
        if (
            component_id in components
            or not set(component).issubset(allowed)
            or not isinstance(component.get("classification"), str)
            or not isinstance(component.get("required"), bool)
            or len(requires) != len(set(requires))
            or not all(isinstance(item, str) and item for item in requires)
            or (
                "default_enabled" in component
                and not isinstance(component["default_enabled"], bool)
            )
        ):
            _fail("package.yaml user_view component contract is invalid or ambiguous")
        components[component_id] = component
    if not components:
        _fail("package.yaml user_view components must not be empty")
    for component_id, component in components.items():
        invalid = [item for item in component["requires"] if item == component_id or item not in components]
        if invalid:
            _fail(f"package.yaml user_view component dependencies are invalid: {component_id}")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(component_id: str) -> None:
        if component_id in visiting:
            _fail(f"package.yaml user_view component dependency cycle includes {component_id}")
        if component_id in visited:
            return
        visiting.add(component_id)
        for dependency in components[component_id]["requires"]:
            visit(dependency)
        visiting.remove(component_id)
        visited.add(component_id)

    for component_id in components:
        visit(component_id)

    selection, selected = _validate_selection(package.get("selection"), components)
    required_components = {
        component_id for component_id, component in components.items() if component["required"]
    }
    if required_components != set(selection["mandatory_components"]):
        _fail("package selection mandatory components diverge from user_view authority")
    for profile_id in selection["profiles"]:
        if components[profile_id]["classification"] != "technology-profile":
            _fail(f"package selection profile has the wrong classification: {profile_id}")
    for provider_id in selection["providers"]:
        if provider_id not in components or components[provider_id]["classification"] != "optional-provider":
            _fail(f"package selection provider has the wrong classification: {provider_id}")
    optional_providers = {
        component_id
        for component_id, component in components.items()
        if component["classification"] == "optional-provider"
    }
    if set(selection["providers"]) != optional_providers:
        _fail("package selection provider projection diverges from user_view components")

    selections: dict[str, set[str]] = {}
    for index, raw in enumerate(
        _require_list(
            contract.get("supported_selections"),
            "package.yaml user_view supported_selections",
        )
    ):
        item = _require_mapping(raw, f"package.yaml supported_selections[{index}]")
        if set(item) != {"selection_id", "components"}:
            _fail("package.yaml supported selection fields are invalid")
        selection_id = _require_string(
            item.get("selection_id"), f"package.yaml supported_selections[{index}].selection_id"
        )
        component_ids = _require_list(
            item.get("components"), f"package.yaml supported_selections[{index}].components"
        )
        selected_ids = set(component_ids)
        if (
            selection_id in selections
            or len(component_ids) != len(selected_ids)
            or not selected_ids.issubset(components)
            or not required_components.issubset(selected_ids)
        ):
            _fail("package.yaml supported selection is invalid or ambiguous")
        for component_id in selected_ids:
            if not set(components[component_id]["requires"]).issubset(selected_ids):
                _fail(f"package.yaml supported selection is not dependency closed: {selection_id}")
        selections[selection_id] = selected_ids
    if selected not in selections.values():
        _fail("package default selection is absent from user_view supported selections")

    record_components = {record["component_id"] for record in records.values()}
    unknown_record_components = sorted(record_components - set(components))
    if unknown_record_components:
        _fail(f"files.yaml uses unknown component ownership: {unknown_record_components!r}")

    capability_ids: set[str] = set()
    for index, raw in enumerate(
        _require_list(contract.get("capabilities"), "package.yaml user_view capabilities")
    ):
        capability = _require_mapping(raw, f"package.yaml user_view capabilities[{index}]")
        if set(capability) != {"capability_id", "owner_component", "path_patterns", "availability"}:
            _fail("package.yaml user_view capability fields are invalid")
        capability_id = _require_string(
            capability.get("capability_id"), f"package.yaml capability[{index}].capability_id"
        )
        owner = capability.get("owner_component")
        patterns = _require_list(
            capability.get("path_patterns"), f"package.yaml capability[{index}].path_patterns"
        )
        availability = _require_mapping(
            capability.get("availability"), f"package.yaml capability[{index}].availability"
        )
        if (
            capability_id in capability_ids
            or owner not in components
            or not patterns
            or not all(isinstance(item, str) and item for item in patterns)
            or set(availability) != set(selections)
        ):
            _fail("package.yaml user_view capability contract is invalid or ambiguous")
        matched = {
            path
            for path in records
            if any(_path_matches(path, pattern) for pattern in patterns)
        }
        if not matched or any(records[path]["component_id"] != owner for path in matched):
            _fail(f"package capability ownership projection diverges: {capability_id}")
        for selection_id, selection_components in selections.items():
            expected = "available" if owner in selection_components else "unavailable-not-selected"
            if availability.get(selection_id) != expected:
                _fail(f"package capability availability diverges: {capability_id}/{selection_id}")
        capability_ids.add(capability_id)


def _validate_package_schema_and_projection(
    package: dict[str, Any],
    migration: dict[str, Any],
    records: dict[str, dict[str, Any]],
    files_digest: str,
) -> None:
    if set(package) != EXPECTED_PACKAGE_KEYS:
        missing = sorted(EXPECTED_PACKAGE_KEYS - set(package))
        extra = sorted(set(package) - EXPECTED_PACKAGE_KEYS)
        _fail(f"package.yaml schema fields differ: missing={missing!r}; extra={extra!r}")
    _require_string(package.get("profile_id"), "package.yaml profile_id")
    version = _require_string(package.get("version"), "package.yaml version")
    if VERSION_RE.fullmatch(version) is None or SEMVER_RE.fullmatch(version) is None:
        _fail("package.yaml version must be MAJOR.MINOR.PATCH")
    if package.get("release_id") != f"REL-v{version}":
        _fail("package.yaml release_id does not match version")
    source = _require_mapping(package.get("source"), "package.yaml source")
    if set(source) != {"repository", "ref", "commit", "tree"}:
        _fail("package.yaml source fields are invalid")
    _require_string(source.get("repository"), "package.yaml source repository")
    if not all(isinstance(source.get(key), str) and FULL_SHA_RE.fullmatch(source[key]) for key in ("commit", "tree")):
        _fail("package.yaml source commit and tree must be full immutable SHAs")
    ref = _require_string(source.get("ref"), "package.yaml source ref")
    if ref != source["commit"] and ref != f"v{version}":
        _fail("package.yaml source ref must be the full commit or exact release tag")
    created_at = _require_string(package.get("created_at"), "package.yaml created_at")
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})", created_at) is None:
        _fail("package.yaml created_at must be timezone-qualified ISO 8601")
    epoch = package.get("source_date_epoch")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        _fail("package.yaml source_date_epoch must be a non-negative integer")
    compatibility = _require_mapping(package.get("compatibility"), "package.yaml compatibility")
    if not {"minimum_governed_source", "breaking_changes"}.issubset(compatibility):
        _fail("package.yaml compatibility is incomplete")
    if SEMVER_RE.fullmatch(str(compatibility["minimum_governed_source"])) is None:
        _fail("package.yaml minimum_governed_source must be an exact semantic version")
    if not isinstance(compatibility["breaking_changes"], bool):
        _fail("package.yaml breaking_changes must be boolean")
    automatic = compatibility.get("automatic_upgrade_sources", [])
    if (
        not isinstance(automatic, list)
        or len(automatic) != len(set(automatic))
        or automatic != sorted(automatic, key=_semver_key)
        or not all(isinstance(item, str) and SEMVER_RE.fullmatch(item) for item in automatic)
    ):
        _fail("package.yaml automatic_upgrade_sources must be unique ordered semantic versions")
    _validate_user_view(package, records)
    if migration.get("schema_version") != "3.0.0":
        _fail("migration.yaml must use component-aware schema 3.0.0")
    if set(migration) != {
        "schema_version",
        "package_id",
        "selection",
        "to",
        "clean_install",
        "sources",
        "safety",
    }:
        _fail("migration.yaml fields do not match schema 3.0.0")
    if migration.get("selection") != package.get("selection"):
        _fail("migration.yaml selection diverges from package.yaml")
    destination = _require_mapping(migration.get("to"), "migration.yaml to")
    if destination != {"version": version, "manifest_sha256": files_digest}:
        _fail("migration.yaml destination identity diverges from package.yaml/files.yaml")
    safety = _require_mapping(migration.get("safety"), "migration.yaml safety")
    expected_safety = {
        "dry_run_default": True,
        "clean_worktree_required": True,
        "starting_commit_required": True,
        "abort_on_unacknowledged_reconciliation": True,
    }
    if safety != expected_safety:
        _fail("migration.yaml safety contract is missing or weakened")
    clean_install = _require_mapping(
        migration.get("clean_install"), "migration.yaml clean_install"
    )
    operations = _require_list(
        clean_install.get("operations"), "migration.yaml clean_install operations"
    )
    indexed: dict[str, dict[str, Any]] = {}
    operation_ids: list[str] = []
    for index, raw in enumerate(operations):
        operation = _require_mapping(raw, f"clean_install operations[{index}]")
        if set(operation) != {
            "id",
            "kind",
            "path",
            "ownership",
            "preconditions",
            "component_id",
        }:
            _fail(f"clean-install operation fields are invalid at index {index}")
        operation_ids.append(
            _require_string(operation.get("id"), f"clean_install operations[{index}].id")
        )
        path = _safe_relative_path(
            operation.get("path"), f"clean_install operations[{index}].path"
        )
        if path in indexed:
            _fail(f"duplicate clean-install operation path: {path}")
        indexed[path] = operation
    if len(operation_ids) != len(set(operation_ids)) or operation_ids != sorted(operation_ids):
        _fail("clean-install operation IDs must be unique and ordered")
    if set(indexed) != set(records):
        _fail("clean-install operations do not exactly cover files.yaml")
    for path, operation in indexed.items():
        if (
            operation.get("kind") != "add"
            or operation.get("ownership") != records[path]["ownership"]
            or operation.get("component_id") != records[path]["component_id"]
            or operation.get("preconditions") != ["destination_absent"]
        ):
            _fail(f"clean-install operation diverges from files.yaml: {path}")


def _validate_inventory(
    package_root: Path, files: dict[str, Path], inventory: dict[str, Any], package_id: str
) -> dict[str, dict[str, Any]]:
    if inventory.get("schema_version") != "2.0.0":
        _fail("files.yaml must use schema 2.0.0")
    if set(inventory) != {"schema_version", "package_id", "files"}:
        _fail("files.yaml fields do not match schema 2.0.0")
    if inventory.get("package_id") != package_id:
        _fail("files.yaml package_id does not match package.yaml")
    records = _record_paths(_require_list(inventory.get("files"), "files.yaml files"), "files.yaml files")
    if list(records) != sorted(records, key=lambda item: item.encode("utf-8")):
        _fail("files.yaml files must be ordered by UTF-8 path")
    for relative, record in records.items():
        expected_fields = {
            "path",
            "source_path",
            "sha256",
            "size",
            "mode",
            "ownership",
            "install_behavior",
            "entry_id",
            "component_id",
        }
        if set(record) != expected_fields:
            _fail(f"files.yaml record fields differ from schema: {relative}")
        _safe_relative_path(record.get("source_path"), f"files.yaml source_path: {relative}")
        _require_string(record.get("entry_id"), f"files.yaml entry_id: {relative}")
        if not _is_sha256(record["sha256"]):
            _fail(f"files.yaml record has invalid sha256: {relative}")
        if not isinstance(record["size"], int) or isinstance(record["size"], bool) or record["size"] < 0:
            _fail(f"files.yaml record has invalid size: {relative}")
        if record["mode"] not in {"0644", "0755"}:
            _fail(f"files.yaml record has invalid mode: {relative}")
        if record["ownership"] not in {"framework-managed", "target-template"}:
            _fail(f"files.yaml record ownership is invalid: {relative}")
        if record["install_behavior"] not in {"managed", "seed", "reconcile"}:
            _fail(f"files.yaml record install_behavior is invalid: {relative}")
        _require_string(record["component_id"], f"files.yaml component_id: {relative}")
        envelope_path = f"payload/{relative}"
        payload = files.get(envelope_path)
        if payload is None:
            _fail(f"payload file is missing from extracted envelope: {relative}")
        content = _read_regular(payload, envelope_path)
        if _sha256(content) != record["sha256"] or len(content) != record["size"]:
            _fail(f"payload digest or size does not match files.yaml: {relative}")
    actual_payload = {
        relative.removeprefix("payload/")
        for relative in files
        if relative.startswith("payload/")
    }
    if set(records) != actual_payload:
        _fail("payload paths and files.yaml paths differ")
    return records


def _payload_fingerprint(records: dict[str, dict[str, Any]]) -> str:
    content = "".join(
        f"{record['sha256']}  {path}\n"
        for path, record in sorted(records.items(), key=lambda item: item[0].encode("utf-8"))
    ).encode("utf-8")
    return _sha256(content)


def _validate_package_identity(
    package: dict[str, Any],
    files_bytes: bytes,
    migration_bytes: bytes,
    records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    identity = _require_mapping(package.get("identity"), "package.yaml identity")
    if set(identity) != {
        "schema_version",
        "selected_input_fingerprint",
        "payload_fingerprint",
        "files_manifest_digest",
        "migration_digest",
    }:
        _fail("package.yaml identity fields are incomplete or unexpected")
    if identity.get("schema_version") != "1.0.0":
        _fail("package.yaml identity must use schema 1.0.0")
    expected = {
        "payload_fingerprint": _payload_fingerprint(records),
        "files_manifest_digest": _sha256(files_bytes),
        "migration_digest": _sha256(migration_bytes),
    }
    for key, digest in expected.items():
        if identity.get(key) != digest:
            _fail(f"package identity {key} does not match package bytes")
    payload = _require_mapping(package.get("payload"), "package.yaml payload")
    if set(payload) != {"root", "file_count", "sha256"}:
        _fail("package.yaml payload fields are incomplete or unexpected")
    if (
        payload.get("root") != "payload"
        or payload.get("file_count") != len(records)
        or payload.get("sha256") != expected["payload_fingerprint"]
    ):
        _fail("package payload identity does not match files.yaml")
    return identity


def _validate_validation_manifest(
    package_root: Path,
    files: dict[str, Path],
    package: dict[str, Any],
    package_id: str,
    identity: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    package_validation = _require_mapping(package.get("validation"), "package.yaml validation")
    if set(package_validation) != {
        "schema_version",
        "manifest",
        "manifest_sha256",
        "selected_inputs",
        "selected_inputs_sha256",
    } or package_validation.get("schema_version") != "package-validation/v1":
        _fail("package.yaml validation pointer does not match package-validation/v1")
    manifest_path = _safe_relative_path(
        package_validation.get("manifest"), "package.yaml validation manifest"
    )
    proof_path = _safe_relative_path(
        package_validation.get("selected_inputs"), "package.yaml validation selected_inputs"
    )
    if manifest_path != "metadata/validation.json" or proof_path != "metadata/selected-inputs.json":
        _fail("package.yaml validation paths are not the package-validation/v1 paths")
    manifest_bytes = _read_regular(
        _path_under(package_root, manifest_path, "validation manifest"), manifest_path
    )
    proof_bytes = _read_regular(
        _path_under(package_root, proof_path, "selected inputs proof"), proof_path
    )
    if files.get(manifest_path) is None or files.get(proof_path) is None:
        _fail("validation metadata is not part of the checksummed envelope")
    if package_validation.get("manifest_sha256") != _sha256(manifest_bytes):
        _fail("package.yaml validation manifest_sha256 does not match validation.json")
    if package_validation.get("selected_inputs_sha256") != _sha256(proof_bytes):
        _fail("package.yaml validation selected_inputs_sha256 does not match selected-inputs.json")
    validation = _load_json_object(manifest_bytes, "validation.json")
    proof = _load_json_object(proof_bytes, "selected-inputs.json")
    if set(validation) != {
        "schema_version",
        "package_id",
        "authority",
        "selected_input_proof",
        "source_only_tests",
        "integrity_policy",
    }:
        _fail("validation.json fields are incomplete or unexpected")
    if set(proof) != {
        "schema_version",
        "source_inputs",
        "payload",
        "migration_sources",
    }:
        _fail("selected-inputs.json fields are incomplete or unexpected")
    if canonical_json_bytes(validation) != manifest_bytes:
        _fail("validation.json is not canonical compact sorted JSON bytes")
    if validation.get("schema_version") != "package-validation/v1":
        _fail("validation.json must use schema package-validation/v1")
    if validation.get("package_id") != package_id:
        _fail("validation.json package_id does not match package.yaml")
    selected = _require_mapping(
        validation.get("selected_input_proof"), "validation.json selected_input_proof"
    )
    if selected.get("path") != proof_path or selected.get("sha256") != _sha256(proof_bytes):
        _fail("validation.json selected-input proof identity does not match package bytes")
    if identity.get("selected_input_fingerprint") != _sha256(proof_bytes):
        _fail("package identity selected_input_fingerprint does not match selected-inputs.json")
    if proof.get("schema_version") != "package-selected-input/v1":
        _fail("selected-inputs.json must use schema package-selected-input/v1")
    if canonical_json_bytes(proof) != proof_bytes:
        _fail("selected-inputs.json is not canonical compact sorted JSON bytes")
    return validation, proof, proof_bytes


def _validate_ordered_records(
    records: list[Any], label: str, key: str = "path"
) -> list[dict[str, Any]]:
    parsed = [_require_mapping(item, f"{label}[{index}]") for index, item in enumerate(records)]
    values = [_require_string(item.get(key), f"{label}[{index}].{key}") for index, item in enumerate(parsed)]
    if len(values) != len(set(values)):
        _fail(f"{label} contain duplicate {key} values")
    if values != sorted(values, key=lambda item: item.encode("utf-8")):
        _fail(f"{label} must be ordered by UTF-8 {key}")
    return parsed


def _validate_selected_input_proof(
    package_root: Path,
    proof: dict[str, Any],
    package: dict[str, Any],
    identity: dict[str, Any],
    records: dict[str, dict[str, Any]],
    migration: dict[str, Any],
) -> None:
    source_inputs = _validate_ordered_records(
        _require_list(proof.get("source_inputs"), "selected-input source_inputs"),
        "selected-input source_inputs",
    )
    for index, source in enumerate(source_inputs):
        _safe_relative_path(source.get("path"), f"selected-input source_inputs[{index}].path")
        if not _is_sha256(source.get("sha256")) or set(source) != {"path", "sha256"}:
            _fail(f"selected-input source_inputs[{index}] is invalid")
    source_by_path = {item["path"]: item["sha256"] for item in source_inputs}
    version = package["version"]
    profile_id = package["profile_id"]
    expected_source_paths = {
        ".ai/distribution/templates/INSTALL.md",
        ".ai/distribution/templates/requirements.txt",
        f".ai/distribution/profiles/{profile_id}.yaml",
        f".dev/releases/v{version}/release.yaml",
    }
    if set(source_by_path) != expected_source_paths:
        _fail("selected-input source_inputs do not identify the exact package authority inputs")
    for envelope_path, source_path in (
        ("INSTALL.md", ".ai/distribution/templates/INSTALL.md"),
        ("requirements.txt", ".ai/distribution/templates/requirements.txt"),
    ):
        content = _read_regular(
            _path_under(package_root, envelope_path, f"package {envelope_path}"),
            f"package {envelope_path}",
        )
        if source_by_path[source_path] != _sha256(content):
            _fail(f"selected-input {source_path} does not match extracted {envelope_path}")
    payload = _validate_ordered_records(
        _require_list(proof.get("payload"), "selected-input payload"), "selected-input payload"
    )
    proof_paths = [item["path"] for item in payload]
    _require_casefold_unique(proof_paths, "selected-input payload paths")
    expected_fields = {
        "path",
        "sha256",
        "mode",
        "ownership",
        "install_behavior",
        "component_id",
    }
    if set(proof_paths) != set(records):
        _fail("selected-input payload paths do not exactly match files.yaml")
    for item in payload:
        path = _safe_relative_path(item.get("path"), "selected-input payload path")
        if set(item) != expected_fields:
            _fail(f"selected-input payload record has unexpected fields: {path}")
        if not _is_sha256(item.get("sha256")) or item.get("mode") not in {"0644", "0755"}:
            _fail(f"selected-input payload record has invalid identity: {path}")
        for key in ("ownership", "install_behavior", "component_id"):
            _require_string(item.get(key), f"selected-input payload {key}: {path}")
        expected = records[path]
        for key in expected_fields - {"path"}:
            if item[key] != expected[key]:
                _fail(f"selected-input payload record differs from files.yaml: {path}")
    migration_sources = _require_list(
        proof.get("migration_sources"), "selected-input migration_sources"
    )
    expected_sources: list[dict[str, str]] = []
    for index, raw in enumerate(_require_list(migration.get("sources"), "migration.yaml sources")):
        source = _require_mapping(raw, f"migration.yaml sources[{index}]")
        version = _require_string(source.get("version"), f"migration.yaml sources[{index}].version")
        digest = source.get("manifest_sha256")
        if not _is_sha256(digest):
            _fail(f"migration.yaml sources[{index}] has invalid manifest_sha256")
        expected_sources.append({"version": version, "manifest_sha256": digest})
    if migration_sources != expected_sources:
        _fail("selected-input migration_sources do not exactly match migration.yaml")
    if not _is_sha256(identity.get("selected_input_fingerprint")):
        _fail("package identity selected_input_fingerprint is invalid")


def _validate_validator_identity(
    package_root: Path, validation: dict[str, Any]
) -> None:
    authority = _require_mapping(validation.get("authority"), "validation.json authority")
    if set(authority) != {"kind", "validator"} or authority.get("kind") != "incoming-candidate":
        _fail("validation.json authority kind must be incoming-candidate")
    validator = _require_mapping(authority.get("validator"), "validation.json authority validator")
    if set(validator) != {"path", "sha256", "argv"}:
        _fail("validation.json validator fields are incomplete or unexpected")
    if validator.get("path") != EXPECTED_VALIDATOR_PATH:
        _fail("validation.json validator path is not the portable incoming validator")
    if validator.get("argv") != EXPECTED_VALIDATOR_ARGV:
        _fail("validation.json validator argv is not deterministic")
    validator_path = _path_under(
        package_root, f"payload/{EXPECTED_VALIDATOR_PATH}", "portable validator"
    )
    content = _read_regular(validator_path, "portable validator")
    if validator.get("sha256") != _sha256(content):
        _fail("validation.json validator sha256 does not match payload bytes")


def _validate_source_only_tests(validation: dict[str, Any], records: dict[str, dict[str, Any]]) -> None:
    source_only = _require_mapping(validation.get("source_only_tests"), "validation.json source_only_tests")
    if set(source_only) != {
        "classification",
        "patterns",
        "contributes_to_portable_success",
    }:
        _fail("source-only test contract fields are incomplete or unexpected")
    if (
        source_only.get("classification") != "source-only"
        or source_only.get("contributes_to_portable_success") is not False
    ):
        _fail("source-only tests must be classified source-only and excluded from portable success")
    patterns = _require_list(source_only.get("patterns"), "source-only test patterns")
    if not patterns or not all(isinstance(item, str) and item for item in patterns):
        _fail("source-only test patterns must be a non-empty string list")
    for relative in records:
        if any(PurePosixPath(relative).match(pattern) for pattern in patterns):
            _fail(f"source-only test is present in payload: {relative}")


def _validate_integrity_policy(
    package_root: Path,
    validation: dict[str, Any],
    records: dict[str, dict[str, Any]],
) -> None:
    policy = _require_mapping(validation.get("integrity_policy"), "validation.json integrity_policy")
    if set(policy) != {"path_case", "payload_text", "text", "modes"}:
        _fail("integrity policy fields are incomplete or unexpected")
    if policy.get("path_case") != "casefold-unique":
        _fail("integrity policy must require casefold-unique paths")
    if policy.get("payload_text") != "all":
        _fail("integrity policy must validate the complete payload as text")
    text = _require_mapping(policy.get("text"), "integrity policy text")
    if text.get("encoding") != "utf-8" or text.get("line_endings") != "lf-only" or text.get("terminal_lf") != "exactly-one":
        _fail("integrity policy text requirements are weakened or unsupported")
    modes = _require_mapping(policy.get("modes"), "integrity policy modes")
    if modes.get("allowed") != ["0644", "0755"]:
        _fail("integrity policy modes must allow exactly 0644 and 0755")
    _require_casefold_unique(records, "payload paths")
    for relative, record in records.items():
        if record["mode"] not in {"0644", "0755"}:
            _fail(f"payload record has unsupported mode: {relative}")
        content = _read_regular(
            _path_under(package_root, f"payload/{relative}", "payload text"),
            f"payload/{relative}",
        )
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PackageValidationError(f"payload text is not UTF-8: {relative}") from exc
        if b"\r" in content:
            _fail(f"payload text is not LF-only: {relative}")
        if not content.endswith(b"\n") or content.endswith(b"\n\n"):
            _fail(f"payload text must have exactly one terminal LF: {relative}")


def _validate_envelope_runtime_contract(
    package_root: Path,
    files: dict[str, Path],
    records: dict[str, dict[str, Any]],
    *,
    run: bool,
) -> int:
    for relative in ("INSTALL.md", "requirements.txt"):
        if relative not in files:
            _fail(f"missing required package runtime document: {relative}")
    install = _read_regular(files["INSTALL.md"], "INSTALL.md")
    try:
        install_text = install.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageValidationError("INSTALL.md is not UTF-8") from exc
    documented = (
        "python -m pip install -r requirements.txt",
        "python payload/.ai/scripts/validate-ai-context-payload.py --package-root .",
    )
    if not all(command in install_text for command in documented):
        _fail("INSTALL.md omits a required extracted-package command")

    requirements = _read_regular(files["requirements.txt"], "requirements.txt")
    try:
        requirement_values = [
            line.strip()
            for line in requirements.decode("utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    except UnicodeDecodeError as exc:
        raise PackageValidationError("requirements.txt is not UTF-8") from exc

    registry_path = _path_under(
        package_root, f"payload/{ENTRYPOINT_REGISTRY_PATH}", "portable entrypoint registry"
    )
    registry = _load_json_object(_read_regular(registry_path, "portable entrypoint registry"), "portable entrypoint registry")
    if registry.get("schema_version") != "1.0":
        _fail("portable entrypoint registry must use schema 1.0")
    if set(registry) != {
        "schema_version",
        "python_floor",
        "governed_requirements",
        "entrypoints",
    }:
        _fail("portable entrypoint registry fields are incomplete or unexpected")
    floor = _require_string(registry.get("python_floor"), "portable Python floor")
    floor_match = re.fullmatch(r"([0-9]+)\.([0-9]+)", floor)
    if floor_match is None:
        _fail("portable Python floor must be MAJOR.MINOR")
    if sys.version_info[:2] < (int(floor_match.group(1)), int(floor_match.group(2))):
        _fail(f"portable runtime requires Python {floor} or newer")
    governed = _require_mapping(
        registry.get("governed_requirements"), "portable governed_requirements"
    )
    expected_requirement_lines: set[str] = set()
    for dependency, raw in governed.items():
        requirement = _require_mapping(raw, f"portable dependency {dependency}")
        if set(requirement) != {"version", "import_name", "requirements_path"}:
            _fail(f"portable dependency contract is invalid: {dependency}")
        version = _require_string(requirement.get("version"), f"portable dependency {dependency} version")
        import_name = _require_string(
            requirement.get("import_name"), f"portable dependency {dependency} import_name"
        )
        if requirement.get("requirements_path") != "requirements.txt":
            _fail(f"portable dependency requirements path is invalid: {dependency}")
        expected_requirement_lines.add(f"{dependency}=={version}")
        specification = importlib.util.find_spec(import_name)
        if specification is None:
            _fail(f"portable dependency is not importable after requirements install: {dependency}")
        try:
            from importlib import metadata

            installed_version = metadata.version(dependency)
        except metadata.PackageNotFoundError as exc:
            raise PackageValidationError(
                f"portable dependency distribution is not installed: {dependency}"
            ) from exc
        if installed_version != version:
            _fail(
                f"portable dependency version differs from requirements.txt: "
                f"{dependency} expected {version}, found {installed_version}"
            )
    if (
        len(requirement_values) != len(set(requirement_values))
        or set(requirement_values) != expected_requirement_lines
    ):
        _fail("requirements.txt diverges from portable governed_requirements")

    entrypoints = _require_list(registry.get("entrypoints"), "portable entrypoint registry entrypoints")
    all_paths: set[str] = set()
    portable: list[str] = []
    source_only: list[str] = []
    declared_dependencies: dict[str, set[str]] = {}
    for index, raw in enumerate(entrypoints):
        entrypoint = _require_mapping(raw, f"portable entrypoint registry entrypoints[{index}]")
        if set(entrypoint) != {
            "path",
            "portable",
            "dependency_profile",
            "prerequisite_exit_code",
        }:
            _fail("portable entrypoint registry record fields are invalid")
        relative = _safe_relative_path(entrypoint.get("path"), f"portable entrypoint registry entrypoints[{index}].path")
        if relative in all_paths:
            _fail(f"duplicate portable entrypoint registry path: {relative}")
        all_paths.add(relative)
        if not isinstance(entrypoint.get("portable"), bool):
            _fail(f"portable entrypoint registry portable flag is invalid: {relative}")
        dependency_profile = _require_list(
            entrypoint.get("dependency_profile"),
            f"portable entrypoint dependency_profile: {relative}",
        )
        if (
            len(dependency_profile) != len(set(dependency_profile))
            or not all(isinstance(item, str) and item in governed for item in dependency_profile)
            or not isinstance(entrypoint.get("prerequisite_exit_code"), int)
            or isinstance(entrypoint.get("prerequisite_exit_code"), bool)
        ):
            _fail(f"portable entrypoint dependency contract is invalid: {relative}")
        declared_dependencies[relative] = set(dependency_profile)
        (portable if entrypoint["portable"] else source_only).append(relative)
    _require_casefold_unique(all_paths, "portable entrypoint registry paths")
    for relative in portable:
        if relative not in records:
            _fail(f"portable entrypoint is absent from payload: {relative}")
    for relative in source_only:
        if relative in records:
            _fail(f"source-only entrypoint is present in payload: {relative}")

    python_paths = {
        relative for relative in records if PurePosixPath(relative).suffix == ".py"
    }
    modules: dict[str, list[str]] = {}
    for relative in python_paths:
        modules.setdefault(PurePosixPath(relative).stem, []).append(relative)
    governed_imports = {
        requirement["import_name"]: dependency
        for dependency, requirement in governed.items()
    }
    for entrypoint in portable:
        queued = [entrypoint]
        compiled: set[str] = set()
        used_governed: set[str] = set()
        while queued:
            relative = queued.pop()
            if relative in compiled:
                continue
            content = _read_regular(
                _path_under(package_root, f"payload/{relative}", "portable Python closure"),
                f"payload/{relative}",
            )
            try:
                source = content.decode("utf-8")
                tree = ast.parse(source, filename=relative)
                compile(tree, relative, "exec")
            except (UnicodeDecodeError, SyntaxError) as exc:
                raise PackageValidationError(f"portable Python source is invalid: {relative}") from exc
            compiled.add(relative)
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    imported.add(node.module.split(".", 1)[0])
            for module in imported:
                if module in governed_imports:
                    used_governed.add(governed_imports[module])
                    continue
                if module in sys.stdlib_module_names:
                    continue
                candidates = modules.get(module, [])
                if len(candidates) == 1:
                    queued.extend(candidates)
                elif len(candidates) > 1:
                    _fail(f"portable local import is ambiguous: {module} (from {relative})")
                else:
                    _fail(f"portable import is neither local nor governed: {module} (from {relative})")
        if not used_governed.issubset(declared_dependencies[entrypoint]):
            _fail(
                f"portable dependency_profile omits an import-closure dependency: {entrypoint}; "
                f"declared={sorted(declared_dependencies[entrypoint])!r}; "
                f"observed={sorted(used_governed)!r}"
            )

    if not run:
        return 0
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    for relative in portable:
        command = [
            sys.executable,
            str(_path_under(package_root, f"payload/{relative}", "portable entrypoint")),
            "--help",
        ]
        try:
            result = subprocess.run(
                command,
                cwd=package_root,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False,
            )
        except OSError as exc:
            raise PackageValidationError(f"cannot execute portable entrypoint: {relative}") from exc
        except subprocess.TimeoutExpired as exc:
            raise PackageValidationError(f"portable entrypoint timed out: {relative}") from exc
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            _fail(
                f"portable entrypoint --help failed: {relative}; exit={result.returncode}; "
                f"output={output[:1000]!r}"
            )
        if "usage:" not in (result.stdout + result.stderr).lower():
            _fail(f"portable entrypoint --help did not expose an argparse contract: {relative}")
    return len(portable)


def validate_extracted_package(
    package_root: Path, *, run_portable_entrypoints: bool = True
) -> dict[str, object]:
    """Validate one freshly extracted schema-2.3.0 package without source-repo reads."""

    package_root = package_root.resolve()
    files = _validate_checksum_coverage(package_root)
    required = {
        "INSTALL.md",
        "requirements.txt",
        "metadata/package.yaml",
        "metadata/files.yaml",
        "metadata/migration.yaml",
        "metadata/validation.json",
        "metadata/selected-inputs.json",
    }
    missing = sorted(required - set(files), key=lambda item: item.encode("utf-8"))
    if missing:
        _fail(f"missing required package metadata: {missing!r}")
    package_path = files["metadata/package.yaml"]
    files_path = files["metadata/files.yaml"]
    migration_path = files["metadata/migration.yaml"]
    package = _load_yaml_mapping(package_path, "package.yaml")
    inventory = _load_yaml_mapping(files_path, "files.yaml")
    migration = _load_yaml_mapping(migration_path, "migration.yaml")
    if package.get("schema_version") != "2.3.0":
        _fail("package.yaml must use schema 2.3.0")
    package_id = _require_string(package.get("package_id"), "package.yaml package_id")
    if migration.get("package_id") != package_id:
        _fail("migration.yaml package_id does not match package.yaml")
    records = _validate_inventory(package_root, files, inventory, package_id)
    files_bytes = _read_regular(files_path, "files.yaml")
    migration_bytes = _read_regular(migration_path, "migration.yaml")
    _validate_package_schema_and_projection(
        package, migration, records, _sha256(files_bytes)
    )
    identity = _validate_package_identity(package, files_bytes, migration_bytes, records)
    validation, proof, _ = _validate_validation_manifest(
        package_root, files, package, package_id, identity
    )
    _validate_selected_input_proof(
        package_root, proof, package, identity, records, migration
    )
    _validate_validator_identity(package_root, validation)
    _validate_source_only_tests(validation, records)
    _validate_integrity_policy(package_root, validation, records)
    portable_verified = _validate_envelope_runtime_contract(
        package_root, files, records, run=run_portable_entrypoints
    )
    return {
        "package_id": package_id,
        "payload_file_count": len(records),
        "portable_entrypoints_verified": portable_verified,
        "portable_entrypoints_execution": "executed" if run_portable_entrypoints else "skipped",
        "source_only_tests": "excluded-from-portable-validation",
    }
