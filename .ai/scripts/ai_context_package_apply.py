#!/usr/bin/env python3
"""Fail-closed planning and application for extracted AI context packages."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Iterator

import yaml

from ai_context_package_identity import (
    POLICY_ID as PUBLIC_PACKAGE_IDENTITY_POLICY,
    PackageIdentityError,
    expected_package_id,
    expected_rule,
)
from ai_context_package_validation import (
    PackageValidationError,
    validate_extracted_package,
)
from ai_context_target_provenance import (
    TargetValidationError,
    framework_managed_ignore_message,
    git_ignore_rule,
)


VERSION_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
COMPONENT_PACKAGE_SCHEMAS = {"2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0"}
IDENTITY_PACKAGE_SCHEMAS = {"1.1.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0"}
PORTABLE_VALIDATION_PACKAGE_SCHEMAS = {"2.3.0", "2.4.0"}


class ApplyError(ValueError):
    """A package application safety contract violation."""


DEFAULT_COMPONENT_SELECTION = {
    "release_model": "single-versioned-componentized-release",
    "mandatory_components": [
        "software-development-core",
        "ai-context-lifecycle-core",
    ],
    "profiles": ["dotnet-backend"],
    "providers": {
        "repo-backlog": {
            "enabled": False,
            "preservation": "preserve-existing-if-recorded",
        }
    },
}
LEGACY_COMPONENT_SELECTION = deepcopy(DEFAULT_COMPONENT_SELECTION)
LEGACY_COMPONENT_SELECTION["providers"]["repo-backlog"]["enabled"] = True
TARGET_EFFECTIVE_STATE_PATH = ".dev/ai-context/effective-rules.yaml"
TARGET_EFFECTIVE_PACKET_DIRECTORY = ".dev/ai-context/effective-rule-packets"
PENDING_RECEIPT_PATH = ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
APPLY_PLAN_SCHEMA_VERSION = "2.2.0"
PENDING_RECEIPT_SCHEMA_VERSION = "2.0.0"
JOURNAL_SCHEMA_VERSION = "ai-context-package-apply-journal/v5"
LEGACY_JOURNAL_SCHEMA_VERSION = "ai-context-package-apply-journal/v4"
JOURNAL_PROGRESS_SCHEMA_VERSION = "ai-context-package-apply-progress/v1"
JOURNAL_PROGRESS_PATH = "progress.jsonl"
JOURNAL_TERMINAL_STATES = frozenset({"finalized", "rolled-back", "rejected"})
UNSUPPORTED_JOURNAL_VERSION_CLASSIFICATION = "unsupported-transaction-journal-version"
MULTI_HOP_ROUTE_CONTEXT_KEY = "multi_hop_checkpoint_context"
MULTI_HOP_ROUTE_CONTEXT_SCHEMA_VERSION = "ai-context-multi-hop-checkpoint-context/v1"
MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION = "ai-context-multi-hop-initial-route-context/v1"
MULTI_HOP_ROUTE_INTENT_SCHEMA_VERSION = "ai-context-multi-hop-upgrade-intent/v1"
MULTI_HOP_ROUTE_JOURNAL_SCHEMA_VERSION = "ai-context-multi-hop-upgrade-journal/v1"
MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA_VERSION = "ai-context-multi-hop-upgrade-checkpoint/v1"
MULTI_HOP_ROUTE_DIRECTORY = "ai-context-multi-hop-upgrade"
UPGRADE_REMEDIATION_PACKET_SCHEMA_VERSION = "upgrade-remediation-packet/v1"
UPGRADE_REMEDIATION_DECISION_SCHEMA_VERSION = "upgrade-remediation-decision/v1"
INCOMING_VALIDATION_RECEIPT_SCHEMA_VERSION = "incoming-package-validation-receipt/v1"
TARGET_VALIDATION_RECEIPT_SCHEMA_VERSION = "target-validation-receipt/v1"
REMEDIATION_PACKET_PATH = "remediation-packet.json"
REMEDIATION_REPORT_PATH = "remediation-report.md"
REMEDIATION_DECISION_PATH = "remediation-decision.json"
INCOMING_VALIDATION_RECEIPT_PATH = "incoming-validation-receipt.json"
TARGET_VALIDATION_RECEIPT_PATH = "target-validation-receipt.json"
TARGET_VALIDATION_OUTPUT_PATH = "target-validation-output.log"
TARGET_VALIDATION_PROFILE_PATH = ".dev/project-config.yaml"
TRANSACTION_STATES = {
    "planned",
    "applying",
    "interrupted",
    "awaiting-target-validation",
    "validated",
    "rolling-back",
    "rolled-back",
    "rejected",
    "finalized",
}
WINDOWS_MOVEFILE_REPLACE_EXISTING = 0x1
WINDOWS_MOVEFILE_WRITE_THROUGH = 0x8
WINDOWS_ATOMIC_REPLACE_FLAGS = (
    WINDOWS_MOVEFILE_REPLACE_EXISTING | WINDOWS_MOVEFILE_WRITE_THROUGH
)


@dataclass(frozen=True)
class FileState:
    exists: bool
    sha256: str | None
    mode: str | None
    git_sha256: str | None = None
    normalized_text_sha256: str | None = None
    tracked: bool = False
    dirty: bool = False
    git_eol_only: bool = False


@dataclass
class JournalWriteStats:
    """Deterministic logical journal I/O counters for tests and diagnostics."""

    write_calls: int = 0
    bytes_written: int = 0
    snapshot_write_calls: int = 0
    append_write_calls: int = 0

    def observe(self, event: dict) -> None:
        self.write_calls += int(event["write_calls"])
        self.bytes_written += int(event["bytes_written"])
        if event["kind"] == "snapshot":
            self.snapshot_write_calls += int(event["write_calls"])
        elif event["kind"] == "append":
            self.append_write_calls += int(event["write_calls"])


@dataclass
class GitInspectionStats:
    """Deterministic counters for one target Git snapshot phase."""

    process_count: int = 0
    bytes_read: int = 0
    blob_read_count: int = 0
    snapshot_duration_ns: int = 0


@dataclass(frozen=True)
class WorktreeInventoryEntry:
    kind: str
    mode: int
    size: int
    modified_ns: int
    changed_ns: int


@dataclass
class TargetGitSnapshot:
    """One Git/index view plus an explicitly advanced worktree drift baseline."""

    root: Path
    phase: str
    head: str
    index_modes: dict[str, str]
    index_bytes: dict[str, bytes]
    dirty_paths: frozenset[str]
    attributes: dict[str, tuple[str, str, str]]
    ignore_rules: dict[str, dict[str, object]]
    ignore_paths: frozenset[str]
    core_filemode: bool
    transaction_base: Path
    multi_hop_route_base: Path
    git_identity_digests: dict[Path, str | None]
    git_identity_inventory: dict[Path, WorktreeInventoryEntry | None]
    worktree_inventory: dict[str, WorktreeInventoryEntry]
    stats: GitInspectionStats

    def tracked_mode(self, relative: str) -> str | None:
        raw_mode = self.index_modes.get(relative)
        if raw_mode is None:
            return None
        if raw_mode == "100644":
            return "0644"
        if raw_mode == "100755":
            return "0755"
        raise ApplyError(f"unsupported target Git mode {raw_mode} for {relative}")

    def tracked_bytes(self, relative: str) -> bytes | None:
        if relative not in self.index_modes:
            return None
        content = self.index_bytes.get(relative)
        if content is None:
            raise ApplyError(f"cannot read tracked Git bytes for {relative}")
        return content

    def path_is_dirty(self, relative: str, path: Path) -> bool:
        baseline = self.worktree_inventory.get(relative)
        current = worktree_inventory_entry(path)
        return relative in self.dirty_paths or current != baseline

    def no_content_transform(self, relative: str) -> bool:
        values = self.attributes.get(relative)
        if values is None:
            raise ApplyError(f"target Git attributes were not snapshotted for {relative}")
        return all(value == "unspecified" for value in values)

    def ignore_rule(self, relative: str) -> dict[str, object] | None:
        if relative not in self.ignore_paths:
            raise ApplyError(f"target Git ignore rule was not snapshotted for {relative}")
        return self.ignore_rules.get(relative)

    def changed_paths(self, *, full_worktree_scan: bool = True) -> set[str]:
        self.assert_identity(full=full_worktree_scan)
        changed = set(self.dirty_paths)
        if full_worktree_scan:
            current = worktree_inventory(self.root)
            candidates = set(self.worktree_inventory) | set(current)
        else:
            # Per-operation durability checks validate the exact operation and
            # journal states directly. Unrelated-path discovery belongs to the
            # bounded full scans at apply admission and terminal receipt
            # boundaries; rescanning every snapshotted path here would turn N
            # operations over N paths back into O(N^2) filesystem work.
            current = {}
            candidates = set()
        for relative in candidates:
            if self.worktree_inventory.get(relative) != current.get(relative):
                changed.add(relative)
        return changed

    def assert_identity(self, *, full: bool = False) -> None:
        for path, expected in self.git_identity_digests.items():
            if path.is_symlink() or is_reparse_point(path):
                raise ApplyError("target Git administrative identity became unsafe")
            if worktree_inventory_entry(path) != self.git_identity_inventory[path]:
                raise ApplyError(
                    "target Git administrative identity changed after snapshot capture"
                )
            if full:
                current = sha256_bytes(path.read_bytes()) if path.is_file() else None
                if current != expected:
                    raise ApplyError(
                        "target Git administrative identity changed after snapshot capture"
                    )

    def same_admission_identity(self, other: "TargetGitSnapshot") -> bool:
        return (
            self.root == other.root
            and self.head == other.head
            and self.index_modes == other.index_modes
            and self.dirty_paths == other.dirty_paths
            and self.core_filemode == other.core_filemode
            and self.transaction_base == other.transaction_base
            and self.multi_hop_route_base == other.multi_hop_route_base
            and self.git_identity_digests == other.git_identity_digests
            and self.worktree_inventory == other.worktree_inventory
        )

    def absorb_stats(self, earlier: "TargetGitSnapshot") -> None:
        self.stats.process_count += earlier.stats.process_count
        self.stats.bytes_read += earlier.stats.bytes_read
        self.stats.blob_read_count += earlier.stats.blob_read_count
        self.stats.snapshot_duration_ns += earlier.stats.snapshot_duration_ns

    def accept_verified_absence(self, paths: Iterable[str]) -> None:
        """Advance only after a journal-bound durable cleanup proved absence."""
        remaining_dirty = set(self.dirty_paths)
        for relative in paths:
            path = self.root / Path(*PurePosixPath(relative).parts)
            if worktree_inventory_entry(path) is not None:
                raise ApplyError(
                    f"verified cleanup path is still present: {relative}"
                )
            remaining_dirty.discard(relative)
            self.worktree_inventory.pop(relative, None)
        self.dirty_paths = frozenset(remaining_dirty)


_ACTIVE_TARGET_GIT_SNAPSHOT: ContextVar[TargetGitSnapshot | None] = ContextVar(
    "active_target_git_snapshot", default=None
)


class InjectedInterruption(BaseException):
    """Deterministic test-only process interruption that bypasses rollback."""


class NoAliasSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data: object) -> bool:
        return True


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def canonical_digest(value: object) -> str:
    content = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256_bytes(content)


def deterministic_yaml_bytes(value: object) -> bytes:
    return yaml.dump(
        value,
        Dumper=NoAliasSafeDumper,
        sort_keys=True,
        allow_unicode=True,
    ).encode("utf-8")


def normalized_text_digest(content: bytes) -> str | None:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return sha256_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def normalize_version(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ApplyError(f"{label} must be a stable semantic version")
    match = VERSION_RE.fullmatch(value)
    if match is None:
        raise ApplyError(f"{label} must be a stable semantic version")
    return ".".join(match.groups())


def safe_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ApplyError(f"{label} must be a non-empty POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ApplyError(f"unsafe {label}: {value!r}")
    return path.as_posix()


def safe_repo_reference(value: object) -> bool:
    """Match target finalization's repository-relative evidence contract."""
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    raw_path = value.split("#", 1)[0]
    path = PurePosixPath(raw_path)
    return (
        bool(raw_path)
        and ":" not in raw_path
        and all(raw_path.split("/"))
        and not path.is_absolute()
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def parse_iso_with_offset(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ):
        raise ApplyError(f"{label} must be ISO 8601 with offset")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApplyError(f"{label} is invalid") from exc
    if parsed.tzinfo is None:
        raise ApplyError(f"{label} must include an offset")
    return parsed


def is_target_effective_rule_path(path: str) -> bool:
    """Keep target-effective state and packets outside framework package control."""
    return (
        path in {TARGET_EFFECTIVE_STATE_PATH, TARGET_EFFECTIVE_PACKET_DIRECTORY}
        or path.startswith(f"{TARGET_EFFECTIVE_PACKET_DIRECTORY}/")
    )


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


def run_git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True
    )


def active_target_git_snapshot(root: Path) -> TargetGitSnapshot | None:
    snapshot = _ACTIVE_TARGET_GIT_SNAPSHOT.get()
    if snapshot is None:
        return None
    if snapshot.root != root.resolve():
        raise ApplyError("active target Git snapshot repository identity differs")
    return snapshot


@contextmanager
def target_git_snapshot_scope(snapshot: TargetGitSnapshot) -> Iterator[None]:
    token = _ACTIVE_TARGET_GIT_SNAPSHOT.set(snapshot)
    try:
        yield
    finally:
        _ACTIVE_TARGET_GIT_SNAPSHOT.reset(token)


def worktree_inventory_entry(path: Path) -> WorktreeInventoryEntry | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    kind = (
        "symlink"
        if path.is_symlink()
        else "reparse"
        if is_reparse_point(path)
        else "directory"
        if stat.S_ISDIR(info.st_mode)
        else "file"
        if stat.S_ISREG(info.st_mode)
        else "other"
    )
    return WorktreeInventoryEntry(
        kind=kind,
        mode=stat.S_IMODE(info.st_mode),
        size=info.st_size,
        modified_ns=info.st_mtime_ns,
        changed_ns=info.st_ctime_ns,
    )


def worktree_inventory(root: Path) -> dict[str, WorktreeInventoryEntry]:
    result: dict[str, WorktreeInventoryEntry] = {}
    for directory, names, files in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        if directory_path == root:
            names[:] = [name for name in names if name != ".git"]
            files = [name for name in files if name != ".git"]
        retained_names: list[str] = []
        for name in names:
            path = directory_path / name
            relative = path.relative_to(root).as_posix()
            entry = worktree_inventory_entry(path)
            if entry is None:
                continue
            if entry.kind in {"symlink", "reparse"}:
                result[relative] = entry
            else:
                retained_names.append(name)
        names[:] = retained_names
        for name in files:
            path = directory_path / name
            entry = worktree_inventory_entry(path)
            if entry is not None:
                result[path.relative_to(root).as_posix()] = entry
    return result


def _snapshot_git(
    root: Path,
    stats: GitInspectionStats,
    *args: str,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            input=input_bytes,
        )
    except OSError as exc:
        raise ApplyError(f"cannot capture target Git snapshot: {exc}") from exc
    stats.process_count += 1
    stats.bytes_read += len(result.stdout) + len(result.stderr)
    return result


def _decode_git_path(value: bytes) -> str:
    return value.decode("utf-8", errors="surrogateescape")


def _parse_index_entries(content: bytes) -> tuple[dict[str, str], dict[str, str]]:
    modes: dict[str, str] = {}
    object_ids: dict[str, str] = {}
    for record in content.split(b"\0"):
        if not record:
            continue
        header, separator, raw_path = record.partition(b"\t")
        parts = header.split(b" ")
        if not separator or len(parts) != 3:
            raise ApplyError("cannot parse target Git index snapshot")
        mode, object_id, stage = (
            part.decode("ascii", errors="strict") for part in parts
        )
        relative = _decode_git_path(raw_path)
        if stage != "0" or relative in modes:
            raise ApplyError(f"target Git index has unresolved stages for {relative}")
        if not re.fullmatch(r"[0-9a-f]{40,64}", object_id):
            raise ApplyError(f"target Git index object identity is invalid for {relative}")
        modes[relative] = mode
        object_ids[relative] = object_id
    return modes, object_ids


def _parse_status_paths(content: bytes) -> frozenset[str]:
    records = content.split(b"\0")
    if records and records[-1] == b"":
        records.pop()
    changed: set[str] = set()
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 4 or record[2:3] != b" ":
            raise ApplyError("cannot parse target Git status snapshot")
        status = record[:2]
        changed.add(_decode_git_path(record[3:]))
        if b"R" in status or b"C" in status:
            index += 1
            if index >= len(records) or not records[index]:
                raise ApplyError("cannot parse target Git rename status snapshot")
            changed.add(_decode_git_path(records[index]))
        index += 1
    return frozenset(changed)


def _parse_batch_blobs(
    content: bytes, object_ids: Iterable[str]
) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    offset = 0
    for expected in object_ids:
        newline = content.find(b"\n", offset)
        if newline < 0:
            raise ApplyError("cannot parse target Git blob snapshot")
        header = content[offset:newline].split(b" ")
        if len(header) != 3:
            raise ApplyError("cannot parse target Git blob snapshot")
        object_id = header[0].decode("ascii", errors="strict")
        object_type = header[1].decode("ascii", errors="strict")
        try:
            size = int(header[2])
        except ValueError as exc:
            raise ApplyError("cannot parse target Git blob size") from exc
        if object_id != expected or object_type != "blob" or size < 0:
            raise ApplyError(f"target Git object is not one blob: {expected}")
        start = newline + 1
        end = start + size
        if end >= len(content) or content[end : end + 1] != b"\n":
            raise ApplyError("cannot parse target Git blob bytes")
        result[object_id] = content[start:end]
        offset = end + 1
    if content[offset:]:
        raise ApplyError("target Git blob snapshot has trailing bytes")
    return result


def _parse_attributes(
    content: bytes, expected_paths: set[str]
) -> dict[str, tuple[str, str, str]]:
    values = content.split(b"\0")
    if values and values[-1] == b"":
        values.pop()
    if len(values) != len(expected_paths) * 9:
        raise ApplyError("cannot parse target Git attributes snapshot")
    by_path: dict[str, dict[str, str]] = {}
    for index in range(0, len(values), 3):
        relative = _decode_git_path(values[index])
        attribute = values[index + 1].decode("utf-8", errors="strict")
        value = values[index + 2].decode("utf-8", errors="surrogateescape")
        if relative not in expected_paths or attribute in by_path.setdefault(relative, {}):
            raise ApplyError("cannot parse target Git attributes snapshot")
        by_path[relative][attribute] = value
    expected_attributes = ("filter", "ident", "working-tree-encoding")
    result: dict[str, tuple[str, str, str]] = {}
    for relative in expected_paths:
        attributes = by_path.get(relative)
        if attributes is None or set(attributes) != set(expected_attributes):
            raise ApplyError(f"cannot parse target Git attributes for {relative}")
        result[relative] = tuple(attributes[name] for name in expected_attributes)
    return result


def _parse_ignore_rules(
    content: bytes, expected_paths: set[str]
) -> dict[str, dict[str, object]]:
    values = content.split(b"\0")
    if values and values[-1] == b"":
        values.pop()
    if len(values) % 4 != 0:
        raise ApplyError("cannot parse target Git ignore snapshot")
    result: dict[str, dict[str, object]] = {}
    for index in range(0, len(values), 4):
        source, line, pattern, matched_path = (
            _decode_git_path(value) for value in values[index : index + 4]
        )
        if (
            matched_path not in expected_paths
            or matched_path in result
            or not line.isdecimal()
            or not source
            or not pattern
        ):
            raise ApplyError("cannot parse target Git ignore snapshot")
        result[matched_path] = {
            "source": source,
            "line": int(line),
            "pattern": pattern,
        }
    return result


def _parse_core_snapshot_config(
    content: bytes, root: Path,
) -> tuple[bool, str | None, str | None, set[Path], set[Path]]:
    """Parse one effective config batch and retain its file-backed origins."""
    values = content.split(b"\0")
    if values and values[-1] == b"":
        values.pop()
    if len(values) % 2 != 0:
        raise ApplyError("cannot parse target Git core configuration")
    effective: dict[str, str] = {}
    origins: set[Path] = set()
    include_paths: set[Path] = set()
    for index in range(0, len(values), 2):
        origin = values[index].decode("utf-8", errors="surrogateescape")
        try:
            raw_key, raw_value = values[index + 1].split(b"\n", 1)
        except ValueError as exc:
            raise ApplyError("cannot parse target Git core configuration") from exc
        key = raw_key.decode("ascii", errors="strict").lower()
        value = raw_value.decode("utf-8", errors="surrogateescape")
        if key in {"core.filemode", "core.excludesfile", "core.attributesfile"}:
            effective[key] = value
        if origin.startswith("file:"):
            raw_origin_path = Path(origin.removeprefix("file:"))
            origin_path = Path(
                os.path.abspath(
                    raw_origin_path
                    if raw_origin_path.is_absolute()
                    else root / raw_origin_path
                )
            )
            origins.add(origin_path)
            if key == "include.path" or (
                key.startswith("includeif.") and key.endswith(".path")
            ):
                include_paths.add(_resolved_git_include_path(origin_path, value))
    filemode = effective.get("core.filemode", "").lower()
    if filemode not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        filemode == "true",
        effective.get("core.excludesfile"),
        effective.get("core.attributesfile"),
        origins,
        include_paths,
    )


def _git_home_path() -> Path:
    """Resolve the home directory Git uses for config and policy paths."""
    home_override = os.environ.get("HOME")
    if home_override is None:
        candidate = Path.home()
    else:
        if not home_override:
            raise ApplyError("cannot resolve target Git home directory")
        candidate = Path(home_override)
    if not candidate.is_absolute():
        raise ApplyError("cannot resolve target Git home directory")
    return Path(os.path.abspath(candidate))


def _expand_git_user_path(value: str) -> Path:
    if value == "~":
        return _git_home_path()
    if value.startswith("~/") or value.startswith("~\\"):
        return _git_home_path() / value[2:]
    if value.startswith("~"):
        raise ApplyError("cannot resolve target Git user-relative path")
    return Path(value)


def _resolved_git_include_path(origin: Path, value: str) -> Path:
    if not value or value.startswith("%(prefix)/"):
        raise ApplyError("cannot resolve target Git include policy path")
    expanded = _expand_git_user_path(value)
    candidate = expanded if expanded.is_absolute() else origin.parent / expanded
    return Path(os.path.abspath(candidate))


def _resolved_git_policy_path(root: Path, value: str | None, name: str) -> Path:
    if value is None:
        xdg_root = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg_root) if xdg_root else _git_home_path() / ".config"
        candidate = base if base.is_absolute() else root / base
        return Path(os.path.abspath(candidate / "git" / name))
    if not value or value.startswith("%(prefix)/"):
        raise ApplyError(f"cannot resolve target Git {name} policy path")
    expanded = _expand_git_user_path(value)
    candidate = expanded if expanded.is_absolute() else root / expanded
    return Path(os.path.abspath(candidate))


def _candidate_git_config_paths(root: Path) -> set[Path]:
    """Bind absent/present config selectors whose paths are process-stable."""
    candidates: set[Path] = set()

    def add(value: str) -> None:
        if not value or value == os.devnull:
            return
        # Raw selector values remain literal on both platforms. Windows path
        # handling normalizes embedded parent segments before access; POSIX
        # access preserves them and can remain blocked by a missing lexical
        # parent. Keep that POSIX boundary so its later creation changes the
        # selector identity instead of silently rebinding another path.
        selected = Path(value)
        candidate = selected if selected.is_absolute() else root / selected
        candidates.add(
            Path(os.path.abspath(candidate)) if os.name == "nt" else candidate
        )

    global_override = os.environ.get("GIT_CONFIG_GLOBAL")
    if global_override is not None:
        add(global_override)
    else:
        git_home = _git_home_path()
        add(str(git_home / ".gitconfig"))
        xdg_root = os.environ.get("XDG_CONFIG_HOME")
        if xdg_root:
            add(str(Path(xdg_root) / "git" / "config"))
        else:
            add(str(git_home / ".config" / "git" / "config"))

    if not os.environ.get("GIT_CONFIG_NOSYSTEM"):
        system_override = os.environ.get("GIT_CONFIG_SYSTEM")
        if system_override is not None:
            add(system_override)
        elif os.name != "nt":
            add("/etc/gitconfig")
    return candidates


