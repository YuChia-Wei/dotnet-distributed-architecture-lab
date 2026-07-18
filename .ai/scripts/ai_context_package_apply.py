#!/usr/bin/env python3
"""Fail-closed planning and application for extracted AI context packages."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

import yaml


class ApplyError(ValueError):
    """A package application safety contract violation."""


@dataclass(frozen=True)
class FileState:
    exists: bool
    sha256: str | None
    mode: str | None


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def safe_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ApplyError(f"{label} must be a non-empty POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ApplyError(f"unsafe {label}: {value!r}")
    return path.as_posix()


def load_yaml(path: Path, label: str) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ApplyError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ApplyError(f"{label} root must be a mapping")
    return value


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )


def clean_target_head(root: Path) -> str:
    if not (root / ".git").exists():
        raise ApplyError("target must be a Git repository")
    head_result = run_git(root, "rev-parse", "--verify", "HEAD^{commit}")
    head = head_result.stdout.strip() if head_result.returncode == 0 else ""
    if len(head) != 40 or any(char not in "0123456789abcdef" for char in head):
        raise ApplyError("target must have a committed HEAD before planning or apply")
    status_result = run_git(root, "status", "--porcelain", "--untracked-files=all")
    if status_result.returncode != 0:
        raise ApplyError("cannot inspect target Git status")
    if status_result.stdout:
        raise ApplyError("target Git worktree must be clean before planning or apply")
    return head


def tracked_mode(root: Path, relative: str) -> str | None:
    result = run_git(root, "ls-files", "--stage", "--", relative)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    modes = {line.split(" ", 1)[0] for line in result.stdout.splitlines() if line}
    if len(modes) != 1:
        raise ApplyError(f"cannot determine one Git mode for {relative}")
    mode = next(iter(modes))
    if mode == "100644":
        return "0644"
    if mode == "100755":
        return "0755"
    raise ApplyError(f"unsupported target Git mode {mode} for {relative}")


def filesystem_mode(path: Path) -> str:
    return "0755" if path.stat().st_mode & stat.S_IXUSR else "0644"


def file_state(root: Path, relative: str) -> FileState:
    path = root / Path(*PurePosixPath(relative).parts)
    if not path.exists():
        return FileState(False, None, None)
    if path.is_symlink() or not path.is_file():
        raise ApplyError(f"target path must be a regular file: {relative}")
    return FileState(
        True,
        sha256_bytes(path.read_bytes()),
        tracked_mode(root, relative) or filesystem_mode(path),
    )


def reject_symlink_boundary(root: Path, relative: str) -> None:
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ApplyError(f"symlink boundary is not allowed: {relative}")


def existing_case_map(root: Path) -> dict[str, str]:
    paths: dict[str, str] = {}
    for directory, names, files in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        if directory_path == root / ".git":
            names[:] = []
            continue
        names[:] = [name for name in names if directory_path / name != root / ".git"]
        for name in [*names, *files]:
            relative = (directory_path / name).relative_to(root).as_posix()
            key = relative.casefold()
            previous = paths.get(key)
            if previous is not None and previous != relative:
                raise ApplyError(f"case-fold collision in target: {previous} and {relative}")
            paths[key] = relative
    return paths


def inventory_records(document: dict, label: str) -> tuple[dict[str, dict], list[str]]:
    records = document.get("files")
    if not isinstance(records, list):
        raise ApplyError(f"{label} files must be a list")
    output: dict[str, dict] = {}
    case_paths: dict[str, str] = {}
    order: list[str] = []
    for raw in records:
        if not isinstance(raw, dict):
            raise ApplyError(f"{label} file entries must be mappings")
        path = safe_path(raw.get("path"), f"{label} file path")
        if path in output:
            raise ApplyError(f"duplicate {label} path: {path}")
        parts = PurePosixPath(path).parts
        for index in range(1, len(parts) + 1):
            prefix = PurePosixPath(*parts[:index]).as_posix()
            folded = prefix.casefold()
            if folded in case_paths and case_paths[folded] != prefix:
                raise ApplyError(f"case-fold collision in {label}: {case_paths[folded]} and {prefix}")
            case_paths[folded] = prefix
        digest, mode = raw.get("sha256"), raw.get("mode")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ApplyError(f"invalid {label} sha256: {path}")
        if mode not in {"0644", "0755"}:
            raise ApplyError(f"invalid {label} mode: {path}")
        output[path] = raw
        order.append(path)
    if order != sorted(order, key=lambda item: item.encode("utf-8")):
        raise ApplyError(f"{label} paths must use UTF-8 bytewise order")
    return output, order


def validate_extracted_checksums(package_root: Path) -> None:
    checksum_path = package_root / "metadata/SHA256SUMS.txt"
    if not checksum_path.is_file() or checksum_path.is_symlink():
        raise ApplyError("missing regular metadata/SHA256SUMS.txt")
    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        try:
            digest, relative_value = line.split("  ", 1)
        except ValueError as exc:
            raise ApplyError("invalid SHA256SUMS entry") from exc
        relative = safe_path(relative_value, "SHA256SUMS path")
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest) or relative in expected:
            raise ApplyError("invalid or duplicate SHA256SUMS entry")
        expected[relative] = digest
    actual: dict[str, str] = {}
    for directory, names, files in os.walk(package_root, followlinks=False):
        directory_path = Path(directory)
        for name in names:
            candidate = directory_path / name
            if candidate.is_symlink():
                raise ApplyError(f"symlink directory in extracted package: {candidate.relative_to(package_root).as_posix()}")
        for name in files:
            candidate = directory_path / name
            relative = candidate.relative_to(package_root).as_posix()
            if relative == "metadata/SHA256SUMS.txt":
                continue
            if candidate.is_symlink() or not candidate.is_file():
                raise ApplyError(f"non-regular extracted package member: {relative}")
            actual[relative] = sha256_bytes(candidate.read_bytes())
    if actual != expected:
        raise ApplyError("SHA256SUMS does not exactly cover the extracted package")


def validate_package_root(package_root: Path) -> tuple[dict, dict[str, dict], dict, str]:
    package_root = package_root.resolve()
    validate_extracted_checksums(package_root)
    package_path = package_root / "metadata/package.yaml"
    files_path = package_root / "metadata/files.yaml"
    migration_path = package_root / "metadata/migration.yaml"
    for path in (package_path, files_path, migration_path):
        if not path.is_file():
            raise ApplyError(f"missing extracted package metadata: {path.name}")
    package = load_yaml(package_path, "package.yaml")
    files_bytes = files_path.read_bytes()
    inventory = load_yaml(files_path, "files.yaml")
    migration = load_yaml(migration_path, "migration.yaml")
    package_id = package.get("package_id")
    if not isinstance(package_id, str) or not package_id:
        raise ApplyError("package.yaml package_id is required")
    if inventory.get("package_id") != package_id or migration.get("package_id") != package_id:
        raise ApplyError("package identity mismatch")
    records, _ = inventory_records(inventory, "incoming inventory")
    for relative, record in records.items():
        payload = package_root / "payload" / Path(*PurePosixPath(relative).parts)
        reject_symlink_boundary(package_root / "payload", relative)
        if not payload.is_file() or payload.is_symlink():
            raise ApplyError(f"missing regular payload file: {relative}")
        content = payload.read_bytes()
        if record["sha256"] != sha256_bytes(content) or record.get("size") != len(content):
            raise ApplyError(f"payload hash or size mismatch: {relative}")
    manifest_sha = sha256_bytes(files_bytes)
    to_data = migration.get("to")
    if not isinstance(to_data, dict) or to_data.get("manifest_sha256") != manifest_sha:
        raise ApplyError("migration target manifest SHA does not match files.yaml")
    return package, records, migration, manifest_sha


def previous_records(path: Path | None, migration: dict) -> dict[str, dict]:
    from_data = migration.get("from")
    if not isinstance(from_data, dict):
        raise ApplyError("migration from must be a mapping")
    expected = from_data.get("manifest_sha256")
    version = from_data.get("version")
    if expected is None and version is None:
        if path is not None:
            raise ApplyError("clean install must not supply a previous files manifest")
        return {}
    if not isinstance(expected, str) or len(expected) != 64 or not isinstance(version, str):
        raise ApplyError("upgrade migration requires previous version and manifest SHA")
    if path is None:
        raise ApplyError("upgrade migration requires --previous-files")
    content = path.read_bytes()
    if sha256_bytes(content) != expected:
        raise ApplyError("previous files manifest SHA does not match migration.from")
    records, _ = inventory_records(load_yaml(path, "previous files.yaml"), "previous inventory")
    return records


def state_matches(state: FileState, record: dict) -> bool:
    return state.exists and state.sha256 == record.get("sha256") and state.mode == record.get("mode")


def observation(paths: Iterable[str], target: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(set(paths), key=lambda item: item.encode("utf-8")):
        reject_symlink_boundary(target, path)
        state = file_state(target, path)
        result[path] = {"exists": state.exists, "sha256": state.sha256, "mode": state.mode}
    return result


def build_plan(
    package_root: Path,
    target_root: Path,
    previous_files_path: Path | None = None,
) -> dict:
    target = target_root.resolve()
    head = clean_target_head(target)
    package, incoming, migration, manifest_sha = validate_package_root(package_root)
    previous = previous_records(previous_files_path, migration)
    operations = migration.get("operations")
    if not isinstance(operations, list):
        raise ApplyError("migration operations must be a list")
    ids: set[str] = set()
    touched_paths: dict[str, str] = {}
    operation_paths: list[str] = []
    normalized: list[dict] = []
    case_map = existing_case_map(target)
    for raw in operations:
        if not isinstance(raw, dict):
            raise ApplyError("migration operations must be mappings")
        operation_id, kind, ownership = raw.get("id"), raw.get("kind"), raw.get("ownership")
        if not isinstance(operation_id, str) or not operation_id or operation_id in ids:
            raise ApplyError("migration operation IDs must be unique non-empty strings")
        ids.add(operation_id)
        if kind not in {"add", "replace", "remove", "rename", "reconcile"}:
            raise ApplyError(f"unsupported migration operation kind: {kind}")
        required_preconditions = {
            "add": {"destination_absent"},
            "replace": {"current_sha256_equals_previous_release"},
            "remove": {"current_sha256_equals_previous_release"},
            "rename": {"source_sha256_equals_previous_release", "destination_absent"},
            "reconcile": {"human_acknowledgement"},
        }[kind]
        preconditions = raw.get("preconditions")
        if not isinstance(preconditions, list) or set(preconditions) != required_preconditions:
            raise ApplyError(f"operation preconditions do not match {kind}: {operation_id}")
        path = safe_path(raw.get("path"), "migration path")
        from_path = safe_path(raw.get("from_path"), "migration from_path") if kind == "rename" else None
        for candidate in [path, from_path]:
            if candidate in {".dev/AI-CONTEXT-SOURCE.yaml", ".dev/AI-CONTEXT-APPLY-PENDING.yaml"}:
                raise ApplyError(f"migration cannot manage provenance or pending receipt: {candidate}")
            if candidate is not None:
                owner = touched_paths.get(candidate)
                if owner is not None:
                    raise ApplyError(f"migration path is touched by multiple operations: {candidate} ({owner}, {operation_id})")
                touched_paths[candidate] = operation_id
        if ownership == "target-template" and kind not in {"add", "reconcile"}:
            raise ApplyError(f"target-template operation is not allowed: {operation_id}")
        if ownership == "target-owned" and kind != "reconcile":
            raise ApplyError(f"target-owned operation is not allowed: {operation_id}")
        if ownership not in {"framework-managed", "target-template", "target-owned"}:
            raise ApplyError(f"invalid operation ownership: {operation_id}")
        operation_paths.extend([path] + ([from_path] if from_path else []))
        for candidate in [path, from_path]:
            if candidate is None:
                continue
            parts = PurePosixPath(candidate).parts
            for index in range(1, len(parts) + 1):
                prefix = PurePosixPath(*parts[:index]).as_posix()
                existing = case_map.get(prefix.casefold())
                if existing is not None and existing != prefix:
                    raise ApplyError(f"case-fold collision for operation path: {existing} and {prefix}")
        normalized.append({"id": operation_id, "kind": kind, "path": path, "from_path": from_path, "ownership": ownership})
    if [item["id"] for item in normalized] != sorted(item["id"] for item in normalized):
        raise ApplyError("migration operations must be ordered by ID")
    destination_paths = {item["path"] for item in normalized if item["kind"] in {"add", "replace", "rename", "reconcile"}}
    source_paths = {item["from_path"] for item in normalized if item["kind"] == "rename"}
    removal_paths = {item["path"] for item in normalized if item["kind"] in {"remove", "reconcile"}}
    for path, record in incoming.items():
        previous_record = previous.get(path)
        unchanged = previous_record is not None and all(
            previous_record.get(key) == record.get(key) for key in ("sha256", "mode", "ownership")
        )
        if not unchanged and path not in destination_paths:
            raise ApplyError(f"changed incoming path has no migration operation: {path}")
    for path, record in previous.items():
        if path in incoming:
            continue
        if path not in removal_paths and path not in source_paths:
            raise ApplyError(f"removed previous path has no migration operation: {path}")
    observed = observation(operation_paths, target)
    planned: list[dict] = []
    for item in normalized:
        operation_id, kind, path, source = item["id"], item["kind"], item["path"], item["from_path"]
        current = FileState(**observed[path])
        action, reason = kind, "all safety preconditions match"
        if kind == "add":
            if path not in incoming:
                raise ApplyError(f"add destination absent from incoming inventory: {path}")
            if incoming[path].get("ownership") != item["ownership"]:
                raise ApplyError(f"add ownership differs from incoming inventory: {path}")
            if current.exists:
                action, reason = "reconcile", "destination already exists"
        elif kind == "replace":
            if item["ownership"] != "framework-managed" or path not in incoming or path not in previous:
                raise ApplyError(f"replace requires managed incoming and previous records: {path}")
            if incoming[path].get("ownership") != "framework-managed" or previous[path].get("ownership") != "framework-managed":
                raise ApplyError(f"replace inventory ownership must be framework-managed: {path}")
            if not state_matches(current, previous[path]):
                action, reason = "reconcile", "current hash or mode differs from previous release"
        elif kind == "remove":
            if item["ownership"] != "framework-managed" or path not in previous:
                raise ApplyError(f"remove requires a previous managed record: {path}")
            if previous[path].get("ownership") != "framework-managed":
                raise ApplyError(f"remove previous ownership must be framework-managed: {path}")
            if not current.exists:
                action, reason = "noop", "path is already absent"
            elif not state_matches(current, previous[path]):
                action, reason = "reconcile", "current hash or mode differs from previous release"
        elif kind == "rename":
            if item["ownership"] != "framework-managed" or source not in previous or path not in incoming:
                raise ApplyError(f"rename requires previous source and incoming destination: {operation_id}")
            if previous[source].get("ownership") != "framework-managed" or incoming[path].get("ownership") != "framework-managed":
                raise ApplyError(f"rename inventory ownership must be framework-managed: {operation_id}")
            source_state = FileState(**observed[source])
            if not state_matches(source_state, previous[source]):
                action, reason = "reconcile", "rename source hash or mode differs from previous release"
            elif current.exists:
                action, reason = "reconcile", "rename destination already exists"
        else:
            action, reason = "reconcile", "migration explicitly requires reconciliation"
        planned.append({**item, "action": action, "reason": reason})
    return {
        "schema_version": "1.0.0",
        "package_id": package["package_id"],
        "package_version": package.get("version"),
        "package_manifest_sha256": manifest_sha,
        "package_root": str(package_root.resolve()),
        "target_root": str(target),
        "target_starting_commit": head,
        "previous_files": str(previous_files_path.resolve()) if previous_files_path else None,
        "observed": observed,
        "operations": planned,
    }


def mode_int(mode: str) -> int:
    return 0o755 if mode == "0755" else 0o644


def write_payload(package_root: Path, target: Path, path: str, record: dict) -> None:
    destination = target / Path(*PurePosixPath(path).parts)
    reject_symlink_boundary(target, path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = package_root / "payload" / Path(*PurePosixPath(path).parts)
    destination.write_bytes(source.read_bytes())
    os.chmod(destination, mode_int(record["mode"]))


def apply_plan(plan: dict, acknowledgements: set[str] | None = None) -> dict:
    acknowledgements = acknowledgements or set()
    target = Path(plan["target_root"])
    package_root = Path(plan["package_root"])
    package, incoming, migration, manifest_sha = validate_package_root(package_root)
    if manifest_sha != plan.get("package_manifest_sha256"):
        raise ApplyError("package manifest changed after planning")
    if clean_target_head(target) != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed after planning")
    current_observed = observation(plan.get("observed", {}).keys(), target)
    if current_observed != plan.get("observed"):
        raise ApplyError("target file state changed after planning")
    reconciles = {item["id"] for item in plan["operations"] if item["action"] == "reconcile"}
    unknown = acknowledgements - reconciles
    if unknown:
        raise ApplyError(f"acknowledgements do not match reconciliation IDs: {sorted(unknown)}")
    missing = reconciles - acknowledgements
    if missing:
        raise ApplyError(f"unacknowledged reconciliation items: {sorted(missing)}")
    receipt_relative = ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
    receipt_path = target / receipt_relative
    if receipt_path.exists() or receipt_path.is_symlink():
        raise ApplyError(f"pending receipt already exists: {receipt_relative}")
    active = [item for item in plan["operations"] if item["action"] in {"add", "replace", "remove", "rename"}]
    touched = {item["path"] for item in active}
    touched.update(item["from_path"] for item in active if item.get("from_path"))
    parent_candidates = {receipt_path.parent}
    for relative in touched:
        parent = (target / Path(*PurePosixPath(relative).parts)).parent
        while parent != target and parent.is_relative_to(target):
            parent_candidates.add(parent)
            parent = parent.parent
    existing_parents = {path for path in parent_candidates if path.exists()}
    snapshots: dict[str, tuple[bytes, int] | None] = {}
    for relative in touched:
        path = target / Path(*PurePosixPath(relative).parts)
        snapshots[relative] = (path.read_bytes(), path.stat().st_mode) if path.exists() else None
    try:
        for item in active:
            action, path = item["action"], item["path"]
            if action in {"add", "replace"}:
                write_payload(package_root, target, path, incoming[path])
            elif action == "remove":
                (target / Path(*PurePosixPath(path).parts)).unlink()
            elif action == "rename":
                source = target / Path(*PurePosixPath(item["from_path"]).parts)
                source.unlink()
                write_payload(package_root, target, path, incoming[path])
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt = {
            "schema_version": "1.0.0",
            "status": "pending-validation",
            "package_id": package["package_id"],
            "package_version": package.get("version"),
            "package_manifest_sha256": manifest_sha,
            "target_starting_commit": plan["target_starting_commit"],
            "applied_operation_ids": [item["id"] for item in active],
            "skipped_reconciliation_ids": sorted(reconciles),
            "provenance_updated": False,
        }
        receipt_path.write_text(yaml.safe_dump(receipt, sort_keys=False), encoding="utf-8", newline="\n")
    except Exception as exc:
        for relative, snapshot in snapshots.items():
            path = target / Path(*PurePosixPath(relative).parts)
            if snapshot is None:
                if path.exists() and path.is_file():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(snapshot[0])
                os.chmod(path, stat.S_IMODE(snapshot[1]))
        if receipt_path.exists() and receipt_path.is_file():
            receipt_path.unlink()
        for directory in sorted(parent_candidates - existing_parents, key=lambda item: len(item.parts), reverse=True):
            if directory.exists() and directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        raise ApplyError(f"package apply rolled back: {exc}") from exc
    return receipt
