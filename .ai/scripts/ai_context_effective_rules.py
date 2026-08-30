#!/usr/bin/env python3
"""Fail-closed framework-source and initialized-target rule-packet resolution.

``framework-source`` reads only its fixed source policy, source evidence
schema, and the two selected rule catalogs from Git HEAD.  It never reads or
creates downstream provenance, target effective state, or target packets.
``initialized-target`` retains the target-owned authority and effective-state
contract.  Neither mode discovers semantics by walking Markdown or selecting
an alternate route.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


RESOLVER_SCHEMA_VERSION = "1.0"
APPLICABILITY_MODES = ("framework-source", "initialized-target")
EFFECTIVE_STATE_PATH = ".dev/ai-context/effective-rules.yaml"
PACKET_DIRECTORY = ".dev/ai-context/effective-rule-packets"
SHARED_CATALOG_PATH = ".ai/assets/shared/governance/engineering-rule-catalog.yaml"
PROVENANCE_PATH = ".dev/ai-context/provenance.yaml"
CUSTOMIZATIONS_PATH = ".dev/ai-context/customizations.yaml"
SOURCE_EFFECTIVE_RULES_POLICY_PATH = (
    ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULES.yaml"
)
SOURCE_EFFECTIVE_RULE_EVIDENCE_SCHEMA_PATH = (
    ".dev/standards/AI-CONTEXT-SOURCE-EFFECTIVE-RULE-EVIDENCE.schema.yaml"
)
SOURCE_RESOLVER_MODULE_PATH = ".ai/scripts/ai_context_effective_rules.py"
SOURCE_RESOLVER_CLI_PATH = ".ai/scripts/resolve-effective-rule-packet.py"
PROVENANCE_EFFECTIVE_RULES_LINKAGE = {
    "state": EFFECTIVE_STATE_PATH,
    "packets_root": f"{PACKET_DIRECTORY}/",
    "schema_version": "1.0",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SEMVER_TAG_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
PROFILE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
STABLE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9][A-Z0-9]*)*-\d{3}$")
ROUTE_ID_RE = re.compile(r"^ROUTE-[A-Z0-9][A-Z0-9._-]*$")
PACKET_ID_RE = re.compile(r"^PACKET-[A-Z0-9][A-Z0-9._-]*$")
DISPOSITIONS = {
    "baseline-effective",
    "target-semantic-delta",
    "enforcement-tuning",
    "tooling-waiver",
    "not-applicable",
}
RULE_STRENGTHS = {"invariant", "conditional", "profile-default"}


class EffectiveRuleError(ValueError):
    """An effective-rule resolver input is unresolved, stale, or invalid."""


class SourceEffectiveRuleError(EffectiveRuleError):
    """A framework-source resolver input violates its explicit source contract."""

    def __init__(self, diagnostic: str, detail: str) -> None:
        self.diagnostic = diagnostic
        super().__init__(f"{diagnostic}: {detail}")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _safe_repo_reference(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    raw_path = value.split("#", 1)[0]
    raw_segments = raw_path.split("/")
    if not raw_path or ":" in raw_path or not all(raw_segments):
        return False
    path = PurePosixPath(raw_path)
    return not path.is_absolute() and all(
        part not in {"", ".", ".."} for part in path.parts
    )


def _safe_target_path(value: object) -> bool:
    return _safe_repo_reference(value) and "#" not in str(value)


def is_profile_slug(value: object) -> bool:
    """Return whether value is one strict lowercase single-segment profile slug."""
    return isinstance(value, str) and PROFILE_SLUG_RE.fullmatch(value) is not None


def _reject_unsafe_parent_chain(root: Path, relative: str) -> None:
    """Reject symlinked or non-directory parents before a staged write."""
    current = root
    parts = PurePosixPath(relative).parts
    for part in parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise EffectiveRuleError(
                f"target-effective parent must be a regular directory: {current}"
            )
        if not current.exists():
            continue
        if not current.is_dir():
            raise EffectiveRuleError(
                f"target-effective parent must be a regular directory: {current}"
            )


def _regular_repo_file(root: Path, relative: str, label: str) -> Path:
    """Resolve one safe regular repository file without following symlinks."""
    if not _safe_target_path(relative):
        raise EffectiveRuleError(f"unsafe {label} path: {relative!r}")
    current = root
    parts = PurePosixPath(relative).parts
    for part in parts[:-1]:
        current = current / part
        if current.is_symlink() or not current.is_dir():
            raise EffectiveRuleError(
                f"{label} parent must be a regular directory: {current}"
            )
    path = current / parts[-1]
    if path.is_symlink() or not path.is_file():
        raise EffectiveRuleError(f"{label} must be a regular file: {relative}")
    return path


def _non_empty_references(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and len(value) == len(set(value))
        and all(_safe_repo_reference(item) for item in value)
    )


def _canonical_value(value: Any) -> Any:
    """Reject values outside the declared supported-type canonical JSON contract."""
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        raise EffectiveRuleError("canonical resolver inputs must not contain floats")
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise EffectiveRuleError("canonical resolver mapping keys must be strings")
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    raise EffectiveRuleError(
        f"canonical resolver inputs contain unsupported type {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return the declared supported-type canonical JSON UTF-8 bytes.

    Effective-rule documents deliberately accept only strings, integers,
    booleans, nulls, arrays, and mappings. Rejecting floats avoids claiming a
    broader JSON-number canonicalization contract than this resolver provides.
    """
    try:
        serialized = json.dumps(
            _canonical_value(value),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise EffectiveRuleError(f"cannot canonicalize resolver input: {exc}") from exc
    return (serialized + "\n").encode("utf-8")


def _without_keys(document: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in document.items() if key not in keys}


def catalog_digest(document: dict[str, Any]) -> str:
    return _sha256_bytes(canonical_json_bytes(_without_keys(document, {"catalog_digest"})))


def target_state_digest(document: dict[str, Any]) -> str:
    """Digest semantic state while omitting derived packet digest metadata."""
    candidate = _without_keys(document, {"target_state_digest", "generated_at"})
    routing = candidate.get("routing")
    if isinstance(routing, list):
        for route in routing:
            if isinstance(route, dict) and isinstance(route.get("packet"), dict):
                route["packet"].pop("digest", None)
    return _sha256_bytes(canonical_json_bytes(candidate))


def packet_digest(document: dict[str, Any]) -> str:
    return _sha256_bytes(
        canonical_json_bytes(_without_keys(document, {"packet_digest", "generated_at"}))
    )


def _read_mapping(root: Path, relative: str, label: str) -> dict[str, Any]:
    path = _regular_repo_file(root, relative, label)
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise EffectiveRuleError(f"cannot read {label}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise EffectiveRuleError(f"{label} root must be a mapping")
    return loaded


def _read_mapping_bytes(value: bytes, label: str) -> dict[str, Any]:
    """Load one UTF-8 YAML mapping from already-authorized bytes."""
    try:
        loaded = yaml.safe_load(value.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise EffectiveRuleError(f"cannot read {label}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise EffectiveRuleError(f"{label} root must be a mapping")
    return loaded


def _profile_catalog_path(profile: str) -> str:
    if not is_profile_slug(profile):
        raise EffectiveRuleError(
            "technology profile must be a lowercase single-segment slug"
        )
    return f".ai/assets/tech-stacks/{profile}/engineering-rule-catalog.yaml"


def _validated_target_authorities(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    """Load only target authorities that pass their full finalized contracts."""
    provenance_path = _regular_repo_file(root, PROVENANCE_PATH, "target provenance")
    ledger_path = _regular_repo_file(root, CUSTOMIZATIONS_PATH, "target customizations")

    # Lazy import avoids a module cycle: target provenance imports this module
    # to expose readiness validation and lifecycle generation entrypoints.
    from ai_context_target_provenance import validate_customizations, validate_manifest

    errors: list[str] = []
    validate_manifest(provenance_path, errors)
    validate_customizations(ledger_path, errors, require_finalized=True)
    if errors:
        raise EffectiveRuleError(
            "target authority contract is malformed: " + "; ".join(errors)
        )
    return (
        _read_mapping(root, PROVENANCE_PATH, "target provenance"),
        _read_mapping(root, CUSTOMIZATIONS_PATH, "target customizations"),
        provenance_path,
        ledger_path,
    )


def _ordered_unique_strings(
    value: object,
    label: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or not all(
        isinstance(item, str) and item for item in value
    ):
        qualifier = "possibly-empty" if allow_empty else "non-empty"
        raise EffectiveRuleError(f"{label} must be a {qualifier} string list")
    values = list(value)
    if len(values) != len(set(values)):
        raise EffectiveRuleError(f"{label} must not contain duplicate IDs")
    if values != sorted(values):
        raise EffectiveRuleError(f"{label} must be ascending lexical order")
    return values


def _catalog_normative_digest(
    catalog_id: str,
    record: dict[str, Any],
    label: str,
) -> str:
    direct_digest = record.get("normative_text_sha256")
    if direct_digest is not None:
        if not _is_sha256(direct_digest):
            raise EffectiveRuleError(
                f"{label} has an invalid direct normative statement digest"
            )
        return direct_digest
    if catalog_id == "shared":
        provenance = record.get("source_governance_provenance")
        digest = (
            provenance.get("normative_text_sha256")
            if isinstance(provenance, dict)
            else None
        )
    else:
        digest = None
    if not _is_sha256(digest):
        raise EffectiveRuleError(
            f"{label} has no catalog-aware normative statement digest"
        )
    return digest


def _validate_catalog(
    root: Path,
    relative: str,
    *,
    expected_catalog_id: str,
    expected_profile: str | None,
) -> dict[str, Any]:
    label_path = relative
    catalog = _read_mapping(
        root,
        relative,
        f"engineering-rule catalog {relative}",
    )
    return _validate_catalog_document(
        catalog,
        label_path,
        expected_catalog_id=expected_catalog_id,
        expected_profile=expected_profile,
    )


def _validate_catalog_document(
    catalog: dict[str, Any],
    label_path: str,
    *,
    expected_catalog_id: str,
    expected_profile: str | None,
) -> dict[str, Any]:
    """Validate one catalog mapping independently of its byte source."""
    if catalog.get("schema_version") != "1.0":
        raise EffectiveRuleError(f"{label_path}: unsupported catalog schema_version")
    catalog_digest_record = catalog.get("catalog_digest")
    if not isinstance(catalog_digest_record, dict) or catalog_digest_record.get("algorithm") != "sha256":
        raise EffectiveRuleError(f"{label_path}: catalog_digest must declare sha256")
    declared_digest = catalog_digest_record.get("value")
    if not _is_sha256(declared_digest):
        raise EffectiveRuleError(f"{label_path}: catalog_digest.value must be SHA-256")
    actual_digest = catalog_digest(catalog)
    if declared_digest != actual_digest:
        raise EffectiveRuleError(f"{label_path}: catalog digest mismatch")
    if expected_catalog_id == "shared":
        if catalog.get("catalog_id") != "engineering-rule-catalog-shared":
            raise EffectiveRuleError(f"{label_path}: expected shared engineering-rule catalog")
        if "technology_profile" in catalog:
            raise EffectiveRuleError(f"{label_path}: shared catalog must not select a profile")
    else:
        expected_id = f"engineering-rule-catalog-{expected_profile}"
        if catalog.get("catalog_id") != expected_id or catalog.get("technology_profile") != expected_profile:
            raise EffectiveRuleError(f"{label_path}: selected-profile catalog identity mismatch")
    rules = catalog.get("rules")
    if not isinstance(rules, list) or not rules:
        raise EffectiveRuleError(f"{label_path}: catalog rules must be a non-empty list")
    rule_records: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for index, record in enumerate(rules):
        label = f"{label_path}: rules[{index}]"
        if not isinstance(record, dict):
            raise EffectiveRuleError(f"{label} must be a mapping")
        rule_id = record.get("rule_id")
        if not isinstance(rule_id, str) or STABLE_ID_RE.fullmatch(rule_id) is None:
            raise EffectiveRuleError(f"{label}.rule_id is not a stable rule ID")
        if rule_id in rule_records:
            raise EffectiveRuleError(f"{label_path}: duplicate catalog rule ID {rule_id}")
        if record.get("kind") != "normative-rule":
            raise EffectiveRuleError(f"{label}.kind must be normative-rule")
        if record.get("status") != "active":
            raise EffectiveRuleError(f"{label}.status must be active")
        if record.get("strength") not in RULE_STRENGTHS:
            raise EffectiveRuleError(f"{label}.strength is invalid")
        normative = record.get("normative_text")
        expected_normative_digest = _catalog_normative_digest(
            expected_catalog_id,
            record,
            label,
        )
        if (
            not isinstance(normative, str)
            or "\r" in normative
            or not normative.endswith("\n")
            or normative.endswith("\n\n")
            or _sha256_bytes(normative.encode("utf-8")) != expected_normative_digest
        ):
            raise EffectiveRuleError(f"{label} has invalid full normative statement")
        selector = (
            record.get("catalog_selector")
            if expected_catalog_id == "shared"
            else record.get("catalog_projection", {}).get("selector")
            if isinstance(record.get("catalog_projection"), dict)
            else None
        )
        if not isinstance(selector, dict) or selector.get("rule_id") != rule_id:
            raise EffectiveRuleError(f"{label} has no exact catalog selector")
        rule_records[rule_id] = record
        order.append(rule_id)
    if order != sorted(order):
        raise EffectiveRuleError(f"{label_path}: catalog rules must be ascending lexical order")
    unpacketized = catalog.get("unpacketized_documents", [])
    if not isinstance(unpacketized, list):
        raise EffectiveRuleError(f"{label_path}: unpacketized_documents must be a list")
    unpacketized_paths: set[str] = set()
    for index, record in enumerate(unpacketized):
        label = f"{label_path}: unpacketized_documents[{index}]"
        if not isinstance(record, dict):
            raise EffectiveRuleError(f"{label} must be a mapping")
        source = record.get("canonical_source")
        source_path = source.get("path") if isinstance(source, dict) else None
        if not _safe_target_path(source_path) or source_path in unpacketized_paths:
            raise EffectiveRuleError(f"{label}.canonical_source.path is invalid or duplicate")
        if (
            record.get("packet_state") != "identity-allocation-required"
            or record.get("resolver_disposition") != "unpacketized-fail-closed"
            or "rule_id" in record
        ):
            raise EffectiveRuleError(f"{label} must remain unpacketized and fail closed")
        unpacketized_paths.add(str(source_path))
    constraints = catalog.get("constraints")
    if not isinstance(constraints, list):
        raise EffectiveRuleError(f"{label_path}: constraints must be a list")
    if constraints:
        raise EffectiveRuleError(
            f"{label_path}: constraint packet records require an allocated runtime contract"
        )
    return {
        "catalog": catalog,
        "digest": actual_digest,
        "rules": rule_records,
        "catalog_id": expected_catalog_id,
    }


def _catalogs_for_profile(root: Path, profile: str) -> dict[str, dict[str, Any]]:
    profile_path = _profile_catalog_path(profile)
    return {
        "shared": _validate_catalog(
            root,
            SHARED_CATALOG_PATH,
            expected_catalog_id="shared",
            expected_profile=None,
        ),
        "selected-profile": _validate_catalog(
            root,
            profile_path,
            expected_catalog_id="selected-profile",
            expected_profile=profile,
        ),
    }


def _catalog_rule_index(catalogs: dict[str, dict[str, Any]]) -> dict[str, tuple[str, dict[str, Any]]]:
    output: dict[str, tuple[str, dict[str, Any]]] = {}
    for catalog_id, catalog in catalogs.items():
        for rule_id, record in catalog["rules"].items():
            if rule_id in output:
                raise EffectiveRuleError(f"duplicate rule ID across catalogs: {rule_id}")
            output[rule_id] = (catalog_id, record)
    return output


def _source_error(diagnostic: str, detail: str) -> SourceEffectiveRuleError:
    """Build one source-only diagnostic with a stable, distinguishable prefix."""
    return SourceEffectiveRuleError(diagnostic, detail)


def _source_regular_repo_file(root: Path, relative: str, label: str) -> Path:
    """Resolve a fixed framework-source file without following a symlink."""
    if not _safe_target_path(relative):
        raise _source_error("source-applicability", f"unsafe {label} path: {relative!r}")
    current = root
    parts = PurePosixPath(relative).parts
    for part in parts[:-1]:
        current = current / part
        if current.is_symlink() or not current.is_dir():
            raise _source_error(
                "source-execution-digest",
                f"{label} parent must be a regular directory: {current}",
            )
    path = current / parts[-1]
    if path.is_symlink() or not path.is_file():
        raise _source_error(
            "source-execution-digest",
            f"{label} must be a regular file: {relative}",
        )
    return path


def _source_git(root: Path, arguments: list[str], diagnostic: str) -> bytes:
    """Run one fixed, read-only Git query and preserve stdout bytes exactly."""
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(root), *arguments],
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        raise _source_error(diagnostic, f"cannot run git {' '.join(arguments)}: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise _source_error(
            diagnostic,
            f"git {' '.join(arguments)} failed with exit {result.returncode}: {detail or 'no stderr'}",
        )
    return result.stdout


def _source_single_line(value: bytes, label: str) -> str:
    """Decode a single Git identity result without accepting ambiguous lines."""
    try:
        decoded = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _source_error("source-repository", f"{label} is not UTF-8") from exc
    normalized = decoded.rstrip("\r\n")
    if not normalized or "\r" in normalized or "\n" in normalized:
        raise _source_error("source-repository", f"{label} is empty or ambiguous")
    return normalized


def _source_head_blob(
    root: Path,
    relative: str,
    *,
    diagnostic: str,
    label: str,
) -> bytes:
    """Read one exact regular Git HEAD blob without pathspec discovery."""
    tree = _source_git(
        root,
        ["ls-tree", "-z", "HEAD", "--", relative],
        diagnostic,
    )
    records = [record for record in tree.split(b"\0") if record]
    if len(records) != 1:
        raise _source_error(
            diagnostic,
            f"{label} is missing or ambiguous in HEAD: {relative}",
        )
    metadata, separator, listed_path = records[0].partition(b"\t")
    fields = metadata.split(b" ")
    try:
        listed = listed_path.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _source_error(
            diagnostic,
            f"{label} path is not UTF-8: {relative}",
        ) from exc
    if (
        not separator
        or len(fields) != 3
        or fields[0] not in {b"100644", b"100755"}
        or fields[1] != b"blob"
        or listed != relative
    ):
        raise _source_error(
            diagnostic,
            f"{label} must be a regular HEAD blob: {relative}",
        )
    return _source_git(root, ["show", f"HEAD:{relative}"], diagnostic)


def _source_head_bound_file(root: Path, relative: str) -> tuple[bytes, dict[str, str]]:
    """Read one required source file from HEAD and prove matching working bytes."""
    path = _source_regular_repo_file(root, relative, "source execution file")
    blob = _source_head_blob(
        root,
        relative,
        diagnostic="source-execution-digest",
        label="source execution file",
    )
    try:
        working_tree = path.read_bytes()
    except OSError as exc:
        raise _source_error(
            "source-execution-digest",
            f"cannot read source execution file {relative}: {exc}",
        ) from exc
    if working_tree != blob:
        raise _source_error(
            "source-execution-digest",
            f"source execution file differs from its exact HEAD blob: {relative}",
        )
    try:
        diff = subprocess.run(
            ["git", "-C", os.fspath(root), "diff", "--quiet", "HEAD", "--", relative],
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        raise _source_error(
            "source-execution-digest",
            f"cannot inspect source execution file dirtiness: {relative}: {exc}",
        ) from exc
    if diff.returncode not in {0, 1}:
        detail = diff.stderr.decode("utf-8", errors="replace").strip()
        raise _source_error(
            "source-execution-digest",
            f"cannot inspect source execution file dirtiness: {relative}: {detail or 'no stderr'}",
        )
    if diff.returncode == 1:
        raise _source_error(
            "source-execution-digest",
            f"source execution file is dirty against HEAD: {relative}",
        )
    return blob, {
        "path": relative,
        "blob_digest": _sha256_bytes(blob),
        "working_tree_digest": _sha256_bytes(working_tree),
    }


def _validated_source_policy(policy: dict[str, Any]) -> dict[str, Any]:
    """Validate the closed source-only policy shape without discovery fallback."""
    expected_top_level = {
        "schema_version",
        "document",
        "applicability_mode",
        "repository",
        "catalogs",
        "execution",
        "selection",
        "diagnostics",
        "prohibitions",
    }
    if set(policy) != expected_top_level:
        raise _source_error("source-applicability", "source policy fields are incomplete or ambiguous")
    if (
        policy.get("schema_version") != "1.0"
        or policy.get("document") != "framework-source effective-rule applicability"
        or policy.get("applicability_mode") != "framework-source"
    ):
        raise _source_error("source-applicability", "source policy identity is invalid")

    repository = policy.get("repository")
    expected_commands = {
        "root": ["git", "rev-parse", "--show-toplevel"],
        "commit": ["git", "rev-parse", "HEAD"],
        "origin": ["git", "config", "--get", "remote.origin.url"],
        "status": ["git", "status", "--porcelain=v1", "--untracked-files=all"],
    }
    if not isinstance(repository, dict) or set(repository) != {
        "id",
        "accepted_origin_urls",
        "identity_commands",
    }:
        raise _source_error("source-applicability", "source repository policy is incomplete")
    repository_id = repository.get("id")
    origins = repository.get("accepted_origin_urls")
    if (
        not isinstance(repository_id, str)
        or not repository_id
        or not isinstance(origins, list)
        or not origins
        or not all(isinstance(origin, str) and origin for origin in origins)
        or len(origins) != len(set(origins))
        or origins != sorted(origins)
        or repository.get("identity_commands") != expected_commands
    ):
        raise _source_error("source-applicability", "source repository policy is invalid")

    catalogs = policy.get("catalogs")
    if not isinstance(catalogs, dict) or set(catalogs) != {
        "shared",
        "technology_profiles",
    }:
        raise _source_error("source-applicability", "source catalog policy is incomplete")
    if catalogs.get("shared") != {"path": SHARED_CATALOG_PATH}:
        raise _source_error("source-applicability", "source shared catalog path is invalid")
    profiles = catalogs.get("technology_profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise _source_error("source-applicability", "source technology profile catalog policy is empty")
    profile_paths: dict[str, str] = {}
    for profile, record in profiles.items():
        if not is_profile_slug(profile):
            raise _source_error("source-applicability", "source technology profile is invalid")
        expected_path = _profile_catalog_path(profile)
        if record != {"path": expected_path}:
            raise _source_error(
                "source-applicability",
                f"source profile catalog path is invalid: {profile}",
            )
        profile_paths[profile] = expected_path

    execution = policy.get("execution")
    if not isinstance(execution, dict) or set(execution) != {
        "required_head_bound_paths",
        "read_contract",
        "evidence_schema",
    }:
        raise _source_error("source-applicability", "source execution policy is incomplete")
    required_paths = execution.get("required_head_bound_paths")
    expected_paths = {
        SOURCE_EFFECTIVE_RULE_EVIDENCE_SCHEMA_PATH,
        SOURCE_EFFECTIVE_RULES_POLICY_PATH,
        SOURCE_RESOLVER_MODULE_PATH,
        SOURCE_RESOLVER_CLI_PATH,
        SHARED_CATALOG_PATH,
        *profile_paths.values(),
    }
    if (
        not isinstance(required_paths, list)
        or not all(isinstance(path, str) and _safe_target_path(path) for path in required_paths)
        or len(required_paths) != len(set(required_paths))
        or set(required_paths) != expected_paths
        or execution.get("evidence_schema")
        != SOURCE_EFFECTIVE_RULE_EVIDENCE_SCHEMA_PATH
        or not isinstance(execution.get("read_contract"), str)
        or not execution["read_contract"].strip()
    ):
        raise _source_error("source-applicability", "source execution paths are invalid")

    selection = policy.get("selection")
    if (
        not isinstance(selection, dict)
        or set(selection) != {
            "rule_ids",
            "selection_evidence",
            "ordering",
            "inference",
        }
        or selection.get("rule_ids") != "explicit-required"
        or selection.get("selection_evidence") != "explicit-required"
        or selection.get("inference") != "forbidden"
        or not isinstance(selection.get("ordering"), str)
        or not selection["ordering"].strip()
    ):
        raise _source_error("source-applicability", "source selection policy is invalid")

    diagnostics = policy.get("diagnostics")
    expected_diagnostics = {
        "source_applicability",
        "source_repository",
        "source_execution_digest",
        "source_rule_selection",
        "downstream_provenance_missing",
        "downstream_state_stale",
        "downstream_semantics_unresolved",
    }
    if (
        not isinstance(diagnostics, dict)
        or set(diagnostics) != expected_diagnostics
        or not all(isinstance(value, str) and value.strip() for value in diagnostics.values())
    ):
        raise _source_error("source-applicability", "source diagnostics policy is invalid")
    prohibitions = policy.get("prohibitions")
    if (
        not isinstance(prohibitions, list)
        or not prohibitions
        or not all(isinstance(item, str) and item.strip() for item in prohibitions)
    ):
        raise _source_error("source-applicability", "source prohibitions policy is invalid")
    return {
        "repository_id": repository_id,
        "accepted_origins": list(origins),
        "profile_paths": profile_paths,
        "required_paths": list(required_paths),
    }


def _validated_source_evidence_schema(value: bytes) -> None:
    """Validate the source-only transient evidence schema needed by the policy."""
    try:
        schema = _read_mapping_bytes(value, "source effective-rule evidence schema")
    except EffectiveRuleError as exc:
        raise _source_error("source-applicability", str(exc)) from exc
    required_fields = [
        "schema_version",
        "resolver_outcome",
        "applicability_mode",
        "source_repository",
        "execution_files",
        "request",
        "selection_evidence",
        "catalogs",
        "loaded_rule_ids",
        "rules",
        "freshness",
        "packet_digest",
    ]
    fixed = {
        "schema_version": "1.0",
        "resolver_outcome": "resolved",
        "applicability_mode": "framework-source",
    }
    if (
        schema.get("schema_version") != "1.0"
        or schema.get("classification") != "source-only-transient"
        or schema.get("required") != required_fields
        or schema.get("fixed") != fixed
        or not isinstance(schema.get("source_repository"), dict)
        or not isinstance(schema.get("execution_files"), dict)
        or not isinstance(schema.get("request"), dict)
        or not isinstance(schema.get("freshness"), dict)
        or not isinstance(schema.get("packet_digest"), dict)
    ):
        raise _source_error("source-applicability", "source evidence schema is invalid")


def _source_repository_identity(
    root: Path,
    policy: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    """Resolve only the fixed source repository identity commands from policy."""
    canonical_root = root.resolve()
    if not canonical_root.is_dir():
        raise _source_error("source-repository", "source root is not a directory")
    top_level = _source_single_line(
        _source_git(
            canonical_root,
            ["rev-parse", "--show-toplevel"],
            "source-repository",
        ),
        "source repository root",
    )
    reported_root = Path(top_level)
    if not reported_root.is_absolute():
        raise _source_error("source-repository", "git top-level root is not absolute")
    resolved_top_level = reported_root.resolve()
    if canonical_root != resolved_top_level:
        raise _source_error(
            "source-repository",
            "--root must be the canonical Git top-level source repository",
        )
    origin_url = _source_single_line(
        _source_git(
            canonical_root,
            ["config", "--get", "remote.origin.url"],
            "source-repository",
        ),
        "source origin URL",
    )
    if origin_url not in policy["accepted_origins"]:
        raise _source_error("source-repository", "source origin URL is not accepted")
    commit = _source_single_line(
        _source_git(canonical_root, ["rev-parse", "HEAD"], "source-repository"),
        "source HEAD commit",
    )
    if GIT_SHA_RE.fullmatch(commit) is None:
        raise _source_error("source-repository", "source HEAD is not a 40-character SHA")
    return canonical_root, {
        "id": policy["repository_id"],
        "root": top_level,
        "origin_url": origin_url,
        "commit": commit,
    }


def _source_repository_status(root: Path) -> dict[str, str]:
    """Capture the exact status bytes only after all source inputs are verified."""
    status_bytes = _source_git(
        root,
        ["status", "--porcelain=v1", "--untracked-files=all"],
        "source-repository",
    )
    try:
        status = status_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _source_error("source-repository", "git porcelain v1 output is not UTF-8") from exc
    return {
        "porcelain_v1": status,
        "digest": _sha256_bytes(status_bytes),
    }


def _source_request(
    *,
    capability: object,
    execution_mode: object,
    technology_profile: object,
    file_type: object,
) -> dict[str, str]:
    request = {
        "capability": capability,
        "execution_mode": execution_mode,
        "technology_profile": technology_profile,
        "file_type": file_type,
    }
    normalized: dict[str, str] = {}
    for field, value in request.items():
        if (
            not isinstance(value, str)
            or not value
            or any(token in value for token in ("*", "?"))
        ):
            raise _source_error(
                "source-rule-selection",
                f"request.{field} must be explicit and non-empty",
            )
        normalized[field] = value
    return normalized


def _source_rule_ids(value: object) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and STABLE_ID_RE.fullmatch(item) for item in value)
    ):
        raise _source_error(
            "source-rule-selection",
            "source rule IDs must be a non-empty list of stable IDs",
        )
    rule_ids = list(value)
    if len(rule_ids) != len(set(rule_ids)):
        raise _source_error("source-rule-selection", "source rule IDs must not be duplicated")
    if rule_ids != sorted(rule_ids):
        raise _source_error("source-rule-selection", "source rule IDs must be ascending")
    return rule_ids


def _source_selection_evidence(value: object) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(_safe_repo_reference(item) for item in value)
    ):
        raise _source_error(
            "source-rule-selection",
            "selection evidence must be non-empty safe repository-relative references",
        )
    evidence = list(value)
    if len(evidence) != len(set(evidence)):
        raise _source_error(
            "source-rule-selection",
            "selection evidence must not be duplicated",
        )
    if evidence != sorted(evidence):
        raise _source_error(
            "source-rule-selection",
            "selection evidence must be ascending",
        )
    for reference in evidence:
        relative = reference.split("#", 1)[0]
        if any(token in relative for token in ("*", "?", "[")):
            raise _source_error(
                "source-rule-selection",
                "selection evidence must not use a wildcard path",
            )
    return evidence


def _source_verify_selection_evidence(root: Path, evidence: list[str]) -> None:
    """Require each explicit evidence reference to name one regular HEAD blob."""
    for reference in evidence:
        relative = reference.split("#", 1)[0]
        _source_head_blob(
            root,
            relative,
            diagnostic="source-rule-selection",
            label="selection evidence reference",
        )


def _source_catalogs(
    head_blobs: dict[str, bytes],
    profile: str,
    profile_path: str,
) -> dict[str, dict[str, Any]]:
    """Validate exactly the two policy-selected committed source catalogs."""
    try:
        shared = _validate_catalog_document(
            _read_mapping_bytes(
                head_blobs[SHARED_CATALOG_PATH],
                f"engineering-rule catalog {SHARED_CATALOG_PATH}",
            ),
            SHARED_CATALOG_PATH,
            expected_catalog_id="shared",
            expected_profile=None,
        )
        selected = _validate_catalog_document(
            _read_mapping_bytes(
                head_blobs[profile_path],
                f"engineering-rule catalog {profile_path}",
            ),
            profile_path,
            expected_catalog_id="selected-profile",
            expected_profile=profile,
        )
    except (KeyError, EffectiveRuleError) as exc:
        raise _source_error("source-rule-selection", str(exc)) from exc
    return {"shared": shared, "selected-profile": selected}


def _customization_index(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = ledger.get("customizations")
    if not isinstance(entries, list):
        raise EffectiveRuleError("target customizations ledger must contain a list")
    output: dict[str, dict[str, Any]] = {}
    for entry in entries:
        customization_id = entry.get("id") if isinstance(entry, dict) else None
        if not isinstance(customization_id, str) or customization_id in output:
            raise EffectiveRuleError(
                "target customizations ledger has an invalid or duplicate identity"
            )
        output[customization_id] = entry
    return output


def _selector_key(selector: dict[str, Any]) -> bytes:
    return canonical_json_bytes(
        {
            "capability": selector.get("capability"),
            "execution_mode": selector.get("execution_mode"),
            "technology_profile": selector.get("technology_profile"),
            "file_type": selector.get("file_type"),
        }
    )


def route_id_for_selector(selector: dict[str, Any]) -> str:
    """Return the stable full-digest route ID for one exact selector tuple."""
    return f"ROUTE-{_sha256_bytes(_selector_key(selector)).upper()}"


def packet_id_for_route(route_id: str, state_digest: str) -> str:
    """Return the stable full-digest packet ID without truncating either input."""
    if ROUTE_ID_RE.fullmatch(route_id) is None or not _is_sha256(state_digest):
        raise EffectiveRuleError("cannot derive packet ID from invalid route or state digest")
    identity = {"route_id": route_id, "target_state_digest": state_digest}
    return f"PACKET-{_sha256_bytes(canonical_json_bytes(identity)).upper()}"


def _validate_selector(selector: object, profile: str, label: str) -> dict[str, str]:
    if not isinstance(selector, dict):
        raise EffectiveRuleError(f"{label}.selector must be a mapping")
    required = ("capability", "execution_mode", "technology_profile", "file_type")
    if set(selector) != set(required):
        raise EffectiveRuleError(f"{label}.selector must contain exactly the request dimensions")
    normalized: dict[str, str] = {}
    for field in required:
        value = selector.get(field)
        if not isinstance(value, str) or not value or any(token in value for token in ("*", "?")):
            raise EffectiveRuleError(f"{label}.selector.{field} must be explicit and non-empty")
        normalized[field] = value
    if normalized["technology_profile"] != profile:
        raise EffectiveRuleError(f"{label}.selector.technology_profile does not match state")
    return normalized


def _validate_disposition(
    record: object,
    *,
    label: str,
    catalog_rule: dict[str, Any],
    customizations: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise EffectiveRuleError(f"{label} must be a mapping")
    rule_id = record.get("rule_id")
    if not isinstance(rule_id, str) or STABLE_ID_RE.fullmatch(rule_id) is None:
        raise EffectiveRuleError(f"{label}.rule_id is invalid")
    disposition = record.get("effective_disposition")
    if disposition not in DISPOSITIONS:
        raise EffectiveRuleError(f"{label}.effective_disposition is invalid")
    applicability = record.get("applicability")
    if not isinstance(applicability, str) or not applicability.strip():
        raise EffectiveRuleError(f"{label}.applicability is required")
    if not _non_empty_references(record.get("evidence")):
        raise EffectiveRuleError(f"{label}.evidence must be non-empty unique references")
    if disposition == "baseline-effective":
        acceptance = record.get("baseline_acceptance")
        verification = acceptance.get("verification") if isinstance(acceptance, dict) else None
        if (
            not isinstance(acceptance, dict)
            or acceptance.get("explicit") is not True
            or not isinstance(verification, dict)
            or verification.get("status") != "verified"
            or not _non_empty_references(verification.get("evidence"))
        ):
            raise EffectiveRuleError(f"{label} has no explicit verified baseline acceptance")
    elif disposition == "target-semantic-delta":
        delta = record.get("semantic_delta")
        customization_id = delta.get("customization_id") if isinstance(delta, dict) else None
        customization = customizations.get(customization_id) if isinstance(customization_id, str) else None
        subject = customization.get("subject") if isinstance(customization, dict) else None
        owner = (
            customization.get("owner_reconciliation")
            if isinstance(customization, dict)
            else None
        )
        active_audit = (
            customization.get("active_context_audit")
            if isinstance(customization, dict)
            else None
        )
        post_audit = (
            customization.get("post_upgrade_audit")
            if isinstance(customization, dict)
            else None
        )
        if (
            not isinstance(delta, dict)
            or set(delta)
            != {
                "customization_id",
                "reconciliation_ref",
                "effective_normative_statement",
                "effective_normative_statement_digest",
            }
            or not isinstance(customization_id, str)
            or not isinstance(customization, dict)
            or not isinstance(subject, dict)
            or subject.get("kind") != "rule"
            or subject.get("id") != rule_id
            or customization.get("relationship")
            not in {"extends", "replaces", "deviates"}
            or customization.get("disposition") not in {"retain", "merge"}
            or not isinstance(owner, dict)
            or owner.get("status") != "approved"
            or not isinstance(active_audit, dict)
            or active_audit.get("status") != "verified"
            or not isinstance(post_audit, dict)
            or post_audit.get("status") != "verified"
            or not _safe_repo_reference(delta.get("reconciliation_ref"))
            or delta.get("reconciliation_ref") != owner.get("evidence")
        ):
            raise EffectiveRuleError(
                f"{label} has no finalized same-rule approved semantic delta"
            )
        effective_statement = delta.get("effective_normative_statement")
        effective_digest = delta.get("effective_normative_statement_digest")
        if (
            not isinstance(effective_statement, str)
            or not effective_statement.strip()
            or "\r" in effective_statement
            or not effective_statement.endswith("\n")
            or effective_statement.endswith("\n\n")
            or not _is_sha256(effective_digest)
            or _sha256_bytes(effective_statement.encode("utf-8")) != effective_digest
        ):
            raise EffectiveRuleError(
                f"{label} has an invalid full effective normative statement"
            )
        if catalog_rule.get("strength") == "invariant":
            raise EffectiveRuleError(f"{label} conflicts with an invariant rule")
    elif disposition in {"enforcement-tuning", "tooling-waiver"}:
        waiver = record.get("waiver")
        if (
            not isinstance(waiver, dict)
            or waiver.get("kind") != disposition
            or not isinstance(waiver.get("constraint_ref"), str)
            or not STABLE_ID_RE.fullmatch(waiver["constraint_ref"])
            or not _safe_repo_reference(waiver.get("reconciliation_ref"))
            or not isinstance(waiver.get("reconsideration_trigger"), str)
            or not waiver["reconsideration_trigger"].strip()
        ):
            raise EffectiveRuleError(f"{label} has an invalid waiver")
        raise EffectiveRuleError(
            f"{label} names unsupported constraint {waiver['constraint_ref']}; fail closed"
        )
    else:
        not_applicable = record.get("not_applicable")
        if (
            not isinstance(not_applicable, dict)
            or not isinstance(not_applicable.get("predicate"), str)
            or not not_applicable["predicate"].strip()
            or not _safe_repo_reference(not_applicable.get("verification"))
        ):
            raise EffectiveRuleError(f"{label} has an invalid not-applicable record")
    return record


def _load_state_inputs(
    root: Path,
    *,
    require_packets: bool,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any], dict[str, dict[str, Any]]]:
    provenance, ledger, provenance_path, ledger_path = _validated_target_authorities(root)
    state = _read_mapping(root, EFFECTIVE_STATE_PATH, "target effective state")
    if state.get("schema_version") != "1.0":
        raise EffectiveRuleError("effective state has unsupported schema_version")
    framework = state.get("framework")
    if not isinstance(framework, dict):
        raise EffectiveRuleError("effective state framework must be a mapping")
    version = framework.get("version")
    commit = framework.get("commit")
    profile = framework.get("selected_technology_profile")
    if (
        not isinstance(version, str)
        or SEMVER_TAG_RE.fullmatch(version) is None
        or not isinstance(commit, str)
        or GIT_SHA_RE.fullmatch(commit) is None
        or not is_profile_slug(profile)
    ):
        raise EffectiveRuleError("effective state framework identity is invalid")
    source = provenance.get("source")
    if provenance.get("effective_rules") != PROVENANCE_EFFECTIVE_RULES_LINKAGE:
        raise EffectiveRuleError("effective state provenance linkage is missing or mismatched")
    if not isinstance(source, dict) or source.get("version") != version or source.get("commit") != commit:
        raise EffectiveRuleError("effective state framework does not match target provenance")
    selection = provenance.get("selection")
    profiles = selection.get("profiles") if isinstance(selection, dict) else None
    if not isinstance(profiles, list) or profile not in profiles:
        raise EffectiveRuleError("effective state profile is not selected by target provenance")
    authorities = state.get("target_authorities")
    if not isinstance(authorities, dict):
        raise EffectiveRuleError("effective state target_authorities must be a mapping")
    expected_authorities = {
        "provenance": (PROVENANCE_PATH, _sha256_bytes(provenance_path.read_bytes())),
        "customizations": (CUSTOMIZATIONS_PATH, _sha256_bytes(ledger_path.read_bytes())),
    }
    if set(authorities) != set(expected_authorities):
        raise EffectiveRuleError("effective state target authorities are incomplete or ambiguous")
    for authority_id, (expected_path, expected_digest) in expected_authorities.items():
        record = authorities.get(authority_id)
        if not isinstance(record, dict) or record.get("path") != expected_path or record.get("digest") != expected_digest:
            raise EffectiveRuleError(f"effective state authority is stale: {authority_id}")
    catalogs = _catalogs_for_profile(root, profile)
    state_catalogs = state.get("catalogs")
    if not isinstance(state_catalogs, list) or len(state_catalogs) != 2:
        raise EffectiveRuleError("effective state must name exactly two catalogs")
    observed_catalog_ids: list[str] = []
    expected_catalog_paths = {
        "shared": SHARED_CATALOG_PATH,
        "selected-profile": _profile_catalog_path(profile),
    }
    for index, record in enumerate(state_catalogs):
        label = f"effective state catalogs[{index}]"
        if not isinstance(record, dict):
            raise EffectiveRuleError(f"{label} must be a mapping")
        catalog_id = record.get("catalog_id")
        if catalog_id not in catalogs or record.get("path") != expected_catalog_paths[catalog_id]:
            raise EffectiveRuleError(f"{label} has an unknown catalog identity or path")
        if record.get("digest") != catalogs[catalog_id]["digest"]:
            raise EffectiveRuleError(f"{label} is stale")
        observed_catalog_ids.append(catalog_id)
    if observed_catalog_ids != sorted(observed_catalog_ids) or observed_catalog_ids != ["selected-profile", "shared"]:
        raise EffectiveRuleError("effective state catalogs must be unique and ascending by catalog_id")
    declared_state_digest = state.get("target_state_digest")
    if not _is_sha256(declared_state_digest) or declared_state_digest != target_state_digest(state):
        raise EffectiveRuleError("effective state digest mismatch")
    customizations = _customization_index(ledger)
    rule_index = _catalog_rule_index(catalogs)
    dispositions = state.get("rule_dispositions")
    if not isinstance(dispositions, list) or not dispositions:
        raise EffectiveRuleError("effective state rule_dispositions must be a non-empty list")
    disposition_by_id: dict[str, dict[str, Any]] = {}
    disposition_order: list[str] = []
    for index, record in enumerate(dispositions):
        raw_rule_id = record.get("rule_id") if isinstance(record, dict) else None
        if raw_rule_id not in rule_index:
            raise EffectiveRuleError(
                f"effective state rule_dispositions[{index}] references unknown, type-invalid, or unpacketized ID"
            )
        checked = _validate_disposition(
            record,
            label=f"effective state rule_dispositions[{index}]",
            catalog_rule=rule_index[raw_rule_id][1],
            customizations=customizations,
        )
        if raw_rule_id in disposition_by_id:
            raise EffectiveRuleError(f"duplicate effective rule disposition: {raw_rule_id}")
        disposition_by_id[raw_rule_id] = checked
        disposition_order.append(raw_rule_id)
    if disposition_order != sorted(disposition_order):
        raise EffectiveRuleError("effective state rule dispositions must be ascending lexical order")
    routing = state.get("routing")
    if not isinstance(routing, list) or not routing:
        raise EffectiveRuleError("effective state routing must be a non-empty list")
    routes: dict[bytes, dict[str, Any]] = {}
    route_ids: set[str] = set()
    route_order: list[str] = []
    for index, route in enumerate(routing):
        label = f"effective state routing[{index}]"
        if not isinstance(route, dict):
            raise EffectiveRuleError(f"{label} must be a mapping")
        if set(route) != {
            "route_id",
            "selector",
            "required_rule_ids",
            "reported_not_applicable_rule_ids",
            "packet",
        }:
            raise EffectiveRuleError(f"{label} must contain the exact route contract")
        route_id = route.get("route_id")
        if not isinstance(route_id, str) or ROUTE_ID_RE.fullmatch(route_id) is None or route_id in route_ids:
            raise EffectiveRuleError(f"{label}.route_id must be a unique ROUTE-* ID")
        selector = _validate_selector(route.get("selector"), profile, label)
        if route_id != route_id_for_selector(selector):
            raise EffectiveRuleError(f"{label}.route_id does not match its exact selector digest")
        required_rule_ids = _ordered_unique_strings(route.get("required_rule_ids"), f"{label}.required_rule_ids")
        for rule_id in required_rule_ids:
            if rule_id not in rule_index or rule_id not in disposition_by_id:
                raise EffectiveRuleError(f"{label} references unresolved, unknown, or unpacketized rule ID {rule_id}")
        reported_not_applicable = _ordered_unique_strings(
            route.get("reported_not_applicable_rule_ids"),
            f"{label}.reported_not_applicable_rule_ids",
            allow_empty=True,
        )
        expected_not_applicable = [
            rule_id
            for rule_id in required_rule_ids
            if disposition_by_id[rule_id]["effective_disposition"] == "not-applicable"
        ]
        if reported_not_applicable != expected_not_applicable:
            raise EffectiveRuleError(
                f"{label}.reported_not_applicable_rule_ids does not exactly match the not-applicable subset"
            )
        packet = route.get("packet")
        expected_packet_path = f"{PACKET_DIRECTORY}/{route_id}.yaml"
        if (
            not isinstance(packet, dict)
            or set(packet) != {"path", "digest"}
            or packet.get("path") != expected_packet_path
            or not _is_sha256(packet.get("digest"))
        ):
            raise EffectiveRuleError(f"{label}.packet must name the exact route packet and digest")
        key = _selector_key(selector)
        if key in routes:
            raise EffectiveRuleError(f"{label} duplicates an exact selector tuple")
        route_ids.add(route_id)
        route_order.append(route_id)
        routes[key] = {**route, "selector": selector}
    if route_order != sorted(route_order):
        raise EffectiveRuleError("effective state routing must be ascending by route_id")
    if require_packets:
        for route in routes.values():
            _validate_packet(
                root,
                state,
                catalogs,
                disposition_by_id,
                route,
            )
    return state, catalogs, disposition_by_id, routes


def _catalog_selector(catalog_id: str, record: dict[str, Any]) -> dict[str, Any]:
    if catalog_id == "shared":
        selector = record.get("catalog_selector")
    else:
        projection = record.get("catalog_projection")
        selector = projection.get("selector") if isinstance(projection, dict) else None
    if not isinstance(selector, dict):
        raise EffectiveRuleError("catalog record selector is unavailable")
    return copy.deepcopy(selector)


def _build_packet_from_inputs(
    state: dict[str, Any],
    catalogs: dict[str, dict[str, Any]],
    dispositions: dict[str, dict[str, Any]],
    route: dict[str, Any],
    resolver_evidence: list[str],
) -> dict[str, Any]:
    """Build one packet from already-validated state inputs without I/O."""
    if not _non_empty_references(resolver_evidence):
        raise EffectiveRuleError("resolver evidence must be non-empty unique repository references")
    technology_profile = state["framework"]["selected_technology_profile"]
    rule_index = _catalog_rule_index(catalogs)
    rules: list[dict[str, Any]] = []
    for rule_id in route["required_rule_ids"]:
        catalog_id, catalog_rule = rule_index[rule_id]
        disposition = dispositions[rule_id]
        catalog_statement_digest = _catalog_normative_digest(
            catalog_id,
            catalog_rule,
            f"catalog rule {rule_id}",
        )
        if disposition["effective_disposition"] == "target-semantic-delta":
            semantic_delta = disposition["semantic_delta"]
            effective_statement = semantic_delta["effective_normative_statement"]
            effective_statement_digest = semantic_delta[
                "effective_normative_statement_digest"
            ]
        else:
            effective_statement = catalog_rule["normative_text"]
            effective_statement_digest = catalog_statement_digest
        rules.append(
            {
                "rule_id": rule_id,
                "catalog_id": catalog_id,
                "catalog_selector": _catalog_selector(catalog_id, catalog_rule),
                "catalog_normative_statement_digest": catalog_statement_digest,
                "effective_disposition": disposition["effective_disposition"],
                "normative_statement": effective_statement,
                "normative_statement_digest": effective_statement_digest,
                "disposition_record": copy.deepcopy(disposition),
            }
        )
    catalog_records = [
        {
            "catalog_id": catalog_id,
            "path": (
                SHARED_CATALOG_PATH
                if catalog_id == "shared"
                else _profile_catalog_path(technology_profile)
            ),
            "digest": catalogs[catalog_id]["digest"],
        }
        for catalog_id in ("selected-profile", "shared")
    ]
    catalog_records.sort(key=lambda value: value["catalog_id"])
    packet = {
        "schema_version": "1.0",
        "packet_id": packet_id_for_route(route["route_id"], state["target_state_digest"]),
        "resolver": {
            "version": RESOLVER_SCHEMA_VERSION,
            "evidence": sorted(resolver_evidence),
        },
        "request": {"route_id": route["route_id"], **route["selector"]},
        "baseline": {
            "framework_version": state["framework"]["version"],
            "framework_commit": state["framework"]["commit"],
            "selected_technology_profile": technology_profile,
        },
        "target_state": {"path": EFFECTIVE_STATE_PATH, "digest": state["target_state_digest"]},
        "catalogs": catalog_records,
        "loaded_rule_ids": list(route["required_rule_ids"]),
        "rules": rules,
        "freshness": {
            "status": "verified",
            "verified_inputs": {
                "target_state_digest": state["target_state_digest"],
                "catalog_digests": copy.deepcopy(catalog_records),
            },
        },
    }
    packet["packet_digest"] = packet_digest(packet)
    return packet


def build_packet_candidate(
    root: Path,
    *,
    capability: str,
    execution_mode: str,
    technology_profile: str,
    file_type: str,
    resolver_evidence: list[str],
) -> dict[str, Any]:
    """Build a deterministic packet candidate for explicit reconciliation only.

    This function does not write a packet and does not make a missing packet
    usable for routine action execution.  Reconciliation records its digest in
    effective-rules.yaml before the candidate is placed at the declared path.
    """
    root = root.resolve()
    state, catalogs, dispositions, routes = _load_state_inputs(root, require_packets=False)
    selector = {
        "capability": capability,
        "execution_mode": execution_mode,
        "technology_profile": technology_profile,
        "file_type": file_type,
    }
    route = routes.get(_selector_key(selector))
    if route is None:
        raise EffectiveRuleError("unresolved effective state: no exact routing record")
    if route["selector"] != selector:
        raise EffectiveRuleError("unresolved effective state: routing selector mismatch")
    return _build_packet_from_inputs(state, catalogs, dispositions, route, resolver_evidence)


def build_effective_state_and_packets(
    root: Path,
    state_candidate: dict[str, Any],
    *,
    resolver_evidence: list[str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Derive one complete state plus all packets from explicit target evidence.

    Installation, upgrade, owner-decision, and reconciliation callers may use
    this pure builder before the staged writer below.  It never invents a
    disposition, route, applicability predicate, or baseline acceptance.
    """
    root = root.resolve()
    provenance, ledger, provenance_path, ledger_path = _validated_target_authorities(root)
    if not isinstance(state_candidate, dict):
        raise EffectiveRuleError("effective-state candidate must be a mapping")
    allowed = {"schema_version", "framework", "rule_dispositions", "routing", "generated_at"}
    unknown = set(state_candidate) - allowed
    if unknown:
        raise EffectiveRuleError(f"effective-state candidate has unsupported fields: {sorted(unknown)}")
    if state_candidate.get("schema_version") != "1.0":
        raise EffectiveRuleError("effective-state candidate has unsupported schema_version")
    framework = state_candidate.get("framework")
    if not isinstance(framework, dict) or set(framework) != {
        "version",
        "commit",
        "selected_technology_profile",
    }:
        raise EffectiveRuleError("effective-state candidate framework must be complete and explicit")
    version = framework.get("version")
    commit = framework.get("commit")
    profile = framework.get("selected_technology_profile")
    if (
        not isinstance(version, str)
        or SEMVER_TAG_RE.fullmatch(version) is None
        or not isinstance(commit, str)
        or GIT_SHA_RE.fullmatch(commit) is None
        or not is_profile_slug(profile)
    ):
        raise EffectiveRuleError("effective-state candidate framework identity is invalid")
    source = provenance.get("source")
    if provenance.get("effective_rules") != PROVENANCE_EFFECTIVE_RULES_LINKAGE:
        raise EffectiveRuleError("effective-state candidate requires exact provenance linkage")
    selection = provenance.get("selection")
    selected_profiles = selection.get("profiles") if isinstance(selection, dict) else None
    if (
        not isinstance(source, dict)
        or source.get("version") != version
        or source.get("commit") != commit
        or not isinstance(selected_profiles, list)
        or profile not in selected_profiles
    ):
        raise EffectiveRuleError("effective-state candidate does not match current target provenance")
    catalogs = _catalogs_for_profile(root, profile)
    rule_index = _catalog_rule_index(catalogs)
    customizations = _customization_index(ledger)
    raw_dispositions = state_candidate.get("rule_dispositions")
    if not isinstance(raw_dispositions, list) or not raw_dispositions:
        raise EffectiveRuleError("effective-state candidate requires explicit rule_dispositions")
    dispositions: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(raw_dispositions):
        rule_id = raw.get("rule_id") if isinstance(raw, dict) else None
        if rule_id not in rule_index:
            raise EffectiveRuleError(
                f"effective-state candidate disposition[{index}] references unknown or unpacketized rule ID"
            )
        if rule_id in dispositions:
            raise EffectiveRuleError(f"effective-state candidate duplicates disposition {rule_id}")
        dispositions[rule_id] = copy.deepcopy(
            _validate_disposition(
                raw,
                label=f"effective-state candidate disposition[{index}]",
                catalog_rule=rule_index[rule_id][1],
                customizations=customizations,
            )
        )
    raw_routes = state_candidate.get("routing")
    if not isinstance(raw_routes, list) or not raw_routes:
        raise EffectiveRuleError("effective-state candidate requires explicit routing")
    routes: list[dict[str, Any]] = []
    seen_selectors: set[bytes] = set()
    for index, raw in enumerate(raw_routes):
        label = f"effective-state candidate routing[{index}]"
        if not isinstance(raw, dict) or not {
            "selector",
            "required_rule_ids",
            "reported_not_applicable_rule_ids",
        }.issubset(raw):
            raise EffectiveRuleError(
                f"{label} must declare selector, required_rule_ids, and reported_not_applicable_rule_ids"
            )
        if set(raw) - {
            "route_id",
            "selector",
            "required_rule_ids",
            "reported_not_applicable_rule_ids",
        }:
            raise EffectiveRuleError(f"{label} contains generated or unsupported fields")
        selector = _validate_selector(raw["selector"], profile, label)
        key = _selector_key(selector)
        if key in seen_selectors:
            raise EffectiveRuleError(f"{label} duplicates an exact selector tuple")
        seen_selectors.add(key)
        route_id = route_id_for_selector(selector)
        supplied_route_id = raw.get("route_id")
        if supplied_route_id is not None and supplied_route_id != route_id:
            raise EffectiveRuleError(f"{label}.route_id does not match its selector digest")
        required_rule_ids = _ordered_unique_strings(raw["required_rule_ids"], f"{label}.required_rule_ids")
        for rule_id in required_rule_ids:
            if rule_id not in dispositions:
                raise EffectiveRuleError(f"{label} names a rule without an explicit disposition: {rule_id}")
        reported_not_applicable = _ordered_unique_strings(
            raw["reported_not_applicable_rule_ids"],
            f"{label}.reported_not_applicable_rule_ids",
            allow_empty=True,
        )
        expected_not_applicable = [
            rule_id
            for rule_id in required_rule_ids
            if dispositions[rule_id]["effective_disposition"] == "not-applicable"
        ]
        if reported_not_applicable != expected_not_applicable:
            raise EffectiveRuleError(
                f"{label}.reported_not_applicable_rule_ids does not exactly match the not-applicable subset"
            )
        routes.append(
            {
                "route_id": route_id,
                "selector": selector,
                "required_rule_ids": required_rule_ids,
                "reported_not_applicable_rule_ids": reported_not_applicable,
                "packet": {
                    "path": f"{PACKET_DIRECTORY}/{route_id}.yaml",
                    "digest": "0" * 64,
                },
            }
        )
    ordered_dispositions = [dispositions[rule_id] for rule_id in sorted(dispositions)]
    routes.sort(key=lambda route: route["route_id"])
    state: dict[str, Any] = {
        "schema_version": "1.0",
        "framework": copy.deepcopy(framework),
        "catalogs": [
            {
                "catalog_id": catalog_id,
                "path": SHARED_CATALOG_PATH if catalog_id == "shared" else _profile_catalog_path(profile),
                "digest": catalogs[catalog_id]["digest"],
            }
            for catalog_id in ("selected-profile", "shared")
        ],
        "target_authorities": {
            "provenance": {
                "path": PROVENANCE_PATH,
                "digest": _sha256_bytes(provenance_path.read_bytes()),
            },
            "customizations": {
                "path": CUSTOMIZATIONS_PATH,
                "digest": _sha256_bytes(ledger_path.read_bytes()),
            },
        },
        "rule_dispositions": ordered_dispositions,
        "routing": routes,
    }
    if "generated_at" in state_candidate:
        if not isinstance(state_candidate["generated_at"], str) or not state_candidate["generated_at"]:
            raise EffectiveRuleError("effective-state candidate generated_at must be non-empty when supplied")
        state["generated_at"] = state_candidate["generated_at"]
    state["target_state_digest"] = target_state_digest(state)
    packets: dict[str, dict[str, Any]] = {}
    for route in state["routing"]:
        packet = _build_packet_from_inputs(
            state, catalogs, dispositions, route, resolver_evidence
        )
        route["packet"]["digest"] = packet["packet_digest"]
        packets[route["packet"]["path"]] = packet
    if state["target_state_digest"] != target_state_digest(state):
        raise EffectiveRuleError("derived packet metadata unexpectedly changed target state digest")
    return state, packets


def write_effective_state_and_packets(
    root: Path,
    state: dict[str, Any],
    packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Publish packets first and state last with in-process exception rollback.

    This is not cross-file crash atomicity. A crash-mixed candidate remains
    unusable because subsequent digest and freshness validation fails closed.
    """
    root = root.resolve()
    if not isinstance(state, dict) or not isinstance(packets, dict):
        raise EffectiveRuleError("effective state and packets must be mappings")
    routing = state.get("routing")
    if not isinstance(routing, list) or not routing:
        raise EffectiveRuleError("effective state must contain complete routing before publish")
    expected_paths = {
        route.get("packet", {}).get("path")
        for route in routing
        if isinstance(route, dict) and isinstance(route.get("packet"), dict)
    }
    if (
        None in expected_paths
        or not all(isinstance(path, str) and path.startswith(f"{PACKET_DIRECTORY}/") for path in expected_paths)
        or set(packets) != expected_paths
        or not all(isinstance(packet, dict) for packet in packets.values())
    ):
        raise EffectiveRuleError("effective packet set must exactly match declared routing paths")
    context = root / ".dev/ai-context"
    if context.is_symlink() or (context.exists() and not context.is_dir()):
        raise EffectiveRuleError("target effective-state directory must be a regular directory")
    documents: dict[str, dict[str, Any]] = {EFFECTIVE_STATE_PATH: state, **packets}
    destinations: dict[str, Path] = {}
    for relative in documents:
        if not _safe_target_path(relative) or relative != EFFECTIVE_STATE_PATH and not relative.startswith(f"{PACKET_DIRECTORY}/"):
            raise EffectiveRuleError(f"unsafe target-effective document path: {relative!r}")
        _reject_unsafe_parent_chain(root, relative)
        destination = root / Path(*PurePosixPath(relative).parts)
        if destination.is_symlink() or destination.exists() and not destination.is_file():
            raise EffectiveRuleError(f"target-effective document must be a regular file: {relative}")
        destinations[relative] = destination
    context.mkdir(parents=True, exist_ok=True)
    snapshots = {
        relative: (destination.read_bytes(), destination.stat().st_mode)
        if destination.is_file()
        else None
        for relative, destination in destinations.items()
    }
    temporary: dict[str, Path] = {}
    try:
        for relative, document in documents.items():
            handle = tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                delete=False,
                dir=context,
                prefix=".effective-rule-",
                suffix=".candidate",
            )
            with handle:
                yaml.safe_dump(document, handle, sort_keys=False, allow_unicode=True)
            temporary[relative] = Path(handle.name)
        replacement_order = [
            *sorted(packets, key=lambda value: value.encode("utf-8")),
            EFFECTIVE_STATE_PATH,
        ]
        for relative in replacement_order:
            destination = destinations[relative]
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(temporary[relative], destination)
        errors = validate_effective_rule_state(root, require_packets=True)
        if errors:
            raise EffectiveRuleError("; ".join(errors))
    except Exception as exc:
        for relative, snapshot in snapshots.items():
            destination = destinations[relative]
            if snapshot is None:
                if destination.exists() and destination.is_file():
                    destination.unlink()
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(snapshot[0])
                os.chmod(destination, snapshot[1])
        if isinstance(exc, EffectiveRuleError):
            raise
        raise EffectiveRuleError(f"effective rule publication rolled back: {exc}") from exc
    finally:
        for path in temporary.values():
            if path.exists():
                path.unlink()
    return {
        "state_path": EFFECTIVE_STATE_PATH,
        "target_state_digest": state["target_state_digest"],
        "packet_paths": sorted(packets),
        "packet_digests": {
            path: packet["packet_digest"] for path, packet in sorted(packets.items())
        },
    }


def _validate_packet(
    root: Path,
    state: dict[str, Any],
    catalogs: dict[str, dict[str, Any]],
    dispositions: dict[str, dict[str, Any]],
    route: dict[str, Any],
) -> dict[str, Any]:
    packet_relative = route["packet"]["path"]
    packet_path = _regular_repo_file(root, packet_relative, "effective rule packet")
    packet = _read_mapping(root, packet_relative, "effective rule packet")
    if packet.get("schema_version") != "1.0":
        raise EffectiveRuleError(f"{packet_path}: unsupported packet schema_version")
    expected_packet_id = packet_id_for_route(route["route_id"], state["target_state_digest"])
    if packet.get("packet_id") != expected_packet_id or PACKET_ID_RE.fullmatch(packet["packet_id"]) is None:
        raise EffectiveRuleError(f"{packet_path}: packet_id is invalid")
    resolver = packet.get("resolver")
    if (
        not isinstance(resolver, dict)
        or not isinstance(resolver.get("version"), str)
        or not resolver["version"]
        or not _non_empty_references(resolver.get("evidence"))
    ):
        raise EffectiveRuleError(f"{packet_path}: resolver evidence is invalid")
    request = packet.get("request")
    expected_request = {"route_id": route["route_id"], **route["selector"]}
    if request != expected_request:
        raise EffectiveRuleError(f"{packet_path}: request does not exactly match route")
    baseline = packet.get("baseline")
    expected_baseline = {
        "framework_version": state["framework"]["version"],
        "framework_commit": state["framework"]["commit"],
        "selected_technology_profile": state["framework"]["selected_technology_profile"],
    }
    if baseline != expected_baseline:
        raise EffectiveRuleError(f"{packet_path}: baseline does not match effective state")
    if packet.get("target_state") != {"path": EFFECTIVE_STATE_PATH, "digest": state["target_state_digest"]}:
        raise EffectiveRuleError(f"{packet_path}: target state is stale")
    expected_catalogs = [
        {
            "catalog_id": catalog_id,
            "path": SHARED_CATALOG_PATH if catalog_id == "shared" else _profile_catalog_path(expected_baseline["selected_technology_profile"]),
            "digest": catalogs[catalog_id]["digest"],
        }
        for catalog_id in ("selected-profile", "shared")
    ]
    expected_catalogs.sort(key=lambda value: value["catalog_id"])
    if packet.get("catalogs") != expected_catalogs:
        raise EffectiveRuleError(f"{packet_path}: catalogs are stale or ambiguous")
    loaded = _ordered_unique_strings(packet.get("loaded_rule_ids"), f"{packet_path}: loaded_rule_ids")
    if loaded != route["required_rule_ids"]:
        raise EffectiveRuleError(f"{packet_path}: loaded_rule_ids do not exactly match route")
    rule_index = _catalog_rule_index(catalogs)
    rules = packet.get("rules")
    if not isinstance(rules, list) or len(rules) != len(loaded):
        raise EffectiveRuleError(f"{packet_path}: rules must exactly cover loaded_rule_ids")
    observed_ids: list[str] = []
    for index, packet_rule in enumerate(rules):
        label = f"{packet_path}: rules[{index}]"
        if not isinstance(packet_rule, dict):
            raise EffectiveRuleError(f"{label} must be a mapping")
        rule_id = packet_rule.get("rule_id")
        if rule_id not in rule_index or rule_id not in dispositions:
            raise EffectiveRuleError(f"{label} has unknown, duplicate, type-invalid, or unpacketized ID")
        catalog_id, catalog_rule = rule_index[rule_id]
        disposition = dispositions[rule_id]
        catalog_statement_digest = _catalog_normative_digest(
            catalog_id,
            catalog_rule,
            f"catalog rule {rule_id}",
        )
        if disposition["effective_disposition"] == "target-semantic-delta":
            semantic_delta = disposition["semantic_delta"]
            effective_statement = semantic_delta["effective_normative_statement"]
            effective_statement_digest = semantic_delta[
                "effective_normative_statement_digest"
            ]
        else:
            effective_statement = catalog_rule["normative_text"]
            effective_statement_digest = catalog_statement_digest
        expected_rule = {
            "rule_id": rule_id,
            "catalog_id": catalog_id,
            "catalog_selector": _catalog_selector(catalog_id, catalog_rule),
            "catalog_normative_statement_digest": catalog_statement_digest,
            "effective_disposition": disposition["effective_disposition"],
            "normative_statement": effective_statement,
            "normative_statement_digest": effective_statement_digest,
            "disposition_record": disposition,
        }
        if packet_rule != expected_rule:
            raise EffectiveRuleError(f"{label} does not preserve exact effective semantics")
        observed_ids.append(rule_id)
    if observed_ids != loaded:
        raise EffectiveRuleError(f"{packet_path}: rules are not in loaded_rule_ids order")
    freshness = packet.get("freshness")
    expected_freshness = {
        "status": "verified",
        "verified_inputs": {
            "target_state_digest": state["target_state_digest"],
            "catalog_digests": expected_catalogs,
        },
    }
    if freshness != expected_freshness:
        raise EffectiveRuleError(f"{packet_path}: freshness inputs are stale")
    actual_digest = packet_digest(packet)
    if packet.get("packet_digest") != actual_digest or route["packet"]["digest"] != actual_digest:
        raise EffectiveRuleError(f"{packet_path}: packet digest mismatch")
    return packet


def validate_effective_rule_state(root: Path, *, require_packets: bool = True) -> list[str]:
    """Return fail-closed errors for a present target-effective state."""
    try:
        _load_state_inputs(root.resolve(), require_packets=require_packets)
    except EffectiveRuleError as exc:
        return [str(exc)]
    return []


def resolve_effective_rule_packet(
    root: Path,
    *,
    capability: str,
    execution_mode: str,
    technology_profile: str,
    file_type: str,
) -> dict[str, Any]:
    """Resolve one existing freshness-validated task-scoped rule packet."""
    root = root.resolve()
    state, catalogs, dispositions, routes = _load_state_inputs(root, require_packets=True)
    selector = {
        "capability": capability,
        "execution_mode": execution_mode,
        "technology_profile": technology_profile,
        "file_type": file_type,
    }
    route = routes.get(_selector_key(selector))
    if route is None:
        raise EffectiveRuleError(
            "unresolved effective state: no exact route for capability/execution_mode/profile/file_type"
        )
    return _validate_packet(root, state, catalogs, dispositions, route)


def resolve_framework_source_rule_packet(
    root: Path,
    *,
    capability: str,
    execution_mode: str,
    technology_profile: str,
    file_type: str,
    source_rule_ids: list[str] | None,
    selection_evidence: list[str] | None,
) -> dict[str, Any]:
    """Resolve a transient framework-source packet from committed source bytes.

    This path deliberately has no dependency on a downstream target's
    provenance, effective state, or packet directory.  It only accepts an
    explicit source policy and an explicit caller-selected rule list.
    """
    root = Path(root).resolve()
    policy_blob, _ = _source_head_bound_file(root, SOURCE_EFFECTIVE_RULES_POLICY_PATH)
    try:
        policy_document = _read_mapping_bytes(
            policy_blob,
            "framework-source effective-rule policy",
        )
        policy = _validated_source_policy(policy_document)
    except SourceEffectiveRuleError:
        raise
    except EffectiveRuleError as exc:
        raise _source_error("source-applicability", str(exc)) from exc
    canonical_root, source_repository = _source_repository_identity(root, policy)

    head_blobs: dict[str, bytes] = {}
    for relative in sorted(policy["required_paths"]):
        blob, _ = _source_head_bound_file(canonical_root, relative)
        head_blobs[relative] = blob
    _validated_source_evidence_schema(
        head_blobs[SOURCE_EFFECTIVE_RULE_EVIDENCE_SCHEMA_PATH]
    )

    request = _source_request(
        capability=capability,
        execution_mode=execution_mode,
        technology_profile=technology_profile,
        file_type=file_type,
    )
    profile_path = policy["profile_paths"].get(request["technology_profile"])
    if profile_path is None:
        raise _source_error(
            "source-rule-selection",
            "technology profile has no exact source catalog route",
        )
    loaded_rule_ids = _source_rule_ids(source_rule_ids)
    evidence = _source_selection_evidence(selection_evidence)
    _source_verify_selection_evidence(canonical_root, evidence)
    catalogs_by_id = _source_catalogs(
        head_blobs,
        request["technology_profile"],
        profile_path,
    )
    rule_index = _catalog_rule_index(catalogs_by_id)
    rules: list[dict[str, Any]] = []
    for rule_id in loaded_rule_ids:
        record = rule_index.get(rule_id)
        if record is None:
            raise _source_error(
                "source-rule-selection",
                f"source rule ID is unknown or ambiguous: {rule_id}",
            )
        catalog_id, catalog_rule = record
        normative_statement = catalog_rule["normative_text"]
        rules.append(
            {
                "rule_id": rule_id,
                "catalog_id": catalog_id,
                "catalog_selector": _catalog_selector(catalog_id, catalog_rule),
                "normative_statement": normative_statement,
                "normative_statement_digest": _catalog_normative_digest(
                    catalog_id,
                    catalog_rule,
                    f"source catalog rule {rule_id}",
                ),
            }
        )
    catalogs = [
        {
            "catalog_id": catalog_id,
            "path": (
                SHARED_CATALOG_PATH
                if catalog_id == "shared"
                else profile_path
            ),
            "digest": catalogs_by_id[catalog_id]["digest"],
        }
        for catalog_id in ("selected-profile", "shared")
    ]
    catalogs.sort(key=lambda record: record["catalog_id"])
    final_head_blobs: dict[str, bytes] = {}
    final_execution_files: list[dict[str, str]] = []
    for relative in sorted(policy["required_paths"]):
        blob, execution_file = _source_head_bound_file(canonical_root, relative)
        final_head_blobs[relative] = blob
        final_execution_files.append(execution_file)
    if final_head_blobs != head_blobs:
        raise _source_error(
            "source-execution-digest",
            "required source execution blobs changed while resolving",
        )
    final_root, final_repository = _source_repository_identity(canonical_root, policy)
    if final_root != canonical_root or final_repository != source_repository:
        raise _source_error(
            "source-repository",
            "source repository identity changed while resolving",
        )
    source_repository = {
        **final_repository,
        "git_status": _source_repository_status(final_root),
    }
    packet: dict[str, Any] = {
        "schema_version": "1.0",
        "resolver_outcome": "resolved",
        "applicability_mode": "framework-source",
        "source_repository": source_repository,
        "execution_files": final_execution_files,
        "request": request,
        "selection_evidence": evidence,
        "catalogs": catalogs,
        "loaded_rule_ids": loaded_rule_ids,
        "rules": rules,
        "freshness": {
            "status": "verified",
            "verified_inputs": {
                "repository_commit": source_repository["commit"],
                "execution_file_digests": [
                    {
                        "path": record["path"],
                        "blob_digest": record["blob_digest"],
                    }
                    for record in final_execution_files
                ],
                "catalog_digests": copy.deepcopy(catalogs),
            },
        },
    }
    packet["packet_digest"] = packet_digest(packet)
    return packet


def resolve_effective_rule_packet_for_mode(
    root: Path,
    *,
    applicability_mode: str,
    capability: str,
    execution_mode: str,
    technology_profile: str,
    file_type: str,
    source_rule_ids: list[str] | None = None,
    selection_evidence: list[str] | None = None,
) -> dict[str, Any]:
    """Resolve one packet only through an explicit applicability mode."""
    if applicability_mode not in APPLICABILITY_MODES:
        raise EffectiveRuleError(
            "applicability mode must be explicitly framework-source or initialized-target"
        )
    dimensions = {
        "capability": capability,
        "execution_mode": execution_mode,
        "technology_profile": technology_profile,
        "file_type": file_type,
    }
    if applicability_mode == "framework-source":
        return resolve_framework_source_rule_packet(
            root,
            **dimensions,
            source_rule_ids=source_rule_ids,
            selection_evidence=selection_evidence,
        )
    if source_rule_ids is not None or selection_evidence is not None:
        raise EffectiveRuleError(
            "downstream-semantics-unresolved: source-only selection arguments are invalid for initialized-target mode"
        )
    return resolve_effective_rule_packet(root, **dimensions)


def initialized_target_diagnostic(error: EffectiveRuleError) -> str:
    """Classify a retained initialized-target error for CLI diagnostics only.

    The underlying public APIs keep their established detailed messages.  This
    lightweight classifier adds a stable downstream category at the CLI
    boundary so source-only and downstream failures cannot be confused.
    """
    detail = str(error)
    if detail.startswith("downstream-"):
        return detail
    normalized = detail.casefold()
    if any(
        token in normalized
        for token in (
            "target provenance",
            "target customizations",
            "target authority contract",
            "provenance linkage",
        )
    ):
        category = "downstream-provenance-missing"
    elif any(
        token in normalized
        for token in (
            "stale",
            "digest",
            "packet",
            "effective state",
            "catalog",
        )
    ):
        category = "downstream-state-stale"
    else:
        category = "downstream-semantics-unresolved"
    return f"{category}: {detail}"
