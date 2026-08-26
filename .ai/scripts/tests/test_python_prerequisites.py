#!/usr/bin/env python3
"""Given-When-Then tests for the shared Python prerequisite preflight."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / ".ai/scripts/python_prerequisites.py"
SPEC = importlib.util.spec_from_file_location("python_prerequisites", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {MODULE_PATH}")
PREREQUISITES = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PREREQUISITES
SPEC.loader.exec_module(PREREQUISITES)


def completed(command: tuple[str, ...], code: int = 0, stdout: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, code, stdout=stdout, stderr="")


class FakeRunner:
    def __init__(self, states: dict[str, tuple[str, bool]], uv: str | None = None) -> None:
        self.states = states
        self.uv = uv
        self.commands: list[tuple[str, ...]] = []

    def __call__(self, command: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        command = tuple(command)
        self.commands.append(command)
        if command == PREREQUISITES.UV_COMMAND:
            return completed(command, stdout=(self.uv + "\n") if self.uv else "", code=0 if self.uv else 1)
        executable = command[0]
        version, yaml_ready = self.states.get(executable, ("", False))
        if command[1:4] == ("-B", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"):
            return completed(command, stdout=(version + "\n") if version else "", code=0 if version else 1)
        if command[1:4] == ("-B", "-c", "import yaml"):
            return completed(command, code=0 if yaml_ready else 1)
        raise AssertionError(f"Unexpected command: {command}")


class PythonPrerequisiteGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = PREREQUISITES.load_registry()

    def test_gwt_001_given_explicit_ready_python_when_preflight_runs_then_it_wins_and_never_mutates(self) -> None:
        # Given an explicit ready interpreter and lower-priority alternatives.
        runner = FakeRunner({"ready": ("3.13.1", True), "other": ("3.14.0", True)}, uv="other")

        # When the PyYAML-bearing portable entrypoint is preflighted.
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-ai-context.py",
            environment={"AI_CONTEXT_PYTHON": "ready", "PATH": ""},
            registry=self.registry,
            runner=runner,
            which=lambda value: value,
        )

        # Then explicit selection is used once, succeeds, and no installer/network command appears.
        self.assertEqual("ready", result.executable)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(any(command[0] in {"pip", "curl", "wget"} or command[:2] in {("uv", "run"), ("uv", "sync")} for command in runner.commands))

    def test_gwt_002_given_old_python_when_preflight_runs_then_json_is_single_blocked_document(self) -> None:
        # Given Python below the 3.11 floor.
        runner = FakeRunner({"old": ("3.10.9", True)})
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-ai-context.py",
            environment={"AI_CONTEXT_PYTHON": "old", "PATH": ""}, registry=self.registry,
            runner=runner, which=lambda value: "old" if value == "old" else None,
        )

        # When JSON diagnostic output is selected, then it contains the stable no-mutation contract.
        self.assertEqual(1, result.exit_code)
        self.assertEqual("unsupported-python", result.diagnostic["reason_code"])
        self.assertFalse(result.diagnostic["mutation_started"])
        rendered = json.dumps(result.diagnostic, separators=(",", ":"))
        self.assertEqual("blocked-by-environment", json.loads(rendered)["outcome"])

    def test_gwt_003_given_missing_yaml_when_profile_requires_it_then_preflight_blocks_before_delegation(self) -> None:
        # Given a supported interpreter whose PyYAML import fails.
        runner = FakeRunner({"missing": ("3.13.1", False)})
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-workflow-artifacts.py",
            environment={"AI_CONTEXT_PYTHON": "missing", "PATH": ""}, registry=self.registry,
            runner=runner, which=lambda value: "missing" if value == "missing" else None,
        )

        # When preflight runs, then it reports the exact governed requirement and does not invoke a target CLI.
        self.assertEqual("missing-dependency", result.diagnostic["reason_code"])
        self.assertEqual(["PyYAML==6.0.3"], result.diagnostic["missing_requirements"])
        self.assertFalse(result.diagnostic["mutation_started"])
        self.assertFalse(any(command[0].endswith("validate-workflow-artifacts.py") for command in runner.commands))

    def test_gwt_004_given_standard_library_entrypoint_when_yaml_is_missing_then_ready_python_delegation_is_allowed(self) -> None:
        # Given Python is ready but PyYAML is not installed.
        runner = FakeRunner({"ready": ("3.13.1", False)})

        # When the declared standard-library-only portable CLI is checked.
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-dependency-versions.py",
            environment={"AI_CONTEXT_PYTHON": "ready", "PATH": ""}, registry=self.registry,
            runner=runner, which=lambda value: "ready" if value == "ready" else None,
        )

        # Then PyYAML is not a false prerequisite.
        self.assertEqual("ready", result.executable)
        self.assertEqual(0, result.exit_code)
        self.assertFalse(any(command[1:4] == ("-B", "-c", "import yaml") for command in runner.commands))

    def test_gwt_005_given_duplicate_path_and_uv_identity_when_discovered_then_it_is_probed_once(self) -> None:
        # Given PATH and uv both resolve to one physical executable.
        runner = FakeRunner({"same": ("3.13.1", True)}, uv="same")
        candidates = PREREQUISITES.discover_candidates(
            {"PATH": ""}, path_value="", which=lambda value: "same" if value in {"python", "python3", "same"} else None, runner=runner,
        )

        # When candidates are discovered, then duplicate identities are bounded and deduplicated.
        self.assertEqual(["same"], [candidate.executable for candidate in candidates])

    def test_gwt_006_given_registry_when_checked_then_all_profiles_and_portable_boundary_are_complete(self) -> None:
        # Given the canonical entrypoint registry.
        entries = self.registry["entrypoints"]

        # When its approved boundary is counted, then it retains 31 entries, 13 portable entries and two no-PyYAML profiles.
        self.assertEqual(31, len(entries))
        self.assertEqual(13, sum(entry["portable"] for entry in entries))
        self.assertEqual(2, sum(not entry["dependency_profile"] for entry in entries))
        self.assertEqual({1, 2, 3}, {entry["prerequisite_exit_code"] for entry in entries})
        self.assertEqual(
            {".ai/scripts/ai_context_release_closeout.py"},
            {
                entry["path"]
                for entry in entries
                if entry["prerequisite_exit_code"] == 3
            },
        )

    def test_gwt_007_given_invalid_explicit_override_when_a_path_candidate_is_ready_then_discovery_falls_through_once(self) -> None:
        # Given the owner override cannot launch but a lower-priority candidate is ready.
        runner = FakeRunner({"invalid": ("", False), "ready": ("3.13.1", True)})
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-ai-context.py",
            environment={"AI_CONTEXT_PYTHON": "invalid", "PATH": ""}, registry=self.registry,
            runner=runner, which=lambda value: "ready" if value in {"python", "python3", "ready"} else None,
        )

        # When selection validates candidates in order, then it skips the unusable override and reaches the ready candidate.
        self.assertEqual("ready", result.executable)
        self.assertEqual(0, result.exit_code)

    def test_gwt_008_given_direct_entrypoint_when_current_python_lacks_yaml_then_guard_removes_json_switch_and_exits_once(self) -> None:
        # Given the already-running interpreter is supported but lacks the required dependency.
        imported: list[str] = []

        def missing_dependency(name: str) -> object:
            imported.append(name)
            raise ImportError(name)

        blocked = PREREQUISITES.preflight_current(
            ".ai/scripts/validate-ai-context.py",
            registry=self.registry,
            importer=missing_dependency,
            version_info=(3, 13, 1),
        )
        original = PREREQUISITES.preflight_current
        try:
            PREREQUISITES.preflight_current = lambda entrypoint: blocked  # type: ignore[assignment]
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exited:
                    PREREQUISITES.guard_direct_entrypoint(
                        ".ai/scripts/validate-ai-context.py",
                        ["--diagnostic-format", "json", "--help"],
                    )
            # Then only the JSON projection is emitted with the mapped code and no alternate discovery occurred.
            self.assertEqual(1, exited.exception.code)
            self.assertEqual("", stderr.getvalue())
            self.assertEqual("missing-dependency", json.loads(stdout.getvalue())["reason_code"])
            self.assertEqual(["yaml"], imported)
        finally:
            PREREQUISITES.preflight_current = original

    def test_gwt_009_given_old_and_missing_dependency_candidates_when_none_is_ready_then_missing_dependency_wins(self) -> None:
        # Given a launchable old override followed by a supported interpreter without PyYAML.
        runner = FakeRunner({"old": ("3.10.9", True), "missing": ("3.13.1", False)})
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-ai-context.py", environment={"AI_CONTEXT_PYTHON": "old", "PATH": ""},
            registry=self.registry, runner=runner,
            which=lambda value: "missing" if value in {"python", "python3", "missing"} else None,
        )

        # When no candidate is ready, then the stable external reason selects missing dependency, not probe internals or last candidate.
        self.assertEqual("missing-dependency", result.diagnostic["reason_code"])
        self.assertEqual("missing", result.diagnostic["selected_executable"])

    def test_gwt_010_given_supplied_empty_path_when_discovered_then_parent_path_is_not_consulted(self) -> None:
        # Given a supplied empty PATH and no override.
        runner = FakeRunner({})
        candidates = PREREQUISITES.discover_candidates({"PATH": ""}, path_value="", runner=runner, include_uv=False)

        # When discovery runs, then no parent-process Python command leaks into the supplied environment.
        self.assertEqual([], candidates)

    def test_gwt_011_given_old_current_interpreter_when_direct_preflight_runs_then_it_never_imports_dependencies(self) -> None:
        # Given the already-running process is below the supported Python floor.
        imported: list[str] = []
        result = PREREQUISITES.preflight_current(
            ".ai/scripts/validate-ai-context.py",
            registry=self.registry,
            importer=lambda name: imported.append(name),
            version_info=(3, 10, 9),
        )

        # When direct preflight reports the failure, then no alternate runtime or dependency probe runs.
        self.assertEqual("unsupported-python", result.diagnostic["reason_code"])
        self.assertEqual([], imported)

    def test_gwt_012_given_active_environment_when_no_explicit_override_then_it_precedes_generic_path(self) -> None:
        # Given an active environment and a separately ready generic Python.
        active = str(Path("active") / ("Scripts/python.exe" if PREREQUISITES.os.name == "nt" else "bin/python"))
        runner = FakeRunner({active: ("3.13.1", True), "generic": ("3.14.0", True)})
        result = PREREQUISITES.preflight(
            ".ai/scripts/validate-ai-context.py", environment={"VIRTUAL_ENV": "active", "PATH": ""},
            registry=self.registry, runner=runner,
            which=lambda value: active if value == active else ("generic" if value in {"python", "python3"} else None),
        )

        # When discovery runs, then the active environment wins before generic PATH commands.
        self.assertEqual(active, result.executable)

    def test_gwt_013_given_every_registered_entrypoint_when_an_old_python_is_selected_then_each_blocks_without_target_execution(self) -> None:
        runner = FakeRunner({"old": ("3.10.9", True)})
        for entry in self.registry["entrypoints"]:
            with self.subTest(entrypoint=entry["path"]):
                result = PREREQUISITES.preflight(entry["path"], environment={"AI_CONTEXT_PYTHON": "old", "PATH": ""}, registry=self.registry, runner=runner, which=lambda value: "old" if value == "old" else None)
                self.assertEqual(entry["prerequisite_exit_code"], result.exit_code)
                self.assertEqual(entry["path"], result.diagnostic["entrypoint"])
                self.assertEqual("unsupported-python", result.diagnostic["reason_code"])
                self.assertFalse(result.diagnostic["mutation_started"])

    def test_gwt_014_given_direct_portable_cli_and_shadowed_yaml_when_json_requested_then_it_blocks_without_repo_bytecode(self) -> None:
        before = list(ROOT.rglob("__pycache__")) + list(ROOT.rglob("*.pyc"))
        fixture_parent = ROOT / ".ai/scripts/tests/.python-prerequisite-fixtures"
        fixture_parent.mkdir(exist_ok=True)
        shadow = Path(tempfile.mkdtemp(prefix="shadow-", dir=fixture_parent))
        try:
            try:
                (shadow / "yaml.py").write_text("raise ImportError('shadowed PyYAML')\n", encoding="utf-8")
            except PermissionError as error:
                raise unittest.SkipTest(f"workspace fixture ACL blocks direct subprocess smoke: {error}") from error
            environment = dict(os.environ)
            environment.update({"PYTHONPATH": str(shadow), "PYTHONDONTWRITEBYTECODE": "1"})
            result = subprocess.run([sys.executable, "-B", str(ROOT / ".ai/scripts/validate-ai-context.py"), "--diagnostic-format=json"], cwd=ROOT, env=environment, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        finally:
            shutil.rmtree(shadow, ignore_errors=True)
            try:
                fixture_parent.rmdir()
            except OSError:
                pass
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("missing-dependency", payload["reason_code"])
        self.assertFalse(payload["mutation_started"])
        self.assertEqual(before, list(ROOT.rglob("__pycache__")) + list(ROOT.rglob("*.pyc")))


if __name__ == "__main__":
    unittest.main()