def capture_target_git_snapshot(
    root: Path,
    paths: Iterable[str],
    *,
    phase: str,
    require_clean: bool,
) -> TargetGitSnapshot:
    started = time.perf_counter_ns()
    root = root.resolve()
    if not (root / ".git").exists():
        raise ApplyError("target must be a Git repository")
    requested_paths = sorted(set(paths), key=lambda item: item.encode("utf-8"))
    # Reject filesystem escape boundaries before asking Git to interpret the
    # pathspecs. On POSIX, check-ignore/check-attr reject a path below a
    # symlink themselves, but their lower-level error would otherwise obscure
    # the package-apply safety contract and make the result platform-specific.
    for relative in requested_paths:
        reject_symlink_boundary(root, relative)
    stats = GitInspectionStats()
    head_result = _snapshot_git(root, stats, "rev-parse", "--verify", "HEAD^{commit}")
    head = head_result.stdout.decode("ascii", errors="replace").strip()
    if head_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40,64}", head):
        raise ApplyError("target must have a committed HEAD before planning or apply")
    index_result = _snapshot_git(root, stats, "ls-files", "--stage", "-z")
    if index_result.returncode != 0:
        raise ApplyError("cannot inspect target Git index")
    index_modes, object_ids = _parse_index_entries(index_result.stdout)
    status_result = _snapshot_git(
        root, stats, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    )
    if status_result.returncode != 0:
        raise ApplyError("cannot inspect target Git status")
    dirty_paths = _parse_status_paths(status_result.stdout)
    if require_clean and dirty_paths:
        raise ApplyError("target Git worktree must be clean before planning or apply")
    # A multi-hop checkpoint surface is defined by every changed path from the
    # status snapshot. Include those paths in the same batch so its verifier
    # never falls back to one Git process group per checkpoint path.
    requested_paths = sorted(
        set(requested_paths) | set(dirty_paths),
        key=lambda item: item.encode("utf-8"),
    )
    selected_object_ids = {
        path: object_ids[path] for path in requested_paths if path in object_ids
    }
    unique_object_ids = list(dict.fromkeys(selected_object_ids.values()))
    blob_result = _snapshot_git(
        root,
        stats,
        "cat-file",
        "--batch",
        input_bytes=("".join(f"{value}\n" for value in unique_object_ids)).encode("ascii"),
    )
    if blob_result.returncode != 0:
        raise ApplyError("cannot read target Git index blobs")
    blobs = _parse_batch_blobs(blob_result.stdout, unique_object_ids)
    stats.blob_read_count = len(unique_object_ids)
    index_bytes = {
        path: blobs[object_id] for path, object_id in selected_object_ids.items()
    }
    config_result = _snapshot_git(
        root,
        stats,
        "config",
        "--null",
        "--show-origin",
        "--list",
    )
    if config_result.returncode != 0:
        raise ApplyError("cannot inspect target Git core configuration")
    (
        core_filemode,
        excludes_value,
        attributes_value,
        config_origins,
        config_include_paths,
    ) = (
        _parse_core_snapshot_config(config_result.stdout, root)
    )
    admin_result = _snapshot_git(
        root,
        stats,
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        "ai-context-package-apply",
        "--git-path",
        MULTI_HOP_ROUTE_DIRECTORY,
        "--git-path",
        "HEAD",
        "--git-path",
        "index",
        "--git-path",
        "packed-refs",
        "--git-path",
        "config",
        "--git-path",
        "config.worktree",
        "--git-path",
        "info/attributes",
        "--git-path",
        "info/exclude",
    )
    admin_paths = [
        Path(line.decode("utf-8", errors="surrogateescape"))
        for line in admin_result.stdout.splitlines()
        if line
    ]
    if admin_result.returncode != 0 or len(admin_paths) != 9:
        raise ApplyError("cannot resolve target Git administrative directories")
    identity_paths = admin_paths[2:]
    identity_paths.extend(sorted(config_origins, key=str))
    identity_paths.extend(sorted(config_include_paths, key=str))
    identity_paths.extend(sorted(_candidate_git_config_paths(root), key=str))
    identity_paths.extend(
        [
            _resolved_git_policy_path(root, excludes_value, "ignore"),
            _resolved_git_policy_path(root, attributes_value, "attributes"),
        ]
    )
    identity_paths = list(dict.fromkeys(identity_paths))
    head_file = identity_paths[0]
    if head_file.is_symlink() or is_reparse_point(head_file) or not head_file.is_file():
        raise ApplyError("target Git HEAD identity is unsafe")
    head_file_bytes = head_file.read_bytes()
    if head_file_bytes.startswith(b"ref: "):
        reference = head_file_bytes[5:].strip().decode("utf-8", errors="strict")
        if not reference.startswith("refs/") or ".." in PurePosixPath(reference).parts:
            raise ApplyError("target Git HEAD reference is invalid")
        reference_result = _snapshot_git(
            root,
            stats,
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            reference,
        )
        if reference_result.returncode != 0:
            raise ApplyError("cannot resolve target Git HEAD reference")
        reference_path = Path(
            reference_result.stdout.decode("utf-8", errors="surrogateescape").strip()
        )
        identity_paths.append(reference_path)
    git_identity_digests: dict[Path, str | None] = {}
    git_identity_inventory: dict[Path, WorktreeInventoryEntry | None] = {}
    for path in identity_paths:
        if path.is_symlink() or is_reparse_point(path):
            raise ApplyError("target Git administrative identity is unsafe")
        git_identity_digests[path] = (
            sha256_bytes(path.read_bytes()) if path.is_file() else None
        )
        git_identity_inventory[path] = worktree_inventory_entry(path)
    attribute_paths = set(requested_paths)
    attr_result = _snapshot_git(
        root,
        stats,
        "check-attr",
        "-z",
        "--stdin",
        "filter",
        "ident",
        "working-tree-encoding",
        input_bytes=b"".join(
            path.encode("utf-8", errors="surrogateescape") + b"\0"
            for path in sorted(
                attribute_paths,
                key=lambda item: item.encode("utf-8", errors="surrogateescape"),
            )
        ),
    )
    if attr_result.returncode != 0:
        raise ApplyError("cannot inspect target Git attributes")
    attributes = _parse_attributes(attr_result.stdout, attribute_paths)
    ignore_input = b"".join(
        path.encode("utf-8", errors="surrogateescape") + b"\0"
        for path in requested_paths
    )
    ignore_result = _snapshot_git(
        root,
        stats,
        "check-ignore",
        "-z",
        "-v",
        "--stdin",
        input_bytes=ignore_input,
    )
    if ignore_result.returncode not in {0, 1}:
        detail = ignore_result.stderr.decode("utf-8", errors="replace").strip()
        raise ApplyError(
            f"cannot inspect target Git ignore rules: {detail or ignore_result.returncode}"
        )
    ignore_rules = _parse_ignore_rules(ignore_result.stdout, set(requested_paths))
    inventory = worktree_inventory(root)
    final_config_result = _snapshot_git(
        root,
        stats,
        "config",
        "--null",
        "--show-origin",
        "--list",
    )
    if (
        final_config_result.returncode != 0
        or final_config_result.stdout != config_result.stdout
    ):
        raise ApplyError("target Git configuration changed while snapshot was captured")
    final_head_result = _snapshot_git(root, stats, "rev-parse", "--verify", "HEAD^{commit}")
    final_status_result = _snapshot_git(
        root, stats, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    )
    if (
        final_head_result.returncode != 0
        or final_head_result.stdout != head_result.stdout
        or final_status_result.returncode != 0
        or final_status_result.stdout != status_result.stdout
    ):
        raise ApplyError("target Git state changed while snapshot was captured")
    for path in identity_paths:
        if path.is_symlink() or is_reparse_point(path):
            raise ApplyError("target Git administrative identity is unsafe")
        current_digest = sha256_bytes(path.read_bytes()) if path.is_file() else None
        if current_digest != git_identity_digests[path]:
            raise ApplyError("target Git identity changed while snapshot was captured")
        # Read-only Git commands may refresh index metadata without changing
        # its bytes. Bind the final metadata only after exact bytes survived
        # the closing HEAD/status check.
        git_identity_inventory[path] = worktree_inventory_entry(path)
    stats.snapshot_duration_ns = time.perf_counter_ns() - started
    return TargetGitSnapshot(
        root=root,
        phase=phase,
        head=head,
        index_modes=index_modes,
        index_bytes=index_bytes,
        dirty_paths=dirty_paths,
        attributes=attributes,
        ignore_rules=ignore_rules,
        ignore_paths=frozenset(requested_paths),
        core_filemode=core_filemode,
        transaction_base=admin_paths[0],
        multi_hop_route_base=admin_paths[1],
        git_identity_digests=git_identity_digests,
        git_identity_inventory=git_identity_inventory,
        worktree_inventory=inventory,
        stats=stats,
    )


def emit_git_inspection_metrics(
    snapshot: TargetGitSnapshot,
    hook: Callable[[dict], None] | None,
    *,
    phase_duration_ns: int,
    outcome: str,
) -> None:
    if hook is None:
        return
    hook(
        {
            "schema_version": "target-git-inspection/v1",
            "phase": snapshot.phase,
            "outcome": outcome,
            "path_count": len(snapshot.ignore_paths),
            "tracked_path_count": len(snapshot.index_modes),
            "git_process_count": snapshot.stats.process_count,
            "git_bytes_read": snapshot.stats.bytes_read,
            "git_blob_read_count": snapshot.stats.blob_read_count,
            "snapshot_duration_ns": snapshot.stats.snapshot_duration_ns,
            "phase_duration_ns": phase_duration_ns,
        }
    )


def target_git_semantic_identity(
    snapshot: TargetGitSnapshot, paths: Iterable[str]
) -> dict:
    attributes: dict[str, list[str]] = {}
    ignore_rules: dict[str, dict[str, object] | None] = {}
    for relative in sorted(set(paths), key=lambda item: item.encode("utf-8")):
        values = snapshot.attributes.get(relative)
        if values is None:
            raise ApplyError(
                f"target Git attributes were not snapshotted for {relative}"
            )
        attributes[relative] = list(values)
        ignore_rules[relative] = deepcopy(snapshot.ignore_rule(relative))
    return {
        "core_filemode": snapshot.core_filemode,
        "attributes": attributes,
        "ignore_rules": ignore_rules,
    }


def verify_planned_target_git_semantics(target: Path, plan: dict) -> None:
    planned = plan.get("target_git_semantics")
    if planned is None:
        # Journal-v5 transactions created before target Git semantic binding
        # retain their historical recovery contract.
        return
    snapshot = active_target_git_snapshot(target)
    if snapshot is None:
        raise ApplyError("target Git semantic verification requires one active snapshot")
    observed = plan.get("observed")
    if not isinstance(planned, dict) or not isinstance(observed, dict):
        raise ApplyError("planned target Git semantic identity is invalid")
    if target_git_semantic_identity(snapshot, observed.keys()) != planned:
        raise ApplyError(
            "target Git attributes, ignore rules, or core.filemode changed after planning"
        )


def clean_target_head(root: Path) -> str:
    snapshot = active_target_git_snapshot(root)
    if snapshot is not None:
        if snapshot.dirty_paths:
            raise ApplyError("target Git worktree must be clean before planning or apply")
        return snapshot.head
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


def target_git_head(root: Path) -> str:
    snapshot = active_target_git_snapshot(root)
    if snapshot is not None:
        snapshot.assert_identity()
        return snapshot.head
    result = run_git(root, "rev-parse", "--verify", "HEAD^{commit}")
    head = result.stdout.strip() if result.returncode == 0 else ""
    if not re.fullmatch(r"[0-9a-f]{40,64}", head):
        raise ApplyError("cannot determine target Git HEAD")
    return head


def tracked_mode(root: Path, relative: str) -> str | None:
    snapshot = active_target_git_snapshot(root)
    if snapshot is not None:
        return snapshot.tracked_mode(relative)
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


def tracked_bytes(root: Path, relative: str) -> bytes | None:
    snapshot = active_target_git_snapshot(root)
    if snapshot is not None:
        return snapshot.tracked_bytes(relative)
    if tracked_mode(root, relative) is None:
        return None
    result = run_git_bytes(root, "show", f":{relative}")
    if result.returncode != 0:
        raise ApplyError(f"cannot read tracked Git bytes for {relative}")
    return result.stdout


def path_is_dirty(root: Path, relative: str) -> bool:
    snapshot = active_target_git_snapshot(root)
    if snapshot is not None:
        path = root / Path(*PurePosixPath(relative).parts)
        return snapshot.path_is_dirty(relative, path)
    result = run_git(root, "status", "--porcelain", "--untracked-files=all", "--", relative)
    if result.returncode != 0:
        raise ApplyError(f"cannot inspect target Git state for {relative}")
    return bool(result.stdout)


def has_no_git_content_transform(root: Path, relative: str) -> bool:
    snapshot = active_target_git_snapshot(root)
    if snapshot is not None:
        return snapshot.no_content_transform(relative)
    result = run_git(
        root,
        "check-attr",
        "filter",
        "ident",
        "working-tree-encoding",
        "--",
        relative,
    )
    if result.returncode != 0:
        raise ApplyError(f"cannot inspect target Git attributes for {relative}")
    values = []
    for line in result.stdout.splitlines():
        parts = line.rsplit(": ", 1)
        if len(parts) != 2:
            raise ApplyError(f"cannot parse target Git attributes for {relative}")
        values.append(parts[1])
    return len(values) == 3 and all(value == "unspecified" for value in values)


def filesystem_mode(path: Path) -> str:
    return "0755" if path.stat().st_mode & stat.S_IXUSR else "0644"


def is_reparse_point(path: Path) -> bool:
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, FileNotFoundError):
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def file_state(
    root: Path,
    relative: str,
    snapshot: TargetGitSnapshot | None = None,
) -> FileState:
    path = root / Path(*PurePosixPath(relative).parts)
    if not path.exists():
        return FileState(False, None, None)
    if path.is_symlink() or is_reparse_point(path) or not path.is_file():
        raise ApplyError(f"target path must be a regular file: {relative}")
    content = path.read_bytes()
    snapshot = snapshot or active_target_git_snapshot(root)
    tracked_git_mode = (
        snapshot.tracked_mode(relative)
        if snapshot is not None
        else tracked_mode(root, relative)
    )
    tracked = tracked_git_mode is not None
    dirty = (
        snapshot.path_is_dirty(relative, path)
        if snapshot is not None
        else path_is_dirty(root, relative)
    )
    index_content = (
        snapshot.tracked_bytes(relative)
        if snapshot is not None and tracked
        else tracked_bytes(root, relative)
        if tracked
        else None
    )
    return FileState(
        True,
        sha256_bytes(content),
        tracked_git_mode if tracked and not dirty else filesystem_mode(path),
        sha256_bytes(index_content) if index_content is not None else None,
        normalized_text_digest(content),
        tracked,
        dirty,
        index_content is not None
        and content != index_content
        and content.replace(b"\r\n", b"\n") == index_content,
    )


def state_record(state: FileState) -> dict:
    return {
        "exists": state.exists,
        "sha256": state.sha256,
        "mode": state.mode,
        "git_sha256": state.git_sha256,
        "normalized_text_sha256": state.normalized_text_sha256,
        "tracked": state.tracked,
        "dirty": state.dirty,
        "git_eol_only": state.git_eol_only,
    }


def reject_symlink_boundary(root: Path, relative: str) -> None:
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink() or is_reparse_point(current):
            raise ApplyError(f"symlink boundary or reparse-point boundary is not allowed: {relative}")


