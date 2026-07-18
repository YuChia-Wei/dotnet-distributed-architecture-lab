#!/usr/bin/env python3
"""Validate selected Git commit messages against repository policy."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".dev/standards/GIT-COMMIT-POLICY.yaml"


def git(*args: str, root: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def selected_commits(commit_range: str | None, commit: str | None, root: Path = ROOT) -> list[str]:
    if commit_range:
        return [line for line in git("rev-list", "--reverse", commit_range, root=root).splitlines() if line]
    return [git("rev-parse", commit or "HEAD", root=root).strip()]


def section_positions(message: str, required: list[str]) -> dict[str, int]:
    positions: dict[str, int] = {}
    for index, line in enumerate(message.splitlines()):
        normalized = line.strip().removesuffix(":")
        if normalized in required and normalized not in positions:
            positions[normalized] = index
    return positions


def validate_message(
    sha: str,
    message: str,
    policy: dict[str, object],
    errors: list[str],
    workflow_id: str | None = None,
) -> None:
    lines = message.rstrip().splitlines()
    subject = lines[0] if lines else ""
    if not re.fullmatch(str(policy["subject_pattern"]), subject):
        errors.append(f"{sha}: subject does not match policy: {subject}")

    signature = policy["ai_signature"]
    assert isinstance(signature, dict)
    trailer_name = str(signature["trailer"])
    trailer_pattern = re.compile(str(signature["value_pattern"]))
    final_line = lines[-1] if lines else ""
    prefix = f"{trailer_name}: "
    if not final_line.startswith(prefix) or not trailer_pattern.fullmatch(final_line[len(prefix):]):
        errors.append(f"{sha}: final non-empty line must be a valid {trailer_name} trailer")

    assessment = policy["assessment"]
    assert isinstance(assessment, dict)
    assessment_ids = re.findall(str(assessment["subject_id_pattern"]), subject)
    if assessment_ids:
        assessment_trailers = [
            line.split(":", 1)[1].strip()
            for line in lines
            if line.startswith(f"{assessment['trailer']}:")
        ]
        for assessment_id in assessment_ids:
            if assessment_id not in assessment_trailers:
                errors.append(f"{sha}: subject assessment ID lacks matching Assessment-Id trailer: {assessment_id}")

    if workflow_id:
        workflow = policy["workflow"]
        assert isinstance(workflow, dict)
        required = [str(value) for value in workflow["required_sections"]]
        positions = section_positions(message, required)
        missing = [section for section in required if section not in positions]
        if missing:
            errors.append(f"{sha}: missing workflow body sections: {', '.join(missing)}")
        elif [positions[section] for section in required] != sorted(positions.values()):
            errors.append(f"{sha}: workflow body sections are out of order")
        workflow_start = positions.get("Workflow")
        workflow_text = "\n".join(lines[workflow_start + 1 :]) if workflow_start is not None else ""
        if workflow_id not in workflow_text:
            errors.append(f"{sha}: Workflow section does not identify {workflow_id}")


def validate_commits(
    shas: list[str],
    policy: dict[str, object],
    workflow_id: str | None = None,
    root: Path = ROOT,
) -> list[str]:
    errors: list[str] = []
    for sha in shas:
        message = git("show", "-s", "--format=%B", sha, root=root)
        validate_message(sha, message, policy, errors, workflow_id)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--range", dest="commit_range", help="Git revision range, for example main..HEAD")
    selector.add_argument("--commit", help="Single commit-ish; defaults to HEAD")
    parser.add_argument("--workflow-id", help="Require workflow sections and this workflow identity")
    args = parser.parse_args()

    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    shas = selected_commits(args.commit_range, args.commit)
    if not shas:
        print("Git commit validation failed: selected range contains no commits")
        return 1
    errors = validate_commits(shas, policy, args.workflow_id)
    if errors:
        print("Git commit validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Git commit validation passed for {len(shas)} commit(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
