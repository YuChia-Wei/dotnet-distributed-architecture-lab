"""Cross-platform process-tree supervision for validation commands.

This module is intentionally internal.  The aggregate validation runner owns
admission, Git identity, outcome interpretation, and exit-code policy.  This
module owns only one command process tree and the bytes written to its log.
"""

from __future__ import annotations

import contextlib
import ctypes
import errno
import hashlib
import json
import math
import os
import re
import select
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import BinaryIO


SCHEMA = "validation-supervision/v1"
_POLL_INTERVAL_SECONDS = 0.02
_STATUSES = {"completed", "timed-out", "cancelled", "cleanup-failed", "launch-failed"}
_WINDOWS_DRIVE_FRAGMENT = re.compile(r"(?i)[a-z]:[\\/]")
_SAFE_RELATIVE_PATH = re.compile(
    r"(?:\.{1,2}|[a-zA-Z0-9_][a-zA-Z0-9_.-]*)(?:[\\/][a-zA-Z0-9_.-]+)*[\\/]?"
)
_SAFE_ABSOLUTE_PLACEHOLDER = re.compile(
    r"(?:[^=\s]+(?:=|<))?<absolute-path>/[^/\\\s]+>?"
)


# The bootstrap blocks on stdin before it can call Popen.  Its stdout is a
# private control pipe; the target's stdout and stderr are both directed to the
# bootstrap's stderr, which is the supervisor-owned validation log.
_WINDOWS_BOOTSTRAP_CODE = r"""
import json
import subprocess
import sys

def emit(value):
    sys.stdout.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()

emit({"event": "awaiting-release"})
raw = sys.stdin.buffer.readline()
if not raw:
    emit({"event": "not-released"})
    raise SystemExit(240)

try:
    payload = json.loads(raw.decode("utf-8"))
    argv = payload["argv"]
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
        raise ValueError("invalid argv")
except BaseException as exc:
    emit({"event": "launch-failed", "error_type": type(exc).__name__})
    raise SystemExit(241)

try:
    child = subprocess.Popen(argv, stdout=sys.stderr.buffer, stderr=subprocess.STDOUT)
except BaseException as exc:
    emit({"event": "launch-failed", "error_type": type(exc).__name__})
    raise SystemExit(242)

emit({"event": "launched"})
child_exit_code = child.wait()
emit({"event": "completed", "child_exit_code": child_exit_code})
raise SystemExit(0)
"""


# Run the Linux subreaper in a fresh interpreter rather than forking the
# caller.  Forking a multi-threaded validation runner can deadlock before the
# child reaches containment setup; subprocess uses Python's thread-safe spawn
# path and pass_fds gives the helper only its private protocol and log handles.
_LINUX_MONITOR_BOOTSTRAP_CODE = r"""
import json
import os
import sys

import validation_process_supervisor as supervisor

os.write(int(sys.argv[3]), b"C")
with os.fdopen(int(sys.argv[1]), "r", encoding="utf-8") as config_handle:
    config = json.load(config_handle)
with os.fdopen(int(sys.argv[4]), "wb", buffering=0) as log_handle:
    supervisor._linux_monitor_entry(
        config,
        log_handle=log_handle,
        outcome_write=int(sys.argv[2]),
        ready_write=int(sys.argv[3]),
        launch_read=int(sys.argv[5]),
    )
"""


@dataclass
class _RunOutcome:
    status: str
    child_exit_code: int | None
    mechanism: str
    termination: dict[str, object]
    error: dict[str, object] | None = None


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _clock_adjustment_seconds(
    started_at: str,
    finished_at: str,
    duration_seconds: float,
) -> float:
    """Return wall elapsed time minus the authoritative monotonic duration."""

    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    finished = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    return round((finished - started).total_seconds() - duration_seconds, 6)


def _safe_error(stage: str, exc: BaseException) -> dict[str, object]:
    """Return an error descriptor that cannot disclose a host path."""

    result: dict[str, object] = {"stage": stage, "type": type(exc).__name__}
    if isinstance(exc, OSError):
        if exc.errno is not None:
            result["errno"] = exc.errno
        winerror = getattr(exc, "winerror", None)
        if winerror is not None:
            result["winerror"] = winerror
    return result


