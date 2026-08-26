#!/usr/bin/env python3
"""Reconcile omitted receipt-required paths from a trusted package payload."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

import yaml


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalized(value: bytes) -> bytes:
    return value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git_blob(repo: Path, commit: str, path: str) -> tuple[str | None, str | None]:
    blob = subprocess.run(
        ["git", "rev-parse", f"{commit}:{path}"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if blob.returncode != 0:
        return None, None
    content = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=repo,
        check=True,
        capture_output=True,
    ).stdout
    return blob.stdout.strip(), sha256(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    payload = args.payload.resolve()
    receipt_path = args.receipt.resolve()
    receipt_bytes = receipt_path.read_bytes()
    receipt = yaml.safe_load(receipt_bytes)
    required = receipt.get("required_framework_paths", [])
    starting_commit = str(receipt["target_starting_commit"])
    records: list[dict[str, object]] = []

    for item in required:
        path = str(item["path"])
        target_path = repo / path
        source_path = payload / path
        expected = str(item["sha256"])
        if not source_path.is_file():
            raise SystemExit(f"trusted payload is missing required path: {path}")
        incoming = source_path.read_bytes()
        if sha256(incoming) != expected:
            raise SystemExit(f"trusted payload hash differs from receipt: {path}")
        before = target_path.read_bytes() if target_path.is_file() else None
        before_hash = sha256(before) if before is not None else None
        if before_hash == expected:
            continue
        if before is None:
            classification = "unchanged-package-path/missing-target"
        elif normalized(before) == normalized(incoming):
            classification = "unchanged-package-path/eol-only-target-drift"
        else:
            classification = "unchanged-package-path/semantic-target-drift"
        blob, starting_hash = git_blob(repo, starting_commit, path)
        if args.apply:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target_path)
        result_hash = sha256(target_path.read_bytes()) if target_path.is_file() else None
        records.append(
            {
                "path": path,
                "component_id": str(item["component_id"]),
                "ownership": str(item["ownership"]),
                "classification": classification,
                "before_sha256": before_hash,
                "target_starting_commit_blob": blob,
                "target_starting_commit_sha256": starting_hash,
                "expected_sha256": expected,
                "result_sha256": result_hash,
                "source": f"published-v0.9.0-payload:{path}",
                "decision_evidence": (
                    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
                    "evidence/v0.9.0/owner-decision-3.yaml"
                ),
            }
        )

    failed = [record["path"] for record in records if record["result_sha256"] != record["expected_sha256"]]
    counts: dict[str, int] = {}
    for record in records:
        key = str(record["classification"])
        counts[key] = counts.get(key, 0) + 1

    evidence = {
        "schema_version": "1.0",
        "workflow_id": "2026-08-12-ai-context-v0-13-upgrade",
        "framework_version": "v0.9.0",
        "package_commit": "c14a3260cba7d0a9e2b67b73df9e221280d2d2ef",
        "receipt": str(receipt_path.relative_to(repo)).replace("\\", "/"),
        "receipt_sha256": sha256(receipt_bytes),
        "target_starting_commit": starting_commit,
        "operation": "copy-exact-published-bytes-for-unplanned-required-paths",
        "receipt_modified": False,
        "applied": bool(args.apply),
        "summary": {
            "required_path_count": len(required),
            "reconciled_path_count": len(records),
            "classifications": dict(sorted(counts.items())),
            "failed_result_count": len(failed),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(evidence, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    if failed:
        print("Required-path reconciliation failed:")
        for path in failed:
            print(f"- {path}")
        return 1
    print(
        "Required-path reconciliation completed: "
        f"required={len(required)} reconciled={len(records)} "
        f"classifications={dict(sorted(counts.items()))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
