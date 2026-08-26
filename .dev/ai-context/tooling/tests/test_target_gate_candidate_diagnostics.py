#!/usr/bin/env python3
"""GWT coverage for exact v0.13 unfinalized target diagnostics."""

from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[4]
RUNNER_PATH = ROOT / ".dev/ai-context/tooling/validate-target-ai-context.py"
SPEC = importlib.util.spec_from_file_location("target_ai_context_gate", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load target gate: {RUNNER_PATH}")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
COMMAND = ["python", "-B", ".ai/scripts/validate-ai-context-target.py"]
EXPECTED = ["effective state catalogs[0] is stale"]


class TargetGateCandidateDiagnosticTests(unittest.TestCase):
    @mock.patch.object(RUNNER.subprocess, "run")
    def test_gwt_001_exact_stale_catalog_diagnostic_is_accepted(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess(
            COMMAND,
            1,
            "AI context target validation failed:\n"
            "- effective state catalogs[0] is stale\n",
            "",
        )
        self.assertEqual(0, RUNNER.run_allowing_exact_diagnostics(COMMAND, EXPECTED))

    @mock.patch.object(RUNNER.subprocess, "run")
    def test_gwt_002_additional_receipt_error_fails_closed(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess(
            COMMAND,
            1,
            "AI context target validation failed:\n"
            "- pending receipt required path hash mismatch\n"
            "- effective state catalogs[0] is stale\n",
            "",
        )
        self.assertEqual(1, RUNNER.run_allowing_exact_diagnostics(COMMAND, EXPECTED))

    @mock.patch.object(RUNNER.subprocess, "run")
    def test_gwt_003_unexpected_stderr_fails_closed(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess(
            COMMAND,
            1,
            "AI context target validation failed:\n"
            "- effective state catalogs[0] is stale\n"
            "unexpected output\n",
            "",
        )
        self.assertEqual(1, RUNNER.run_allowing_exact_diagnostics(COMMAND, EXPECTED))


if __name__ == "__main__":
    unittest.main()