def _canonical_argv_bytes(argv: Sequence[str]) -> bytes:
    return json.dumps(
        list(argv),
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _absolute_path_flavour(value: str) -> str | None:
    if PureWindowsPath(value).is_absolute() or value.startswith("\\"):
        return "windows"
    if PurePosixPath(value).is_absolute():
        return "posix"
    return None


def _safe_absolute_path(value: str, cwd: Path) -> str:
    flavour = _absolute_path_flavour(value)
    if flavour is None:
        return value

    native_flavour = "windows" if os.name == "nt" else "posix"
    pure_path = PureWindowsPath(value) if flavour == "windows" else PurePosixPath(value)
    if flavour == native_flavour:
        try:
            resolved = Path(value).resolve(strict=False)
            relative = resolved.relative_to(cwd.resolve(strict=False))
        except (OSError, ValueError):
            pass
        else:
            relative_text = relative.as_posix()
            return "./" if relative_text == "." else f"./{relative_text}"

    basename = pure_path.name or "root"
    return f"<absolute-path>/{basename}"


def _safe_argv_argument(value: str, cwd: Path) -> str:
    if _absolute_path_flavour(value) is not None:
        return _safe_absolute_path(value, cwd)

    # Preserve option identity for the common --key=/absolute/path form.
    if "=" in value:
        prefix, candidate = value.split("=", 1)
        if _absolute_path_flavour(candidate) is not None:
            return f"{prefix}={_safe_absolute_path(candidate, cwd)}"

    # An attached/rooted path or embedded shell/program fragment cannot be
    # normalized without interpreting another language.  Preserve exact
    # binding only in the effective digest and redact the persisted argument.
    if _contains_unsafe_path_fragment(value):
        return "<argument-containing-absolute-path>"
    return value


def _privacy_safe_argv(argv: Sequence[str], cwd: Path) -> list[str]:
    return [_safe_argv_argument(value, cwd) for value in argv]


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _contains_unsafe_path_fragment(value: str) -> bool:
    if _SAFE_ABSOLUTE_PLACEHOLDER.fullmatch(value):
        return False
    if _SAFE_RELATIVE_PATH.fullmatch(value):
        return False
    if _WINDOWS_DRIVE_FRAGMENT.search(value):
        return True
    # Any slash or backslash outside a syntactically clean relative path is
    # treated as privacy-sensitive.  This intentionally redacts URLs, shell
    # fragments, attached include paths, and rooted drive-relative paths.
    return "/" in value or "\\" in value


def _assert_privacy_safe_string(value: str, field: str) -> None:
    if _absolute_path_flavour(value) is not None:
        raise ValueError(f"{field} contains an absolute path")
    if _contains_unsafe_path_fragment(value):
        raise ValueError(f"{field} contains an absolute path fragment")


def _validate_no_host_identity(value: object, field: str = "receipt") -> None:
    if isinstance(value, str):
        _assert_privacy_safe_string(value, field)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_no_host_identity(item, f"{field}[{index}]")
        return
    if not isinstance(value, dict):
        return
    prohibited_keys = {"pid", "process_id", "cwd", "log_path", "result_path", "host"}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError("receipt keys must be strings")
        if key.lower() in prohibited_keys:
            raise ValueError(f"receipt contains prohibited host identity field {key}")
        _validate_no_host_identity(item, f"{field}.{key}")


def _validate_receipt_invariants(receipt: dict[str, object]) -> None:
    """Reject internally inconsistent or privacy-unsafe receipts before write."""

    if receipt.get("schema") != SCHEMA:
        raise ValueError("invalid supervision receipt schema")
    status = receipt.get("status")
    if status not in _STATUSES:
        raise ValueError("invalid supervision receipt status")
    child_exit_code = receipt.get("child_exit_code")
    if child_exit_code is not None and (
        not isinstance(child_exit_code, int) or isinstance(child_exit_code, bool)
    ):
        raise ValueError("invalid child exit code")

    argv = receipt.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
        raise ValueError("invalid privacy-safe argv")
    for index, item in enumerate(argv):
        _assert_privacy_safe_string(item, f"argv[{index}]")
    if not _is_sha256(receipt.get("argv_sha256")):
        raise ValueError("invalid privacy-safe argv digest")
    if not _is_sha256(receipt.get("effective_argv_sha256")):
        raise ValueError("invalid effective argv digest")

    cwd_ref = receipt.get("cwd_ref")
    if not isinstance(cwd_ref, str) or not cwd_ref:
        raise ValueError("invalid cwd_ref")
    _assert_privacy_safe_string(cwd_ref, "cwd_ref")

    for field in ("timeout_seconds", "termination_grace_seconds", "duration_seconds"):
        value = receipt.get(field)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            or float(value) < 0
        ):
            raise ValueError(f"invalid {field}")
    for field in ("started_at", "finished_at"):
        value = receipt.get(field)
        if not isinstance(value, str) or not value.endswith("Z"):
            raise ValueError(f"invalid {field}")
    clock_adjustment = receipt.get("clock_adjustment_seconds")
    if (
        not isinstance(clock_adjustment, (int, float))
        or isinstance(clock_adjustment, bool)
        or not math.isfinite(float(clock_adjustment))
    ):
        raise ValueError("invalid clock_adjustment_seconds")
    try:
        expected_clock_adjustment = _clock_adjustment_seconds(
            receipt["started_at"],  # type: ignore[arg-type]
            receipt["finished_at"],  # type: ignore[arg-type]
            float(receipt["duration_seconds"]),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid supervision receipt timestamp") from exc
    if abs(float(clock_adjustment) - expected_clock_adjustment) > 0.000002:
        raise ValueError("inconsistent clock_adjustment_seconds")

    platform = receipt.get("platform")
    if not isinstance(platform, dict):
        raise ValueError("invalid platform evidence")
    if platform.get("family") not in {"windows", "posix"}:
        raise ValueError("invalid platform family")
    if not isinstance(platform.get("mechanism"), str) or not platform["mechanism"]:
        raise ValueError("invalid platform mechanism")

    termination = receipt.get("termination")
    if not isinstance(termination, dict):
        raise ValueError("invalid termination evidence")
    for field in ("soft_signal_sent", "hard_kill_sent", "root_reaped", "tree_empty"):
        if not isinstance(termination.get(field), bool):
            raise ValueError(f"invalid termination {field}")
    trigger = termination.get("trigger")
    if trigger is not None:
        if not isinstance(trigger, str) or not trigger:
            raise ValueError("invalid termination trigger")
        _assert_privacy_safe_string(trigger, "termination trigger")
    active_processes = termination.get("active_processes")
    if active_processes is not None and (
        not isinstance(active_processes, int)
        or isinstance(active_processes, bool)
        or active_processes < 0
    ):
        raise ValueError("invalid termination active_processes")
    if not isinstance(termination.get("verification"), str) or not termination["verification"]:
        raise ValueError("invalid termination verification")
    errors = termination.get("errors")
    if not isinstance(errors, list) or not all(isinstance(item, str) for item in errors):
        raise ValueError("invalid termination errors")
    for error in errors:
        _assert_privacy_safe_string(error, "termination error")
    tree_empty = termination["tree_empty"]
    containment = termination.get("containment")
    if containment is not None:
        if not isinstance(containment, dict):
            raise ValueError("invalid containment evidence")
        for field in ("dedicated_monitor", "subreaper", "procfs"):
            if not isinstance(containment.get(field), bool):
                raise ValueError(f"invalid containment {field}")
        for field in (
            "observed_descendants",
            "observed_detached_descendants",
            "observed_adopted_descendants",
            "remaining_descendants",
        ):
            value = containment.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"invalid containment {field}")
        proof = containment.get("proof")
        if not isinstance(proof, str) or not proof:
            raise ValueError("invalid containment proof")
        _assert_privacy_safe_string(proof, "containment proof")
        if tree_empty and containment["remaining_descendants"] != 0:
            raise ValueError("empty tree cannot retain descendants")

    if status in {"completed", "timed-out", "cancelled"} and not tree_empty:
        raise ValueError("terminal status requires empty tree proof")
    if status == "completed" and child_exit_code is None:
        raise ValueError("completed status requires child exit code")

    log = receipt.get("log")
    if not isinstance(log, dict) or not isinstance(log.get("sealed"), bool):
        raise ValueError("invalid log evidence")
    sealed = log["sealed"]
    if sealed and not tree_empty:
        raise ValueError("unproven tree cannot have a sealed log")
    if sealed:
        if not _is_sha256(log.get("sha256")):
            raise ValueError("sealed log requires a digest")
        for field in ("bytes", "lines"):
            value = log.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"sealed log requires valid {field}")
    elif any(log.get(field) is not None for field in ("sha256", "bytes", "lines")):
        raise ValueError("unsealed log cannot retain digest or counts")

    error = receipt.get("error")
    if error is not None:
        if not isinstance(error, dict):
            raise ValueError("invalid error evidence")
        for field in ("stage", "type"):
            value = error.get(field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"invalid error {field}")
            _assert_privacy_safe_string(value, f"error {field}")
        for field, value in error.items():
            if isinstance(value, str):
                _assert_privacy_safe_string(value, f"error {field}")
    _validate_no_host_identity(receipt)


def _validate_inputs(
    argv: Sequence[str],
    cwd_ref: str,
    timeout_seconds: float,
    termination_grace_seconds: float,
) -> list[str]:
    normalized_argv = list(argv)
    if not normalized_argv or not all(isinstance(item, str) for item in normalized_argv):
        raise ValueError("argv must contain at least one string")
    if any("\0" in item for item in normalized_argv):
        raise ValueError("argv cannot contain NUL bytes")
    if not isinstance(cwd_ref, str) or not cwd_ref:
        raise ValueError("cwd_ref must be a non-empty relative reference")
    if PurePosixPath(cwd_ref).is_absolute() or PureWindowsPath(cwd_ref).is_absolute():
        raise ValueError("cwd_ref must be relative")
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and greater than zero")
    if not math.isfinite(termination_grace_seconds) or termination_grace_seconds < 0:
        raise ValueError("termination_grace_seconds must be finite and non-negative")
    return normalized_argv


@contextlib.contextmanager
def _capture_cancellation() -> Iterator[tuple[threading.Event, dict[str, object]]]:
    cancellation = threading.Event()
    state: dict[str, object] = {"signal": None}
    prior_handlers: dict[int, object] = {}

    if threading.current_thread() is threading.main_thread():
        signals = {signal.SIGINT, signal.SIGTERM}

        def request_cancellation(signum: int, _frame: object) -> None:
            if not cancellation.is_set():
                try:
                    state["signal"] = signal.Signals(signum).name
                except ValueError:
                    state["signal"] = "UNKNOWN"
                cancellation.set()

        for signum in signals:
            try:
                prior_handlers[signum] = signal.getsignal(signum)
                signal.signal(signum, request_cancellation)
            except (OSError, RuntimeError, ValueError):
                prior_handlers.pop(signum, None)

    try:
        yield cancellation, state
    finally:
        for signum, handler in prior_handlers.items():
            signal.signal(signum, handler)


def _wait_for_root(
    process: subprocess.Popen[bytes],
    timeout_seconds: float,
    cancellation: threading.Event,
) -> str:
    deadline = time.monotonic() + timeout_seconds
    while True:
        if cancellation.is_set():
            return "cancelled"
        if process.poll() is not None:
            return "completed"
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "timed-out"
        try:
            process.wait(timeout=min(_POLL_INTERVAL_SECONDS, remaining))
        except subprocess.TimeoutExpired:
            continue


@dataclass(frozen=True)
class _ProcEntry:
    process_id: int
    parent_id: int
    process_group_id: int
    state: str
    start_time: int


def _read_proc_table() -> dict[int, _ProcEntry]:
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        raise RuntimeError("procfs-unavailable")
    table: dict[int, _ProcEntry] = {}
    try:
        candidates = tuple(proc_root.iterdir())
    except OSError as exc:
        raise RuntimeError("procfs-scan-unavailable") from exc
    for candidate in candidates:
        if not candidate.name.isdigit():
            continue
        try:
            stat_text = (candidate / "stat").read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise RuntimeError("procfs-scan-incomplete") from exc
        closing_parenthesis = stat_text.rfind(")")
        if closing_parenthesis < 0:
            raise RuntimeError("procfs-stat-invalid")
        fields = stat_text[closing_parenthesis + 2 :].split()
        if len(fields) <= 19:
            raise RuntimeError("procfs-stat-incomplete")
        try:
            process_id = int(candidate.name)
            entry = _ProcEntry(
                process_id=process_id,
                parent_id=int(fields[1]),
                process_group_id=int(fields[2]),
                state=fields[0],
                start_time=int(fields[19]),
            )
        except (TypeError, ValueError) as exc:
            raise RuntimeError("procfs-stat-invalid") from exc
        table[process_id] = entry
    return table


