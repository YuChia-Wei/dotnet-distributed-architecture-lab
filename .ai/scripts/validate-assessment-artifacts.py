#!/usr/bin/env python3
"""Validate durable standalone assessment locators and index coverage."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml


ID_RE = re.compile(r"^ASM-(\d{8})-(\d{3})$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
STATUSES = {"draft", "final", "superseded", "withdrawn"}
STATUS_SECTIONS = {
    "draft": "Draft Assessments",
    "final": "Final Assessments",
    "superseded": "Superseded Or Withdrawn Assessments",
    "withdrawn": "Superseded Or Withdrawn Assessments",
}
REQUIRED_FIELDS = {
    "schema_version",
    "assessment_id",
    "commit_search_id",
    "assessment_type",
    "title",
    "owner_skill",
    "status",
    "report",
    "artifact_branch",
    "base_branch",
    "created_at",
    "updated_at",
    "template_source",
    "template_version",
    "report_template_source",
    "report_template_version",
    "subject_ref",
    "scope",
    "relations",
    "resume",
}
RELATION_KEYS = {
    "supersedes",
    "superseded_by",
    "related_assessments",
    "workflow_refs",
    "backlog_refs",
    "adr_refs",
}
INDEX_ROW = re.compile(
    r"^\| \[`(ASM-\d{8}-\d{3})`\]\(([^)]+/assessment\.yaml)\) "
    r"\| (.*?) \| `([^`]+)` \| `([^`]+)` \| `([^`]+)` "
    r"\| `([0-9a-fA-F]{40})` \| `([^`]+)` \| \[report\]\(([^)]+/report\.md)\) \|$"
)


def load_mapping(path: Path, label: str, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        errors.append(f"{label}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: YAML root must be a mapping")
        return None
    return value


def parse_timestamp(value: object, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label}: timestamp must be a string")
        return None
    if not TIMESTAMP_RE.fullmatch(value):
        errors.append(f"{label}: timestamp must include seconds and an explicit UTC offset")
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label}: invalid ISO 8601 timestamp {value!r}")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label}: timestamp must include UTC offset")
        return None
    return parsed


def non_empty_string(value: object, label: str, errors: list[str]) -> bool:
    valid = isinstance(value, str) and bool(value.strip())
    if not valid:
        errors.append(f"{label}: must be a non-empty string")
    return valid


def string_list(value: object, label: str, errors: list[str]) -> list[str] | None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and bool(item.strip()) for item in value
    ):
        errors.append(f"{label}: must be a list of non-empty strings")
        return None
    return value


def safe_repo_path(root: Path, value: str, label: str, errors: list[str]) -> Path | None:
    candidate = (root / value).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        errors.append(f"{label}: path escapes repository: {value}")
        return None
    return candidate


def parse_index(index_path: Path, errors: list[str]) -> dict[str, tuple[str, ...]]:
    rows: dict[str, tuple[str, ...]] = {}
    section = ""
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## "):
            section = line[3:]
            continue
        match = INDEX_ROW.match(line)
        if not match:
            continue
        assessment_id = match.group(1)
        if assessment_id in rows:
            errors.append(f".dev/assessments/INDEX.MD:{line_number}: duplicate row for {assessment_id}")
            continue
        rows[assessment_id] = (section, *match.groups()[1:])
    return rows


def validate_assessments(root: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    assessment_root = root / ".dev" / "assessments"
    index_path = assessment_root / "INDEX.MD"
    readme_path = assessment_root / "README.MD"
    if not readme_path.is_file() or not index_path.is_file():
        errors.append(".dev/assessments: README.MD and INDEX.MD are required")
        return errors, 0

    index_rows = parse_index(index_path, errors)
    directories = sorted(
        path for path in assessment_root.iterdir()
        if path.is_dir() and path.name != "templates"
    )
    locators: dict[str, tuple[Path, dict]] = {}

    for directory in directories:
        label = str(directory.relative_to(root))
        if not ID_RE.fullmatch(directory.name):
            errors.append(f"{label}: assessment directory must match ASM-YYYYMMDD-NNN")
            continue
        locator_path = directory / "assessment.yaml"
        if not locator_path.is_file():
            errors.append(f"{label}: missing assessment.yaml")
            continue
        locator = load_mapping(locator_path, str(locator_path.relative_to(root)), errors)
        if locator is not None:
            locators[directory.name] = (locator_path, locator)

    for assessment_id, (locator_path, locator) in locators.items():
        label = str(locator_path.relative_to(root))
        missing = sorted(REQUIRED_FIELDS - locator.keys())
        if missing:
            errors.append(f"{label}: missing fields {', '.join(missing)}")
            continue
        if locator.get("schema_version") != "1.0":
            errors.append(f"{label}: schema_version must be 1.0")
        if locator.get("assessment_id") != assessment_id:
            errors.append(f"{label}: assessment_id must match directory name")
        if locator.get("commit_search_id") != assessment_id:
            errors.append(f"{label}: commit_search_id must equal assessment_id")
        match = ID_RE.fullmatch(assessment_id)
        created = parse_timestamp(locator.get("created_at"), f"{label} created_at", errors)
        updated = parse_timestamp(locator.get("updated_at"), f"{label} updated_at", errors)
        if created and updated and updated < created:
            errors.append(f"{label}: updated_at is earlier than created_at")
        if match and created and created.strftime("%Y%m%d") != match.group(1):
            errors.append(f"{label}: assessment ID date must match created_at local date")

        for key in ("assessment_type", "title", "owner_skill", "artifact_branch", "base_branch", "template_version", "report_template_version"):
            non_empty_string(locator.get(key), f"{label} {key}", errors)
        if locator.get("artifact_branch") in {"main", locator.get("base_branch")}:
            errors.append(f"{label}: artifact_branch must differ from base_branch and main")
        status = locator.get("status")
        if status not in STATUSES:
            errors.append(f"{label}: unsupported status {status!r}")
        if locator.get("report") != "report.md":
            errors.append(f"{label}: report must be report.md")
        report_path = locator_path.parent / "report.md"
        if not report_path.is_file():
            errors.append(f"{label}: missing report.md")

        for key in ("template_source", "report_template_source"):
            value = locator.get(key)
            if non_empty_string(value, f"{label} {key}", errors):
                target = safe_repo_path(root, value, f"{label} {key}", errors)
                if target is not None and not target.is_file():
                    errors.append(f"{label}: missing {key} {value}")

        subject = locator.get("subject_ref")
        if not isinstance(subject, dict):
            errors.append(f"{label}: subject_ref must be a mapping")
            subject = {}
        for key in ("repository", "branch"):
            non_empty_string(subject.get(key), f"{label} subject_ref.{key}", errors)
        commit = subject.get("commit")
        if not isinstance(commit, str) or not SHA_RE.fullmatch(commit):
            errors.append(f"{label}: subject_ref.commit must be a 40-character Git SHA")

        scope = locator.get("scope")
        if not isinstance(scope, dict):
            errors.append(f"{label}: scope must be a mapping")
            scope = {}
        included = string_list(scope.get("included"), f"{label} scope.included", errors)
        string_list(scope.get("excluded"), f"{label} scope.excluded", errors)
        if included == []:
            errors.append(f"{label}: scope.included must not be empty")

        relations = locator.get("relations")
        if not isinstance(relations, dict):
            errors.append(f"{label}: relations must be a mapping")
            relations = {}
        missing_relations = sorted(RELATION_KEYS - relations.keys())
        if missing_relations:
            errors.append(f"{label}: missing relation lists {', '.join(missing_relations)}")
        for key in RELATION_KEYS:
            string_list(relations.get(key), f"{label} relations.{key}", errors)

        resume = locator.get("resume")
        if not isinstance(resume, dict):
            errors.append(f"{label}: resume must be a mapping")
            resume = {}
        for key in ("last_completed_action", "next_action"):
            if not isinstance(resume.get(key), str):
                errors.append(f"{label}: resume.{key} must be a string")
        string_list(resume.get("blockers"), f"{label} resume.blockers", errors)
        if status == "draft" and not str(resume.get("next_action", "")).strip():
            errors.append(f"{label}: draft assessment requires resume.next_action")
        if status == "superseded" and not relations.get("superseded_by"):
            errors.append(f"{label}: superseded assessment requires superseded_by")

        row = index_rows.get(assessment_id)
        if row is None:
            errors.append(f"{label}: missing INDEX.MD row")
        else:
            expected = (
                STATUS_SECTIONS.get(str(status), ""),
                f"{assessment_id}/assessment.yaml",
                str(locator.get("title", "")),
                str(locator.get("assessment_type", "")),
                str(locator.get("owner_skill", "")),
                str(status),
                str(commit or ""),
                str(locator.get("updated_at", "")),
                f"{assessment_id}/report.md",
            )
            if row != expected:
                errors.append(f"{label}: INDEX.MD row differs; expected={expected}, actual={row}")

    locator_ids = set(locators)
    extra_rows = sorted(set(index_rows) - locator_ids)
    if extra_rows:
        errors.append(f".dev/assessments/INDEX.MD: rows without locators {extra_rows}")

    for assessment_id, (locator_path, locator) in locators.items():
        relations = locator.get("relations")
        if not isinstance(relations, dict):
            continue
        for key in ("supersedes", "superseded_by", "related_assessments"):
            values = relations.get(key, [])
            if not isinstance(values, list):
                continue
            for related in values:
                if related == assessment_id:
                    errors.append(f"{locator_path.relative_to(root)}: relations.{key} cannot reference itself")
                elif related not in locator_ids:
                    errors.append(f"{locator_path.relative_to(root)}: relations.{key} references missing assessment {related}")
        for predecessor in relations.get("supersedes", []) if isinstance(relations.get("supersedes"), list) else []:
            other = locators.get(predecessor)
            if other and assessment_id not in other[1].get("relations", {}).get("superseded_by", []):
                errors.append(f"{locator_path.relative_to(root)}: supersedes relation to {predecessor} is not reciprocal")
        for successor in relations.get("superseded_by", []) if isinstance(relations.get("superseded_by"), list) else []:
            other = locators.get(successor)
            if other and assessment_id not in other[1].get("relations", {}).get("supersedes", []):
                errors.append(f"{locator_path.relative_to(root)}: superseded_by relation to {successor} is not reciprocal")
        for workflow_id in relations.get("workflow_refs", []) if isinstance(relations.get("workflow_refs"), list) else []:
            if not (root / ".dev" / "workflows" / workflow_id / "workflow.yaml").is_file():
                errors.append(f"{locator_path.relative_to(root)}: workflow_refs references missing workflow {workflow_id}")
        for backlog_id in relations.get("backlog_refs", []) if isinstance(relations.get("backlog_refs"), list) else []:
            if not (root / ".dev" / "backlog" / "items" / f"{backlog_id}.yaml").is_file():
                errors.append(f"{locator_path.relative_to(root)}: backlog_refs references missing item {backlog_id}")
        for adr_ref in relations.get("adr_refs", []) if isinstance(relations.get("adr_refs"), list) else []:
            target = safe_repo_path(root, adr_ref, f"{locator_path.relative_to(root)} relations.adr_refs", errors)
            if target is not None and not target.is_file():
                errors.append(f"{locator_path.relative_to(root)}: adr_refs references missing file {adr_ref}")

    return errors, len(locators)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    errors, count = validate_assessments(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Assessment artifact validation passed for {count} assessment(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
