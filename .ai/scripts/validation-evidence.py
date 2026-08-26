#!/usr/bin/env python3
"""Privacy-preserving, deterministic evidence records for validation profiles."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "2.0.0"
# Reuse eligibility is intentionally independent from the emitted evidence
# schema.  Existing successful evidence remains safe to reuse when the input
# and validator fingerprints still match; a presentation-schema increment must
# not turn an otherwise valid run into a cache-read failure.
CACHE_SCHEMA_VERSION = "1.0.0"
OUTCOMES = {"passed", "failed", "blocked-by-environment", "not-applicable", "deferred-with-owner"}
DISPOSITIONS = {"executed", "reused", "not-selected", "timed-out", "cancelled"}


class EvidenceError(ValueError):
    """Fail-closed validation evidence contract violation."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha256(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def relative_path(repo: Path, candidate: Path) -> str:
    try:
        return candidate.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return candidate.name


def tracked_git_state(repo: Path) -> dict[str, str]:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD", "HEAD^{tree}"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    values = result.stdout.splitlines()
    if result.returncode or len(values) != 2:
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
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


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
        raise EvidenceError(f"cannot read validation evidence cache: {path}") from exc
    if value.get("schema_version") != CACHE_SCHEMA_VERSION or not isinstance(value.get("entries"), dict):
        raise EvidenceError("validation evidence cache schema is invalid")
    return value


def write_cache(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def iso_from_millis(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).isoformat().replace("+00:00", "Z")


def count_lines(value: bytes) -> int:
    return 0 if not value else value.count(b"\n") + (0 if value.endswith(b"\n") else 1)


def lookup(arguments: argparse.Namespace) -> None:
    repo = Path(arguments.repo).resolve()
    fingerprint = selected_input_fingerprint(
        repo, arguments.input_paths, git_snapshot=git_input_snapshot(repo)
    )
    cache = load_cache(Path(arguments.cache))
    eligible = False
    log_ref = ""
    if arguments.cache_policy != "no-reuse":
        entry = cache["entries"].get(
            cache_key(
                arguments.validator_id,
                arguments.validator_version,
                arguments.profile,
                fingerprint,
                arguments.environment_class,
            )
        )
        if isinstance(entry, dict) and entry.get("outcome") == "passed" and entry.get("eligible") is True:
            eligible = True
            log_ref = str(entry.get("log_ref", ""))
    print(f"{fingerprint}\t{'true' if eligible else 'false'}\t{log_ref}")


def prepare(arguments: argparse.Namespace) -> None:
    repo = Path(arguments.repo).resolve()
    cache = load_cache(Path(arguments.cache))
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
        eligible = False
        log_ref = ""
        if cache_policy != "no-reuse":
            entry = cache["entries"].get(
                cache_key(
                    validator_id,
                    validator_version,
                    arguments.profile,
                    fingerprint,
                    arguments.environment_class,
                )
            )
            if isinstance(entry, dict) and entry.get("outcome") == "passed" and entry.get("eligible") is True:
                eligible = True
                log_ref = str(entry.get("log_ref", ""))
        print(f"{validator_id}\t{fingerprint}\t{'true' if eligible else 'false'}\t{log_ref}")


def record(arguments: argparse.Namespace) -> None:
    if arguments.outcome not in OUTCOMES:
        raise EvidenceError(f"unsupported outcome: {arguments.outcome}")
    if arguments.disposition not in DISPOSITIONS:
        raise EvidenceError(f"unsupported execution disposition: {arguments.disposition}")
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
    content = log_path.read_bytes() if log_path.is_file() else b""
    log_ref = relative_path(repo, log_path)
    record_value = {
        "schema_version": SCHEMA_VERSION,
        "invocation_id": arguments.invocation_id,
        "validator_id": arguments.validator_id,
        "validator_version": arguments.validator_version,
        "profile": arguments.profile,
        "input_fingerprint": arguments.input_fingerprint,
        "environment_class": arguments.environment_class,
        "started_at": iso_from_millis(arguments.started_ms),
        "completed_at": iso_from_millis(arguments.completed_ms),
        "duration_ms": arguments.duration_ms,
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
    evidence = Path(arguments.evidence)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    with evidence.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record_value, ensure_ascii=False, sort_keys=True) + "\n")
    if arguments.disposition == "executed" and arguments.outcome == "passed":
        cache = load_cache(Path(arguments.cache))
        cache["entries"][
            cache_key(
                arguments.validator_id,
                arguments.validator_version,
                arguments.profile,
                arguments.input_fingerprint,
                arguments.environment_class,
            )
        ] = {
            "eligible": True,
            "outcome": "passed",
            "log_ref": log_ref,
        }
        write_cache(Path(arguments.cache), cache)


