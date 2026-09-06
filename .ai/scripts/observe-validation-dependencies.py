#!/usr/bin/env python3
"""Observe bounded validator dependencies and emit a privacy-safe drift report."""

from __future__ import annotations

import argparse
import builtins
from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import importlib.util
import io
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/observe-validation-dependencies.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_HARNESS = "in-process-python-callable/v1"
REQUEST_SCHEMA = "validation-dependency-observation-request/v1"
REPORT_SCHEMA = "validation-dependency-observation-report/v1"
DIMENSIONS = ("file", "subprocess", "git", "environment", "runtime")
OUTPUT_ROOT = Path(".dev/ai-context/local/validation")
FRESH_GATES = (
    "current-head-review-binding",
    "hosted-required-contexts",
    "live-provider-admission",
    "tag-release-binding",
)
BLIND_SPOTS = (
    "complete-transitive-dependency-closure",
    "entrypoint-imports-and-file-reads-before-observation-hooks",
    "environment-or-runtime-dependencies-not-accessed-by-the-representative-path",
    "native-extensions-direct-os-calls-and-child-process-internals",
    "provider-and-hosted-state-outside-the-local-harness",
    "untaken-branches",
)
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._+-]{0,127}$")
GIT_IDENTIFIER = re.compile(r"^git:[a-z0-9][a-z0-9-]{0,63}$")
RUNTIME_IDENTIFIER = re.compile(r"^module:[a-z0-9][a-z0-9._+-]{0,127}$")
VALIDATOR_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class ObservationError(ValueError):
    """Raised when an observation request is malformed or unsafe."""


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ObservationError("observation request must be a YAML mapping")
    return value


