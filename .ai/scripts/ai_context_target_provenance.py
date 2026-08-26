#!/usr/bin/env python3
"""Downstream AI context provenance and semantic customization contracts."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
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


def validate_pending_apply_receipt(root: Path, errors: list[str]) -> None:
    """Validate selected managed bytes and ignore state carried by a new receipt."""
    receipt_path = root / PENDING_APPLY_RECEIPT
    if receipt_path.is_symlink():
        errors.append(f"{receipt_path}: pending apply receipt must not be a symlink")
        return
    if not receipt_path.is_file():
        return
    receipt = load_mapping(receipt_path, errors)
    if receipt is None:
        return
    if receipt.get("schema_version") not in {"1.0.0", "1.1.0"}:
        errors.append(f"{receipt_path}: unsupported pending apply receipt schema")
        return
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
        candidate = root / Path(*PurePosixPath(path).parts)
        if candidate.is_symlink() or not candidate.is_file():
            errors.append(f"required framework-managed path is absent: {path}")
            continue
        if isinstance(expected_sha, str) and re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            actual_sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_sha != expected_sha:
                errors.append(
                    f"required framework-managed path bytes differ: {path}"
                )
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


def validate_manifest(path: Path, errors: list[str]) -> None:
    data = load_mapping(path, errors)
    if data is None:
        return
    if data.get("schema_version") != "2.0":
        errors.append(f"{path}: schema_version must be 2.0")
        return
    version = validate_source(data.get("source"), str(path), errors)
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
    context = root / ".dev/ai-context"
    legacy = root / ".dev/AI-CONTEXT-SOURCE.yaml"
    provenance_path = context / "provenance.yaml"
    ledger_path = context / "customizations.yaml"
    if legacy.is_file():
        raise TargetValidationError("legacy provenance must be reconciled before finalization")
    if provenance_path.exists() and not allow_existing:
        raise TargetValidationError("component-aware provenance already exists")
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
    pending_errors: list[str] = []
    validate_pending_apply_receipt(root, pending_errors)
    if pending_errors:
        raise TargetValidationError("; ".join(pending_errors))
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
        if errors:
            raise TargetValidationError("; ".join(errors))
        previous = {
            path: path.read_bytes() if path.is_file() else None
            for path in (provenance_path, ledger_path)
        }
        try:
            os.replace(temporary_paths[1], ledger_path)
            os.replace(temporary_paths[0], provenance_path)
            if effective_state_candidate is not None:
                state, packets = build_effective_state_and_packets(
                    root,
                    effective_state_candidate,
                    resolver_evidence=effective_resolver_evidence or [],
                )
                write_effective_state_and_packets(root, state, packets)
        except Exception:
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
    return {
        "status": "finalized",
        "effective_rule_readiness": effective_rule_readiness(root),
    }


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
