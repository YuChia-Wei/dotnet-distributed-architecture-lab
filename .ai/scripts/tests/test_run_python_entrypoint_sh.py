#!/usr/bin/env python3
"""Contract tests for the thin POSIX Python-entrypoint launcher."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / ".ai/scripts/run-python-entrypoint.sh"


def with_python(candidate: str) -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if key.upper() != "AI_CONTEXT_PYTHON"}
    environment["AI_CONTEXT_PYTHON"] = candidate
    return environment


class PosixPythonEntrypointLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
        cls.bash = str(git_bash) if git_bash.is_file() else shutil.which("bash")
        if cls.bash is None:
            raise unittest.SkipTest("bash is required for POSIX launcher contract tests")
        probe = subprocess.run(
            [cls.bash, "--version"], capture_output=True, text=True, check=False,
            encoding="utf-8", errors="replace",
        )
        if probe.returncode != 0:
            raise unittest.SkipTest("bash is present but unavailable in this runtime")

    def run_launcher(self, *arguments: str, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [self.bash, LAUNCHER.as_posix(), *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_gwt_001_given_explicit_ready_python_when_delegating_then_direct_command_remains_valid(self) -> None:
        environment = with_python(sys.executable)
        result = self.run_launcher(
            ".ai/scripts/validate-dependency-versions.py", "--help", environment=environment
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_002_given_no_candidate_when_launcher_starts_then_it_fails_closed_with_recovery_context(self) -> None:
        environment = {"PATH": "", "AI_CONTEXT_PYTHON": ""}
        result = self.run_launcher(
            ".ai/scripts/validate-dependency-versions.py", environment=environment
        )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("no-ready-python", result.stderr)
        self.assertIn("Python >=3.11", result.stderr)
        self.assertIn("requirements.txt", result.stderr)

    def test_gwt_003_given_invalid_explicit_candidate_when_path_python_is_ready_then_launcher_falls_through(self) -> None:
        environment = with_python("definitely-missing-ai-context-python")
        result = self.run_launcher(
            ".ai/scripts/validate-dependency-versions.py", "--help", environment=environment
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("not found", result.stderr.lower())

    def test_gwt_004_given_no_ready_python_when_json_requested_then_schema_is_one_stdout_object_and_exit_is_mapped(self) -> None:
        for entrypoint, expected_exit in ((".ai/scripts/validate-dependency-versions.py", 1), (".ai/scripts/plan-ai-context-package-apply.py", 2)):
            with self.subTest(entrypoint=entrypoint):
                result = self.run_launcher(entrypoint, "--diagnostic-format=json", environment={"PATH": "", "VIRTUAL_ENV": "", "AI_CONTEXT_PYTHON": ""})
                self.assertEqual(expected_exit, result.returncode, result.stdout + result.stderr)
                self.assertEqual("", result.stderr)
                lines = result.stdout.splitlines()
                self.assertEqual(1, len(lines))
                payload = __import__("json").loads(lines[0])
                self.assertEqual(entrypoint, payload["entrypoint"])
                self.assertEqual("blocked-by-environment", payload["outcome"])

    def test_gwt_005_given_delegated_cli_returns_two_when_launcher_runs_then_exit_is_propagated(self) -> None:
        result = self.run_launcher(".ai/scripts/validate-dependency-versions.py", "--unknown-option", environment=with_python(sys.executable))
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
