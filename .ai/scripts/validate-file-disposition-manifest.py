#!/usr/bin/env python3
"""Validate a workflow file-disposition manifest against repository Git facts."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_DISPOSITIONS = {"kept", "moved-to", "merged-into", "retired"}
DESTINATION_DISPOSITIONS = {"moved-to", "merged-into"}


def run_git(root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return [line for line in result.stdout.splitlines() if line]


def valid_repo_path(value: object, *, allow_directory: bool = True) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if value.startswith("/") or value.startswith("./"):
        return False
    is_directory = value.endswith("/")
    if is_directory and not allow_directory:
        return False
    normalized = value[:-1] if is_directory else value
    path = PurePosixPath(normalized)
    return normalized not in {"", "."} and ".." not in path.parts


def path_exists(path: str, candidates: set[str]) -> bool:
    if path.endswith("/"):
        return any(candidate.startswith(path) for candidate in candidates)
    return path in candidates


def path_is_covered(path: str, entries: set[str]) -> bool:
    return path in entries or any(
        entry.endswith("/") and path.startswith(entry) for entry in entries
    )


def validate_manifest_data(
    data: object,
    *,
    current_paths: set[str],
    base_paths: set[str],
    changed_paths: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be a mapping"]

    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("contract must be a mapping")
    elif set(contract.get("allowed_dispositions", [])) != ALLOWED_DISPOSITIONS:
        errors.append("contract.allowed_dispositions must declare the four supported values")

    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage must be a mapping")
    else:
        base_commit = coverage.get("base_commit")
        if not isinstance(base_commit, str) or len(base_commit) != 40:
            errors.append("coverage.base_commit must be a full Git commit SHA")
        roots = coverage.get("included_roots")
        if not isinstance(roots, list) or not roots:
            errors.append("coverage.included_roots must be a non-empty list")
        elif any(not valid_repo_path(root) or not root.endswith("/") for root in roots):
            errors.append("coverage.included_roots must contain repository-relative directories")

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["entries must be a non-empty list"]

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be a mapping")
            continue
        path = entry.get("path")
        disposition = entry.get("disposition")
        destination = entry.get("destination")

        if not valid_repo_path(path):
            errors.append(f"{label}.path must be a repository-relative exact-case path")
            continue
        if path in seen:
            errors.append(f"{label}.path duplicates {path}")
        seen.add(path)

        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{label}.disposition is unsupported")
            continue
        if disposition in DESTINATION_DISPOSITIONS:
            if not valid_repo_path(destination):
                errors.append(f"{label}.destination is required for {disposition}")
            elif not path_exists(destination, current_paths):
                errors.append(f"{label}.destination does not exist with exact Git casing")
        elif destination is not None:
            errors.append(f"{label}.destination must be null for {disposition}")

        if disposition == "kept":
            if not path_exists(path, current_paths):
                errors.append(f"{label}.path does not exist with exact Git casing")
        elif not path_exists(path, base_paths):
            errors.append(f"{label}.path is absent from the coverage base commit")

        if not isinstance(entry.get("change_summary"), str) or not entry["change_summary"].strip():
            errors.append(f"{label}.change_summary is required")
        if not isinstance(entry.get("target_migration"), str) or not entry["target_migration"].strip():
            errors.append(f"{label}.target_migration is required")

    missing = sorted(path for path in changed_paths if not path_is_covered(path, seen))
    for path in missing:
        errors.append(f"coverage missing changed path: {path}")
    return errors


def collect_git_facts(root: Path, data: dict) -> tuple[set[str], set[str], set[str]]:
    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        return set(), set(), set()
    base_commit = coverage.get("base_commit")
    roots = coverage.get("included_roots")
    if not isinstance(base_commit, str) or not isinstance(roots, list):
        return set(), set(), set()

    run_git(root, "cat-file", "-e", f"{base_commit}^{{commit}}")
    current_paths = set(run_git(root, "ls-files", "--cached", "--others", "--exclude-standard"))
    base_paths = set(run_git(root, "ls-tree", "-r", "--name-only", base_commit))
    changed_paths = set(run_git(root, "diff", "--name-only", base_commit, "--", *roots))
    changed_paths.update(
        path for path in run_git(root, "ls-files", "--others", "--exclude-standard", "--", *roots)
    )
    return current_paths, base_paths, changed_paths


def validate(root: Path, manifest: Path) -> list[str]:
    manifest_path = manifest if manifest.is_absolute() else root / manifest
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return [f"{manifest}: cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{manifest}: root must be a mapping"]
    try:
        current_paths, base_paths, changed_paths = collect_git_facts(root, data)
    except RuntimeError as exc:
        return [f"{manifest}: {exc}"]
    return validate_manifest_data(
        data,
        current_paths=current_paths,
        base_paths=base_paths,
        changed_paths=changed_paths,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    errors = validate(args.root.resolve(), args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"File-disposition manifest validation passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
