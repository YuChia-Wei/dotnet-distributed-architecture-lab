#!/usr/bin/env python3
"""Validate explicitly selected target-owned terminal audit evidence, read-only."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[3]
ROLE_PATH = ".ai/assets/sub-agent-role-prompts/fixed-head-independent-auditor/sub-agent.yaml"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z")
WINDOWS_RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\..*)?\Z", re.IGNORECASE)
RECEIPT_FIELDS = {
    "schema_version", "status", "subject_commit", "subject_tree", "reviewer_id",
    "invocation_id", "role_path", "started_at", "completed_at", "criteria",
    "report", "invocation_evidence", "authority_hashes",
}
INVOCATION_FIELDS = {
    "status", "subject_commit", "subject_tree", "reviewer_id", "invocation_id",
    "role_path", "started_at", "completed_at", "evidence_refs",
}


def fail(message: str) -> None:
    raise ValueError(message)


def exact_fields(value: object, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        fail(f"{label} must contain exactly: {', '.join(sorted(fields))}")
    return value


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        fail(f"{label} must be a non-empty, trimmed string")
    return value


def sha(value: object, label: str, pattern: re.Pattern = SHA256) -> str:
    value = text(value, label)
    if not pattern.fullmatch(value):
        fail(f"{label} has an invalid digest")
    return value


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-optional-locks", "--no-replace-objects", "-C", str(root), *args],
        capture_output=True, timeout=30, check=False,
    )
    if result.returncode:
        fail(f"Git verification failed ({args[0]}): {result.stderr.decode('utf-8', errors='replace').strip()}")
    return result.stdout


def no_links(path: Path) -> None:
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            fail(f"symlink or reparse-point evidence is forbidden: {part}")
    if not path.is_file():
        fail(f"evidence is not a regular file: {path}")


def safe_relative_path(value: object, label: str = "evidence path") -> tuple[str, list[str]]:
    value = text(value, label)
    parts = value.split("/")
    if (
        any(character in value for character in '\\:\x00"<>|?*[')
        or any(ord(character) < 32 for character in value)
        or any(part in {"", ".", ".."} or part.rstrip(" .") != part or WINDOWS_RESERVED.fullmatch(part) for part in parts)
        or parts[0].lower() == ".git"
    ):
        fail(f"unsafe repository-relative path: {value}")
    return value, parts


def safe_file(root: Path, value: object, *, tracked: bool) -> Path:
    value, parts = safe_relative_path(value)
    path = root.joinpath(*parts)
    no_links(path)
    if not path.resolve().is_relative_to(root.resolve()):
        fail(f"evidence escapes repository: {value}")
    if tracked:
        git(root, "ls-files", "--error-unmatch", "--", value)
    return path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pin(root: Path, record: object, label: str, *, tracked: bool) -> tuple[str, bytes]:
    record = exact_fields(record, {"path", "sha256"}, label)
    path = safe_file(root, record["path"], tracked=tracked)
    data = path.read_bytes()
    if digest(data) != sha(record["sha256"], f"{label}.sha256"):
        fail(f"{label} hash mismatch: {record['path']}")
    if not data.strip():
        fail(f"{label} evidence is empty")
    return record["path"], data


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def read_json(data: bytes) -> object:
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)


def verify_subject_bytes(root: Path, commit: str, path: str, expected: str) -> None:
    path, _ = safe_relative_path(path, "reviewed subject evidence path")
    if digest(git(root, "cat-file", "blob", f"{commit}:{path}")) != expected:
        fail(f"reviewed subject evidence hash mismatch: {path}")


def validate_receipt(
    root: Path,
    receipt: object,
    *,
    tracked: bool = True,
    require_current_authorities: bool = True,
) -> dict:
    receipt = exact_fields(receipt, RECEIPT_FIELDS, "passed receipt")
    if receipt["schema_version"] != "1.0" or receipt["status"] != "passed":
        fail("terminal audit must have schema_version 1.0 and status passed")
    commit = sha(receipt["subject_commit"], "subject_commit", GIT_SHA)
    tree = sha(receipt["subject_tree"], "subject_tree", GIT_SHA)
    if git(root, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
        fail("subject_commit must identify an exact Git commit")
    if git(root, "rev-parse", "--verify", f"{commit}^{{tree}}").decode().strip() != tree:
        fail("subject_tree does not match subject_commit")
    text(receipt["reviewer_id"], "reviewer_id")
    text(receipt["invocation_id"], "invocation_id")
    if receipt["role_path"] != ROLE_PATH:
        fail("role_path must select the canonical fixed-head-independent-auditor role")
    times = []
    for key in ("started_at", "completed_at"):
        value = text(receipt[key], key)
        if not TIMESTAMP.fullmatch(value):
            fail(f"{key} must have seconds and an explicit UTC offset")
        times.append(datetime.fromisoformat(value.replace("Z", "+00:00")))
    if times[1] < times[0]:
        fail("completed_at precedes started_at")
    criteria_path, _ = pin(root, receipt["criteria"], "criteria", tracked=tracked)
    verify_subject_bytes(root, commit, criteria_path, receipt["criteria"]["sha256"])
    pin(root, receipt["report"], "report", tracked=tracked)
    _, invocation_bytes = pin(root, receipt["invocation_evidence"], "invocation_evidence", tracked=tracked)
    invocation = exact_fields(read_json(invocation_bytes), INVOCATION_FIELDS, "invocation evidence")
    for key in INVOCATION_FIELDS - {"evidence_refs"}:
        if invocation[key] != receipt[key]:
            fail(f"invocation evidence does not match receipt: {key}")
    refs = invocation["evidence_refs"]
    if not isinstance(refs, list) or not refs or len(refs) != len(set(map(str, refs))):
        fail("invocation evidence_refs must be a non-empty unique list")
    for ref in refs:
        safe_file(root, ref, tracked=tracked)
    if receipt["report"]["path"] not in refs:
        fail("invocation evidence_refs must include the pinned report")
    authorities = receipt["authority_hashes"]
    if not isinstance(authorities, dict) or ROLE_PATH not in authorities:
        fail("authority_hashes must pin the canonical role_path")
    for path, expected in authorities.items():
        if require_current_authorities:
            pin(root, {"path": path, "sha256": expected}, "authority", tracked=tracked)
        else:
            safe_relative_path(path, "authority path")
        verify_subject_bytes(root, commit, path, expected)
    return receipt


def validate_workflow(root: Path, locator_path: str) -> str:
    locator = yaml.safe_load(safe_file(root, locator_path, tracked=True).read_text(encoding="utf-8"))
    if not isinstance(locator, dict):
        fail(f"workflow locator is not a mapping: {locator_path}")
    if "terminal_audit" not in locator:
        return "not-selected"
    contract = exact_fields(locator["terminal_audit"], {
        "schema_version", "required", "historical_record", "current_record",
    }, "terminal_audit")
    if contract["schema_version"] != "1.0" or contract["required"] is not True:
        fail("terminal_audit must explicitly require schema_version 1.0")
    history = exact_fields(contract["historical_record"], {"path", "sha256", "disposition"}, "historical_record")
    if history["disposition"] != "superseded-incomplete":
        fail("historical_record disposition must be superseded-incomplete")
    pin(root, {key: history[key] for key in ("path", "sha256")}, "historical_record", tracked=True)
    if history["path"] == contract["current_record"]:
        fail("current_record must not replace historical_record")
    receipt_path = safe_file(root, contract["current_record"], tracked=True)
    receipt = read_json(receipt_path.read_bytes())
    if isinstance(receipt, dict) and receipt.get("status") == "pending":
        exact_fields(receipt, {"schema_version", "status"}, "pending receipt")
        if receipt["schema_version"] != "1.0" or locator.get("status") != "in_progress":
            fail("pending terminal audit is allowed only for an in_progress workflow")
        return "pending (workflow remains in_progress; no terminal acceptance)"
    if locator.get("status") not in {"in_progress", "completed"}:
        fail("selected terminal_audit workflow status must be in_progress or completed")
    validate_receipt(
        root,
        receipt,
        require_current_authorities=locator.get("status") != "completed",
    )
    return f"passed retained audit of {receipt['subject_commit']} (not current-HEAD admission)"


def admit(root: Path, receipt_path: Path) -> str:
    # Explicit admission can consume ignored/untracked outcome files. Nothing is
    # written or excluded from the reviewed full tree to manufacture equality.
    path = receipt_path.absolute()
    no_links(path)
    receipt = validate_receipt(
        root,
        read_json(path.read_bytes()),
        tracked=False,
        require_current_authorities=True,
    )
    if git(root, "status", "--porcelain=v1", "--untracked-files=all").strip():
        fail("admission requires a clean tracked checkout without non-ignored untracked files")
    current = git(root, "rev-parse", "--verify", "HEAD").decode().strip()
    current_tree = git(root, "rev-parse", "--verify", "HEAD^{tree}").decode().strip()
    if current_tree != receipt["subject_tree"]:
        fail("current HEAD full tree differs from reviewed subject; no evidence-only exclusions are permitted")
    return f"admitted {current}; reviewed {receipt['subject_commit']}; identical full tree {current_tree}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--workflow-id")
    selector.add_argument("--admit", type=Path, metavar="RECEIPT_JSON")
    args = parser.parse_args(argv)
    try:
        if args.admit:
            print(f"Target terminal audit: {admit(ROOT, args.admit)}")
            return 0
        if args.workflow_id:
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.workflow_id):
                fail("unsafe workflow-id")
            paths = [f".dev/workflows/{args.workflow_id}/workflow.yaml"]
        else:
            paths = [path for path in git(ROOT, "ls-files", "-z", "--", ".dev/workflows/*/workflow.yaml").decode().split("\0") if path]
        selected = 0
        for path in paths:
            result = validate_workflow(ROOT, path)
            if result != "not-selected":
                selected += 1
                print(f"Target terminal audit: {path}: {result}")
            elif args.workflow_id:
                fail("selected workflow has no explicit terminal_audit contract")
        print(f"Target terminal audit: validated {selected} explicitly selected workflow(s); no historical backfill")
        return 0
    except (OSError, ValueError, TypeError, yaml.YAMLError, subprocess.TimeoutExpired) as exc:
        print(f"Target terminal audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