class _LinuxContainment:
    _PR_SET_CHILD_SUBREAPER = 36
    _PR_GET_CHILD_SUBREAPER = 37

    def __init__(self) -> None:
        self._self_id = os.getpid()
        self._prior_subreaper = 0
        self._prepared = False
        self._root_id: int | None = None
        self._root_start_time: int | None = None
        self._root_group_id: int | None = None
        self._baseline_direct_children: set[tuple[int, int]] = set()
        self._tracked: dict[int, int] = {}
        self._observed: set[tuple[int, int]] = set()
        self._observed_detached: set[tuple[int, int]] = set()
        self._observed_adopted: set[tuple[int, int]] = set()
        self._libc = ctypes.CDLL(None, use_errno=True)
        self._libc.prctl.restype = ctypes.c_int

    def _prctl_get(self) -> int:
        value = ctypes.c_int(0)
        if self._libc.prctl(
            self._PR_GET_CHILD_SUBREAPER,
            ctypes.byref(value),
            0,
            0,
            0,
        ) != 0:
            raise OSError(ctypes.get_errno(), "prctl-get-subreaper")
        return int(value.value)

    def _prctl_set(self, value: int) -> None:
        if self._libc.prctl(self._PR_SET_CHILD_SUBREAPER, value, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), "prctl-set-subreaper")

    def prepare(self) -> None:
        if not sys.platform.startswith("linux"):
            raise RuntimeError("linux-subreaper-unavailable")
        table = _read_proc_table()
        self._prior_subreaper = self._prctl_get()
        self._baseline_direct_children = {
            (entry.process_id, entry.start_time)
            for entry in table.values()
            if entry.parent_id == self._self_id
        }
        if self._prior_subreaper != 1:
            self._prctl_set(1)
        self._prepared = True

    def register_root(self, process_id: int, process_group_id: int) -> None:
        table = _read_proc_table()
        root = table.get(process_id)
        if root is None:
            raise RuntimeError("procfs-root-identity-unavailable")
        self._root_id = process_id
        self._root_start_time = root.start_time
        self._root_group_id = process_group_id
        self.discover(table)

    def _remember(self, entry: _ProcEntry, *, adopted: bool) -> None:
        if (
            entry.process_id == self._root_id
            and entry.start_time == self._root_start_time
        ):
            return
        identity = (entry.process_id, entry.start_time)
        self._tracked[entry.process_id] = entry.start_time
        self._observed.add(identity)
        if self._root_group_id is not None and entry.process_group_id != self._root_group_id:
            self._observed_detached.add(identity)
        if adopted:
            self._observed_adopted.add(identity)

    def discover(self, table: dict[int, _ProcEntry] | None = None) -> dict[int, _ProcEntry]:
        if self._root_id is None or self._root_start_time is None:
            raise RuntimeError("containment-root-unregistered")
        if table is None:
            table = _read_proc_table()

        root = table.get(self._root_id)
        parent_ids: set[int] = set()
        if root is not None and root.start_time == self._root_start_time:
            parent_ids.add(root.process_id)
        for process_id, start_time in tuple(self._tracked.items()):
            entry = table.get(process_id)
            if entry is not None and entry.start_time == start_time:
                parent_ids.add(process_id)

        changed = True
        while changed:
            changed = False
            for entry in table.values():
                if entry.process_id in parent_ids:
                    continue
                if entry.parent_id in parent_ids:
                    self._remember(entry, adopted=False)
                    parent_ids.add(entry.process_id)
                    changed = True

        root_identity = (self._root_id, self._root_start_time)
        for entry in table.values():
            identity = (entry.process_id, entry.start_time)
            if (
                entry.parent_id == self._self_id
                and identity != root_identity
                and identity not in self._baseline_direct_children
            ):
                self._remember(entry, adopted=True)
        return table

    def _matching_entries(self, table: dict[int, _ProcEntry]) -> list[_ProcEntry]:
        return [
            entry
            for process_id, start_time in self._tracked.items()
            if (entry := table.get(process_id)) is not None
            and entry.start_time == start_time
        ]

    def reap_adopted(self) -> None:
        table = self.discover()
        for entry in self._matching_entries(table):
            if entry.parent_id != self._self_id or entry.state != "Z":
                continue
            try:
                os.waitpid(entry.process_id, os.WNOHANG)
            except ChildProcessError:
                continue

    def remaining(self) -> list[_ProcEntry]:
        self.reap_adopted()
        table = self.discover()
        return self._matching_entries(table)

    def signal_descendants(self, signum: int) -> tuple[int, list[str]]:
        errors: list[str] = []
        sent_count = 0
        table = self.discover()
        for entry in self._matching_entries(table):
            if entry.state == "Z":
                continue
            try:
                os.kill(entry.process_id, signum)
                sent_count += 1
            except ProcessLookupError:
                continue
            except OSError as exc:
                errors.append(f"descendant-signal-{signum}-errno-{exc.errno}")
        return sent_count, errors

    def evidence(self, remaining_count: int) -> dict[str, object]:
        return {
            "dedicated_monitor": True,
            "subreaper": True,
            "procfs": True,
            "observed_descendants": len(self._observed),
            "observed_detached_descendants": len(self._observed_detached),
            "observed_adopted_descendants": len(self._observed_adopted),
            "remaining_descendants": remaining_count,
            "proof": (
                "subreaper-procfs-descendants-empty"
                if remaining_count == 0
                else "subreaper-procfs-descendants-remain"
            ),
        }

    def restore(self) -> None:
        if not self._prepared:
            return
        if self._prior_subreaper != 1:
            self._prctl_set(0)
        self._prepared = False


def _posix_group_state(process_group_id: int) -> tuple[bool | None, str | None]:
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False, None
    except PermissionError:
        return True, None
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False, None
        return None, f"group-query-errno-{exc.errno}"
    return True, None


def _reap_root(process: subprocess.Popen[bytes], timeout_seconds: float) -> bool:
    if process.poll() is not None:
        return True
    try:
        process.wait(timeout=max(timeout_seconds, 0.0))
    except subprocess.TimeoutExpired:
        return False
    return True


def _wait_linux_tree_empty(
    containment: _LinuxContainment,
    process: subprocess.Popen[bytes],
    process_group_id: int,
    timeout_seconds: float,
) -> tuple[bool, int, list[str]]:
    errors: list[str] = []
    deadline = time.monotonic() + timeout_seconds
    remaining_count = 0
    while True:
        process.poll()
        try:
            remaining_count = len(containment.remaining())
        except (OSError, RuntimeError) as exc:
            errors.append(str(exc) if str(exc).startswith("procfs-") else type(exc).__name__)
            return False, remaining_count, errors
        group_exists, group_error = _posix_group_state(process_group_id)
        if group_error is not None and group_error not in errors:
            errors.append(group_error)
        if group_exists is False and remaining_count == 0:
            return True, 0, errors
        remaining_time = deadline - time.monotonic()
        if remaining_time <= 0:
            return False, remaining_count, errors
        time.sleep(min(_POLL_INTERVAL_SECONDS, remaining_time))


def _signal_posix_group(process_group_id: int, signum: int) -> tuple[bool, str | None]:
    try:
        os.killpg(process_group_id, signum)
    except ProcessLookupError:
        return False, None
    except OSError as exc:
        return False, f"group-signal-{signum}-errno-{exc.errno}"
    return True, None


