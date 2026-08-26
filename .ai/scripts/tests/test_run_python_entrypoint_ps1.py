#!/usr/bin/env python3
"""Contract tests for the thin Windows PowerShell Python-entrypoint launcher."""

from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / ".ai/scripts/run-python-entrypoint.ps1"


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class PowerShellPythonEntrypointLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.powershell = shutil.which("pwsh") or shutil.which("powershell")
        if cls.powershell is None:
            raise unittest.SkipTest("PowerShell is required for PowerShell launcher contract tests")

    def run_launcher(self, *arguments: str, candidate: str, isolated: bool = False) -> subprocess.CompletedProcess[str]:
        command = (
            "$env:AI_CONTEXT_PYTHON = " + quote(candidate) + "; $env:VIRTUAL_ENV = ''; "
            + ("$env:PATH = ''; " if isolated else "") + "& " + quote(str(LAUNCHER))
            + " " + " ".join(quote(argument) for argument in arguments) + "; exit $LASTEXITCODE"
        )
        return subprocess.run(
            [self.powershell, "-NoProfile", "-Command", command],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_gwt_001_given_explicit_ready_python_when_delegating_then_direct_command_remains_valid(self) -> None:
        result = self.run_launcher(
            ".ai/scripts/validate-dependency-versions.py", "--help", candidate=sys.executable
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_002_given_invalid_explicit_candidate_when_another_ready_candidate_exists_then_launcher_delegates_without_raw_command_failure(self) -> None:
        result = self.run_launcher(
            ".ai/scripts/validate-dependency-versions.py", candidate="definitely-missing-ai-context-python"
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertNotIn("not recognized", result.stderr.lower())

    def test_gwt_003_given_no_ready_python_when_json_requested_then_schema_is_one_stdout_object_and_exit_is_mapped(self) -> None:
        for entrypoint, expected_exit in ((".ai/scripts/validate-dependency-versions.py", 1), (".ai/scripts/plan-ai-context-package-apply.py", 2)):
            with self.subTest(entrypoint=entrypoint):
                result = self.run_launcher(entrypoint, "--diagnostic-format=json", candidate="definitely-missing-ai-context-python", isolated=True)
                self.assertEqual(expected_exit, result.returncode, result.stdout + result.stderr)
                self.assertEqual("", result.stderr)
                lines = result.stdout.splitlines()
                self.assertEqual(1, len(lines))
                payload = __import__("json").loads(lines[0])
                self.assertEqual(entrypoint, payload["entrypoint"])
                self.assertEqual("blocked-by-environment", payload["outcome"])
                self.assertIsNone(payload["selected_executable"])

    def test_gwt_004_given_delegated_cli_returns_two_when_launcher_runs_then_exit_is_propagated(self) -> None:
        result = self.run_launcher(".ai/scripts/validate-dependency-versions.py", "--unknown-option", candidate=sys.executable)
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
