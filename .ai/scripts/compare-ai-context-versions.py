#!/usr/bin/env python3
"""Read-only Git-backed AI context version comparison."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


EXCLUDED_PREFIXES = (
    ".dev/releases/",
    ".git/",
    ".codebase-memory/",
    "src/",
    "tests/",
)
TARGET_OWNED_PREFIXES = (
    ".dev/adr/",
    ".dev/domain-language/",
    ".dev/operations/",
    ".dev/requirement/",
    ".dev/specs/",
)
TARGET_OWNED_FILES = {
    ".dev/ARCHITECTURE.md",
    ".dev/AI-CONTEXT-SOURCE.yaml",
    ".dev/project-config.yaml",
    ".dev/assessments/INDEX.MD",
    ".dev/backlog/INDEX.MD",
    ".dev/workflows/INDEX.MD",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "README.en.md",
    "AGENTS.zh-TW.md",
}


def is_excluded_path(path: str) -> bool:
    return (
        path.startswith(EXCLUDED_PREFIXES)
        or path.startswith(".dev/assessments/ASM-")
        or path.startswith(".dev/backlog/items/")
        or bool(re.match(r"^\.dev/workflows/\d{4}-", path))
    )


def run_git(repo: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=text,
    )


def resolve_ref(repo: Path, ref: str) -> str:
    result = run_git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    if result.returncode != 0:
        raise ValueError(f"cannot resolve Git ref {ref!r}: {result.stderr.strip()}")
    return result.stdout.strip()


def changed_paths(repo: Path, from_ref: str, to_ref: str) -> list[tuple[str, str]]:
    result = run_git(repo, "diff", "--name-status", "--no-renames", from_ref, to_ref)
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git diff failed")
    changes: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        status, path = line.split("\t", 1)
        changes.append((status, PurePosixPath(path).as_posix()))
    return changes


def git_blob(repo: Path, ref: str, path: str) -> bytes | None:
    result = run_git(repo, "show", f"{ref}:{path}", text=False)
    return result.stdout if result.returncode == 0 else None


def classify_change(
    repo: Path,
    from_ref: str,
    status: str,
    path: str,
    target_root: Path | None,
) -> tuple[str, str]:
    if is_excluded_path(path):
        return "exclude", "source history, product code, or local tooling is outside upgrade scope"
    if path in TARGET_OWNED_FILES or path.startswith(TARGET_OWNED_PREFIXES):
        return "reconcile", "path owns target-specific truth"
    if status == "D":
        return "reconcile", "deletion requires release-guide confirmation"
    if target_root is None:
        return "reconcile", "target state was not supplied for three-way comparison"

    target_path = target_root.joinpath(*PurePosixPath(path).parts)
    base = git_blob(repo, from_ref, path)
    if base is None and not target_path.exists():
        return "automatic-candidate", "incoming reusable path is absent from both base and target"
    if base is not None and target_path.is_file() and target_path.read_bytes() == base:
        return "automatic-candidate", "target content is byte-identical to the recorded base"
    return "reconcile", "target differs from base, is absent, or cannot be proven unchanged"


def build_report(repo: Path, from_ref: str, to_ref: str, target_root: Path | None) -> dict:
    from_commit = resolve_ref(repo, from_ref)
    to_commit = resolve_ref(repo, to_ref)
    items = []
    for status, path in changed_paths(repo, from_commit, to_commit):
        classification, reason = classify_change(repo, from_commit, status, path, target_root)
        items.append({"status": status, "path": path, "classification": classification, "reason": reason})
    return {
        "from": {"ref": from_ref, "commit": from_commit},
        "to": {"ref": to_ref, "commit": to_commit},
        "target_root": str(target_root.resolve()) if target_root else None,
        "read_only": True,
        "changes": items,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# AI Context Version Comparison",
        "",
        f"- From: `{report['from']['ref']}` (`{report['from']['commit']}`)",
        f"- To: `{report['to']['ref']}` (`{report['to']['commit']}`)",
        f"- Target: `{report['target_root'] or 'not supplied'}`",
        "- Mode: read-only",
    ]
    for category in ("automatic-candidate", "reconcile", "exclude"):
        lines.extend(["", f"## {category}", "", "| Status | Path | Reason |", "| --- | --- | --- |"])
        selected = [item for item in report["changes"] if item["classification"] == category]
        if selected:
            lines.extend(f"| `{item['status']}` | `{item['path']}` | {item['reason']} |" for item in selected)
        else:
            lines.append("| - | - | none |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-ref", required=True)
    parser.add_argument("--to-ref", required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--target-root", type=Path)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    try:
        report = build_report(args.repo.resolve(), args.from_ref, args.to_ref, args.target_root)
    except (OSError, ValueError) as exc:
        print(f"AI context version comparison failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2) if args.format == "json" else render_markdown(report), end="\n" if args.format == "json" else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