def _terminate_linux_tree(
    containment: _LinuxContainment,
    process: subprocess.Popen[bytes],
    process_group_id: int,
    *,
    trigger: str,
    termination_grace_seconds: float,
) -> dict[str, object]:
    errors: list[str] = []
    try:
        containment.discover()
    except (OSError, RuntimeError) as exc:
        errors.append(str(exc) if str(exc).startswith("procfs-") else type(exc).__name__)

    soft_group, group_error = _signal_posix_group(process_group_id, signal.SIGTERM)
    if group_error is not None:
        errors.append(group_error)
    try:
        soft_descendants, descendant_errors = containment.signal_descendants(signal.SIGTERM)
    except (OSError, RuntimeError) as exc:
        soft_descendants = 0
        descendant_errors = [
            str(exc) if str(exc).startswith("procfs-") else type(exc).__name__
        ]
    errors.extend(error for error in descendant_errors if error not in errors)
    soft_signal_sent = soft_group or soft_descendants > 0

    empty, remaining_count, wait_errors = _wait_linux_tree_empty(
        containment,
        process,
        process_group_id,
        termination_grace_seconds,
    )
    errors.extend(error for error in wait_errors if error not in errors)

    hard_kill_sent = False
    if not empty:
        hard_group, group_error = _signal_posix_group(process_group_id, signal.SIGKILL)
        if group_error is not None and group_error not in errors:
            errors.append(group_error)
        try:
            hard_descendants, descendant_errors = containment.signal_descendants(signal.SIGKILL)
        except (OSError, RuntimeError) as exc:
            hard_descendants = 0
            descendant_errors = [
                str(exc) if str(exc).startswith("procfs-") else type(exc).__name__
            ]
        errors.extend(error for error in descendant_errors if error not in errors)
        hard_kill_sent = hard_group or hard_descendants > 0
        empty, remaining_count, wait_errors = _wait_linux_tree_empty(
            containment,
            process,
            process_group_id,
            termination_grace_seconds,
        )
        errors.extend(error for error in wait_errors if error not in errors)

    root_reaped = _reap_root(process, termination_grace_seconds)
    if not root_reaped:
        errors.append("root-not-reaped")
    return {
        "trigger": trigger,
        "soft_signal_sent": soft_signal_sent,
        "hard_kill_sent": hard_kill_sent,
        "root_reaped": root_reaped,
        "tree_empty": empty,
        "active_processes": 0 if empty else None,
        "verification": (
            "pgid-esrch-and-subreaper-procfs-empty"
            if empty
            else "linux-tree-termination-unproven"
        ),
        "errors": errors,
        "containment": containment.evidence(remaining_count),
    }


def _linux_completed_termination(containment: _LinuxContainment) -> dict[str, object]:
    return {
        "trigger": None,
        "soft_signal_sent": False,
        "hard_kill_sent": False,
        "root_reaped": True,
        "tree_empty": True,
        "active_processes": 0,
        "verification": "pgid-esrch-and-subreaper-procfs-empty",
        "errors": [],
        "containment": containment.evidence(0),
    }


def _restore_linux_containment(
    containment: _LinuxContainment,
    outcome: _RunOutcome,
) -> _RunOutcome:
    try:
        containment.restore()
    except OSError as exc:
        errors = outcome.termination.get("errors")
        if isinstance(errors, list):
            errors.append(f"subreaper-restore-errno-{exc.errno}")
        outcome.status = "cleanup-failed"
        outcome.error = _safe_error("containment-restore", exc)
    return outcome


