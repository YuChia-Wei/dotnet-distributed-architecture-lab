#!/usr/bin/env python3
"""Validate a workflow file-disposition manifest against repository Git facts."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_DISPOSITIONS = {"kept", "moved-to", "merged-into", "retired"}
DESTINATION_DISPOSITIONS = {"moved-to", "merged-into"}
V2_DECISIONS = {"retain", "deprecate", "relocate", "remove"}
V2_PUBLISHED_BYTES = {"identical", "evolved"}
V2_LIFECYCLES = {
    "active",
    "compatibility",
    "transitional",
    "retirement-candidate",
    "historical-compatibility",
    "deprecated",
    "removed",
}
V2_DISTRIBUTIONS = {"packaged", "relocated", "excluded"}
SEMVER_TAG = re.compile(r"^v\d+\.\d+\.\d+$")


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


def validate_v1_manifest_data(
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


def non_empty_strings(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def compile_package_glob(pattern: str) -> re.Pattern[str]:
    """Mirror package glob semantics: one star never crosses a slash."""
    expression = ""
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 2
                if index < len(pattern) and pattern[index] == "/":
                    expression += "(?:.*/)?"
                    index += 1
                else:
                    expression += ".*"
                continue
            expression += "[^/]*"
        elif char == "?":
            expression += "[^/]"
        else:
            expression += re.escape(char)
        index += 1
    return re.compile(f"^{expression}$")


def package_glob_matches(path: str, pattern: str) -> bool:
    return bool(compile_package_glob(pattern).fullmatch(path))


def validate_v2_manifest_data(
    data: dict,
    *,
    current_paths: set[str],
    subject_paths: set[str],
    published_paths: dict[str, set[str]],
    packaged_paths: set[str],
    subject_match_paths: set[str],
    published_identical_paths: set[str],
    published_evolved_paths: set[str],
    latest_published_match_paths: set[str],
    base_matches_latest_published: bool,
    actual_profile_id: str | None,
    actual_lifecycles: dict[str, str],
) -> list[str]:
    """Validate the evidence-rich v2 release path disposition contract."""
    errors: list[str] = []
    if data.get("schema_version") != "2.0":
        errors.append("schema_version must be 2.0")
    if not isinstance(data.get("manifest_id"), str) or not data["manifest_id"].strip():
        errors.append("manifest_id must be a non-empty string")
    if not isinstance(data.get("target_release"), str) or not SEMVER_TAG.fullmatch(
        data["target_release"]
    ):
        errors.append("target_release must use vMAJOR.MINOR.PATCH")
    subject_commit = data.get("subject_commit")
    if not isinstance(subject_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", subject_commit):
        errors.append("subject_commit must be a full lowercase Git commit SHA")

    profile = data.get("profile")
    if not isinstance(profile, dict):
        errors.append("profile must be a mapping")
    else:
        profile_path = profile.get("path")
        if not valid_repo_path(profile_path, allow_directory=False):
            errors.append("profile.path must be a repository-relative file")
        elif profile_path not in current_paths:
            errors.append("profile.path must exist with exact Git casing")
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not profile_id:
            errors.append("profile.id must be a non-empty string")
        elif actual_profile_id is not None and profile_id != actual_profile_id:
            errors.append(
                f"profile.id {profile_id!r} differs from profile truth {actual_profile_id!r}"
            )

    versions = data.get("published_versions")
    if not non_empty_strings(versions):
        errors.append("published_versions must be a non-empty list of version tags")
        versions = []
    else:
        if len(versions) != len(set(versions)):
            errors.append("published_versions must not contain duplicates")
        for version in versions:
            if not SEMVER_TAG.fullmatch(version):
                errors.append(f"published_versions contains invalid tag {version!r}")
        version_keys = [
            tuple(int(part) for part in version.removeprefix("v").split("."))
            for version in versions
            if SEMVER_TAG.fullmatch(version)
        ]
        if len(version_keys) == len(versions) and version_keys != sorted(version_keys):
            errors.append("published_versions must be ordered from oldest to newest")
    if set(published_paths) != set(versions):
        errors.append(
            "published version evidence mismatch; "
            f"missing={sorted(set(versions) - set(published_paths))}, "
            f"extra={sorted(set(published_paths) - set(versions))}"
        )

    approval = data.get("approval")
    if not isinstance(approval, dict):
        errors.append("approval must be a mapping")
    else:
        for field in ("authority", "authorized_at", "scope"):
            if not isinstance(approval.get(field), str) or not approval[field].strip():
                errors.append(f"approval.{field} must be a non-empty string")

    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("contract must be a mapping")
    else:
        if set(contract.get("allowed_decisions", [])) != V2_DECISIONS:
            errors.append("contract.allowed_decisions must declare the four v2 decisions")
        for field in ("removal_rule", "compatibility_rule"):
            if not isinstance(contract.get(field), str) or not contract[field].strip():
                errors.append(f"contract.{field} must be a non-empty string")

    coverage = data.get("coverage")
    candidates: list[str] = []
    if not isinstance(coverage, dict):
        errors.append("coverage must be a mapping")
    else:
        base_commit = coverage.get("base_commit")
        if not isinstance(base_commit, str) or not re.fullmatch(
            r"[0-9a-f]{40}", base_commit
        ):
            errors.append("coverage.base_commit must be a full lowercase Git commit SHA")
        elif not base_matches_latest_published:
            errors.append(
                "coverage.base_commit must resolve to the newest published version commit"
            )
        roots = coverage.get("included_roots")
        if not non_empty_strings(roots) or any(
            not valid_repo_path(root) or not root.endswith("/") for root in roots or []
        ):
            errors.append(
                "coverage.included_roots must contain repository-relative directories"
            )
            roots = []
        raw_candidates = coverage.get("candidate_paths")
        if not non_empty_strings(raw_candidates):
            errors.append("coverage.candidate_paths must be a non-empty list")
        else:
            candidates = raw_candidates
            if len(candidates) != len(set(candidates)):
                errors.append("coverage.candidate_paths must not contain duplicates")
            for candidate in candidates:
                if not valid_repo_path(candidate, allow_directory=False):
                    errors.append(
                        f"coverage candidate must be an exact repository file: {candidate!r}"
                    )
                elif not any(candidate.startswith(root) for root in roots):
                    errors.append(
                        f"coverage candidate is outside included_roots: {candidate}"
                    )

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
        if not valid_repo_path(path, allow_directory=False):
            errors.append(f"{label}.path must be a repository-relative exact-case file")
            continue
        if path in seen:
            errors.append(f"{label}.path duplicates {path}")
        seen.add(path)

        decision = entry.get("decision")
        if decision not in V2_DECISIONS:
            errors.append(f"{label}.decision is unsupported")
            continue
        before = entry.get("lifecycle_before")
        after = entry.get("lifecycle_after")
        if before not in V2_LIFECYCLES:
            errors.append(f"{label}.lifecycle_before is unsupported")
        if after not in V2_LIFECYCLES:
            errors.append(f"{label}.lifecycle_after is unsupported")
        elif path in actual_lifecycles and after != actual_lifecycles[path]:
            errors.append(
                f"{label}.lifecycle_after {after!r} differs from registry truth "
                f"{actual_lifecycles[path]!r}"
            )
        distribution = entry.get("distribution_after")
        if distribution not in V2_DISTRIBUTIONS:
            errors.append(f"{label}.distribution_after is unsupported")

        if path not in current_paths:
            errors.append(f"{label}.path does not exist with exact Git casing")
        if path not in subject_paths:
            errors.append(f"{label}.path is absent from subject_commit")
        for version, paths in sorted(published_paths.items()):
            if path not in paths:
                errors.append(f"{label}.path is absent from published version {version}")
        published_bytes = entry.get("published_bytes")
        if published_bytes not in V2_PUBLISHED_BYTES:
            errors.append(
                f"{label}.published_bytes must declare one of "
                f"{sorted(V2_PUBLISHED_BYTES)}"
            )
        elif published_bytes == "identical" and path not in published_identical_paths:
            errors.append(
                f"{label}.published_bytes is not identical across declared versions and subject"
            )
        elif published_bytes == "evolved":
            if path not in published_evolved_paths:
                errors.append(
                    f"{label}.published_bytes does not show an evolved blob history"
                )
            if path not in latest_published_match_paths:
                errors.append(
                    f"{label}.latest published version differs from subject_commit"
                )
        if path not in subject_match_paths:
            errors.append(f"{label}.path differs from the pinned subject_commit")

        replacement = entry.get("replacement")
        destination = entry.get("destination")
        downstream = entry.get("downstream_evidence")
        if decision == "retain":
            if after != before:
                errors.append(f"{label}: retain must preserve lifecycle")
            if distribution != "packaged" or path not in packaged_paths:
                errors.append(f"{label}: retain must remain packaged")
            if replacement is not None or destination is not None:
                errors.append(f"{label}: retain must not declare replacement or destination")
        elif decision == "deprecate":
            if after != "deprecated":
                errors.append(f"{label}: deprecate requires lifecycle_after deprecated")
            if distribution != "packaged" or path not in packaged_paths:
                errors.append(f"{label}: deprecate must retain the packaged path")
            if not isinstance(replacement, str) or not replacement.strip():
                errors.append(f"{label}: deprecate requires a replacement direction")
            if destination is not None:
                errors.append(f"{label}: deprecate-in-place must not declare destination")
        else:
            if not non_empty_strings(downstream):
                errors.append(
                    f"{label}: {decision} requires retained downstream evidence"
                )
            if decision == "relocate":
                if not valid_repo_path(destination, allow_directory=False):
                    errors.append(f"{label}: relocate requires an exact destination file")
                elif destination not in current_paths:
                    errors.append(f"{label}: relocate destination does not exist")
                if distribution != "relocated":
                    errors.append(f"{label}: relocate requires distribution_after relocated")
            if decision == "remove":
                if destination is not None:
                    errors.append(f"{label}: remove must not declare destination")
                if distribution != "excluded":
                    errors.append(f"{label}: remove requires distribution_after excluded")

        for field in ("compatibility_impact", "migration"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f"{label}.{field} must be a non-empty string")
        for field in ("consumer_refs", "evidence_refs"):
            values = entry.get(field)
            if not non_empty_strings(values):
                errors.append(f"{label}.{field} must be a non-empty list")
                continue
            for value in values:
                if not valid_repo_path(value, allow_directory=False):
                    errors.append(f"{label}.{field} contains invalid path {value!r}")
                elif value not in current_paths:
                    errors.append(
                        f"{label}.{field} path does not exist with exact Git casing: {value}"
                    )
        decision_ref = entry.get("decision_ref")
        if not valid_repo_path(decision_ref, allow_directory=False):
            errors.append(f"{label}.decision_ref must be a repository-relative file")
        elif decision_ref not in current_paths:
            errors.append(f"{label}.decision_ref does not exist with exact Git casing")

    if set(candidates) != seen:
        errors.append(
            "candidate/entry parity mismatch; "
            f"missing={sorted(set(candidates) - seen)}, "
            f"extra={sorted(seen - set(candidates))}"
        )
    return errors


def validate_manifest_data(
    data: object,
    *,
    current_paths: set[str],
    base_paths: set[str] | None = None,
    changed_paths: set[str] | None = None,
    subject_paths: set[str] | None = None,
    published_paths: dict[str, set[str]] | None = None,
    packaged_paths: set[str] | None = None,
    subject_match_paths: set[str] | None = None,
    published_identical_paths: set[str] | None = None,
    published_evolved_paths: set[str] | None = None,
    latest_published_match_paths: set[str] | None = None,
    base_matches_latest_published: bool = False,
    actual_profile_id: str | None = None,
    actual_lifecycles: dict[str, str] | None = None,
) -> list[str]:
    """Dispatch legacy v1 and evidence-rich v2 manifest validation."""
    if isinstance(data, dict) and data.get("schema_version") == "2.0":
        return validate_v2_manifest_data(
            data,
            current_paths=current_paths,
            subject_paths=subject_paths or set(),
            published_paths=published_paths or {},
            packaged_paths=packaged_paths or set(),
            subject_match_paths=subject_match_paths or set(),
            published_identical_paths=published_identical_paths or set(),
            published_evolved_paths=published_evolved_paths or set(),
            latest_published_match_paths=latest_published_match_paths or set(),
            base_matches_latest_published=base_matches_latest_published,
            actual_profile_id=actual_profile_id,
            actual_lifecycles=actual_lifecycles or {},
        )
    return validate_v1_manifest_data(
        data,
        current_paths=current_paths,
        base_paths=base_paths or set(),
        changed_paths=changed_paths or set(),
    )


def collect_v1_git_facts(root: Path, data: dict) -> tuple[set[str], set[str], set[str]]:
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


def profile_packaged_paths(
    profile: dict, current_paths: set[str]
) -> set[str]:
    """Resolve source profile include/exclude patterns for current exact paths."""
    include_patterns: list[str] = []
    for entry in profile.get("entries", []):
        if not isinstance(entry, dict):
            continue
        source = entry.get("source")
        if isinstance(source, str):
            include_patterns.append(source)
        elif isinstance(source, list):
            include_patterns.extend(item for item in source if isinstance(item, str))

    exclusions = [
        exclusion
        for exclusion in profile.get("exclusions", [])
        if isinstance(exclusion, dict)
    ]
    packaged: set[str] = set()
    for path in current_paths:
        if not any(package_glob_matches(path, pattern) for pattern in include_patterns):
            continue
        excluded = False
        for exclusion in exclusions:
            patterns = exclusion.get("patterns", [])
            exceptions = exclusion.get("except", [])
            if any(
                isinstance(pattern, str) and package_glob_matches(path, pattern)
                for pattern in patterns
            ) and not any(
                isinstance(pattern, str) and package_glob_matches(path, pattern)
                for pattern in exceptions
            ):
                excluded = True
                break
        if not excluded:
            packaged.add(path)
    return packaged


def collect_v2_git_facts(root: Path, data: dict) -> dict[str, object]:
    """Collect exact current, subject, published, and package-profile evidence."""
    current_paths = set(
        run_git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    )
    subject_commit = data.get("subject_commit")
    coverage = data.get("coverage", {})
    candidates = coverage.get("candidate_paths", []) if isinstance(coverage, dict) else []
    versions = data.get("published_versions", [])
    profile_record = data.get("profile", {})
    profile_value = profile_record.get("path") if isinstance(profile_record, dict) else None

    base_commit = coverage.get("base_commit") if isinstance(coverage, dict) else None
    base_commit_sha: str | None = None
    if isinstance(base_commit, str):
        run_git(root, "cat-file", "-e", f"{base_commit}^{{commit}}")
        resolved = run_git(root, "rev-parse", f"{base_commit}^{{commit}}")
        base_commit_sha = resolved[0] if resolved else None

    if not isinstance(subject_commit, str):
        raise RuntimeError("subject_commit is unavailable")
    run_git(root, "cat-file", "-e", f"{subject_commit}^{{commit}}")
    subject_paths = set(run_git(root, "ls-tree", "-r", "--name-only", subject_commit))

    published_paths: dict[str, set[str]] = {}
    published_commits: dict[str, str] = {}
    for version in versions if isinstance(versions, list) else []:
        if not isinstance(version, str):
            continue
        run_git(root, "cat-file", "-e", f"{version}^{{commit}}")
        resolved = run_git(root, "rev-parse", f"{version}^{{commit}}")
        if resolved:
            published_commits[version] = resolved[0]
        published_paths[version] = set(
            run_git(root, "ls-tree", "-r", "--name-only", version)
        )
    latest_version = (
        versions[-1]
        if isinstance(versions, list) and versions and isinstance(versions[-1], str)
        else None
    )
    base_matches_latest_published = bool(
        base_commit_sha
        and latest_version
        and published_commits.get(latest_version) == base_commit_sha
    )

    profile: dict = {}
    if isinstance(profile_value, str):
        profile_path = root / profile_value
        try:
            loaded = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            raise RuntimeError(f"cannot load package profile {profile_value}: {exc}") from exc
        if isinstance(loaded, dict):
            profile = loaded
    actual_profile_id = (
        profile.get("profile", {}).get("id")
        if isinstance(profile.get("profile"), dict)
        else None
    )
    packaged_paths = profile_packaged_paths(profile, current_paths)
    actual_lifecycles: dict[str, str] = {}
    shell_manifest = root / ".ai/scripts/shell-assets.yaml"
    if shell_manifest.is_file():
        try:
            loaded_shell = yaml.safe_load(shell_manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            raise RuntimeError(f"cannot load shell lifecycle registry: {exc}") from exc
        if isinstance(loaded_shell, dict):
            actual_lifecycles = {
                record["path"]: record["lifecycle"]
                for record in loaded_shell.get("assets", [])
                if isinstance(record, dict)
                and isinstance(record.get("path"), str)
                and isinstance(record.get("lifecycle"), str)
            }

    subject_match_paths: set[str] = set()
    published_identical_paths: set[str] = set()
    published_evolved_paths: set[str] = set()
    latest_published_match_paths: set[str] = set()
    for candidate in candidates if isinstance(candidates, list) else []:
        if not isinstance(candidate, str) or candidate not in current_paths:
            continue
        subject_blob = run_git(root, "rev-parse", f"{subject_commit}:{candidate}")
        current_blob = run_git(root, "hash-object", "--", candidate)
        if subject_blob and current_blob and subject_blob[0] == current_blob[0]:
            subject_match_paths.add(candidate)
        published_blobs: list[str] = []
        for version in versions if isinstance(versions, list) else []:
            if (
                isinstance(version, str)
                and candidate in published_paths.get(version, set())
            ):
                published_blobs.extend(
                    run_git(root, "rev-parse", f"{version}:{candidate}")
                )
        blobs = published_blobs + list(subject_blob)
        if blobs and len(blobs) == 1 + len(versions) and len(set(blobs)) == 1:
            published_identical_paths.add(candidate)
        elif blobs and len(blobs) == 1 + len(versions) and len(set(blobs)) > 1:
            published_evolved_paths.add(candidate)
        if (
            subject_blob
            and published_blobs
            and len(published_blobs) == len(versions)
            and published_blobs[-1] == subject_blob[0]
        ):
            latest_published_match_paths.add(candidate)

    return {
        "current_paths": current_paths,
        "subject_paths": subject_paths,
        "published_paths": published_paths,
        "packaged_paths": packaged_paths,
        "subject_match_paths": subject_match_paths,
        "published_identical_paths": published_identical_paths,
        "published_evolved_paths": published_evolved_paths,
        "latest_published_match_paths": latest_published_match_paths,
        "base_matches_latest_published": base_matches_latest_published,
        "actual_profile_id": actual_profile_id,
        "actual_lifecycles": actual_lifecycles,
    }


def validate(root: Path, manifest: Path) -> list[str]:
    manifest_path = manifest if manifest.is_absolute() else root / manifest
    try:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        return [f"{manifest}: cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{manifest}: root must be a mapping"]
    try:
        if data.get("schema_version") == "2.0":
            facts = collect_v2_git_facts(root, data)
            return validate_manifest_data(data, **facts)
        current_paths, base_paths, changed_paths = collect_v1_git_facts(root, data)
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
