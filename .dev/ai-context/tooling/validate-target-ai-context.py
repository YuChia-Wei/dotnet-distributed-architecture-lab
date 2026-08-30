#!/usr/bin/env python3
"""Run the downstream-applicable AI context validation gate."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / ".dev/ai-context/tooling/target-gate-manifest.yaml"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, object]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("target gate manifest must be a mapping")
    if str(manifest.get("schema_version")) != "1.0":
        raise ValueError("target gate manifest schema_version must be 1.0")
    if str(manifest.get("framework_version")) != "v0.14.0":
        raise ValueError("target gate manifest must be explicitly pinned to v0.14.0")
    expected_diagnostics = manifest.get("unfinalized_target_diagnostics")
    if not isinstance(expected_diagnostics, list) or not expected_diagnostics or not all(
        isinstance(value, str) and value for value in expected_diagnostics
    ):
        raise ValueError(
            "target gate manifest unfinalized_target_diagnostics must be a non-empty string list"
        )
    checks = manifest.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("target gate manifest checks must be a non-empty list")
    seen: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict) or set(check) != {"id", "path", "sha256", "args"}:
            raise ValueError(f"checks[{index}] has an invalid shape")
        identifier = str(check["id"])
        if identifier in seen:
            raise ValueError(f"duplicate target gate check id: {identifier}")
        seen.add(identifier)
        path = ROOT / str(check["path"])
        if not path.is_file():
            raise ValueError(f"target gate dependency is missing: {check['path']}")
        actual = digest(path)
        if actual != str(check["sha256"]):
            raise ValueError(
                f"target gate dependency hash mismatch: {check['path']} "
                f"expected={check['sha256']} actual={actual}"
            )
        if not isinstance(check["args"], list) or not all(
            isinstance(value, str) for value in check["args"]
        ):
            raise ValueError(f"checks[{index}].args must be a string list")
    return manifest


def run(command: list[str]) -> int:
    print(f"==> {' '.join(command)}", flush=True)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode


def run_allowing_exact_diagnostics(
    command: list[str],
    expected_diagnostics: list[str],
) -> int:
    """Accept only the exact fail-closed catalog-staleness transition output."""
    print(f"==> {' '.join(command)}", flush=True)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode == 0:
        return 0
    expected_lines = [
        "AI context target validation failed:",
        *[f"- {diagnostic}" for diagnostic in expected_diagnostics],
    ]
    if not result.stderr.strip() and result.stdout.strip().splitlines() == expected_lines:
        print(
            "Accepted exact unfinalized target diagnostic; action readiness remains "
            "fail-closed until authority regeneration."
        )
        return 0
    return result.returncode


def build_commands(
    manifest: dict[str, object],
    args: argparse.Namespace,
    python: str,
) -> list[list[str]]:
    """Build the target-applicable command set for one validation phase."""
    commands: list[list[str]] = []
    for check in manifest["checks"]:
        if check["id"] == "target-provenance" and args.allow_unfinalized:
            # The package transaction records target validation before it can
            # bind the receipt that validate-ai-context-target requires. The
            # transaction recorder and finalization gate validate provenance
            # after that receipt exists; running it here would be circular.
            continue
        command = [
            python,
            "-B",
            str(check["path"]),
            *[str(value) for value in check["args"]],
        ]
        if check["id"] == "target-provenance" and args.require_effective_rules:
            command.append("--require-effective-rules")
        commands.append(command)
    commands.append(
        [
            python,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            ".dev/ai-context/tooling/tests",
            "-p",
            "test_*.py",
            "-v",
        ],
    )
    if args.commit_range or args.commit:
        commit_command = [
            python,
            "-B",
            ".dev/ai-context/tooling/git-commit-policy/validate-target-git-commits.py",
        ]
        if args.commit_range:
            commit_command.extend(["--range", args.commit_range])
        else:
            commit_command.extend(["--commit", args.commit])
        if args.workflow_id:
            commit_command.extend(["--workflow-id", args.workflow_id])
        commands.append(commit_command)
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commit_selector = parser.add_mutually_exclusive_group()
    commit_selector.add_argument("--commit-range")
    commit_selector.add_argument("--commit")
    parser.add_argument("--workflow-id")
    parser.add_argument("--allow-unfinalized", action="store_true")
    parser.add_argument("--require-effective-rules", action="store_true")
    args = parser.parse_args()

    try:
        manifest = load_manifest()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Target AI context validation failed: {exc}")
        return 1

    commands = build_commands(manifest, args, sys.executable)

    for command in commands:
        result = run(command)
        if result != 0:
            print("Target AI context validation failed.")
            return 1
    print("Target AI context validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
