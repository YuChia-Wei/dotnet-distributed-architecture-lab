#!/usr/bin/env python3
"""Shared, read-only Python prerequisite preflight for supported entrypoints."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
REGISTRY_PATH = ROOT / ".ai/scripts/python-entrypoints.json"
UV_COMMAND = ("uv", "python", "find", "--managed-python", "--no-python-downloads", "--offline", "--no-config", "--no-project", ">=3.11")
Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class Candidate:
    executable: str
    source: str


@dataclass(frozen=True)
class PreflightResult:
    executable: str | None
    version: str | None
    diagnostic: dict[str, object] | None
    exit_code: int


def _run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def entrypoint_contract(entrypoint: str, registry: Mapping[str, object]) -> dict[str, object]:
    normalized = entrypoint.replace("\\", "/")
    for record in registry["entrypoints"]:  # type: ignore[index]
        if record["path"] == normalized:
            return dict(record)
    raise ValueError(f"Unsupported Python entrypoint: {normalized}")


def _path_candidates(path_value: str) -> list[str]:
    names = ("python", "python3")
    found = list(names)
    pattern = re.compile(r"^(?:python(?:3(?:\.\d+)?)?|python\d{2,3})(?:\.exe)?$", re.IGNORECASE)
    for directory in path_value.split(os.pathsep):
        if not directory:
            continue
        try:
            for child in sorted(Path(directory).iterdir(), key=lambda item: item.name.casefold()):
                if child.is_file() and pattern.fullmatch(child.name):
                    found.append(str(child))
        except OSError:
            continue
    return found


def _uv_candidate(runner: Runner) -> Candidate | None:
    try:
        uv = runner(UV_COMMAND)
        if uv.returncode == 0 and uv.stdout.strip():
            return Candidate(uv.stdout.strip().splitlines()[0], "uv-managed")
    except OSError:
        pass
    return None


def discover_candidates(environment: Mapping[str, str] | None = None, *, path_value: str | None = None, which: Callable[[str], str | None] = shutil.which, runner: Runner = _run, include_uv: bool = True) -> list[Candidate]:
    """Discover candidates once in approved precedence order, without mutation."""
    env = os.environ if environment is None else environment
    candidates: list[Candidate] = []
    explicit = env.get("AI_CONTEXT_PYTHON")
    if explicit:
        candidates.append(Candidate(explicit, "AI_CONTEXT_PYTHON"))
    active = env.get("VIRTUAL_ENV")
    if active:
        candidates.append(Candidate(str(Path(active) / ("Scripts/python.exe" if os.name == "nt" else "bin/python")), "active-environment"))
    effective_path = path_value if path_value is not None else env.get("PATH", "")
    resolver = (lambda name: shutil.which(name, path=effective_path)) if which is shutil.which else which
    for name in _path_candidates(effective_path):
        resolved = resolver(name)
        if resolved:
            candidates.append(Candidate(resolved, "PATH" if name in {"python", "python3"} else "versioned-PATH"))
    if include_uv:
        uv = _uv_candidate(runner)
        if uv:
            candidates.append(uv)
    deduped: list[Candidate] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = resolver(candidate.executable) or candidate.executable
        try:
            identity = str(Path(resolved).resolve()).casefold() if os.name == "nt" else str(Path(resolved).resolve())
        except OSError:
            identity = resolved
        if identity not in seen:
            seen.add(identity)
            deduped.append(Candidate(resolved, candidate.source))
    return deduped


def _probe(candidate: Candidate, dependencies: Sequence[str], runner: Runner) -> tuple[str | None, str | None]:
    version = runner((candidate.executable, "-B", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"))
    if version.returncode != 0:
        return None, "unlaunchable"
    value = version.stdout.strip()
    parts = tuple(int(item) for item in value.split(".")[:2] if item.isdigit())
    if len(parts) != 2 or parts < (3, 11):
        return value or None, "unsupported-python"
    for dependency in dependencies:
        import_name = "yaml" if dependency == "PyYAML" else dependency
        probe = runner((candidate.executable, "-B", "-c", f"import {import_name}"))
        if probe.returncode != 0:
            return value, "missing-dependency"
    return value, None


def _diagnostic(contract: Mapping[str, object], registry: Mapping[str, object], *, reason: str, candidates: list[dict[str, str]], selected: Candidate | None = None, version: str | None = None) -> dict[str, object]:
    dependencies = list(contract["dependency_profile"])
    requirements = registry["governed_requirements"]  # type: ignore[index]
    missing = []
    if reason == "missing-dependency":
        missing = [f"{name}=={requirements[name]['version']}" for name in dependencies]  # type: ignore[index]
    source_requirements = ROOT / "requirements.txt"
    envelope_requirements = ROOT.parent / "requirements.txt"
    governed_requirements = (
        source_requirements
        if source_requirements.is_file() or not envelope_requirements.is_file()
        else envelope_requirements
    )
    requirements_path = str(governed_requirements.resolve())
    recovery = None
    if selected and missing:
        recovery = f'"{selected.executable}" -m pip install -r "{requirements_path}"'
    return {
        "schema_version": "1.0", "outcome": "blocked-by-environment", "reason_code": reason,
        "entrypoint": contract["path"], "required_python": ">=3.11", "candidates": candidates[:8],
        "selected_executable": selected.executable if selected else None,
        "selected_version": version, "missing_requirements": missing,
        "requirements_path": requirements_path, "recovery_command": recovery,
        "mutation_started": False,
    }


def preflight(entrypoint: str, *, environment: Mapping[str, str] | None = None, registry: Mapping[str, object] | None = None, runner: Runner = _run, which: Callable[[str], str | None] = shutil.which) -> PreflightResult:
    registry = load_registry() if registry is None else registry
    contract = entrypoint_contract(entrypoint, registry)
    dependencies = list(contract["dependency_profile"])
    observed: list[dict[str, str]] = []
    missing: tuple[Candidate, str | None] | None = None
    old: tuple[Candidate, str | None] | None = None
    def inspect(candidate: Candidate) -> PreflightResult | None:
        nonlocal missing, old
        version, reason = _probe(candidate, dependencies, runner)
        observed.append({"executable": candidate.executable, "source": candidate.source, "status": reason or "ready", **({"version": version} if version else {})})
        if reason is None:
            return PreflightResult(candidate.executable, version, None, 0)
        if reason == "missing-dependency" and missing is None:
            missing = (candidate, version)
        elif reason == "unsupported-python" and old is None:
            old = (candidate, version)
        return None

    for candidate in discover_candidates(environment, which=which, runner=runner, include_uv=False):
        ready = inspect(candidate)
        if ready:
            return ready
    uv = _uv_candidate(runner)
    if uv:
        ready = inspect(uv)
        if ready:
            return ready
    if missing:
        reason, (selected, selected_version) = "missing-dependency", missing
    elif old:
        reason, (selected, selected_version) = "unsupported-python", old
    else:
        reason, selected, selected_version = "no-ready-python", None, None
    diagnostic = _diagnostic(contract, registry, reason=reason, candidates=observed, selected=selected, version=selected_version)
    return PreflightResult(None, None, diagnostic, int(contract["prerequisite_exit_code"]))


def _probe_current(
    dependencies: Sequence[str],
    *,
    importer: Callable[[str], object] = importlib.import_module,
    version_info: Sequence[int] | None = None,
) -> tuple[str | None, str | None]:
    """Inspect the already-running interpreter without launching an alternate process."""
    observed_version = sys.version_info[:3] if version_info is None else version_info[:3]
    parts = tuple(int(item) for item in observed_version)
    value = ".".join(str(item) for item in parts)
    if len(parts) < 2 or parts[:2] < (3, 11):
        return value or None, "unsupported-python"
    for dependency in dependencies:
        import_name = "yaml" if dependency == "PyYAML" else dependency
        try:
            importer(import_name)
        except Exception:
            return value, "missing-dependency"
    return value, None


def preflight_current(
    entrypoint: str,
    *,
    registry: Mapping[str, object] | None = None,
    importer: Callable[[str], object] = importlib.import_module,
    version_info: Sequence[int] | None = None,
) -> PreflightResult:
    """Check only this process's interpreter; direct callers must not switch runtime."""
    registry = load_registry() if registry is None else registry
    contract = entrypoint_contract(entrypoint, registry)
    candidate = Candidate(sys.executable, "current-process")
    version, reason = _probe_current(
        list(contract["dependency_profile"]),
        importer=importer,
        version_info=version_info,
    )
    if reason is None:
        return PreflightResult(candidate.executable, version, None, 0)
    observed = [{"executable": candidate.executable, "source": candidate.source, "status": reason, **({"version": version} if version else {})}]
    diagnostic = _diagnostic(contract, registry, reason=reason, candidates=observed, selected=candidate if version else None, version=version)
    return PreflightResult(None, version, diagnostic, int(contract["prerequisite_exit_code"]))


