#!/usr/bin/env python3
"""Privacy-preserving, deterministic evidence records for validation profiles."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable


SCHEMA_VERSION = "2.0.0"
# Reuse eligibility is intentionally independent from the emitted evidence
# schema.  Existing successful evidence remains safe to reuse when the input
# and validator fingerprints still match; a presentation-schema increment must
# not turn an otherwise valid run into a cache-read failure.
CACHE_SCHEMA_VERSION = "1.0.0"
OUTCOMES = {"passed", "failed", "blocked-by-environment", "not-applicable", "deferred-with-owner"}
DISPOSITIONS = {
    "executed",
    "reused",
    "not-selected",
    "not-executed",
    "timed-out",
    "cancelled",
    "snapshot-drift",
}
SNAPSHOT_SCHEMA = "validation-repository-snapshot/v1"
SNAPSHOT_ADMISSION_FAILURE_SCHEMA = "validation-repository-admission-failure/v1"
SUPERVISION_SCHEMA = "validation-supervision-result/v1"
BOOTSTRAP_SCHEMA = "validation-supervision-bootstrap/v1"
INVOCATION_SCHEMA = "validation-invocation/v1"
SELECTION_COMPARISON_SCHEMA = "validation-selection-comparison/v1"
IMMUTABLE_HISTORY_RECEIPT_REF = ".ai/distribution/validation/immutable-history-receipt.yaml"
IMMUTABLE_HISTORY_VALIDATOR_REF = ".ai/scripts/validate-immutable-history.py"
VALIDATION_EVIDENCE_HELPER_REF = ".ai/scripts/validation-evidence.py"
CONTROL_ROLES = {
    "bootstrap-snapshot",
    "prepare",
    "post-snapshot",
    "finalize",
    "summarize",
    "workflow-summary",
}
GIT_TIMEOUT_SECONDS = 30
WINDOWS_ABSOLUTE_FRAGMENT = re.compile(r"(?i)(?<![a-z0-9_<>])(?:[a-z]:[\\/]|\\\\)")
POSIX_ABSOLUTE_FRAGMENT = re.compile(r"(?<![a-zA-Z0-9_.<>-])/")
GIT_SHA_RE = re.compile(r"[0-9a-f]{40}")


class EvidenceError(ValueError):
    """Fail-closed validation evidence contract violation."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha256(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_write_bytes(path: Path, content: bytes) -> None:
    """Write and fsync a retained artifact before atomically publishing it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def fsync_directory(path: Path) -> None:
    try:
        directory_descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write_bytes(path, formatted_json_bytes(value))


def formatted_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def load_json_object(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"cannot read {description}") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"{description} must be a JSON object")
    return value


def run_git(repo: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repo,
            check=False,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceError(f"Git command failed or exceeded {GIT_TIMEOUT_SECONDS} seconds") from exc
    if result.returncode:
        raise EvidenceError("Git command did not complete successfully")
    return result.stdout


def repository_root(repo: Path) -> Path:
    candidate = repo.resolve()
    raw_root = run_git(candidate, "rev-parse", "--show-toplevel").rstrip(b"\r\n")
    if not raw_root:
        raise EvidenceError("cannot identify repository root")
    root = Path(os.fsdecode(raw_root)).resolve()
    if root != candidate:
        raise EvidenceError("--repo must identify the repository root")
    return root


def repository_root_identity(repo: Path) -> str:
    normalized = os.path.normcase(str(repo.resolve()))
    return sha256_bytes(os.fsencode(normalized))


def git_path_exists(repo: Path, name: str) -> bool:
    raw_path = run_git(repo, "rev-parse", "--git-path", name).rstrip(b"\r\n")
    if not raw_path:
        raise EvidenceError("cannot resolve Git operation state")
    path = Path(os.fsdecode(raw_path))
    if not path.is_absolute():
        path = repo / path
    return path.exists()


def untracked_content_records(repo: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for raw_path in sorted(
        (item for item in run_git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if item)
    ):
        relative = os.fsdecode(raw_path)
        candidate = repo / relative
        try:
            metadata = candidate.lstat()
            if candidate.is_symlink():
                content = os.fsencode(os.readlink(candidate))
                kind = "symlink"
            elif candidate.is_file():
                content = candidate.read_bytes()
                kind = "file"
            else:
                content = b""
                kind = "other"
        except OSError as exc:
            raise EvidenceError("cannot fingerprint untracked target state") from exc
        records.append(
            {
                "path_digest": sha256_bytes(raw_path),
                "kind": kind,
                "mode": f"{metadata.st_mode & 0o7777:04o}",
                "content_sha256": sha256_bytes(content),
                "bytes": len(content),
            }
        )
    return records


def capture_repository_identity_once(repo: Path) -> dict[str, object]:
    head_values = run_git(repo, "rev-parse", "HEAD", "HEAD^{tree}").decode(
        "ascii", errors="strict"
    ).splitlines()
    if len(head_values) != 2:
        raise EvidenceError("cannot read repository commit and tree")
    branch_raw = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    branch = branch_raw.decode("utf-8", errors="replace").strip()
    head_state: dict[str, object] = (
        {"kind": "branch", "name": branch} if branch != "HEAD" else {"kind": "detached"}
    )
    status = run_git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    operations = {
        "merge": git_path_exists(repo, "MERGE_HEAD"),
        "rebase": git_path_exists(repo, "rebase-merge")
        or git_path_exists(repo, "rebase-apply"),
        "cherry_pick": git_path_exists(repo, "CHERRY_PICK_HEAD"),
        "revert": git_path_exists(repo, "REVERT_HEAD"),
        "bisect": git_path_exists(repo, "BISECT_START"),
    }
    target_state = {
        "status_sha256": sha256_bytes(status),
        "staged_diff_sha256": sha256_bytes(
            run_git(repo, "diff", "--cached", "--binary", "--no-ext-diff", "--no-renames")
        ),
        "worktree_diff_sha256": sha256_bytes(
            run_git(repo, "diff", "--binary", "--no-ext-diff", "--no-renames")
        ),
        "untracked": untracked_content_records(repo),
    }
    return {
        "commit": head_values[0],
        "tree": head_values[1],
        "head": head_state,
        "operation_state": operations,
        "clean": not status and not any(operations.values()),
        "status_digest": sha256_bytes(status),
        "target_state_digest": canonical_sha256(target_state),
        "repo_root_identity_digest": repository_root_identity(repo),
    }


def capture_repository_snapshot(repo: Path, profile: str) -> dict[str, object]:
    repo = repository_root(repo)
    first_identity = capture_repository_identity_once(repo)
    second_identity = capture_repository_identity_once(repo)
    if first_identity != second_identity:
        raise EvidenceError("repository changed during sequential snapshot capture")
    return {
        "schema_version": SNAPSHOT_SCHEMA,
        "profile": profile,
        "captured_at": utc_now(),
        "identity": second_identity,
        "identity_digest": canonical_sha256(second_identity),
    }


def validated_snapshot(path: Path) -> dict[str, Any]:
    value = load_json_object(path, "repository snapshot")
    if value.get("schema_version") != SNAPSHOT_SCHEMA:
        raise EvidenceError("repository snapshot schema is invalid")
    identity = value.get("identity")
    if not isinstance(identity, dict) or value.get("identity_digest") != canonical_sha256(identity):
        raise EvidenceError("repository snapshot identity digest is invalid")
    if not isinstance(value.get("profile"), str) or not value["profile"]:
        raise EvidenceError("repository snapshot profile is invalid")
    captured_at = value.get("captured_at")
    try:
        if not isinstance(captured_at, str) or not captured_at.endswith("Z"):
            raise ValueError("snapshot time must be UTC")
        datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceError("repository snapshot capture time is invalid") from exc
    operations = identity.get("operation_state")
    head = identity.get("head")
    git_oids = (identity.get("commit"), identity.get("tree"))
    if (
        not all(
            isinstance(oid, str)
            and len(oid) in {40, 64}
            and all(character in "0123456789abcdef" for character in oid)
            for oid in git_oids
        )
        or not isinstance(head, dict)
        or head.get("kind") not in {"branch", "detached"}
        or head.get("kind") == "branch"
        and (not isinstance(head.get("name"), str) or not head["name"])
        or head.get("kind") == "detached"
        and set(head) != {"kind"}
        or not isinstance(operations, dict)
        or set(operations) != {"merge", "rebase", "cherry_pick", "revert", "bisect"}
        or not all(isinstance(state, bool) for state in operations.values())
        or not isinstance(identity.get("clean"), bool)
        or not is_sha256(identity.get("status_digest"))
        or not is_sha256(identity.get("target_state_digest"))
        or not is_sha256(identity.get("repo_root_identity_digest"))
    ):
        raise EvidenceError("repository snapshot identity contract is invalid")
    expected_clean = identity["status_digest"] == sha256_bytes(b"") and not any(
        operations.values()
    )
    if identity["clean"] is not expected_clean:
        raise EvidenceError("repository snapshot clean state is inconsistent")
    return value


def compare_snapshot(repo: Path, snapshot_path: Path) -> tuple[dict[str, Any], dict[str, object], bool]:
    expected = validated_snapshot(snapshot_path)
    observed = capture_repository_snapshot(repo, str(expected["profile"]))
    matches = expected["identity_digest"] == observed["identity_digest"]
    return expected, observed, matches


def snapshot_command(arguments: argparse.Namespace) -> None:
    output = Path(arguments.output)
    try:
        value = capture_repository_snapshot(Path(arguments.repo), arguments.profile)
    except EvidenceError as exc:
        atomic_write_json(output, snapshot_admission_failure(arguments.profile))
        raise EvidenceError("repository snapshot admission failed") from exc
    atomic_write_json(output, value)
    if arguments.require_clean and not value["identity"]["clean"]:
        raise EvidenceError("repository snapshot is not clean")


def snapshot_admission_failure(profile: str) -> dict[str, object]:
    return {
        "schema_version": SNAPSHOT_ADMISSION_FAILURE_SCHEMA,
        "profile": profile,
        "status": "rejected",
        "reason_code": "snapshot-capture-failed",
        "captured_at": utc_now(),
    }


def bootstrap_driver_argv(
    python_executable: str,
    *,
    snapshot_ref: str,
    profile: str,
    sidecar_ref: str,
    cwd_ref: str,
    require_clean: bool,
    target_argv: list[str],
) -> list[str]:
    validate_record_token(python_executable, "bootstrap Python executable")
    validate_relative_reference(snapshot_ref, "bootstrap snapshot output")
    validate_record_token(profile, "bootstrap profile")
    validate_relative_reference(sidecar_ref, "bootstrap sidecar output")
    validate_relative_reference(cwd_ref, "bootstrap cwd")
    if not target_argv or not all(isinstance(value, str) and value for value in target_argv):
        raise EvidenceError("bootstrap target argv is empty or invalid")
    result = [
        python_executable,
        VALIDATION_EVIDENCE_HELPER_REF,
        "bootstrap-run",
        "--repo", ".",
        "--snapshot-output", snapshot_ref,
        "--profile", profile,
        "--sidecar-output", sidecar_ref,
        "--cwd-ref", cwd_ref,
    ]
    if require_clean:
        result.append("--require-clean")
    result.extend(("--", *target_argv))
    return result


def bootstrap_sidecar_payload(
    repo: Path,
    *,
    profile: str,
    status: str,
    reason_code: str | None,
    snapshot_path: Path,
    snapshot_identity_digest: str | None,
    snapshot_clean: bool | None,
    post_verified: bool,
    target_argv: list[str],
    cwd_ref: str,
    target_launched: bool,
    target_exit_code: int | None,
) -> dict[str, object]:
    safe_target = privacy_safe_argv(repo, target_argv)
    return {
        "schema_version": BOOTSTRAP_SCHEMA,
        "profile": profile,
        "status": status,
        "reason_code": reason_code,
        "snapshot_ref": relative_path(repo, snapshot_path),
        "snapshot_identity_digest": snapshot_identity_digest,
        "snapshot_clean": snapshot_clean,
        "post_verified": post_verified,
        "target_argv": safe_target,
        "target_argv_digest": canonical_sha256(safe_target),
        "target_effective_argv_digest": canonical_sha256(target_argv),
        "target_cwd_ref": cwd_ref,
        "target_launched": target_launched,
        "target_exit_code": target_exit_code,
    }


def bootstrap_run(arguments: argparse.Namespace) -> int:
    """Capture admission and run the target inside one supervisor-owned tree."""
    if arguments.repo != ".":
        raise EvidenceError("bootstrap internal repository reference must be '.'")
    repo = Path.cwd().resolve()
    snapshot_path = artifact_path_inside(
        repo, arguments.snapshot_output, "bootstrap snapshot output"
    )
    sidecar_path = artifact_path_inside(
        repo, arguments.sidecar_output, "bootstrap sidecar output"
    )
    cwd_ref = validate_relative_reference(arguments.cwd_ref, "bootstrap cwd")
    cwd = artifact_path_inside(repo, cwd_ref, "bootstrap cwd")
    if not cwd.is_dir():
        raise EvidenceError("bootstrap cwd does not exist")
    target_argv = list(arguments.command_argv)
    if target_argv and target_argv[0] == "--":
        target_argv = target_argv[1:]
    if not target_argv:
        raise EvidenceError("bootstrap target argv is empty")
    profile = validate_record_token(arguments.profile, "bootstrap profile")

    def persist(
        status: str,
        *,
        reason_code: str | None = None,
        identity_digest: str | None = None,
        clean: bool | None = None,
        post_verified: bool = False,
        launched: bool = False,
        exit_code: int | None = None,
    ) -> None:
        atomic_write_json(
            sidecar_path,
            bootstrap_sidecar_payload(
                repo,
                profile=profile,
                status=status,
                reason_code=reason_code,
                snapshot_path=snapshot_path,
                snapshot_identity_digest=identity_digest,
                snapshot_clean=clean,
                post_verified=post_verified,
                target_argv=target_argv,
                cwd_ref=cwd_ref,
                target_launched=launched,
                target_exit_code=exit_code,
            ),
        )

    # This is the durable no-launch boundary.  The target cannot be started
    # before a retained sidecar says that admission is still being captured.
    persist("capturing")
    try:
        snapshot_value = capture_repository_snapshot(repo, profile)
    except EvidenceError:
        atomic_write_json(snapshot_path, snapshot_admission_failure(profile))
        persist("admission-rejected", reason_code="snapshot-capture-failed")
        return 128
    atomic_write_json(snapshot_path, snapshot_value)
    identity_digest = str(snapshot_value["identity_digest"])
    clean = bool(snapshot_value["identity"]["clean"])
    if arguments.require_clean and not clean:
        persist(
            "admission-rejected",
            reason_code="repository-not-clean",
            identity_digest=identity_digest,
            clean=False,
        )
        return 128

    # Crossing this durable boundary means the target may have launched.  A
    # cancellation between this write and process creation therefore errs on
    # the safe side when the runner accounts for launched work.
    persist(
        "launching",
        identity_digest=identity_digest,
        clean=clean,
        launched=True,
    )
    try:
        completed = subprocess.run(target_argv, cwd=cwd, check=False)
    except OSError:
        persist(
            "launch-failed",
            reason_code="target-launch-failed",
            identity_digest=identity_digest,
            clean=clean,
            launched=True,
        )
        return 127
    target_exit = completed.returncode
    if target_exit < 0 or target_exit > 255:
        persist(
            "launch-failed",
            reason_code="target-exit-unrepresentable",
            identity_digest=identity_digest,
            clean=clean,
            launched=True,
        )
        return 127
    try:
        _expected, _observed, matches = compare_snapshot(repo, snapshot_path)
    except EvidenceError:
        matches = False
    if not matches:
        persist(
            "snapshot-drift",
            reason_code="repository-snapshot-drift",
            identity_digest=identity_digest,
            clean=clean,
            launched=True,
            exit_code=target_exit,
        )
        return 125
    persist(
        "completed",
        identity_digest=identity_digest,
        clean=clean,
        post_verified=True,
        launched=True,
        exit_code=target_exit,
    )
    return target_exit


def verify_snapshot_command(arguments: argparse.Namespace) -> None:
    _expected, observed, matches = compare_snapshot(
        Path(arguments.repo), Path(arguments.snapshot)
    )
    if arguments.output:
        atomic_write_json(Path(arguments.output), observed)
    if not matches:
        raise EvidenceError("repository snapshot identity drifted")


def relative_path(repo: Path, candidate: Path) -> str:
    try:
        return candidate.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return candidate.name


def tracked_git_state(repo: Path) -> dict[str, str]:
    values = run_git(repo, "rev-parse", "HEAD", "HEAD^{tree}").decode(
        "ascii", errors="strict"
    ).splitlines()
    if len(values) != 2:
        raise EvidenceError("cannot read Git state for selected input")
    return {"commit": values[0], "tree": values[1]}


def files_under(root: Path) -> Iterable[Path]:
    if root.is_file() or root.is_symlink():
        yield root
        return
    if not root.is_dir():
        return
    for directory, directories, filenames in os.walk(root):
        directories[:] = sorted(
            name for name in directories if name not in {".git", "__pycache__"}
        )
        for filename in sorted(filenames):
            candidate = Path(directory) / filename
            if candidate.is_file() and not candidate.is_symlink():
                yield candidate


def git_text(repo: Path, *arguments: str) -> str | None:
    try:
        return run_git(repo, *arguments).decode("utf-8", errors="replace")
    except EvidenceError:
        return None


def git_input_snapshot(repo: Path) -> dict[str, object] | None:
    index = git_text(repo, "ls-files", "-s")
    if index is None:
        return None
    tracked: dict[str, dict[str, str]] = {}
    for line in index.splitlines():
        try:
            metadata, path = line.split("\t", 1)
            mode, blob, _stage = metadata.split()
        except ValueError as exc:
            raise EvidenceError("cannot parse Git index entry") from exc
        tracked[path] = {"mode": mode, "blob": blob}
    modified = set()
    for arguments in (
        ("diff", "--name-only", "--no-renames"),
        ("diff", "--cached", "--name-only", "--no-renames"),
    ):
        changed = git_text(repo, *arguments)
        if changed is None:
            return None
        modified.update(path for path in changed.splitlines() if path)
    untracked = git_text(repo, "ls-files", "--others", "--exclude-standard")
    if untracked is None:
        return None
    return {
        "tracked": tracked,
        "modified": modified,
        "untracked": {path for path in untracked.splitlines() if path},
    }


def input_matches(path: str, token: str) -> bool:
    if any(marker in token for marker in "*?["):
        return fnmatch.fnmatchcase(path, token)
    return path == token or path.startswith(token.rstrip("/") + "/")


def file_record(repo: Path, path: str, file_records: dict[str, dict[str, object]]) -> dict[str, object]:
    if path in file_records:
        return file_records[path]
    candidate = repo / path
    if not candidate.is_file() or candidate.is_symlink():
        record = {"path": path, "state": "missing"}
    else:
        stat = candidate.stat()
        record = {
            "path": path,
            "sha256": sha256_bytes(candidate.read_bytes()),
            "mode": f"{stat.st_mode & 0o777:04o}",
        }
    file_records[path] = record
    return record


def selected_input_fingerprint(
    repo: Path,
    input_paths: str,
    file_records: dict[str, dict[str, object]] | None = None,
    git_snapshot: dict[str, object] | None = None,
) -> str:
    records: list[dict[str, object]] = []
    file_records = file_records if file_records is not None else {}
    for token in input_paths.split():
        if token == ".git":
            records.append({"path": ".git", "git": tracked_git_state(repo)})
            continue
        if git_snapshot is not None:
            tracked = git_snapshot["tracked"]
            modified = git_snapshot["modified"]
            untracked = git_snapshot["untracked"]
            selected_paths = sorted(
                {path for path in (*tracked, *untracked) if input_matches(path, token)},
                key=lambda item: item.encode("utf-8"),
            )
            if not selected_paths:
                records.append({"path": token, "state": "missing"})
                continue
            for path in selected_paths:
                if path in tracked and path not in modified:
                    records.append({"path": path, "git_blob": tracked[path]["blob"], "mode": tracked[path]["mode"]})
                else:
                    records.append(file_record(repo, path, file_records))
            continue
        candidates = sorted(repo.glob(token), key=lambda item: relative_path(repo, item).encode("utf-8")) if any(
            marker in token for marker in "*?["
        ) else [repo / token]
        existing = False
        for candidate in candidates:
            for path in files_under(candidate):
                existing = True
                records.append(file_record(repo, relative_path(repo, path), file_records))
        if not existing:
            records.append({"path": token, "state": "missing"})
    records.sort(key=lambda item: str(item["path"]).encode("utf-8"))
    return canonical_sha256({"schema_version": "selected-input/v2", "records": records})


def cache_key(
    validator_id: str,
    validator_version: str,
    profile: str,
    input_fingerprint: str,
    environment_class: str,
) -> str:
    return "|".join(
        (validator_id, validator_version, profile, input_fingerprint, environment_class)
    )


def load_cache(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"schema_version": CACHE_SCHEMA_VERSION, "entries": {}}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError("cannot read validation evidence cache") from exc
    if value.get("schema_version") != CACHE_SCHEMA_VERSION or not isinstance(value.get("entries"), dict):
        raise EvidenceError("validation evidence cache schema is invalid")
    return value


def iso_from_millis(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).isoformat().replace("+00:00", "Z")


def count_lines(value: bytes) -> int:
    return 0 if not value else value.count(b"\n") + (0 if value.endswith(b"\n") else 1)


def absolute_path_flavour(value: str) -> str | None:
    if PureWindowsPath(value).is_absolute():
        return "windows"
    if PurePosixPath(value).is_absolute():
        return "posix"
    return None


def privacy_safe_argument(value: str, cwd: Path) -> str:
    flavour = absolute_path_flavour(value)
    if flavour is not None:
        pure = PureWindowsPath(value) if flavour == "windows" else PurePosixPath(value)
        native = "windows" if os.name == "nt" else "posix"
        if flavour == native:
            try:
                relative = Path(value).resolve(strict=False).relative_to(cwd.resolve(strict=False))
            except (OSError, ValueError):
                pass
            else:
                relative_text = relative.as_posix()
                return "./" if relative_text == "." else f"./{relative_text}"
        return f"<absolute-path>/{pure.name or 'root'}"
    if "=" in value:
        prefix, candidate = value.split("=", 1)
        if absolute_path_flavour(candidate) is not None:
            return f"{prefix}={privacy_safe_argument(candidate, cwd)}"
    if WINDOWS_ABSOLUTE_FRAGMENT.search(value) or POSIX_ABSOLUTE_FRAGMENT.search(value):
        return "<argument-containing-absolute-path>"
    return value


def privacy_safe_argv(repo: Path, argv: list[str]) -> list[str]:
    return [privacy_safe_argument(argument, repo) for argument in argv]


def require_privacy_safe_string(value: str, description: str) -> None:
    if (
        absolute_path_flavour(value) is not None
        or WINDOWS_ABSOLUTE_FRAGMENT.search(value)
        or POSIX_ABSOLUTE_FRAGMENT.search(value)
    ):
        raise EvidenceError(f"{description} contains an absolute host path")


def validate_no_host_identity(value: object, description: str) -> None:
    if isinstance(value, str):
        require_privacy_safe_string(value, description)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_no_host_identity(item, f"{description}[{index}]")
        return
    if not isinstance(value, dict):
        return
    prohibited = {"pid", "process_id", "cwd", "log_path", "result_path", "host"}
    for key, item in value.items():
        if not isinstance(key, str) or key.lower() in prohibited:
            raise EvidenceError(f"{description} contains a prohibited host identity field")
        validate_no_host_identity(item, f"{description}.{key}")


def validate_relative_reference(value: object, description: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or absolute_path_flavour(value) is not None
        or ".." in PurePosixPath(value.replace("\\", "/")).parts
    ):
        raise EvidenceError(f"{description} is not a repository-relative reference")
    return Path(value).as_posix()


def validated_bootstrap_sidecar(
    repo: Path,
    sidecar_path: Path,
    snapshot_path: Path,
    *,
    expected_profile: str | None = None,
    expected_target_argv: list[str] | None = None,
) -> tuple[dict[str, Any], bytes]:
    sidecar_path = artifact_path_inside(repo, str(sidecar_path), "bootstrap sidecar")
    snapshot_path = artifact_path_inside(repo, str(snapshot_path), "bootstrap snapshot")
    content = sidecar_path.read_bytes() if sidecar_path.is_file() else b""
    if not content:
        raise EvidenceError("bootstrap sidecar is missing")
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise EvidenceError("bootstrap sidecar is malformed") from exc
    required = {
        "schema_version",
        "profile",
        "status",
        "reason_code",
        "snapshot_ref",
        "snapshot_identity_digest",
        "snapshot_clean",
        "post_verified",
        "target_argv",
        "target_argv_digest",
        "target_effective_argv_digest",
        "target_cwd_ref",
        "target_launched",
        "target_exit_code",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise EvidenceError("bootstrap sidecar schema is invalid")
    validate_no_host_identity(value, "bootstrap sidecar")
    if value.get("schema_version") != BOOTSTRAP_SCHEMA:
        raise EvidenceError("bootstrap sidecar version is invalid")
    profile = validate_record_token(value.get("profile"), "bootstrap sidecar profile")
    if expected_profile is not None and profile != expected_profile:
        raise EvidenceError("bootstrap sidecar profile does not match admission")
    status = value.get("status")
    if status not in {
        "capturing",
        "admission-rejected",
        "launching",
        "launch-failed",
        "snapshot-drift",
        "completed",
    }:
        raise EvidenceError("bootstrap sidecar status is invalid")
    reason_code = value.get("reason_code")
    if reason_code is not None:
        validate_record_token(reason_code, "bootstrap sidecar reason code")
    expected_snapshot_ref = relative_path(repo, snapshot_path)
    if (
        validate_relative_reference(value.get("snapshot_ref"), "bootstrap snapshot reference")
        != expected_snapshot_ref
    ):
        raise EvidenceError("bootstrap sidecar does not bind its snapshot output")
    identity_digest = value.get("snapshot_identity_digest")
    clean = value.get("snapshot_clean")
    post_verified = value.get("post_verified")
    target_argv = value.get("target_argv")
    target_exit = value.get("target_exit_code")
    if (
        identity_digest is not None and not is_sha256(identity_digest)
        or clean is not None and not isinstance(clean, bool)
        or not isinstance(post_verified, bool)
        or not isinstance(target_argv, list)
        or not target_argv
        or not all(isinstance(item, str) for item in target_argv)
        or value.get("target_argv_digest") != canonical_sha256(target_argv)
        or not is_sha256(value.get("target_effective_argv_digest"))
        or validate_relative_reference(value.get("target_cwd_ref"), "bootstrap target cwd")
        != "."
        or not isinstance(value.get("target_launched"), bool)
        or target_exit is not None
        and (not isinstance(target_exit, int) or isinstance(target_exit, bool))
    ):
        raise EvidenceError("bootstrap sidecar target or snapshot fields are invalid")
    for item in target_argv:
        require_privacy_safe_string(item, "bootstrap target argv")
    if expected_target_argv is not None:
        safe_expected = privacy_safe_argv(repo, expected_target_argv)
        if (
            target_argv != safe_expected
            or value["target_argv_digest"] != canonical_sha256(safe_expected)
            or value["target_effective_argv_digest"]
            != canonical_sha256(expected_target_argv)
        ):
            raise EvidenceError("bootstrap sidecar does not bind the expected target argv")

    if identity_digest is not None:
        snapshot = validated_snapshot(snapshot_path)
        if (
            snapshot["profile"] != profile
            or snapshot["identity_digest"] != identity_digest
            or snapshot["identity"]["clean"] is not clean
        ):
            raise EvidenceError("bootstrap sidecar snapshot identity is inconsistent")
    elif status == "admission-rejected" and reason_code == "snapshot-capture-failed":
        failure = load_json_object(snapshot_path, "bootstrap admission failure")
        if (
            set(failure)
            != {"schema_version", "profile", "status", "reason_code", "captured_at"}
            or failure.get("schema_version") != SNAPSHOT_ADMISSION_FAILURE_SCHEMA
            or failure.get("profile") != profile
            or failure.get("status") != "rejected"
            or failure.get("reason_code") != "snapshot-capture-failed"
        ):
            raise EvidenceError("bootstrap admission failure receipt is invalid")

    state_contracts: dict[str, tuple[set[str | None], bool, bool, bool]] = {
        # allowed reason codes, identity required, launched, exit required
        "capturing": ({None}, False, False, False),
        "admission-rejected": (
            {"snapshot-capture-failed", "repository-not-clean"}, False, False, False
        ),
        "launching": ({None}, True, True, False),
        "launch-failed": (
            {"target-launch-failed", "target-exit-unrepresentable"}, True, True, False
        ),
        "snapshot-drift": ({"repository-snapshot-drift"}, True, True, True),
        "completed": ({None}, True, True, True),
    }
    reasons, identity_required, launched, exit_required = state_contracts[status]
    if (
        reason_code not in reasons
        or value["target_launched"] is not launched
        or (target_exit is not None) is not exit_required
        or post_verified is not (status == "completed")
    ):
        raise EvidenceError("bootstrap sidecar state transition is inconsistent")
    if status == "admission-rejected":
        if reason_code == "repository-not-clean" and (
            identity_digest is None or clean is not False
        ):
            raise EvidenceError("dirty bootstrap rejection lacks its snapshot identity")
        if reason_code == "snapshot-capture-failed" and (
            identity_digest is not None or clean is not None
        ):
            raise EvidenceError("failed bootstrap capture claims a snapshot identity")
    elif identity_required and (identity_digest is None or not isinstance(clean, bool)):
        raise EvidenceError("bootstrap sidecar lacks its captured snapshot identity")
    return value, content


def raw_supervisor_timing(raw: dict[str, Any]) -> dict[str, int]:
    has_clock_adjustment = "clock_adjustment_seconds" in raw
    try:
        if (
            not isinstance(raw["started_at"], str)
            or not isinstance(raw["finished_at"], str)
            or not raw["started_at"].endswith("Z")
            or not raw["finished_at"].endswith("Z")
            or not isinstance(raw["duration_seconds"], (int, float))
            or isinstance(raw["duration_seconds"], bool)
            or not math.isfinite(float(raw["duration_seconds"]))
        ):
            raise ValueError("timestamps must be UTC Z values")
        started = datetime.fromisoformat(raw["started_at"].replace("Z", "+00:00"))
        finished = datetime.fromisoformat(raw["finished_at"].replace("Z", "+00:00"))
        raw_duration_ms = round(float(raw["duration_seconds"]) * 1000)
        if has_clock_adjustment:
            clock_adjustment = raw["clock_adjustment_seconds"]
            if (
                not isinstance(clock_adjustment, (int, float))
                or isinstance(clock_adjustment, bool)
                or not math.isfinite(float(clock_adjustment))
            ):
                raise ValueError("clock adjustment must be finite")
            clock_adjustment_ms = round(float(clock_adjustment) * 1000)
    except (KeyError, OverflowError, TypeError, ValueError) as exc:
        raise EvidenceError("raw supervisor timing is invalid") from exc
    started_ms = int(started.timestamp() * 1000)
    wall_completed_ms = int(finished.timestamp() * 1000)
    wall_duration_ms = wall_completed_ms - started_ms
    if raw_duration_ms < 0:
        raise EvidenceError("raw supervisor duration is inconsistent")
    if has_clock_adjustment:
        if abs((wall_duration_ms - raw_duration_ms) - clock_adjustment_ms) > 2:
            raise EvidenceError("raw supervisor clock adjustment is inconsistent")
        completed_ms = started_ms + raw_duration_ms
        duration_ms = raw_duration_ms
    else:
        completed_ms = wall_completed_ms
        duration_ms = wall_duration_ms
        if duration_ms < 0 or abs(duration_ms - raw_duration_ms) > 2:
            raise EvidenceError("raw supervisor duration is inconsistent")
    return {
        "started_ms": started_ms,
        "completed_ms": completed_ms,
        "duration_ms": duration_ms,
    }


def validate_raw_supervisor_binding(
    receipt: dict[str, Any], raw: dict[str, Any], log_content: bytes
) -> None:
    if raw.get("schema") != "validation-supervision/v1":
        raise EvidenceError("raw supervisor receipt schema is invalid")
    raw_status = raw.get("status")
    if raw_status not in {"completed", "timed-out", "cancelled", "cleanup-failed", "launch-failed"}:
        raise EvidenceError("raw supervisor receipt status is invalid")
    raw_argv = raw.get("argv")
    if not isinstance(raw_argv, list) or not raw_argv or not all(
        isinstance(item, str) for item in raw_argv
    ):
        raise EvidenceError("raw supervisor argv is invalid")
    for item in raw_argv:
        require_privacy_safe_string(item, "raw supervisor argv")
    raw_safe_digest = canonical_sha256(raw_argv)
    if raw.get("argv_sha256") != raw_safe_digest:
        raise EvidenceError("raw supervisor safe argv digest is invalid")
    effective_digest = raw.get("effective_argv_sha256", raw_safe_digest)
    if not is_sha256(effective_digest):
        raise EvidenceError("raw supervisor effective argv digest is invalid")
    command = receipt["command"]
    if (
        command["argv"] != raw_argv
        or command["argv_digest"] != raw_safe_digest
        or command.get("effective_argv_digest") != effective_digest
        or command["cwd_ref"] != raw.get("cwd_ref")
    ):
        raise EvidenceError("supervision wrapper command does not authenticate raw argv or cwd")
    raw_timeout = raw.get("timeout_seconds")
    raw_grace = raw.get("termination_grace_seconds")
    if (
        not isinstance(raw_timeout, (int, float))
        or isinstance(raw_timeout, bool)
        or not math.isfinite(raw_timeout)
        or raw_timeout <= 0
        or receipt.get("timeout_seconds") != raw_timeout
        or not isinstance(raw_grace, (int, float))
        or isinstance(raw_grace, bool)
        or not math.isfinite(raw_grace)
        or raw_grace < 0
        or receipt.get("termination_grace_seconds") != raw_grace
    ):
        raise EvidenceError("supervision wrapper timeout or grace does not authenticate raw receipt")
    if receipt["timing"] != raw_supervisor_timing(raw):
        raise EvidenceError("supervision wrapper timing does not authenticate raw receipt")
    raw_exit = raw.get("child_exit_code")
    if raw_exit is not None and (not isinstance(raw_exit, int) or isinstance(raw_exit, bool)):
        raise EvidenceError("raw supervisor child exit code is invalid")
    if receipt.get("exit_code") != raw_exit:
        raise EvidenceError("supervision wrapper exit code does not authenticate raw receipt")
    raw_log = raw.get("log")
    if (
        not isinstance(raw_log, dict)
        or not isinstance(raw_log.get("sealed"), bool)
        or raw_log.get("bytes") is not None
        and (
            not isinstance(raw_log.get("bytes"), int)
            or isinstance(raw_log.get("bytes"), bool)
            or raw_log["bytes"] < 0
        )
        or raw_log.get("lines") is not None
        and (
            not isinstance(raw_log.get("lines"), int)
            or isinstance(raw_log.get("lines"), bool)
            or raw_log["lines"] < 0
        )
    ):
        raise EvidenceError("raw supervisor log metadata is invalid")
    wrapper_log = receipt["log"]
    if raw_log["sealed"] is True:
        if (
            raw_log.get("sha256") != sha256_bytes(log_content)
            or raw_log.get("bytes") != len(log_content)
            or raw_log.get("lines") != count_lines(log_content)
            or any(wrapper_log.get(key) != raw_log.get(key) for key in ("sealed", "sha256", "bytes", "lines"))
        ):
            raise EvidenceError("supervision wrapper log does not authenticate raw receipt")
    elif (
        raw_log.get("sha256") is not None
        or raw_log.get("bytes") is not None
        or raw_log.get("lines") is not None
        or wrapper_log.get("sealed") is not False
    ):
        raise EvidenceError("unsealed raw supervisor log metadata is invalid")
    raw_platform = raw.get("platform")
    raw_termination = raw.get("termination")
    raw_error = raw.get("error")
    if (
        not isinstance(raw_platform, dict)
        or raw_platform.get("family") not in {"windows", "posix"}
        or not isinstance(raw_platform.get("mechanism"), str)
        or not raw_platform["mechanism"]
        or not isinstance(raw_termination, dict)
        or raw_termination.get("trigger") is not None
        and not isinstance(raw_termination.get("trigger"), str)
        or not all(
            isinstance(raw_termination.get(key), bool)
            for key in ("soft_signal_sent", "hard_kill_sent", "root_reaped", "tree_empty")
        )
        or raw_termination.get("active_processes") is not None
        and (
            not isinstance(raw_termination.get("active_processes"), int)
            or isinstance(raw_termination.get("active_processes"), bool)
            or raw_termination["active_processes"] < 0
        )
        or not isinstance(raw_termination.get("verification"), str)
        or not isinstance(raw_termination.get("errors"), list)
        or not all(isinstance(item, str) for item in raw_termination["errors"])
        or raw_error is not None
        and (
            not isinstance(raw_error, dict)
            or not isinstance(raw_error.get("stage"), str)
            or not isinstance(raw_error.get("type"), str)
        )
    ):
        raise EvidenceError("raw supervisor platform or termination proof is invalid")
    supervisor = receipt.get("supervisor")
    if supervisor != {
        "status": raw_status,
        "platform": raw_platform,
        "termination": raw_termination,
        "error": raw_error,
    }:
        raise EvidenceError("supervision wrapper proof does not authenticate raw receipt")
    execution = receipt.get("execution")
    if execution != {"launched": raw_status != "launch-failed"}:
        raise EvidenceError("supervision wrapper launch state does not authenticate raw receipt")
    snapshot = receipt["snapshot"]
    wrapper_status = receipt.get("status")
    bootstrap = receipt.get("bootstrap")
    if isinstance(bootstrap, dict):
        bootstrap_status = bootstrap.get("status")
        expected_status = (
            {
                "completed": "completed",
                "admission-rejected": "snapshot-drift",
                "snapshot-drift": "snapshot-drift",
                "launch-failed": "launch-failed",
            }.get(str(bootstrap_status))
            if raw_status == "completed"
            else raw_status
        )
        if expected_status is None or wrapper_status != expected_status:
            raise EvidenceError("bootstrap wrapper status does not authenticate raw receipt")
        if bootstrap_status == "completed" and raw.get("child_exit_code") != bootstrap.get(
            "target_exit_code"
        ):
            raise EvidenceError("bootstrap wrapper target exit does not bind the driver exit")
        expected_pre = is_sha256(bootstrap.get("snapshot_identity_digest"))
        expected_post = bootstrap_status == "completed"
        if (
            snapshot.get("pre_verified") is not expected_pre
            or snapshot.get("post_verified") is not expected_post
        ):
            raise EvidenceError("bootstrap wrapper snapshot verification state is invalid")
    elif wrapper_status == "snapshot-drift":
        if snapshot.get("pre_verified") is not True or snapshot.get("post_verified") is not False:
            raise EvidenceError("post-launch snapshot drift wrapper is invalid")
    elif wrapper_status != raw_status:
        raise EvidenceError("supervision wrapper status does not authenticate raw receipt")
    tree_empty = raw_termination.get("tree_empty") is True
    expected_cleanup = (
        "failed"
        if raw_status == "cleanup-failed" or not tree_empty
        else "completed"
        if raw_termination.get("trigger") is not None
        else "not-required"
    )
    if receipt.get("cleanup") != {"state": expected_cleanup, "tree_empty": tree_empty}:
        raise EvidenceError("supervision wrapper cleanup does not authenticate raw receipt")


def validated_supervision_receipt(
    repo: Path,
    result_path: Path,
    log_path: Path,
    snapshot_path: Path | None,
) -> tuple[dict[str, Any], bytes]:
    result_path = artifact_path_inside(repo, str(result_path), "supervision receipt")
    log_path = artifact_path_inside(repo, str(log_path), "supervision log")
    if snapshot_path is not None:
        snapshot_path = artifact_path_inside(repo, str(snapshot_path), "repository snapshot")
    result_content = result_path.read_bytes() if result_path.is_file() else b""
    if not result_content:
        raise EvidenceError("supervision receipt is missing")
    try:
        receipt = json.loads(result_content)
    except json.JSONDecodeError as exc:
        raise EvidenceError("supervision receipt is malformed") from exc
    if not isinstance(receipt, dict) or receipt.get("schema_version") != SUPERVISION_SCHEMA:
        raise EvidenceError("supervision receipt schema is invalid")
    validate_no_host_identity(receipt, "supervision receipt")
    status = receipt.get("status")
    if status not in {
        "completed",
        "timed-out",
        "snapshot-drift",
        "cleanup-failed",
        "launch-failed",
        "cancelled",
    }:
        raise EvidenceError("supervision receipt status is invalid")
    command = receipt.get("command")
    if (
        not isinstance(command, dict)
        or not isinstance(command.get("argv"), list)
        or not command["argv"]
        or not all(isinstance(item, str) for item in command["argv"])
    ):
        raise EvidenceError("supervision receipt command is invalid")
    for item in command["argv"]:
        require_privacy_safe_string(item, "supervision argv")
    validate_relative_reference(command.get("cwd_ref"), "supervision cwd")
    if command.get("argv_digest") != canonical_sha256(command["argv"]):
        raise EvidenceError("supervision argv digest is invalid")
    if command.get("effective_argv_digest") is not None and not is_sha256(
        command.get("effective_argv_digest")
    ):
        raise EvidenceError("supervision effective argv digest is invalid")
    timeout_seconds = receipt.get("timeout_seconds")
    accepted_child_exit_codes = receipt.get("accepted_child_exit_codes")
    grace_seconds = receipt.get("termination_grace_seconds")
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
        or not isinstance(accepted_child_exit_codes, list)
        or not accepted_child_exit_codes
        or any(
            not isinstance(code, int)
            or isinstance(code, bool)
            or code < 0
            or code > 255
            for code in accepted_child_exit_codes
        )
        or accepted_child_exit_codes != sorted(set(accepted_child_exit_codes))
        or grace_seconds is not None
        and (
            not isinstance(grace_seconds, (int, float))
            or isinstance(grace_seconds, bool)
            or not math.isfinite(grace_seconds)
            or grace_seconds < 0
        )
    ):
        raise EvidenceError("supervision timeout or grace is invalid")
    timing = receipt.get("timing")
    if (
        not isinstance(timing, dict)
        or not all(
            isinstance(timing.get(key), int) and not isinstance(timing.get(key), bool)
            for key in ("started_ms", "completed_ms", "duration_ms")
        )
        or timing["started_ms"] < 0
        or timing["completed_ms"] < timing["started_ms"]
        or timing["duration_ms"] != timing["completed_ms"] - timing["started_ms"]
    ):
        raise EvidenceError("supervision receipt timing is invalid")
    log = receipt.get("log")
    if not log_path.is_file():
        raise EvidenceError("supervision retained log is missing")
    content = log_path.read_bytes()
    if (
        not isinstance(log, dict)
        or validate_relative_reference(log.get("ref"), "supervision log") != relative_path(repo, log_path)
        or log.get("sha256") != sha256_bytes(content)
        or log.get("bytes") != len(content)
        or log.get("lines") != count_lines(content)
        or not isinstance(log.get("sealed"), bool)
    ):
        raise EvidenceError("supervision receipt does not bind the sealed log")
    snapshot = receipt.get("snapshot")
    if (
        not isinstance(snapshot, dict)
        or not is_sha256(snapshot.get("identity_digest"))
        or not isinstance(snapshot.get("pre_verified"), bool)
        or not isinstance(snapshot.get("post_verified"), bool)
        or (
            snapshot.get("observed_identity_digest") is not None
            and not is_sha256(snapshot.get("observed_identity_digest"))
        )
    ):
        raise EvidenceError("supervision receipt snapshot is invalid")
    if snapshot_path is not None:
        expected = validated_snapshot(snapshot_path)
        if snapshot.get("identity_digest") != expected["identity_digest"]:
            raise EvidenceError("supervision receipt snapshot identity is invalid")
    if snapshot.get("pre_verified") is True and snapshot.get("post_verified") is True:
        if snapshot.get("observed_identity_digest") != snapshot.get("identity_digest"):
            raise EvidenceError("supervision verified snapshot observations are inconsistent")
    bootstrap = receipt.get("bootstrap")
    if bootstrap is not None:
        sidecar_keys = {
            "schema_version",
            "profile",
            "status",
            "reason_code",
            "snapshot_ref",
            "snapshot_identity_digest",
            "snapshot_clean",
            "post_verified",
            "target_argv",
            "target_argv_digest",
            "target_effective_argv_digest",
            "target_cwd_ref",
            "target_launched",
            "target_exit_code",
        }
        if not isinstance(bootstrap, dict) or set(bootstrap) != sidecar_keys | {"sidecar"}:
            raise EvidenceError("supervision bootstrap proof schema is invalid")
        sidecar_record = bootstrap.get("sidecar")
        if (
            not isinstance(sidecar_record, dict)
            or set(sidecar_record) != {"ref", "sha256", "bytes"}
            or not is_sha256(sidecar_record.get("sha256"))
            or not isinstance(sidecar_record.get("bytes"), int)
            or isinstance(sidecar_record.get("bytes"), bool)
            or sidecar_record["bytes"] <= 0
        ):
            raise EvidenceError("supervision bootstrap sidecar artifact is invalid")
        sidecar_ref = validate_relative_reference(
            sidecar_record.get("ref"), "supervision bootstrap sidecar"
        )
        sidecar_path = artifact_path_inside(repo, sidecar_ref, "supervision bootstrap sidecar")
        sidecar_value, sidecar_content = validated_bootstrap_sidecar(
            repo,
            sidecar_path,
            snapshot_path if snapshot_path is not None else repo / str(bootstrap["snapshot_ref"]),
            expected_profile=str(bootstrap["profile"]),
        )
        if (
            sidecar_record["sha256"] != sha256_bytes(sidecar_content)
            or sidecar_record["bytes"] != len(sidecar_content)
            or {key: bootstrap[key] for key in sidecar_keys} != sidecar_value
        ):
            raise EvidenceError("supervision bootstrap proof does not authenticate its sidecar")
        if (
            snapshot.get("identity_digest") != bootstrap.get("snapshot_identity_digest")
            or snapshot.get("pre_verified")
            is not is_sha256(bootstrap.get("snapshot_identity_digest"))
            or snapshot.get("post_verified") is not bootstrap.get("post_verified")
        ):
            raise EvidenceError("supervision bootstrap proof does not bind wrapper snapshot state")
    cleanup = receipt.get("cleanup")
    if (
        not isinstance(cleanup, dict)
        or cleanup.get("state") not in {"not-required", "completed", "failed"}
        or not isinstance(cleanup.get("tree_empty"), bool)
    ):
        raise EvidenceError("supervision receipt cleanup state is invalid")
    execution = receipt.get("execution")
    if (
        not isinstance(execution, dict)
        or set(execution) != {"launched"}
        or not isinstance(execution.get("launched"), bool)
    ):
        raise EvidenceError("supervision receipt launch state is invalid")
    exit_code = receipt.get("exit_code")
    if exit_code is not None and (
        not isinstance(exit_code, int) or isinstance(exit_code, bool)
    ):
        raise EvidenceError("supervision receipt exit code is invalid")
    raw_reference = receipt.get("supervisor_receipt")
    if isinstance(raw_reference, dict):
        if not isinstance(raw_reference, dict):
            raise EvidenceError("supervision wrapper is missing the raw supervisor receipt")
        raw_ref = validate_relative_reference(
            raw_reference.get("ref"), "raw supervisor receipt"
        )
        raw_path = artifact_path_inside(repo, raw_ref, "raw supervisor receipt")
        raw_content = raw_path.read_bytes() if raw_path.is_file() else b""
        if (
            not raw_content
            or raw_reference.get("sha256") != sha256_bytes(raw_content)
            or raw_reference.get("bytes") != len(raw_content)
            or raw_reference.get("schema") != "validation-supervision/v1"
        ):
            raise EvidenceError("raw supervisor receipt is missing or tampered")
        try:
            raw_value = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise EvidenceError("raw supervisor receipt is malformed") from exc
        if not isinstance(raw_value, dict):
            raise EvidenceError("raw supervisor receipt contract is invalid")
        validate_no_host_identity(raw_value, "raw supervisor receipt")
        if (
            raw_reference.get("schema") != raw_value.get("schema")
            or raw_reference.get("status") != raw_value.get("status")
        ):
            raise EvidenceError("raw supervisor reference does not authenticate its receipt")
        validate_raw_supervisor_binding(receipt, raw_value, content)
    else:
        if execution["launched"] is not False:
            raise EvidenceError("launched supervision receipt is missing raw proof")
        common_prelaunch_invalid = (
            snapshot.get("post_verified") is not False
            or receipt.get("exit_code") is not None
            or cleanup != {"state": "not-required", "tree_empty": True}
            or raw_reference is not None
            or receipt.get("supervisor") is not None
        )
        if status == "snapshot-drift":
            if common_prelaunch_invalid or snapshot.get("pre_verified") is not False:
                raise EvidenceError("pre-launch snapshot drift receipt is invalid")
        elif status == "launch-failed":
            if common_prelaunch_invalid or snapshot.get("pre_verified") is not True:
                raise EvidenceError("pre-launch failure receipt is invalid")
        else:
            raise EvidenceError("supervision receipt without raw proof has invalid status")
    return receipt, result_content


def verify_supervision_result(arguments: argparse.Namespace) -> None:
    repo = repository_root(Path(arguments.repo))
    snapshot_path = artifact_path_inside(repo, arguments.snapshot, "repository snapshot")
    result_path = artifact_path_inside(repo, arguments.result_path, "supervision receipt")
    preliminary = load_json_object(result_path, "supervision receipt")
    log = preliminary.get("log")
    if not isinstance(log, dict):
        raise EvidenceError("supervision receipt log is invalid")
    log_ref = validate_relative_reference(log.get("ref"), "supervision log")
    log_path = artifact_path_inside(repo, log_ref, "supervision log")
    receipt, _content = validated_supervision_receipt(
        repo, result_path, log_path, snapshot_path
    )
    bootstrap = receipt.get("bootstrap")
    launched = receipt["execution"]["launched"]
    exit_code = receipt.get("exit_code")
    if isinstance(bootstrap, dict):
        launched = bootstrap["target_launched"]
        exit_code = bootstrap["target_exit_code"]
    print(
        "\t".join(
            (
                str(receipt["status"]),
                "true" if launched else "false",
                "" if exit_code is None else str(exit_code),
            )
        )
    )


def immutable_preparation_argv(python_executable: str, profile: str) -> list[str]:
    validate_record_token(python_executable, "preparation Python executable")
    validate_record_token(profile, "preparation profile")
    return [
        python_executable,
        IMMUTABLE_HISTORY_VALIDATOR_REF,
        "verify",
        "--repo",
        ".",
        "--profile",
        profile,
        "--output-format",
        "tsv",
    ]


def parse_immutable_preparation_log(content: bytes, exit_code: int) -> dict[str, object]:
    try:
        rendered = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise EvidenceError("immutable-history preparation output is not UTF-8") from exc
    lines = rendered.splitlines()
    if len(lines) != 1:
        raise EvidenceError("immutable-history preparation output must contain one TSV decision")
    fields = lines[0].split("\t")
    if len(fields) != 6:
        raise EvidenceError("immutable-history preparation decision is malformed")
    outcome, reason, source_revision, source_tree, receipt_commit, reusable_csv = fields
    validate_record_token(outcome, "immutable-history preparation outcome")
    validate_record_token(reason, "immutable-history preparation reason")
    reusable_ids = reusable_csv.split(",") if reusable_csv else []
    if any(not item for item in reusable_ids) or len(set(reusable_ids)) != len(reusable_ids):
        raise EvidenceError("immutable-history reusable validator ids are invalid")
    for validator_id in reusable_ids:
        validate_record_token(validator_id, "immutable-history reusable validator id")
    if exit_code == 0:
        if (
            outcome != "routine-reusable"
            or reason != "receipt-valid"
            or GIT_SHA_RE.fullmatch(source_revision) is None
            or GIT_SHA_RE.fullmatch(source_tree) is None
            or GIT_SHA_RE.fullmatch(receipt_commit) is None
            or not reusable_ids
        ):
            raise EvidenceError("immutable-history reusable decision is invalid")
    elif exit_code == 10:
        if outcome != "full-required" or reusable_ids:
            raise EvidenceError("immutable-history full-required decision is invalid")
        for value in (source_revision, source_tree, receipt_commit):
            if value and GIT_SHA_RE.fullmatch(value) is None:
                raise EvidenceError("immutable-history full-required identity is invalid")
    else:
        raise EvidenceError("immutable-history preparation exit code is unsupported")
    return {
        "outcome": outcome,
        "reason": reason,
        "source_revision": source_revision or None,
        "source_tree": source_tree or None,
        "receipt_commit": receipt_commit or None,
        "reusable_check_ids": reusable_ids,
    }


def immutable_history_fingerprint(decision: dict[str, object]) -> str:
    return sha256_bytes(
        "{}\n{}\n{}\n".format(
            decision["source_revision"],
            decision["source_tree"],
            decision["receipt_commit"],
        ).encode("utf-8")
    )


def validated_immutable_preparation(
    repo: Path,
    result_path: Path,
    snapshot_path: Path,
    profile: str,
    python_executable: str,
) -> tuple[dict[str, object], list[Path]]:
    result_path = artifact_path_inside(repo, str(result_path), "immutable preparation receipt")
    preliminary = load_json_object(result_path, "immutable preparation receipt")
    log_value = preliminary.get("log")
    if not isinstance(log_value, dict):
        raise EvidenceError("immutable preparation receipt log is invalid")
    log_ref = validate_relative_reference(log_value.get("ref"), "immutable preparation log")
    log_path = artifact_path_inside(repo, log_ref, "immutable preparation log")
    receipt, receipt_content = validated_supervision_receipt(
        repo, result_path, log_path, snapshot_path
    )
    expected_effective_argv = immutable_preparation_argv(python_executable, profile)
    command = receipt.get("command")
    if (
        not isinstance(command, dict)
        or command.get("effective_argv_digest") != canonical_sha256(expected_effective_argv)
        or command.get("cwd_ref") != "."
    ):
        raise EvidenceError("immutable preparation command does not match the exact verifier argv")
    if (
        receipt.get("status") != "completed"
        or receipt.get("exit_code") not in {0, 10}
        or receipt.get("accepted_child_exit_codes") != [0, 10]
        or receipt.get("execution") != {"launched": True}
        or receipt.get("cleanup") != {"state": "not-required", "tree_empty": True}
        or receipt.get("snapshot", {}).get("pre_verified") is not True
        or receipt.get("snapshot", {}).get("post_verified") is not True
        or receipt.get("log", {}).get("sealed") is not True
    ):
        raise EvidenceError("immutable preparation is not backed by a completed supervised verification")
    log_content = log_path.read_bytes()
    decision = parse_immutable_preparation_log(log_content, int(receipt["exit_code"]))
    raw_reference = receipt.get("supervisor_receipt")
    if not isinstance(raw_reference, dict):
        raise EvidenceError("immutable preparation lacks its raw supervisor receipt")
    raw_ref = validate_relative_reference(
        raw_reference.get("ref"), "immutable preparation raw receipt"
    )
    raw_path = artifact_path_inside(repo, raw_ref, "immutable preparation raw receipt")
    paths = [result_path, raw_path, log_path]
    tracked_receipt: dict[str, object] | None = None
    if decision["outcome"] == "routine-reusable":
        receipt_path = artifact_path_inside(
            repo, IMMUTABLE_HISTORY_RECEIPT_REF, "immutable-history tracked receipt"
        )
        tracked_receipt = repository_artifact_record(repo, receipt_path)
        paths.append(receipt_path)
    proof: dict[str, object] = {
        "kind": "immutable-history",
        "preparation_result": {
            **repository_artifact_record(repo, result_path),
            "status": receipt["status"],
            "exit_code": receipt["exit_code"],
        },
        "preparation_log": repository_artifact_record(repo, log_path),
        "raw_supervisor_receipt": repository_artifact_record(repo, raw_path),
        "decision": decision,
        "tracked_receipt": tracked_receipt,
    }
    if proof["preparation_result"]["sha256"] != sha256_bytes(receipt_content):
        raise EvidenceError("immutable preparation receipt changed while it was authenticated")
    return proof, paths


def control_role_argv(
    role: str,
    python_executable: str,
    context: dict[str, object],
) -> list[str]:
    validate_record_token(python_executable, "control Python executable")
    prefix = [python_executable, VALIDATION_EVIDENCE_HELPER_REF]
    if role == "bootstrap-snapshot":
        snapshot_ref = str(context["snapshot"])
        target_argv = [
            *prefix,
            "verify-snapshot",
            "--repo", ".",
            "--snapshot", snapshot_ref,
        ]
        bootstrap_result_ref = str(context["bootstrap_result"])
        return bootstrap_driver_argv(
            python_executable,
            snapshot_ref=snapshot_ref,
            profile=str(context["profile"]),
            sidecar_ref=f"{bootstrap_result_ref}.bootstrap.json",
            cwd_ref=".",
            require_clean=str(context["profile"]) in {"release", "nightly-full"},
            target_argv=target_argv,
        )
    if role == "prepare":
        return [
            *prefix,
            "prepare",
            "--repo", ".",
            "--cache", str(context["cache"]),
            "--profile", str(context["profile"]),
            "--environment-class", str(context["environment_class"]),
            "--selection", str(context["preparation_selection"]),
        ]
    if role == "post-snapshot":
        return [
            *prefix,
            "verify-snapshot",
            "--repo", ".",
            "--snapshot", str(context["snapshot"]),
            "--output", str(context["post_snapshot"]),
        ]
    if role == "finalize":
        argv = [
            *prefix,
            "finalize",
            "--repo", ".",
            "--cache", str(context["cache"]),
            "--evidence", str(context["evidence"]),
            "--events", str(context["events"]),
            "--invocation-id", str(context["invocation_id"]),
            "--profile", str(context["profile"]),
            "--environment-class", str(context["environment_class"]),
            "--snapshot", str(context["snapshot"]),
        ]
        preparation_python = context.get("preparation_python")
        if preparation_python:
            argv.extend(("--preparation-python", str(preparation_python)))
        return argv
    if role == "summarize":
        return [
            *prefix,
            "summarize",
            "--evidence", str(context["evidence"]),
            "--output", str(context["summary"]),
            "--invocation-id", str(context["invocation_id"]),
            "--profile", str(context["profile"]),
        ]
    if role == "workflow-summary":
        argv = [
            *prefix,
            "workflow-summary",
            "--evidence", str(context["evidence"]),
            "--output", str(context["workflow_summary"]),
            "--invocation-id", str(context["invocation_id"]),
            "--profile", str(context["profile"]),
            "--wall-span-ms", str(context["wall_span_ms"]),
        ]
        workflow_id = context.get("workflow_id")
        if workflow_id:
            argv.extend(("--workflow-id", str(workflow_id)))
        return argv
    raise EvidenceError("unknown supervised control role")


def validated_control_result(
    repo: Path,
    role: str,
    result_path: Path,
    snapshot_path: Path,
    expected_argv: list[str],
) -> tuple[dict[str, object], list[Path]]:
    result_path = artifact_path_inside(repo, str(result_path), f"{role} control receipt")
    preliminary = load_json_object(result_path, f"{role} control receipt")
    log_value = preliminary.get("log")
    if not isinstance(log_value, dict):
        raise EvidenceError(f"{role} control receipt log is invalid")
    log_ref = validate_relative_reference(log_value.get("ref"), f"{role} control log")
    log_path = artifact_path_inside(repo, log_ref, f"{role} control log")
    receipt, receipt_content = validated_supervision_receipt(
        repo, result_path, log_path, snapshot_path
    )
    command = receipt.get("command")
    if (
        not isinstance(command, dict)
        or command.get("effective_argv_digest") != canonical_sha256(expected_argv)
        or command.get("cwd_ref") != "."
    ):
        raise EvidenceError(f"{role} control command does not match its exact argv")
    if (
        receipt.get("status") != "completed"
        or receipt.get("exit_code") != 0
        or receipt.get("accepted_child_exit_codes") != [0]
        or receipt.get("execution") != {"launched": True}
        or receipt.get("cleanup") != {"state": "not-required", "tree_empty": True}
        or receipt.get("snapshot", {}).get("pre_verified") is not True
        or receipt.get("snapshot", {}).get("post_verified") is not True
        or receipt.get("log", {}).get("sealed") is not True
    ):
        raise EvidenceError(f"{role} control command lacks passing supervision proof")
    extra_paths: list[Path] = []
    bootstrap = receipt.get("bootstrap")
    if role == "bootstrap-snapshot":
        if not isinstance(bootstrap, dict) or "--" not in expected_argv:
            raise EvidenceError("bootstrap-snapshot control lacks its bootstrap proof")
        sidecar_record = bootstrap.get("sidecar")
        if not isinstance(sidecar_record, dict):
            raise EvidenceError("bootstrap-snapshot control sidecar is invalid")
        sidecar_ref = validate_relative_reference(
            sidecar_record.get("ref"), "bootstrap-snapshot control sidecar"
        )
        sidecar_path = artifact_path_inside(
            repo, sidecar_ref, "bootstrap-snapshot control sidecar"
        )
        target_argv = expected_argv[expected_argv.index("--") + 1 :]
        sidecar_value, _sidecar_content = validated_bootstrap_sidecar(
            repo,
            sidecar_path,
            snapshot_path,
            expected_profile=str(bootstrap["profile"]),
            expected_target_argv=target_argv,
        )
        if (
            bootstrap.get("status") != "completed"
            or bootstrap.get("target_launched") is not True
            or bootstrap.get("target_exit_code") != 0
            or bootstrap.get("post_verified") is not True
            or {key: bootstrap[key] for key in sidecar_value} != sidecar_value
        ):
            raise EvidenceError("bootstrap-snapshot control proof is not passing")
        extra_paths.append(sidecar_path)
    elif bootstrap is not None:
        raise EvidenceError(f"{role} control unexpectedly contains bootstrap proof")
    raw_reference = receipt.get("supervisor_receipt")
    if not isinstance(raw_reference, dict):
        raise EvidenceError(f"{role} control command lacks its raw supervisor receipt")
    raw_ref = validate_relative_reference(
        raw_reference.get("ref"), f"{role} control raw receipt"
    )
    raw_path = artifact_path_inside(repo, raw_ref, f"{role} control raw receipt")
    result_record = repository_artifact_record(repo, result_path)
    if result_record["sha256"] != sha256_bytes(receipt_content):
        raise EvidenceError(f"{role} control receipt changed while it was authenticated")
    return {
        "role": role,
        "result": {**result_record, "status": "completed", "exit_code": 0},
        "log": repository_artifact_record(repo, log_path),
        "raw_supervisor_receipt": repository_artifact_record(repo, raw_path),
        "command": receipt["command"],
        "timing": receipt["timing"],
    }, [result_path, log_path, raw_path, *extra_paths]


def artifact_path_inside(repo: Path, value: str, description: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = repo / candidate
    lexical_repo = Path(os.path.abspath(repo))
    lexical_candidate = Path(os.path.abspath(candidate))
    try:
        relative = lexical_candidate.relative_to(lexical_repo)
    except ValueError as exc:
        raise EvidenceError(f"{description} must remain inside the repository") from exc
    current = lexical_repo
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            raise EvidenceError(f"{description} cannot traverse a symlink")
    resolved = lexical_candidate.resolve()
    try:
        resolved.relative_to(repo.resolve())
    except ValueError as exc:
        raise EvidenceError(f"{description} resolves outside the repository") from exc
    return resolved


def supervision_log_record(repo: Path, log_path: Path, *, sealed: bool) -> dict[str, object]:
    content = log_path.read_bytes() if log_path.is_file() else b""
    return {
        "ref": relative_path(repo, log_path),
        "sha256": sha256_bytes(content),
        "bytes": len(content),
        "lines": count_lines(content),
        "sealed": sealed,
    }


def supervision_wrapper(
    *,
    repo: Path,
    status: str,
    argv: list[str],
    cwd_ref: str,
    timeout_seconds: float,
    accepted_child_exit_codes: list[int],
    termination_grace_seconds: float | None,
    started_ms: int,
    completed_ms: int,
    exit_code: int | None,
    log_path: Path,
    log_sealed: bool,
    snapshot_identity: str | None,
    pre_verified: bool,
    post_verified: bool,
    observed_identity: str | None,
    cleanup_state: str,
    tree_empty: bool,
    launched: bool,
    raw_receipt: dict[str, object] | None = None,
    bootstrap: dict[str, object] | None = None,
) -> dict[str, object]:
    safe_argv = privacy_safe_argv(repo, argv)
    value: dict[str, object] = {
        "schema_version": SUPERVISION_SCHEMA,
        "status": status,
        "command": {
            "argv": safe_argv,
            "argv_digest": canonical_sha256(safe_argv),
            "effective_argv_digest": canonical_sha256(argv),
            "cwd_ref": cwd_ref,
        },
        "timeout_seconds": timeout_seconds,
        "accepted_child_exit_codes": accepted_child_exit_codes,
        "termination_grace_seconds": termination_grace_seconds,
        "timing": {
            "started_ms": started_ms,
            "completed_ms": completed_ms,
            "duration_ms": completed_ms - started_ms,
        },
        "exit_code": exit_code,
        "cleanup": {"state": cleanup_state, "tree_empty": tree_empty},
        "execution": {"launched": launched},
        "log": supervision_log_record(repo, log_path, sealed=log_sealed),
        "snapshot": {
            "identity_digest": snapshot_identity,
            "pre_verified": pre_verified,
            "post_verified": post_verified,
            "observed_identity_digest": observed_identity,
        },
    }
    if raw_receipt is not None:
        value["supervisor_receipt"] = raw_receipt
    if bootstrap is not None:
        value["bootstrap"] = bootstrap
    return value


def supervise(arguments: argparse.Namespace) -> int:
    bootstrap_mode = bool(arguments.bootstrap_snapshot_output)
    if bootstrap_mode:
        # No Git subprocess may run in this outer adapter before containment.
        # The internal driver validates repository identity inside the process
        # tree owned by validation_process_supervisor.
        repo = Path(arguments.repo).resolve()
        if not repo.is_dir():
            raise EvidenceError("bootstrap repository root does not exist")
    else:
        repo = repository_root(Path(arguments.repo))
    log_path = artifact_path_inside(repo, arguments.log_path, "supervision log")
    result_path = artifact_path_inside(repo, arguments.result_path, "supervision result")
    raw_result_path = artifact_path_inside(
        repo, str(result_path) + ".process.json", "raw supervision receipt"
    )
    target_argv = list(arguments.command_argv)
    if target_argv and target_argv[0] == "--":
        target_argv = target_argv[1:]
    if not target_argv:
        raise EvidenceError("supervision command argv is empty")
    if arguments.timeout_seconds <= 0:
        raise EvidenceError("supervision timeout must be positive")
    accepted_child_exit_codes = sorted(set(arguments.accepted_child_exit_code))
    if (
        not accepted_child_exit_codes
        or any(code < 0 or code > 255 for code in accepted_child_exit_codes)
    ):
        raise EvidenceError("accepted child exit codes must be between 0 and 255")
    cwd_ref = validate_relative_reference(arguments.cwd_ref, "supervision cwd")
    cwd = artifact_path_inside(repo, cwd_ref, "supervision cwd")
    if not cwd.is_dir():
        raise EvidenceError("supervision cwd does not exist")

    bootstrap_sidecar_path: Path | None = None
    bootstrap_profile: str | None = None
    if bootstrap_mode:
        if not arguments.bootstrap_profile or not arguments.bootstrap_python:
            raise EvidenceError("bootstrap supervision requires profile and selected Python")
        bootstrap_profile = validate_record_token(arguments.bootstrap_profile, "bootstrap profile")
        snapshot_path = artifact_path_inside(
            repo, arguments.bootstrap_snapshot_output, "bootstrap snapshot output"
        )
        bootstrap_sidecar_path = artifact_path_inside(
            repo, str(result_path) + ".bootstrap.json", "bootstrap sidecar output"
        )
        if bootstrap_sidecar_path.exists():
            raise EvidenceError("bootstrap sidecar must not predate the supervised admission")
        actual_argv = bootstrap_driver_argv(
            arguments.bootstrap_python,
            snapshot_ref=relative_path(repo, snapshot_path),
            profile=bootstrap_profile,
            sidecar_ref=relative_path(repo, bootstrap_sidecar_path),
            cwd_ref=cwd_ref,
            require_clean=arguments.bootstrap_require_clean,
            target_argv=target_argv,
        )
    else:
        if (
            arguments.bootstrap_profile
            or arguments.bootstrap_python
            or arguments.bootstrap_require_clean
        ):
            raise EvidenceError("bootstrap-only arguments require bootstrap snapshot mode")
        snapshot_path = artifact_path_inside(repo, arguments.snapshot, "repository snapshot")
        actual_argv = target_argv

    started_ms = int(time.time() * 1000)
    expected_identity: str | None = None
    observed_identity: str | None = None
    if bootstrap_mode:
        pre_verified = True
    else:
        try:
            expected, observed, pre_verified = compare_snapshot(repo, snapshot_path)
            expected_identity = str(expected["identity_digest"])
            observed_identity = str(observed["identity_digest"])
        except EvidenceError:
            pre_verified = False
    if not pre_verified:
        atomic_write_bytes(log_path, b"validation supervision blocked: repository snapshot drift\n")
        completed_ms = int(time.time() * 1000)
        receipt = supervision_wrapper(
            repo=repo,
            status="snapshot-drift",
            argv=target_argv,
            cwd_ref=cwd_ref,
            timeout_seconds=arguments.timeout_seconds,
            accepted_child_exit_codes=accepted_child_exit_codes,
            termination_grace_seconds=None,
            started_ms=started_ms,
            completed_ms=max(started_ms, completed_ms),
            exit_code=None,
            log_path=log_path,
            log_sealed=True,
            snapshot_identity=expected_identity,
            pre_verified=False,
            post_verified=False,
            observed_identity=observed_identity,
            cleanup_state="not-required",
            tree_empty=True,
            launched=False,
        )
        atomic_write_json(result_path, receipt)
        return 128

    try:
        module = importlib.import_module("validation_process_supervisor")
        raw = module.supervise_command(
            actual_argv,
            cwd=cwd,
            cwd_ref=cwd_ref,
            log_path=log_path,
            result_path=raw_result_path,
            timeout_seconds=arguments.timeout_seconds,
        )
    except (ImportError, AttributeError):
        atomic_write_bytes(log_path, b"validation supervision failed before process launch\n")
        completed_ms = max(started_ms, int(time.time() * 1000))
        receipt = supervision_wrapper(
            repo=repo,
            status="launch-failed",
            argv=actual_argv,
            cwd_ref=cwd_ref,
            timeout_seconds=arguments.timeout_seconds,
            accepted_child_exit_codes=accepted_child_exit_codes,
            termination_grace_seconds=None,
            started_ms=started_ms,
            completed_ms=completed_ms,
            exit_code=None,
            log_path=log_path,
            log_sealed=True,
            snapshot_identity=expected_identity,
            pre_verified=not bootstrap_mode,
            post_verified=False,
            observed_identity=observed_identity,
            cleanup_state="not-required",
            tree_empty=True,
            launched=False,
        )
        atomic_write_json(result_path, receipt)
        return 127
    if not isinstance(raw, dict) or raw.get("schema") != "validation-supervision/v1":
        raise EvidenceError("process supervisor returned an invalid receipt")
    raw_content = raw_result_path.read_bytes() if raw_result_path.is_file() else b""
    if not raw_content:
        raise EvidenceError("process supervisor did not persist its receipt")
    try:
        persisted_raw = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise EvidenceError("process supervisor persisted a malformed receipt") from exc
    if persisted_raw != raw:
        raise EvidenceError("process supervisor return value and persisted receipt differ")
    validate_no_host_identity(raw, "process supervisor receipt")
    raw_argv = raw.get("argv")
    if (
        not isinstance(raw_argv, list)
        or not raw_argv
        or not all(isinstance(item, str) for item in raw_argv)
        or raw.get("argv_sha256") != canonical_sha256(raw_argv)
        or raw.get("effective_argv_sha256") != canonical_sha256(actual_argv)
    ):
        raise EvidenceError("process supervisor receipt does not bind safe and effective argv")
    for item in raw_argv:
        require_privacy_safe_string(item, "process supervisor argv")
    if raw.get("cwd_ref") != cwd_ref or raw.get("timeout_seconds") != arguments.timeout_seconds:
        raise EvidenceError("process supervisor receipt does not bind invocation parameters")
    raw_grace = raw.get("termination_grace_seconds")
    if (
        not isinstance(raw_grace, (int, float))
        or isinstance(raw_grace, bool)
        or not math.isfinite(raw_grace)
        or raw_grace < 0
    ):
        raise EvidenceError("process supervisor receipt grace interval is invalid")
    raw_log = raw.get("log")
    if not isinstance(raw_log, dict):
        raise EvidenceError("process supervisor receipt log is invalid")
    raw_status = raw.get("status")
    if raw_status not in {"completed", "timed-out", "cancelled", "cleanup-failed", "launch-failed"}:
        raise EvidenceError("process supervisor receipt status is invalid")
    termination = raw.get("termination")
    if not isinstance(termination, dict):
        raise EvidenceError("process supervisor receipt termination proof is invalid")
    log_content = log_path.read_bytes() if log_path.is_file() else b""
    log_sealed = raw_log.get("sealed") is True
    if log_sealed and (
        raw_log.get("sha256") != sha256_bytes(log_content)
        or raw_log.get("bytes") != len(log_content)
        or raw_log.get("lines") != count_lines(log_content)
    ):
        raise EvidenceError("process supervisor receipt does not bind its sealed log")

    bootstrap_proof: dict[str, object] | None = None
    if bootstrap_mode and bootstrap_sidecar_path is not None and bootstrap_sidecar_path.is_file():
        sidecar, sidecar_content = validated_bootstrap_sidecar(
            repo,
            bootstrap_sidecar_path,
            snapshot_path,
            expected_profile=bootstrap_profile,
            expected_target_argv=target_argv,
        )
        expected_identity = (
            str(sidecar["snapshot_identity_digest"])
            if is_sha256(sidecar.get("snapshot_identity_digest"))
            else None
        )
        post_verified = sidecar["post_verified"] is True
        observed_identity = expected_identity if post_verified else None
        bootstrap_proof = {
            **sidecar,
            "sidecar": {
                "ref": relative_path(repo, bootstrap_sidecar_path),
                "sha256": sha256_bytes(sidecar_content),
                "bytes": len(sidecar_content),
            },
        }
        if raw_status == "completed":
            status = {
                "completed": "completed",
                "admission-rejected": "snapshot-drift",
                "snapshot-drift": "snapshot-drift",
                "launch-failed": "launch-failed",
            }.get(str(sidecar["status"]), "cleanup-failed")
        else:
            status = str(raw_status)
    elif bootstrap_mode:
        post_verified = False
        status = str(raw_status) if raw_status != "completed" else "cleanup-failed"
    else:
        try:
            _expected, post, post_verified = compare_snapshot(repo, snapshot_path)
            observed_identity = str(post["identity_digest"])
        except EvidenceError:
            post_verified = False
            observed_identity = None
        status = (
            "snapshot-drift"
            if not post_verified and raw_status != "launch-failed"
            else str(raw_status)
        )
    raw_timing = raw_supervisor_timing(raw)
    started_ms = raw_timing["started_ms"]
    completed_ms = raw_timing["completed_ms"]
    tree_empty = termination.get("tree_empty") is True
    cleanup_state = (
        "failed"
        if raw_status == "cleanup-failed" or not tree_empty
        else "completed"
        if termination.get("trigger") is not None
        else "not-required"
    )
    raw_reference = {
        "ref": relative_path(repo, raw_result_path),
        "sha256": sha256_bytes(raw_content),
        "bytes": len(raw_content),
        "schema": raw["schema"],
        "status": raw_status,
    }
    receipt = supervision_wrapper(
        repo=repo,
        status=status,
        argv=raw_argv,
        cwd_ref=cwd_ref,
        timeout_seconds=arguments.timeout_seconds,
        accepted_child_exit_codes=accepted_child_exit_codes,
        termination_grace_seconds=float(raw_grace),
        started_ms=started_ms,
        completed_ms=completed_ms,
        exit_code=raw.get("child_exit_code") if isinstance(raw.get("child_exit_code"), int) else None,
        log_path=log_path,
        log_sealed=log_sealed,
        snapshot_identity=expected_identity,
        pre_verified=is_sha256(expected_identity),
        post_verified=post_verified,
        observed_identity=observed_identity,
        cleanup_state=cleanup_state,
        tree_empty=tree_empty,
        launched=raw_status != "launch-failed",
        raw_receipt=raw_reference,
        bootstrap=bootstrap_proof,
    )
    receipt["supervisor"] = {
        "status": raw_status,
        "platform": raw.get("platform"),
        "termination": termination,
        "error": raw.get("error"),
    }
    receipt["command"]["effective_argv_digest"] = raw["effective_argv_sha256"]
    validate_raw_supervisor_binding(receipt, raw, log_content)
    atomic_write_json(result_path, receipt)
    if bootstrap_proof is not None and bootstrap_proof["status"] == "admission-rejected":
        return 128
    if status == "snapshot-drift":
        return 125
    return {
        "completed": 0 if receipt["exit_code"] in accepted_child_exit_codes else 1,
        "timed-out": 124,
        "cleanup-failed": 126,
        "launch-failed": 127,
        "cancelled": 130,
    }[status]


def reusable_cache_log_ref(
    repo: Path,
    cache: dict[str, object] | None,
    *,
    validator_id: str,
    validator_version: str,
    profile: str,
    environment_class: str,
    input_fingerprint: str,
    cache_policy: str,
) -> str | None:
    if cache is None or cache_policy == "no-reuse":
        return None
    entry = cache["entries"].get(
        cache_key(
            validator_id,
            validator_version,
            profile,
            input_fingerprint,
            environment_class,
        )
    )
    if not isinstance(entry, dict) or entry.get("outcome") != "passed" or entry.get("eligible") is not True:
        return None
    try:
        normalized, _paths = validated_cache_reuse_source(
            repo,
            entry.get("reuse_source"),
            validator_id=validator_id,
            validator_version=validator_version,
            profile=profile,
            environment_class=environment_class,
            input_fingerprint=input_fingerprint,
        )
    except EvidenceError:
        return None
    return (
        str(entry["log_ref"])
        if entry.get("log_ref") == normalized["source_log"]["ref"]
        else None
    )


def lookup(arguments: argparse.Namespace) -> None:
    repo = Path(arguments.repo).resolve()
    fingerprint = selected_input_fingerprint(
        repo, arguments.input_paths, git_snapshot=git_input_snapshot(repo)
    )
    cache = (
        None
        if arguments.profile in {"release", "nightly-full"}
        else load_cache(Path(arguments.cache))
    )
    log_ref = reusable_cache_log_ref(
        repo,
        cache,
        validator_id=arguments.validator_id,
        validator_version=arguments.validator_version,
        profile=arguments.profile,
        environment_class=arguments.environment_class,
        input_fingerprint=fingerprint,
        cache_policy=arguments.cache_policy,
    )
    eligible = log_ref is not None
    print(f"{fingerprint}\t{'true' if eligible else 'false'}\t{log_ref or ''}")


def prepare(arguments: argparse.Namespace) -> None:
    repo = Path(arguments.repo).resolve()
    cache = (
        None
        if arguments.profile in {"release", "nightly-full"}
        else load_cache(Path(arguments.cache))
    )
    fingerprints: dict[str, str] = {}
    file_records: dict[str, dict[str, object]] = {}
    git_snapshot = git_input_snapshot(repo)
    for line in Path(arguments.selection).read_text(encoding="utf-8").splitlines():
        validator_id, validator_version, input_paths, cache_policy = line.split("\t", 3)
        if input_paths not in fingerprints:
            fingerprints[input_paths] = selected_input_fingerprint(
                repo, input_paths, file_records, git_snapshot
            )
        fingerprint = fingerprints[input_paths]
        log_ref = reusable_cache_log_ref(
            repo,
            cache,
            validator_id=validator_id,
            validator_version=validator_version,
            profile=arguments.profile,
            environment_class=arguments.environment_class,
            input_fingerprint=fingerprint,
            cache_policy=cache_policy,
        )
        eligible = log_ref is not None
        print(f"{validator_id}\t{fingerprint}\t{'true' if eligible else 'false'}\t{log_ref or ''}")


def validate_record_token(value: object, description: str) -> str:
    if not isinstance(value, str) or not value or "\t" in value or "\n" in value:
        raise EvidenceError(f"invalid {description}")
    return value


def validate_outcome_disposition(outcome: str, disposition: str) -> None:
    allowed = {
        "executed": {"passed", "failed", "blocked-by-environment"},
        "reused": {"passed"},
        "not-selected": {"not-applicable"},
        "not-executed": {
            "failed",
            "blocked-by-environment",
            "not-applicable",
            "deferred-with-owner",
        },
        "timed-out": {"failed"},
        "cancelled": {"failed"},
        "snapshot-drift": {"failed"},
    }
    if outcome not in allowed[disposition]:
        raise EvidenceError("outcome and execution disposition are inconsistent")


def build_record(arguments: argparse.Namespace) -> dict[str, Any]:
    if arguments.outcome not in OUTCOMES:
        raise EvidenceError(f"unsupported outcome: {arguments.outcome}")
    if arguments.disposition not in DISPOSITIONS:
        raise EvidenceError(f"unsupported execution disposition: {arguments.disposition}")
    validate_outcome_disposition(arguments.outcome, arguments.disposition)
    for value, description in (
        (arguments.invocation_id, "invocation id"),
        (arguments.validator_id, "validator id"),
        (arguments.validator_version, "validator version"),
        (arguments.profile, "profile"),
        (arguments.environment_class, "environment class"),
        (arguments.input_fingerprint, "input fingerprint"),
    ):
        validate_record_token(value, description)
    if not isinstance(arguments.cache_hit, bool):
        raise EvidenceError("invalid cache-hit state")
    enforcement = getattr(arguments, "enforcement", None)
    if enforcement not in {None, "required", "advisory"}:
        raise EvidenceError("invalid validation enforcement")
    if arguments.duration_ms < 0 or arguments.started_ms < 0 or arguments.completed_ms < arguments.started_ms:
        raise EvidenceError("invalid validation timing")
    if arguments.duration_ms != arguments.completed_ms - arguments.started_ms:
        raise EvidenceError("validation duration does not match timestamps")
    if arguments.suppressed_output_bytes < -1:
        raise EvidenceError("invalid suppressed output byte count")
    if not arguments.selection_reason or "\t" in arguments.selection_reason or "\n" in arguments.selection_reason:
        raise EvidenceError("invalid selection reason")
    if not arguments.changed_paths_digest:
        raise EvidenceError("missing changed paths digest")
    repo = Path(arguments.repo).resolve()
    log_path = Path(arguments.log_path)
    if not log_path.is_absolute():
        log_path = Path(arguments.evidence).parent / log_path
    log_path = artifact_path_inside(repo, str(log_path), "validation log")
    if not log_path.is_file():
        raise EvidenceError("validation log is missing")
    content = log_path.read_bytes()
    log_ref = relative_path(repo, log_path)
    runner_timing = {
        "started_ms": arguments.started_ms,
        "completed_ms": arguments.completed_ms,
        "duration_ms": arguments.duration_ms,
    }
    snapshot_argument = getattr(arguments, "snapshot", None)
    snapshot_path = (
        artifact_path_inside(repo, snapshot_argument, "repository snapshot")
        if snapshot_argument
        else None
    )
    result_argument = getattr(arguments, "result_path", None)
    result_path = Path(result_argument) if result_argument else None
    receipt: dict[str, Any] | None = None
    result_content = b""
    reuse_source: dict[str, object] | None = None
    if arguments.disposition == "reused":
        if arguments.cache_hit:
            if arguments.profile in {"release", "nightly-full"}:
                raise EvidenceError("terminal validation profiles forbid cache reuse")
            if result_path is not None:
                raise EvidenceError("cache reuse must not claim an immutable preparation result")
            cache = load_cache(Path(arguments.cache))
            entry = cache["entries"].get(
                cache_key(
                    arguments.validator_id,
                    arguments.validator_version,
                    arguments.profile,
                    arguments.input_fingerprint,
                    arguments.environment_class,
                )
            )
            if not isinstance(entry, dict) or entry.get("eligible") is not True or entry.get("outcome") != "passed":
                raise EvidenceError("cache reuse has no eligible sealed source")
            reuse_source, _reuse_paths = validated_cache_reuse_source(
                repo,
                entry.get("reuse_source"),
                validator_id=arguments.validator_id,
                validator_version=arguments.validator_version,
                profile=arguments.profile,
                environment_class=arguments.environment_class,
                input_fingerprint=arguments.input_fingerprint,
            )
            if entry.get("log_ref") != reuse_source["source_log"]["ref"]:
                raise EvidenceError("cache reuse entry log does not match its sealed source")
        else:
            preparation_python = getattr(arguments, "preparation_python", None)
            if result_path is None or snapshot_path is None or not preparation_python:
                raise EvidenceError(
                    "immutable-history reuse requires preparation result, Python identity, and snapshot"
                )
            if not result_path.is_absolute():
                result_path = Path(arguments.evidence).parent / result_path
            reuse_source, _reuse_paths = validated_immutable_preparation(
                repo,
                result_path,
                snapshot_path,
                arguments.profile,
                preparation_python,
            )
            decision = reuse_source["decision"]
            if (
                decision["outcome"] != "routine-reusable"
                or arguments.validator_id not in decision["reusable_check_ids"]
            ):
                raise EvidenceError("immutable-history preparation does not authorize this reuse")
            expected_fingerprint = immutable_history_fingerprint(decision)
            if arguments.input_fingerprint != expected_fingerprint:
                raise EvidenceError("immutable-history reuse fingerprint is invalid")
    elif arguments.cache_hit:
        raise EvidenceError("cache-hit state is only valid for cache reuse")

    requires_receipt = arguments.disposition in {
        "executed",
        "timed-out",
        "cancelled",
        "snapshot-drift",
    }
    execution_result_path = result_path if arguments.disposition != "reused" else None
    if requires_receipt and (execution_result_path is None or snapshot_path is None):
        raise EvidenceError("executed or drifted validation record requires receipt and repository snapshot")
    if execution_result_path is not None and snapshot_path is None:
        raise EvidenceError("supervision receipt requires repository snapshot binding")
    if execution_result_path is not None:
        if not execution_result_path.is_absolute():
            execution_result_path = Path(arguments.evidence).parent / execution_result_path
        receipt, result_content = validated_supervision_receipt(
            repo, execution_result_path, log_path, snapshot_path
        )
        timing = receipt["timing"]
        arguments.started_ms = timing["started_ms"]
        arguments.completed_ms = timing["completed_ms"]
        arguments.duration_ms = timing["duration_ms"]
        expected_status = {
            "timed-out": "timed-out",
            "cancelled": "cancelled",
            "snapshot-drift": "snapshot-drift",
        }.get(arguments.disposition)
        if expected_status is not None and receipt.get("status") != expected_status:
            raise EvidenceError("execution disposition does not match supervision receipt status")
        if arguments.disposition == "executed" and receipt.get("status") not in {
            "completed",
            "cleanup-failed",
        }:
            raise EvidenceError("executed disposition does not match supervision receipt status")
        if arguments.disposition == "not-executed" and (
            receipt.get("status") != "launch-failed"
            or receipt.get("execution") != {"launched": False}
        ):
            raise EvidenceError("not-executed receipt must prove a pre-launch failure")
    if arguments.disposition in {"not-selected"} and receipt is not None:
        raise EvidenceError("not-selected validation record cannot contain a supervision receipt")
    if arguments.disposition == "not-executed" and receipt is not None and receipt.get("status") != "launch-failed":
        raise EvidenceError("not-executed validation receipt has invalid status")
    if receipt is not None and arguments.disposition == "executed" and arguments.outcome == "passed":
        if (
            receipt.get("status") != "completed"
            or receipt.get("exit_code") not in receipt.get("accepted_child_exit_codes", [])
            or receipt["snapshot"].get("pre_verified") is not True
            or receipt["snapshot"].get("post_verified") is not True
            or receipt["cleanup"].get("state") == "failed"
            or receipt["cleanup"].get("tree_empty") is not True
            or receipt["log"].get("sealed") is not True
        ):
            raise EvidenceError("passing executed evidence is not backed by a passing supervision receipt")
    record_value = {
        "schema_version": SCHEMA_VERSION,
        "invocation_id": arguments.invocation_id,
        "validator_id": arguments.validator_id,
        "validator_version": arguments.validator_version,
        "profile": arguments.profile,
        "enforcement": enforcement,
        "input_fingerprint": arguments.input_fingerprint,
        "environment_class": arguments.environment_class,
        "started_at": iso_from_millis(arguments.started_ms),
        "completed_at": iso_from_millis(arguments.completed_ms),
        "duration_ms": arguments.duration_ms,
        "runner_timing": runner_timing,
        "outcome": arguments.outcome,
        "execution_disposition": arguments.disposition,
        "output_bytes": len(content),
        "output_lines": count_lines(content),
        "suppressed_output_bytes": (
            len(content)
            if arguments.suppressed_output_bytes == -1
            else arguments.suppressed_output_bytes
        ),
        # The aggregate runner can observe only the top-level process it starts.
        # Child scripts are not yet instrumented, so claiming a numeric nested
        # process total would be a proxy metric rather than execution evidence.
        "subprocess_count": None,
        "temp_repository_count": None,
        "retry_count": 0,
        "cache_hit": arguments.cache_hit,
        "log_ref": log_ref,
        "log_sha256": sha256_bytes(content),
        "selection_reason": arguments.selection_reason,
        "selection": {
            "changed_paths_digest": arguments.changed_paths_digest,
            "reason": arguments.selection_reason,
        },
        "metrics": {
            "output_bytes": {"availability": "observed", "value": len(content)},
            "output_lines": {"availability": "observed", "value": count_lines(content)},
            "suppressed_output_bytes": {
                "availability": "observed",
                "value": len(content)
                if arguments.suppressed_output_bytes == -1
                else arguments.suppressed_output_bytes,
            },
            "child_process_count": {
                "availability": "unavailable",
                "reason": "child-script-not-instrumented",
                "value": None,
            },
            "git_invocation_count": {
                "availability": "unavailable",
                "reason": "child-script-not-instrumented",
                "value": None,
            },
            "temp_repository_count": {
                "availability": "unavailable",
                "reason": "child-script-not-instrumented",
                "value": None,
            },
            "retry_count": {"availability": "observed", "value": 0},
        },
    }
    if receipt is not None and execution_result_path is not None:
        raw_reference = receipt.get("supervisor_receipt")
        record_value["execution"] = {
            "launched": receipt["execution"]["launched"],
            "receipt_ref": relative_path(repo, execution_result_path),
            "receipt_sha256": sha256_bytes(result_content),
            "command": receipt["command"],
            "timing": receipt["timing"],
            "timeout_seconds": receipt.get("timeout_seconds"),
            "accepted_child_exit_codes": receipt["accepted_child_exit_codes"],
            "status": receipt["status"],
            "exit_code": receipt.get("exit_code"),
            "cleanup": receipt["cleanup"],
            "snapshot": receipt["snapshot"],
            "artifacts": {
                "log": receipt["log"],
                "receipt": {
                    "ref": relative_path(repo, execution_result_path),
                    "sha256": sha256_bytes(result_content),
                    "bytes": len(result_content),
                },
                "raw_supervisor_receipt": raw_reference,
            },
        }
    if reuse_source is not None:
        record_value["reuse_source"] = reuse_source
    validate_evidence_record_core(
        record_value,
        profile=arguments.profile,
        invocation_id=arguments.invocation_id,
    )
    return record_value


def cache_promotable(record_value: dict[str, Any]) -> bool:
    return (
        record_value["execution_disposition"] == "executed"
        and record_value["outcome"] == "passed"
        and record_value["profile"] not in {"release", "nightly-full"}
    )


def cache_payload_with_promotions(
    repo: Path,
    cache_path: Path,
    records: list[dict[str, Any]],
    *,
    manifest_path: Path,
    manifest_content: bytes,
    manifest_payload: dict[str, Any],
    evidence_path: Path,
    snapshot_path: Path,
) -> dict[str, object] | None:
    promotions = [record_value for record_value in records if cache_promotable(record_value)]
    if not promotions:
        return None
    cache = load_cache(cache_path)
    manifest_artifacts = {
        item["ref"]: item for item in manifest_payload["artifacts"]
    }
    manifest_record = {
        "ref": relative_path(repo, manifest_path),
        "sha256": sha256_bytes(manifest_content),
        "bytes": len(manifest_content),
    }
    evidence_record = repository_artifact_record(repo, evidence_path)
    snapshot_record = repository_artifact_record(repo, snapshot_path)
    if (
        manifest_artifacts.get(evidence_record["ref"]) != evidence_record
        or manifest_artifacts.get(snapshot_record["ref"]) != snapshot_record
    ):
        raise EvidenceError("cache source evidence or snapshot is absent from pending seal")
    for record_value in promotions:
        log_path = artifact_path_inside(repo, record_value["log_ref"], "cache source log")
        log_record = repository_artifact_record(repo, log_path)
        if manifest_artifacts.get(log_record["ref"]) != log_record:
            raise EvidenceError("cache source log is absent from pending seal")
        reuse_source = {
            "kind": "cache",
            "source_manifest": manifest_record,
            "source_evidence": {
                **evidence_record,
                "record_sha256": canonical_sha256(record_value),
            },
            "source_snapshot": snapshot_record,
            "source_log": log_record,
        }
        cache["entries"][
            cache_key(
                record_value["validator_id"],
                record_value["validator_version"],
                record_value["profile"],
                record_value["input_fingerprint"],
                record_value["environment_class"],
            )
        ] = {
            "eligible": True,
            "outcome": "passed",
            "log_ref": record_value["log_ref"],
            "reuse_source": reuse_source,
        }
    return cache


def encode_evidence_records(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record_value, ensure_ascii=False, sort_keys=True) + "\n"
        for record_value in records
    ).encode("utf-8")


def record(arguments: argparse.Namespace) -> None:
    record_value = build_record(arguments)
    evidence = Path(arguments.evidence)
    existing = evidence.read_bytes() if evidence.is_file() else b""
    if existing and not existing.endswith(b"\n"):
        raise EvidenceError("existing validation evidence is not newline terminated")
    atomic_write_bytes(evidence, existing + encode_evidence_records([record_value]))


def parse_event_line(line: str) -> dict[str, Any]:
    fields = line.split("\t")
    if len(fields) not in {12, 13, 14}:
        raise EvidenceError("validation evidence event is malformed")
    (
        validator_id,
        validator_version,
        input_fingerprint,
        outcome,
        disposition,
        started_ms,
        completed_ms,
        cache_hit,
        log_path,
        suppressed_bytes,
        selection_reason,
        changed_paths_digest,
    ) = fields[:12]
    if cache_hit not in {"true", "false"}:
        raise EvidenceError("validation evidence event cache state is invalid")
    try:
        started = int(started_ms)
        completed = int(completed_ms)
        suppressed = int(suppressed_bytes)
    except ValueError as exc:
        raise EvidenceError("validation evidence event numeric field is invalid") from exc
    enforcement = fields[13] if len(fields) == 14 and fields[13] else None
    if enforcement not in {None, "required", "advisory"}:
        raise EvidenceError("validation evidence event enforcement is invalid")
    for value, description in (
        (validator_id, "event validator id"),
        (validator_version, "event validator version"),
        (input_fingerprint, "event input fingerprint"),
        (log_path, "event log path"),
        (selection_reason, "event selection reason"),
        (changed_paths_digest, "event changed paths digest"),
    ):
        validate_record_token(value, description)
    if not is_sha256(input_fingerprint):
        raise EvidenceError("validation evidence event input fingerprint is invalid")
    if outcome not in OUTCOMES or disposition not in DISPOSITIONS:
        raise EvidenceError("validation evidence event outcome or disposition is invalid")
    validate_outcome_disposition(outcome, disposition)
    if started < 0 or completed < started or suppressed < -1:
        raise EvidenceError("validation evidence event timing or output count is invalid")
    result_path = fields[12] if len(fields) >= 13 and fields[12] else None
    if result_path is not None:
        validate_record_token(result_path, "event result path")
    return {
        "validator_id": validator_id,
        "validator_version": validator_version,
        "input_fingerprint": input_fingerprint,
        "outcome": outcome,
        "disposition": disposition,
        "started_ms": started,
        "completed_ms": completed,
        "cache_hit": cache_hit == "true",
        "log_path": log_path,
        "suppressed_output_bytes": suppressed,
        "selection_reason": selection_reason,
        "changed_paths_digest": changed_paths_digest,
        "result_path": result_path,
        "enforcement": enforcement,
    }


def finalize(arguments: argparse.Namespace) -> None:
    try:
        event_lines = [
            line for line in Path(arguments.events).read_text(encoding="utf-8").splitlines() if line
        ]
    except OSError as exc:
        raise EvidenceError("cannot read validation evidence events") from exc
    events = [parse_event_line(line) for line in event_lines]
    validator_ids = [event["validator_id"] for event in events]
    if any(not validator_id for validator_id in validator_ids) or len(set(validator_ids)) != len(
        validator_ids
    ):
        raise EvidenceError("validation evidence events contain missing or duplicate validator ids")
    records: list[dict[str, Any]] = []
    for event in events:
        records.append(
            build_record(
                argparse.Namespace(
                    repo=arguments.repo,
                    cache=arguments.cache,
                    evidence=arguments.evidence,
                    invocation_id=arguments.invocation_id,
                    validator_id=event["validator_id"],
                    validator_version=event["validator_version"],
                    profile=arguments.profile,
                    environment_class=arguments.environment_class,
                    input_fingerprint=event["input_fingerprint"],
                    outcome=event["outcome"],
                    disposition=event["disposition"],
                    started_ms=event["started_ms"],
                    completed_ms=event["completed_ms"],
                    duration_ms=event["completed_ms"] - event["started_ms"],
                    suppressed_output_bytes=event["suppressed_output_bytes"],
                    subprocess_count=None,
                    cache_hit=event["cache_hit"],
                    log_path=event["log_path"],
                    selection_reason=event["selection_reason"],
                    changed_paths_digest=event["changed_paths_digest"],
                    result_path=event["result_path"],
                    enforcement=event["enforcement"],
                    snapshot=arguments.snapshot,
                    preparation_python=getattr(arguments, "preparation_python", None),
                )
            )
        )
    atomic_write_bytes(Path(arguments.evidence), encode_evidence_records(records))


def summary_payload(
    records: list[dict[str, Any]], *, invocation_id: str, profile: str
) -> dict[str, object]:
    dispositions = {
        disposition: sum(
            record["execution_disposition"] == disposition for record in records
        )
        for disposition in sorted(DISPOSITIONS)
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "invocation_id": invocation_id,
        "profile": profile,
        "records": len(records),
        "total_duration_ms": sum(record["duration_ms"] for record in records),
        "executed": dispositions["executed"],
        "reused": dispositions["reused"],
        "not_selected": dispositions["not-selected"],
        "dispositions": dispositions,
        "outcomes": {
            outcome: sum(record["outcome"] == outcome for record in records)
            for outcome in sorted(OUTCOMES)
        },
        "enforcement": enforcement_counts(records),
    }


def workflow_summary_payload(
    records: list[dict[str, Any]],
    *,
    invocation_id: str,
    profile: str,
    wall_span_ms: int,
    workflow_id: str | None,
) -> dict[str, object]:
    active_execution_ms = sum(
        int(record["duration_ms"])
        for record in records
        if record["execution_disposition"] == "executed"
    )
    dispositions = {
        disposition: sum(
            record["execution_disposition"] == disposition for record in records
        )
        for disposition in sorted(DISPOSITIONS)
    }
    return {
        "schema_version": "1.0.0",
        "invocation_id": invocation_id,
        "workflow_id": workflow_id,
        "profile": profile,
        "wall_span_ms": wall_span_ms,
        "segments": {
            "active_execution_ms": active_execution_ms,
            "external_wait_ms": None,
            "approval_wait_ms": None,
            "environment_retry_ms": None,
            "unknown_ms": max(0, wall_span_ms - active_execution_ms),
        },
        "validator_invocations": len(records),
        "executed_results": dispositions["executed"],
        "reused_results": dispositions["reused"],
        "not_selected_results": dispositions["not-selected"],
        "dispositions": dispositions,
        "outcomes": {
            outcome: sum(record["outcome"] == outcome for record in records)
            for outcome in sorted(OUTCOMES)
        },
        "enforcement": enforcement_counts(records),
        "retry_count": 0,
        "sub_agents": {"availability": "unavailable", "value": None},
        "observability": {"export_status": "unavailable", "trace_id": None},
    }


def evidence_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        values = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError("validation evidence records cannot be read") from exc
    if not all(isinstance(value, dict) for value in values):
        raise EvidenceError("validation evidence contains a non-object record")
    return values


def summarize(arguments: argparse.Namespace) -> None:
    records = evidence_records(Path(arguments.evidence))
    atomic_write_json(
        Path(arguments.output),
        summary_payload(
            records, invocation_id=arguments.invocation_id, profile=arguments.profile
        ),
    )


def workflow_summary(arguments: argparse.Namespace) -> None:
    if arguments.wall_span_ms < 0:
        raise EvidenceError("workflow wall span cannot be negative")
    workflow_id = arguments.workflow_id or None
    if workflow_id is not None:
        validate_record_token(workflow_id, "workflow id")
        require_privacy_safe_string(workflow_id, "workflow id")
    records = evidence_records(Path(arguments.evidence))
    atomic_write_json(
        Path(arguments.output),
        workflow_summary_payload(
            records,
            invocation_id=arguments.invocation_id,
            profile=arguments.profile,
            wall_span_ms=arguments.wall_span_ms,
            workflow_id=workflow_id,
        ),
    )


def repository_artifact_record(repo: Path, path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise EvidenceError("retained artifact cannot be a symlink")
    try:
        resolved = path.resolve(strict=True)
        reference = resolved.relative_to(repo.resolve()).as_posix()
    except (OSError, ValueError) as exc:
        raise EvidenceError("retained artifact is missing or outside the repository") from exc
    if not resolved.is_file():
        raise EvidenceError("retained artifact must be a regular non-symlink file")
    before = resolved.stat()
    content = resolved.read_bytes()
    after = resolved.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise EvidenceError("retained artifact changed while it was being sealed")
    return {"ref": reference, "sha256": sha256_bytes(content), "bytes": len(content)}


def invocation_manifest_artifacts(
    manifest: dict[str, Any], *, expected_sha256: str | None = None, expected_bytes: int | None = None,
    content: bytes | None = None, require_passing: bool = True,
) -> dict[str, dict[str, object]]:
    required = {
        "schema_version",
        "invocation_id",
        "profile",
        "outcome",
        "sealed_at",
        "repository",
        "cardinality",
        "control_plane",
        "terminal_supervision",
        "artifacts",
        "manifest_digest",
    }
    if set(manifest) != required or manifest.get("schema_version") != INVOCATION_SCHEMA:
        raise EvidenceError("source invocation manifest schema is invalid")
    validate_no_host_identity(manifest, "source invocation manifest")
    core = {key: manifest[key] for key in required if key != "manifest_digest"}
    if manifest.get("manifest_digest") != canonical_sha256(core):
        raise EvidenceError("source invocation manifest digest is invalid")
    if expected_sha256 is not None and (content is None or sha256_bytes(content) != expected_sha256):
        raise EvidenceError("source invocation manifest bytes do not match reuse proof")
    if expected_bytes is not None and (content is None or len(content) != expected_bytes):
        raise EvidenceError("source invocation manifest size does not match reuse proof")
    for key in ("invocation_id", "profile", "outcome", "sealed_at"):
        validate_record_token(manifest.get(key), f"source invocation {key}")
    if manifest["outcome"] not in {"passed", "failed", "blocked"}:
        raise EvidenceError("source invocation manifest outcome is invalid")
    if require_passing and manifest["outcome"] != "passed":
        raise EvidenceError("cache reuse source manifest is not passing")
    repository = manifest.get("repository")
    cardinality = manifest.get("cardinality")
    control_plane = manifest.get("control_plane")
    terminal_supervision = manifest.get("terminal_supervision")
    artifacts = manifest.get("artifacts")
    if (
        not isinstance(repository, dict)
        or not is_sha256(repository.get("pre_identity_digest"))
        or not is_sha256(repository.get("post_identity_digest"))
        or not is_sha256(repository.get("verified_identity_digest"))
        or not isinstance(repository.get("clean"), bool)
        or not isinstance(cardinality, dict)
        or not all(
            isinstance(cardinality.get(key), int)
            and not isinstance(cardinality.get(key), bool)
            and cardinality[key] >= 0
            for key in ("events", "evidence_records")
        )
        or cardinality["events"] != cardinality["evidence_records"]
        or not isinstance(control_plane, list)
        or not isinstance(terminal_supervision, dict)
        or not isinstance(artifacts, list)
    ):
        raise EvidenceError("source invocation manifest identity or cardinality is invalid")
    by_ref: dict[str, dict[str, object]] = {}
    for item in artifacts:
        if (
            not isinstance(item, dict)
            or set(item) != {"ref", "sha256", "bytes"}
            or not is_sha256(item.get("sha256"))
            or not isinstance(item.get("bytes"), int)
            or isinstance(item.get("bytes"), bool)
            or item["bytes"] < 0
        ):
            raise EvidenceError("source invocation manifest artifact is invalid")
        ref = validate_relative_reference(item.get("ref"), "source invocation artifact")
        if ref in by_ref:
            raise EvidenceError("source invocation manifest contains duplicate artifact refs")
        by_ref[ref] = item
    if list(by_ref) != sorted(by_ref, key=lambda value: value.encode("utf-8")):
        raise EvidenceError("source invocation manifest artifacts are not canonical")
    roles = [
        item.get("role") if isinstance(item, dict) else None
        for item in control_plane
    ]
    if roles != sorted(CONTROL_ROLES):
        raise EvidenceError("source invocation control roles are incomplete or noncanonical")
    for item in control_plane:
        if set(item) != {
            "role", "result", "log", "raw_supervisor_receipt", "command", "timing"
        }:
            raise EvidenceError("source invocation control proof schema is invalid")
        for field in ("result", "log", "raw_supervisor_receipt"):
            artifact = item.get(field)
            allowed = {"ref", "sha256", "bytes"}
            if field == "result":
                allowed |= {"status", "exit_code"}
            if (
                not isinstance(artifact, dict)
                or set(artifact) != allowed
                or not is_sha256(artifact.get("sha256"))
                or not isinstance(artifact.get("bytes"), int)
                or isinstance(artifact.get("bytes"), bool)
                or artifact["bytes"] < 0
                or field in {"result", "raw_supervisor_receipt"}
                and artifact["bytes"] == 0
            ):
                raise EvidenceError("source invocation control artifact is invalid")
            ref = validate_relative_reference(
                artifact.get("ref"), "source invocation control artifact"
            )
            expected_artifact = {
                "ref": ref,
                "sha256": artifact["sha256"],
                "bytes": artifact["bytes"],
            }
            if by_ref.get(ref) != expected_artifact:
                raise EvidenceError("source invocation control artifact is absent from its seal")
        result = item["result"]
        command = item.get("command")
        timing = item.get("timing")
        if result.get("status") != "completed" or result.get("exit_code") != 0:
            raise EvidenceError("source invocation control result is not passing")
        if (
            not isinstance(command, dict)
            or set(command) != {"argv", "argv_digest", "effective_argv_digest", "cwd_ref"}
            or not isinstance(command.get("argv"), list)
            or not command["argv"]
            or not all(isinstance(value, str) for value in command["argv"])
            or command.get("argv_digest") != canonical_sha256(command["argv"])
            or not is_sha256(command.get("effective_argv_digest"))
            or command.get("cwd_ref") != "."
        ):
            raise EvidenceError("source invocation control command is invalid")
        if (
            not isinstance(timing, dict)
            or set(timing) != {"started_ms", "completed_ms", "duration_ms"}
            or not all(
                isinstance(timing.get(key), int) and not isinstance(timing.get(key), bool)
                for key in timing
            )
            or timing["started_ms"] < 0
            or timing["completed_ms"] < timing["started_ms"]
            or timing["duration_ms"] != timing["completed_ms"] - timing["started_ms"]
        ):
            raise EvidenceError("source invocation control timing is invalid")
    if terminal_supervision.get("mode") == "direct":
        if set(terminal_supervision) != {"mode"}:
            raise EvidenceError("source invocation direct terminal proof is invalid")
    elif terminal_supervision.get("mode") == "supervised":
        if set(terminal_supervision) != {
            "mode",
            "result_ref",
            "log_ref",
            "raw_result_ref",
            "expected_effective_argv_digest",
        }:
            raise EvidenceError("source invocation terminal supervision schema is invalid")
        for field in ("result_ref", "log_ref", "raw_result_ref"):
            validate_relative_reference(
                terminal_supervision.get(field), "source invocation terminal supervision ref"
            )
        if not is_sha256(terminal_supervision.get("expected_effective_argv_digest")):
            raise EvidenceError("source invocation terminal supervision digest is invalid")
    else:
        raise EvidenceError("source invocation terminal supervision mode is invalid")
    return by_ref


def require_manifest_artifact(
    repo: Path,
    artifacts: dict[str, dict[str, object]],
    path: Path,
    description: str,
) -> dict[str, object]:
    observed = repository_artifact_record(repo, path)
    expected = artifacts.get(str(observed["ref"]))
    if expected != observed:
        raise EvidenceError(f"{description} is absent from or differs from its source seal")
    return observed


def validated_terminal_supervision(
    repo: Path,
    declaration: dict[str, object],
    snapshot_path: Path,
) -> list[Path]:
    if declaration.get("mode") == "direct":
        return []
    result_path = artifact_path_inside(
        repo, str(declaration["result_ref"]), "terminal seal supervision result"
    )
    log_path = artifact_path_inside(
        repo, str(declaration["log_ref"]), "terminal seal supervision log"
    )
    raw_path = artifact_path_inside(
        repo, str(declaration["raw_result_ref"]), "terminal seal raw supervision result"
    )
    expected_raw_path = artifact_path_inside(
        repo,
        str(result_path) + ".process.json",
        "terminal seal expected raw supervision result",
    )
    if raw_path != expected_raw_path:
        raise EvidenceError("terminal seal raw supervision ref is not deterministic")
    receipt, result_content = validated_supervision_receipt(
        repo, result_path, log_path, snapshot_path
    )
    raw_reference = receipt.get("supervisor_receipt")
    if (
        receipt.get("status") != "completed"
        or receipt.get("exit_code") != 0
        or receipt.get("accepted_child_exit_codes") != [0]
        or receipt.get("execution") != {"launched": True}
        or receipt.get("cleanup") != {"state": "not-required", "tree_empty": True}
        or receipt.get("snapshot", {}).get("pre_verified") is not True
        or receipt.get("snapshot", {}).get("post_verified") is not True
        or receipt.get("log", {}).get("sealed") is not True
        or receipt.get("command", {}).get("effective_argv_digest")
        != declaration.get("expected_effective_argv_digest")
        or not isinstance(raw_reference, dict)
        or raw_reference.get("ref") != relative_path(repo, raw_path)
    ):
        raise EvidenceError("terminal seal supervision proof is invalid")
    result_record = repository_artifact_record(repo, result_path)
    log_record = repository_artifact_record(repo, log_path)
    raw_record = repository_artifact_record(repo, raw_path)
    if (
        result_record["sha256"] != sha256_bytes(result_content)
        or log_record["sha256"] != receipt["log"]["sha256"]
        or log_record["bytes"] != receipt["log"]["bytes"]
        or raw_record["sha256"] != raw_reference.get("sha256")
        or raw_record["bytes"] != raw_reference.get("bytes")
    ):
        raise EvidenceError("terminal seal supervision artifacts changed while authenticated")
    return [result_path, log_path, raw_path]


def verify_terminal_invocation(arguments: argparse.Namespace) -> None:
    repo = repository_root(Path(arguments.repo))
    snapshot_path = artifact_path_inside(
        repo, arguments.snapshot, "terminal verification snapshot"
    )
    manifest_path = artifact_path_inside(
        repo, arguments.manifest, "staged invocation manifest"
    )
    result_path = artifact_path_inside(
        repo, arguments.result_path, "terminal seal supervision result"
    )
    supplied_argv = list(arguments.command_argv)
    if not supplied_argv or supplied_argv[0] != "--":
        raise EvidenceError("terminal verification requires an exact command argv boundary")
    expected_argv = supplied_argv[1:]
    if not expected_argv or not all(isinstance(value, str) and value for value in expected_argv):
        raise EvidenceError("terminal verification command argv is empty or invalid")

    initial_record = repository_artifact_record(repo, manifest_path)
    try:
        manifest_content = manifest_path.read_bytes()
        manifest = json.loads(manifest_content)
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError("staged invocation manifest cannot be read") from exc
    if (
        not isinstance(manifest, dict)
        or sha256_bytes(manifest_content) != initial_record["sha256"]
        or len(manifest_content) != initial_record["bytes"]
    ):
        raise EvidenceError("staged invocation manifest changed while being authenticated")
    invocation_manifest_artifacts(
        manifest,
        expected_sha256=str(initial_record["sha256"]),
        expected_bytes=int(initial_record["bytes"]),
        content=manifest_content,
        require_passing=False,
    )
    declaration = manifest.get("terminal_supervision")
    if (
        not isinstance(declaration, dict)
        or declaration.get("mode") != "supervised"
        or declaration.get("result_ref") != relative_path(repo, result_path)
        or declaration.get("expected_effective_argv_digest")
        != canonical_sha256(expected_argv)
    ):
        raise EvidenceError("staged invocation terminal declaration is incompatible")
    terminal_paths = validated_terminal_supervision(repo, declaration, snapshot_path)
    if result_path not in terminal_paths:
        raise EvidenceError("terminal verification did not authenticate the declared result")
    final_record = repository_artifact_record(repo, manifest_path)
    if final_record != initial_record:
        raise EvidenceError("staged invocation manifest drifted during terminal verification")
    try:
        final_content = manifest_path.read_bytes()
    except OSError as exc:
        raise EvidenceError("staged invocation manifest cannot be read back") from exc
    if (
        sha256_bytes(final_content) != initial_record["sha256"]
        or len(final_content) != initial_record["bytes"]
    ):
        raise EvidenceError("staged invocation manifest changed after terminal verification")
    print(initial_record["sha256"])


def validated_cache_reuse_source(
    repo: Path,
    proof: object,
    *,
    validator_id: str,
    validator_version: str,
    profile: str,
    environment_class: str,
    input_fingerprint: str,
) -> tuple[dict[str, object], list[Path]]:
    if not isinstance(proof, dict) or set(proof) != {
        "kind",
        "source_manifest",
        "source_evidence",
        "source_snapshot",
        "source_log",
    } or proof.get("kind") != "cache":
        raise EvidenceError("cache reuse source proof schema is invalid")
    for field in ("source_manifest", "source_snapshot", "source_log"):
        item = proof.get(field)
        if (
            not isinstance(item, dict)
            or set(item) != {"ref", "sha256", "bytes"}
            or not is_sha256(item.get("sha256"))
            or not isinstance(item.get("bytes"), int)
            or isinstance(item.get("bytes"), bool)
            or item["bytes"] < 0
        ):
            raise EvidenceError(f"cache reuse {field} proof is invalid")
    source_evidence = proof.get("source_evidence")
    if (
        not isinstance(source_evidence, dict)
        or set(source_evidence) != {"ref", "sha256", "bytes", "record_sha256"}
        or not is_sha256(source_evidence.get("sha256"))
        or not is_sha256(source_evidence.get("record_sha256"))
        or not isinstance(source_evidence.get("bytes"), int)
        or isinstance(source_evidence.get("bytes"), bool)
        or source_evidence["bytes"] <= 0
    ):
        raise EvidenceError("cache reuse source evidence proof is invalid")
    paths = {
        field: artifact_path_inside(repo, str(proof[field]["ref"]), f"cache reuse {field}")
        for field in ("source_manifest", "source_evidence", "source_snapshot", "source_log")
    }
    manifest_content = paths["source_manifest"].read_bytes() if paths["source_manifest"].is_file() else b""
    if not manifest_content:
        raise EvidenceError("cache reuse source manifest is missing")
    try:
        manifest = json.loads(manifest_content)
    except json.JSONDecodeError as exc:
        raise EvidenceError("cache reuse source manifest is malformed") from exc
    if not isinstance(manifest, dict):
        raise EvidenceError("cache reuse source manifest is not an object")
    artifacts = invocation_manifest_artifacts(
        manifest,
        expected_sha256=str(proof["source_manifest"]["sha256"]),
        expected_bytes=int(proof["source_manifest"]["bytes"]),
        content=manifest_content,
    )
    evidence_content = paths["source_evidence"].read_bytes() if paths["source_evidence"].is_file() else b""
    if (
        not evidence_content
        or sha256_bytes(evidence_content) != source_evidence["sha256"]
        or len(evidence_content) != source_evidence["bytes"]
    ):
        raise EvidenceError("cache reuse source evidence is missing or tampered")
    require_manifest_artifact(
        repo, artifacts, paths["source_evidence"], "cache reuse source evidence"
    )
    require_manifest_artifact(
        repo, artifacts, paths["source_snapshot"], "cache reuse source snapshot"
    )
    require_manifest_artifact(repo, artifacts, paths["source_log"], "cache reuse source log")
    try:
        source_records = [
            json.loads(line)
            for line in evidence_content.decode("utf-8", errors="strict").splitlines()
            if line.strip()
        ]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("cache reuse source evidence is malformed") from exc
    if (
        len(source_records) != manifest["cardinality"]["evidence_records"]
        or not all(isinstance(item, dict) for item in source_records)
    ):
        raise EvidenceError("cache reuse source evidence cardinality is invalid")
    source_ids: list[str] = []
    for source_record in source_records:
        validate_evidence_record_core(
            source_record,
            profile=str(manifest["profile"]),
            invocation_id=str(manifest["invocation_id"]),
        )
        source_ids.append(str(source_record["validator_id"]))
    if len(set(source_ids)) != len(source_ids):
        raise EvidenceError("cache reuse source evidence has duplicate validators")
    matches = [item for item in source_records if item["validator_id"] == validator_id]
    if len(matches) != 1:
        raise EvidenceError("cache reuse source evidence lacks one exact validator")
    source_record = matches[0]
    if canonical_sha256(source_record) != source_evidence["record_sha256"]:
        raise EvidenceError("cache reuse source record digest is invalid")
    if (
        source_record["validator_version"] != validator_version
        or source_record["profile"] != profile
        or source_record["environment_class"] != environment_class
        or source_record["input_fingerprint"] != input_fingerprint
        or source_record["outcome"] != "passed"
        or source_record["execution_disposition"] != "executed"
        or source_record.get("execution", {}).get("launched") is not True
        or profile in {"release", "nightly-full"}
    ):
        raise EvidenceError("cache reuse source validator identity is incompatible")
    log_observed = repository_artifact_record(repo, paths["source_log"])
    if (
        log_observed != proof["source_log"]
        or source_record["log_ref"] != log_observed["ref"]
        or source_record["log_sha256"] != log_observed["sha256"]
        or source_record["output_bytes"] != log_observed["bytes"]
    ):
        raise EvidenceError("cache reuse source log does not match its evidence record")
    snapshot_observed = repository_artifact_record(repo, paths["source_snapshot"])
    if snapshot_observed != proof["source_snapshot"]:
        raise EvidenceError("cache reuse source snapshot does not match its proof")
    terminal_paths = validated_terminal_supervision(
        repo,
        manifest["terminal_supervision"],
        paths["source_snapshot"],
    )
    execution_paths = validate_execution_binding(
        repo, paths["source_snapshot"], source_record, paths["source_log"]
    )
    for execution_path in execution_paths:
        require_manifest_artifact(
            repo, artifacts, execution_path, "cache reuse source execution artifact"
        )
    normalized: dict[str, object] = {
        "kind": "cache",
        "source_manifest": repository_artifact_record(repo, paths["source_manifest"]),
        "source_evidence": {
            **repository_artifact_record(repo, paths["source_evidence"]),
            "record_sha256": canonical_sha256(source_record),
        },
        "source_snapshot": snapshot_observed,
        "source_log": log_observed,
    }
    if normalized != proof:
        raise EvidenceError("cache reuse source proof does not match authenticated artifacts")
    return normalized, [*paths.values(), *execution_paths, *terminal_paths]


def enforcement_counts(records: list[dict[str, Any]]) -> dict[str, object]:
    return {
        level: {
            "records": sum(
                (record.get("enforcement") or "unbound") == level for record in records
            ),
            "outcomes": {
                outcome: sum(
                    (record.get("enforcement") or "unbound") == level
                    and record["outcome"] == outcome
                    for record in records
                )
                for outcome in sorted(OUTCOMES)
            },
        }
        for level in ("required", "advisory", "unbound")
    }


def parse_selected_checks(path: Path) -> dict[str, str]:
    selected: dict[str, str] = {}
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    except OSError as exc:
        raise EvidenceError("cannot read selected-checks artifact") from exc
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 2:
            raise EvidenceError("selected-checks artifact is malformed")
        validator_id = validate_record_token(fields[0], "selected validator id")
        reason = validate_record_token(fields[1], "selected validator reason")
        if validator_id in selected:
            raise EvidenceError("selected-checks artifact contains duplicate validator ids")
        selected[validator_id] = reason
    return selected


def parse_fingerprint_selection(path: Path) -> dict[str, tuple[str, str, str]]:
    contracts: dict[str, tuple[str, str, str]] = {}
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    except OSError as exc:
        raise EvidenceError("cannot read fingerprint-selection artifact") from exc
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 4 or any(not field for field in fields):
            raise EvidenceError("fingerprint-selection artifact is malformed")
        validator_id, validator_version, input_paths, cache_policy = fields
        for value, description in (
            (validator_id, "fingerprint validator id"),
            (validator_version, "fingerprint validator version"),
            (input_paths, "fingerprint input paths"),
            (cache_policy, "fingerprint cache policy"),
        ):
            validate_record_token(value, description)
        if validator_id in contracts:
            raise EvidenceError("fingerprint-selection artifact contains duplicate validator ids")
        contracts[validator_id] = (validator_version, input_paths, cache_policy)
    return contracts


def validate_prepare_control_log(
    repo: Path,
    control_entry: dict[str, object],
    preparation_contracts: dict[str, tuple[str, str, str]],
    records_by_id: dict[str, dict[str, Any]],
    standard_fingerprints: dict[str, str],
    *,
    cache_path: Path,
    profile: str,
    environment_class: str,
) -> set[Path]:
    log_record = control_entry.get("log")
    if not isinstance(log_record, dict):
        raise EvidenceError("prepare control log proof is missing")
    log_ref = validate_relative_reference(log_record.get("ref"), "prepare control log")
    log_path = artifact_path_inside(repo, log_ref, "prepare control log")
    try:
        lines = log_path.read_text(encoding="utf-8", errors="strict").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvidenceError("prepare control log is not readable UTF-8") from exc
    if set(preparation_contracts) != set(records_by_id):
        raise EvidenceError("preparation-selection validators do not match evidence")
    if len(lines) != len(preparation_contracts):
        raise EvidenceError("prepare control output cardinality does not match selection")
    cache = None if profile in {"release", "nightly-full"} else load_cache(cache_path)
    retained_cache_paths: set[Path] = set()
    for line, validator_id in zip(lines, preparation_contracts, strict=True):
        fields = line.split("\t")
        if len(fields) != 4:
            raise EvidenceError("prepare control output is malformed")
        observed_id, fingerprint, reusable_value, log_value = fields
        if observed_id != validator_id or reusable_value not in {"true", "false"}:
            raise EvidenceError("prepare control output order or reuse state is invalid")
        record_value = records_by_id[validator_id]
        if fingerprint != standard_fingerprints[validator_id]:
            raise EvidenceError("prepare control standard fingerprint is invalid")
        immutable_reused = (
            record_value["execution_disposition"] == "reused"
            and isinstance(record_value.get("reuse_source"), dict)
            and record_value["reuse_source"].get("kind") == "immutable-history"
        )
        if not immutable_reused and fingerprint != record_value["input_fingerprint"]:
            raise EvidenceError("prepare control fingerprint does not match evidence")
        reuse_source = record_value.get("reuse_source")
        cache_reused = (
            record_value["execution_disposition"] == "reused"
            and record_value["cache_hit"] is True
            and isinstance(reuse_source, dict)
            and reuse_source.get("kind") == "cache"
        )
        validator_version, _input_paths, cache_policy = preparation_contracts[validator_id]
        expected_log = reusable_cache_log_ref(
            repo,
            cache,
            validator_id=validator_id,
            validator_version=validator_version,
            profile=profile,
            environment_class=environment_class,
            input_fingerprint=fingerprint,
            cache_policy=cache_policy,
        )
        if (reusable_value == "true") is not (expected_log is not None):
            raise EvidenceError("prepare control reuse decision does not match authenticated cache")
        if log_value != (expected_log or ""):
            raise EvidenceError("prepare control reused log does not match authenticated cache")
        if expected_log is not None and cache is not None:
            entry = cache["entries"].get(
                cache_key(
                    validator_id,
                    validator_version,
                    profile,
                    fingerprint,
                    environment_class,
                )
            )
            if not isinstance(entry, dict):
                raise EvidenceError("prepare control authenticated cache entry disappeared")
            _normalized, source_paths = validated_cache_reuse_source(
                repo,
                entry.get("reuse_source"),
                validator_id=validator_id,
                validator_version=validator_version,
                profile=profile,
                environment_class=environment_class,
                input_fingerprint=fingerprint,
            )
            retained_cache_paths.update(source_paths)
        if cache_reused:
            source_log = reuse_source.get("source_log")
            if not isinstance(source_log, dict) or source_log.get("ref") != expected_log:
                raise EvidenceError("prepare cache reuse does not match evidence source")
    return retained_cache_paths


def validate_selection_comparison(
    path: Path,
    *,
    snapshot: dict[str, Any],
    changed_paths_content: bytes,
    records: list[dict[str, Any]],
) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvidenceError("cannot read selection comparison artifact") from exc
    if len(lines) != 1:
        raise EvidenceError("selection comparison must contain exactly one TSV record")
    fields = lines[0].split("\t")
    if len(fields) != 6:
        raise EvidenceError("selection comparison artifact is malformed")
    schema, mode, base, head, changed_digest, escalation_reason = fields
    if (
        schema != SELECTION_COMPARISON_SCHEMA
        or mode not in {"changed-path", "full", "escalated"}
        or GIT_SHA_RE.fullmatch(base) is None
        or GIT_SHA_RE.fullmatch(head) is None
        or not is_sha256(changed_digest)
        or head != snapshot["identity"]["commit"]
        or changed_digest != sha256_bytes(changed_paths_content)
    ):
        raise EvidenceError("selection comparison identity or digest is invalid")
    if mode == "changed-path":
        if snapshot["identity"].get("clean") is not True or escalation_reason:
            raise EvidenceError("changed-path selection requires a clean snapshot and empty escalation")
    else:
        validate_record_token(escalation_reason, "selection escalation reason")
        require_privacy_safe_string(escalation_reason, "selection escalation reason")
    if any(
        record["selection"]["changed_paths_digest"] != changed_digest
        for record in records
    ):
        raise EvidenceError("selection comparison digest does not match every evidence record")


def validate_evidence_record_core(
    record_value: dict[str, Any], *, profile: str, invocation_id: str
) -> None:
    required = {
        "schema_version",
        "invocation_id",
        "validator_id",
        "validator_version",
        "profile",
        "enforcement",
        "input_fingerprint",
        "environment_class",
        "started_at",
        "completed_at",
        "duration_ms",
        "runner_timing",
        "outcome",
        "execution_disposition",
        "output_bytes",
        "output_lines",
        "suppressed_output_bytes",
        "cache_hit",
        "log_ref",
        "log_sha256",
        "selection_reason",
        "selection",
        "metrics",
        "subprocess_count",
        "temp_repository_count",
        "retry_count",
    }
    if not required.issubset(record_value):
        raise EvidenceError("evidence record is missing required core fields")
    if set(record_value) - (required | {"execution", "reuse_source"}):
        raise EvidenceError("evidence record contains unsupported core fields")
    validate_no_host_identity(record_value, "evidence record")
    if (
        record_value["schema_version"] != SCHEMA_VERSION
        or record_value["profile"] != profile
        or record_value["invocation_id"] != invocation_id
    ):
        raise EvidenceError("evidence record schema, profile, or invocation is invalid")
    for key in (
        "invocation_id",
        "validator_id",
        "validator_version",
        "profile",
        "input_fingerprint",
        "environment_class",
        "selection_reason",
    ):
        validate_record_token(record_value[key], f"evidence {key}")
    if not is_sha256(record_value["input_fingerprint"]):
        raise EvidenceError("evidence record input fingerprint is invalid")
    if record_value["enforcement"] not in {None, "required", "advisory"}:
        raise EvidenceError("evidence record enforcement is invalid")
    outcome = record_value["outcome"]
    disposition = record_value["execution_disposition"]
    if outcome not in OUTCOMES or disposition not in DISPOSITIONS:
        raise EvidenceError("evidence record outcome or disposition is invalid")
    validate_outcome_disposition(outcome, disposition)
    runner_timing = record_value["runner_timing"]
    if (
        not isinstance(runner_timing, dict)
        or not all(
            isinstance(runner_timing.get(key), int)
            and not isinstance(runner_timing.get(key), bool)
            for key in ("started_ms", "completed_ms", "duration_ms")
        )
        or runner_timing["started_ms"] < 0
        or runner_timing["completed_ms"] < runner_timing["started_ms"]
        or runner_timing["duration_ms"]
        != runner_timing["completed_ms"] - runner_timing["started_ms"]
    ):
        raise EvidenceError("evidence record runner timing is invalid")
    execution = record_value.get("execution")
    reuse_source = record_value.get("reuse_source")
    effective_timing = execution.get("timing") if isinstance(execution, dict) else runner_timing
    if (
        not isinstance(effective_timing, dict)
        or not all(
            isinstance(effective_timing.get(key), int)
            and not isinstance(effective_timing.get(key), bool)
            for key in ("started_ms", "completed_ms", "duration_ms")
        )
        or effective_timing["started_ms"] < 0
        or effective_timing["completed_ms"] < effective_timing["started_ms"]
        or effective_timing["duration_ms"]
        != effective_timing["completed_ms"] - effective_timing["started_ms"]
        or not isinstance(record_value["duration_ms"], int)
        or isinstance(record_value["duration_ms"], bool)
        or record_value["duration_ms"] != effective_timing["duration_ms"]
        or record_value["started_at"] != iso_from_millis(effective_timing["started_ms"])
        or record_value["completed_at"] != iso_from_millis(effective_timing["completed_ms"])
    ):
        raise EvidenceError("evidence record effective timing is invalid")
    for key in ("output_bytes", "output_lines", "suppressed_output_bytes"):
        if (
            not isinstance(record_value[key], int)
            or isinstance(record_value[key], bool)
            or record_value[key] < 0
        ):
            raise EvidenceError(f"evidence record {key} is invalid")
    if record_value["suppressed_output_bytes"] > record_value["output_bytes"]:
        raise EvidenceError("evidence record suppressed output exceeds retained log")
    if not isinstance(record_value["cache_hit"], bool) or not is_sha256(
        record_value["log_sha256"]
    ):
        raise EvidenceError("evidence record cache or log digest is invalid")
    if (
        record_value["subprocess_count"] is not None
        or record_value["temp_repository_count"] is not None
        or not isinstance(record_value["retry_count"], int)
        or isinstance(record_value["retry_count"], bool)
        or record_value["retry_count"] != 0
    ):
        raise EvidenceError("evidence record unsupported proxy metrics are invalid")
    validate_relative_reference(record_value["log_ref"], "evidence log")
    selection = record_value["selection"]
    if (
        not isinstance(selection, dict)
        or selection.get("reason") != record_value["selection_reason"]
        or validate_record_token(
            selection.get("changed_paths_digest"), "evidence changed paths digest"
        )
        != selection.get("changed_paths_digest")
    ):
        raise EvidenceError("evidence record selection binding is invalid")
    expected_metrics = {
        "output_bytes": {"availability": "observed", "value": record_value["output_bytes"]},
        "output_lines": {"availability": "observed", "value": record_value["output_lines"]},
        "suppressed_output_bytes": {
            "availability": "observed",
            "value": record_value["suppressed_output_bytes"],
        },
        "child_process_count": {
            "availability": "unavailable",
            "reason": "child-script-not-instrumented",
            "value": None,
        },
        "git_invocation_count": {
            "availability": "unavailable",
            "reason": "child-script-not-instrumented",
            "value": None,
        },
        "temp_repository_count": {
            "availability": "unavailable",
            "reason": "child-script-not-instrumented",
            "value": None,
        },
        "retry_count": {"availability": "observed", "value": 0},
    }
    if record_value["metrics"] != expected_metrics:
        raise EvidenceError("evidence record metrics are invalid")
    if disposition in {"executed", "timed-out", "cancelled"}:
        if not isinstance(execution, dict) or execution.get("launched") is not True:
            raise EvidenceError("launched evidence record is missing execution proof")
    elif disposition == "snapshot-drift":
        if not isinstance(execution, dict) or not isinstance(execution.get("launched"), bool):
            raise EvidenceError("snapshot-drift evidence is missing its launch-state proof")
    elif disposition == "not-executed":
        if execution is not None and (
            not isinstance(execution, dict)
            or execution.get("launched") is not False
            or execution.get("status") != "launch-failed"
        ):
            raise EvidenceError("not-executed evidence contains invalid pre-launch proof")
    elif execution is not None:
        raise EvidenceError("non-launched evidence record contains execution proof")
    if execution is not None and (
        not isinstance(execution, dict) or not isinstance(execution.get("launched"), bool)
    ):
        raise EvidenceError("evidence execution launch state is invalid")
    if disposition == "reused":
        if not isinstance(reuse_source, dict) or reuse_source.get("kind") not in {
            "cache",
            "immutable-history",
        }:
            raise EvidenceError("reused evidence lacks an authenticated source")
        if record_value["cache_hit"] != (reuse_source.get("kind") == "cache"):
            raise EvidenceError("reused evidence cache state does not match its source kind")
    elif reuse_source is not None:
        raise EvidenceError("non-reused evidence contains a reuse source")


def validate_execution_binding(
    repo: Path,
    snapshot_path: Path,
    record_value: dict[str, Any],
    log_path: Path,
) -> list[Path]:
    execution = record_value.get("execution")
    disposition = record_value["execution_disposition"]
    requires_execution = disposition in {
        "executed",
        "timed-out",
        "cancelled",
        "snapshot-drift",
    }
    if execution is None:
        if requires_execution:
            raise EvidenceError("launched evidence record is missing execution binding")
        return []
    if not isinstance(execution, dict):
        raise EvidenceError("evidence execution binding is invalid")
    receipt_ref = validate_relative_reference(execution.get("receipt_ref"), "evidence receipt")
    receipt_path = artifact_path_inside(repo, receipt_ref, "evidence receipt")
    receipt, receipt_content = validated_supervision_receipt(
        repo, receipt_path, log_path, snapshot_path
    )
    raw_reference = receipt.get("supervisor_receipt")
    expected_execution = {
        "launched": receipt["execution"]["launched"],
        "receipt_ref": receipt_ref,
        "receipt_sha256": sha256_bytes(receipt_content),
        "command": receipt["command"],
        "timing": receipt["timing"],
        "timeout_seconds": receipt.get("timeout_seconds"),
        "accepted_child_exit_codes": receipt["accepted_child_exit_codes"],
        "status": receipt["status"],
        "exit_code": receipt.get("exit_code"),
        "cleanup": receipt["cleanup"],
        "snapshot": receipt["snapshot"],
        "artifacts": {
            "log": receipt["log"],
            "receipt": {
                "ref": receipt_ref,
                "sha256": sha256_bytes(receipt_content),
                "bytes": len(receipt_content),
            },
            "raw_supervisor_receipt": raw_reference,
        },
    }
    if execution != expected_execution:
        raise EvidenceError("evidence execution record does not match authenticated receipt")
    expected_status = {
        "timed-out": "timed-out",
        "cancelled": "cancelled",
        "snapshot-drift": "snapshot-drift",
    }.get(disposition)
    if expected_status is not None and receipt["status"] != expected_status:
        raise EvidenceError("evidence execution disposition does not match receipt")
    if disposition == "executed" and receipt["status"] not in {
        "completed",
        "cleanup-failed",
    }:
        raise EvidenceError("executed evidence disposition does not match receipt")
    if disposition in {"executed", "timed-out", "cancelled"} and execution["launched"] is not True:
        raise EvidenceError("launched evidence record lacks raw supervisor proof")
    if disposition == "not-executed" and (
        receipt["status"] != "launch-failed" or execution["launched"] is not False
    ):
        raise EvidenceError("not-executed evidence does not prove a launch failure")
    paths = [receipt_path]
    if isinstance(raw_reference, dict):
        raw_ref = validate_relative_reference(raw_reference.get("ref"), "raw supervisor receipt")
        paths.append(artifact_path_inside(repo, raw_ref, "raw supervisor receipt"))
    return paths


def validate_event_record_binding(
    repo: Path,
    evidence_path: Path,
    event: dict[str, Any],
    record_value: dict[str, Any],
) -> None:
    scalar_bindings = {
        "validator_id": "validator_id",
        "validator_version": "validator_version",
        "input_fingerprint": "input_fingerprint",
        "outcome": "outcome",
        "disposition": "execution_disposition",
        "cache_hit": "cache_hit",
        "selection_reason": "selection_reason",
        "enforcement": "enforcement",
    }
    if any(record_value[record_key] != event[event_key] for event_key, record_key in scalar_bindings.items()):
        raise EvidenceError("event and evidence record identity or outcome do not match")
    if record_value["runner_timing"] != {
        "started_ms": event["started_ms"],
        "completed_ms": event["completed_ms"],
        "duration_ms": event["completed_ms"] - event["started_ms"],
    }:
        raise EvidenceError("event and evidence runner timing do not match")
    expected_suppressed = (
        record_value["output_bytes"]
        if event["suppressed_output_bytes"] == -1
        else event["suppressed_output_bytes"]
    )
    if (
        record_value["suppressed_output_bytes"] != expected_suppressed
        or record_value["selection"]["changed_paths_digest"]
        != event["changed_paths_digest"]
    ):
        raise EvidenceError("event and evidence output or selection do not match")
    event_log = Path(event["log_path"])
    if not event_log.is_absolute():
        event_log = evidence_path.parent / event_log
    event_log = artifact_path_inside(repo, str(event_log), "event log")
    if relative_path(repo, event_log) != record_value["log_ref"]:
        raise EvidenceError("event and evidence log references do not match")
    execution = record_value.get("execution")
    reuse_source = record_value.get("reuse_source")
    if event["result_path"]:
        event_result = Path(event["result_path"])
        if not event_result.is_absolute():
            event_result = evidence_path.parent / event_result
        event_result = artifact_path_inside(repo, str(event_result), "event result")
        event_ref = relative_path(repo, event_result)
        if record_value["execution_disposition"] == "reused":
            preparation = reuse_source.get("preparation_result") if isinstance(reuse_source, dict) else None
            if (
                not isinstance(preparation, dict)
                or reuse_source.get("kind") != "immutable-history"
                or event_ref != preparation.get("ref")
            ):
                raise EvidenceError("event and immutable reuse preparation references do not match")
        elif not isinstance(execution, dict) or event_ref != execution.get("receipt_ref"):
            raise EvidenceError("event and evidence result references do not match")
    elif execution is not None or (
        isinstance(reuse_source, dict) and reuse_source.get("kind") == "immutable-history"
    ):
        raise EvidenceError("evidence receipt exists without an event result reference")


def passing_record_allowed(record_value: dict[str, Any]) -> bool:
    if record_value["enforcement"] not in {"required", "advisory"}:
        return False
    if record_value["outcome"] == "blocked-by-environment":
        return False
    if record_value["execution_disposition"] in {"timed-out", "cancelled", "snapshot-drift"}:
        return False
    if record_value["outcome"] in {"passed", "not-applicable"}:
        return True
    return (
        record_value["enforcement"] == "advisory"
        and record_value["outcome"] in {"failed", "deferred-with-owner"}
    )


def validate_record_reuse_source(
    repo: Path,
    snapshot_path: Path,
    record_value: dict[str, Any],
    immutable_preparations: dict[str, tuple[dict[str, object], list[Path]]],
) -> list[Path]:
    proof = record_value.get("reuse_source")
    if record_value["execution_disposition"] != "reused":
        if proof is not None:
            raise EvidenceError("non-reused record contains a reuse source")
        return []
    if not isinstance(proof, dict):
        raise EvidenceError("reused record lacks a reuse source proof")
    if proof.get("kind") == "cache":
        normalized, paths = validated_cache_reuse_source(
            repo,
            proof,
            validator_id=record_value["validator_id"],
            validator_version=record_value["validator_version"],
            profile=record_value["profile"],
            environment_class=record_value["environment_class"],
            input_fingerprint=record_value["input_fingerprint"],
        )
        if normalized != proof or record_value["cache_hit"] is not True:
            raise EvidenceError("cache reuse proof is inconsistent")
        return paths
    if proof.get("kind") != "immutable-history" or record_value["cache_hit"] is not False:
        raise EvidenceError("reused record source kind or cache state is invalid")
    preparation = proof.get("preparation_result")
    if not isinstance(preparation, dict):
        raise EvidenceError("immutable reuse preparation proof is missing")
    preparation_ref = validate_relative_reference(
        preparation.get("ref"), "immutable reuse preparation receipt"
    )
    authenticated = immutable_preparations.get(preparation_ref)
    if authenticated is None:
        raise EvidenceError("immutable reuse does not reference a sealed preparation result")
    normalized, paths = authenticated
    if normalized != proof:
        raise EvidenceError("immutable reuse proof differs from its authenticated preparation")
    decision = normalized["decision"]
    if (
        decision["outcome"] != "routine-reusable"
        or record_value["validator_id"] not in decision["reusable_check_ids"]
    ):
        raise EvidenceError("immutable preparation does not authorize reused validator")
    expected_fingerprint = immutable_history_fingerprint(decision)
    if record_value["input_fingerprint"] != expected_fingerprint:
        raise EvidenceError("immutable reused validator fingerprint is invalid")
    validated_snapshot(snapshot_path)
    return paths


def seal_invocation(arguments: argparse.Namespace) -> None:
    repo = repository_root(Path(arguments.repo))
    snapshot_path = artifact_path_inside(repo, arguments.snapshot, "repository snapshot")
    post_snapshot_path = artifact_path_inside(
        repo, arguments.post_snapshot, "post repository snapshot"
    )
    expected, current, matches = compare_snapshot(repo, snapshot_path)
    post_snapshot = validated_snapshot(post_snapshot_path)
    if not matches or post_snapshot["identity_digest"] != expected["identity_digest"]:
        raise EvidenceError("repository snapshot drift prevents invocation sealing")
    if arguments.outcome == "passed" and expected["profile"] in {"release", "nightly-full"}:
        if expected["identity"].get("clean") is not True:
            raise EvidenceError("terminal passing invocation requires a clean repository snapshot")

    profile = str(expected["profile"])
    invocation_id = validate_record_token(arguments.invocation_id, "seal invocation id")
    control_python = validate_record_token(
        arguments.control_python, "supervised control Python executable"
    )
    control_values = list(arguments.control_result or ())
    control_result_values: dict[str, str] = {}
    for pair in control_values:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise EvidenceError("supervised control result argument is malformed")
        role, result_value = pair
        if role not in CONTROL_ROLES:
            raise EvidenceError("unknown supervised control role")
        if role in control_result_values:
            raise EvidenceError("duplicate supervised control role")
        control_result_values[role] = validate_record_token(
            result_value, f"{role} control result path"
        )
    if set(control_result_values) != CONTROL_ROLES:
        raise EvidenceError("supervised control roles are incomplete")
    preparation_python = getattr(arguments, "preparation_python", None)
    preparation_results = list(getattr(arguments, "preparation_result", ()) or ())
    if preparation_results and not preparation_python:
        raise EvidenceError("preparation results require the selected Python executable identity")
    immutable_preparations: dict[str, tuple[dict[str, object], list[Path]]] = {}
    preparation_artifact_paths: set[Path] = set()
    for preparation_value in preparation_results:
        preparation_path = artifact_path_inside(
            repo, preparation_value, "invocation preparation result"
        )
        proof, proof_paths = validated_immutable_preparation(
            repo,
            preparation_path,
            snapshot_path,
            profile,
            preparation_python,
        )
        preparation_ref = str(proof["preparation_result"]["ref"])
        if preparation_ref in immutable_preparations:
            raise EvidenceError("duplicate invocation preparation result")
        immutable_preparations[preparation_ref] = (proof, proof_paths)
        preparation_artifact_paths.update(proof_paths)
    evidence_path = artifact_path_inside(repo, arguments.evidence, "evidence artifact")
    events_path = artifact_path_inside(repo, arguments.events, "event artifact")
    try:
        evidence_lines = [
            line for line in evidence_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        event_lines = [
            line for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
    except OSError as exc:
        raise EvidenceError("cannot read evidence or event artifacts") from exc
    if len(evidence_lines) != len(event_lines):
        raise EvidenceError("evidence and event cardinality do not match")
    try:
        evidence_records = [json.loads(line) for line in evidence_lines]
    except json.JSONDecodeError as exc:
        raise EvidenceError("evidence artifact contains malformed JSON") from exc
    if not all(isinstance(record, dict) for record in evidence_records):
        raise EvidenceError("evidence artifact contains a non-object record")
    events = [parse_event_line(line) for line in event_lines]
    record_ids = [record.get("validator_id") for record in evidence_records]
    event_ids = [event["validator_id"] for event in events]
    if (
        any(not validator_id for validator_id in (*record_ids, *event_ids))
        or len(set(record_ids)) != len(record_ids)
        or len(set(event_ids)) != len(event_ids)
    ):
        raise EvidenceError("events or evidence contain missing or duplicate validator ids")
    if record_ids != event_ids:
        raise EvidenceError("events and evidence validators are not bound one-to-one in order")
    for event, record_value in zip(events, evidence_records, strict=True):
        validate_evidence_record_core(
            record_value, profile=profile, invocation_id=invocation_id
        )
        validate_event_record_binding(repo, evidence_path, event, record_value)
    changed_paths_path = artifact_path_inside(
        repo, arguments.changed_paths, "changed paths artifact"
    )
    selection_comparison_path = artifact_path_inside(
        repo, arguments.selection_comparison, "selection comparison artifact"
    )
    try:
        changed_paths_content = changed_paths_path.read_bytes()
    except OSError as exc:
        raise EvidenceError("cannot read changed paths artifact") from exc
    validate_selection_comparison(
        selection_comparison_path,
        snapshot=expected,
        changed_paths_content=changed_paths_content,
        records=evidence_records,
    )
    if arguments.outcome == "passed" and any(
        not passing_record_allowed(record_value) for record_value in evidence_records
    ):
        raise EvidenceError("passing invocation seal contains a disallowed evidence result")

    summary_path = artifact_path_inside(repo, arguments.summary, "summary artifact")
    workflow_summary_path = artifact_path_inside(
        repo, arguments.workflow_summary, "workflow summary artifact"
    )
    summary_value = load_json_object(summary_path, "validation evidence summary")
    workflow_summary_value = load_json_object(
        workflow_summary_path, "validation workflow summary"
    )
    if summary_value != summary_payload(
        evidence_records, invocation_id=invocation_id, profile=profile
    ):
        raise EvidenceError("validation evidence summary does not match evidence records")
    wall_span_ms = workflow_summary_value.get("wall_span_ms")
    workflow_id = workflow_summary_value.get("workflow_id")
    if (
        not isinstance(wall_span_ms, int)
        or isinstance(wall_span_ms, bool)
        or wall_span_ms < 0
        or workflow_id is not None
        and not isinstance(workflow_id, str)
    ):
        raise EvidenceError("validation workflow summary identity is invalid")
    if isinstance(workflow_id, str):
        validate_record_token(workflow_id, "workflow summary workflow id")
        require_privacy_safe_string(workflow_id, "workflow summary workflow id")
    if workflow_summary_value != workflow_summary_payload(
        evidence_records,
        invocation_id=invocation_id,
        profile=profile,
        wall_span_ms=wall_span_ms,
        workflow_id=workflow_id,
    ):
        raise EvidenceError("validation workflow summary does not match evidence records")

    environment_classes = {
        str(record_value["environment_class"]) for record_value in evidence_records
    }
    if len(environment_classes) > 1:
        raise EvidenceError("evidence records contain multiple environment classes")
    if environment_classes:
        environment_class = next(iter(environment_classes))
    else:
        finalize_result_path = artifact_path_inside(
            repo,
            control_result_values["finalize"],
            "finalize control receipt",
        )
        preliminary_finalize = load_json_object(
            finalize_result_path, "finalize control receipt"
        )
        preliminary_command = preliminary_finalize.get("command")
        preliminary_argv = (
            preliminary_command.get("argv")
            if isinstance(preliminary_command, dict)
            else None
        )
        if (
            not isinstance(preliminary_argv, list)
            or preliminary_argv.count("--environment-class") != 1
        ):
            raise EvidenceError("finalize control environment class is unavailable")
        environment_index = preliminary_argv.index("--environment-class") + 1
        if environment_index >= len(preliminary_argv):
            raise EvidenceError("finalize control environment class is unavailable")
        environment_class = validate_record_token(
            preliminary_argv[environment_index], "finalize control environment class"
        )
    validate_record_token(environment_class, "control environment class")
    require_privacy_safe_string(environment_class, "control environment class")
    cache_path = artifact_path_inside(repo, arguments.cache, "validation evidence cache")
    selection_path = artifact_path_inside(repo, arguments.selection, "selected-checks artifact")
    fingerprint_selection_path = artifact_path_inside(
        repo, arguments.fingerprint_selection, "fingerprint-selection artifact"
    )
    preparation_selection_path = artifact_path_inside(
        repo, arguments.preparation_selection, "preparation-selection artifact"
    )
    control_context: dict[str, object] = {
        "snapshot": relative_path(repo, snapshot_path),
        "post_snapshot": relative_path(repo, post_snapshot_path),
        "cache": relative_path(repo, cache_path),
        "evidence": relative_path(repo, evidence_path),
        "events": relative_path(repo, events_path),
        "summary": relative_path(repo, summary_path),
        "workflow_summary": relative_path(repo, workflow_summary_path),
        "invocation_id": invocation_id,
        "profile": profile,
        "environment_class": environment_class,
        "preparation_selection": relative_path(repo, preparation_selection_path),
        "bootstrap_result": relative_path(
            repo,
            artifact_path_inside(
                repo,
                control_result_values["bootstrap-snapshot"],
                "bootstrap-snapshot control receipt",
            ),
        ),
        "wall_span_ms": wall_span_ms,
        "workflow_id": workflow_id,
        "preparation_python": preparation_python,
    }
    control_plane: list[dict[str, object]] = []
    control_entries: dict[str, dict[str, object]] = {}
    control_artifact_paths: set[Path] = set()
    for role in sorted(CONTROL_ROLES):
        control_result_path = artifact_path_inside(
            repo, control_result_values[role], f"{role} control receipt"
        )
        control_entry, control_paths = validated_control_result(
            repo,
            role,
            control_result_path,
            snapshot_path,
            control_role_argv(role, control_python, control_context),
        )
        control_plane.append(control_entry)
        control_entries[role] = control_entry
        control_artifact_paths.update(control_paths)

    selected = parse_selected_checks(selection_path)
    fingerprint_contracts = parse_fingerprint_selection(fingerprint_selection_path)
    preparation_contracts = parse_fingerprint_selection(preparation_selection_path)
    records_by_id = {record["validator_id"]: record for record in evidence_records}
    if not set(selected).issubset(records_by_id):
        raise EvidenceError("selected-checks artifact contains a missing evidence validator")
    for validator_id, record_value in records_by_id.items():
        is_selected = validator_id in selected
        if (record_value["execution_disposition"] == "not-selected") == is_selected:
            raise EvidenceError("selected-checks and not-selected evidence are inconsistent")
        if is_selected and record_value["selection_reason"] != selected[validator_id]:
            raise EvidenceError("selected-checks reason does not match evidence")
    immutable_reused_ids = {
        validator_id
        for validator_id, record_value in records_by_id.items()
        if record_value["execution_disposition"] == "reused"
        and isinstance(record_value.get("reuse_source"), dict)
        and record_value["reuse_source"].get("kind") == "immutable-history"
    }
    if set(fingerprint_contracts) != set(records_by_id) - immutable_reused_ids:
        raise EvidenceError("fingerprint-selection validators do not match evidence")
    if set(preparation_contracts) != set(records_by_id):
        raise EvidenceError("preparation-selection validators do not match evidence")
    file_records: dict[str, dict[str, object]] = {}
    git_snapshot = git_input_snapshot(repo)
    input_fingerprints: dict[str, str] = {}
    standard_fingerprints: dict[str, str] = {}
    for validator_id, (validator_version, input_paths, _cache_policy) in preparation_contracts.items():
        record_value = records_by_id[validator_id]
        if record_value["validator_version"] != validator_version:
            raise EvidenceError("preparation-selection validator version does not match evidence")
        if input_paths not in input_fingerprints:
            input_fingerprints[input_paths] = selected_input_fingerprint(
                repo, input_paths, file_records, git_snapshot
            )
        standard_fingerprints[validator_id] = input_fingerprints[input_paths]
    for validator_id, (validator_version, input_paths, _cache_policy) in fingerprint_contracts.items():
        record_value = records_by_id[validator_id]
        if record_value["validator_version"] != validator_version:
            raise EvidenceError("fingerprint-selection validator version does not match evidence")
        if input_paths not in input_fingerprints:
            input_fingerprints[input_paths] = selected_input_fingerprint(
                repo, input_paths, file_records, git_snapshot
            )
        if record_value["input_fingerprint"] != input_fingerprints[input_paths]:
            raise EvidenceError("fingerprint-selection input contract does not match evidence")
    prepare_cache_artifact_paths = validate_prepare_control_log(
        repo,
        control_entries["prepare"],
        preparation_contracts,
        records_by_id,
        standard_fingerprints,
        cache_path=cache_path,
        profile=profile,
        environment_class=environment_class,
    )

    artifact_paths: set[Path] = {
        snapshot_path,
        post_snapshot_path,
        evidence_path,
        summary_path,
        workflow_summary_path,
        selection_path,
        fingerprint_selection_path,
        preparation_selection_path,
        events_path,
        changed_paths_path,
        selection_comparison_path,
        *preparation_artifact_paths,
        *control_artifact_paths,
        *prepare_cache_artifact_paths,
    }
    for record_value in evidence_records:
        log_path = artifact_path_inside(repo, record_value["log_ref"], "evidence log")
        if not log_path.is_file():
            raise EvidenceError("evidence retained log is missing")
        log_content = log_path.read_bytes()
        if (
            record_value["log_sha256"] != sha256_bytes(log_content)
            or record_value["output_bytes"] != len(log_content)
            or record_value["output_lines"] != count_lines(log_content)
        ):
            raise EvidenceError("evidence retained log is missing or tampered")
        artifact_paths.add(log_path)
        artifact_paths.update(
            validate_execution_binding(repo, snapshot_path, record_value, log_path)
        )
        artifact_paths.update(
            validate_record_reuse_source(
                repo, snapshot_path, record_value, immutable_preparations
            )
        )
    artifacts = sorted(
        (repository_artifact_record(repo, path) for path in artifact_paths),
        key=lambda item: str(item["ref"]).encode("utf-8"),
    )
    _expected_again, current_again, matches_again = compare_snapshot(repo, snapshot_path)
    if not matches_again or current_again["identity_digest"] != current["identity_digest"]:
        raise EvidenceError("repository snapshot drifted while invocation was being sealed")
    artifacts_again = sorted(
        (repository_artifact_record(repo, path) for path in artifact_paths),
        key=lambda item: str(item["ref"]).encode("utf-8"),
    )
    if artifacts_again != artifacts:
        raise EvidenceError("retained invocation artifacts drifted while being sealed")
    output = artifact_path_inside(repo, arguments.output, "sealed invocation output")
    publication_output = artifact_path_inside(
        repo,
        arguments.publication_output or arguments.output,
        "sealed invocation publication output",
    )
    if output.parent != publication_output.parent:
        raise EvidenceError("staged and published invocation manifests must share a directory")
    if output.exists() or publication_output.exists():
        raise EvidenceError("sealed invocation output must not predate the current seal")
    terminal_result_value = getattr(arguments, "terminal_result", None)
    terminal_log_value = getattr(arguments, "terminal_log", None)
    if bool(terminal_result_value) != bool(terminal_log_value):
        raise EvidenceError("terminal supervision result and log must be declared together")
    if output != publication_output and not terminal_result_value:
        raise EvidenceError("staged invocation publication requires terminal supervision refs")
    terminal_supervision: dict[str, object]
    if terminal_result_value:
        terminal_result_path = artifact_path_inside(
            repo, terminal_result_value, "terminal seal supervision result"
        )
        terminal_log_path = artifact_path_inside(
            repo, terminal_log_value, "terminal seal supervision log"
        )
        terminal_raw_path = artifact_path_inside(
            repo,
            str(terminal_result_path) + ".process.json",
            "terminal seal raw supervision result",
        )
        if terminal_result_path.exists() or terminal_raw_path.exists():
            raise EvidenceError("terminal seal supervision result must not predate the seal child")
        if terminal_log_path.exists() and not terminal_log_path.is_file():
            raise EvidenceError("terminal seal supervision log is not a regular file")
        terminal_supervision = {
            "mode": "supervised",
            "result_ref": relative_path(repo, terminal_result_path),
            "log_ref": relative_path(repo, terminal_log_path),
            "raw_result_ref": relative_path(repo, terminal_raw_path),
            "expected_effective_argv_digest": canonical_sha256([
                control_python,
                VALIDATION_EVIDENCE_HELPER_REF,
                *sys.argv[1:],
            ]),
        }
    else:
        terminal_supervision = {"mode": "direct"}
    core = {
        "schema_version": INVOCATION_SCHEMA,
        "invocation_id": invocation_id,
        "profile": profile,
        "outcome": arguments.outcome,
        "sealed_at": utc_now(),
        "repository": {
            "pre_identity_digest": expected["identity_digest"],
            "post_identity_digest": post_snapshot["identity_digest"],
            "verified_identity_digest": current_again["identity_digest"],
            "commit": expected["identity"]["commit"],
            "tree": expected["identity"]["tree"],
            "clean": expected["identity"]["clean"],
        },
        "cardinality": {"events": len(event_lines), "evidence_records": len(evidence_lines)},
        "control_plane": control_plane,
        "terminal_supervision": terminal_supervision,
        "artifacts": artifacts,
    }
    payload = {**core, "manifest_digest": canonical_sha256(core)}
    manifest_content = formatted_json_bytes(payload)
    cache_payload = cache_payload_with_promotions(
        repo,
        cache_path,
        evidence_records,
        manifest_path=publication_output,
        manifest_content=manifest_content,
        manifest_payload=payload,
        evidence_path=evidence_path,
        snapshot_path=snapshot_path,
    )
    previous_cache_content = cache_path.read_bytes() if cache_path.is_file() else None
    promoted_cache_content = (
        formatted_json_bytes(cache_payload) if cache_payload is not None else None
    )
    if promoted_cache_content is not None:
        atomic_write_bytes(cache_path, promoted_cache_content)
    try:
        atomic_write_bytes(output, manifest_content)
    except BaseException:
        if promoted_cache_content is not None:
            current_cache_content = cache_path.read_bytes() if cache_path.is_file() else None
            if current_cache_content != promoted_cache_content:
                raise EvidenceError(
                    "sealed manifest publication failed and promoted cache changed concurrently"
                )
            if previous_cache_content is None:
                cache_path.unlink()
                fsync_directory(cache_path.parent)
            else:
                atomic_write_bytes(cache_path, previous_cache_content)
        raise


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    lookup_parser = commands.add_parser("lookup")
    prepare_parser = commands.add_parser("prepare")
    record_parser = commands.add_parser("record")
    finalize_parser = commands.add_parser("finalize")
    summary_parser = commands.add_parser("summarize")
    workflow_summary_parser = commands.add_parser("workflow-summary")
    snapshot_parser = commands.add_parser("snapshot")
    verify_snapshot_parser = commands.add_parser("verify-snapshot")
    verify_supervision_parser = commands.add_parser("verify-supervision-result")
    verify_terminal_parser = commands.add_parser("verify-terminal-invocation")
    supervise_parser = commands.add_parser("supervise")
    bootstrap_run_parser = commands.add_parser("bootstrap-run")
    seal_parser = commands.add_parser("seal-invocation")
    for command in (lookup_parser, record_parser):
        command.add_argument("--repo", required=True)
        command.add_argument("--cache", required=True)
        command.add_argument("--validator-id", required=True)
        command.add_argument("--validator-version", required=True)
        command.add_argument("--profile", required=True)
        command.add_argument("--environment-class", required=True)
    lookup_parser.add_argument("--input-paths", required=True)
    lookup_parser.add_argument("--cache-policy", required=True)
    prepare_parser.add_argument("--repo", required=True)
    prepare_parser.add_argument("--cache", required=True)
    prepare_parser.add_argument("--profile", required=True)
    prepare_parser.add_argument("--environment-class", required=True)
    prepare_parser.add_argument("--selection", required=True)
    finalize_parser.add_argument("--repo", required=True)
    finalize_parser.add_argument("--cache", required=True)
    finalize_parser.add_argument("--evidence", required=True)
    finalize_parser.add_argument("--events", required=True)
    finalize_parser.add_argument("--invocation-id", required=True)
    finalize_parser.add_argument("--profile", required=True)
    finalize_parser.add_argument("--environment-class", required=True)
    finalize_parser.add_argument("--snapshot")
    finalize_parser.add_argument("--preparation-python")
    record_parser.add_argument("--evidence", required=True)
    record_parser.add_argument("--invocation-id", required=True)
    record_parser.add_argument("--input-fingerprint", required=True)
    record_parser.add_argument("--outcome", required=True)
    record_parser.add_argument("--disposition", required=True)
    record_parser.add_argument("--started-ms", type=int, required=True)
    record_parser.add_argument("--completed-ms", type=int, required=True)
    record_parser.add_argument("--duration-ms", type=int, required=True)
    record_parser.add_argument("--suppressed-output-bytes", type=int, required=True)
    record_parser.add_argument("--subprocess-count", type=int, required=True)
    record_parser.add_argument("--cache-hit", action="store_true")
    record_parser.add_argument("--log-path", required=True)
    record_parser.add_argument("--selection-reason", required=True)
    record_parser.add_argument("--changed-paths-digest", default="unavailable")
    record_parser.add_argument("--enforcement", choices=("required", "advisory"))
    record_parser.add_argument("--result-path")
    record_parser.add_argument("--snapshot")
    record_parser.add_argument("--preparation-python")
    summary_parser.add_argument("--evidence", required=True)
    summary_parser.add_argument("--output", required=True)
    summary_parser.add_argument("--invocation-id", required=True)
    summary_parser.add_argument("--profile", required=True)
    workflow_summary_parser.add_argument("--evidence", required=True)
    workflow_summary_parser.add_argument("--output", required=True)
    workflow_summary_parser.add_argument("--profile", required=True)
    workflow_summary_parser.add_argument("--invocation-id", required=True)
    workflow_summary_parser.add_argument("--wall-span-ms", type=int, required=True)
    workflow_summary_parser.add_argument("--workflow-id", default="")
    snapshot_parser.add_argument("--repo", required=True)
    snapshot_parser.add_argument("--output", required=True)
    snapshot_parser.add_argument("--profile", required=True)
    snapshot_parser.add_argument("--require-clean", action="store_true")
    verify_snapshot_parser.add_argument("--repo", required=True)
    verify_snapshot_parser.add_argument("--snapshot", required=True)
    verify_snapshot_parser.add_argument("--output")
    verify_supervision_parser.add_argument("--repo", required=True)
    verify_supervision_parser.add_argument("--snapshot", required=True)
    verify_supervision_parser.add_argument("--result-path", required=True)
    verify_terminal_parser.add_argument("--repo", required=True)
    verify_terminal_parser.add_argument("--snapshot", required=True)
    verify_terminal_parser.add_argument("--manifest", required=True)
    verify_terminal_parser.add_argument("--result-path", required=True)
    verify_terminal_parser.add_argument("command_argv", nargs=argparse.REMAINDER)
    supervise_parser.add_argument("--repo", required=True)
    supervision_snapshot_group = supervise_parser.add_mutually_exclusive_group(required=True)
    supervision_snapshot_group.add_argument("--snapshot")
    supervision_snapshot_group.add_argument("--bootstrap-snapshot-output")
    supervise_parser.add_argument("--bootstrap-profile")
    supervise_parser.add_argument("--bootstrap-python")
    supervise_parser.add_argument("--bootstrap-require-clean", action="store_true")
    supervise_parser.add_argument("--log-path", required=True)
    supervise_parser.add_argument("--result-path", required=True)
    supervise_parser.add_argument("--timeout-seconds", type=float, required=True)
    supervise_parser.add_argument(
        "--accepted-child-exit-code", type=int, action="append", default=[0]
    )
    supervise_parser.add_argument("--cwd-ref", default=".")
    supervise_parser.add_argument("command_argv", nargs=argparse.REMAINDER)
    bootstrap_run_parser.add_argument("--repo", required=True)
    bootstrap_run_parser.add_argument("--snapshot-output", required=True)
    bootstrap_run_parser.add_argument("--profile", required=True)
    bootstrap_run_parser.add_argument("--sidecar-output", required=True)
    bootstrap_run_parser.add_argument("--cwd-ref", default=".")
    bootstrap_run_parser.add_argument("--require-clean", action="store_true")
    bootstrap_run_parser.add_argument("command_argv", nargs=argparse.REMAINDER)
    seal_parser.add_argument("--repo", required=True)
    seal_parser.add_argument("--snapshot", required=True)
    seal_parser.add_argument("--post-snapshot", required=True)
    seal_parser.add_argument("--evidence", required=True)
    seal_parser.add_argument("--summary", required=True)
    seal_parser.add_argument("--workflow-summary", required=True)
    seal_parser.add_argument("--selection", required=True)
    seal_parser.add_argument("--selection-comparison", required=True)
    seal_parser.add_argument("--fingerprint-selection", required=True)
    seal_parser.add_argument("--preparation-selection", required=True)
    seal_parser.add_argument("--events", required=True)
    seal_parser.add_argument("--changed-paths", required=True)
    seal_parser.add_argument("--output", required=True)
    seal_parser.add_argument("--publication-output")
    seal_parser.add_argument("--cache", required=True)
    seal_parser.add_argument("--invocation-id", required=True)
    seal_parser.add_argument("--control-python", required=True)
    seal_parser.add_argument(
        "--control-result", action="append", nargs=2, default=[],
        metavar=("ROLE", "WRAPPER"),
    )
    seal_parser.add_argument("--terminal-result")
    seal_parser.add_argument("--terminal-log")
    seal_parser.add_argument("--preparation-python")
    seal_parser.add_argument("--preparation-result", action="append", default=[])
    seal_parser.add_argument("--outcome", choices=("passed", "failed", "blocked"), required=True)
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        if arguments.command == "lookup":
            lookup(arguments)
        elif arguments.command == "prepare":
            prepare(arguments)
        elif arguments.command == "finalize":
            finalize(arguments)
        elif arguments.command == "record":
            record(arguments)
        elif arguments.command == "workflow-summary":
            workflow_summary(arguments)
        elif arguments.command == "snapshot":
            snapshot_command(arguments)
        elif arguments.command == "verify-snapshot":
            verify_snapshot_command(arguments)
        elif arguments.command == "verify-supervision-result":
            verify_supervision_result(arguments)
        elif arguments.command == "verify-terminal-invocation":
            verify_terminal_invocation(arguments)
        elif arguments.command == "supervise":
            return supervise(arguments)
        elif arguments.command == "bootstrap-run":
            return bootstrap_run(arguments)
        elif arguments.command == "seal-invocation":
            seal_invocation(arguments)
        else:
            summarize(arguments)
    except EvidenceError as exc:
        raise SystemExit(f"validation evidence failed closed: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
