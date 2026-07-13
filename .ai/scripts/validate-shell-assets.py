#!/usr/bin/env python3
"""Validate shell asset classification and executable modes from Git index truth."""

from __future__ import annotations

import subprocess
import sys
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(".ai/scripts/shell-assets.yaml")
GROUPS = ("retained", "retirement_candidates")
REQUIRED_GROUPS = ("required_entrypoints", "check_all_required_scripts")
RUN_CHECK_START = re.compile(r'^\s*run_check\s+"([^"]+)"\s*\\\s*$')


def runner_required_scripts(errors: list[str], modes: dict[str, str]) -> set[str] | None:
    runner = ".ai/scripts/check-all.sh"
    if runner not in modes:
        return None
    try:
        lines = (ROOT / runner).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{runner}: cannot inspect required child declarations: {exc}")
        return set()

    required: set[str] = set()
    for index, line in enumerate(lines):
        match = RUN_CHECK_START.match(line)
        if match and index + 2 < len(lines) and lines[index + 2].strip().startswith('"required"'):
            required.add(f".ai/scripts/{match.group(1)}")
    return required


def git_shell_modes(errors: list[str]) -> dict[str, str]:
    result = subprocess.run(
        ["git", "ls-files", "--stage", "*.sh"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append(f"git ls-files --stage failed: {result.stderr.strip()}")
        return {}
    modes: dict[str, str] = {}
    for line in result.stdout.splitlines():
        metadata, path = line.split("\t", 1)
        mode = metadata.split(" ", 1)[0]
        if (
            path.startswith(".ai/scripts/")
            and path.endswith(".sh")
            and (ROOT / path).is_file()
        ):
            modes[path] = mode
    return modes


def main() -> int:
    errors: list[str] = []
    try:
        manifest = yaml.safe_load((ROOT / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        print(f"Shell asset validation failed:\n- {MANIFEST}: invalid YAML: {exc}")
        return 1
    if not isinstance(manifest, dict):
        print(f"Shell asset validation failed:\n- {MANIFEST}: root must be a mapping")
        return 1
    if manifest.get("schema_version") != "1.0":
        errors.append(f"{MANIFEST}: schema_version must be 1.0")

    values: dict[str, list[str]] = {}
    for group in (*GROUPS, *REQUIRED_GROUPS):
        items = manifest.get(group)
        if not isinstance(items, list) or not all(isinstance(item, str) and item for item in items):
            errors.append(f"{MANIFEST}: {group} must be a list of non-empty paths")
            values[group] = []
        else:
            values[group] = items
            if len(items) != len(set(items)):
                errors.append(f"{MANIFEST}: {group} contains duplicate paths")

    retained = set(values.get("retained", []))
    retirement = set(values.get("retirement_candidates", []))
    overlap = sorted(retained & retirement)
    if overlap:
        errors.append(f"{MANIFEST}: lifecycle groups overlap: {overlap}")

    modes = git_shell_modes(errors)
    classified = retained | retirement
    if classified != set(modes):
        errors.append(
            f"{MANIFEST}: tracked shell coverage mismatch; "
            f"missing={sorted(set(modes) - classified)}, extra={sorted(classified - set(modes))}"
        )
    for path in sorted(retained):
        if modes.get(path) != "100755":
            errors.append(f"{path}: retained shell asset must use Git mode 100755, found {modes.get(path, 'missing')}")
    for group in REQUIRED_GROUPS:
        outside = sorted(set(values.get(group, [])) - retained)
        if outside:
            errors.append(f"{MANIFEST}: {group} must be a subset of retained: {outside}")

    runner_required = runner_required_scripts(errors, modes)
    if runner_required is not None:
        declared_required = set(values.get("check_all_required_scripts", []))
        if runner_required != declared_required:
            errors.append(
                f"{MANIFEST}: check_all required-script coverage mismatch; "
                f"missing={sorted(runner_required - declared_required)}, "
                f"extra={sorted(declared_required - runner_required)}"
            )

    if errors:
        print("Shell asset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Shell asset validation passed for {len(retained)} retained executable asset(s), "
        f"{len(retirement)} retirement candidate(s), and {len(modes)} tracked shell asset(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