def consume_diagnostic_format(argv: Sequence[str]) -> tuple[list[str], str]:
    """Remove the shared format switch before an entrypoint's own argparse runs."""
    remaining: list[str] = []
    diagnostic_format = "human"
    index = 0
    while index < len(argv):
        value = argv[index]
        if value == "--diagnostic-format=json":
            diagnostic_format = "json"
        elif value == "--diagnostic-format" and index + 1 < len(argv) and argv[index + 1] == "json":
            diagnostic_format = "json"
            index += 1
        else:
            remaining.append(value)
        index += 1
    return remaining, diagnostic_format


def guard_direct_entrypoint(entrypoint: str, argv: Sequence[str] | None = None) -> list[str]:
    """Remove the common format switch and exit before local/domain imports if blocked."""
    sys.dont_write_bytecode = True
    remaining, diagnostic_format = consume_diagnostic_format(sys.argv[1:] if argv is None else argv)
    result = preflight_current(entrypoint)
    if result.exit_code:
        raise SystemExit(emit(result, diagnostic_format))
    if argv is None:
        sys.argv[:] = [sys.argv[0], *remaining]
    return remaining


def emit(result: PreflightResult, diagnostic_format: str) -> int:
    if result.diagnostic is None:
        return 0
    if diagnostic_format == "json":
        print(json.dumps(result.diagnostic, sort_keys=True, separators=(",", ":")))
    else:
        detail = result.diagnostic["reason_code"]
        selected = result.diagnostic.get("selected_executable")
        version = result.diagnostic.get("selected_version")
        missing = ", ".join(result.diagnostic["missing_requirements"]) or "none"
        recovery = result.diagnostic.get("recovery_command") or "install Python >=3.11, then retry"
        print(f"Python prerequisite blocked for {result.diagnostic['entrypoint']}: {detail}; selected={selected or 'none'} version={version or 'unknown'}; missing={missing}; requirements={result.diagnostic['requirements_path']}; recovery: {recovery}", file=sys.stderr)
    return result.exit_code


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrypoint", required=True)
    parser.add_argument("--diagnostic-format", choices=("human", "json"), default="human")
    parser.add_argument("--delegate", action="store_true")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    arguments = parser.parse_args(argv)
    result = preflight(arguments.entrypoint)
    exit_code = emit(result, arguments.diagnostic_format)
    if exit_code or not arguments.delegate:
        return exit_code
    target = ROOT / arguments.entrypoint
    forwarded = arguments.args[1:] if arguments.args[:1] == ["--"] else arguments.args
    return subprocess.run((result.executable, str(target), *forwarded), check=False).returncode  # type: ignore[arg-type]


if __name__ == "__main__":
    raise SystemExit(main())