def _run_linux_locked(
    argv: Sequence[str],
    *,
    cwd: Path,
    log_handle: BinaryIO,
    timeout_seconds: float,
    termination_grace_seconds: float,
    cancellation: threading.Event,
) -> _RunOutcome:
    containment = _LinuxContainment()
    try:
        containment.prepare()
    except BaseException as exc:
        return _RunOutcome(
            status="launch-failed",
            child_exit_code=None,
            mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
            termination={
                "trigger": "launch-failure",
                "soft_signal_sent": False,
                "hard_kill_sent": False,
                "root_reaped": False,
                "tree_empty": True,
                "active_processes": 0,
                "verification": "containment-setup-failed-before-launch",
                "errors": [],
                "containment": {
                    "dedicated_monitor": True,
                    "subreaper": False,
                    "procfs": False,
                    "observed_descendants": 0,
                    "observed_detached_descendants": 0,
                    "observed_adopted_descendants": 0,
                    "remaining_descendants": 0,
                    "proof": "command-not-started",
                },
            },
            error=_safe_error("containment-setup", exc),
        )

    try:
        process = subprocess.Popen(
            list(argv),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except BaseException as exc:
        outcome = _RunOutcome(
            status="launch-failed",
            child_exit_code=None,
            mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
            termination={
                "trigger": "launch-failure",
                "soft_signal_sent": False,
                "hard_kill_sent": False,
                "root_reaped": False,
                "tree_empty": True,
                "active_processes": 0,
                "verification": "no-process-started",
                "errors": [],
                "containment": containment.evidence(0),
            },
            error=_safe_error("launch", exc),
        )
        return _restore_linux_containment(containment, outcome)

    process_group_id = process.pid
    try:
        containment.register_root(process.pid, process_group_id)
    except (OSError, RuntimeError) as exc:
        termination = _terminate_linux_tree(
            containment,
            process,
            process_group_id,
            trigger="containment-failure",
            termination_grace_seconds=termination_grace_seconds,
        )
        outcome = _RunOutcome(
            status="cleanup-failed",
            child_exit_code=process.returncode,
            mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
            termination=termination,
            error=_safe_error("containment-register", exc),
        )
        return _restore_linux_containment(containment, outcome)

    disposition = _wait_for_root(process, timeout_seconds, cancellation)
    if disposition == "completed":
        child_exit_code = process.returncode
        try:
            remaining_count = len(containment.remaining())
            group_exists, query_error = _posix_group_state(process_group_id)
        except (OSError, RuntimeError) as exc:
            remaining_count = -1
            group_exists = None
            query_error = type(exc).__name__
        if group_exists is False and remaining_count == 0:
            outcome = _RunOutcome(
                status="completed",
                child_exit_code=child_exit_code,
                mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
                termination=_linux_completed_termination(containment),
            )
            return _restore_linux_containment(containment, outcome)

        termination = _terminate_linux_tree(
            containment,
            process,
            process_group_id,
            trigger="orphan-descendant",
            termination_grace_seconds=termination_grace_seconds,
        )
        if query_error is not None:
            errors = termination["errors"]
            assert isinstance(errors, list)
            errors.insert(0, query_error)
        outcome = _RunOutcome(
            status="cleanup-failed",
            child_exit_code=child_exit_code,
            mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
            termination=termination,
            error={"stage": "normal-exit", "type": "DescendantSurvivedRoot"},
        )
        return _restore_linux_containment(containment, outcome)

    trigger = "cancelled" if disposition == "cancelled" else "timeout"
    termination = _terminate_linux_tree(
        containment,
        process,
        process_group_id,
        trigger=trigger,
        termination_grace_seconds=termination_grace_seconds,
    )
    status = disposition if termination["tree_empty"] else "cleanup-failed"
    outcome = _RunOutcome(
        status=status,
        child_exit_code=process.returncode,
        mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
        termination=termination,
        error=(
            None
            if status == disposition
            else {"stage": "tree-cleanup", "type": "TerminationProofFailed"}
        ),
    )
    return _restore_linux_containment(containment, outcome)


def _linux_monitor_failure(
    stage: str,
    error_type: str,
    *,
    command_may_have_started: bool,
) -> _RunOutcome:
    tree_empty = not command_may_have_started
    return _RunOutcome(
        status="cleanup-failed" if command_may_have_started else "launch-failed",
        child_exit_code=None,
        mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
        termination={
            "trigger": "monitor-failure" if command_may_have_started else "launch-failure",
            "soft_signal_sent": False,
            "hard_kill_sent": False,
            "root_reaped": False,
            "tree_empty": tree_empty,
            "active_processes": 0 if tree_empty else None,
            "verification": (
                "monitor-not-started"
                if tree_empty
                else "dedicated-monitor-tree-proof-unavailable"
            ),
            "errors": [error_type],
            "containment": {
                "dedicated_monitor": True,
                "subreaper": False,
                "procfs": False,
                "observed_descendants": 0,
                "observed_detached_descendants": 0,
                "observed_adopted_descendants": 0,
                "remaining_descendants": 0,
                "proof": "command-not-started" if tree_empty else "monitor-proof-unavailable",
            },
        },
        error={"stage": stage, "type": error_type},
    )


def _linux_prelaunch_cancelled() -> _RunOutcome:
    return _RunOutcome(
        status="cancelled",
        child_exit_code=None,
        mechanism="linux-dedicated-monitor-subreaper-procfs-process-group",
        termination={
            "trigger": "cancelled",
            "soft_signal_sent": False,
            "hard_kill_sent": False,
            "root_reaped": False,
            "tree_empty": True,
            "active_processes": 0,
            "verification": "launch-ack-withheld-command-not-started",
            "errors": [],
            "containment": {
                "dedicated_monitor": True,
                "subreaper": False,
                "procfs": False,
                "observed_descendants": 0,
                "observed_detached_descendants": 0,
                "observed_adopted_descendants": 0,
                "remaining_descendants": 0,
                "proof": "command-not-started",
            },
        },
    )


def _outcome_payload(outcome: _RunOutcome) -> bytes:
    return json.dumps(
        {
            "status": outcome.status,
            "child_exit_code": outcome.child_exit_code,
            "mechanism": outcome.mechanism,
            "termination": outcome.termination,
            "error": outcome.error,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _write_pipe_bytes(descriptor: int, payload: bytes) -> None:
    offset = 0
    while offset < len(payload):
        offset += os.write(descriptor, payload[offset:])


class _MonitorProtocolFailure(RuntimeError):
    def __init__(self, stage: str, error_type: str) -> None:
        super().__init__(error_type)
        self.stage = stage
        self.error_type = error_type


def _linux_monitor_entry(
    config: dict[str, object],
    *,
    log_handle: BinaryIO,
    outcome_write: int,
    ready_write: int,
    launch_read: int,
) -> None:
    """Own and supervise exactly one Linux command lineage in a helper."""

    try:
        argv_value = config["argv"]
        cwd_value = config["cwd"]
        timeout_value = config["timeout_seconds"]
        grace_value = config["termination_grace_seconds"]
        if (
            not isinstance(argv_value, list)
            or not argv_value
            or not all(isinstance(item, str) for item in argv_value)
            or not isinstance(cwd_value, str)
            or not isinstance(timeout_value, (int, float))
            or isinstance(timeout_value, bool)
            or not isinstance(grace_value, (int, float))
            or isinstance(grace_value, bool)
        ):
            raise ValueError("invalid monitor configuration")
        with _capture_cancellation() as (monitor_cancellation, _state):
            _write_pipe_bytes(ready_write, b"R")
            os.close(ready_write)
            launch_ack = os.read(launch_read, 1)
            os.close(launch_read)
            if launch_ack != b"A":
                outcome = _linux_monitor_failure(
                    "monitor-launch-ack",
                    "MonitorLaunchNotAcknowledged",
                    command_may_have_started=False,
                )
            else:
                outcome = _run_linux_locked(
                    argv_value,
                    cwd=Path(cwd_value),
                    log_handle=log_handle,
                    timeout_seconds=float(timeout_value),
                    termination_grace_seconds=float(grace_value),
                    cancellation=monitor_cancellation,
                )
    except BaseException as exc:
        try:
            os.close(ready_write)
        except OSError:
            pass
        try:
            os.close(launch_read)
        except OSError:
            pass
        outcome = _linux_monitor_failure(
            "monitor-execution",
            type(exc).__name__,
            command_may_have_started=True,
        )
    try:
        _write_pipe_bytes(outcome_write, _outcome_payload(outcome))
    except OSError:
        pass
    finally:
        os.close(outcome_write)


def _wait_for_monitor_marker(
    descriptor: int,
    process: subprocess.Popen[bytes],
    cancellation: threading.Event,
    timeout_seconds: float,
) -> bytes:
    deadline = time.monotonic() + timeout_seconds
    while process.poll() is None:
        remaining = deadline - time.monotonic()
        if remaining <= 0 or cancellation.is_set():
            break
        readable, _, _ = select.select(
            [descriptor],
            [],
            [],
            min(_POLL_INTERVAL_SECONDS, remaining),
        )
        if readable:
            return os.read(descriptor, 1)
    readable, _, _ = select.select([descriptor], [], [], 0)
    return os.read(descriptor, 1) if readable else b""


def _write_monitor_config(
    descriptor: int,
    payload: bytes,
    *,
    process: subprocess.Popen[bytes],
    cancellation: threading.Event,
    timeout_seconds: float,
) -> None:
    os.set_blocking(descriptor, False)
    deadline = time.monotonic() + timeout_seconds
    offset = 0
    while offset < len(payload):
        if cancellation.is_set():
            raise InterruptedError("monitor config write cancelled")
        if process.poll() is not None:
            raise BrokenPipeError("monitor exited during config write")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("monitor config write timed out")
        try:
            written = os.write(descriptor, payload[offset:])
        except BlockingIOError:
            written = 0
        if written > 0:
            offset += written
            continue
        _, writable, _ = select.select(
            [],
            [descriptor],
            [],
            min(_POLL_INTERVAL_SECONDS, remaining),
        )
        if not writable:
            continue


def _terminate_and_reap_monitor(
    process: subprocess.Popen[bytes],
    timeout_seconds: float,
) -> bool:
    try:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=timeout_seconds)
        return True
    except subprocess.TimeoutExpired:
        try:
            process.kill()
            process.wait(timeout=timeout_seconds)
            return True
        except (OSError, subprocess.TimeoutExpired):
            return False
    except OSError:
        return process.poll() is not None


def _decode_linux_monitor_outcome(payload: bytes) -> _RunOutcome:
    try:
        value = json.loads(payload.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("monitor result is not an object")
        termination = value["termination"]
        if not isinstance(termination, dict):
            raise ValueError("monitor termination is not an object")
        error = value.get("error")
        if error is not None and not isinstance(error, dict):
            raise ValueError("monitor error is not an object")
        return _RunOutcome(
            status=str(value["status"]),
            child_exit_code=value.get("child_exit_code"),
            mechanism=str(value["mechanism"]),
            termination=termination,
            error=error,
        )
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return _linux_monitor_failure(
            "monitor-result",
            "MonitorResultInvalid",
            command_may_have_started=True,
        )


def _collect_linux_monitor_outcome(
    monitor: subprocess.Popen[bytes],
    outcome_read: int,
    *,
    timeout_seconds: float,
    termination_grace_seconds: float,
    cancellation: threading.Event,
) -> _RunOutcome:
    os.set_blocking(outcome_read, False)
    chunks: list[bytes] = []
    watchdog_deadline = (
        time.monotonic()
        + timeout_seconds
        + max(termination_grace_seconds * 2.0, 0.1)
        + 2.0
    )
    forced_deadline: float | None = None
    monitor_forced = False
    monitor_returncode: int | None = None
    while monitor_returncode is None:
        try:
            chunk = os.read(outcome_read, 65536)
        except BlockingIOError:
            chunk = b""
        if chunk:
            chunks.append(chunk)
        monitor_returncode = monitor.poll()
        if monitor_returncode is not None:
            break

        now = time.monotonic()
        if cancellation.is_set() and forced_deadline is None:
            try:
                monitor.send_signal(signal.SIGTERM)
            except OSError:
                pass
            forced_deadline = now + max(termination_grace_seconds * 2.0, 0.1) + 2.0
        if now >= watchdog_deadline and forced_deadline is None:
            try:
                monitor.send_signal(signal.SIGTERM)
            except OSError:
                pass
            forced_deadline = now + max(termination_grace_seconds * 2.0, 0.1) + 2.0
        if forced_deadline is not None and now >= forced_deadline:
            try:
                monitor.kill()
                monitor_forced = True
            except OSError:
                pass
            try:
                monitor_returncode = monitor.wait(
                    timeout=max(termination_grace_seconds, 0.1) + 1.0
                )
            except subprocess.TimeoutExpired:
                monitor_returncode = None
            break
        time.sleep(_POLL_INTERVAL_SECONDS)

    if monitor_returncode is not None:
        os.set_blocking(outcome_read, True)
        while True:
            chunk = os.read(outcome_read, 65536)
            if not chunk:
                break
            chunks.append(chunk)

    if monitor_forced or monitor_returncode != 0:
        return _linux_monitor_failure(
            "monitor-exit",
            "MonitorTerminationUnproven",
            command_may_have_started=True,
        )
    return _decode_linux_monitor_outcome(b"".join(chunks))


def _run_linux_monitor(
    argv: Sequence[str],
    *,
    cwd: Path,
    log_handle: BinaryIO,
    timeout_seconds: float,
    termination_grace_seconds: float,
    cancellation: threading.Event,
    before_launch_ack: Callable[[], None] | None = None,
) -> _RunOutcome:
    effective_cwd = cwd.resolve(strict=False)
    open_descriptors: set[int] = set()
    descriptor_cleanup_errors: list[int | None] = []
    monitor: subprocess.Popen[bytes] | None = None
    command_may_have_started = False
    outcome: _RunOutcome | None = None
    handshake_timeout = max(termination_grace_seconds, 0.1) + 2.0

    def create_pipe() -> tuple[int, int]:
        descriptors = os.pipe()
        open_descriptors.update(descriptors)
        return descriptors

    def close_descriptor(descriptor: int) -> None:
        if descriptor not in open_descriptors:
            return
        try:
            os.close(descriptor)
        except OSError as exc:
            # Cleanup continues across every owned descriptor; a later helper
            # termination/reap is the authoritative process-leak boundary.
            descriptor_cleanup_errors.append(exc.errno)
        finally:
            open_descriptors.remove(descriptor)

    try:
        config_read, config_write = create_pipe()
        outcome_read, outcome_write = create_pipe()
        ready_read, ready_write = create_pipe()
        launch_read, launch_write = create_pipe()
        monitor = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _LINUX_MONITOR_BOOTSTRAP_CODE,
                str(config_read),
                str(outcome_write),
                str(ready_write),
                str(log_handle.fileno()),
                str(launch_read),
            ],
            cwd=Path(__file__).resolve().parent,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            pass_fds=(
                config_read,
                outcome_write,
                ready_write,
                launch_read,
                log_handle.fileno(),
            ),
        )
        close_descriptor(config_read)
        close_descriptor(outcome_write)
        close_descriptor(ready_write)
        close_descriptor(launch_read)

        marker = _wait_for_monitor_marker(
            ready_read,
            monitor,
            cancellation,
            handshake_timeout,
        )
        if marker != b"C":
            raise _MonitorProtocolFailure(
                "monitor-config-readiness",
                "MonitorConfigReadinessMissing",
            )

        try:
            config_payload = json.dumps(
                {
                    "argv": list(argv),
                    "cwd": os.fspath(effective_cwd),
                    "timeout_seconds": timeout_seconds,
                    "termination_grace_seconds": termination_grace_seconds,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        except BaseException as exc:
            raise _MonitorProtocolFailure(
                "monitor-config-encode",
                type(exc).__name__,
            ) from exc
        try:
            _write_monitor_config(
                config_write,
                config_payload,
                process=monitor,
                cancellation=cancellation,
                timeout_seconds=handshake_timeout,
            )
        except BaseException as exc:
            raise _MonitorProtocolFailure(
                "monitor-config-write",
                type(exc).__name__,
            ) from exc
        close_descriptor(config_write)

        marker = _wait_for_monitor_marker(
            ready_read,
            monitor,
            cancellation,
            handshake_timeout,
        )
        if marker != b"R":
            raise _MonitorProtocolFailure(
                "monitor-command-readiness",
                "MonitorCommandReadinessMissing",
            )
        close_descriptor(ready_read)
        if before_launch_ack is not None:
            before_launch_ack()
        if cancellation.is_set():
            raise _MonitorProtocolFailure(
                "monitor-launch-ack",
                "MonitorLaunchAcknowledgementWithheld",
            )
        try:
            _write_monitor_config(
                launch_write,
                b"A",
                process=monitor,
                cancellation=cancellation,
                timeout_seconds=handshake_timeout,
            )
        except BaseException as exc:
            raise _MonitorProtocolFailure(
                "monitor-launch-ack",
                type(exc).__name__,
            ) from exc
        command_may_have_started = True
        close_descriptor(launch_write)
        outcome = _collect_linux_monitor_outcome(
            monitor,
            outcome_read,
            timeout_seconds=timeout_seconds,
            termination_grace_seconds=termination_grace_seconds,
            cancellation=cancellation,
        )
    except _MonitorProtocolFailure as exc:
        if cancellation.is_set() and not command_may_have_started:
            outcome = _linux_prelaunch_cancelled()
        else:
            outcome = _linux_monitor_failure(
                exc.stage,
                exc.error_type,
                command_may_have_started=command_may_have_started,
            )
    except BaseException as exc:
        outcome = _linux_monitor_failure(
            "monitor-protocol",
            type(exc).__name__,
            command_may_have_started=command_may_have_started,
        )
    finally:
        for descriptor in tuple(open_descriptors):
            close_descriptor(descriptor)
        cleanup_ok = monitor is None or _terminate_and_reap_monitor(
            monitor,
            max(termination_grace_seconds, 0.1) + 1.0,
        )

    if not cleanup_ok or descriptor_cleanup_errors:
        return _linux_monitor_failure(
            "monitor-cleanup",
            (
                "MonitorReapFailed"
                if not cleanup_ok
                else "MonitorDescriptorCloseFailed"
            ),
            command_may_have_started=command_may_have_started,
        )
    assert outcome is not None
    return outcome


def _run_posix(
    argv: Sequence[str],
    *,
    cwd: Path,
    log_handle: BinaryIO,
    timeout_seconds: float,
    termination_grace_seconds: float,
    cancellation: threading.Event,
) -> _RunOutcome:
    if not sys.platform.startswith("linux"):
        return _RunOutcome(
            status="launch-failed",
            child_exit_code=None,
            mechanism="posix-complete-containment-unavailable",
            termination={
                "trigger": "launch-failure",
                "soft_signal_sent": False,
                "hard_kill_sent": False,
                "root_reaped": False,
                "tree_empty": True,
                "active_processes": 0,
                "verification": "command-not-started",
                "errors": ["complete-posix-containment-unavailable"],
            },
            error={"stage": "containment-setup", "type": "UnsupportedPlatform"},
        )
    return _run_linux_monitor(
        argv,
        cwd=cwd,
        log_handle=log_handle,
        timeout_seconds=timeout_seconds,
        termination_grace_seconds=termination_grace_seconds,
        cancellation=cancellation,
    )


class _WindowsJob:
    """Minimal ctypes adapter for a KILL_ON_JOB_CLOSE Windows Job Object."""

    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    _JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
    _PROCESS_TERMINATE = 0x0001
    _PROCESS_SET_QUOTA = 0x0100
    _WAIT_OBJECT_0 = 0x00000000
    _WAIT_TIMEOUT = 0x00000102

    def __init__(self) -> None:
        from ctypes import wintypes

        class IoCounters(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class BasicLimitInformation(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class ExtendedLimitInformation(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", BasicLimitInformation),
                ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        class BasicAccountingInformation(ctypes.Structure):
            _fields_ = [
                ("TotalUserTime", ctypes.c_longlong),
                ("TotalKernelTime", ctypes.c_longlong),
                ("ThisPeriodTotalUserTime", ctypes.c_longlong),
                ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
                ("TotalPageFaultCount", wintypes.DWORD),
                ("TotalProcesses", wintypes.DWORD),
                ("ActiveProcesses", wintypes.DWORD),
                ("TotalTerminatedProcesses", wintypes.DWORD),
            ]

        self._extended_type = ExtendedLimitInformation
        self._accounting_type = BasicAccountingInformation
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        self._kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self._kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        self._kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
        ]
        self._kernel32.SetInformationJobObject.restype = wintypes.BOOL
        self._kernel32.OpenProcess.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]
        self._kernel32.OpenProcess.restype = wintypes.HANDLE
        self._kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self._kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        self._kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self._kernel32.TerminateJobObject.restype = wintypes.BOOL
        self._kernel32.QueryInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self._kernel32.QueryInformationJobObject.restype = wintypes.BOOL
        self._kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self._kernel32.WaitForSingleObject.restype = wintypes.DWORD
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self._kernel32.CloseHandle.restype = wintypes.BOOL

        self._handle = self._kernel32.CreateJobObjectW(None, None)
        if not self._handle:
            raise ctypes.WinError(ctypes.get_last_error())

        limits = self._extended_type()
        limits.BasicLimitInformation.LimitFlags = self._JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self._kernel32.SetInformationJobObject(
            self._handle,
            self._JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, process_id: int) -> None:
        process_handle = self._kernel32.OpenProcess(
            self._PROCESS_TERMINATE | self._PROCESS_SET_QUOTA,
            False,
            process_id,
        )
        if not process_handle:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            if not self._kernel32.AssignProcessToJobObject(self._handle, process_handle):
                raise ctypes.WinError(ctypes.get_last_error())
        finally:
            self._kernel32.CloseHandle(process_handle)

    def terminate(self) -> None:
        if not self._kernel32.TerminateJobObject(self._handle, 1):
            raise ctypes.WinError(ctypes.get_last_error())

    def _active_processes(self) -> tuple[int, str | None]:
        accounting = self._accounting_type()
        returned_length = ctypes.c_ulong(0)
        if not self._kernel32.QueryInformationJobObject(
            self._handle,
            self._JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
            ctypes.byref(accounting),
            ctypes.sizeof(accounting),
            ctypes.byref(returned_length),
        ):
            return -1, f"job-query-winerror-{ctypes.get_last_error()}"
        return int(accounting.ActiveProcesses), None

    def proof_empty(
        self,
        timeout_seconds: float,
        *,
        require_signaled: bool = True,
    ) -> tuple[bool, int, str | None]:
        if require_signaled:
            timeout_ms = min(max(math.ceil(timeout_seconds * 1000), 0), 0xFFFFFFFE)
            wait_result = self._kernel32.WaitForSingleObject(self._handle, timeout_ms)
            if wait_result not in (self._WAIT_OBJECT_0, self._WAIT_TIMEOUT):
                return False, -1, f"job-wait-result-{wait_result}"
            active_processes, query_error = self._active_processes()
            if query_error is not None:
                return False, active_processes, query_error
            empty = wait_result == self._WAIT_OBJECT_0 and active_processes == 0
            return empty, active_processes, None

        # A Job Object is not generally signaled on ordinary process exit; the
        # documented signaled transition is tied to end-of-job termination.
        # After the bootstrap process handle is reaped, bounded accounting at
        # ActiveProcesses == 0 is the ordinary-completion proof.
        deadline = time.monotonic() + timeout_seconds
        while True:
            active_processes, query_error = self._active_processes()
            if query_error is not None:
                return False, active_processes, query_error
            if active_processes == 0:
                return True, 0, None
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False, active_processes, None
            time.sleep(min(_POLL_INTERVAL_SECONDS, remaining))

    def close(self) -> None:
        handle = getattr(self, "_handle", None)
        if handle:
            self._kernel32.CloseHandle(handle)
            self._handle = None


def _windows_bootstrap_payload(argv: Sequence[str]) -> bytes:
    return json.dumps(
        {"argv": list(argv)},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"


class _WindowsBootstrapGate:
    """Make payload release impossible until Job Object assignment succeeds."""

    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self.process = process
        self.assigned = False

    def assign(self, job: object) -> None:
        assign = getattr(job, "assign")
        assign(self.process.pid)
        self.assigned = True

    def release(self, argv: Sequence[str]) -> None:
        if not self.assigned:
            raise RuntimeError("bootstrap is not assigned to the Job Object")
        if self.process.stdin is None:
            raise RuntimeError("bootstrap stdin is unavailable")
        payload = _windows_bootstrap_payload(argv)
        self.process.stdin.write(payload)
        self.process.stdin.flush()
        self.process.stdin.close()


def _read_windows_control_events(
    process: subprocess.Popen[bytes],
) -> tuple[list[dict[str, object]], list[str]]:
    events: list[dict[str, object]] = []
    errors: list[str] = []
    if process.stdout is None:
        return events, ["bootstrap-control-unavailable"]
    try:
        control_bytes = process.stdout.read()
    except OSError as exc:
        return events, [f"bootstrap-control-errno-{exc.errno}"]
    finally:
        process.stdout.close()

    for line in control_bytes.splitlines():
        try:
            value = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append("bootstrap-control-invalid-json")
            continue
        if not isinstance(value, dict) or not isinstance(value.get("event"), str):
            errors.append("bootstrap-control-invalid-record")
            continue
        events.append(value)
    return events, errors


def _stop_uncontained_windows_bootstrap(
    process: subprocess.Popen[bytes],
    termination_grace_seconds: float,
) -> bool:
    if process.stdin is not None and not process.stdin.closed:
        process.stdin.close()
    try:
        process.wait(timeout=termination_grace_seconds)
        return True
    except subprocess.TimeoutExpired:
        process.terminate()
    try:
        process.wait(timeout=termination_grace_seconds)
        return True
    except subprocess.TimeoutExpired:
        process.kill()
    try:
        process.wait(timeout=termination_grace_seconds)
    except subprocess.TimeoutExpired:
        return False
    return True


def _terminate_windows_job(
    job: _WindowsJob,
    process: subprocess.Popen[bytes],
    *,
    trigger: str,
    termination_grace_seconds: float,
) -> dict[str, object]:
    errors: list[str] = []
    hard_kill_sent = False
    try:
        job.terminate()
        hard_kill_sent = True
    except OSError as exc:
        errors.append(f"job-terminate-winerror-{getattr(exc, 'winerror', None)}")

    empty, active_processes, proof_error = job.proof_empty(termination_grace_seconds)
    if proof_error is not None:
        errors.append(proof_error)
    root_reaped = _reap_root(process, termination_grace_seconds)
    if not root_reaped:
        errors.append("bootstrap-not-reaped")
    return {
        "trigger": trigger,
        "soft_signal_sent": False,
        "hard_kill_sent": hard_kill_sent,
        "root_reaped": root_reaped,
        "tree_empty": empty,
        "active_processes": active_processes if active_processes >= 0 else None,
        "verification": (
            "job-signaled-and-active-processes-zero"
            if empty
            else "job-termination-unproven"
        ),
        "errors": errors,
    }


def _run_windows(
    argv: Sequence[str],
    *,
    cwd: Path,
    log_handle: BinaryIO,
    timeout_seconds: float,
    termination_grace_seconds: float,
    cancellation: threading.Event,
    release_bootstrap: Callable[[_WindowsBootstrapGate, Sequence[str]], None]
    | None = None,
) -> _RunOutcome:
    try:
        job = _WindowsJob()
    except BaseException as exc:
        return _RunOutcome(
            status="launch-failed",
            child_exit_code=None,
            mechanism="windows-job-object-kill-on-close",
            termination={
                "trigger": "launch-failure",
                "soft_signal_sent": False,
                "hard_kill_sent": False,
                "root_reaped": False,
                "tree_empty": True,
                "active_processes": 0,
                "verification": "job-creation-failed-before-bootstrap",
                "errors": [],
            },
            error=_safe_error("job-create", exc),
        )

    try:
        try:
            process = subprocess.Popen(
                [sys.executable, "-I", "-c", _WINDOWS_BOOTSTRAP_CODE],
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=log_handle,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except BaseException as exc:
            return _RunOutcome(
                status="launch-failed",
                child_exit_code=None,
                mechanism="windows-job-object-kill-on-close",
                termination={
                    "trigger": "launch-failure",
                    "soft_signal_sent": False,
                    "hard_kill_sent": False,
                    "root_reaped": False,
                    "tree_empty": True,
                    "active_processes": 0,
                    "verification": "bootstrap-not-started",
                    "errors": [],
                },
                error=_safe_error("bootstrap-launch", exc),
            )

        gate = _WindowsBootstrapGate(process)
        try:
            gate.assign(job)
        except BaseException as exc:
            # Assignment is a distinct phase: no payload write is attempted
            # until it succeeds, so the target cannot have started here.
            root_reaped = _stop_uncontained_windows_bootstrap(
                process,
                termination_grace_seconds,
            )
            events, control_errors = _read_windows_control_events(process)
            empty, active_processes, proof_error = job.proof_empty(
                termination_grace_seconds,
                require_signaled=False,
            )
            errors = list(control_errors)
            if proof_error is not None:
                errors.append(proof_error)
            if not root_reaped:
                errors.append("bootstrap-not-reaped")
            status = "launch-failed" if empty and root_reaped else "cleanup-failed"
            return _RunOutcome(
                status=status,
                child_exit_code=None,
                mechanism="windows-job-object-kill-on-close",
                termination={
                    "trigger": "launch-failure",
                    "soft_signal_sent": False,
                    "hard_kill_sent": False,
                    "root_reaped": root_reaped,
                    "tree_empty": empty,
                    "active_processes": active_processes if active_processes >= 0 else None,
                    "verification": (
                        "job-assignment-failed-before-payload"
                        if empty and root_reaped
                        else "unassigned-bootstrap-cleanup-unproven"
                    ),
                    "errors": errors,
                    "bootstrap_control_events": [
                        str(event.get("event")) for event in events
                    ],
                },
                error=_safe_error("job-assign", exc),
            )

        try:
            if release_bootstrap is None:
                gate.release(argv)
            else:
                release_bootstrap(gate, argv)
        except BaseException as exc:
            # A write/flush/close failure happens after containment exists and
            # may occur after partial or complete payload delivery.  Close the
            # gate, terminate the entire Job, and inspect control events; never
            # relabel this uncertain phase as "never released".
            if process.stdin is not None and not process.stdin.closed:
                try:
                    process.stdin.close()
                except OSError:
                    pass
            termination = _terminate_windows_job(
                job,
                process,
                trigger="launch-release-failure",
                termination_grace_seconds=termination_grace_seconds,
            )
            events, control_errors = _read_windows_control_events(process)
            errors = termination["errors"]
            assert isinstance(errors, list)
            errors.extend(error for error in control_errors if error not in errors)
            termination["bootstrap_control_events"] = [
                str(event.get("event")) for event in events
            ]
            return _RunOutcome(
                status="cleanup-failed",
                child_exit_code=_child_exit_code_from_events(events),
                mechanism="windows-job-object-kill-on-close",
                termination=termination,
                error=_safe_error("bootstrap-release", exc),
            )

        disposition = _wait_for_root(process, timeout_seconds, cancellation)
        if disposition != "completed":
            trigger = "cancelled" if disposition == "cancelled" else "timeout"
            termination = _terminate_windows_job(
                job,
                process,
                trigger=trigger,
                termination_grace_seconds=termination_grace_seconds,
            )
            events, control_errors = _read_windows_control_events(process)
            errors = termination["errors"]
            assert isinstance(errors, list)
            errors.extend(error for error in control_errors if error not in errors)
            status = disposition if termination["tree_empty"] else "cleanup-failed"
            return _RunOutcome(
                status=status,
                child_exit_code=_child_exit_code_from_events(events),
                mechanism="windows-job-object-kill-on-close",
                termination=termination,
                error=(
                    None
                    if status == disposition
                    else {"stage": "tree-cleanup", "type": "TerminationProofFailed"}
                ),
            )

        events, control_errors = _read_windows_control_events(process)
        launch_failure = next(
            (event for event in events if event.get("event") == "launch-failed"),
            None,
        )
        child_exit_code = _child_exit_code_from_events(events)
        # Process-handle signaling can precede the Job Object's accounting
        # transition to zero by a few scheduler ticks.  Await bounded
        # ActiveProcesses accounting before classifying an ordinary completion
        # as an orphan.  Job signaling is required separately after forced
        # TerminateJobObject cleanup, not after an ordinary process exit.
        empty, active_processes, proof_error = job.proof_empty(
            termination_grace_seconds,
            require_signaled=False,
        )

        if launch_failure is not None and empty:
            return _RunOutcome(
                status="launch-failed",
                child_exit_code=None,
                mechanism="windows-job-object-kill-on-close",
                termination={
                    "trigger": "launch-failure",
                    "soft_signal_sent": False,
                    "hard_kill_sent": False,
                    "root_reaped": True,
                    "tree_empty": True,
                    "active_processes": 0,
                    "verification": "bootstrap-reaped-and-active-processes-zero",
                    "errors": control_errors,
                },
                error={
                    "stage": "target-launch",
                    "type": str(launch_failure.get("error_type", "UnknownError")),
                },
            )

        completed_event = any(event.get("event") == "completed" for event in events)
        if empty and proof_error is None and completed_event and child_exit_code is not None:
            return _RunOutcome(
                status="completed",
                child_exit_code=child_exit_code,
                mechanism="windows-job-object-kill-on-close",
                termination={
                    "trigger": None,
                    "soft_signal_sent": False,
                    "hard_kill_sent": False,
                    "root_reaped": True,
                    "tree_empty": True,
                    "active_processes": 0,
                    "verification": "bootstrap-reaped-and-active-processes-zero",
                    "errors": control_errors,
                },
            )

        trigger = "orphan-descendant" if active_processes > 0 else "completion-unproven"
        termination = _terminate_windows_job(
            job,
            process,
            trigger=trigger,
            termination_grace_seconds=termination_grace_seconds,
        )
        errors = termination["errors"]
        assert isinstance(errors, list)
        if proof_error is not None and proof_error not in errors:
            errors.insert(0, proof_error)
        errors.extend(error for error in control_errors if error not in errors)
        return _RunOutcome(
            status="cleanup-failed",
            child_exit_code=child_exit_code,
            mechanism="windows-job-object-kill-on-close",
            termination=termination,
            error={"stage": "normal-exit", "type": "DescendantOrProofSurvivedRoot"},
        )
    finally:
        job.close()


def _child_exit_code_from_events(events: Sequence[dict[str, object]]) -> int | None:
    for event in reversed(events):
        if event.get("event") != "completed":
            continue
        value = event.get("child_exit_code")
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _sealed_log_metadata(log_path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    byte_count = 0
    line_count = 0
    final_byte: bytes | None = None
    with log_path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            byte_count += len(chunk)
            line_count += chunk.count(b"\n")
            final_byte = chunk[-1:]
    if byte_count and final_byte != b"\n":
        line_count += 1
    return {
        "sealed": True,
        "sha256": digest.hexdigest(),
        "bytes": byte_count,
        "lines": line_count,
    }


def _atomic_write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        if os.name == "posix":
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
    except BaseException:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass
        raise


def supervise_command(
    argv: Sequence[str],
    *,
    cwd: Path,
    cwd_ref: str,
    log_path: Path,
    result_path: Path,
    timeout_seconds: float,
    termination_grace_seconds: float = 1.0,
) -> dict[str, object]:
    """Run one command under a complete-tree supervisor and persist its receipt.

    A ``completed`` status means the root command exited (zero or non-zero) and
    no descendant remains.  The caller, not this module, maps the child exit
    code to validation pass/fail.  Any unproven cleanup is non-passing and never
    receives a sealed-log claim.
    """

    normalized_argv = _validate_inputs(
        argv,
        cwd_ref,
        timeout_seconds,
        termination_grace_seconds,
    )
    # Resolve relative cwd against the caller before any helper changes its
    # own working directory to import this internal module.
    cwd = Path(cwd).resolve(strict=False)
    log_path = Path(log_path)
    result_path = Path(result_path)
    if log_path.resolve(strict=False) == result_path.resolve(strict=False):
        raise ValueError("log_path and result_path must be different")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = _utc_now()
    monotonic_started = time.monotonic()
    log_metadata: dict[str, object] = {
        "sealed": False,
        "sha256": None,
        "bytes": None,
        "lines": None,
    }

    with log_path.open("wb", buffering=0) as log_handle:
        with _capture_cancellation() as (cancellation, _cancellation_state):
            if os.name == "nt":
                outcome = _run_windows(
                    normalized_argv,
                    cwd=cwd,
                    log_handle=log_handle,
                    timeout_seconds=timeout_seconds,
                    termination_grace_seconds=termination_grace_seconds,
                    cancellation=cancellation,
                )
                platform_family = "windows"
            else:
                outcome = _run_posix(
                    normalized_argv,
                    cwd=cwd,
                    log_handle=log_handle,
                    timeout_seconds=timeout_seconds,
                    termination_grace_seconds=termination_grace_seconds,
                    cancellation=cancellation,
                )
                platform_family = "posix"

        if outcome.termination["tree_empty"]:
            try:
                log_handle.flush()
                os.fsync(log_handle.fileno())
            except OSError as exc:
                outcome.status = "cleanup-failed"
                outcome.error = _safe_error("log-seal", exc)

    # Do not claim a sealed digest after a log-fsync failure.  Other
    # non-passing outcomes (for example an orphan that was successfully
    # killed) may retain a stable forensic log once the tree is proven empty.
    if outcome.termination["tree_empty"] and not (
        outcome.error and outcome.error.get("stage") == "log-seal"
    ):
        log_metadata = _sealed_log_metadata(log_path)

    finished_at = _utc_now()
    duration_seconds = round(max(0.0, time.monotonic() - monotonic_started), 6)
    clock_adjustment_seconds = _clock_adjustment_seconds(
        started_at,
        finished_at,
        duration_seconds,
    )
    safe_argv = _privacy_safe_argv(normalized_argv, cwd)
    safe_argv_bytes = _canonical_argv_bytes(safe_argv)
    effective_argv_bytes = _canonical_argv_bytes(normalized_argv)
    receipt: dict[str, object] = {
        "schema": SCHEMA,
        "status": outcome.status,
        "child_exit_code": outcome.child_exit_code,
        "argv": safe_argv,
        "argv_sha256": hashlib.sha256(safe_argv_bytes).hexdigest(),
        "effective_argv_sha256": hashlib.sha256(effective_argv_bytes).hexdigest(),
        "cwd_ref": cwd_ref,
        "timeout_seconds": float(timeout_seconds),
        "termination_grace_seconds": float(termination_grace_seconds),
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "clock_adjustment_seconds": clock_adjustment_seconds,
        "platform": {
            "family": platform_family,
            "mechanism": outcome.mechanism,
        },
        "termination": outcome.termination,
        "log": log_metadata,
        "error": outcome.error,
    }
    _validate_receipt_invariants(receipt)
    _atomic_write_json(result_path, receipt)
    return receipt
