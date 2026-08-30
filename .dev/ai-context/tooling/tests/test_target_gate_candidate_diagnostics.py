#!/usr/bin/env python3
"""GWT coverage for the v0.14 target-validation phase boundary."""

from __future__ import annotations

import importlib.util
import argparse
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNNER_PATH = ROOT / ".dev/ai-context/tooling/validate-target-ai-context.py"
SPEC = importlib.util.spec_from_file_location("target_ai_context_gate", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load target gate: {RUNNER_PATH}")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
class TargetGateCandidateDiagnosticTests(unittest.TestCase):
    def args(self, *, allow_unfinalized: bool) -> argparse.Namespace:
        return argparse.Namespace(
            allow_unfinalized=allow_unfinalized,
            require_effective_rules=False,
            commit_range=None,
            commit=None,
            workflow_id=None,
        )

    def test_gwt_001_pre_finalization_route_avoids_receipt_cycle(self) -> None:
        manifest = RUNNER.load_manifest()
        commands = RUNNER.build_commands(
            manifest, self.args(allow_unfinalized=True), "python"
        )
        self.assertNotIn(
            ".ai/scripts/validate-ai-context-target.py",
            [value for command in commands for value in command],
        )

    def test_gwt_002_final_route_restores_provenance_validation(self) -> None:
        manifest = RUNNER.load_manifest()
        commands = RUNNER.build_commands(
            manifest, self.args(allow_unfinalized=False), "python"
        )
        self.assertIn(
            ".ai/scripts/validate-ai-context-target.py",
            [value for command in commands for value in command],
        )


if __name__ == "__main__":
    unittest.main()
