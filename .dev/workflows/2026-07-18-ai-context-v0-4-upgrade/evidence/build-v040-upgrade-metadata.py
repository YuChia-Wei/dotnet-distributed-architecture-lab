"""Derive v0.3.0 -> v0.4.0 planner metadata from governed file inventories.

REL-v0.4.0's published package contains clean-install migration metadata even
though its published migration guide requires a governed v0.3.0 files.yaml
baseline. This workflow-local helper replaces only the extracted planning
envelope's migration metadata and member checksum index. It does not alter the
validated release archive or either governed files.yaml inventory.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def load_inventory(path: Path) -> dict[str, dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {entry["path"]: entry for entry in document["files"]}


def operation(
    sequence: int,
    kind: str,
    path: str,
    ownership: str,
) -> dict:
    preconditions = {
        "add": ["destination_absent"],
        "replace": ["current_sha256_equals_previous_release"],
        "remove": ["current_sha256_equals_previous_release"],
        "reconcile": ["human_acknowledgement"],
    }
    return {
        "id": f"v040-upgrade-{sequence:04d}",
        "kind": kind,
        "path": path,
        "ownership": ownership,
        "preconditions": preconditions[kind],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous-files", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    args = parser.parse_args()

    previous_content = args.previous_files.read_bytes()
    incoming_path = args.package_root / "metadata/files.yaml"
    incoming_content = incoming_path.read_bytes()
    previous = load_inventory(args.previous_files)
    incoming = load_inventory(incoming_path)

    changes: list[tuple[str, str, str]] = []
    for path, current in incoming.items():
        prior = previous.get(path)
        if prior is not None and all(
            prior.get(key) == current.get(key)
            for key in ("sha256", "mode", "ownership")
        ):
            continue
        ownership = current["ownership"]
        if prior is None:
            kind = "reconcile" if ownership == "target-owned" else "add"
        elif (
            ownership == "framework-managed"
            and prior.get("ownership") == "framework-managed"
        ):
            kind = "replace"
        else:
            kind = "reconcile"
        changes.append((path, kind, ownership))

    for path, prior in previous.items():
        if path in incoming:
            continue
        ownership = prior["ownership"]
        kind = "remove" if ownership == "framework-managed" else "reconcile"
        changes.append((path, kind, ownership))

    changes.sort(key=lambda item: item[0].encode("utf-8"))
    operations = [
        operation(index, kind, path, ownership)
        for index, (path, kind, ownership) in enumerate(changes, 1)
    ]
    migration = {
        "schema_version": "1.0.0",
        "package_id": f"ai-context-dotnet-backend-v0.4.0",
        "from": {
            "version": "0.3.0",
            "manifest_sha256": sha256(previous_content),
        },
        "to": {
            "version": "0.4.0",
            "manifest_sha256": sha256(incoming_content),
        },
        "operations": operations,
        "safety": {
            "dry_run_default": True,
            "clean_worktree_required": True,
            "starting_commit_required": True,
            "abort_on_unacknowledged_reconciliation": True,
        },
    }
    migration_path = args.package_root / "metadata/migration.yaml"
    migration_path.write_text(
        yaml.safe_dump(migration, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )

    checksum_path = args.package_root / "metadata/SHA256SUMS.txt"
    members = [
        path
        for path in args.package_root.rglob("*")
        if path.is_file() and path != checksum_path
    ]
    checksum_lines = [
        f"{sha256(path.read_bytes())}  {path.relative_to(args.package_root).as_posix()}"
        for path in sorted(
            members,
            key=lambda item: item.relative_to(args.package_root).as_posix().encode(
                "utf-8"
            ),
        )
    ]
    checksum_path.write_text(
        "\n".join(checksum_lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        yaml.safe_dump(
            {
                "previous_files_sha256": sha256(previous_content),
                "incoming_files_sha256": sha256(incoming_content),
                "operation_count": len(operations),
                "operation_kinds": {
                    kind: sum(1 for item in operations if item["kind"] == kind)
                    for kind in ("add", "replace", "remove", "reconcile")
                },
            },
            sort_keys=False,
        ).strip()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