def finalize(arguments: argparse.Namespace) -> None:
    for line in Path(arguments.events).read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) != 12:
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
        ) = fields
        started = int(started_ms)
        completed = int(completed_ms)
        record(
            argparse.Namespace(
                repo=arguments.repo,
                cache=arguments.cache,
                evidence=arguments.evidence,
                invocation_id=arguments.invocation_id,
                validator_id=validator_id,
                validator_version=validator_version,
                profile=arguments.profile,
                environment_class=arguments.environment_class,
                input_fingerprint=input_fingerprint,
                outcome=outcome,
                disposition=disposition,
                started_ms=started,
                completed_ms=completed,
                duration_ms=completed - started,
                suppressed_output_bytes=int(suppressed_bytes),
                subprocess_count=None,
                cache_hit=cache_hit == "true",
                log_path=log_path,
                selection_reason=selection_reason,
                changed_paths_digest=changed_paths_digest,
            )
        )


def summarize(arguments: argparse.Namespace) -> None:
    evidence = Path(arguments.evidence)
    records = [
        json.loads(line)
        for line in evidence.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if evidence.exists() else []
    payload = {
        "schema_version": SCHEMA_VERSION,
        "invocation_id": arguments.invocation_id,
        "profile": arguments.profile,
        "records": len(records),
        "executed": sum(record["execution_disposition"] == "executed" for record in records),
        "reused": sum(record["execution_disposition"] == "reused" for record in records),
        "not_selected": sum(
            record["execution_disposition"] == "not-selected" for record in records
        ),
        "dispositions": {
            disposition: sum(
                record["execution_disposition"] == disposition for record in records
            )
            for disposition in sorted(DISPOSITIONS)
        },
        "outcomes": {
            outcome: sum(record["outcome"] == outcome for record in records)
            for outcome in sorted(OUTCOMES)
        },
    }
    Path(arguments.output).write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def workflow_summary(arguments: argparse.Namespace) -> None:
    evidence = Path(arguments.evidence)
    records = [
        json.loads(line)
        for line in evidence.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] if evidence.exists() else []
    active_execution_ms = sum(
        int(record["duration_ms"])
        for record in records
        if record["execution_disposition"] == "executed"
    )
    unknown_ms = max(0, arguments.wall_span_ms - active_execution_ms)
    payload = {
        "schema_version": "1.0.0",
        "workflow_id": arguments.workflow_id or None,
        "profile": arguments.profile,
        "wall_span_ms": arguments.wall_span_ms,
        "segments": {
            "active_execution_ms": active_execution_ms,
            "external_wait_ms": None,
            "approval_wait_ms": None,
            "environment_retry_ms": None,
            "unknown_ms": unknown_ms,
        },
        "validator_invocations": len(records),
        "executed_results": sum(
            record["execution_disposition"] == "executed" for record in records
        ),
        "reused_results": sum(
            record["execution_disposition"] == "reused" for record in records
        ),
        "not_selected_results": sum(
            record["execution_disposition"] == "not-selected" for record in records
        ),
        "retry_count": 0,
        "sub_agents": {"availability": "unavailable", "value": None},
        "observability": {"export_status": "unavailable", "trace_id": None},
    }
    Path(arguments.output).write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    lookup_parser = commands.add_parser("lookup")
    prepare_parser = commands.add_parser("prepare")
    record_parser = commands.add_parser("record")
    finalize_parser = commands.add_parser("finalize")
    summary_parser = commands.add_parser("summarize")
    workflow_summary_parser = commands.add_parser("workflow-summary")
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
    summary_parser.add_argument("--evidence", required=True)
    summary_parser.add_argument("--output", required=True)
    summary_parser.add_argument("--invocation-id", required=True)
    summary_parser.add_argument("--profile", required=True)
    workflow_summary_parser.add_argument("--evidence", required=True)
    workflow_summary_parser.add_argument("--output", required=True)
    workflow_summary_parser.add_argument("--profile", required=True)
    workflow_summary_parser.add_argument("--wall-span-ms", type=int, required=True)
    workflow_summary_parser.add_argument("--workflow-id", default="")
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
        else:
            summarize(arguments)
    except EvidenceError as exc:
        raise SystemExit(f"validation evidence failed closed: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
