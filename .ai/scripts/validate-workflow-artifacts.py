#!/usr/bin/env python3
"""Validate the shared locator and minimum metadata for new workflows."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import yaml


ADOPTION_DATE = date(2026, 7, 10)
BRANCH_POLICY_DATE = date(2026, 7, 11)
IMPLEMENTATION_CONTRACT_DATE = date(2026, 7, 14)
DEVELOPMENT_ACCEPTANCE_CONTRACT_AT = datetime.fromisoformat(
    "2026-07-24T08:10:00+08:00"
)
DEV_TASK_TEMPLATE = ".ai/assets/skills/software-development-orchestrator/templates/development-workflow-task-template.json"
DEV_LOCATOR_TEMPLATE = ".ai/assets/skills/software-development-orchestrator/templates/workflow-locator-template.yaml"
LEGACY_SKILL_REFERENCE_PREFIXES = {
    ".ai/assets/skills/repo-structure-sync/": ".ai/assets/skills/ai-context-init/",
    ".ai/assets/skills/dev-workflow/": ".ai/assets/skills/software-development-orchestrator/",
}
EXECUTION_MODES = {"command", "query", "reactor", "generic"}
IMPLEMENTATION_INTENTS = {
    "feature",
    "bug-fix",
    "review-remediation",
    "validation-failure-remediation",
    "behavior-correction",
    "refactor",
    "cleanup",
}
IMPLEMENTATION_OVERLAYS = {"remediation"}
REMEDIATION_INTENTS = {"review-remediation", "validation-failure-remediation"}
APPROVAL_STATUSES = {"not-required", "awaiting-approval", "approved"}
TEST_PROVIDERS = {
    "target-profile-commands",
    "evaluated-external-skill",
    "fallback-contract",
}
DEFAULT_TEST_LEVELS = {"unit", "integration"}
CONDITIONAL_TEST_LEVELS = {
    "e2e",
    "browser",
    "playwright",
    "environment-dependent",
}
TEST_OUTCOMES = {
    "passed",
    "failed",
    "blocked-by-environment",
    "not-applicable",
    "deferred-with-owner",
}
COMPLIANCE_OUTCOMES = {
    "pending",
    "100-percent-pass",
    "failed-closed",
    "not-applicable",
}
WORKFLOW_STATUSES = {"planned", "in_progress", "completed", "blocked", "cancelled"}
TASK_STATUSES = {"pending", "in_progress", "completed", "deferred", "blocked", "cancelled"}
TERMINAL_TASK_STATUSES = {"completed", "deferred", "cancelled"}
ID_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-[a-z0-9][a-z0-9-]*$")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REQUIRED_LOCATOR = {
    "schema_version",
    "workflow_id",
    "workflow_kind",
    "title",
    "owner_skill",
    "status",
    "artifact_root",
    "entrypoint",
    "created_at",
    "updated_at",
    "template_source",
    "template_version",
}
REQUIRED_TASK = {
    "task_id",
    "workflow_id",
    "owner_skill",
    "status",
    "created_at",
    "updated_at",
    "template_source",
    "template_version",
}
BACKLOG_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BACKLOG_STATUSES = {"open", "planned", "in_progress", "resolved", "declined"}
RELEASE_VERSION_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$")
WORKFLOW_INDEX_ROW = re.compile(
    r"^\| \[`([^`]+)`\]\(([^)]+/workflow\.yaml)\) \| (.*?) \| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| \[plan\]\(([^)]+)\) \|$"
)
LEGACY_INDEX_ROW = re.compile(
    r"^\| \[`([^`]+)`\]\(([^)]+/)\) \| legacy / no locator \|$"
)
BACKLOG_INDEX_ROW = re.compile(
    r"^\| \[([^]]+)\]\((items/[^)]+\.yaml)\) \|"
)


def parse_flat_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def parse_yaml_mapping(path: Path, label: str, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{label}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: YAML root must be a mapping")
        return None
    return value


def reference_path(repo: Path, value: str) -> Path:
    return repo / value.split("#", 1)[0]


def reference_exists_with_compatibility(repo: Path, value: str) -> bool:
    if reference_path(repo, value).exists():
        return True
    path_value, _, fragment = value.partition("#")
    for legacy, active in LEGACY_SKILL_REFERENCE_PREFIXES.items():
        if path_value.startswith(legacy):
            replacement = active + path_value[len(legacy) :]
            if fragment:
                replacement = f"{replacement}#{fragment}"
            return reference_path(repo, replacement).exists()
    return False


def validate_backlog_release(
    release: object,
    backlog_status: str,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(release, dict):
        errors.append(f"{label}: release must be a mapping")
        return
    required = {"target", "completed_in", "published_in"}
    missing = sorted(required - release.keys())
    if missing:
        errors.append(f"{label}: release missing fields {', '.join(missing)}")
        return

    target = release["target"]
    if not isinstance(target, str) or (
        target != "unassigned" and not RELEASE_VERSION_RE.fullmatch(target)
    ):
        errors.append(f"{label}: release.target must be vMAJOR.MINOR.PATCH or unassigned")

    for key in ("completed_in", "published_in"):
        value = release[key]
        if value is not None and (
            not isinstance(value, str) or not RELEASE_VERSION_RE.fullmatch(value)
        ):
            errors.append(f"{label}: release.{key} must be null or vMAJOR.MINOR.PATCH")

    completed = release["completed_in"]
    published = release["published_in"]
    if backlog_status == "resolved" and completed is None:
        errors.append(f"{label}: resolved backlog item requires release.completed_in")
    if published is not None and completed is None:
        errors.append(f"{label}: release.published_in requires release.completed_in")


def validate_backlog(repo: Path, errors: list[str]) -> int:
    backlog_root = repo / ".dev" / "backlog"
    item_root = backlog_root / "items"
    index_path = backlog_root / "INDEX.MD"
    if not item_root.is_dir() or not index_path.is_file():
        errors.append(".dev/backlog: README, INDEX, and items directory are required")
        return 0

    index_rows: dict[str, str] = {}
    for line in index_path.read_text(encoding="utf-8").splitlines():
        match = BACKLOG_INDEX_ROW.match(line)
        if match:
            index_rows[match.group(1)] = match.group(2)

    item_paths = sorted(item_root.glob("*.yaml"))
    item_ids: set[str] = set()
    required = {
        "schema_version", "backlog_id", "title", "category", "status", "summary",
        "created_at", "updated_at", "origin_refs", "recommended_owner_skill",
        "handoff_condition", "workflow_refs", "task_refs", "resolution_ref", "release",
    }
    for path in item_paths:
        label = str(path.relative_to(repo))
        item = parse_yaml_mapping(path, label, errors)
        if item is None:
            continue
        missing = sorted(required - item.keys())
        if missing:
            errors.append(f"{label}: missing fields {', '.join(missing)}")
            continue
        backlog_id = item["backlog_id"]
        if not isinstance(backlog_id, str) or not BACKLOG_ID_RE.fullmatch(backlog_id):
            errors.append(f"{label}: backlog_id is not path-safe")
            continue
        if backlog_id != path.stem:
            errors.append(f"{label}: backlog_id must match file name")
        if backlog_id in item_ids:
            errors.append(f"{label}: duplicate backlog_id {backlog_id}")
        item_ids.add(backlog_id)
        if item["schema_version"] != "1.0":
            errors.append(f"{label}: schema_version must be 1.0")
        if item["status"] not in BACKLOG_STATUSES:
            errors.append(f"{label}: unsupported status {item['status']!r}")
        validate_backlog_release(item["release"], str(item["status"]), label, errors)
        created = timestamp(str(item["created_at"]), f"{label} created_at", errors)
        updated = timestamp(str(item["updated_at"]), f"{label} updated_at", errors)
        if created and updated and updated < created:
            errors.append(f"{label}: updated_at is earlier than created_at")
        for key in ("title", "category", "summary", "recommended_owner_skill", "handoff_condition"):
            if not isinstance(item[key], str) or not item[key]:
                errors.append(f"{label}: {key} must be a non-empty string")
        for key in ("origin_refs", "workflow_refs", "task_refs"):
            values = item[key]
            if not isinstance(values, list) or not all(isinstance(value, str) and value for value in values):
                errors.append(f"{label}: {key} must be a list of non-empty strings")
                continue
            for value in values:
                if not reference_exists_with_compatibility(repo, value):
                    errors.append(f"{label}: missing {key} path {value}")
        resolution = item["resolution_ref"]
        if resolution is not None and (
            not isinstance(resolution, str) or not resolution or not reference_path(repo, resolution).exists()
        ):
            errors.append(f"{label}: invalid resolution_ref {resolution!r}")
        if item["status"] == "resolved" and resolution is None:
            errors.append(f"{label}: resolved item requires resolution_ref")
        expected_link = f"items/{path.name}"
        if index_rows.get(backlog_id) != expected_link:
            errors.append(f"{label}: backlog INDEX row is missing or points to the wrong file")

    extra_rows = sorted(set(index_rows) - item_ids)
    if extra_rows:
        errors.append(f".dev/backlog/INDEX.MD: rows without item files {extra_rows}")
    return len(item_paths)


def backlog_provider_enabled(repo: Path, errors: list[str]) -> bool:
    """Resolve backlog applicability from source identity or governed provenance."""
    if (repo / ".ai/distribution/profiles/dotnet-backend.yaml").is_file():
        return True

    provenance_path = repo / ".dev/ai-context/provenance.yaml"
    legacy_path = repo / ".dev/AI-CONTEXT-SOURCE.yaml"
    if provenance_path.is_file() and legacy_path.is_file():
        errors.append(
            ".dev/ai-context: legacy and component-aware provenance authorities cannot coexist"
        )
        return False
    if provenance_path.is_file():
        provenance = parse_yaml_mapping(
            provenance_path,
            ".dev/ai-context/provenance.yaml",
            errors,
        )
        if provenance is None:
            return False
        selection = provenance.get("selection")
        providers = selection.get("providers") if isinstance(selection, dict) else None
        backlog = providers.get("repo-backlog") if isinstance(providers, dict) else None
        if (
            not isinstance(backlog, dict)
            or not isinstance(backlog.get("enabled"), bool)
            or backlog.get("preservation") != "preserve-existing-if-recorded"
        ):
            errors.append(
                ".dev/ai-context/provenance.yaml: invalid repo-backlog provider selection"
            )
            return False
        return backlog["enabled"]

    # Legacy targets predate explicit provider selection. Validate a retained
    # provider only when the legacy provenance and provider root both exist.
    return legacy_path.is_file() and (repo / ".dev/backlog").is_dir()


def validate_workflow_index(repo: Path, discovery_root: Path, errors: list[str]) -> int:
    index_path = discovery_root / "INDEX.MD"
    if not index_path.is_file():
        errors.append(".dev/workflows/INDEX.MD: missing workflow discovery index")
        return 0
    locator_rows: dict[str, tuple[str, str, str, str, str, str]] = {}
    legacy_rows: dict[str, str] = {}
    for line in index_path.read_text(encoding="utf-8").splitlines():
        locator_match = WORKFLOW_INDEX_ROW.match(line)
        if locator_match:
            workflow_id = locator_match.group(1)
            locator_rows[workflow_id] = locator_match.groups()[1:]
            continue
        legacy_match = LEGACY_INDEX_ROW.match(line)
        if legacy_match:
            legacy_rows[legacy_match.group(1)] = legacy_match.group(2)

    directories = {
        path.name: path
        for path in discovery_root.iterdir()
        if path.is_dir() and path.name != "templates"
    }
    expected_ids = set(directories)
    indexed_ids = set(locator_rows) | set(legacy_rows)
    if expected_ids != indexed_ids:
        errors.append(
            ".dev/workflows/INDEX.MD: directory coverage mismatch; "
            f"missing={sorted(expected_ids - indexed_ids)}, extra={sorted(indexed_ids - expected_ids)}"
        )

    for workflow_id, directory in directories.items():
        locator_path = directory / "workflow.yaml"
        if not locator_path.is_file():
            if legacy_rows.get(workflow_id) != f"{workflow_id}/":
                errors.append(f".dev/workflows/INDEX.MD: legacy row mismatch for {workflow_id}")
            continue
        locator = parse_yaml_mapping(
            locator_path, str(locator_path.relative_to(repo)), errors
        )
        if locator is None:
            continue
        row = locator_rows.get(workflow_id)
        if row is None:
            errors.append(f".dev/workflows/INDEX.MD: missing locator-backed row for {workflow_id}")
            continue
        locator_link, title, owner, status, updated_at, entrypoint_link = row
        expected = (
            f"{workflow_id}/workflow.yaml",
            str(locator.get("title", "")),
            str(locator.get("owner_skill", "")),
            str(locator.get("status", "")),
            str(locator.get("updated_at", "")),
            f"{workflow_id}/{locator.get('entrypoint', '')}",
        )
        actual = (locator_link, title, owner, status, updated_at, entrypoint_link)
        if actual != expected:
            errors.append(
                f".dev/workflows/INDEX.MD: row differs from {workflow_id}/workflow.yaml; "
                f"expected={expected}, actual={actual}"
            )
    return len(directories)


def timestamp(value: str, label: str, errors: list[str]) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label}: invalid ISO 8601 timestamp: {value}")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label}: timestamp must include UTC offset: {value}")
        return None
    return parsed


def validate_implementation_contract(
    task: dict, label: str, errors: list[str], task_created: datetime | None
) -> None:
    if task.get("template_source") != DEV_TASK_TEMPLATE:
        return
    if task_created is None or task_created.date() < IMPLEMENTATION_CONTRACT_DATE:
        return

    execution = task.get("execution")
    if not isinstance(execution, dict):
        errors.append(f"{label}: execution must be a mapping")
        return

    contract = execution.get("implementation_contract")
    is_implementation = (
        execution.get("capability_slot") == "implementation"
        or task.get("owner_skill") == "slice-implementer"
        or contract is not None
    )
    if not is_implementation:
        return
    if execution.get("capability_slot") != "implementation":
        errors.append(f"{label}: implementation_contract requires capability_slot implementation")
    if "mode" in execution:
        errors.append(f"{label}: use implementation_contract.execution_mode, not execution.mode")

    inputs = task.get("inputs")
    if isinstance(inputs, dict):
        for deprecated in ("source_truth", "source_findings"):
            if deprecated in inputs:
                errors.append(f"{label}: deprecated inputs.{deprecated} collapses source responsibilities")

    if not isinstance(contract, dict):
        errors.append(f"{label}: implementation task requires implementation_contract mapping")
        return

    required = {
        "intent",
        "execution_mode",
        "overlays",
        "authorization_source",
        "normative_truth",
        "finding_evidence",
        "subject_revision",
        "acceptance_criteria",
    }
    missing = sorted(required - contract.keys())
    if missing:
        errors.append(f"{label}: implementation_contract missing fields {', '.join(missing)}")
        return

    intent = contract["intent"]
    if intent not in IMPLEMENTATION_INTENTS:
        errors.append(f"{label}: unsupported implementation intent {intent!r}")
    mode = contract["execution_mode"]
    if mode not in EXECUTION_MODES:
        errors.append(f"{label}: execution_mode must be command, query, reactor, or generic")

    overlays = contract["overlays"]
    if not isinstance(overlays, list) or any(value not in IMPLEMENTATION_OVERLAYS for value in overlays):
        errors.append(f"{label}: overlays must contain only supported overlay names")
        overlays = []
    elif len(overlays) != len(set(overlays)):
        errors.append(f"{label}: overlays must not contain duplicates")
    remediation_selected = "remediation" in overlays
    if intent in REMEDIATION_INTENTS and not remediation_selected:
        errors.append(f"{label}: remediation intent requires remediation overlay")
    if intent not in REMEDIATION_INTENTS and remediation_selected:
        errors.append(f"{label}: remediation overlay requires a remediation intent")

    for field in ("authorization_source", "normative_truth", "acceptance_criteria"):
        value = contract[field]
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{label}: implementation_contract.{field} must be a non-empty string list")
    findings = contract["finding_evidence"]
    if not isinstance(findings, list) or not all(isinstance(item, str) and item.strip() for item in findings):
        errors.append(f"{label}: implementation_contract.finding_evidence must be a string list")
    elif intent in REMEDIATION_INTENTS and not findings:
        errors.append(f"{label}: remediation intent requires finding_evidence")

    revision = contract["subject_revision"]
    if not isinstance(revision, str) or (revision and not re.fullmatch(r"[0-9a-fA-F]{40}", revision)):
        errors.append(f"{label}: subject_revision must be empty or a 40-character Git SHA")


def non_empty_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def development_acceptance_applies(
    task: dict, task_created: datetime | None
) -> bool:
    return (
        task.get("template_source") == DEV_TASK_TEMPLATE
        and task_created is not None
        and task_created >= DEVELOPMENT_ACCEPTANCE_CONTRACT_AT
    )


def validate_development_approval_contract(
    task: dict, label: str, errors: list[str], task_created: datetime | None
) -> None:
    if not development_acceptance_applies(task, task_created):
        return
    execution = task.get("execution")
    if not isinstance(execution, dict):
        errors.append(f"{label}: execution must be a mapping")
        return
    contract = execution.get("approval_contract")
    if not isinstance(contract, dict):
        errors.append(f"{label}: approval_contract must be a mapping")
        return
    required = {
        "status",
        "required_before",
        "authorization_source",
        "pending_decision",
    }
    missing = sorted(required - contract.keys())
    if missing:
        errors.append(f"{label}: approval_contract missing fields {', '.join(missing)}")
        return
    status = contract["status"]
    if status not in APPROVAL_STATUSES:
        errors.append(f"{label}: unsupported approval status {status!r}")
        return
    required_before = contract["required_before"]
    authorization = contract["authorization_source"]
    pending = contract["pending_decision"]
    if status == "awaiting-approval":
        if not isinstance(required_before, str) or not required_before.strip():
            errors.append(f"{label}: awaiting approval requires required_before")
        if not isinstance(pending, str) or not pending.strip():
            errors.append(f"{label}: awaiting approval requires pending_decision")
        if authorization not in ([], None):
            errors.append(f"{label}: awaiting approval must not claim authorization_source")
        if (
            execution.get("capability_slot") == "implementation"
            or execution.get("implementation_contract") is not None
        ):
            errors.append(
                f"{label}: awaiting approval blocks creation or execution of implementation work"
            )
    elif status == "approved":
        if not isinstance(required_before, str) or not required_before.strip():
            errors.append(f"{label}: approved transition requires required_before")
        if not non_empty_string_list(authorization):
            errors.append(f"{label}: approved transition requires authorization_source evidence")
        if pending not in ("", None):
            errors.append(f"{label}: approved transition must clear pending_decision")
    else:
        if required_before not in ("", None):
            errors.append(f"{label}: not-required approval must clear required_before")
        if authorization not in ([], None):
            errors.append(f"{label}: not-required approval must not claim authorization_source")
        if pending not in ("", None):
            errors.append(f"{label}: not-required approval must clear pending_decision")


def validate_test_execution_contract(
    task: dict, label: str, errors: list[str], task_created: datetime | None
) -> None:
    if not development_acceptance_applies(task, task_created):
        return
    execution = task.get("execution")
    if not isinstance(execution, dict):
        return
    contract = execution.get("test_execution_contract")
    selected = execution.get("capability_slot") == "test-execution" or contract is not None
    if not selected:
        return
    if execution.get("capability_slot") != "test-execution":
        errors.append(f"{label}: test_execution_contract requires capability_slot test-execution")
    if not isinstance(contract, dict):
        errors.append(f"{label}: test-execution task requires test_execution_contract mapping")
        return
    required = {
        "provider",
        "target_owned",
        "selected_levels",
        "required_for_closeout",
        "conditional_selection_sources",
        "outcomes",
    }
    missing = sorted(required - contract.keys())
    if missing:
        errors.append(f"{label}: test_execution_contract missing fields {', '.join(missing)}")
        return
    if contract["provider"] not in TEST_PROVIDERS:
        errors.append(f"{label}: unsupported test-execution provider {contract['provider']!r}")

    target_owned = contract["target_owned"]
    if not isinstance(target_owned, dict):
        errors.append(f"{label}: test_execution_contract.target_owned must be a mapping")
        return
    for field in ("working_directory", "commands", "prerequisites", "environment_boundary", "policy"):
        if field not in target_owned:
            errors.append(f"{label}: test_execution_contract.target_owned missing {field}")
    working_directory = target_owned.get("working_directory")
    if not isinstance(working_directory, str) or not working_directory.strip():
        errors.append(f"{label}: target_owned.working_directory must be non-empty")
    for field in ("prerequisites", "environment_boundary", "policy"):
        value = target_owned.get(field)
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            errors.append(f"{label}: target_owned.{field} must be a string list")

    levels = contract["selected_levels"]
    if (
        not isinstance(levels, list)
        or not levels
        or not all(isinstance(item, str) for item in levels)
    ):
        errors.append(f"{label}: selected_levels must be a non-empty string list")
        return
    if len(levels) != len(set(levels)):
        errors.append(f"{label}: selected_levels must not contain duplicates")
    level_set = set(levels)
    allowed_levels = DEFAULT_TEST_LEVELS | CONDITIONAL_TEST_LEVELS
    unknown_levels = sorted(level_set - allowed_levels)
    if unknown_levels:
        errors.append(f"{label}: selected_levels contains unsupported levels {unknown_levels}")
    if not DEFAULT_TEST_LEVELS <= level_set:
        errors.append(f"{label}: selected_levels must include default unit and integration levels")

    conditional_sources = contract["conditional_selection_sources"]
    selected_conditional = level_set & CONDITIONAL_TEST_LEVELS
    if selected_conditional and not non_empty_string_list(conditional_sources):
        errors.append(
            f"{label}: conditional test levels require conditional_selection_sources"
        )
    if not selected_conditional and conditional_sources not in ([], None):
        errors.append(
            f"{label}: conditional_selection_sources requires a selected conditional level"
        )

    required_levels = contract["required_for_closeout"]
    if not isinstance(required_levels, list) or not all(
        isinstance(item, str) for item in required_levels
    ):
        errors.append(f"{label}: required_for_closeout must be a string list")
        required_set: set[str] = set()
    else:
        if len(required_levels) != len(set(required_levels)):
            errors.append(f"{label}: required_for_closeout must not contain duplicates")
        required_set = set(required_levels)
        if not required_set <= level_set:
            errors.append(f"{label}: required_for_closeout must be a subset of selected_levels")

    commands = target_owned.get("commands")
    command_levels: list[str] = []
    if not isinstance(commands, list):
        errors.append(f"{label}: target_owned.commands must be a list")
    else:
        for index, command in enumerate(commands):
            if not isinstance(command, dict):
                errors.append(f"{label}: target_owned.commands[{index}] must be a mapping")
                continue
            command_level = command.get("level")
            command_text = command.get("command")
            if command_level not in level_set:
                errors.append(
                    f"{label}: target_owned.commands[{index}].level must be selected"
                )
            elif isinstance(command_level, str):
                command_levels.append(command_level)
            if not isinstance(command_text, str) or not command_text.strip():
                errors.append(
                    f"{label}: target_owned.commands[{index}].command must be non-empty"
                )
    outcomes = contract["outcomes"]
    outcome_by_level: dict[str, dict] = {}
    if not isinstance(outcomes, list):
        errors.append(f"{label}: test_execution_contract.outcomes must be a list")
        return
    for index, outcome in enumerate(outcomes):
        if not isinstance(outcome, dict):
            errors.append(f"{label}: outcomes[{index}] must be a mapping")
            continue
        level = outcome.get("level")
        value = outcome.get("outcome")
        if level not in level_set:
            errors.append(f"{label}: outcomes[{index}].level must be selected")
            continue
        if level in outcome_by_level:
            errors.append(f"{label}: outcomes contains duplicate level {level}")
        outcome_by_level[str(level)] = outcome
        if value not in TEST_OUTCOMES:
            errors.append(f"{label}: unsupported test outcome {value!r}")
        evidence = outcome.get("evidence")
        if not isinstance(evidence, list) or not all(
            isinstance(item, str) and item.strip() for item in evidence
        ):
            errors.append(f"{label}: outcomes[{index}].evidence must be a string list")
        if value == "deferred-with-owner":
            if not isinstance(outcome.get("deferral_owner"), str) or not outcome["deferral_owner"].strip():
                errors.append(f"{label}: deferred test outcome requires deferral_owner")
            if not isinstance(outcome.get("follow_up"), str) or not outcome["follow_up"].strip():
                errors.append(f"{label}: deferred test outcome requires follow_up")
    if set(outcome_by_level) != level_set:
        errors.append(f"{label}: outcomes must contain exactly one record per selected level")
    expected_command_levels = {
        level
        for level in level_set
        if outcome_by_level.get(level, {}).get("outcome") != "not-applicable"
    }
    if (
        set(command_levels) != expected_command_levels
        or len(command_levels) != len(set(command_levels))
    ):
        errors.append(
            f"{label}: target_owned.commands must contain exactly one command "
            "per selected applicable level"
        )

    if task.get("status") == "completed":
        for level in sorted(required_set):
            outcome = outcome_by_level.get(level, {})
            value = outcome.get("outcome")
            if value == "deferred-with-owner" and target_owned.get("policy"):
                continue
            if value != "passed":
                errors.append(
                    f"{label}: required test level {level} must pass or have "
                    "an owner-approved policy deferral before task completion"
                )
            elif not non_empty_string_list(outcome.get("evidence")):
                errors.append(f"{label}: passed required test level {level} requires evidence")


def validate_spec_compliance_contract(
    task: dict, label: str, errors: list[str], task_created: datetime | None
) -> None:
    if not development_acceptance_applies(task, task_created):
        return
    execution = task.get("execution")
    results = task.get("results")
    if not isinstance(execution, dict) or not isinstance(results, dict):
        errors.append(f"{label}: development task requires execution and results mappings")
        return
    selection = execution.get("spec_compliance")
    result = results.get("spec_compliance")
    if not isinstance(selection, dict) or not isinstance(result, dict):
        errors.append(f"{label}: spec_compliance selection and result must be mappings")
        return
    selected = selection.get("selected")
    activation = selection.get("activation_source")
    expected = selection.get("expected_outcome")
    outcome = result.get("outcome")
    coverage = result.get("coverage_percent")
    evidence = result.get("evidence")
    if not isinstance(evidence, list) or not all(
        isinstance(item, str) and item.strip() for item in evidence
    ):
        errors.append(f"{label}: results.spec_compliance.evidence must be a string list")
        evidence = []
    if selected is False:
        if activation not in ([], None):
            errors.append(f"{label}: unselected spec compliance must not claim activation_source")
        if expected != "not-applicable" or outcome != "not-applicable":
            errors.append(f"{label}: unselected spec compliance must be not-applicable")
        if coverage is not None or evidence:
            errors.append(f"{label}: unselected spec compliance must not claim coverage or evidence")
        return
    if selected is not True:
        errors.append(f"{label}: execution.spec_compliance.selected must be boolean")
        return
    if not non_empty_string_list(activation):
        errors.append(f"{label}: selected spec compliance requires activation_source")
    if expected != "100-percent-pass":
        errors.append(f"{label}: selected spec compliance expected_outcome must be 100-percent-pass")
    if outcome not in COMPLIANCE_OUTCOMES:
        errors.append(f"{label}: unsupported spec compliance outcome {outcome!r}")
    if task.get("status") == "completed":
        if outcome != "100-percent-pass" or coverage != 100 or not evidence:
            errors.append(
                f"{label}: completed selected spec compliance requires 100 percent "
                "coverage and execution evidence"
            )
    elif outcome == "100-percent-pass" and (coverage != 100 or not evidence):
        errors.append(f"{label}: claimed compliance pass requires 100 percent evidence")


def validate_development_commit_checkpoint(
    task: dict, label: str, errors: list[str], task_created: datetime | None
) -> None:
    if not development_acceptance_applies(task, task_created):
        return
    execution = task.get("execution")
    if not isinstance(execution, dict):
        return
    checkpoint = execution.get("commit_checkpoint")
    if not isinstance(checkpoint, str) or not checkpoint.strip():
        errors.append(
            f"{label}: development task requires a durable-stage or coherent-batch commit checkpoint"
        )
    if task.get("status") != "completed":
        return
    results = task.get("results")
    commits = results.get("commits") if isinstance(results, dict) else None
    if not isinstance(commits, list) or not commits:
        errors.append(f"{label}: completed development task requires commit evidence")
        return
    for commit in commits:
        if not isinstance(commit, str) or not (
            commit == "containing-commit"
            or re.fullmatch(r"[0-9a-fA-F]{40}", commit)
        ):
            errors.append(
                f"{label}: commit evidence must be containing-commit or a 40-character Git SHA"
            )


def safe_repo_reference(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path_value = value.split("#", 1)[0]
    segments = path_value.split("/")
    path = Path(path_value)
    return (
        bool(path_value)
        and ":" not in path_value
        and all(segments)
        and not path.is_absolute()
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def validate_development_continuation_contract(
    locator: dict,
    tasks: list[tuple[str, dict]],
    label: str,
    errors: list[str],
    *,
    repo: Path,
    locator_created: datetime | None,
) -> None:
    if (
        locator.get("template_source") != DEV_LOCATOR_TEMPLATE
        or locator_created is None
        or locator_created < DEVELOPMENT_ACCEPTANCE_CONTRACT_AT
    ):
        return
    continuation = locator.get("continuation")
    if not isinstance(continuation, dict):
        errors.append(f"{label}: development locator requires continuation mapping")
        return
    required = {"current_task_id", "target_policy_refs", "handoff_checkpoint"}
    missing = sorted(required - continuation.keys())
    if missing:
        errors.append(f"{label}: continuation missing fields {', '.join(missing)}")
        return
    current_task_id = continuation["current_task_id"]
    task_by_id = {
        str(task.get("task_id")): task
        for _, task in tasks
        if isinstance(task.get("task_id"), str)
    }
    if locator.get("status") == "in_progress":
        if current_task_id not in task_by_id:
            errors.append(f"{label}: continuation.current_task_id must reference a current task")
        elif task_by_id[current_task_id].get("status") != "in_progress":
            errors.append(f"{label}: continuation.current_task_id must reference the in_progress task")

    policy_refs = continuation["target_policy_refs"]
    if not isinstance(policy_refs, list) or not all(safe_repo_reference(item) for item in policy_refs):
        errors.append(f"{label}: continuation.target_policy_refs must be safe repository paths")
        policy_refs = []
    for policy_ref in policy_refs:
        if not reference_path(repo, policy_ref).is_file():
            errors.append(f"{label}: target policy reference does not exist: {policy_ref}")

    checkpoint_ref = continuation["handoff_checkpoint"]
    if checkpoint_ref is None:
        return
    if not safe_repo_reference(checkpoint_ref):
        errors.append(f"{label}: continuation.handoff_checkpoint must be a safe repository path")
        return
    if not policy_refs:
        errors.append(f"{label}: fresh-session handoff requires target_policy_refs")
    checkpoint_path = reference_path(repo, checkpoint_ref)
    if not checkpoint_path.is_file():
        errors.append(f"{label}: handoff checkpoint does not exist: {checkpoint_ref}")
        return
    registry_path = repo / ".dev/workflows/handoff-checkpoints.yaml"
    registry = parse_yaml_mapping(
        registry_path,
        ".dev/workflows/handoff-checkpoints.yaml",
        errors,
    )
    registered = registry.get("checkpoints") if isinstance(registry, dict) else None
    if not isinstance(registered, list) or checkpoint_ref not in registered:
        errors.append(f"{label}: handoff checkpoint must be registered")
    checkpoint = parse_yaml_mapping(checkpoint_path, checkpoint_ref, errors)
    if checkpoint is None:
        return
    workflow = checkpoint.get("workflow")
    resume = checkpoint.get("resume")
    if not isinstance(workflow, dict):
        errors.append(f"{checkpoint_ref}: workflow must be a mapping")
    else:
        if workflow.get("workflow_id") != locator.get("workflow_id"):
            errors.append(f"{checkpoint_ref}: workflow_id must match locator")
        if workflow.get("task_id") != current_task_id:
            errors.append(f"{checkpoint_ref}: task_id must match continuation.current_task_id")
    if not isinstance(resume, dict):
        errors.append(f"{checkpoint_ref}: resume must be a mapping")
        return
    if resume.get("hidden_context_required") is not False:
        errors.append(f"{checkpoint_ref}: hidden_context_required must be false")
    exact_next_action = resume.get("exact_next_action")
    if not isinstance(exact_next_action, str) or not exact_next_action.strip():
        errors.append(f"{checkpoint_ref}: exact_next_action must be non-empty")


def validate_lifecycle_contract(
    locator: dict[str, str], tasks: list[tuple[str, dict]], label: str, errors: list[str]
) -> None:
    """Validate prospective workflow/task semantic consistency when opted in."""
    contract = locator.get("lifecycle_contract")
    if contract is None:
        return
    if contract != "1.0":
        errors.append(f"{label}: lifecycle_contract must be 1.0")
        return

    workflow_status = locator.get("status", "")
    if workflow_status not in WORKFLOW_STATUSES:
        errors.append(f"{label}: unsupported workflow status {workflow_status!r}")

    statuses: list[tuple[str, str]] = []
    for task_label, task in tasks:
        status = str(task.get("status", ""))
        statuses.append((task_label, status))
        if status not in TASK_STATUSES:
            errors.append(f"{task_label}: unsupported task status {status!r}")
        if status == "completed":
            results = task.get("results")
            if not isinstance(results, dict):
                errors.append(f"{task_label}: completed task requires results mapping")
                continue
            if not isinstance(results.get("summary"), str) or not results["summary"].strip():
                errors.append(f"{task_label}: completed task requires non-empty results.summary")
            if results.get("finding_status") in (None, "", "not-addressed"):
                errors.append(f"{task_label}: completed task requires an addressed results.finding_status")

    in_progress = [task_label for task_label, status in statuses if status == "in_progress"]
    if workflow_status == "in_progress" and len(in_progress) != 1:
        errors.append(f"{label}: in_progress workflow requires exactly one in_progress task; found={in_progress}")
    if workflow_status == "completed":
        unfinished = [task_label for task_label, status in statuses if status not in TERMINAL_TASK_STATUSES]
        if unfinished:
            errors.append(f"{label}: completed workflow has unfinished tasks {unfinished}")
        if locator.get("current_phase") not in {"completed", "closed"}:
            errors.append(f"{label}: completed workflow current_phase must be completed or closed")


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    discovery_root = repo / ".dev" / "workflows"
    errors: list[str] = []
    checked = 0
    roots: dict[Path, str] = {}

    for directory in sorted(path for path in discovery_root.iterdir() if path.is_dir()):
        match = ID_RE.match(directory.name)
        if not match:
            continue
        workflow_date = date.fromisoformat(match.group(1))
        if workflow_date < ADOPTION_DATE:
            continue
        checked += 1
        locator_path = directory / "workflow.yaml"
        if not locator_path.is_file():
            errors.append(f"{directory.relative_to(repo)}: missing workflow.yaml")
            continue
        locator = parse_flat_yaml(locator_path)
        missing = sorted(REQUIRED_LOCATOR - locator.keys())
        if missing:
            errors.append(f"{locator_path.relative_to(repo)}: missing fields {', '.join(missing)}")
            continue
        if locator["workflow_id"] != directory.name:
            errors.append(f"{locator_path.relative_to(repo)}: workflow_id must match directory name")
        if workflow_date >= BRANCH_POLICY_DATE:
            missing_branch = sorted({"branch", "base_branch"} - locator.keys())
            if missing_branch:
                errors.append(f"{locator_path.relative_to(repo)}: missing branch fields {', '.join(missing_branch)}")
            else:
                branch = locator["branch"]
                base_branch = locator["base_branch"]
                if branch in {"main", "master"} or branch == base_branch:
                    errors.append(f"{locator_path.relative_to(repo)}: workflow branch must differ from the long-lived base branch")
                if "/" not in branch:
                    errors.append(f"{locator_path.relative_to(repo)}: workflow branch must use a short-lived branch prefix")
        created = timestamp(locator["created_at"], f"{locator_path.relative_to(repo)} created_at", errors)
        updated = timestamp(locator["updated_at"], f"{locator_path.relative_to(repo)} updated_at", errors)
        if created and updated and updated < created:
            errors.append(f"{locator_path.relative_to(repo)}: updated_at is earlier than created_at")
        root = (repo / locator["artifact_root"]).resolve()
        try:
            root.relative_to(repo.resolve())
        except ValueError:
            errors.append(f"{locator_path.relative_to(repo)}: artifact_root is outside the repository")
            continue
        if not root.is_dir():
            errors.append(f"{locator_path.relative_to(repo)}: artifact_root does not exist")
            continue
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", str(root)],
            cwd=repo,
            check=False,
            capture_output=True,
        )
        if ignored.returncode == 0:
            errors.append(f"{locator_path.relative_to(repo)}: artifact_root is ignored by Git")
        if root in roots and roots[root] != directory.name:
            errors.append(f"{locator_path.relative_to(repo)}: artifact_root also owned by {roots[root]}")
        roots[root] = directory.name
        entrypoint = (root / locator["entrypoint"]).resolve()
        try:
            entrypoint.relative_to(root)
        except ValueError:
            errors.append(f"{locator_path.relative_to(repo)}: entrypoint escapes artifact_root")
            continue
        if not entrypoint.is_file():
            errors.append(f"{locator_path.relative_to(repo)}: entrypoint does not exist in artifact_root")
        task_root = root / "tasks"
        task_records: list[tuple[str, dict]] = []
        if task_root.is_dir():
            seen: set[str] = set()
            for task_path in sorted(task_root.glob("*.json")):
                try:
                    task = json.loads(task_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    errors.append(f"{task_path.relative_to(repo)}: invalid JSON: {exc}")
                    continue
                task_records.append((str(task_path.relative_to(repo)), task))
                missing_task = sorted(REQUIRED_TASK - task.keys())
                if missing_task:
                    errors.append(f"{task_path.relative_to(repo)}: missing fields {', '.join(missing_task)}")
                    continue
                if task["workflow_id"] != directory.name:
                    errors.append(f"{task_path.relative_to(repo)}: workflow_id does not match locator")
                if task["task_id"] in seen:
                    errors.append(f"{task_path.relative_to(repo)}: duplicate task_id {task['task_id']}")
                seen.add(task["task_id"])
                if not TASK_ID_RE.match(str(task["task_id"])):
                    errors.append(f"{task_path.relative_to(repo)}: task_id is not path-safe")
                task_created = timestamp(task["created_at"], f"{task_path.relative_to(repo)} created_at", errors)
                task_updated = timestamp(task["updated_at"], f"{task_path.relative_to(repo)} updated_at", errors)
                if task_created and task_updated and task_updated < task_created:
                    errors.append(f"{task_path.relative_to(repo)}: updated_at is earlier than created_at")
                validate_implementation_contract(task, str(task_path.relative_to(repo)), errors, task_created)
                validate_development_approval_contract(
                    task, str(task_path.relative_to(repo)), errors, task_created
                )
                validate_test_execution_contract(
                    task, str(task_path.relative_to(repo)), errors, task_created
                )
                validate_spec_compliance_contract(
                    task, str(task_path.relative_to(repo)), errors, task_created
                )
                validate_development_commit_checkpoint(
                    task, str(task_path.relative_to(repo)), errors, task_created
                )
        validate_development_continuation_contract(
            locator,
            task_records,
            str(locator_path.relative_to(repo)),
            errors,
            repo=repo,
            locator_created=created,
        )
        validate_lifecycle_contract(
            locator,
            task_records,
            str(locator_path.relative_to(repo)),
            errors,
        )

    indexed_workflows = validate_workflow_index(repo, discovery_root, errors)
    backlog_items = (
        validate_backlog(repo, errors)
        if backlog_provider_enabled(repo, errors)
        else 0
    )

    if errors:
        print("Workflow artifact validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Workflow artifact validation passed for {checked} post-adoption workflow(s), "
        f"{indexed_workflows} indexed workflow directories, and {backlog_items} backlog item(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
