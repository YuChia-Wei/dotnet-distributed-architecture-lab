#!/usr/bin/env python3
"""Validate shell asset roles, lifecycle, distribution, and Git index truth."""

from __future__ import annotations

from collections import Counter
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(".ai/scripts/shell-assets.yaml")
ROLES = {
    "active-orchestrator",
    "context-validator",
    "compatibility-entrypoint",
    "manual-advisory",
    "transitional-helper",
}
LIFECYCLES = {
    "active",
    "compatibility",
    "transitional",
    "retirement-candidate",
    "deprecated",
}
DISTRIBUTIONS = {"packaged", "source-only"}
AUTHORITIES = {"orchestration-only", "structural", "context", "advisory"}
REQUIRED_GROUPS = ("required_entrypoints", "check_all_required_scripts")
COMMAND_GROUPS = ("check_all_required_commands",)
RUN_CHECK_START = re.compile(r'^\s*run_check\s+"([^"]+)"\s*\\\s*$')
RUN_COMMAND_START = re.compile(r'^\s*run_command_check\s+"([^"]+)"\s*\\\s*$')


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


def runner_required_commands(errors: list[str], modes: dict[str, str]) -> set[str] | None:
    runner = ".ai/scripts/check-all.sh"
    if runner not in modes:
        return None
    try:
        lines = (ROOT / runner).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{runner}: cannot inspect required command declarations: {exc}")
        return set()
    required: set[str] = set()
    for index, line in enumerate(lines):
        match = RUN_COMMAND_START.match(line)
        if match and not match.group(1).startswith("$") and index + 2 < len(lines):
            if lines[index + 2].strip().startswith('"required"'):
                required.add(match.group(1))
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
        if path.startswith(".ai/scripts/") and path.endswith(".sh") and (ROOT / path).is_file():
            modes[path] = mode
    return modes


def validate_manifest(manifest: object, modes: dict[str, str], errors: list[str]) -> dict[str, dict]:
    if not isinstance(manifest, dict):
        errors.append(f"{MANIFEST}: root must be a mapping")
        return {}
    if manifest.get("schema_version") != "2.0":
        errors.append(f"{MANIFEST}: schema_version must be 2.0")

    contract = manifest.get("contract")
    if not isinstance(contract, dict):
        errors.append(f"{MANIFEST}: contract must be a mapping")
    else:
        for field in ("distribution_rule", "authority_rule"):
            if not isinstance(contract.get(field), str) or not contract[field].strip():
                errors.append(f"{MANIFEST}: contract.{field} is required")

    records = manifest.get("assets")
    if not isinstance(records, list):
        errors.append(f"{MANIFEST}: assets must be a list")
        records = []

    assets: dict[str, dict] = {}
    for index, record in enumerate(records):
        label = f"{MANIFEST}: assets[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be a mapping")
            continue
        path = record.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{label}.path is required")
            continue
        if path in assets:
            errors.append(f"{MANIFEST}: assets contains duplicate path {path}")
        assets[path] = record
        if record.get("role") not in ROLES:
            errors.append(f"{label}.role is unsupported")
        if record.get("lifecycle") not in LIFECYCLES:
            errors.append(f"{label}.lifecycle is unsupported")
        if record.get("distribution") not in DISTRIBUTIONS:
            errors.append(f"{label}.distribution is unsupported")
        if record.get("authority") not in AUTHORITIES:
            errors.append(f"{label}.authority is unsupported")
        replacement = record.get("replacement")
        if record.get("lifecycle") in {
            "compatibility",
            "transitional",
            "retirement-candidate",
            "deprecated",
        }:
            if not isinstance(replacement, str) or not replacement.strip():
                errors.append(f"{label}.replacement is required for non-active lifecycle")
        elif replacement is not None:
            errors.append(f"{label}.replacement must be null for active lifecycle")
        if record.get("role") == "transitional-helper" and record.get("lifecycle") not in {
            "transitional",
            "retirement-candidate",
            "deprecated",
        }:
            errors.append(
                f"{label}: transitional-helper must use transitional, "
                "retirement-candidate, or deprecated lifecycle"
            )

    if set(assets) != set(modes):
        errors.append(
            f"{MANIFEST}: tracked shell coverage mismatch; "
            f"missing={sorted(set(modes) - set(assets))}, extra={sorted(set(assets) - set(modes))}"
        )
    for path, record in sorted(assets.items()):
        if modes.get(path) != "100755":
            errors.append(f"{path}: tracked shell asset must use Git mode 100755, found {modes.get(path, 'missing')}")
        if record.get("distribution") == "source-only" and record.get("lifecycle") == "compatibility":
            errors.append(f"{path}: compatibility assets must remain packaged or move to transitional lifecycle")

    for group in (*REQUIRED_GROUPS, *COMMAND_GROUPS):
        values = manifest.get(group)
        if not isinstance(values, list) or not all(isinstance(item, str) and item for item in values):
            errors.append(f"{MANIFEST}: {group} must be a list of non-empty strings")
            continue
        if len(values) != len(set(values)):
            errors.append(f"{MANIFEST}: {group} contains duplicates")
        if group in REQUIRED_GROUPS:
            for path in values:
                record = assets.get(path)
                if record is None:
                    errors.append(f"{MANIFEST}: {group} contains unclassified path {path}")
                elif record.get("lifecycle") not in {"active", "compatibility"}:
                    errors.append(f"{MANIFEST}: {group} contains non-runnable lifecycle path {path}")
                elif record.get("distribution") != "packaged":
                    errors.append(f"{MANIFEST}: {group} path must be packaged: {path}")
    return assets


def main() -> int:
    errors: list[str] = []
    try:
        manifest = yaml.safe_load((ROOT / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        print(f"Shell asset validation failed:\n- {MANIFEST}: invalid YAML: {exc}")
        return 1

    modes = git_shell_modes(errors)
    assets = validate_manifest(manifest, modes, errors)
    if isinstance(manifest, dict):
        runner_required = runner_required_scripts(errors, modes)
        if runner_required is not None:
            declared = set(manifest.get("check_all_required_scripts", []))
            if runner_required != declared:
                errors.append(
                    f"{MANIFEST}: check_all required-script coverage mismatch; "
                    f"missing={sorted(runner_required - declared)}, extra={sorted(declared - runner_required)}"
                )
        runner_commands = runner_required_commands(errors, modes)
        if runner_commands is not None:
            declared = set(manifest.get("check_all_required_commands", []))
            if runner_commands != declared:
                errors.append(
                    f"{MANIFEST}: check_all required-command coverage mismatch; "
                    f"missing={sorted(runner_commands - declared)}, extra={sorted(declared - runner_commands)}"
                )

    if errors:
        print("Shell asset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    lifecycle_counts = Counter(record["lifecycle"] for record in assets.values())
    role_counts = Counter(record["role"] for record in assets.values())
    print(
        f"Shell asset validation passed for {len(assets)} tracked asset(s): "
        f"lifecycle={dict(sorted(lifecycle_counts.items()))}; "
        f"roles={dict(sorted(role_counts.items()))}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
