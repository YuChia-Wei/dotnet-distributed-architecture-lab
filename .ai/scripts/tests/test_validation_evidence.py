#!/usr/bin/env python3
"""GWT tests for deterministic, privacy-preserving validation evidence."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HELPER = ROOT / ".ai/scripts/validation-evidence.py"


class ValidationEvidenceGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="validation-evidence-")
        self.repo = Path(self.temporary.name) / "repo"
        self.repo.mkdir()
        self.inputs = self.repo / "inputs"
        self.inputs.mkdir()
        (self.inputs / "rule.md").write_text("governed bytes\n", encoding="utf-8")
        self.logs = self.repo / "artifacts/validation/run"
        self.logs.mkdir(parents=True)
        self.log = self.logs / "check.log"
        self.log.write_text("private-token=must-not-appear\n", encoding="utf-8")
        self.cache = self.repo / "artifacts/validation/evidence-cache.json"
        self.evidence = self.logs / "evidence.jsonl"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def helper(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HELPER), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )

    def lookup(self, *, version: str = "validator-v1", profile: str = "fast", environment: str = "windows-native") -> tuple[str, bool]:
        result = self.helper(
            "lookup",
            "--repo", str(self.repo),
            "--cache", str(self.cache),
            "--validator-id", "fixture-check",
            "--validator-version", version,
            "--profile", profile,
            "--environment-class", environment,
            "--input-paths", "inputs",
            "--cache-policy", "reuse-by-input",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        fingerprint, reusable, _ = result.stdout.rstrip("\r\n").split("\t")
        return fingerprint, reusable == "true"

    def record(
        self,
        fingerprint: str,
        *,
        outcome: str = "passed",
        disposition: str = "executed",
        started_ms: int = 1000,
        completed_ms: int = 1010,
    ) -> None:
        result = self.helper(
            "record",
            "--repo", str(self.repo),
            "--cache", str(self.cache),
            "--evidence", str(self.evidence),
            "--invocation-id", "fixture-invocation",
            "--validator-id", "fixture-check",
            "--validator-version", "validator-v1",
            "--profile", "fast",
            "--environment-class", "windows-native",
            "--input-fingerprint", fingerprint,
            "--outcome", outcome,
            "--disposition", disposition,
            "--started-ms", str(started_ms),
            "--completed-ms", str(completed_ms),
            "--duration-ms", str(completed_ms - started_ms),
            "--suppressed-output-bytes", "30",
            "--subprocess-count", "1",
            "--log-path", str(self.log),
            "--selection-reason", "fixture",
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_gwt_001_given_executed_eligible_evidence_when_same_identity_is_checked_then_reuse_is_reported_separately(self) -> None:
        fingerprint, reusable = self.lookup()
        self.assertFalse(reusable)
        self.record(fingerprint)

        same_fingerprint, reusable = self.lookup()

        self.assertEqual(fingerprint, same_fingerprint)
        self.assertTrue(reusable)
        record = json.loads(self.evidence.read_text(encoding="utf-8"))
        self.assertEqual("passed", record["outcome"])
        self.assertEqual("executed", record["execution_disposition"])
        self.assertEqual(30, record["suppressed_output_bytes"])

    def test_gwt_002_given_changed_input_or_incompatible_identity_when_checked_then_reuse_is_invalidated(self) -> None:
        fingerprint, _ = self.lookup()
        self.record(fingerprint)
        (self.inputs / "rule.md").write_text("changed bytes\n", encoding="utf-8")

        changed_fingerprint, changed_reusable = self.lookup()
        _, version_reusable = self.lookup(version="validator-v2")
        _, profile_reusable = self.lookup(profile="pr")
        _, environment_reusable = self.lookup(environment="ubuntu-hosted")

        self.assertNotEqual(fingerprint, changed_fingerprint)
        self.assertFalse(changed_reusable)
        self.assertFalse(version_reusable)
        self.assertFalse(profile_reusable)
        self.assertFalse(environment_reusable)

    def test_gwt_003_given_retained_output_when_recorded_then_evidence_contains_counts_not_output_or_host_identity(self) -> None:
        fingerprint, _ = self.lookup()
        self.record(fingerprint)

        serialized = self.evidence.read_text(encoding="utf-8")

        self.assertNotIn("private-token", serialized)
        self.assertNotIn(str(self.temporary.name), serialized)
        record = json.loads(serialized)
        self.assertEqual("artifacts/validation/run/check.log", record["log_ref"])
        self.assertEqual(len(self.log.read_bytes()), record["output_bytes"])
        self.assertEqual(1, record["output_lines"])

    def test_gwt_004_given_profile_selection_dispositions_when_serialized_then_timeout_cancellation_and_nonselection_remain_distinct(self) -> None:
        fingerprint, _ = self.lookup()
        expectations = (
            ("executed", "passed"),
            ("reused", "passed"),
            ("not-selected", "not-applicable"),
            ("timed-out", "failed"),
            ("cancelled", "failed"),
        )
        for offset, (disposition, outcome) in enumerate(expectations):
            self.record(
                fingerprint,
                disposition=disposition,
                outcome=outcome,
                started_ms=1000 + offset * 20,
                completed_ms=1010 + offset * 20,
            )

        summary_path = self.logs / "summary.json"
        result = self.helper(
            "summarize",
            "--evidence", str(self.evidence),
            "--output", str(summary_path),
            "--invocation-id", "fixture-invocation",
            "--profile", "fast",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        records = [
            json.loads(line)
            for line in self.evidence.read_text(encoding="utf-8").splitlines()
        ]

        self.assertEqual(
            set(expectations),
            {(record["execution_disposition"], record["outcome"]) for record in records},
        )
        self.assertEqual(1, summary["dispositions"]["timed-out"])
        self.assertEqual(1, summary["dispositions"]["cancelled"])
        self.assertEqual(1, summary["dispositions"]["not-selected"])

    def test_gwt_005_given_tracked_input_when_unmodified_then_git_content_identity_is_reused_but_dirty_content_invalidates_it(self) -> None:
        for arguments in (
            ("git", "init"),
            ("git", "config", "user.email", "validator@example.test"),
            ("git", "config", "user.name", "Validator Fixture"),
            ("git", "add", "inputs/rule.md"),
            ("git", "commit", "-m", "fixture"),
        ):
            result = subprocess.run(arguments, cwd=self.repo, check=False, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)

        fingerprint, reusable = self.lookup()
        self.assertFalse(reusable)
        self.record(fingerprint)
        same_fingerprint, reusable = self.lookup()
        (self.inputs / "rule.md").write_text("dirty content\n", encoding="utf-8")
        dirty_fingerprint, dirty_reusable = self.lookup()

        self.assertEqual(fingerprint, same_fingerprint)
        self.assertTrue(reusable)
        self.assertNotEqual(fingerprint, dirty_fingerprint)
        self.assertFalse(dirty_reusable)


if __name__ == "__main__":
    unittest.main()