def _normalized_relative_path(root: Path, value: object, label: str) -> tuple[str, Path]:
    if not isinstance(value, str) or not value.strip():
        raise ObservationError(f"{label} must be a non-empty repository-relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ObservationError(f"{label} must be a safe repository-relative path")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if resolved_root not in (resolved, *resolved.parents):
        raise ObservationError(f"{label} escapes the repository root")
    return candidate.as_posix(), resolved


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _subject_commit(root: Path, requested: object) -> str:
    if requested != "HEAD" and not (isinstance(requested, str) and COMMIT_SHA.fullmatch(requested)):
        raise ObservationError("subject must be HEAD or a lowercase 40-character commit SHA")
    result = _git(root, "rev-parse", "HEAD")
    if result.returncode != 0 or not COMMIT_SHA.fullmatch(result.stdout.strip()):
        raise ObservationError("repository HEAD could not be resolved")
    current = result.stdout.strip()
    if requested != "HEAD" and requested != current:
        raise ObservationError("requested subject does not match repository HEAD")
    return current


def _tracked_status_digest(root: Path) -> str:
    result = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if result.returncode != 0:
        raise ObservationError("tracked worktree status could not be resolved")
    return hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()


def _string_list(value: object, label: str, *, canonical: bool = True) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ObservationError(f"{label} must be a string list")
    if canonical and value != sorted(set(value)):
        raise ObservationError(f"{label} must be sorted and unique")
    return list(value)


def validate_request(request: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    if request.get("schema_version") != REQUEST_SCHEMA:
        raise ObservationError(f"schema_version must be {REQUEST_SCHEMA}")
    validator_id = request.get("validator_id")
    if not isinstance(validator_id, str) or not VALIDATOR_ID.fullmatch(validator_id):
        raise ObservationError("validator_id is invalid")
    harness = request.get("harness")
    if not isinstance(harness, str) or not harness:
        raise ObservationError("harness must be a non-empty string")
    entrypoint, entrypoint_path = _normalized_relative_path(
        root, request.get("entrypoint"), "entrypoint"
    )
    if not entrypoint_path.is_file() or entrypoint_path.suffix != ".py":
        raise ObservationError("entrypoint must be an existing Python file")
    callable_name = request.get("callable")
    if not isinstance(callable_name, str) or not callable_name.isidentifier():
        raise ObservationError("callable must be one Python identifier")
    argv = _string_list(request.get("argv"), "argv", canonical=False)
    declarations_value = request.get("declared_dependencies")
    if not isinstance(declarations_value, dict) or set(declarations_value) != set(DIMENSIONS):
        raise ObservationError("declared_dependencies must contain exactly the five dimensions")

    declarations: dict[str, list[str]] = {}
    for dimension in DIMENSIONS:
        values = _string_list(
            declarations_value.get(dimension),
            f"declared_dependencies.{dimension}",
        )
        if dimension == "file":
            normalized_files: list[str] = []
            for index, item in enumerate(values):
                normalized, candidate = _normalized_relative_path(
                    root, item, f"declared_dependencies.file[{index}]"
                )
                if not candidate.exists():
                    raise ObservationError("declared file dependency does not exist")
                normalized_files.append(normalized)
            if normalized_files != values:
                raise ObservationError("declared file dependencies must use canonical POSIX paths")
        elif dimension == "environment":
            if any(not ENVIRONMENT_NAME.fullmatch(item) for item in values):
                raise ObservationError("environment declarations contain an invalid variable name")
        elif dimension == "git":
            if any(not GIT_IDENTIFIER.fullmatch(item) for item in values):
                raise ObservationError("Git declarations must use git:<subcommand>")
        elif dimension == "runtime":
            if any(
                item != "python"
                and not RUNTIME_IDENTIFIER.fullmatch(item)
                for item in values
            ):
                raise ObservationError("runtime declarations must use python or module:<name>")
        elif any(not IDENTIFIER.fullmatch(item) for item in values):
            raise ObservationError("subprocess declarations contain an invalid tool name")
        declarations[dimension] = values

    normalized_request = {
        "schema_version": REQUEST_SCHEMA,
        "validator_id": validator_id,
        "subject": request.get("subject"),
        "harness": harness,
        "entrypoint": entrypoint,
        "callable": callable_name,
        "argv": argv,
        "declared_dependencies": declarations,
    }
    return normalized_request


def _inside(root: Path, candidate: Path) -> bool:
    resolved_root = root.resolve()
    try:
        resolved = candidate.resolve()
    except OSError:
        resolved = candidate.absolute()
    return resolved_root in (resolved, *resolved.parents)


@dataclass
class Recorder:
    root: Path
    root_identity: str = field(init=False, repr=False)
    observed: dict[str, set[str]] = field(
        default_factory=lambda: {dimension: set() for dimension in DIMENSIONS}
    )
    unsupported_events: set[str] = field(default_factory=set)
    outside_repository_file_reads: int = 0
    environment_suppression_depth: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        self.root_identity = os.path.normcase(os.path.realpath(self.root))

    def _caller_is_inside_repository(self, caller_file: str) -> bool:
        candidate = os.path.normcase(os.path.realpath(caller_file))
        try:
            return os.path.commonpath((self.root_identity, candidate)) == self.root_identity
        except ValueError:
            return False

    def record_file(self, value: object) -> None:
        if isinstance(value, int):
            return
        try:
            candidate = Path(os.fspath(value))
        except TypeError:
            self.unsupported_events.add("non-path-file-operand")
            return
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        if _inside(self.root, candidate):
            relative = candidate.resolve().relative_to(self.root.resolve()).as_posix()
            self.observed["file"].add(relative)
        else:
            self.outside_repository_file_reads += 1

    @staticmethod
    def _tool_name(value: object) -> str | None:
        try:
            name = Path(os.fspath(value)).name.casefold()
        except TypeError:
            return None
        if name.endswith(".exe"):
            name = name[:-4]
        if name == "py" or name.startswith("python"):
            return "python"
        return name if IDENTIFIER.fullmatch(name) else None

    def record_command(self, command: object, *, shell: bool) -> None:
        if shell or isinstance(command, (str, bytes)):
            self.unsupported_events.add("untokenized-shell-command")
            return
        if not isinstance(command, Sequence) or not command:
            self.unsupported_events.add("malformed-subprocess-command")
            return
        tool = self._tool_name(command[0])
        if tool is None:
            self.unsupported_events.add("unnormalizable-subprocess-tool")
            return
        self.observed["subprocess"].add(tool)
        if tool != "git":
            return
        if len(command) < 2:
            self.unsupported_events.add("git-subcommand-missing")
            return
        subcommand = str(command[1]).casefold()
        if subcommand.startswith("-") or not GIT_IDENTIFIER.fullmatch(f"git:{subcommand}"):
            self.unsupported_events.add("git-subcommand-unresolved")
            return
        self.observed["git"].add(f"git:{subcommand}")

    def record_environment(self, name: object) -> None:
        if self.environment_suppression_depth:
            return
        if isinstance(name, str) and ENVIRONMENT_NAME.fullmatch(name):
            self.observed["environment"].add(name)
        else:
            self.unsupported_events.add("invalid-environment-name")

    def record_import(self, name: object, globals_value: object) -> None:
        if not isinstance(name, str) or not name:
            return
        caller_file = globals_value.get("__file__") if isinstance(globals_value, dict) else None
        if (
            not isinstance(caller_file, str)
            or not self._caller_is_inside_repository(caller_file)
        ):
            return
        top_level = name.split(".", 1)[0].casefold()
        identity = f"module:{top_level}"
        if RUNTIME_IDENTIFIER.fullmatch(identity):
            self.observed["runtime"].add(identity)


@contextmanager
def observation_hooks(recorder: Recorder) -> Iterator[None]:
    original_builtin_open = builtins.open
    original_io_open = io.open
    original_path_open = Path.open
    original_popen = subprocess.Popen
    original_getenv = os.getenv
    environment_type = type(os.environ)
    original_environment_getitem = environment_type.__getitem__
    original_environment_get = environment_type.get
    original_import = builtins.__import__

    def observed_builtin_open(file: object, *args: object, **kwargs: object):
        recorder.record_file(file)
        return original_builtin_open(file, *args, **kwargs)

    def observed_io_open(file: object, *args: object, **kwargs: object):
        recorder.record_file(file)
        return original_io_open(file, *args, **kwargs)

    def observed_path_open(path_value: Path, *args: object, **kwargs: object):
        recorder.record_file(path_value)
        return original_path_open(path_value, *args, **kwargs)

    def observed_popen(*popenargs: object, **kwargs: object):
        command = popenargs[0] if popenargs else kwargs.get("args")
        recorder.record_command(command, shell=bool(kwargs.get("shell", False)))
        # POSIX executable resolution reads PATH internally, sometimes with a bytes
        # key. That is subprocess implementation detail rather than a direct target
        # dependency; target-owned environment reads outside Popen remain observed.
        recorder.environment_suppression_depth += 1
        try:
            return original_popen(*popenargs, **kwargs)
        finally:
            recorder.environment_suppression_depth -= 1

    def observed_getenv(name: str, default: str | None = None):
        recorder.record_environment(name)
        return original_getenv(name, default)

    def observed_environment_getitem(environment: object, name: str):
        recorder.record_environment(name)
        return original_environment_getitem(environment, name)

    def observed_environment_get(environment: object, name: str, default: object = None):
        recorder.record_environment(name)
        return original_environment_get(environment, name, default)

    def observed_import(
        name: str,
        globals_value: dict[str, Any] | None = None,
        locals_value: dict[str, Any] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ):
        recorder.record_import(name, globals_value)
        return original_import(name, globals_value, locals_value, fromlist, level)

    builtins.open = observed_builtin_open
    io.open = observed_io_open
    Path.open = observed_path_open
    subprocess.Popen = observed_popen  # type: ignore[assignment]
    os.getenv = observed_getenv
    environment_type.__getitem__ = observed_environment_getitem
    environment_type.get = observed_environment_get
    builtins.__import__ = observed_import
    try:
        yield
    finally:
        builtins.open = original_builtin_open
        io.open = original_io_open
        Path.open = original_path_open
        subprocess.Popen = original_popen
        os.getenv = original_getenv
        environment_type.__getitem__ = original_environment_getitem
        environment_type.get = original_environment_get
        builtins.__import__ = original_import


def _load_target(path: Path, callable_name: str, request_digest: str):
    module_name = f"_dependency_observation_target_{request_digest[:16]}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ObservationError("target entrypoint could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = getattr(module, callable_name, None)
    if not callable(target):
        raise ObservationError("target callable is missing")
    return target


def _coverage(status: str) -> dict[str, dict[str, object]]:
    observers = {
        "file": "python-open-wrappers-after-target-load",
        "subprocess": "tokenized-subprocess-popen-wrapper",
        "git": "direct-tokenized-git-subcommand-wrapper",
        "environment": "python-os-environment-access-wrappers",
        "runtime": "active-python-identity-and-repository-import-wrapper",
    }
    return {
        dimension: {
            "status": status,
            "observer": observers[dimension],
            "complete": False,
        }
        for dimension in DIMENSIONS
    }


def _file_declares(root: Path, declaration: str, observed: str) -> bool:
    declared_path = root / declaration
    if declared_path.is_dir():
        prefix = declaration.rstrip("/") + "/"
        return observed.startswith(prefix)
    return declaration == observed


def _drift(
    root: Path,
    declarations: Mapping[str, list[str]],
    observed: Mapping[str, list[str]],
) -> tuple[dict[str, dict[str, list[str]]], bool]:
    undeclared: dict[str, list[str]] = {}
    unobserved: dict[str, list[str]] = {}
    for dimension in DIMENSIONS:
        declared_values = declarations[dimension]
        observed_values = observed[dimension]
        if dimension == "file":
            undeclared[dimension] = [
                item
                for item in observed_values
                if not any(_file_declares(root, declaration, item) for declaration in declared_values)
            ]
            unobserved[dimension] = [
                declaration
                for declaration in declared_values
                if not any(_file_declares(root, declaration, item) for item in observed_values)
            ]
        else:
            undeclared[dimension] = sorted(set(observed_values) - set(declared_values))
            unobserved[dimension] = sorted(set(declared_values) - set(observed_values))
    return {
        "observed_but_undeclared": undeclared,
        "declared_but_unobserved": unobserved,
    }, any(undeclared[dimension] for dimension in DIMENSIONS)


def _runtime_identity() -> dict[str, object]:
    return {
        "implementation": platform.python_implementation().casefold(),
        "version": ".".join(str(item) for item in sys.version_info[:3]),
        "cache_tag": sys.implementation.cache_tag,
        "abi_flags": getattr(sys, "abiflags", ""),
    }


def observe_request(request_value: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    request = validate_request(request_value, root)
    request_digest = canonical_digest(request)
    subject = _subject_commit(root, request["subject"])
    before_status = _tracked_status_digest(root)
    recorder = Recorder(root)
    recorder.observed["runtime"].add("python")
    recorder.observed["file"].add(request["entrypoint"])
    target_exit_code: int | None = None
    target_error: str | None = None

    if request["harness"] == SUPPORTED_HARNESS:
        target_path = root / request["entrypoint"]
        try:
            target = _load_target(target_path, request["callable"], request_digest)
            with observation_hooks(recorder):
                result = target(list(request["argv"]))
            if result is None:
                target_exit_code = 0
            elif isinstance(result, int) and not isinstance(result, bool):
                target_exit_code = result
            else:
                target_error = "unsupported-target-result"
        except Exception as exc:
            target_error = f"target-exception:{type(exc).__name__}"
    else:
        target_error = "unsupported-harness"

    after_status = _tracked_status_digest(root)
    observed = {
        dimension: sorted(recorder.observed[dimension]) for dimension in DIMENSIONS
    }
    drift, has_undeclared = _drift(root, request["declared_dependencies"], observed)
    worktree_changed = before_status != after_status
    reasons: list[str] = []
    if target_error is not None or target_exit_code not in (0,):
        reasons.append(target_error or "target-nonzero-exit")
    if recorder.unsupported_events:
        reasons.append("unsupported-observation-event")
    if worktree_changed:
        reasons.append("tracked-worktree-drift")
    if has_undeclared:
        reasons.append("observed-but-undeclared")

    if target_error is not None or target_exit_code not in (0,) or recorder.unsupported_events:
        outcome = "blocked"
    elif worktree_changed or has_undeclared:
        outcome = "failed"
    else:
        outcome = "passed"
    coverage_status = "partial" if request["harness"] == SUPPORTED_HARNESS else "unsupported"
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "validator_id": request["validator_id"],
        "subject": {"commit": subject, "requested": request["subject"]},
        "request_digest": request_digest,
        "observation_boundary": {
            "harness": request["harness"],
            "coverage_state": coverage_status,
            "closure_claim": "lower-bound-only",
            "complete_transitive_closure": False,
            "blind_spots": list(BLIND_SPOTS),
        },
        "coverage": _coverage(coverage_status),
        "observed_dependencies": observed,
        "runtime_identity": _runtime_identity(),
        "drift": {
            **drift,
            "declared_but_unobserved_disposition": "advisory-retain",
        },
        "worktree": {
            "before_status_digest": before_status,
            "after_status_digest": after_status,
            "tracked_state_unchanged": not worktree_changed,
        },
        "diagnostics": {
            "unsupported_events": sorted(recorder.unsupported_events),
            "outside_repository_file_read_count": recorder.outside_repository_file_reads,
            "target_exit_code": target_exit_code,
            "target_error": target_error,
        },
        "decision": {
            "outcome": outcome,
            "reasons": sorted(reasons),
            "automatic_registry_edits": False,
            "declarations_removed": False,
            "fresh_gates": list(FRESH_GATES),
        },
    }
    report["report_digest"] = canonical_digest(report)
    return report


def _safe_output_path(root: Path, value: Path) -> tuple[str, Path]:
    normalized, output = _normalized_relative_path(root, value.as_posix(), "output")
    allowed = (root / OUTPUT_ROOT).resolve()
    if allowed not in (output, *output.parents) or output == allowed:
        raise ObservationError("output must be a file beneath .dev/ai-context/local/validation")
    if output.exists():
        raise ObservationError("output already exists; observation reports are create-only")
    ignored = _git(root, "check-ignore", "-q", "--", normalized)
    if ignored.returncode != 0:
        raise ObservationError("output must be ignored by Git")
    return normalized, output


def write_report(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        yaml.safe_dump(dict(report), stream, sort_keys=False, allow_unicode=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        request_relative, request_path = _normalized_relative_path(
            ROOT, arguments.request.as_posix(), "request"
        )
        if not request_path.is_file():
            raise ObservationError("request file does not exist")
        output_relative, output_path = _safe_output_path(ROOT, arguments.output)
        report = observe_request(load_yaml_mapping(request_path), ROOT)
        write_report(output_path, report)
        print(
            f"Validation dependency observation {report['decision']['outcome']}: "
            f"{report['validator_id']} ({output_relative}; request={request_relative})"
        )
        return {"passed": 0, "failed": 1, "blocked": 2}[report["decision"]["outcome"]]
    except (ObservationError, OSError, yaml.YAMLError) as exc:
        print(f"Validation dependency observation blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