def canonical_json_bytes(value: object) -> bytes:
    """Return the one portable byte representation for sealed JSON evidence."""
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def require_sha256(value: object, label: str, *, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ApplyError(f"{label} must be a lowercase SHA-256")
    return value


def is_upgrade_plan(plan: dict) -> bool:
    return plan.get("upgrade_remediation_required") is True


def target_file_identity(target: Path, relative: str) -> dict:
    relative = safe_path(relative, "target authority path")
    reject_symlink_boundary(target, relative)
    path = target / Path(*PurePosixPath(relative).parts)
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError(f"target authority path is unsafe: {relative}")
    if not path.exists():
        return {"path": relative, "sha256": None}
    if not path.is_file():
        raise ApplyError(f"target authority path must be a regular file: {relative}")
    return {"path": relative, "sha256": sha256_bytes(path.read_bytes())}


def target_provenance_source(target: Path) -> dict | None:
    """Capture the exact predecessor source identity for prospective upgrades."""
    relative = ".dev/ai-context/provenance.yaml"
    identity = target_file_identity(target, relative)
    if identity["sha256"] is None:
        return None
    document = load_yaml(
        target / Path(*PurePosixPath(relative).parts), "target provenance"
    )
    source = document.get("source")
    if not isinstance(source, dict):
        raise ApplyError("target provenance source identity is invalid")
    return deepcopy(source)


def target_validation_profile(target: Path) -> dict:
    """Capture target-owned routine policy without inferring a command from it."""
    identity = target_file_identity(target, TARGET_VALIDATION_PROFILE_PATH)
    if identity["sha256"] is None:
        return {
            **identity,
            "argv": [],
            "snapshot": {"status": "absent"},
        }
    path = target / Path(*PurePosixPath(TARGET_VALIDATION_PROFILE_PATH).parts)
    document = load_yaml(path, "target validation profile")
    validation = document.get("validation")
    routine = validation.get("routine") if isinstance(validation, dict) else None
    argv = routine.get("argv") if isinstance(routine, dict) else None
    if argv is None:
        argv = []
    if not isinstance(argv, list) or not all(
        isinstance(item, str) and item for item in argv
    ):
        raise ApplyError("target validation routine argv must be a string list")
    return {
        **identity,
        "argv": argv,
        "snapshot": deepcopy(routine) if isinstance(routine, dict) else {"status": "absent"},
    }


def incoming_package_validation(package_root: Path, package: dict) -> dict:
    """Execute only the validator embedded in a portable incoming package."""
    if package.get("schema_version") not in PORTABLE_VALIDATION_PACKAGE_SCHEMAS:
        return {
            "applicable": False,
            "schema_version": None,
            "manifest_path": None,
            "manifest_sha256": None,
            "authority": "not-applicable",
            "path": None,
            "sha256": None,
            "argv": [],
            "execution": {
                "outcome": "not-applicable",
                "exit_code": None,
                "output_sha256": None,
            },
        }
    # The portable structural validator checks canonical metadata, checksum
    # coverage, and that this identity points at an incoming-candidate payload.
    try:
        validate_extracted_package(package_root, run_portable_entrypoints=False)
    except PackageValidationError as exc:
        raise ApplyError(f"portable package validation failed: {exc}") from exc
    manifest_path = package_root / "metadata" / "validation.json"
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyError("cannot read incoming package validation metadata") from exc
    if not isinstance(manifest, dict):
        raise ApplyError("incoming package validation metadata must be a mapping")
    authority = manifest.get("authority")
    if not isinstance(authority, dict) or authority.get("kind") != "incoming-candidate":
        raise ApplyError("incoming package validator authority is invalid")
    validator = authority.get("validator")
    if not isinstance(validator, dict) or set(validator) != {"path", "sha256", "argv"}:
        raise ApplyError("incoming package validator identity is incomplete")
    validator_path = safe_path(validator.get("path"), "incoming package validator path")
    validator_sha = require_sha256(validator.get("sha256"), "incoming package validator SHA-256")
    argv = validator.get("argv")
    if not isinstance(argv, list) or not all(isinstance(item, str) and item for item in argv):
        raise ApplyError("incoming package validator argv is invalid")
    expected_argv = ["python", f"payload/{validator_path}", "--package-root", "."]
    if argv != expected_argv:
        raise ApplyError("incoming package validator argv is not deterministic")
    validator_file = package_root / Path(*PurePosixPath(f"payload/{validator_path}").parts)
    if not validator_file.is_file() or validator_file.is_symlink():
        raise ApplyError("incoming package validator payload is missing")
    if sha256_bytes(validator_file.read_bytes()) != validator_sha:
        raise ApplyError("incoming package validator payload identity differs")
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    command = [sys.executable, *argv[1:]]
    try:
        result = subprocess.run(
            command,
            cwd=package_root,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
    except OSError as exc:
        raise ApplyError("incoming package validator could not start") from exc
    except subprocess.TimeoutExpired as exc:
        raise ApplyError("incoming package validator timed out") from exc
    output_digest = sha256_bytes(
        (result.stdout + "\0" + result.stderr).encode("utf-8")
    )
    if result.returncode != 0:
        raise ApplyError(
            "incoming package validator failed: "
            f"exit={result.returncode}; output_sha256={output_digest}"
        )
    return {
        "applicable": True,
        "schema_version": manifest.get("schema_version"),
        "manifest_path": "metadata/validation.json",
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "authority": "incoming-candidate",
        "path": validator_path,
        "sha256": validator_sha,
        "argv": argv,
        "execution": {
            "outcome": "passed",
            "exit_code": 0,
            "output_sha256": output_digest,
        },
    }


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
    schema_version = document.get("schema_version")
    if schema_version not in {"1.0.0", "2.0.0"}:
        raise ApplyError(f"{label} uses unsupported files schema: {schema_version!r}")
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
        if schema_version == "2.0.0" and (
            not isinstance(raw.get("component_id"), str)
            or not raw["component_id"]
        ):
            raise ApplyError(f"missing {label} component_id: {path}")
        output[path] = raw
        order.append(path)
    if order != sorted(order, key=lambda item: item.encode("utf-8")):
        raise ApplyError(f"{label} paths must use UTF-8 bytewise order")
    return output, order


def validate_component_selection(selection: object, label: str) -> dict:
    if not isinstance(selection, dict):
        raise ApplyError(f"{label} must be a mapping")
    if selection.get("release_model") != "single-versioned-componentized-release":
        raise ApplyError(f"{label}.release_model is invalid")
    mandatory = selection.get("mandatory_components")
    if not isinstance(mandatory, list) or set(mandatory) != {
        "software-development-core",
        "ai-context-lifecycle-core",
    }:
        raise ApplyError(f"{label} must include both mandatory cores")
    if selection.get("profiles") != ["dotnet-backend"]:
        raise ApplyError(f"{label}.profiles must select dotnet-backend")
    providers = selection.get("providers")
    backlog = providers.get("repo-backlog") if isinstance(providers, dict) else None
    if (
        not isinstance(backlog, dict)
        or not isinstance(backlog.get("enabled"), bool)
        or backlog.get("preservation") != "preserve-existing-if-recorded"
        or set(backlog) != {"enabled", "preservation"}
    ):
        raise ApplyError(f"{label}.repo-backlog contract is invalid")
    return selection


def enabled_components(selection: dict) -> set[str]:
    selected = set(selection["mandatory_components"])
    selected.update(selection["profiles"])
    if selection["providers"]["repo-backlog"]["enabled"]:
        selected.add("repo-backlog")
    return selected


def inferred_component(path: str, record: dict | None = None) -> str:
    if isinstance(record, dict):
        component = record.get("component_id")
        if isinstance(component, str) and component:
            return component
        if record.get("entry_id") == "dotnet-validation-tools":
            return "dotnet-backend"
        if record.get("entry_id") in {
            "ai-entry-documents",
            "assessment-governance",
            "public-root-and-catalog-seeds",
        }:
            return "ai-context-lifecycle-core"
    if path.startswith(".dev/backlog/"):
        return "repo-backlog"
    return "software-development-core"


def inventory_schema(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(load_yaml(path, "previous files.yaml").get("schema_version"))


def resolve_effective_selection(
    package: dict,
    target: Path,
    previous_files_path: Path | None,
    enable_providers: Iterable[str] | None,
) -> tuple[dict, dict]:
    requested = sorted(set(enable_providers or []))
    unsupported = [provider for provider in requested if provider != "repo-backlog"]
    if unsupported:
        raise ApplyError(f"unsupported provider selection: {unsupported}")

    new_provenance = target / ".dev/ai-context/provenance.yaml"
    legacy_provenance = target / ".dev/AI-CONTEXT-SOURCE.yaml"
    if new_provenance.is_file() and legacy_provenance.is_file():
        raise ApplyError(
            "legacy and component-aware provenance authorities cannot coexist"
        )

    package_schema = package.get("schema_version")
    default = (
        validate_component_selection(package.get("selection"), "package selection")
        if package_schema in COMPONENT_PACKAGE_SCHEMAS
        else deepcopy(LEGACY_COMPONENT_SELECTION)
    )
    resolved = deepcopy(default)
    if previous_files_path is None:
        if "repo-backlog" in requested:
            resolved["providers"]["repo-backlog"]["enabled"] = True
        return resolved, {
            "source": (
                "explicit-cli-provider"
                if requested
                else (
                    "clean-install-default"
                    if package_schema in COMPONENT_PACKAGE_SCHEMAS
                    else "legacy-package-contract"
                )
            ),
            "evidence": [
                "metadata/package.yaml#selection"
                if package_schema in COMPONENT_PACKAGE_SCHEMAS
                else "legacy-package-schema"
            ]
            + [f"cli:--enable-provider={provider}" for provider in requested],
        }

    if requested:
        raise ApplyError(
            "--enable-provider is a clean-install choice; upgrades use provenance"
        )
    if new_provenance.is_file():
        content = new_provenance.read_bytes()
        provenance = load_yaml(new_provenance, "target provenance")
        resolved = deepcopy(
            validate_component_selection(
                provenance.get("selection"), "target provenance selection"
            )
        )
        return resolved, {
            "source": "target-provenance",
            "evidence": [
                {
                    "path": ".dev/ai-context/provenance.yaml",
                    "sha256": sha256_bytes(content),
                }
            ],
        }

    schema = inventory_schema(previous_files_path)
    if schema == "2.0.0":
        raise ApplyError(
            "component-aware upgrade requires .dev/ai-context/provenance.yaml"
        )
    if schema != "1.0.0":
        raise ApplyError(f"unsupported previous inventory schema: {schema!r}")
    content = previous_files_path.read_bytes()
    records, _ = inventory_records(
        load_yaml(previous_files_path, "previous files.yaml"), "previous inventory"
    )
    backlog_paths = sorted(
        path
        for path in records
        if inferred_component(path, records[path]) == "repo-backlog"
    )
    resolved["providers"]["repo-backlog"]["enabled"] = bool(backlog_paths)
    return resolved, {
        "source": "legacy-schema1-inventory",
        "evidence": [
            {
                "path": str(previous_files_path.resolve()),
                "sha256": sha256_bytes(content),
                "repo_backlog_path_count": len(backlog_paths),
            }
        ],
    }


def filter_component_records(
    records: dict[str, dict], selected: set[str]
) -> dict[str, dict]:
    return {
        path: record
        for path, record in records.items()
        if inferred_component(path, record) in selected
    }


def operation_component(operation: dict) -> str:
    component = operation.get("component_id")
    if isinstance(component, str) and component:
        return component
    return inferred_component(
        str(operation.get("path") or operation.get("from_path") or "")
    )


def count_components(operations: Iterable[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for operation in operations:
        component = operation_component(operation)
        counts[component] = counts.get(component, 0) + 1
    return dict(sorted(counts.items()))


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
    migration_bytes = migration_path.read_bytes()
    inventory = load_yaml(files_path, "files.yaml")
    migration = load_yaml(migration_path, "migration.yaml")
    package_id = package.get("package_id")
    if not isinstance(package_id, str) or not package_id:
        raise ApplyError("package.yaml package_id is required")
    if inventory.get("package_id") != package_id or migration.get("package_id") != package_id:
        raise ApplyError("package identity mismatch")
    package_schema = package.get("schema_version")
    if package_schema not in {"1.0.0", "1.1.0", *COMPONENT_PACKAGE_SCHEMAS}:
        raise ApplyError(f"unsupported package schema version: {package_schema!r}")
    if package_schema in COMPONENT_PACKAGE_SCHEMAS:
        selection = package.get("selection")
        if not isinstance(selection, dict):
            raise ApplyError("package selection must be a mapping")
        if migration.get("schema_version") == "3.0.0" and migration.get(
            "selection"
        ) != selection:
            raise ApplyError("package and migration selections must match")
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
    if package_schema in IDENTITY_PACKAGE_SCHEMAS:
        source = package.get("source")
        identity = package.get("identity")
        if not isinstance(source, dict) or not all(
            isinstance(source.get(key), str)
            and len(source[key]) == 40
            and all(char in "0123456789abcdef" for char in source[key])
            for key in ("commit", "tree")
        ):
            raise ApplyError("package source identity requires commit and tree SHA")
        expected_identity_schema = "1.1.0" if package_schema == "2.4.0" else "1.0.0"
        if (
            not isinstance(identity, dict)
            or identity.get("schema_version") != expected_identity_schema
        ):
            raise ApplyError("package identity schema is missing or unsupported")
        if package_schema == "2.4.0":
            if identity.get("public_artifact_base") != package_id:
                raise ApplyError(
                    "package public artifact base differs from package identity"
                )
            if package.get("profile_id") == "dotnet-backend":
                try:
                    resolved = expected_rule(package.get("version"))
                except PackageIdentityError as exc:
                    raise ApplyError(
                        f"package public identity version is invalid: {exc}"
                    ) from exc
                if (
                    package_id != expected_package_id(package.get("version"))
                    or identity.get("package_identity_policy")
                    != PUBLIC_PACKAGE_IDENTITY_POLICY
                    or identity.get("identity_rule") != resolved["rule_id"]
                ):
                    raise ApplyError(
                        "package public identity does not match its version"
                    )
        payload_fingerprint = sha256_bytes(
            "".join(
                f"{record['sha256']}  {relative}\n"
                for relative, record in sorted(
                    records.items(), key=lambda item: item[0].encode("utf-8")
                )
            ).encode("utf-8")
        )
        expected_identity = {
            "payload_fingerprint": payload_fingerprint,
            "files_manifest_digest": manifest_sha,
            "migration_digest": sha256_bytes(migration_bytes),
        }
        for key, value in expected_identity.items():
            if identity.get(key) != value:
                raise ApplyError(f"package identity {key} does not match package bytes")
        selected = identity.get("selected_input_fingerprint")
        if not isinstance(selected, str) or len(selected) != 64 or any(
            char not in "0123456789abcdef" for char in selected
        ):
            raise ApplyError("package identity selected_input_fingerprint is invalid")
    if package_schema in PORTABLE_VALIDATION_PACKAGE_SCHEMAS:
        try:
            validate_extracted_package(
                package_root,
                run_portable_entrypoints=False,
            )
        except PackageValidationError as exc:
            raise ApplyError(f"portable package validation failed: {exc}") from exc
    return package, records, migration, manifest_sha


def schema_1_migration_selection(
    path: Path | None,
    previous_version_value: str | None,
    migration: dict,
) -> tuple[dict[str, dict], list[dict], str | None]:
    from_data = migration.get("from")
    if not isinstance(from_data, dict):
        raise ApplyError("migration from must be a mapping")
    expected = from_data.get("manifest_sha256")
    version = from_data.get("version")
    if expected is None and version is None:
        if path is not None or previous_version_value is not None:
            raise ApplyError("clean install must not supply previous source identity")
        operations = migration.get("operations")
        if not isinstance(operations, list):
            raise ApplyError("migration operations must be a list")
        return {}, operations, None
    if not isinstance(expected, str) or len(expected) != 64 or not isinstance(version, str):
        raise ApplyError("upgrade migration requires previous version and manifest SHA")
    if path is None:
        raise ApplyError("upgrade migration requires --previous-files")
    declared_version = normalize_version(version, "migration source version")
    if (
        previous_version_value is not None
        and normalize_version(previous_version_value, "previous version") != declared_version
    ):
        raise ApplyError("previous version does not match migration.from")
    content = path.read_bytes()
    if sha256_bytes(content) != expected:
        raise ApplyError("previous files manifest SHA does not match migration.from")
    records, _ = inventory_records(load_yaml(path, "previous files.yaml"), "previous inventory")
    operations = migration.get("operations")
    if not isinstance(operations, list):
        raise ApplyError("migration operations must be a list")
    return records, operations, declared_version


def schema_2_migration_selection(
    path: Path | None,
    previous_version_value: str | None,
    migration: dict,
) -> tuple[dict[str, dict], list[dict], str | None]:
    clean_install = migration.get("clean_install")
    sources = migration.get("sources")
    if not isinstance(clean_install, dict) or not isinstance(
        clean_install.get("operations"), list
    ):
        raise ApplyError("schema 2 migration clean_install.operations must be a list")
    if not isinstance(sources, list):
        raise ApplyError("schema 2 migration sources must be a list")
    normalized_sources: list[tuple[str, str, list[dict]]] = []
    versions: set[str] = set()
    identities: set[tuple[str, str]] = set()
    for raw in sources:
        if not isinstance(raw, dict):
            raise ApplyError("schema 2 migration sources must be mappings")
        version = normalize_version(raw.get("version"), "migration source version")
        if raw.get("version") != version:
            raise ApplyError("migration source version must omit the v prefix")
        digest = raw.get("manifest_sha256")
        operations = raw.get("operations")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise ApplyError("migration source manifest_sha256 must be lowercase SHA-256")
        if not isinstance(operations, list):
            raise ApplyError("migration source operations must be a list")
        identity = (version, digest)
        if version in versions or identity in identities:
            raise ApplyError(f"duplicate or ambiguous migration source: {version}")
        versions.add(version)
        identities.add(identity)
        normalized_sources.append((version, digest, operations))
    expected_order = sorted(
        normalized_sources,
        key=lambda item: tuple(int(part) for part in item[0].split(".")),
    )
    if normalized_sources != expected_order:
        raise ApplyError("migration sources must use semantic-version order")
    if path is None and previous_version_value is None:
        return {}, clean_install["operations"], None
    if path is None or previous_version_value is None:
        raise ApplyError(
            "schema 2 upgrade requires --previous-version and --previous-files"
        )
    selected_version = normalize_version(previous_version_value, "previous version")
    content = path.read_bytes()
    selected_sha = sha256_bytes(content)
    matches = [
        item
        for item in normalized_sources
        if item[0] == selected_version and item[1] == selected_sha
    ]
    if not matches:
        raise ApplyError(
            "previous version and files manifest SHA do not match a supported migration source"
        )
    if len(matches) != 1:
        raise ApplyError("previous source identity is ambiguous")
    records, _ = inventory_records(
        load_yaml(path, "previous files.yaml"), "previous inventory"
    )
    return records, matches[0][2], selected_version


def migration_selection(
    path: Path | None,
    previous_version_value: str | None,
    migration: dict,
) -> tuple[dict[str, dict], list[dict], str | None]:
    schema_version = migration.get("schema_version")
    if schema_version == "1.0.0":
        return schema_1_migration_selection(
            path, previous_version_value, migration
        )
    if schema_version == "2.0.0":
        return schema_2_migration_selection(
            path, previous_version_value, migration
        )
    if schema_version == "3.0.0":
        return schema_2_migration_selection(
            path, previous_version_value, migration
        )
    raise ApplyError(f"unsupported migration schema version: {schema_version!r}")


def state_matches(
    root: Path,
    state: FileState,
    record: dict,
    snapshot: TargetGitSnapshot | None = None,
) -> bool:
    if not state.exists:
        return False
    raw_match = state.sha256 == record.get("sha256")
    canonical_match = (
        state.tracked
        and not state.dirty
        and state.git_eol_only
        and state.git_sha256 == record.get("sha256")
        and state.normalized_text_sha256 == record.get("sha256")
        and isinstance(record.get("path"), str)
        and (
            snapshot.no_content_transform(record["path"])
            if snapshot is not None
            else has_no_git_content_transform(root, record["path"])
        )
    )
    if not raw_match and not canonical_match:
        return False
    if state.mode == record.get("mode"):
        return True
    snapshot = snapshot or active_target_git_snapshot(root)
    if snapshot is not None:
        filemode_value = snapshot.core_filemode
        return (
            not filemode_value
            and state.mode == "0644"
            and record.get("mode") == "0755"
        )
    filemode = run_git(root, "config", "--bool", "core.filemode")
    if filemode.returncode != 0 or filemode.stdout.strip() not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        filemode.stdout.strip() == "false"
        and state.mode == "0644"
        and record.get("mode") == "0755"
    )


def observation(
    paths: Iterable[str],
    target: Path,
    snapshot: TargetGitSnapshot | None = None,
) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(set(paths), key=lambda item: item.encode("utf-8")):
        reject_symlink_boundary(target, path)
        state = file_state(target, path, snapshot)
        result[path] = state_record(state)
    return result


def required_framework_paths(incoming: dict[str, dict]) -> list[dict]:
    """Bind selected framework-managed package bytes to the pending receipt."""
    required: list[dict] = []
    for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
        record = incoming[path]
        if record.get("ownership") != "framework-managed":
            continue
        component_id = record.get("component_id")
        if not isinstance(component_id, str) or not component_id:
            component_id = "legacy-framework-core"
        required.append(
            {
                "path": path,
                "component_id": component_id,
                "ownership": "framework-managed",
                "sha256": record["sha256"],
                "mode": record["mode"],
            }
        )
    return required


def expected_operation_post_states(
    operations: Iterable[dict], incoming: dict[str, dict]
) -> list[dict]:
    """Seal the exact successful state of every active operation path."""
    absent = {"exists": False, "sha256": None, "mode": None}
    result: list[dict] = []
    for operation in operations:
        action = operation.get("action")
        if action not in {"add", "replace", "remove", "rename"}:
            continue
        paths: list[dict] = []
        if action in {"add", "replace", "rename"}:
            relative = operation["path"]
            record = incoming.get(relative)
            if not isinstance(record, dict):
                raise ApplyError(
                    f"active operation destination is absent from incoming inventory: {relative}"
                )
            paths.append(
                {"path": relative, "state": expected_present_state(record)}
            )
        if action == "remove":
            paths.append({"path": operation["path"], "state": absent})
        elif action == "rename":
            paths.append({"path": operation["from_path"], "state": absent})
        result.append({"operation_id": operation["id"], "paths": paths})
    return result


def selected_input_proof_identity(package: dict) -> dict | None:
    if package.get("schema_version") not in PORTABLE_VALIDATION_PACKAGE_SCHEMAS:
        return None
    validation = package.get("validation")
    if not isinstance(validation, dict):
        raise ApplyError("package validation identity is missing")
    path = validation.get("selected_inputs")
    digest = validation.get("selected_inputs_sha256")
    if path != "metadata/selected-inputs.json" or not isinstance(digest, str) or not re.fullmatch(
        r"[0-9a-f]{64}", digest
    ):
        raise ApplyError("package selected-input proof identity is invalid")
    return {"path": path, "sha256": digest}


def ignored_framework_paths(
    target: Path,
    required: list[dict],
    snapshot: TargetGitSnapshot | None = None,
) -> list[dict]:
    """Expose target-owned Git ignores without choosing an owner disposition."""
    unresolved: list[dict] = []
    snapshot = snapshot or active_target_git_snapshot(target)
    for item in required:
        path = item["path"]
        component_id = item["component_id"]
        reject_symlink_boundary(target, path)
        if snapshot is not None:
            rule = snapshot.ignore_rule(path)
        else:
            try:
                rule = git_ignore_rule(target, path)
            except TargetValidationError as exc:
                raise ApplyError(str(exc)) from exc
        if rule is None:
            continue
        unresolved.append(
            {
                "path": path,
                "component_id": component_id,
                "ownership": "framework-managed",
                "ignore_rule": rule,
                "owner_dispositions": [
                    "preserve-target-rule",
                    "add-narrow-exception",
                    "disable-component",
                    "pending-owner-decision",
                ],
            }
        )
    return unresolved


def build_plan(
    package_root: Path,
    target_root: Path,
    previous_files_path: Path | None = None,
    previous_version_value: str | None = None,
    enable_providers: Iterable[str] | None = None,
    multi_hop_checkpoint_context: dict | None = None,
    git_inspection_hook: Callable[[dict], None] | None = None,
) -> dict:
    phase_started = time.perf_counter_ns()
    target = target_root.resolve()
    admission_snapshot = active_target_git_snapshot(target)
    if admission_snapshot is None:
        admission_snapshot = capture_target_git_snapshot(
            target,
            [],
            phase="plan-admission",
            require_clean=multi_hop_checkpoint_context is None,
        )
    elif admission_snapshot.phase != "plan-admission":
        raise ApplyError("active target Git snapshot phase is not plan admission")
    with target_git_snapshot_scope(admission_snapshot):
        route_context = (
            verify_multi_hop_checkpoint_for_planning(
                target, multi_hop_checkpoint_context
            )
            if multi_hop_checkpoint_context is not None
            else None
        )
    package, incoming, migration, manifest_sha = validate_package_root(package_root)
    previous, operations, selected_version = migration_selection(
        previous_files_path,
        previous_version_value,
        migration,
    )
    upgrade_remediation_required = selected_version is not None
    selected_input = {
        "previous_files": (
            str(previous_files_path.resolve()) if previous_files_path else None
        ),
        "previous_files_sha256": (
            sha256_bytes(previous_files_path.read_bytes())
            if previous_files_path is not None
            else None
        ),
        "previous_version": selected_version,
    }
    incoming_validation = (
        incoming_package_validation(package_root, package)
        if upgrade_remediation_required
        else None
    )
    default_selection = (
        validate_component_selection(package.get("selection"), "package selection")
        if package.get("schema_version") in COMPONENT_PACKAGE_SCHEMAS
        else deepcopy(LEGACY_COMPONENT_SELECTION)
    )
    resolved_selection, selection_resolution = resolve_effective_selection(
        package,
        target,
        previous_files_path,
        enable_providers,
    )
    selected_components = enabled_components(resolved_selection)
    incoming = filter_component_records(incoming, selected_components)
    previous = filter_component_records(previous, selected_components)
    required_paths = required_framework_paths(incoming)
    skipped_by_selection = [
        raw
        for raw in operations
        if isinstance(raw, dict)
        and operation_component(raw) not in selected_components
    ]
    operations = [
        raw
        for raw in operations
        if not isinstance(raw, dict)
        or operation_component(raw) in selected_components
    ]
    ids: set[str] = set()
    touched_paths: dict[str, str] = {}
    operation_paths: list[str] = []
    normalized: list[dict] = []
    case_map = existing_case_map(target)
    for raw in operations:
        if not isinstance(raw, dict):
            raise ApplyError("migration operations must be mappings")
        operation_id, kind, ownership = raw.get("id"), raw.get("kind"), raw.get("ownership")
        component_id = raw.get("component_id")
        if not isinstance(operation_id, str) or not operation_id or operation_id in ids:
            raise ApplyError("migration operation IDs must be unique non-empty strings")
        ids.add(operation_id)
        if migration.get("schema_version") == "3.0.0" and (
            not isinstance(component_id, str) or not component_id
        ):
            raise ApplyError(
                f"schema 3 migration operation requires component_id: {operation_id}"
            )
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
            if candidate in {
                ".dev/AI-CONTEXT-SOURCE.yaml",
                ".dev/AI-CONTEXT-APPLY-PENDING.yaml",
                ".dev/ai-context/provenance.yaml",
                ".dev/ai-context/customizations.yaml",
            } or (candidate is not None and is_target_effective_rule_path(candidate)):
                raise ApplyError(
                    f"migration cannot manage provenance, pending receipt, or target effective state: {candidate}"
                )
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
        normalized.append(
            {
                "id": operation_id,
                "kind": kind,
                "path": path,
                "from_path": from_path,
                "ownership": ownership,
                "component_id": component_id,
            }
        )
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
    observed_paths = [*operation_paths, *(item["path"] for item in required_paths)]
    snapshot = capture_target_git_snapshot(
        target,
        observed_paths,
        phase="plan",
        require_clean=route_context is None,
    )
    if not admission_snapshot.same_admission_identity(snapshot):
        raise ApplyError("target Git or worktree identity changed during planning")
    snapshot.absorb_stats(admission_snapshot)
    head = snapshot.head
    ignored_paths = ignored_framework_paths(target, required_paths, snapshot)
    ignored_by_path = {item["path"]: item for item in ignored_paths}
    observed = observation(observed_paths, target, snapshot)
    managed_state_conflicts: list[dict] = []
    for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
        record = incoming[path]
        if record.get("ownership") != "framework-managed" or path not in previous:
            continue
        previous_record = previous[path]
        unchanged = all(
            previous_record.get(key) == record.get(key)
            for key in ("sha256", "mode", "ownership")
        )
        if unchanged and not state_matches(
            target, FileState(**observed[path]), previous_record, snapshot
        ):
            managed_state_conflicts.append(
                {
                    "path": path,
                    "component_id": record.get("component_id"),
                    "ownership": "framework-managed",
                    "reason": "selected managed path differs from the unchanged previous release identity",
                    "observed": observed[path],
                    "expected_previous": {
                        "sha256": previous_record["sha256"],
                        "mode": previous_record["mode"],
                    },
                }
            )
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
            if not state_matches(target, current, previous[path], snapshot):
                action, reason = "reconcile", "current hash or mode differs from previous release"
        elif kind == "remove":
            if item["ownership"] != "framework-managed" or path not in previous:
                raise ApplyError(f"remove requires a previous managed record: {path}")
            if previous[path].get("ownership") != "framework-managed":
                raise ApplyError(f"remove previous ownership must be framework-managed: {path}")
            if not current.exists:
                action, reason = "noop", "path is already absent"
            elif not state_matches(target, current, previous[path], snapshot):
                action, reason = "reconcile", "current hash or mode differs from previous release"
        elif kind == "rename":
            if item["ownership"] != "framework-managed" or source not in previous or path not in incoming:
                raise ApplyError(f"rename requires previous source and incoming destination: {operation_id}")
            if previous[source].get("ownership") != "framework-managed" or incoming[path].get("ownership") != "framework-managed":
                raise ApplyError(f"rename inventory ownership must be framework-managed: {operation_id}")
            source_state = FileState(**observed[source])
            if not state_matches(target, source_state, previous[source], snapshot):
                action, reason = "reconcile", "rename source hash or mode differs from previous release"
            elif current.exists:
                action, reason = "reconcile", "rename destination already exists"
        else:
            action, reason = "reconcile", "migration explicitly requires reconciliation"
        ignored = ignored_by_path.get(path)
        if ignored is not None:
            action = "unresolved"
            reason = framework_managed_ignore_message(
                path, ignored["component_id"], ignored["ignore_rule"]
            )
        planned.append({**item, "action": action, "reason": reason})
    would_apply = [
        item
        for item in planned
        if item["action"] in {"add", "replace", "remove", "rename"}
    ]
    would_skip = [
        item
        for item in planned
        if item["action"] in {"noop", "reconcile", "unresolved"}
    ]
    plan = {
        "schema_version": APPLY_PLAN_SCHEMA_VERSION,
        "package_id": package["package_id"],
        "package_version": package.get("version"),
        "package_manifest_sha256": manifest_sha,
        "migration_sha256": sha256_bytes(
            (package_root / "metadata/migration.yaml").read_bytes()
        ),
        "package_selected_input_proof": selected_input_proof_identity(package),
        "package_source": deepcopy(package.get("source")),
        "migration_contract": {
            "schema_version": migration.get("schema_version"),
            "from": deepcopy(migration.get("from")),
            "sources": deepcopy(migration.get("sources")),
            "to": deepcopy(migration.get("to")),
        },
        "upgrade_remediation_required": upgrade_remediation_required,
        "migration_selected_input": selected_input,
        "incoming_package_validation": incoming_validation,
        "package_root": str(package_root.resolve()),
        "target_root": str(target),
        "target_starting_commit": head,
        "previous_files": str(previous_files_path.resolve()) if previous_files_path else None,
        "previous_version": selected_version,
        "selection": resolved_selection,
        "selection_default": default_selection,
        "selection_resolution": selection_resolution,
        "selection_request": {
            "enable_providers": sorted(set(enable_providers or [])),
        },
        "component_operation_counts": {
            "would_apply": count_components(would_apply),
            "would_skip": count_components(
                [*would_skip, *skipped_by_selection]
            ),
        },
        "required_framework_paths": required_paths,
        "ignored_framework_paths": ignored_paths,
        "managed_state_conflicts": managed_state_conflicts,
        "observed": observed,
        "target_observed_prestate_sha256": canonical_digest(observed),
        "target_git_semantics": target_git_semantic_identity(
            snapshot, observed.keys()
        ),
        "target_validation_profile": target_validation_profile(target),
        "target_provenance": target_file_identity(
            target, ".dev/ai-context/provenance.yaml"
        ),
        "target_provenance_source": target_provenance_source(target),
        "target_semantic_customizations": target_file_identity(
            target, ".dev/ai-context/customizations.yaml"
        ),
        "operations": planned,
        "operation_post_states": expected_operation_post_states(planned, incoming),
    }
    if route_context is not None:
        # Keep #203's plan schema.  The sealed optional context is a strictly
        # dispatched S2 admission record, never a generic dirty-worktree mode.
        plan[MULTI_HOP_ROUTE_CONTEXT_KEY] = route_context
    if snapshot.changed_paths(full_worktree_scan=True) != set(snapshot.dirty_paths):
        raise ApplyError("target worktree changed after planning snapshot capture")
    plan["plan_sha256"] = canonical_digest(plan)
    emit_git_inspection_metrics(
        snapshot,
        git_inspection_hook,
        phase_duration_ns=time.perf_counter_ns() - phase_started,
        outcome="passed",
    )
    return plan


def remediation_proposal(plan: dict) -> dict:
    operations = plan.get("operations")
    if not isinstance(operations, list):
        raise ApplyError("upgrade remediation plan operations are invalid")
    actionable = deepcopy(active_operations(plan))
    active = [item.get("id") for item in actionable]
    if not all(isinstance(item, str) and item for item in active):
        raise ApplyError("upgrade remediation automatic operation records are invalid")
    reconciliation = [
        item.get("id")
        for item in operations
        if isinstance(item, dict) and item.get("action") == "reconcile"
    ]
    unresolved = [
        item.get("id")
        for item in operations
        if isinstance(item, dict) and item.get("action") == "unresolved"
    ]
    if not all(isinstance(item, str) and item for item in [*reconciliation, *unresolved]):
        raise ApplyError("upgrade remediation operation identities are invalid")
    return {
        "apply_operation_ids": active,
        "apply_operations": actionable,
        "reconciliation_ids": reconciliation,
        "unresolved_operation_ids": unresolved,
        "ignored_framework_paths": deepcopy(plan.get("ignored_framework_paths", [])),
        "managed_state_conflicts": deepcopy(plan.get("managed_state_conflicts", [])),
    }


def remediation_unresolved_conflicts(plan: dict, proposal: dict) -> list[dict]:
    conflicts: list[dict] = []
    operations = plan.get("operations", [])
    for item in operations:
        if not isinstance(item, dict) or item.get("action") not in {"reconcile", "unresolved"}:
            continue
        conflicts.append(
            {
                "kind": item["action"],
                "operation_id": item.get("id"),
                "path": item.get("path"),
                "reason": item.get("reason"),
            }
        )
    for item in proposal["ignored_framework_paths"]:
        conflicts.append({"kind": "ignored-framework-path", "detail": item})
    for item in proposal["managed_state_conflicts"]:
        conflicts.append({"kind": "managed-state-conflict", "detail": item})
    return conflicts


def packet_digest(packet: dict) -> str:
    unsigned = deepcopy(packet)
    declared = unsigned.pop("canonical_digest", None)
    digest = canonical_digest(unsigned)
    if declared != digest:
        raise ApplyError("upgrade remediation packet digest is invalid")
    return digest


def build_upgrade_remediation_packet(plan: dict) -> dict:
    """Create the immutable machine proposal; it deliberately has no owner grant."""
    if not is_upgrade_plan(plan):
        raise ApplyError("clean-install plans do not have an upgrade remediation packet")
    transaction_id = transaction_id_for_plan(plan)
    observed_digest = require_sha256(
        plan.get("target_observed_prestate_sha256"), "target observed pre-state SHA-256"
    )
    if observed_digest != canonical_digest(plan.get("observed")):
        raise ApplyError("target observed pre-state digest is invalid")
    validation_profile = plan.get("target_validation_profile")
    if not isinstance(validation_profile, dict):
        raise ApplyError("target validation profile is invalid")
    profile_path = safe_path(validation_profile.get("path"), "target validation profile path")
    profile_sha = require_sha256(
        validation_profile.get("sha256"),
        "target validation profile SHA-256",
        allow_none=True,
    )
    profile_argv = validation_profile.get("argv")
    if not isinstance(profile_argv, list) or not all(
        isinstance(item, str) and item for item in profile_argv
    ):
        raise ApplyError("target validation profile argv is invalid")
    profile_snapshot = validation_profile.get("snapshot")
    if not isinstance(profile_snapshot, dict):
        raise ApplyError("target validation profile snapshot is invalid")
    profile = {
        "path": profile_path,
        "sha256": profile_sha,
        "argv": profile_argv,
        "snapshot": deepcopy(profile_snapshot),
    }
    proposal = remediation_proposal(plan)
    package_validation = plan.get("incoming_package_validation")
    if not isinstance(package_validation, dict):
        raise ApplyError("incoming package validation evidence is missing")
    for authority in ("target_provenance", "target_semantic_customizations"):
        identity = plan.get(authority)
        if not isinstance(identity, dict):
            raise ApplyError(f"{authority} identity is invalid")
        safe_path(identity.get("path"), authority)
        require_sha256(identity.get("sha256"), authority, allow_none=True)
    packet = {
        "schema_version": UPGRADE_REMEDIATION_PACKET_SCHEMA_VERSION,
        "transaction_id": transaction_id,
        "plan_sha256": transaction_id,
        "target": {
            "root": plan.get("target_root"),
            "starting_commit": plan.get("target_starting_commit"),
            "observed_prestate_sha256": observed_digest,
            "observed": deepcopy(plan.get("observed")),
        },
        "package": {
            "id": plan.get("package_id"),
            "version": plan.get("package_version"),
            "root": plan.get("package_root"),
            "source": deepcopy(plan.get("package_source")),
            "manifest_sha256": plan.get("package_manifest_sha256"),
            "migration_sha256": plan.get("migration_sha256"),
            "selected_input_proof": deepcopy(plan.get("package_selected_input_proof")),
            "validation": deepcopy(package_validation),
        },
        "migration": {
            "contract": deepcopy(plan.get("migration_contract")),
            "selected_input": deepcopy(plan.get("migration_selected_input")),
        },
        "selection": deepcopy(plan.get("selection")),
        "automatic_proposal": proposal,
        "owner_decision": None,
        "unresolved_conflicts": remediation_unresolved_conflicts(plan, proposal),
        "target_validation_profile": profile,
        "target_validation_profile_digest": canonical_digest(profile),
        "provenance": {
            **deepcopy(plan.get("target_provenance")),
            "source": deepcopy(plan.get("target_provenance_source")),
        },
        "semantic_customizations": deepcopy(plan.get("target_semantic_customizations")),
        "resume_rollback": {
            "initial_state": "planned",
            "resume_requires": ["same-plan", "same-packet", "same-decision"],
            "rollback_allowed_until_provenance_finalized": True,
        },
    }
    packet["canonical_digest"] = canonical_digest(packet)
    return packet


def render_upgrade_remediation_report(packet: dict) -> str:
    """Render only values already sealed in the machine-readable proposal."""
    digest = packet_digest(packet)
    target = packet["target"]
    package = packet["package"]
    proposal = packet["automatic_proposal"]
    return "\n".join(
        [
            f"derived_from_packet_digest: {digest}",
            "# Upgrade remediation report",
            "",
            f"- Transaction: `{packet['transaction_id']}`",
            f"- Target HEAD: `{target['starting_commit']}`",
            f"- Package: `{package['id']}` / `{package['version']}`",
            f"- Automatic operations: {', '.join(proposal['apply_operation_ids']) or '(none)'}",
            f"- Reconciliation decisions: {', '.join(proposal['reconciliation_ids']) or '(none)'}",
            f"- Unresolved conflicts: {len(packet['unresolved_conflicts'])}",
            f"- Incoming validation: {package['validation']['execution']['outcome']}",
            "",
        ]
    )


def load_upgrade_remediation_decision(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ApplyError("upgrade remediation decision must be a regular file")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ApplyError("cannot read upgrade remediation decision") from exc
    if not isinstance(value, dict):
        raise ApplyError("upgrade remediation decision must be a mapping")
    return value


def validate_upgrade_remediation_decision(decision: dict, packet: dict) -> dict:
    required = {
        "schema_version",
        "packet_sha256",
        "plan_sha256",
        "transaction_id",
        "status",
        "owner",
        "decided_at",
        "evidence",
        "reason",
        "accepted_operation_ids",
        "reconciliation_ids",
        "policy_adoptions",
        "candidate_authority",
    }
    if set(decision) != required:
        raise ApplyError("upgrade remediation decision fields are incomplete or unexpected")
    digest = packet_digest(packet)
    if decision.get("schema_version") != UPGRADE_REMEDIATION_DECISION_SCHEMA_VERSION:
        raise ApplyError("unsupported upgrade remediation decision schema")
    if decision.get("packet_sha256") != digest:
        raise ApplyError("upgrade remediation decision packet binding differs")
    if (
        decision.get("plan_sha256") != packet.get("plan_sha256")
        or decision.get("transaction_id") != packet.get("transaction_id")
    ):
        raise ApplyError("upgrade remediation decision plan binding differs")
    status = decision.get("status")
    if status not in {"approved", "rejected"}:
        raise ApplyError("upgrade remediation decision status is invalid")
    for key in ("owner", "decided_at", "evidence", "reason"):
        if not isinstance(decision.get(key), str) or not decision[key].strip():
            raise ApplyError(f"upgrade remediation decision {key} is invalid")
    if not safe_repo_reference(decision["evidence"]):
        raise ApplyError("upgrade remediation decision evidence is not a safe repository reference")
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        decision["decided_at"],
    ):
        raise ApplyError("upgrade remediation decision decided_at must be ISO 8601 with offset")
    proposal = packet["automatic_proposal"]
    accepted = decision.get("accepted_operation_ids")
    reconciliations = decision.get("reconciliation_ids")
    if not isinstance(accepted, list) or not isinstance(reconciliations, list) or not all(
        isinstance(item, str) and item for item in [*accepted, *reconciliations]
    ):
        raise ApplyError("upgrade remediation decision operation selections are invalid")
    if len(accepted) != len(set(accepted)) or len(reconciliations) != len(set(reconciliations)):
        raise ApplyError("upgrade remediation decision operation selections contain duplicates")
    if status == "rejected":
        if (
            accepted
            or reconciliations
            or decision.get("policy_adoptions") is not None
            or decision.get("candidate_authority") is not None
        ):
            raise ApplyError("rejected upgrade remediation decision cannot grant operation or policy authority")
        return deepcopy(decision)
    candidate_authority = decision.get("candidate_authority")
    if not isinstance(candidate_authority, dict) or set(candidate_authority) != {
        "provenance_sha256",
        "customizations_sha256",
    }:
        raise ApplyError("approved upgrade remediation decision candidate_authority is invalid")
    require_sha256(
        candidate_authority.get("provenance_sha256"),
        "approved upgrade remediation decision candidate provenance SHA-256",
    )
    require_sha256(
        candidate_authority.get("customizations_sha256"),
        "approved upgrade remediation decision candidate customizations SHA-256",
    )
    policy_adoptions = decision.get("policy_adoptions")
    if policy_adoptions is not None:
        if not isinstance(policy_adoptions, dict) or set(policy_adoptions) != {
            "commit_subject_grammar"
        }:
            raise ApplyError("upgrade remediation decision policy_adoptions is invalid")
        adoption = policy_adoptions.get("commit_subject_grammar")
        if not isinstance(adoption, dict) or set(adoption) != {
            "policy_id",
            "legacy_history_tip",
            "adopted_at",
            "incoming_policy_sha256",
            "decision_evidence",
        }:
            raise ApplyError("upgrade remediation decision commit grammar adoption is invalid")
        if adoption.get("policy_id") != "git-commit-subject/v2":
            raise ApplyError("upgrade remediation decision commit grammar policy differs")
        require_sha256(
            adoption.get("legacy_history_tip"),
            "upgrade remediation decision legacy history tip",
        )
        require_sha256(
            adoption.get("incoming_policy_sha256"),
            "upgrade remediation decision incoming policy SHA-256",
        )
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
            str(adoption.get("adopted_at", "")),
        ):
            raise ApplyError("upgrade remediation decision adoption time is invalid")
        if not safe_repo_reference(adoption.get("decision_evidence")):
            raise ApplyError("upgrade remediation decision adoption evidence is invalid")
    if accepted != proposal["apply_operation_ids"]:
        raise ApplyError("approved decision does not accept the exact automatic proposal")
    if reconciliations != proposal["reconciliation_ids"]:
        raise ApplyError("approved decision does not bind all reconciliation items")
    if (
        proposal["unresolved_operation_ids"]
        or proposal["ignored_framework_paths"]
        or proposal["managed_state_conflicts"]
    ):
        raise ApplyError("approved decision cannot override unresolved package conflicts")
    return deepcopy(decision)


def build_incoming_validation_receipt(packet: dict) -> dict:
    digest = packet_digest(packet)
    validation = deepcopy(packet["package"]["validation"])
    execution = validation.get("execution") if isinstance(validation, dict) else None
    if not isinstance(execution, dict):
        raise ApplyError("incoming package validation receipt is missing execution evidence")
    return {
        "schema_version": INCOMING_VALIDATION_RECEIPT_SCHEMA_VERSION,
        "authority": validation.get("authority"),
        "outcome": execution.get("outcome"),
        "transaction_id": packet["transaction_id"],
        "plan_sha256": packet["plan_sha256"],
        "packet_sha256": digest,
        "target": {
            "root": packet["target"]["root"],
            "starting_commit": packet["target"]["starting_commit"],
            "observed_prestate_sha256": packet["target"]["observed_prestate_sha256"],
        },
        "package": {
            "id": packet["package"]["id"],
            "version": packet["package"]["version"],
            "manifest_sha256": packet["package"]["manifest_sha256"],
            "migration_sha256": packet["package"]["migration_sha256"],
        },
        "target_validation_profile": deepcopy(packet["target_validation_profile"]),
        "target_validation_profile_digest": packet[
            "target_validation_profile_digest"
        ],
        "validator": validation,
    }


def mode_int(mode: str) -> int:
    return 0o755 if mode == "0755" else 0o644


def fsync_directory(path: Path) -> None:
    """Persist a directory entry where the host exposes directory fsync.

    Windows namespace durability is supplied by MoveFileExW with
    MOVEFILE_WRITE_THROUGH at each atomic replacement or removal boundary.
    """
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def windows_move_path(source: Path, destination: Path, flags: int) -> None:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    move_file = kernel32.MoveFileExW
    move_file.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
    move_file.restype = wintypes.BOOL
    if not move_file(str(source), str(destination), flags):
        raise ctypes.WinError(ctypes.get_last_error())


def atomic_replace(temporary: Path, destination: Path) -> None:
    if os.name == "nt":
        windows_move_path(temporary, destination, WINDOWS_ATOMIC_REPLACE_FLAGS)
        return
    os.replace(temporary, destination)


def atomic_write_bytes(
    path: Path,
    content: bytes,
    mode: int = 0o644,
    *,
    temporary_path: Path | None = None,
    hook: Callable[[str, dict], None] | None = None,
    boundary_details: dict | None = None,
) -> None:
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError(f"cannot atomically replace symlink or reparse point: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if temporary_path is None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary = Path(temporary_name)
    else:
        temporary = temporary_path
        if temporary.parent != path.parent:
            raise ApplyError(f"atomic staging path must share its destination parent: {path}")
        if temporary.exists() or temporary.is_symlink() or is_reparse_point(temporary):
            raise ApplyError(f"atomic staging path already exists or is unsafe: {temporary}")
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
    preserve_temporary = False
    try:
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            if written <= 0:
                raise ApplyError(f"short write while staging {path}")
            offset += written
        os.fsync(descriptor)
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        if hook is not None:
            invoke_boundary(
                hook,
                "after_target_staging_fsync",
                {**(boundary_details or {}), "staging_path": str(temporary)},
            )
        atomic_replace(temporary, path)
        fsync_directory(path.parent)
    except InjectedInterruption:
        preserve_temporary = True
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary.exists() and not preserve_temporary:
            temporary.unlink()


def atomic_write_yaml(path: Path, value: dict) -> bytes:
    content = deterministic_yaml_bytes(value)
    atomic_write_bytes(path, content)
    return content


def observe_journal_io(
    hook: Callable[[dict], None] | None,
    *,
    kind: str,
    path: Path,
    bytes_written: int,
) -> None:
    if hook is not None:
        hook(
            {
                "kind": kind,
                "path": str(path),
                "write_calls": 1,
                "bytes_written": bytes_written,
            }
        )


def durable_append_bytes(
    path: Path,
    content: bytes,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> None:
    """Append one framed record and durably publish it before returning."""
    if not content or not content.endswith(b"\n"):
        raise ApplyError("durable journal append must be one newline-framed record")
    require_safe_transaction_root(path.parent)
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError("transaction journal progress log is unsafe")
    existed = path.exists()
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_APPEND
            | getattr(os, "O_BINARY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except OSError as exc:
        raise ApplyError(f"cannot safely append transaction journal progress: {path}") from exc
    try:
        offset = 0
        while offset < len(content):
            written = os.write(descriptor, content[offset:])
            if written <= 0:
                raise ApplyError(f"short write while appending {path}")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if not existed:
        fsync_directory(path.parent)
    observe_journal_io(
        journal_io_hook,
        kind="append",
        path=path,
        bytes_written=len(content),
    )


def durable_unlink(path: Path, transaction_root_path: Path) -> None:
    if os.name != "nt":
        path.unlink()
        fsync_directory(path.parent)
        return
    tombstone_root = transaction_root_path / "deleted"
    tombstone_root.mkdir(parents=True, exist_ok=True)
    if path.stat().st_dev != tombstone_root.stat().st_dev:
        raise ApplyError(
            f"cannot durably remove a target path across Windows volumes: {path}"
        )
    stem = sha256_bytes(str(path.resolve()).encode("utf-8"))
    index = 0
    while True:
        tombstone = tombstone_root / f"{stem}-{index:04d}.deleted"
        if not tombstone.exists():
            break
        index += 1
    windows_move_path(path, tombstone, WINDOWS_MOVEFILE_WRITE_THROUGH)
    try:
        tombstone.unlink()
    except OSError:
        # The write-through rename already made the governed source path
        # durably absent. A retained Git-admin tombstone is safe to collect
        # after recovery and must not weaken the journal boundary.
        pass


def write_payload(
    package_root: Path,
    target: Path,
    path: str,
    record: dict,
    journal: dict,
    hook: Callable[[str, dict], None] | None,
    boundary_details: dict,
) -> None:
    destination = target / Path(*PurePosixPath(path).parts)
    reject_symlink_boundary(target, path)
    source = package_root / "payload" / Path(*PurePosixPath(path).parts)
    content = source.read_bytes()
    if sha256_bytes(content) != record["sha256"]:
        raise ApplyError(f"package payload changed after validation: {path}")
    atomic_write_bytes(
        destination,
        content,
        mode_int(record["mode"]),
        temporary_path=target_staging_path(target, journal, path),
        hook=hook,
        boundary_details={**boundary_details, "destination": path, "purpose": "apply"},
    )


def plan_digest(plan: dict) -> str:
    unsigned = deepcopy(plan)
    declared = unsigned.pop("plan_sha256", None)
    digest = canonical_digest(unsigned)
    if declared != digest:
        raise ApplyError("apply plan digest is invalid")
    return digest


def transaction_id_for_plan(plan: dict) -> str:
    return plan_digest(plan)


def git_admin_transaction_base(target: Path) -> Path:
    snapshot = active_target_git_snapshot(target)
    if snapshot is not None:
        return snapshot.transaction_base
    result = run_git(target, "rev-parse", "--path-format=absolute", "--git-path", "ai-context-package-apply")
    if result.returncode != 0:
        result = run_git(target, "rev-parse", "--git-path", "ai-context-package-apply")
    if result.returncode != 0 or not result.stdout.strip():
        raise ApplyError("cannot resolve target Git administrative transaction directory")
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else (target / value).resolve()


def git_admin_multi_hop_route_base(target: Path) -> Path:
    """Return the one Git-admin root for sealed multi-hop route evidence."""
    snapshot = active_target_git_snapshot(target)
    if snapshot is not None:
        return snapshot.multi_hop_route_base
    result = run_git(
        target,
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        MULTI_HOP_ROUTE_DIRECTORY,
    )
    if result.returncode != 0:
        result = run_git(target, "rev-parse", "--git-path", MULTI_HOP_ROUTE_DIRECTORY)
    if result.returncode != 0 or not result.stdout.strip():
        raise ApplyError("cannot resolve target Git administrative multi-hop route directory")
    value = Path(result.stdout.strip())
    return value if value.is_absolute() else (target / value).resolve()


def multi_hop_route_root(target: Path, route_transaction_id: str) -> Path:
    require_sha256(route_transaction_id, "multi-hop route transaction ID")
    return git_admin_multi_hop_route_base(target) / route_transaction_id


def _route_version(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", value
    ):
        raise ApplyError(f"{label} must be a vMAJOR.MINOR.PATCH version")
    return value


def _read_route_regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or is_reparse_point(path) or not path.is_file():
        raise ApplyError(f"{label} must be a regular file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ApplyError(f"cannot read {label}: {exc}") from exc


def _read_canonical_route_json(path: Path, label: str) -> tuple[dict, bytes]:
    raw = _read_route_regular_bytes(path, label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyError(f"{label} is not canonical JSON") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
        raise ApplyError(f"{label} is not canonical JSON")
    return value, raw


def _read_deterministic_route_yaml(path: Path, label: str) -> tuple[dict, bytes]:
    raw = _read_route_regular_bytes(path, label)
    try:
        value = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ApplyError(f"{label} cannot be parsed") from exc
    if not isinstance(value, dict) or deterministic_yaml_bytes(value) != raw:
        raise ApplyError(f"{label} is not deterministic YAML")
    return value, raw


def _route_context(value: object) -> dict:
    if not isinstance(value, dict):
        raise ApplyError("multi-hop route context fields are invalid")
    schema = value.get("schema_version")
    initial = schema == MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION
    required = (
        {
            "schema_version",
            "route_transaction_id",
            "route_intent_sha256",
            "next_hop_index",
            "edge_id",
            "edge_order",
            "from_version",
            "to_version",
        }
        if initial
        else {
            "schema_version",
            "route_transaction_id",
            "route_intent_sha256",
            "checkpoint_index",
            "checkpoint_sha256",
            "checkpoint_predecessor_sha256",
            "next_hop_index",
            "edge_id",
            "edge_order",
            "from_version",
            "to_version",
        }
    )
    if set(value) != required:
        raise ApplyError("multi-hop route context fields are invalid")
    if schema not in {
        MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION,
        MULTI_HOP_ROUTE_CONTEXT_SCHEMA_VERSION,
    }:
        raise ApplyError("multi-hop route context schema is invalid")
    context = deepcopy(value)
    for key in ("route_transaction_id", "route_intent_sha256"):
        require_sha256(context.get(key), f"multi-hop checkpoint context {key}")
    if not initial:
        require_sha256(context.get("checkpoint_sha256"), "multi-hop checkpoint context checkpoint_sha256")
        predecessor = context.get("checkpoint_predecessor_sha256")
        require_sha256(
            predecessor,
            "multi-hop checkpoint context predecessor checkpoint SHA-256",
            allow_none=True,
        )
    if type(context.get("next_hop_index")) is not int or type(context.get("edge_order")) is not int:
        raise ApplyError("multi-hop checkpoint context hop order is invalid")
    if initial:
        if context["next_hop_index"] != 0 or context["edge_order"] != 1:
            raise ApplyError("multi-hop initial route context hop order is invalid")
    elif (
        type(context.get("checkpoint_index")) is not int
        or context["checkpoint_index"] < 0
        or context["next_hop_index"] != context["checkpoint_index"] + 1
        or context["edge_order"] != context["next_hop_index"] + 1
    ):
        raise ApplyError("multi-hop checkpoint context hop order is invalid")
    if not isinstance(context.get("edge_id"), str) or not context["edge_id"]:
        raise ApplyError("multi-hop checkpoint context edge ID is invalid")
    _route_version(context.get("from_version"), "multi-hop checkpoint context from_version")
    _route_version(context.get("to_version"), "multi-hop checkpoint context to_version")
    return context


def route_checkpoint_context(plan: dict) -> dict | None:
    value = plan.get(MULTI_HOP_ROUTE_CONTEXT_KEY)
    return None if value is None else _route_context(value)


def _require_complete_multi_hop_checkpoint_evidence(target: Path) -> None:
    """Require the target-owned validator to accept retained route evidence.

    A later child is allowed to plan against a dirty target only through an
    already finalized, fully cross-bound route checkpoint.  The target
    validator is the sole shared implementation of the retained checkpoint
    shape (child plan/journal/terminal/receipt/authority bindings), so do not
    duplicate a lossy subset here.
    """
    try:
        import ai_context_target_provenance as target_provenance
    except ImportError as exc:
        raise ApplyError("multi-hop checkpoint validator is unavailable") from exc
    snapshot = active_target_git_snapshot(target)
    if snapshot is None:
        raise ApplyError(
            "multi-hop checkpoint validation requires one active target Git snapshot"
        )
    current_surface = route_checkpoint_surface(target)
    errors: list[str] = []
    target_provenance.validate_multi_hop_route_transactions(
        target,
        errors,
        git_snapshot={
            "head": snapshot.head,
            "apply_transaction_directory": snapshot.transaction_base,
            "multi_hop_route_directory": snapshot.multi_hop_route_base,
            "target_surface": current_surface,
        },
    )
    if errors:
        raise ApplyError(
            "multi-hop finalized checkpoint evidence is invalid: "
            + "; ".join(errors)
        )


def route_checkpoint_surface(target: Path) -> dict[str, dict]:
    # The pending receipt is a transient, separately archived transaction
    # artifact.  It is cleared immediately after checkpoint sealing and must
    # never become part of the durable target authority surface.
    paths = sorted(
        (
            item
            for item in changed_target_paths(target)
            if item != PENDING_RECEIPT_PATH
        ),
        key=lambda item: item.encode("utf-8"),
    )
    result: dict[str, dict] = {}
    for relative in paths:
        relative = safe_path(relative, "multi-hop checkpoint target path")
        result[relative] = state_record(file_state(target, relative))
    return result


def _route_edge_identity(value: object, label: str) -> dict:
    required = {"edge_id", "order", "from_version", "to_version", "identity_sha256"}
    if not isinstance(value, dict) or set(value) != required:
        raise ApplyError(f"{label} fields are invalid")
    if not isinstance(value.get("edge_id"), str) or not value["edge_id"]:
        raise ApplyError(f"{label} edge ID is invalid")
    if type(value.get("order")) is not int or value["order"] < 1:
        raise ApplyError(f"{label} order is invalid")
    _route_version(value.get("from_version"), f"{label} from_version")
    _route_version(value.get("to_version"), f"{label} to_version")
    require_sha256(value.get("identity_sha256"), f"{label} identity SHA-256")
    return deepcopy(value)


def _load_route_checkpoint_context(
    target: Path,
    context_value: object,
    *,
    allowed_route_states: set[str],
    allowed_mutations: set[str] | None = None,
) -> tuple[dict, dict, dict]:
    """Validate a sealed checkpoint before a later child hop can use it.

    The caller supplies no path: every location is derived from Git's own
    administrative root and the sealed route transaction ID.  This deliberately
    prevents a generic ``allow dirty`` escape hatch for ordinary package apply.
    """
    context = _route_context(context_value)
    route_root = multi_hop_route_root(target, context["route_transaction_id"])
    if route_root.is_symlink() or is_reparse_point(route_root) or not route_root.is_dir():
        raise ApplyError("multi-hop route transaction directory is missing or unsafe")
    intent, intent_raw = _read_canonical_route_json(
        route_root / "route-intent.json", "multi-hop route intent"
    )
    if (
        intent.get("schema_version") != MULTI_HOP_ROUTE_INTENT_SCHEMA_VERSION
        or intent.get("route_transaction_id") != context["route_transaction_id"]
        or sha256_bytes(intent_raw) != context["route_intent_sha256"]
        or intent.get("target_root") != str(target.resolve())
    ):
        raise ApplyError("multi-hop route intent identity differs")
    sealed_head = intent.get("target_starting_commit")
    if not isinstance(sealed_head, str) or not re.fullmatch(r"[0-9a-f]{40}", sealed_head):
        raise ApplyError("multi-hop route intent target HEAD is invalid")
    current_head = target_git_head(target)
    if current_head != sealed_head:
        raise ApplyError("target HEAD changed after multi-hop route planning")
    matrix = intent.get("matrix")
    if (
        not isinstance(matrix, dict)
        or set(matrix) != {"path", "sha256", "byte_length"}
        or matrix.get("path") != "route-matrix.yaml"
        or type(matrix.get("byte_length")) is not int
        or matrix["byte_length"] < 0
    ):
        raise ApplyError("multi-hop route matrix identity is invalid")
    require_sha256(matrix.get("sha256"), "multi-hop route matrix SHA-256")
    matrix_raw = _read_route_regular_bytes(route_root / matrix["path"], "multi-hop route matrix")
    if len(matrix_raw) != matrix["byte_length"] or sha256_bytes(matrix_raw) != matrix["sha256"]:
        raise ApplyError("multi-hop route matrix bytes differ")
    route = intent.get("route")
    if not isinstance(route, dict) or set(route) != {"route_id", "edges"}:
        raise ApplyError("multi-hop route identity is invalid")
    if not isinstance(route.get("route_id"), str) or not route["route_id"]:
        raise ApplyError("multi-hop route ID is invalid")
    edges_value = route.get("edges")
    if not isinstance(edges_value, list) or len(edges_value) < 2:
        raise ApplyError("multi-hop route edges are invalid")
    edges = [_route_edge_identity(item, "multi-hop route edge") for item in edges_value]
    if [item["order"] for item in edges] != list(range(1, len(edges) + 1)):
        raise ApplyError("multi-hop route edge order is invalid")
    if context["next_hop_index"] >= len(edges):
        raise ApplyError("multi-hop checkpoint context exceeds route edge count")
    expected_edge = edges[context["next_hop_index"]]
    if {
        "edge_id": context["edge_id"],
        "order": context["edge_order"],
        "from_version": context["from_version"],
        "to_version": context["to_version"],
    } != {
        key: expected_edge[key]
        for key in ("edge_id", "order", "from_version", "to_version")
    }:
        raise ApplyError("multi-hop checkpoint context next edge differs")
    if context["schema_version"] == MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION:
        journal, _journal_raw = _read_deterministic_route_yaml(
            route_root / "journal.yaml", "multi-hop route journal"
        )
        if (
            journal.get("schema_version") != MULTI_HOP_ROUTE_JOURNAL_SCHEMA_VERSION
            or journal.get("route_transaction_id") != context["route_transaction_id"]
            or journal.get("route_intent_sha256") != context["route_intent_sha256"]
            or journal.get("state") not in allowed_route_states
            or journal.get("next_hop_index") != 0
            or journal.get("last_checkpoint_index") is not None
            or journal.get("last_checkpoint_sha256") is not None
        ):
            raise ApplyError("multi-hop initial route journal state differs")
        current_surface = route_checkpoint_surface(target)
        allowed = allowed_mutations or set()
        for relative in allowed:
            safe_path(relative, "multi-hop active mutation path")
        unexpected = set(current_surface) - allowed
        if unexpected:
            raise ApplyError(
                f"unrelated target changes block multi-hop initial route: {sorted(unexpected)}"
            )
        return context, {}, journal
    checkpoint_path = route_root / "checkpoints" / f"{context['checkpoint_index']:04d}.json"
    checkpoint, checkpoint_raw = _read_canonical_route_json(
        checkpoint_path, "multi-hop route checkpoint"
    )
    if sha256_bytes(checkpoint_raw) != context["checkpoint_sha256"]:
        raise ApplyError("multi-hop route checkpoint bytes differ")
    unsigned_checkpoint = deepcopy(checkpoint)
    checkpoint_digest = unsigned_checkpoint.pop("digest", None)
    if checkpoint_digest != canonical_digest(unsigned_checkpoint):
        raise ApplyError("multi-hop route checkpoint digest is invalid")
    if (
        checkpoint.get("schema_version") != MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA_VERSION
        or checkpoint.get("route_transaction_id") != context["route_transaction_id"]
        or checkpoint.get("route_intent_sha256") != context["route_intent_sha256"]
        or checkpoint.get("checkpoint_index") != context["checkpoint_index"]
        or checkpoint.get("predecessor_checkpoint_sha256")
        != context["checkpoint_predecessor_sha256"]
    ):
        raise ApplyError("multi-hop route checkpoint identity differs")
    checkpoint_edge = _route_edge_identity(
        checkpoint.get("edge"), "multi-hop route checkpoint edge"
    )
    if checkpoint_edge != edges[context["checkpoint_index"]]:
        raise ApplyError("multi-hop route checkpoint edge differs")
    if checkpoint_edge["to_version"] != context["from_version"]:
        raise ApplyError("multi-hop route checkpoint predecessor does not join next edge")
    target_surface = checkpoint.get("target_surface")
    if (
        not isinstance(target_surface, dict)
        or set(target_surface) != {"starting_commit", "paths"}
        or target_surface.get("starting_commit") != sealed_head
        or not isinstance(target_surface.get("paths"), dict)
    ):
        raise ApplyError("multi-hop route checkpoint target surface is invalid")
    expected_surface = target_surface["paths"]
    if any(
        not isinstance(path, str)
        or safe_path(path, "multi-hop checkpoint target path") != path
        or not isinstance(state, dict)
        for path, state in expected_surface.items()
    ):
        raise ApplyError("multi-hop route checkpoint target surface paths are invalid")
    journal, _journal_raw = _read_deterministic_route_yaml(
        route_root / "journal.yaml", "multi-hop route journal"
    )
    if (
        journal.get("schema_version") != MULTI_HOP_ROUTE_JOURNAL_SCHEMA_VERSION
        or journal.get("route_transaction_id") != context["route_transaction_id"]
        or journal.get("route_intent_sha256") != context["route_intent_sha256"]
        or journal.get("state") not in allowed_route_states
        or journal.get("next_hop_index") != context["next_hop_index"]
        or journal.get("last_checkpoint_sha256") != context["checkpoint_sha256"]
    ):
        raise ApplyError("multi-hop route journal checkpoint state differs")
    # Do not admit a canonical-but-empty checkpoint as a dirty-worktree
    # exemption.  A later child may consume only the target validator's full
    # finalized child/receipt/terminal/authority cross-bind.
    _require_complete_multi_hop_checkpoint_evidence(target)
    current_surface = route_checkpoint_surface(target)
    allowed = allowed_mutations or set()
    for relative in allowed:
        safe_path(relative, "multi-hop active mutation path")
    unexpected = set(current_surface) - set(expected_surface) - allowed
    if unexpected:
        raise ApplyError(
            f"unrelated target changes block multi-hop recovery: {sorted(unexpected)}"
        )
    for relative, state in expected_surface.items():
        if relative not in allowed and current_surface.get(relative) != state:
            raise ApplyError(
                f"multi-hop checkpoint target surface changed: {relative}"
            )
    return context, checkpoint, journal


def verify_multi_hop_checkpoint_for_planning(target: Path, context_value: object) -> dict:
    if active_target_git_snapshot(target) is None:
        snapshot = capture_target_git_snapshot(
            target,
            [],
            phase="plan-admission",
            require_clean=False,
        )
        with target_git_snapshot_scope(snapshot):
            return verify_multi_hop_checkpoint_for_planning(target, context_value)
    context = _route_context(context_value)
    context, _checkpoint, _journal = _load_route_checkpoint_context(
        target,
        context,
        allowed_route_states=(
            {"planned"}
            if context["schema_version"] == MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION
            else {"checkpointed"}
        ),
    )
    return context


def verify_multi_hop_checkpoint_for_active_child(
    target: Path,
    context_value: object,
    *,
    allowed_mutations: set[str],
) -> dict:
    context, _checkpoint, _journal = _load_route_checkpoint_context(
        target,
        context_value,
        allowed_route_states={
            "applying",
            "awaiting-target-validation",
            "validating",
            "rolling-back",
        },
        allowed_mutations=allowed_mutations,
    )
    return context


@contextmanager
def transaction_lock(target: Path) -> Iterator[None]:
    base = git_admin_transaction_base(target)
    require_safe_transaction_directory(
        base, "transaction base", allow_missing=True
    )
    base.mkdir(parents=True, exist_ok=True)
    require_safe_transaction_directory(base, "transaction base")
    lock_path = base / "transaction.lock"
    if (
        lock_path.is_symlink()
        or is_reparse_point(lock_path)
        or (lock_path.exists() and not lock_path.is_file())
    ):
        raise ApplyError("transaction lock is unsafe")
    descriptor = -1
    handle = None
    try:
        try:
            descriptor = os.open(
                lock_path,
                os.O_RDWR
                | os.O_CREAT
                | os.O_APPEND
                | getattr(os, "O_BINARY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o600,
            )
        except OSError as exc:
            raise ApplyError("cannot safely open transaction lock") from exc
        if (
            lock_path.is_symlink()
            or is_reparse_point(lock_path)
            or not stat.S_ISREG(os.fstat(descriptor).st_mode)
        ):
            raise ApplyError("transaction lock is unsafe")
        handle = os.fdopen(descriptor, "a+b")
        descriptor = -1
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ApplyError("another AI context package transaction is active") from exc
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ApplyError("another AI context package transaction is active") from exc
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        if handle is not None:
            handle.close()
        elif descriptor >= 0:
            os.close(descriptor)


@contextmanager
def _transaction_lock_scope(target: Path, *, lock_held: bool) -> Iterator[None]:
    """Use the shared child lock once when S2 composes child transitions."""
    if lock_held:
        yield
        return
    with transaction_lock(target):
        yield


def transaction_root(target: Path, transaction_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", transaction_id):
        raise ApplyError("transaction ID must be a lowercase SHA-256")
    return git_admin_transaction_base(target) / transaction_id


def require_safe_transaction_directory(
    path: Path, label: str, *, allow_missing: bool = False
) -> None:
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError(f"{label} is unsafe")
    if path.exists():
        if not path.is_dir():
            raise ApplyError(f"{label} is unsafe")
    elif not allow_missing:
        raise ApplyError(f"{label} is missing")


def require_safe_transaction_root(root: Path, *, allow_missing: bool = False) -> None:
    require_safe_transaction_directory(root.parent, "transaction base")
    require_safe_transaction_directory(
        root, "transaction root", allow_missing=allow_missing
    )


def reject_unfinished_v4_transactions(target: Path) -> None:
    """Block new mutation without offering v4 recovery or conversion."""

    def block_unclassified_legacy_transaction(child: Path, reason: str) -> None:
        raise ApplyError(
            f"{UNSUPPORTED_JOURNAL_VERSION_CLASSIFICATION}: legacy transaction "
            f"{child.name} {reason} and cannot be proven terminal; use prior tooling "
            "that supports journal v4 or perform owner-directed manual recovery"
        )

    base = git_admin_transaction_base(target)
    if not base.is_dir():
        return
    for child in sorted(base.iterdir(), key=lambda item: item.name):
        if not re.fullmatch(r"[0-9a-f]{64}", child.name):
            continue
        require_safe_transaction_root(child)
        journal_path = child / "journal.yaml"
        if (
            journal_path.is_symlink()
            or is_reparse_point(journal_path)
            or (journal_path.exists() and not journal_path.is_file())
        ):
            block_unclassified_legacy_transaction(child, "has unsafe journal evidence")
        if not journal_path.exists():
            block_unclassified_legacy_transaction(child, "has missing journal evidence")
        try:
            journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            block_unclassified_legacy_transaction(child, "has unreadable journal evidence")
        if not isinstance(journal, dict):
            block_unclassified_legacy_transaction(child, "has invalid journal evidence")
        schema_version = journal.get("schema_version")
        if schema_version == JOURNAL_SCHEMA_VERSION:
            continue
        if schema_version != LEGACY_JOURNAL_SCHEMA_VERSION:
            block_unclassified_legacy_transaction(
                child, "has an unsupported journal version"
            )
        state = journal.get("state")
        if state in JOURNAL_TERMINAL_STATES:
            continue
        raise ApplyError(
            f"{UNSUPPORTED_JOURNAL_VERSION_CLASSIFICATION}: unfinished journal v4 "
            f"transaction {child.name} blocks new target mutation; use prior tooling "
            "that supports journal v4 or perform owner-directed manual recovery"
        )


def active_operations(plan: dict) -> list[dict]:
    return [
        item
        for item in plan.get("operations", [])
        if item.get("action") in {"add", "replace", "remove", "rename"}
    ]


def operation_post_state_map(plan: dict) -> dict[str, dict[str, dict]]:
    operations = active_operations(plan)
    records = plan.get("operation_post_states")
    if not isinstance(records, list) or len(records) != len(operations):
        raise ApplyError("apply plan operation post-state evidence is invalid")
    result: dict[str, dict[str, dict]] = {}
    for operation, record in zip(operations, records, strict=True):
        if not isinstance(record, dict) or record.get("operation_id") != operation["id"]:
            raise ApplyError("apply plan operation post-state order is invalid")
        paths = record.get("paths")
        expected_paths = [operation["path"]]
        if operation["action"] == "rename":
            expected_paths.append(operation["from_path"])
        if not isinstance(paths, list) or [
            item.get("path") if isinstance(item, dict) else None for item in paths
        ] != expected_paths:
            raise ApplyError(
                f"apply plan operation post-state paths are invalid: {operation['id']}"
            )
        by_path: dict[str, dict] = {}
        for item in paths:
            state = item.get("state")
            if not isinstance(state, dict) or set(state) != {
                "exists",
                "sha256",
                "mode",
            }:
                raise ApplyError(
                    f"apply plan operation post-state record is invalid: {operation['id']}"
                )
            if state.get("exists") is True:
                if not isinstance(state.get("sha256"), str) or not re.fullmatch(
                    r"[0-9a-f]{64}", state["sha256"]
                ) or state.get("mode") not in {"0644", "0755"}:
                    raise ApplyError(
                        f"apply plan present post-state identity is invalid: {operation['id']}"
                    )
            elif state.get("exists") is not False or state != {
                "exists": False,
                "sha256": None,
                "mode": None,
            }:
                raise ApplyError(
                    f"apply plan absent post-state identity is invalid: {operation['id']}"
                )
            by_path[item["path"]] = state
        result[operation["id"]] = by_path
    return result


def touched_paths(plan: dict) -> list[str]:
    values: set[str] = set()
    for item in active_operations(plan):
        values.add(item["path"])
        if item.get("from_path"):
            values.add(item["from_path"])
    return sorted(values, key=lambda value: value.encode("utf-8"))


def target_staging_records(plan: dict) -> list[dict[str, str]]:
    """Derive the only target-side staging paths authorized for a transaction."""
    transaction_id = transaction_id_for_plan(plan)
    destinations = set(touched_paths(plan)) | {PENDING_RECEIPT_PATH}
    records: list[dict[str, str]] = []
    staging_paths: set[str] = set()
    for destination in sorted(destinations, key=lambda value: value.encode("utf-8")):
        destination = safe_path(destination, "transaction staging destination")
        destination_path = PurePosixPath(destination)
        digest = sha256_bytes(
            f"{transaction_id}\0{destination}".encode("utf-8")
        )
        staging = (
            destination_path.parent / f".ai-context-apply-{digest}.staging"
        ).as_posix()
        if staging in destinations or staging in staging_paths:
            raise ApplyError("transaction staging path collision")
        staging_paths.add(staging)
        records.append({"destination": destination, "path": staging})
    return records


def target_staging_path(target: Path, journal: dict, destination: str) -> Path:
    records = journal.get("target_staging_paths")
    if not isinstance(records, list):
        raise ApplyError("transaction staging path evidence is invalid")
    matches = [
        item.get("path")
        for item in records
        if isinstance(item, dict) and item.get("destination") == destination
    ]
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ApplyError(f"transaction staging path is missing: {destination}")
    staging = matches[0]
    reject_symlink_boundary(target, staging)
    return target / Path(*PurePosixPath(staging).parts)


def require_target_staging_absent(target: Path, records: list[dict[str, str]]) -> None:
    for item in records:
        relative = item["path"]
        reject_symlink_boundary(target, relative)
        path = target / Path(*PurePosixPath(relative).parts)
        if path.exists() or path.is_symlink() or is_reparse_point(path):
            raise ApplyError(f"transaction staging path already exists or is unsafe: {relative}")


def planned_created_parents(target: Path, plan: dict) -> list[str]:
    parents: set[str] = set()
    destinations = [
        item["path"]
        for item in active_operations(plan)
        if item["action"] in {"add", "replace", "rename"}
    ]
    destinations.append(PENDING_RECEIPT_PATH)
    for relative in destinations:
        parent = PurePosixPath(relative).parent
        lineage: list[PurePosixPath] = []
        while str(parent) not in {"", "."}:
            lineage.append(parent)
            parent = parent.parent
        for candidate in reversed(lineage):
            native = target / Path(*candidate.parts)
            if not native.exists():
                parents.add(candidate.as_posix())
            elif native.is_symlink() or is_reparse_point(native) or not native.is_dir():
                raise ApplyError(f"target parent boundary is unsafe: {candidate.as_posix()}")
    return sorted(parents, key=lambda value: (len(PurePosixPath(value).parts), value.encode("utf-8")))


def protected_target_paths(target: Path) -> list[str]:
    fixed = {
        ".dev/AI-CONTEXT-SOURCE.yaml",
        TARGET_VALIDATION_PROFILE_PATH,
        ".dev/ai-context/provenance.yaml",
        ".dev/ai-context/customizations.yaml",
        ".dev/ai-context/effective-rules.yaml",
    }
    packet_root = target / TARGET_EFFECTIVE_PACKET_DIRECTORY
    if packet_root.exists():
        if packet_root.is_symlink() or is_reparse_point(packet_root) or not packet_root.is_dir():
            raise ApplyError(f"target-owned packet boundary is unsafe: {TARGET_EFFECTIVE_PACKET_DIRECTORY}")
        for candidate in packet_root.rglob("*"):
            if candidate.is_symlink() or is_reparse_point(candidate):
                raise ApplyError(
                    f"target-owned packet boundary is unsafe: {candidate.relative_to(target).as_posix()}"
                )
            if candidate.is_file():
                fixed.add(candidate.relative_to(target).as_posix())
    return sorted(
        (path for path in fixed if (target / Path(*PurePosixPath(path).parts)).exists()),
        key=lambda value: value.encode("utf-8"),
    )


def preflight_writable(target: Path, plan: dict) -> None:
    for relative in touched_paths(plan):
        reject_symlink_boundary(target, relative)
        path = target / Path(*PurePosixPath(relative).parts)
        if path.exists() and not path.is_file():
            raise ApplyError(f"target path must be a regular file: {relative}")
        if path.exists() and not (path.stat().st_mode & stat.S_IWRITE):
            raise ApplyError(f"target path is read-only: {relative}")
    planned_created_parents(target, plan)
    require_target_staging_absent(target, target_staging_records(plan))


def verify_route_child_admission(
    target: Path, plan: dict, *, route_operation_authorized: bool
) -> None:
    context = route_checkpoint_context(plan)
    if context is None:
        if clean_target_head(target) != plan.get("target_starting_commit"):
            raise ApplyError("target HEAD changed during transaction preparation")
        return
    if not route_operation_authorized:
        raise ApplyError(
            "multi-hop child plans may be applied only by the sealed route orchestrator"
        )
    verify_multi_hop_checkpoint_for_active_child(
        target,
        context,
        allowed_mutations=set(),
    )


def verify_preparation_admission(
    target: Path, plan: dict, *, route_operation_authorized: bool = False
) -> None:
    verify_route_child_admission(
        target, plan, route_operation_authorized=route_operation_authorized
    )
    if target_git_head(target) != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed during transaction preparation")
    current_observed = observation(plan.get("observed", {}).keys(), target)
    if current_observed != plan.get("observed"):
        raise ApplyError("target file state changed during transaction preparation")
    if is_upgrade_plan(plan):
        if canonical_digest(current_observed) != plan.get(
            "target_observed_prestate_sha256"
        ):
            raise ApplyError("target observed pre-state digest changed during transaction preparation")
        if target_validation_profile(target) != plan.get("target_validation_profile"):
            raise ApplyError("target validation profile changed during transaction preparation")
        if target_file_identity(
            target, ".dev/ai-context/provenance.yaml"
        ) != plan.get("target_provenance"):
            raise ApplyError("target provenance changed during transaction preparation")
        if target_file_identity(
            target, ".dev/ai-context/customizations.yaml"
        ) != plan.get("target_semantic_customizations"):
            raise ApplyError("target semantic customizations changed during transaction preparation")
    require_target_staging_absent(target, target_staging_records(plan))


def verify_package_binding(plan: dict, package_root: Path) -> tuple[dict, dict[str, dict], dict, str]:
    package, incoming, migration, manifest_sha = validate_package_root(package_root)
    if manifest_sha != plan.get("package_manifest_sha256"):
        raise ApplyError("package manifest changed after planning")
    if sha256_bytes((package_root / "metadata/migration.yaml").read_bytes()) != plan.get(
        "migration_sha256"
    ):
        raise ApplyError("migration contract changed after planning")
    if selected_input_proof_identity(package) != plan.get("package_selected_input_proof"):
        raise ApplyError("package selected-input proof changed after planning")
    if is_upgrade_plan(plan):
        validation = incoming_package_validation(package_root, package)
        if validation != plan.get("incoming_package_validation"):
            raise ApplyError("incoming package validation evidence changed after planning")
    return package, incoming, migration, manifest_sha


def verify_plan_for_apply(
    plan: dict,
    acknowledgements: set[str],
    *,
    require_write_authority: bool = True,
    route_operation_authorized: bool = False,
) -> tuple[dict, dict[str, dict], str, set[str]]:
    if plan.get("schema_version") != APPLY_PLAN_SCHEMA_VERSION:
        raise ApplyError("unsupported apply plan schema")
    plan_digest(plan)
    target = Path(plan["target_root"])
    package_root = Path(plan["package_root"])
    package, incoming, _migration, manifest_sha = verify_package_binding(plan, package_root)
    verify_route_child_admission(
        target, plan, route_operation_authorized=route_operation_authorized
    )
    if target_git_head(target) != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed after planning")
    verify_planned_target_git_semantics(target, plan)
    previous_files_value = plan.get("previous_files")
    previous_files = Path(previous_files_value) if previous_files_value else None
    resolved_selection, selection_resolution = resolve_effective_selection(
        package,
        target,
        previous_files,
        plan.get("selection_request", {}).get("enable_providers", []),
    )
    if resolved_selection != plan.get("selection") or selection_resolution != plan.get(
        "selection_resolution"
    ):
        raise ApplyError("selection authority changed after planning")
    incoming = filter_component_records(incoming, enabled_components(resolved_selection))
    required_paths = required_framework_paths(incoming)
    if required_paths != plan.get("required_framework_paths"):
        raise ApplyError("required framework-managed path identity changed after planning")
    operation_post_states = expected_operation_post_states(
        plan.get("operations", []), incoming
    )
    if operation_post_states != plan.get("operation_post_states"):
        raise ApplyError("active operation post-state identity changed after planning")
    current_ignored = ignored_framework_paths(target, required_paths)
    if current_ignored != plan.get("ignored_framework_paths"):
        raise ApplyError("target Git ignore rules changed after planning")
    if current_ignored and require_write_authority:
        paths = [item["path"] for item in current_ignored]
        raise ApplyError(
            "unresolved target Git ignore rules for selected framework-managed paths: "
            f"{paths}; owner must choose a recorded disposition before apply"
        )
    current_observed = observation(plan.get("observed", {}).keys(), target)
    if current_observed != plan.get("observed"):
        raise ApplyError("target file state changed after planning")
    if is_upgrade_plan(plan):
        if canonical_digest(current_observed) != plan.get(
            "target_observed_prestate_sha256"
        ):
            raise ApplyError("target observed pre-state digest changed after planning")
        if target_validation_profile(target) != plan.get("target_validation_profile"):
            raise ApplyError("target validation profile changed after planning")
        if target_file_identity(
            target, ".dev/ai-context/provenance.yaml"
        ) != plan.get("target_provenance"):
            raise ApplyError("target provenance changed after planning")
        if target_file_identity(
            target, ".dev/ai-context/customizations.yaml"
        ) != plan.get("target_semantic_customizations"):
            raise ApplyError("target semantic customizations changed after planning")
    conflicts = plan.get("managed_state_conflicts")
    if not isinstance(conflicts, list):
        raise ApplyError("apply plan managed-state conflicts are invalid")
    if conflicts and require_write_authority:
        raise ApplyError(
            "selected unchanged framework-managed paths require reconciliation: "
            f"{[item.get('path') for item in conflicts]}"
        )
    reconciles = {item["id"] for item in plan["operations"] if item["action"] == "reconcile"}
    if require_write_authority:
        unknown = acknowledgements - reconciles
        if unknown:
            raise ApplyError(f"acknowledgements do not match reconciliation IDs: {sorted(unknown)}")
        missing = reconciles - acknowledgements
        if missing:
            raise ApplyError(f"unacknowledged reconciliation items: {sorted(missing)}")
    receipt_path = target / PENDING_RECEIPT_PATH
    if receipt_path.exists() or receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError(f"pending receipt already exists: {PENDING_RECEIPT_PATH}")
    if require_write_authority:
        preflight_writable(target, plan)
    return package, incoming, manifest_sha, reconciles


def prepare_transaction(
    target: Path,
    plan: dict,
    acknowledgements: set[str],
    remediation: tuple[dict, dict] | None = None,
    hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    route_operation_authorized: bool = False,
) -> tuple[Path, dict]:
    transaction_id = transaction_id_for_plan(plan)
    verify_preparation_admission(
        target, plan, route_operation_authorized=route_operation_authorized
    )
    root = transaction_root(target, transaction_id)
    require_safe_transaction_root(root, allow_missing=True)
    if root.exists():
        raise ApplyError(
            f"transaction evidence already exists; resume or roll back {transaction_id}"
        )
    base = root.parent
    preparation = Path(
        tempfile.mkdtemp(prefix=f".{transaction_id}.preparing-", dir=base)
    )
    try:
        invoke_boundary(
            hook, "after_preparation_root", {"transaction_id": transaction_id}
        )
        (preparation / "prestate").mkdir()
        plan_bytes = json.dumps(
            plan,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8") + b"\n"
        atomic_write_bytes(preparation / "plan.json", plan_bytes)
        invoke_boundary(hook, "after_preparation_plan", {"transaction_id": transaction_id})
        remediation_bindings = {
            "remediation_packet_path": None,
            "remediation_packet_sha256": None,
            "remediation_report_path": None,
            "remediation_report_sha256": None,
            "remediation_decision_path": None,
            "remediation_decision_sha256": None,
            "incoming_validation_receipt_path": None,
            "incoming_validation_receipt_sha256": None,
            "target_validation_receipt_path": None,
            "target_validation_receipt_sha256": None,
            "target_observed_prestate_sha256": None,
        }
        initial_state = "planned"
        if remediation is not None:
            packet, decision = remediation
            if (
                packet.get("transaction_id") != transaction_id
                or packet.get("plan_sha256") != transaction_id
            ):
                raise ApplyError("upgrade remediation packet transaction identity differs")
            sealed_decision = validate_upgrade_remediation_decision(decision, packet)
            packet_bytes = canonical_json_bytes(packet)
            report_bytes = render_upgrade_remediation_report(packet).encode("utf-8")
            decision_bytes = canonical_json_bytes(sealed_decision)
            incoming_receipt_bytes = canonical_json_bytes(
                build_incoming_validation_receipt(packet)
            )
            atomic_write_bytes(preparation / REMEDIATION_PACKET_PATH, packet_bytes)
            atomic_write_bytes(preparation / REMEDIATION_REPORT_PATH, report_bytes)
            atomic_write_bytes(preparation / REMEDIATION_DECISION_PATH, decision_bytes)
            atomic_write_bytes(
                preparation / INCOMING_VALIDATION_RECEIPT_PATH,
                incoming_receipt_bytes,
            )
            remediation_bindings = {
                "remediation_packet_path": REMEDIATION_PACKET_PATH,
                "remediation_packet_sha256": sha256_bytes(packet_bytes),
                "remediation_report_path": REMEDIATION_REPORT_PATH,
                "remediation_report_sha256": sha256_bytes(report_bytes),
                "remediation_decision_path": REMEDIATION_DECISION_PATH,
                "remediation_decision_sha256": sha256_bytes(decision_bytes),
                "incoming_validation_receipt_path": INCOMING_VALIDATION_RECEIPT_PATH,
                "incoming_validation_receipt_sha256": sha256_bytes(
                    incoming_receipt_bytes
                ),
                "target_validation_receipt_path": (
                    TARGET_VALIDATION_RECEIPT_PATH
                    if sealed_decision["status"] == "approved"
                    else None
                ),
                "target_validation_receipt_sha256": None,
                "target_observed_prestate_sha256": packet["target"][
                    "observed_prestate_sha256"
                ],
            }
            initial_state = (
                "rejected" if sealed_decision["status"] == "rejected" else "planned"
            )
            invoke_boundary(
                hook,
                "after_remediation_artifacts",
                {"transaction_id": transaction_id},
            )
        pre_state: list[dict] = []
        for index, relative in enumerate(touched_paths(plan)):
            state = file_state(target, relative)
            recorded_state = state_record(state)
            if recorded_state != plan.get("observed", {}).get(relative):
                raise ApplyError(
                    f"target file state changed during transaction preparation: {relative}"
                )
            backup_path = None
            backup_sha = None
            if state.exists:
                content = (target / Path(*PurePosixPath(relative).parts)).read_bytes()
                if sha256_bytes(content) != state.sha256:
                    raise ApplyError(
                        f"target file changed while transaction backup was captured: {relative}"
                    )
                backup_name = (
                    f"{index:04d}-{sha256_bytes(relative.encode('utf-8'))}.bin"
                )
                backup = preparation / "prestate" / backup_name
                atomic_write_bytes(backup, content, mode_int(state.mode or "0644"))
                backup_path = f"prestate/{backup_name}"
                backup_sha = sha256_bytes(content)
            pre_state.append(
                {
                    "path": relative,
                    "state": recorded_state,
                    "backup_path": backup_path,
                    "backup_sha256": backup_sha,
                }
            )
            invoke_boundary(
                hook,
                "after_preparation_backup",
                {"transaction_id": transaction_id, "index": index, "path": relative},
            )
        journal = {
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "state": initial_state,
            "transition_sequence": 0,
            "plan_sha256": plan["plan_sha256"],
            "operation_order_sha256": canonical_digest(
                [item["id"] for item in active_operations(plan)]
            ),
            "next_apply_index": 0,
            "completed_operation_ids": [],
            "rollback_next_index": 0,
            "rollback_completed_paths": [],
            "rollback_start_state": None,
            "progress_log_path": JOURNAL_PROGRESS_PATH,
            "progress_record_count": 0,
            "progress_tail_sha256": None,
            "acknowledgements": sorted(acknowledgements),
            "pre_state": pre_state,
            "protected_state": observation(protected_target_paths(target), target),
            "planned_created_parents": planned_created_parents(target, plan),
            "target_staging_paths": target_staging_records(plan),
            "last_error": None,
            "final_receipt_sha256": None,
            "terminal_receipt_path": None,
            "terminal_receipt_sha256": None,
            **remediation_bindings,
        }
        context = route_checkpoint_context(plan)
        if context is not None:
            journal[MULTI_HOP_ROUTE_CONTEXT_KEY] = context
        verify_preparation_admission(
            target, plan, route_operation_authorized=route_operation_authorized
        )
        journal_path = preparation / "journal.yaml"
        journal_bytes = atomic_write_yaml(journal_path, journal)
        observe_journal_io(
            journal_io_hook,
            kind="snapshot",
            path=journal_path,
            bytes_written=len(journal_bytes),
        )
        fsync_directory(preparation)
        invoke_boundary(
            hook, "after_preparation_journal", {"transaction_id": transaction_id}
        )
        verify_preparation_admission(
            target, plan, route_operation_authorized=route_operation_authorized
        )
        require_safe_transaction_root(root, allow_missing=True)
        if root.exists():
            raise ApplyError(
                f"transaction evidence already exists; resume or roll back {transaction_id}"
            )
        atomic_replace(preparation, root)
        require_safe_transaction_root(root)
        fsync_directory(base)
        return root, journal
    except Exception:
        if preparation.exists():
            shutil.rmtree(preparation)
            fsync_directory(base)
        raise


def expected_v5_transition_sequence(plan: dict, journal: dict) -> int | None:
    """Return the semantic v5 transition position, not its write-attempt count."""
    if journal.get("schema_version") != JOURNAL_SCHEMA_VERSION:
        return None
    state = journal.get("state")
    if state in {"planned", "rejected"}:
        return 0
    next_index = journal.get("next_apply_index")
    if state in {"applying", "interrupted"}:
        return next_index + 1 if type(next_index) is int and next_index >= 0 else None
    operation_count = len(active_operations(plan))
    if state == "awaiting-target-validation":
        return operation_count + 2
    if state == "validated":
        return operation_count + 3
    if state == "finalized":
        return operation_count + (4 if is_upgrade_plan(plan) else 2)
    return None


def persist_journal(
    root: Path,
    plan: dict,
    journal: dict,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> None:
    require_safe_transaction_root(root)
    expected_sequence = expected_v5_transition_sequence(plan, journal)
    journal["transition_sequence"] = (
        expected_sequence
        if expected_sequence is not None
        else int(journal.get("transition_sequence", 0)) + 1
    )
    journal_path = root / "journal.yaml"
    content = atomic_write_yaml(journal_path, journal)
    observe_journal_io(
        journal_io_hook,
        kind="snapshot",
        path=journal_path,
        bytes_written=len(content),
    )


def progress_log_path(root: Path, journal: dict) -> Path:
    if journal.get("progress_log_path") != JOURNAL_PROGRESS_PATH:
        raise ApplyError("transaction journal progress log path is invalid")
    return root / JOURNAL_PROGRESS_PATH


def load_progress_records(root: Path, journal: dict) -> tuple[list[dict], bool]:
    require_safe_transaction_root(root)
    path = progress_log_path(root, journal)
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError("transaction journal progress log is unsafe")
    if not path.exists():
        return [], False
    if not path.is_file():
        raise ApplyError("transaction journal progress log is unsafe")
    raw = path.read_bytes()
    trailing_partial = bool(raw) and not raw.endswith(b"\n")
    framed = raw[: raw.rfind(b"\n") + 1] if trailing_partial else raw
    records: list[dict] = []
    previous_digest: str | None = None
    for sequence, line in enumerate(framed.splitlines(keepends=True), start=1):
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ApplyError("transaction journal progress log cannot be parsed") from exc
        if not isinstance(record, dict) or canonical_json_bytes(record) != line:
            raise ApplyError("transaction journal progress record is not canonical JSON")
        phase = record.get("phase")
        common = {
            "schema_version",
            "sequence",
            "phase",
            "previous_record_sha256",
            "transition_sequence",
            "record_sha256",
        }
        expected_keys = (
            common | {"operation_index", "operation_id"}
            if phase == "apply"
            else common | {"rollback_index", "path"}
            if phase == "rollback"
            else set()
        )
        if (
            not expected_keys
            or set(record) != expected_keys
            or record.get("schema_version") != JOURNAL_PROGRESS_SCHEMA_VERSION
            or type(record.get("sequence")) is not int
            or record.get("sequence") != sequence
            or record.get("previous_record_sha256") != previous_digest
            or type(record.get("transition_sequence")) is not int
            or record["transition_sequence"] < 0
            or (
                phase == "apply"
                and (
                    type(record.get("operation_index")) is not int
                    or not isinstance(record.get("operation_id"), str)
                )
            )
            or (
                phase == "rollback"
                and (
                    type(record.get("rollback_index")) is not int
                    or not isinstance(record.get("path"), str)
                )
            )
        ):
            raise ApplyError("transaction journal progress record is invalid")
        unsigned = dict(record)
        declared_digest = unsigned.pop("record_sha256", None)
        if (
            not isinstance(declared_digest, str)
            or canonical_digest(unsigned) != declared_digest
        ):
            raise ApplyError("transaction journal progress record digest is invalid")
        previous_digest = declared_digest
        records.append(record)
    return records, trailing_partial


def progress_prefixes(
    plan: dict, journal: dict, records: list[dict]
) -> tuple[list[str], list[str]]:
    operations = active_operations(plan)
    rollback_paths = [item["path"] for item in reversed(journal["pre_state"])]
    completed_operations: list[str] = []
    completed_rollback_paths: list[str] = []
    rollback_started = False
    previous_transition = 0
    for record in records:
        transition = record["transition_sequence"]
        if transition <= previous_transition:
            raise ApplyError("transaction journal progress transition is not monotonic")
        previous_transition = transition
        if record["phase"] == "apply":
            index = len(completed_operations)
            if (
                rollback_started
                or index >= len(operations)
                or record.get("operation_index") != index
                or record.get("operation_id") != operations[index]["id"]
                or transition != index + 2
            ):
                raise ApplyError("transaction journal apply progress is invalid")
            completed_operations.append(operations[index]["id"])
            continue
        rollback_started = True
        index = len(completed_rollback_paths)
        if (
            index >= len(rollback_paths)
            or record.get("rollback_index") != index
            or record.get("path") != rollback_paths[index]
        ):
            raise ApplyError("transaction journal rollback progress is invalid")
        completed_rollback_paths.append(rollback_paths[index])
    return completed_operations, completed_rollback_paths


def replay_journal_progress(root: Path, plan: dict, snapshot: dict) -> dict:
    records, _trailing_partial = load_progress_records(root, snapshot)
    compacted_count = snapshot.get("progress_record_count")
    if type(compacted_count) is not int or not 0 <= compacted_count <= len(records):
        raise ApplyError("transaction journal progress record count is invalid")
    compacted_tail = snapshot.get("progress_tail_sha256")
    expected_tail = (
        records[compacted_count - 1]["record_sha256"] if compacted_count else None
    )
    if compacted_tail != expected_tail:
        raise ApplyError("transaction journal progress tail binding is invalid")
    compacted_apply, compacted_rollback = progress_prefixes(
        plan, snapshot, records[:compacted_count]
    )
    if (
        snapshot.get("completed_operation_ids") != compacted_apply
        or snapshot.get("next_apply_index") != len(compacted_apply)
        or snapshot.get("rollback_completed_paths") != compacted_rollback
        or snapshot.get("rollback_next_index") != len(compacted_rollback)
    ):
        raise ApplyError("transaction journal snapshot progress differs from its log")
    effective = deepcopy(snapshot)
    for record in records[compacted_count:]:
        if record["phase"] == "apply":
            if effective.get("state") not in {"applying", "interrupted"}:
                raise ApplyError("transaction journal apply progress follows an invalid state")
            effective["completed_operation_ids"].append(record["operation_id"])
            effective["next_apply_index"] += 1
        else:
            if effective.get("state") != "rolling-back":
                raise ApplyError("transaction journal rollback progress follows an invalid state")
            effective["rollback_completed_paths"].append(record["path"])
            effective["rollback_next_index"] += 1
        effective["transition_sequence"] = record["transition_sequence"]
        effective["progress_record_count"] = record["sequence"]
        effective["progress_tail_sha256"] = record["record_sha256"]
    progress_prefixes(plan, effective, records)
    return effective


def truncate_incomplete_progress_tail(root: Path, journal: dict) -> None:
    require_safe_transaction_root(root)
    path = progress_log_path(root, journal)
    if path.is_symlink() or is_reparse_point(path):
        raise ApplyError("transaction journal progress log is unsafe")
    if not path.exists():
        return
    if not path.is_file():
        raise ApplyError("transaction journal progress log is unsafe")
    raw = path.read_bytes()
    if not raw or raw.endswith(b"\n"):
        return
    valid_length = raw.rfind(b"\n") + 1
    try:
        descriptor = os.open(
            path,
            os.O_RDWR
            | getattr(os, "O_BINARY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise ApplyError(
            f"cannot safely truncate transaction journal progress: {path}"
        ) from exc
    try:
        os.ftruncate(descriptor, valid_length)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def append_progress_record(
    root: Path,
    plan: dict,
    journal: dict,
    *,
    phase: str,
    index: int,
    value: str,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> None:
    records, trailing_partial = load_progress_records(root, journal)
    if trailing_partial:
        truncate_incomplete_progress_tail(root, journal)
    if journal.get("progress_record_count") != len(records):
        raise ApplyError("transaction journal in-memory progress differs from its log")
    sequence = len(records) + 1
    if phase == "apply":
        expected = active_operations(plan)
        if (
            index != journal.get("next_apply_index")
            or index >= len(expected)
            or value != expected[index]["id"]
        ):
            raise ApplyError("transaction journal apply append is out of order")
        transition_sequence = index + 2
        phase_fields = {"operation_index": index, "operation_id": value}
    elif phase == "rollback":
        rollback_paths = [item["path"] for item in reversed(journal["pre_state"])]
        if (
            index != journal.get("rollback_next_index")
            or index >= len(rollback_paths)
            or value != rollback_paths[index]
        ):
            raise ApplyError("transaction journal rollback append is out of order")
        transition_sequence = int(journal["transition_sequence"]) + 1
        phase_fields = {"rollback_index": index, "path": value}
    else:
        raise ApplyError("transaction journal progress phase is invalid")
    record = {
        "schema_version": JOURNAL_PROGRESS_SCHEMA_VERSION,
        "sequence": sequence,
        "phase": phase,
        "previous_record_sha256": journal.get("progress_tail_sha256"),
        "transition_sequence": transition_sequence,
        **phase_fields,
    }
    record["record_sha256"] = canonical_digest(record)
    durable_append_bytes(
        progress_log_path(root, journal),
        canonical_json_bytes(record),
        journal_io_hook,
    )
    if phase == "apply":
        journal["completed_operation_ids"].append(value)
        journal["next_apply_index"] = index + 1
    else:
        journal["rollback_completed_paths"].append(value)
        journal["rollback_next_index"] = index + 1
    journal["transition_sequence"] = transition_sequence
    journal["progress_record_count"] = sequence
    journal["progress_tail_sha256"] = record["record_sha256"]


def exact_state_matches(target: Path, relative: str, expected: dict) -> bool:
    reject_symlink_boundary(target, relative)
    current = file_state(target, relative)
    return (
        current.exists == expected.get("exists")
        and current.sha256 == expected.get("sha256")
        and current.mode == expected.get("mode")
    )


def expected_present_state(record: dict) -> dict:
    return {"exists": True, "sha256": record["sha256"], "mode": record["mode"]}


def prestate_by_path(journal: dict) -> dict[str, dict]:
    return {item["path"]: item for item in journal["pre_state"]}


def validate_journal_progress(plan: dict, journal: dict) -> None:
    operations = active_operations(plan)
    operation_post_state_map(plan)
    expected_staging = target_staging_records(plan)
    if journal.get("target_staging_paths") != expected_staging:
        raise ApplyError("transaction journal staging path evidence is invalid")
    next_index = journal.get("next_apply_index")
    if type(next_index) is not int or not 0 <= next_index <= len(operations):
        raise ApplyError("transaction journal next operation index is invalid")
    completed = journal.get("completed_operation_ids")
    expected_completed = [item["id"] for item in operations[:next_index]]
    if completed != expected_completed:
        raise ApplyError("transaction journal completed operation prefix is invalid")
    progress_record_count = journal.get("progress_record_count")
    progress_tail = journal.get("progress_tail_sha256")
    if (
        journal.get("progress_log_path") != JOURNAL_PROGRESS_PATH
        or type(progress_record_count) is not int
        or progress_record_count < 0
        or (progress_record_count == 0 and progress_tail is not None)
        or (
            progress_record_count > 0
            and (
                not isinstance(progress_tail, str)
                or not re.fullmatch(r"[0-9a-f]{64}", progress_tail)
            )
        )
    ):
        raise ApplyError("transaction journal progress log binding is invalid")
    transition_sequence = journal.get("transition_sequence")
    if type(transition_sequence) is not int or transition_sequence < 0:
        raise ApplyError("transaction journal transition sequence is invalid")
    state = journal.get("state")
    expected_v5_sequence = expected_v5_transition_sequence(plan, journal)
    if (
        journal.get("schema_version") == JOURNAL_SCHEMA_VERSION
        and expected_v5_sequence is not None
        and transition_sequence != expected_v5_sequence
    ):
        raise ApplyError("transaction journal transition sequence is impossible")
    rollback_paths = [
        item.get("path")
        for item in reversed(journal.get("pre_state", []))
        if isinstance(item, dict)
    ]
    rollback_next_index = journal.get("rollback_next_index")
    if (
        type(rollback_next_index) is not int
        or not 0 <= rollback_next_index <= len(rollback_paths)
    ):
        raise ApplyError("transaction journal rollback index is invalid")
    rollback_completed = journal.get("rollback_completed_paths")
    if rollback_completed != rollback_paths[:rollback_next_index]:
        raise ApplyError("transaction journal rollback path prefix is invalid")
    rollback_start_state = journal.get("rollback_start_state")
    if state in {"rolling-back", "rolled-back"}:
        if (
            not isinstance(rollback_start_state, dict)
            or list(sorted(rollback_start_state, key=lambda item: item.encode("utf-8")))
            != touched_paths(plan)
        ):
            raise ApplyError("transaction journal rollback start state is invalid")
        for relative, value in rollback_start_state.items():
            if (
                not isinstance(relative, str)
                or not isinstance(value, dict)
                or set(value)
                != {
                    "exists",
                    "sha256",
                    "mode",
                    "git_sha256",
                    "normalized_text_sha256",
                    "tracked",
                    "dirty",
                    "git_eol_only",
                }
            ):
                raise ApplyError("transaction journal rollback start state is invalid")
    elif (
        rollback_next_index != 0
        or rollback_completed != []
        or rollback_start_state is not None
    ):
        raise ApplyError("non-rollback journal contains rollback progress")
    if state == "rolled-back" and rollback_next_index != len(rollback_paths):
        raise ApplyError("rolled-back transaction journal is incomplete")
    receipt_digest = journal.get("final_receipt_sha256")
    target_receipt_path = journal.get("target_validation_receipt_path")
    target_receipt_digest = journal.get("target_validation_receipt_sha256")
    terminal_path = journal.get("terminal_receipt_path")
    terminal_digest = journal.get("terminal_receipt_sha256")
    if state in {"planned", "rejected"} and next_index != 0:
        raise ApplyError("non-applying transaction journal cannot contain progress")
    completed_apply_states = {
        "awaiting-target-validation",
        "validated",
        "finalized",
    }
    if state in completed_apply_states:
        if next_index != len(operations) or not isinstance(
            receipt_digest, str
        ) or not re.fullmatch(r"[0-9a-f]{64}", receipt_digest):
            raise ApplyError("applied transaction journal is incomplete")
        if journal.get("schema_version") != JOURNAL_SCHEMA_VERSION:
            minimum_sequence = len(operations) + 2
            if is_upgrade_plan(plan):
                minimum_sequence += {
                    "awaiting-target-validation": 0,
                    "validated": 1,
                    "finalized": 2,
                }[state]
            if transition_sequence < minimum_sequence:
                raise ApplyError("applied transaction transition sequence is impossible")
    elif state in {"rolling-back", "rolled-back"} and receipt_digest is not None:
        require_sha256(receipt_digest, "rollback transaction receipt SHA-256")
    elif receipt_digest is not None:
        raise ApplyError("non-applied transaction journal has a receipt identity")
    if not is_upgrade_plan(plan):
        if target_receipt_path is not None or target_receipt_digest is not None:
            raise ApplyError("clean-install transaction has target validation receipt evidence")
    elif state == "rejected":
        if target_receipt_path is not None or target_receipt_digest is not None:
            raise ApplyError("rejected transaction has target validation receipt evidence")
    else:
        if target_receipt_path != TARGET_VALIDATION_RECEIPT_PATH:
            raise ApplyError("upgrade transaction target validation receipt path is invalid")
        if state in {"validated", "finalized"}:
            require_sha256(
                target_receipt_digest,
                "target validation receipt SHA-256",
            )
        elif state in {"rolling-back", "rolled-back"} and target_receipt_digest is not None:
            require_sha256(target_receipt_digest, "rollback target validation receipt SHA-256")
        elif target_receipt_digest is not None:
            raise ApplyError("target validation receipt cannot bind before target validation")
    if (terminal_path is None) != (terminal_digest is None):
        raise ApplyError("terminal receipt journal binding is incomplete")
    if terminal_path is not None:
        safe_path(terminal_path, "terminal receipt path")
        require_sha256(terminal_digest, "terminal receipt SHA-256")
    if is_upgrade_plan(plan):
        if state == "finalized" and terminal_path != "terminal-receipt.json":
            raise ApplyError("finalized upgrade transaction lacks terminal receipt evidence")
        if state != "finalized" and terminal_path is not None:
            raise ApplyError("non-finalized upgrade transaction has terminal receipt evidence")


def read_sealed_transaction_json(root: Path, relative: str, digest: object, label: str) -> dict:
    safe_path(relative, label)
    require_sha256(digest, f"{label} SHA-256")
    path = root / Path(*PurePosixPath(relative).parts)
    if not path.is_file() or path.is_symlink() or is_reparse_point(path):
        raise ApplyError(f"{label} is missing")
    content = path.read_bytes()
    if sha256_bytes(content) != digest:
        raise ApplyError(f"{label} digest differs")
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyError(f"{label} cannot be parsed") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != content:
        raise ApplyError(f"{label} is not canonical JSON")
    return value


def validate_target_validation_receipt(
    receipt: dict,
    plan: dict,
    journal: dict,
    packet: dict,
    decision: dict,
    *,
    require_current_pending_receipt: bool = True,
) -> dict:
    """Validate a separately executed target-validation result without running it."""
    required = {
        "schema_version",
        "transaction_id",
        "plan_sha256",
        "packet_sha256",
        "decision_sha256",
        "target",
        "target_validation_profile",
        "target_validation_profile_digest",
        "pending_receipt",
        "execution",
    }
    if set(receipt) != required:
        raise ApplyError("target validation receipt fields are incomplete or unexpected")
    if receipt.get("schema_version") != TARGET_VALIDATION_RECEIPT_SCHEMA_VERSION:
        raise ApplyError("unsupported target validation receipt schema")
    transaction_id = transaction_id_for_plan(plan)
    if (
        receipt.get("transaction_id") != transaction_id
        or receipt.get("plan_sha256") != transaction_id
        or receipt.get("packet_sha256") != packet_digest(packet)
        or receipt.get("decision_sha256")
        != journal.get("remediation_decision_sha256")
    ):
        raise ApplyError("target validation receipt transaction identity differs")
    packet_target = packet.get("target")
    if not isinstance(packet_target, dict):
        raise ApplyError("target validation receipt packet target is invalid")
    target = receipt.get("target")
    expected_target = {
        "root": packet_target.get("root"),
        "starting_commit": packet_target.get("starting_commit"),
        "observed_prestate_sha256": packet_target.get("observed_prestate_sha256"),
    }
    if target != expected_target:
        raise ApplyError("target validation receipt target identity differs")
    profile = packet.get("target_validation_profile")
    if (
        not isinstance(profile, dict)
        or not isinstance(profile.get("argv"), list)
        or not all(isinstance(item, str) and item for item in profile["argv"])
        or packet.get("target_validation_profile_digest") != canonical_digest(profile)
    ):
        raise ApplyError("target validation receipt packet profile is invalid")
    if (
        not isinstance(profile.get("sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", profile["sha256"])
        or not profile["argv"]
    ):
        raise ApplyError(
            "target validation receipt requires a present executable target validation profile"
        )
    if (
        receipt.get("target_validation_profile") != profile
        or receipt.get("target_validation_profile_digest")
        != packet.get("target_validation_profile_digest")
    ):
        raise ApplyError("target validation receipt profile identity differs")
    pending = receipt.get("pending_receipt")
    if not isinstance(pending, dict) or set(pending) != {"path", "sha256"}:
        raise ApplyError("target validation receipt pending receipt identity is invalid")
    if pending.get("path") != PENDING_RECEIPT_PATH:
        raise ApplyError("target validation receipt pending receipt path differs")
    pending_sha = require_sha256(
        pending.get("sha256"), "target validation receipt pending receipt SHA-256"
    )
    target_root = Path(plan["target_root"])
    pending_matches = journal.get("final_receipt_sha256") == pending_sha
    if require_current_pending_receipt:
        reject_symlink_boundary(target_root, PENDING_RECEIPT_PATH)
        pending_path = target_root / Path(*PurePosixPath(PENDING_RECEIPT_PATH).parts)
        pending_matches = (
            pending_matches
            and pending_path.is_file()
            and not pending_path.is_symlink()
            and not is_reparse_point(pending_path)
            and sha256_bytes(pending_path.read_bytes()) == pending_sha
        )
    if not pending_matches:
        raise ApplyError("target validation receipt pending receipt identity differs")
    execution = receipt.get("execution")
    if not isinstance(execution, dict) or set(execution) != {
        "argv",
        "outcome",
        "exit_code",
        "started_at",
        "completed_at",
        "output_sha256",
        "evidence",
    }:
        raise ApplyError("target validation receipt execution evidence is invalid")
    if (
        execution.get("argv") != profile.get("argv")
        or execution.get("outcome") != "passed"
        or execution.get("exit_code") != 0
    ):
        raise ApplyError("target validation receipt does not record a passed profile execution")
    started_at = parse_iso_with_offset(
        execution.get("started_at"), "target validation receipt started_at"
    )
    completed_at = parse_iso_with_offset(
        execution.get("completed_at"), "target validation receipt completed_at"
    )
    if completed_at < started_at:
        raise ApplyError("target validation receipt completed_at precedes started_at")
    output_sha256 = require_sha256(
        execution.get("output_sha256"),
        "target validation receipt execution output SHA-256",
    )
    expected_evidence = (
        f".git/ai-context-package-apply/{transaction_id}/"
        f"{TARGET_VALIDATION_OUTPUT_PATH}"
    )
    if (
        not safe_repo_reference(execution.get("evidence"))
        or execution.get("evidence") != expected_evidence
    ):
        raise ApplyError("target validation receipt execution evidence is invalid")
    evidence_path = (
        transaction_root(target_root, transaction_id)
        / TARGET_VALIDATION_OUTPUT_PATH
    )
    if (
        not evidence_path.is_file()
        or evidence_path.is_symlink()
        or is_reparse_point(evidence_path)
        or sha256_bytes(evidence_path.read_bytes()) != output_sha256
    ):
        raise ApplyError(
            "target validation receipt execution evidence bytes differ from output SHA-256"
        )
    return deepcopy(receipt)


def validate_target_validation_receipt_binding(
    root: Path,
    plan: dict,
    journal: dict,
    packet: dict,
    decision: dict,
    *,
    allow_unbound: bool = False,
    allow_cleared_multi_hop_pending_receipt: bool = False,
) -> dict | None:
    """Verify the target-validation file-to-journal binding for record recovery."""
    if not is_upgrade_plan(plan) or journal.get("state") == "rejected":
        unexpected = root / TARGET_VALIDATION_RECEIPT_PATH
        if unexpected.exists() or unexpected.is_symlink() or is_reparse_point(unexpected):
            raise ApplyError("transaction has an unexpected target validation receipt")
        return None
    relative = journal.get("target_validation_receipt_path")
    digest = journal.get("target_validation_receipt_sha256")
    if relative != TARGET_VALIDATION_RECEIPT_PATH:
        raise ApplyError("target validation receipt journal path is invalid")
    path = root / Path(*PurePosixPath(relative).parts)
    if digest is None:
        if path.exists() or path.is_symlink() or is_reparse_point(path):
            if not allow_unbound:
                raise ApplyError("target validation receipt exists without a journal binding")
            if not path.is_file() or path.is_symlink() or is_reparse_point(path):
                raise ApplyError("unbound target validation receipt is unsafe")
        return None
    receipt = read_sealed_transaction_json(
        root,
        relative,
        digest,
        "target validation receipt",
    )
    return validate_target_validation_receipt(
        receipt,
        plan,
        journal,
        packet,
        decision,
        require_current_pending_receipt=(
            journal.get("state") not in {"rolling-back", "rolled-back"}
            and not allow_cleared_multi_hop_pending_receipt
        ),
    )


def validate_upgrade_remediation_artifacts(
    root: Path,
    plan: dict,
    journal: dict,
    *,
    allow_unbound_target_validation_receipt: bool = False,
    allow_cleared_multi_hop_pending_receipt: bool = False,
) -> tuple[dict, dict] | None:
    binding_keys = (
        "remediation_packet_path",
        "remediation_packet_sha256",
        "remediation_report_path",
        "remediation_report_sha256",
        "remediation_decision_path",
        "remediation_decision_sha256",
        "incoming_validation_receipt_path",
        "incoming_validation_receipt_sha256",
        "target_validation_receipt_path",
        "target_validation_receipt_sha256",
        "target_observed_prestate_sha256",
    )
    if not is_upgrade_plan(plan):
        if any(journal.get(key) is not None for key in binding_keys):
            raise ApplyError("clean-install transaction has unexpected remediation evidence")
        unexpected = root / TARGET_VALIDATION_RECEIPT_PATH
        if unexpected.exists() or unexpected.is_symlink() or is_reparse_point(unexpected):
            raise ApplyError("clean-install transaction has target validation receipt evidence")
        return None
    expected_paths = {
        "remediation_packet_path": REMEDIATION_PACKET_PATH,
        "remediation_report_path": REMEDIATION_REPORT_PATH,
        "remediation_decision_path": REMEDIATION_DECISION_PATH,
        "incoming_validation_receipt_path": INCOMING_VALIDATION_RECEIPT_PATH,
    }
    for key, expected in expected_paths.items():
        if journal.get(key) != expected:
            raise ApplyError("upgrade remediation artifact path is invalid")
    packet = read_sealed_transaction_json(
        root,
        journal["remediation_packet_path"],
        journal["remediation_packet_sha256"],
        "upgrade remediation packet",
    )
    if packet.get("schema_version") != UPGRADE_REMEDIATION_PACKET_SCHEMA_VERSION:
        raise ApplyError("upgrade remediation packet schema is invalid")
    packet_sha = packet_digest(packet)
    transaction_id = transaction_id_for_plan(plan)
    if (
        packet.get("transaction_id") != transaction_id
        or packet.get("plan_sha256") != transaction_id
        or journal.get("target_observed_prestate_sha256")
        != plan.get("target_observed_prestate_sha256")
        or packet.get("target", {}).get("observed_prestate_sha256")
        != plan.get("target_observed_prestate_sha256")
    ):
        raise ApplyError("upgrade remediation packet binding differs")
    report_path = root / REMEDIATION_REPORT_PATH
    report_digest = journal.get("remediation_report_sha256")
    require_sha256(report_digest, "upgrade remediation report SHA-256")
    if not report_path.is_file() or report_path.is_symlink():
        raise ApplyError("upgrade remediation report is missing")
    report_bytes = report_path.read_bytes()
    if (
        sha256_bytes(report_bytes) != report_digest
        or report_bytes != render_upgrade_remediation_report(packet).encode("utf-8")
    ):
        raise ApplyError("upgrade remediation report is not derived from packet")
    decision = read_sealed_transaction_json(
        root,
        journal["remediation_decision_path"],
        journal["remediation_decision_sha256"],
        "upgrade remediation decision",
    )
    decision = validate_upgrade_remediation_decision(decision, packet)
    receipt = read_sealed_transaction_json(
        root,
        journal["incoming_validation_receipt_path"],
        journal["incoming_validation_receipt_sha256"],
        "incoming validation receipt",
    )
    if receipt != build_incoming_validation_receipt(packet):
        raise ApplyError("incoming validation receipt binding differs")
    if receipt.get("packet_sha256") != packet_sha:
        raise ApplyError("incoming validation receipt packet digest differs")
    if journal["state"] == "rejected" and decision.get("status") != "rejected":
        raise ApplyError("rejected transaction lacks a rejected owner decision")
    if journal["state"] != "rejected" and decision.get("status") != "approved":
        raise ApplyError("active upgrade transaction lacks an approved owner decision")
    validate_target_validation_receipt_binding(
        root,
        plan,
        journal,
        packet,
        decision,
        allow_unbound=allow_unbound_target_validation_receipt,
        allow_cleared_multi_hop_pending_receipt=allow_cleared_multi_hop_pending_receipt,
    )
    return packet, decision


def transaction_state_matches(
    target: Path, relative: str, expected: dict
) -> bool:
    if expected.get("exists") is not True:
        return exact_state_matches(target, relative, expected)
    reject_symlink_boundary(target, relative)
    current = file_state(target, relative)
    if not current.exists or current.sha256 != expected.get("sha256"):
        return False
    if current.mode == expected.get("mode"):
        return True
    snapshot = active_target_git_snapshot(target)
    if snapshot is not None:
        return (
            not snapshot.core_filemode
            and current.mode == "0644"
            and expected.get("mode") == "0755"
        )
    filemode = run_git(target, "config", "--bool", "core.filemode")
    if filemode.returncode != 0 or filemode.stdout.strip() not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        filemode.stdout.strip() == "false"
        and current.mode == "0644"
        and expected.get("mode") == "0755"
    )


def states_match(target: Path, states: dict[str, dict]) -> bool:
    return all(
        transaction_state_matches(target, relative, expected)
        for relative, expected in states.items()
    )


def recorded_transaction_state_matches(
    target: Path, current: dict, expected: dict
) -> bool:
    if current.get("exists") != expected.get("exists"):
        return False
    if current.get("sha256") != expected.get("sha256"):
        return False
    if current.get("mode") == expected.get("mode"):
        return True
    snapshot = active_target_git_snapshot(target)
    if snapshot is not None:
        return (
            not snapshot.core_filemode
            and current.get("mode") == "0644"
            and expected.get("mode") == "0755"
        )
    filemode = run_git(target, "config", "--bool", "core.filemode")
    if filemode.returncode != 0 or filemode.stdout.strip() not in {"true", "false"}:
        raise ApplyError("cannot determine target Git core.filemode")
    return (
        expected.get("exists") is True
        and filemode.stdout.strip() == "false"
        and current.get("mode") == "0644"
        and expected.get("mode") == "0755"
    )


def recorded_states_match(
    target: Path, current: dict[str, dict], expected: dict[str, dict]
) -> bool:
    return all(
        relative in current
        and recorded_transaction_state_matches(target, current[relative], state)
        for relative, state in expected.items()
    )


def operation_pre_states(
    operation: dict, prestate: dict[str, dict]
) -> dict[str, dict]:
    paths = [operation["path"]]
    if operation["action"] == "rename":
        paths.append(operation["from_path"])
    return {relative: prestate[relative]["state"] for relative in paths}


def current_operation_state_matches(
    target: Path,
    operation: dict,
    pre_states: dict[str, dict],
    post_states: dict[str, dict],
) -> bool:
    if states_match(target, pre_states) or states_match(target, post_states):
        return True
    if operation["action"] != "rename":
        return False
    intermediate = {
        operation["path"]: post_states[operation["path"]],
        operation["from_path"]: pre_states[operation["from_path"]],
    }
    return states_match(target, intermediate)


def validate_transaction_surface(target: Path, plan: dict, journal: dict) -> None:
    validate_journal_progress(plan, journal)
    if journal["state"] in {"rolling-back", "rolled-back"}:
        validate_rollback_start_surface(target, plan, journal)
        validate_rollback_surface(target, journal)
        return
    operations = active_operations(plan)
    prestate = prestate_by_path(journal)
    poststate = operation_post_state_map(plan)
    state = journal["state"]
    next_index = journal["next_apply_index"]
    for index, operation in enumerate(operations):
        before = operation_pre_states(operation, prestate)
        after = poststate[operation["id"]]
        if state in {"planned", "rolled-back", "rejected"}:
            matches = states_match(target, before)
        elif state == "finalized" or index < next_index:
            matches = states_match(target, after)
        elif index == next_index:
            matches = current_operation_state_matches(
                target, operation, before, after
            )
        else:
            matches = states_match(target, before)
        if not matches:
            raise ApplyError(
                f"target state does not match transaction progress: {operation['id']}"
            )


def validate_rollback_surface(target: Path, journal: dict) -> None:
    prestate = prestate_by_path(journal)
    start_state = journal["rollback_start_state"]
    rollback_paths = [item["path"] for item in reversed(journal["pre_state"])]
    next_index = journal["rollback_next_index"]
    for index, relative in enumerate(rollback_paths):
        before = prestate[relative]["state"]
        started = start_state[relative]
        if journal["state"] == "rolled-back" or index < next_index:
            matches = exact_state_matches(target, relative, before)
        elif index == next_index:
            matches = exact_state_matches(
                target, relative, started
            ) or exact_state_matches(target, relative, before)
        else:
            matches = exact_state_matches(target, relative, started)
        if not matches:
            raise ApplyError(
                f"target state does not match rollback progress: {relative}"
            )


def validate_rollback_start_surface(
    target: Path, plan: dict, journal: dict
) -> None:
    operations = active_operations(plan)
    prestate = prestate_by_path(journal)
    poststate = operation_post_state_map(plan)
    start_state = journal["rollback_start_state"]
    next_index = journal["next_apply_index"]
    for index, operation in enumerate(operations):
        before = operation_pre_states(operation, prestate)
        after = poststate[operation["id"]]
        if index < next_index:
            matches = recorded_states_match(target, start_state, after)
        elif index > next_index:
            matches = recorded_states_match(target, start_state, before)
        elif recorded_states_match(target, start_state, before) or recorded_states_match(
            target, start_state, after
        ):
            matches = True
        elif operation["action"] == "rename":
            intermediate = {
                operation["path"]: after[operation["path"]],
                operation["from_path"]: before[operation["from_path"]],
            }
            matches = recorded_states_match(target, start_state, intermediate)
        else:
            matches = False
        if not matches:
            raise ApplyError(
                f"rollback start state does not match transaction progress: {operation['id']}"
            )


def invoke_boundary(
    hook: Callable[[str, dict], None] | None, name: str, details: dict
) -> None:
    if hook is not None:
        hook(name, details)


def execute_operation(
    root: Path,
    package_root: Path,
    target: Path,
    incoming: dict[str, dict],
    journal: dict,
    operation: dict,
    index: int,
    prestate: dict[str, dict],
    hook: Callable[[str, dict], None] | None,
) -> None:
    action = operation["action"]
    relative = operation["path"]
    expected = expected_present_state(incoming[relative]) if action in {"add", "replace", "rename"} else None
    if action in {"add", "replace"}:
        if exact_state_matches(target, relative, expected):
            return
        if not exact_state_matches(target, relative, prestate[relative]["state"]):
            raise ApplyError(f"ambiguous transaction state for {relative}")
        write_payload(
            package_root,
            target,
            relative,
            incoming[relative],
            journal,
            hook,
            {"index": index, "operation_id": operation["id"]},
        )
        invoke_boundary(hook, "after_destination_replace", {"index": index, "operation_id": operation["id"]})
        return
    if action == "remove":
        if exact_state_matches(target, relative, {"exists": False, "sha256": None, "mode": None}):
            return
        if not exact_state_matches(target, relative, prestate[relative]["state"]):
            raise ApplyError(f"ambiguous transaction state for {relative}")
        durable_unlink(target / Path(*PurePosixPath(relative).parts), root)
        invoke_boundary(hook, "after_source_remove", {"index": index, "operation_id": operation["id"]})
        return
    if action == "rename":
        source_relative = operation["from_path"]
        source_pre = prestate[source_relative]["state"]
        destination_pre = prestate[relative]["state"]
        source_absent = {"exists": False, "sha256": None, "mode": None}
        source_is_pre = exact_state_matches(target, source_relative, source_pre)
        source_is_absent = exact_state_matches(target, source_relative, source_absent)
        destination_is_pre = exact_state_matches(target, relative, destination_pre)
        destination_is_post = exact_state_matches(target, relative, expected)
        if source_is_absent and destination_is_post:
            return
        if not source_is_pre or not (destination_is_pre or destination_is_post):
            raise ApplyError(f"ambiguous rename transaction state for {source_relative} -> {relative}")
        if destination_is_pre:
            write_payload(
                package_root,
                target,
                relative,
                incoming[relative],
                journal,
                hook,
                {"index": index, "operation_id": operation["id"]},
            )
            invoke_boundary(hook, "after_destination_replace", {"index": index, "operation_id": operation["id"]})
        durable_unlink(target / Path(*PurePosixPath(source_relative).parts), root)
        invoke_boundary(hook, "after_source_remove", {"index": index, "operation_id": operation["id"]})
        return
    raise ApplyError(f"unsupported active operation action: {action}")


def verify_protected_state(target: Path, journal: dict) -> None:
    current = observation(journal.get("protected_state", {}).keys(), target)
    if current != journal.get("protected_state"):
        raise ApplyError("target-owned authority changed during package transaction")


def build_final_receipt(
    plan: dict,
    journal: dict,
    incoming: dict[str, dict],
    reconciles: set[str],
) -> dict:
    target = Path(plan["target_root"])
    if journal.get("next_apply_index") != len(active_operations(plan)):
        raise ApplyError("transaction operations are incomplete before receipt")
    validate_transaction_surface(target, plan, journal)
    artifacts: list[dict] = []
    removed: list[dict] = []
    for item in active_operations(plan):
        if item["action"] in {"add", "replace", "rename"}:
            state = file_state(target, item["path"])
            artifacts.append(
                {
                    "operation_id": item["id"],
                    "path": item["path"],
                    "raw_sha256": state.sha256,
                    "git_mode": incoming[item["path"]]["mode"],
                    "observed_filesystem_mode": state.mode,
                }
            )
        if item["action"] == "remove":
            if file_state(target, item["path"]).exists:
                raise ApplyError(
                    f"removed operation path is still present: {item['path']}"
                )
            removed.append({"operation_id": item["id"], "path": item["path"], "result": "absent"})
        elif item["action"] == "rename":
            if file_state(target, item["from_path"]).exists:
                raise ApplyError(
                    f"renamed operation source is still present: {item['from_path']}"
                )
            removed.append({"operation_id": item["id"], "path": item["from_path"], "result": "absent"})
    results: list[dict] = []
    reconciliation_paths = {
        item["path"] for item in plan["operations"] if item["action"] == "reconcile"
    }
    for item in plan["required_framework_paths"]:
        state = file_state(target, item["path"])
        matches_incoming = state_matches(target, state, item)
        if not matches_incoming and item["path"] not in reconciliation_paths:
            raise ApplyError(f"required framework-managed result differs: {item['path']}")
        results.append(
            {
                "path": item["path"],
                "expected_raw_sha256": item["sha256"],
                "expected_git_mode": item["mode"],
                "observed_raw_sha256": state.sha256,
                "observed_git_mode": item["mode"] if matches_incoming else state.mode,
                "observed_filesystem_mode": state.mode,
                "disposition": "package-identical" if matches_incoming else "reconciliation-preserved",
                "match_basis": (
                    "raw"
                    if state.sha256 == item["sha256"]
                    else "git-eol-canonical"
                    if matches_incoming
                    else "mismatch"
                ),
            }
        )
    return {
        "schema_version": PENDING_RECEIPT_SCHEMA_VERSION,
        "status": "pending-validation",
        "transaction_state": (
            "awaiting-target-validation" if is_upgrade_plan(plan) else "finalized"
        ),
        "transaction_id": journal["transaction_id"],
        "plan_sha256": plan["plan_sha256"],
        "package_id": plan["package_id"],
        "package_version": plan.get("package_version"),
        "package_manifest_sha256": plan["package_manifest_sha256"],
        "migration_sha256": plan["migration_sha256"],
        "selected_input_proof": plan.get("package_selected_input_proof"),
        "target_starting_commit": plan["target_starting_commit"],
        "operation_order": [item["id"] for item in active_operations(plan)],
        "applied_operation_ids": [item["id"] for item in active_operations(plan)],
        "skipped_reconciliation_ids": sorted(reconciles),
        "selection": plan["selection"],
        "selection_default": plan["selection_default"],
        "selection_resolution": plan["selection_resolution"],
        "component_operation_counts": {
            "applied": count_components(active_operations(plan)),
            "skipped": plan["component_operation_counts"]["would_skip"],
        },
        "applied_artifacts": artifacts,
        "removed_paths": removed,
        "required_framework_paths": plan["required_framework_paths"],
        "selected_managed_path_results": results,
        "provenance_updated": False,
    }


def expected_rollback_receipt_bytes(plan: dict, journal: dict) -> bytes:
    """Rebuild the only pending receipt rollback may remove without a package."""
    post_states = operation_post_state_map(plan)
    incoming: dict[str, dict] = {}
    for operation in active_operations(plan):
        if operation["action"] in {"add", "replace", "rename"}:
            state = post_states[operation["id"]][operation["path"]]
            incoming[operation["path"]] = {"mode": state["mode"]}
    reconciles = {
        item["id"] for item in plan["operations"] if item["action"] == "reconcile"
    }
    return deterministic_yaml_bytes(
        build_final_receipt(plan, journal, incoming, reconciles)
    )


def recovery_receipt_path(target: Path) -> Path:
    reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
    receipt_path = target / PENDING_RECEIPT_PATH
    if receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError("unsafe pending receipt blocks recovery")
    if receipt_path.exists() and not receipt_path.is_file():
        raise ApplyError("pending receipt must be a regular file during recovery")
    return receipt_path


def run_transaction(
    root: Path,
    journal: dict,
    plan: dict,
    package_root: Path,
    incoming: dict[str, dict],
    reconciles: set[str],
    hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> dict:
    target = Path(plan["target_root"])
    require_target_staging_absent(target, journal["target_staging_paths"])
    verify_recovery_surface(target, plan, journal)
    admitted_journal = deepcopy(journal)
    admitted_journal["state"] = "applying"
    admitted_journal["last_error"] = None
    persist_journal(root, plan, admitted_journal, journal_io_hook)
    journal.clear()
    journal.update(admitted_journal)
    invoke_boundary(hook, "after_applying_journal", {"transaction_id": journal["transaction_id"]})
    operations = active_operations(plan)
    prestate = prestate_by_path(journal)
    for index in range(int(journal["next_apply_index"]), len(operations)):
        verify_recovery_surface(target, plan, journal)
        operation = operations[index]
        execute_operation(
            root,
            package_root,
            target,
            incoming,
            journal,
            operation,
            index,
            prestate,
            hook,
        )
        invoke_boundary(hook, "after_operation", {"index": index, "operation_id": operation["id"]})
        append_progress_record(
            root,
            plan,
            journal,
            phase="apply",
            index=index,
            value=operation["id"],
            journal_io_hook=journal_io_hook,
        )
        invoke_boundary(
            hook,
            "after_progress_journal",
            {
                "index": index,
                "operation_id": operation["id"],
                "next_apply_index": index + 1,
            },
        )
    verify_recovery_surface(
        target, plan, journal, full_worktree_scan=True
    )
    verify_protected_state(target, journal)
    receipt = build_final_receipt(plan, journal, incoming, reconciles)
    receipt_path = target / PENDING_RECEIPT_PATH
    reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
    expected_bytes = deterministic_yaml_bytes(receipt)
    if receipt_path.exists():
        if receipt_path.is_symlink() or is_reparse_point(receipt_path):
            raise ApplyError("pending receipt is ambiguous after interruption")
        existing_bytes = receipt_path.read_bytes()
        if existing_bytes != expected_bytes:
            try:
                existing_receipt = yaml.safe_load(existing_bytes)
            except yaml.YAMLError as exc:
                raise ApplyError(
                    "pending receipt is ambiguous after interruption"
                ) from exc
            if not isinstance(existing_receipt, dict) or not all(
                isinstance(key, str) for key in existing_receipt
            ):
                raise ApplyError("pending receipt is ambiguous after interruption")
            differing_fields = sorted(
                key
                for key in set(existing_receipt) | set(receipt)
                if existing_receipt.get(key) != receipt.get(key)
            )
            detail = (
                f" fields differ: {differing_fields}"
                if differing_fields
                else " deterministic bytes differ"
            )
            raise ApplyError(
                f"pending receipt is ambiguous after interruption;{detail}"
            )
    else:
        atomic_write_bytes(
            receipt_path,
            expected_bytes,
            temporary_path=target_staging_path(
                target, journal, PENDING_RECEIPT_PATH
            ),
            hook=hook,
            boundary_details={
                "transaction_id": journal["transaction_id"],
                "destination": PENDING_RECEIPT_PATH,
                "purpose": "receipt",
            },
        )
    invoke_boundary(hook, "after_receipt", {"transaction_id": journal["transaction_id"]})
    verify_recovery_surface(
        target, plan, journal, full_worktree_scan=True
    )
    journal["final_receipt_sha256"] = sha256_bytes(expected_bytes)
    journal["state"] = (
        "awaiting-target-validation" if is_upgrade_plan(plan) else "finalized"
    )
    persist_journal(root, plan, journal, journal_io_hook)
    invoke_boundary(hook, "after_finalized_journal", {"transaction_id": journal["transaction_id"]})
    return receipt


def load_transaction(
    target: Path,
    transaction_id: str,
    *,
    allow_unbound_target_validation_receipt: bool = False,
    allow_cleared_multi_hop_pending_receipt: bool = False,
) -> tuple[Path, dict, dict]:
    root = transaction_root(target, transaction_id)
    require_safe_transaction_root(root)
    plan_path = root / "plan.json"
    journal_path = root / "journal.yaml"
    if not plan_path.is_file() or plan_path.is_symlink() or not journal_path.is_file() or journal_path.is_symlink():
        raise ApplyError(f"transaction evidence is missing: {transaction_id}")
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        journal = yaml.safe_load(journal_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ApplyError("transaction evidence cannot be parsed") from exc
    if not isinstance(plan, dict) or not isinstance(journal, dict):
        raise ApplyError("transaction evidence must contain mappings")
    if plan.get("schema_version") != APPLY_PLAN_SCHEMA_VERSION:
        raise ApplyError("unsupported transaction apply plan schema")
    if plan_digest(plan) != transaction_id:
        raise ApplyError("transaction plan identity does not match transaction ID")
    plan_target = plan.get("target_root")
    if not isinstance(plan_target, str) or Path(plan_target).resolve() != target.resolve():
        raise ApplyError("transaction target root does not match recovery target")
    if journal.get("schema_version") == LEGACY_JOURNAL_SCHEMA_VERSION:
        raise ApplyError(
            f"{UNSUPPORTED_JOURNAL_VERSION_CLASSIFICATION}: journal v4 recovery is not "
            "supported; use prior tooling that supports journal v4 or perform "
            "owner-directed manual recovery"
        )
    if journal.get("schema_version") != JOURNAL_SCHEMA_VERSION:
        raise ApplyError("unsupported transaction journal schema")
    if journal.get("transaction_id") != transaction_id or journal.get("plan_sha256") != transaction_id:
        raise ApplyError("transaction journal identity is invalid")
    if journal.get("state") not in TRANSACTION_STATES:
        raise ApplyError("transaction journal state is invalid")
    context = route_checkpoint_context(plan)
    if context is None:
        if MULTI_HOP_ROUTE_CONTEXT_KEY in journal:
            raise ApplyError("ordinary transaction journal has multi-hop route context")
    elif journal.get(MULTI_HOP_ROUTE_CONTEXT_KEY) != context:
        raise ApplyError("multi-hop route context differs between plan and journal")
    if journal.get("operation_order_sha256") != canonical_digest(
        [item["id"] for item in active_operations(plan)]
    ):
        raise ApplyError("transaction operation order changed")
    pre_state = journal.get("pre_state")
    if not isinstance(pre_state, list) or [item.get("path") for item in pre_state] != touched_paths(plan):
        raise ApplyError("transaction pre-state path set is invalid")
    for item in pre_state:
        state = item.get("state")
        if not isinstance(state, dict):
            raise ApplyError("transaction pre-state record is invalid")
        if state.get("exists"):
            backup_value = item.get("backup_path")
            backup = root / str(backup_value)
            if not isinstance(backup_value, str) or not backup.is_file() or backup.is_symlink():
                raise ApplyError(f"transaction backup is missing: {item.get('path')}")
            if sha256_bytes(backup.read_bytes()) != item.get("backup_sha256") or item.get("backup_sha256") != state.get("sha256"):
                raise ApplyError(f"transaction backup identity differs: {item.get('path')}")
        elif item.get("backup_path") is not None or item.get("backup_sha256") is not None:
            raise ApplyError(f"absent pre-state has a backup: {item.get('path')}")
    journal = replay_journal_progress(root, plan, journal)
    validate_journal_progress(plan, journal)
    validate_upgrade_remediation_artifacts(
        root,
        plan,
        journal,
        allow_unbound_target_validation_receipt=allow_unbound_target_validation_receipt,
        allow_cleared_multi_hop_pending_receipt=allow_cleared_multi_hop_pending_receipt,
    )
    terminal_path = journal.get("terminal_receipt_path")
    terminal_digest = journal.get("terminal_receipt_sha256")
    if terminal_path is not None:
        path = root / Path(*PurePosixPath(terminal_path).parts)
        if not path.is_file() or path.is_symlink() or sha256_bytes(path.read_bytes()) != terminal_digest:
            raise ApplyError("terminal receipt journal binding differs")
    return root, plan, journal


def load_supplied_target_validation_receipt(path: Path) -> tuple[dict, bytes]:
    """Load externally executed evidence without accepting a lossy reserialization."""
    if path.is_symlink() or is_reparse_point(path) or not path.is_file():
        raise ApplyError("supplied target validation receipt must be a regular file")
    try:
        content = path.read_bytes()
        value = json.loads(content.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyError("cannot read supplied target validation receipt") from exc
    if not isinstance(value, dict) or canonical_json_bytes(value) != content:
        raise ApplyError("supplied target validation receipt must be canonical JSON")
    return value, content


def _record_target_validation_receipt_core(
    target: Path,
    transaction_id: str,
    supplied_receipt_path: Path,
    boundary_hook: Callable[[str, dict], None] | None = None,
    *,
    lock_held: bool,
    route_operation_authorized: bool,
) -> dict:
    """Bind supplied target-validation evidence; this never executes target commands."""
    with _transaction_lock_scope(target, lock_held=lock_held):
        root, plan, journal = load_transaction(
            target,
            transaction_id,
            allow_unbound_target_validation_receipt=True,
        )
        if not is_upgrade_plan(plan):
            raise ApplyError("clean-install transactions do not record target validation receipts")
        if journal.get("state") not in {
            "awaiting-target-validation",
            "validated",
        }:
            raise ApplyError(
                "target validation receipt requires an applied upgrade awaiting provenance finalization"
            )
        remediation = validate_upgrade_remediation_artifacts(
            root,
            plan,
            journal,
            allow_unbound_target_validation_receipt=True,
        )
        if remediation is None:
            raise ApplyError("upgrade remediation evidence is unavailable")
        packet, decision = remediation
        if route_checkpoint_context(plan) is not None and not route_operation_authorized:
            raise ApplyError(
                "multi-hop child target validation may be recorded only by the sealed route orchestrator"
            )
        verify_recovery_surface(
            target, plan, journal, full_worktree_scan=True
        )
        supplied, supplied_bytes = load_supplied_target_validation_receipt(
            supplied_receipt_path
        )
        validate_target_validation_receipt(
            supplied,
            plan,
            journal,
            packet,
            decision,
        )
        receipt_digest = sha256_bytes(supplied_bytes)
        if journal.get("target_validation_receipt_path") != TARGET_VALIDATION_RECEIPT_PATH:
            raise ApplyError("target validation receipt journal path is invalid")
        recorded_digest = journal.get("target_validation_receipt_sha256")
        receipt_path = root / TARGET_VALIDATION_RECEIPT_PATH
        if recorded_digest is not None:
            require_sha256(
                recorded_digest,
                "target validation receipt journal SHA-256",
            )
            if recorded_digest != receipt_digest:
                raise ApplyError("target validation receipt is already bound to different bytes")
            recorded = read_sealed_transaction_json(
                root,
                TARGET_VALIDATION_RECEIPT_PATH,
                recorded_digest,
                "target validation receipt",
            )
            if recorded != supplied:
                raise ApplyError("target validation receipt is already bound to different content")
            if journal.get("state") != "validated":
                raise ApplyError("bound target validation receipt journal state is invalid")
            return recorded
        if receipt_path.exists() or receipt_path.is_symlink() or is_reparse_point(receipt_path):
            if (
                not receipt_path.is_file()
                or receipt_path.is_symlink()
                or is_reparse_point(receipt_path)
                or receipt_path.read_bytes() != supplied_bytes
            ):
                raise ApplyError("unbound target validation receipt differs from supplied evidence")
        else:
            atomic_write_bytes(receipt_path, supplied_bytes)
        invoke_boundary(
            boundary_hook,
            "after_target_validation_receipt_file",
            {"transaction_id": transaction_id},
        )
        if receipt_path.read_bytes() != supplied_bytes:
            raise ApplyError("target validation receipt file differs after write")
        journal["target_validation_receipt_sha256"] = receipt_digest
        journal["state"] = "validated"
        persist_journal(root, plan, journal)
        invoke_boundary(
            boundary_hook,
            "after_target_validation_receipt_journal",
            {"transaction_id": transaction_id},
        )
        validate_target_validation_receipt_binding(
            root,
            plan,
            journal,
            packet,
            decision,
        )
        return supplied


def _record_target_validation_receipt(
    target: Path,
    transaction_id: str,
    supplied_receipt_path: Path,
    boundary_hook: Callable[[str, dict], None] | None = None,
    *,
    lock_held: bool,
    route_operation_authorized: bool,
) -> dict:
    """Capture one bounded target Git view before receipt admission."""
    _root, plan, _journal = load_transaction(
        target,
        transaction_id,
        allow_unbound_target_validation_receipt=True,
    )
    snapshot_paths = (
        set(plan.get("observed", {}))
        | {item["path"] for item in plan.get("required_framework_paths", [])}
        | set(touched_paths(plan))
        | set(protected_target_paths(target))
        | {PENDING_RECEIPT_PATH}
        | {item["path"] for item in target_staging_records(plan)}
    )
    snapshot = capture_target_git_snapshot(
        target,
        snapshot_paths,
        phase="target-validation-receipt",
        require_clean=False,
    )
    with target_git_snapshot_scope(snapshot):
        return _record_target_validation_receipt_core(
            target,
            transaction_id,
            supplied_receipt_path,
            boundary_hook,
            lock_held=lock_held,
            route_operation_authorized=route_operation_authorized,
        )


def record_target_validation_receipt(
    target: Path,
    transaction_id: str,
    supplied_receipt_path: Path,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    return _record_target_validation_receipt(
        target,
        transaction_id,
        supplied_receipt_path,
        boundary_hook,
        lock_held=False,
        route_operation_authorized=False,
    )


def record_target_validation_receipt_locked(
    target: Path,
    transaction_id: str,
    supplied_receipt_path: Path,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    """Internal S2 primitive; caller already holds ``transaction_lock(target)``."""
    return _record_target_validation_receipt(
        target,
        transaction_id,
        supplied_receipt_path,
        boundary_hook,
        lock_held=True,
        route_operation_authorized=True,
    )


def clear_checkpointed_pending_receipt_locked(
    target: Path,
    transaction_id: str,
    expected_pending_receipt_sha256: str,
    *,
    route_transaction_id: str,
    route_intent_sha256: str,
    checkpoint_index: int,
    expected_child_route_context: dict,
) -> None:
    """Clear one pending receipt only after its outer checkpoint is durable.

    This intentionally has no public unlocked counterpart.  The multi-hop
    orchestrator holds the shared package transaction lock across checkpoint
    persistence, this durable clear, and terminal journal promotion.  A
    ``checkpointing`` journal therefore remains recoverable when a crash
    occurs before or after the clear: the exact sealed checkpoint remains the
    authority for the archived receipt bytes.
    """
    require_sha256(
        expected_pending_receipt_sha256,
        "checkpointed pending receipt SHA-256",
    )
    require_sha256(route_transaction_id, "multi-hop route transaction ID")
    require_sha256(route_intent_sha256, "multi-hop route intent SHA-256")
    if type(checkpoint_index) is not int or checkpoint_index < 0:
        raise ApplyError("multi-hop checkpoint index is invalid")
    expected_context = _route_context(expected_child_route_context)
    if (
        expected_context.get("route_transaction_id") != route_transaction_id
        or expected_context.get("route_intent_sha256") != route_intent_sha256
        or expected_context.get("next_hop_index") != checkpoint_index
    ):
        raise ApplyError("pending receipt clearance expected route context differs")
    requested_checkpoint_index = checkpoint_index
    root, plan, journal = load_transaction(
        target,
        transaction_id,
        allow_cleared_multi_hop_pending_receipt=True,
    )
    context = route_checkpoint_context(plan)
    if (
        context != expected_context
        or journal.get(MULTI_HOP_ROUTE_CONTEXT_KEY) != expected_context
    ):
        raise ApplyError("pending receipt clearance route context differs")
    if (
        journal.get("state") != "finalized"
        or journal.get("terminal_receipt_path") != "terminal-receipt.json"
        or not isinstance(journal.get("terminal_receipt_sha256"), str)
        or journal.get("final_receipt_sha256") != expected_pending_receipt_sha256
    ):
        raise ApplyError("pending receipt clearance requires a finalized child transaction")
    route_root = multi_hop_route_root(target, route_transaction_id)
    route_journal, _ = _read_deterministic_route_yaml(
        route_root / "journal.yaml", "multi-hop route journal"
    )
    route_state = route_journal.get("state")
    route_checkpoint_index: object
    checkpoint_sha256: object | None
    if route_state == "checkpointing":
        active_hop = route_journal.get("active_hop")
        if (
            not isinstance(active_hop, dict)
            or type(active_hop.get("hop_index")) is not int
            or active_hop["hop_index"] < 0
            or active_hop.get("child_transaction_id") != transaction_id
            or active_hop["hop_index"] != requested_checkpoint_index
            or route_journal.get("next_hop_index") != active_hop["hop_index"]
        ):
            raise ApplyError("multi-hop checkpointing journal lacks its active child")
        route_checkpoint_index = active_hop["hop_index"]
        checkpoint_sha256 = None
    else:
        route_checkpoint_index = route_journal.get("last_checkpoint_index")
        checkpoint_sha256 = route_journal.get("last_checkpoint_sha256")
    if (
        route_journal.get("schema_version") != MULTI_HOP_ROUTE_JOURNAL_SCHEMA_VERSION
        or route_state not in {"checkpointing", "checkpointed"}
        or route_journal.get("route_transaction_id") != route_transaction_id
        or route_journal.get("route_intent_sha256") != route_intent_sha256
        or type(route_checkpoint_index) is not int
        or route_checkpoint_index < 0
    ):
        raise ApplyError("multi-hop route journal is not ready for receipt clearance")
    if checkpoint_sha256 is not None:
        require_sha256(checkpoint_sha256, "multi-hop route journal checkpoint SHA-256")
    if route_checkpoint_index != requested_checkpoint_index:
        raise ApplyError("multi-hop route checkpoint index differs")
    checkpoint_path = route_root / "checkpoints" / f"{route_checkpoint_index:04d}.json"
    checkpoint, checkpoint_raw = _read_canonical_route_json(
        checkpoint_path, "multi-hop route checkpoint"
    )
    if checkpoint_sha256 is not None and sha256_bytes(checkpoint_raw) != checkpoint_sha256:
        raise ApplyError("multi-hop route checkpoint clearance identity differs")
    checkpoint_unsigned = deepcopy(checkpoint)
    if checkpoint_unsigned.pop("digest", None) != canonical_digest(checkpoint_unsigned):
        raise ApplyError("multi-hop route checkpoint clearance digest differs")
    child = checkpoint.get("child_transaction")
    pending = checkpoint.get("pending_receipt")
    if (
        not isinstance(child, dict)
        or child.get("transaction_id") != transaction_id
        or child.get("plan_sha256") != transaction_id
        or child.get("terminal_receipt_sha256") != journal.get("terminal_receipt_sha256")
        or not isinstance(pending, dict)
        or pending.get("path") != PENDING_RECEIPT_PATH
        or pending.get("sha256") != expected_pending_receipt_sha256
        or not isinstance(pending.get("archive_path"), str)
    ):
        raise ApplyError("multi-hop route checkpoint lacks exact child receipt evidence")
    archive_relative = safe_path(
        pending["archive_path"], "multi-hop checkpoint pending receipt archive path"
    )
    archived = _read_route_regular_bytes(
        route_root / Path(*PurePosixPath(archive_relative).parts),
        "multi-hop checkpoint pending receipt archive",
    )
    if sha256_bytes(archived) != expected_pending_receipt_sha256:
        raise ApplyError("multi-hop checkpoint pending receipt archive differs")
    receipt_path = recovery_receipt_path(target)
    if receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError("current pending receipt differs from checkpoint evidence")
    if not receipt_path.exists():
        # The process may have crashed after the durable clear but before the
        # outer route journal was promoted.  The sealed archive plus finalized
        # child receipt prove this exact idempotent completion case.
        return
    if (
        not receipt_path.is_file()
        or sha256_bytes(receipt_path.read_bytes()) != expected_pending_receipt_sha256
    ):
        raise ApplyError("current pending receipt differs from checkpoint evidence")
    durable_unlink(receipt_path, root)
    if receipt_path.exists():
        raise ApplyError("checkpointed pending receipt was not durably cleared")


def changed_target_paths(
    target: Path, *, full_worktree_scan: bool = False
) -> set[str]:
    snapshot = active_target_git_snapshot(target)
    if snapshot is not None:
        return snapshot.changed_paths(full_worktree_scan=full_worktree_scan)
    changed: set[str] = set()
    for arguments in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        result = run_git_bytes(target, *arguments)
        if result.returncode != 0:
            raise ApplyError("cannot inspect recovery worktree state")
        changed.update(
            value.decode("utf-8", errors="surrogateescape")
            for value in result.stdout.split(b"\0")
            if value
        )
    return changed


def cleanup_transaction_staging(
    target: Path, root: Path, plan: dict, journal: dict
) -> None:
    expected = target_staging_records(plan)
    if journal.get("target_staging_paths") != expected:
        raise ApplyError("transaction journal staging path evidence is invalid")
    for item in expected:
        relative = item["path"]
        reject_symlink_boundary(target, relative)
        path = target / Path(*PurePosixPath(relative).parts)
        if path.is_symlink() or is_reparse_point(path):
            raise ApplyError(f"transaction staging path is unsafe: {relative}")
        if not path.exists():
            continue
        if not path.is_file():
            raise ApplyError(f"transaction staging path is not a regular file: {relative}")
        durable_unlink(path, root)


def verify_recovery_surface(
    target: Path,
    plan: dict,
    journal: dict,
    *,
    allow_target_staging: bool = False,
    full_worktree_scan: bool = False,
) -> None:
    if target_git_head(target) != plan.get("target_starting_commit"):
        raise ApplyError("target HEAD changed after transaction planning")
    verify_planned_target_git_semantics(target, plan)
    if is_upgrade_plan(plan):
        if target_validation_profile(target) != plan.get("target_validation_profile"):
            raise ApplyError("target validation profile changed after transaction planning")
        if target_file_identity(
            target, ".dev/ai-context/provenance.yaml"
        ) != plan.get("target_provenance"):
            raise ApplyError("target provenance changed after transaction planning")
        if target_file_identity(
            target, ".dev/ai-context/customizations.yaml"
        ) != plan.get("target_semantic_customizations"):
            raise ApplyError("target semantic customizations changed after transaction planning")
    allowed = set(touched_paths(plan)) | {PENDING_RECEIPT_PATH}
    if allow_target_staging:
        expected_staging = target_staging_records(plan)
        if journal.get("target_staging_paths") != expected_staging:
            raise ApplyError("transaction journal staging path evidence is invalid")
        allowed.update(item["path"] for item in expected_staging)
    context = route_checkpoint_context(plan)
    if context is not None:
        journal_context = journal.get(MULTI_HOP_ROUTE_CONTEXT_KEY)
        if journal_context != context:
            raise ApplyError("multi-hop route context differs between plan and journal")
        verify_multi_hop_checkpoint_for_active_child(
            target,
            context,
            allowed_mutations=allowed,
        )
    else:
        unrelated = changed_target_paths(
            target, full_worktree_scan=full_worktree_scan
        ) - allowed
        if unrelated:
            raise ApplyError(f"unrelated target changes block recovery: {sorted(unrelated)}")
    verify_protected_state(target, journal)
    validate_transaction_surface(target, plan, journal)


def rollback_loaded_transaction(
    root: Path,
    plan: dict,
    journal: dict,
    hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> dict:
    target = Path(plan["target_root"])
    receipt_path = recovery_receipt_path(target)
    verify_recovery_surface(
        target,
        plan,
        journal,
        allow_target_staging=True,
        full_worktree_scan=True,
    )
    if journal["state"] == "rolled-back":
        if not all(exact_state_matches(target, item["path"], item["state"]) for item in journal["pre_state"]):
            raise ApplyError("rolled-back transaction no longer matches its exact pre-state")
        if receipt_path.exists():
            raise ApplyError("rolled-back transaction still has a pending receipt")
        return journal
    if journal["state"] == "finalized":
        raise ApplyError("finalized transaction cannot be rolled back")
    validate_transaction_surface(target, plan, journal)
    if receipt_path.exists():
        reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
        if journal["state"] == "rolling-back":
            raise ApplyError("rolling-back transaction still has a pending receipt")
        expected_receipt = expected_rollback_receipt_bytes(plan, journal)
        if receipt_path.read_bytes() != expected_receipt:
            raise ApplyError("pending receipt does not match rollback transaction")
        reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
        durable_unlink(receipt_path, root)
    rollback_items = list(reversed(journal["pre_state"]))
    if journal["state"] != "rolling-back":
        journal["state"] = "rolling-back"
        journal["last_error"] = None
        journal["rollback_next_index"] = 0
        journal["rollback_completed_paths"] = []
        journal["rollback_start_state"] = observation(touched_paths(plan), target)
        persist_journal(root, plan, journal, journal_io_hook)
        invoke_boundary(
            hook,
            "after_rollback_start_journal",
            {"transaction_id": journal["transaction_id"]},
        )
    for index in range(journal["rollback_next_index"], len(rollback_items)):
        verify_recovery_surface(target, plan, journal)
        item = rollback_items[index]
        relative = item["path"]
        path = target / Path(*PurePosixPath(relative).parts)
        if exact_state_matches(target, relative, item["state"]):
            pass
        elif item["state"]["exists"]:
            backup = root / item["backup_path"]
            atomic_write_bytes(
                path,
                backup.read_bytes(),
                mode_int(item["state"]["mode"]),
                temporary_path=target_staging_path(target, journal, relative),
                hook=hook,
                boundary_details={
                    "transaction_id": journal["transaction_id"],
                    "destination": relative,
                    "purpose": "rollback",
                },
            )
        elif path.exists():
            durable_unlink(path, root)
        invoke_boundary(hook, "after_rollback_restore", {"path": relative})
        append_progress_record(
            root,
            plan,
            journal,
            phase="rollback",
            index=index,
            value=relative,
            journal_io_hook=journal_io_hook,
        )
        invoke_boundary(
            hook,
            "after_rollback_progress_journal",
            {"index": index, "path": relative},
        )
    verify_recovery_surface(
        target, plan, journal, full_worktree_scan=True
    )
    for relative in reversed(journal.get("planned_created_parents", [])):
        directory = target / Path(*PurePosixPath(relative).parts)
        if directory.exists() and directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
            fsync_directory(directory.parent)
    if not all(exact_state_matches(target, item["path"], item["state"]) for item in journal["pre_state"]):
        raise ApplyError("rollback did not restore the exact transaction pre-state")
    reject_symlink_boundary(target, PENDING_RECEIPT_PATH)
    if receipt_path.exists() or receipt_path.is_symlink() or is_reparse_point(receipt_path):
        raise ApplyError("rollback did not remove the pending receipt boundary")
    journal["state"] = "rolled-back"
    journal["last_error"] = None
    persist_journal(root, plan, journal, journal_io_hook)
    invoke_boundary(hook, "after_rollback_journal", {"transaction_id": journal["transaction_id"]})
    return journal


def _recover_transaction_core(
    target: Path,
    transaction_id: str,
    action: str,
    package_root: Path | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    *,
    lock_held: bool,
    route_operation_authorized: bool,
) -> dict:
    if action not in {"resume", "rollback"}:
        raise ApplyError("recovery action must be resume or rollback")
    with _transaction_lock_scope(target, lock_held=lock_held):
        reject_unfinished_v4_transactions(target)
        root, plan, journal = load_transaction(target, transaction_id)
        if route_checkpoint_context(plan) is not None and not route_operation_authorized:
            raise ApplyError(
                "multi-hop child recovery may be performed only by the sealed route orchestrator"
            )
        verify_recovery_surface(
            target,
            plan,
            journal,
            allow_target_staging=True,
            full_worktree_scan=True,
        )
        receipt_path = recovery_receipt_path(target)
        reconciles = {
            item["id"] for item in plan["operations"] if item["action"] == "reconcile"
        }
        if journal["state"] == "rejected":
            if action == "resume":
                raise ApplyError("rejected owner decision transaction cannot be resumed")
            return journal
        if action == "rollback" and journal["state"] == "finalized":
            raise ApplyError("finalized transaction cannot be rolled back")
        if action == "rollback" and receipt_path.exists():
            if journal["state"] == "rolling-back":
                raise ApplyError("rolling-back transaction still has a pending receipt")
            if journal["state"] == "rolled-back":
                raise ApplyError("rolled-back transaction still has a pending receipt")
            if receipt_path.read_bytes() != expected_rollback_receipt_bytes(
                plan, journal
            ):
                raise ApplyError("pending receipt does not match rollback transaction")
        if action == "resume" and journal["state"] in {"rolling-back", "rolled-back"}:
            raise ApplyError(
                f"{journal['state']} transaction cannot be resumed"
            )
        incoming: dict[str, dict] | None = None
        if action == "resume":
            if package_root is None:
                raise ApplyError("resume requires the exact extracted package root")
            _package, incoming, _migration, _manifest_sha = verify_package_binding(
                plan, package_root
            )
            incoming = filter_component_records(
                incoming, enabled_components(plan["selection"])
            )
            if journal["state"] in {
                "awaiting-target-validation",
                "validated",
                "finalized",
            } and not receipt_path.is_file():
                raise ApplyError("applied transaction receipt identity differs")
            if receipt_path.exists():
                if (
                    journal["state"]
                    not in {
                        "applying",
                        "interrupted",
                        "awaiting-target-validation",
                        "validated",
                        "finalized",
                    }
                    or journal["next_apply_index"] != len(active_operations(plan))
                ):
                    raise ApplyError("pending receipt is ambiguous after interruption")
                expected_receipt = build_final_receipt(
                    plan, journal, incoming, reconciles
                )
                expected_receipt_bytes = deterministic_yaml_bytes(expected_receipt)
                if receipt_path.read_bytes() != expected_receipt_bytes:
                    raise ApplyError("pending receipt is ambiguous after interruption")
                if (
                    journal["state"]
                    in {"awaiting-target-validation", "validated", "finalized"}
                    and sha256_bytes(expected_receipt_bytes)
                    != journal.get("final_receipt_sha256")
                ):
                    raise ApplyError("applied transaction receipt identity differs")
        verify_recovery_surface(
            target,
            plan,
            journal,
            allow_target_staging=True,
            full_worktree_scan=True,
        )
        cleanup_transaction_staging(target, root, plan, journal)
        snapshot = active_target_git_snapshot(target)
        if snapshot is None:
            raise ApplyError("transaction staging cleanup requires one active snapshot")
        snapshot.accept_verified_absence(
            item["path"] for item in target_staging_records(plan)
        )
        verify_recovery_surface(
            target,
            plan,
            journal,
            full_worktree_scan=True,
        )
        if action == "rollback":
            return rollback_loaded_transaction(
                root, plan, journal, boundary_hook, journal_io_hook
            )
        if journal["state"] == "applying":
            journal["state"] = "interrupted"
            journal["last_error"] = "recovered an abandoned applying state"
            persist_journal(root, plan, journal, journal_io_hook)
        if journal["state"] in {
            "awaiting-target-validation",
            "validated",
            "finalized",
        }:
            if not receipt_path.is_file() or sha256_bytes(receipt_path.read_bytes()) != journal.get("final_receipt_sha256"):
                raise ApplyError("applied transaction receipt identity differs")
            receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
            if not isinstance(receipt, dict):
                raise ApplyError("applied transaction receipt is invalid")
            return receipt
        if incoming is None:
            raise ApplyError("resume package binding is unavailable")
        return run_transaction(
            root,
            journal,
            plan,
            package_root,
            incoming,
            reconciles,
            boundary_hook,
            journal_io_hook,
        )


def _recover_transaction(
    target: Path,
    transaction_id: str,
    action: str,
    package_root: Path | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    *,
    lock_held: bool,
    route_operation_authorized: bool,
) -> dict:
    if action not in {"resume", "rollback"}:
        raise ApplyError("recovery action must be resume or rollback")
    _root, plan, _journal = load_transaction(target, transaction_id)
    snapshot_paths = (
        set(plan.get("observed", {}))
        | {item["path"] for item in plan.get("required_framework_paths", [])}
        | set(touched_paths(plan))
        | set(protected_target_paths(target))
        | {PENDING_RECEIPT_PATH}
        | {item["path"] for item in target_staging_records(plan)}
    )
    snapshot = capture_target_git_snapshot(
        target,
        snapshot_paths,
        phase=f"recovery-{action}",
        require_clean=False,
    )
    with target_git_snapshot_scope(snapshot):
        verify_planned_target_git_semantics(target, plan)
        return _recover_transaction_core(
            target,
            transaction_id,
            action,
            package_root,
            boundary_hook,
            journal_io_hook,
            lock_held=lock_held,
            route_operation_authorized=route_operation_authorized,
        )


def recover_transaction(
    target: Path,
    transaction_id: str,
    action: str,
    package_root: Path | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> dict:
    return _recover_transaction(
        target,
        transaction_id,
        action,
        package_root,
        boundary_hook,
        journal_io_hook,
        lock_held=False,
        route_operation_authorized=False,
    )


def recover_transaction_locked(
    target: Path,
    transaction_id: str,
    action: str,
    package_root: Path | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
) -> dict:
    """Internal S2 primitive; caller already holds ``transaction_lock(target)``."""
    return _recover_transaction(
        target,
        transaction_id,
        action,
        package_root,
        boundary_hook,
        journal_io_hook,
        lock_held=True,
        route_operation_authorized=True,
    )


def _apply_plan_core(
    plan: dict,
    acknowledgements: set[str] | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    remediation_decision: dict | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    *,
    lock_held: bool,
    route_operation_authorized: bool,
) -> dict:
    acknowledgements = acknowledgements or set()
    target = Path(plan["target_root"])
    package_root = Path(plan["package_root"])
    with _transaction_lock_scope(target, lock_held=lock_held):
        reject_unfinished_v4_transactions(target)
        remediation: tuple[dict, dict] | None = None
        if is_upgrade_plan(plan):
            if remediation_decision is None:
                raise ApplyError(
                    "upgrade apply requires an explicit approved remediation decision"
                )
            if acknowledgements:
                raise ApplyError(
                    "upgrade apply does not accept separate reconciliation acknowledgements"
                )
            packet = build_upgrade_remediation_packet(plan)
            decision = validate_upgrade_remediation_decision(remediation_decision, packet)
            acknowledgements = set(decision["reconciliation_ids"])
            remediation = (packet, decision)
        elif remediation_decision is not None:
            raise ApplyError("clean-install apply does not accept an upgrade remediation decision")
        rejected = remediation is not None and remediation[1]["status"] == "rejected"
        _package, incoming, _manifest_sha, reconciles = verify_plan_for_apply(
            plan,
            acknowledgements,
            require_write_authority=not rejected,
            route_operation_authorized=route_operation_authorized,
        )
        root, journal = prepare_transaction(
            target,
            plan,
            acknowledgements,
            remediation=remediation,
            hook=boundary_hook,
            journal_io_hook=journal_io_hook,
            route_operation_authorized=route_operation_authorized,
        )
        invoke_boundary(
            boundary_hook,
            "after_planned_journal",
            {"transaction_id": journal["transaction_id"]},
        )
        if journal["state"] == "rejected":
            raise ApplyError(
                "package apply rejected by owner decision before target mutation; "
                f"transaction retained: {journal['transaction_id']}"
            )
        try:
            return run_transaction(
                root,
                journal,
                plan,
                package_root,
                incoming,
                reconciles,
                boundary_hook,
                journal_io_hook,
            )
        except Exception as exc:
            if journal["state"] == "planned":
                raise ApplyError(
                    f"package apply rejected before target mutation; recover transaction {journal['transaction_id']}: {exc}"
                ) from exc
            journal["state"] = "interrupted"
            journal["last_error"] = str(exc)
            persist_journal(root, plan, journal, journal_io_hook)
            try:
                rollback_loaded_transaction(
                    root, plan, journal, boundary_hook, journal_io_hook
                )
            except Exception as rollback_exc:
                if journal["state"] == "rolling-back":
                    journal["last_error"] = (
                        f"{exc}; rollback failed: {rollback_exc}"
                    )
                    persist_journal(root, plan, journal, journal_io_hook)
                raise ApplyError(
                    f"package apply interrupted and rollback failed; recover transaction {journal['transaction_id']}: {rollback_exc}"
                ) from exc
            raise ApplyError(
                f"package apply rolled back transaction {journal['transaction_id']}: {exc}"
            ) from exc


def _apply_plan(
    plan: dict,
    acknowledgements: set[str] | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    remediation_decision: dict | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    git_inspection_hook: Callable[[dict], None] | None = None,
    *,
    lock_held: bool,
    route_operation_authorized: bool,
) -> dict:
    phase_started = time.perf_counter_ns()
    target = Path(plan["target_root"])
    snapshot_paths = (
        set(plan.get("observed", {}))
        | {item["path"] for item in plan.get("required_framework_paths", [])}
        | set(touched_paths(plan))
        | set(protected_target_paths(target))
        | {PENDING_RECEIPT_PATH}
    )
    snapshot = capture_target_git_snapshot(
        target,
        snapshot_paths,
        phase="apply",
        require_clean=route_checkpoint_context(plan) is None,
    )
    with target_git_snapshot_scope(snapshot):
        # The captured Git-admin path resolves the transaction lock without a
        # pre-snapshot subprocess.  Recheck the local identity after acquiring
        # the lock so a concurrent package apply cannot turn the snapshot into
        # stale authority during that interval.
        with _transaction_lock_scope(target, lock_held=lock_held):
            if snapshot.changed_paths(
                full_worktree_scan=True
            ) != set(snapshot.dirty_paths):
                raise ApplyError(
                    "target worktree changed before apply snapshot admission"
                )
            snapshot.assert_identity(full=True)
            try:
                result = _apply_plan_core(
                    plan,
                    acknowledgements,
                    boundary_hook,
                    remediation_decision,
                    journal_io_hook,
                    lock_held=True,
                    route_operation_authorized=route_operation_authorized,
                )
            except Exception:
                emit_git_inspection_metrics(
                    snapshot,
                    git_inspection_hook,
                    phase_duration_ns=time.perf_counter_ns() - phase_started,
                    outcome="failed",
                )
                raise
            emit_git_inspection_metrics(
                snapshot,
                git_inspection_hook,
                phase_duration_ns=time.perf_counter_ns() - phase_started,
                outcome="passed",
            )
            return result


def apply_plan(
    plan: dict,
    acknowledgements: set[str] | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    remediation_decision: dict | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    git_inspection_hook: Callable[[dict], None] | None = None,
) -> dict:
    return _apply_plan(
        plan,
        acknowledgements,
        boundary_hook,
        remediation_decision,
        journal_io_hook,
        git_inspection_hook,
        lock_held=False,
        route_operation_authorized=False,
    )


def apply_plan_locked(
    plan: dict,
    acknowledgements: set[str] | None = None,
    boundary_hook: Callable[[str, dict], None] | None = None,
    remediation_decision: dict | None = None,
    journal_io_hook: Callable[[dict], None] | None = None,
    git_inspection_hook: Callable[[dict], None] | None = None,
) -> dict:
    """Internal S2 primitive; caller already holds ``transaction_lock(target)``."""
    return _apply_plan(
        plan,
        acknowledgements,
        boundary_hook,
        remediation_decision,
        journal_io_hook,
        git_inspection_hook,
        lock_held=True,
        route_operation_authorized=True,
    )
