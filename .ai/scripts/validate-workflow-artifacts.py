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
DEV_TASK_TEMPLATE = ".ai/assets/skills/dev-workflow/templates/development-workflow-task-template.json"
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
                if not reference_path(repo, value).exists():
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
        validate_lifecycle_contract(
            locator,
            task_records,
            str(locator_path.relative_to(repo)),
            errors,
        )

    indexed_workflows = validate_workflow_index(repo, discovery_root, errors)
    backlog_items = validate_backlog(repo, errors)

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
