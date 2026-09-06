"""Target-owned terminal audit negatives; isolated Git fixtures, no product tests."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "validate-target-terminal-audit.py"
SPEC = importlib.util.spec_from_file_location("target_terminal_audit", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
WORKFLOW = ".dev/workflows/2026-09-07-test/workflow.yaml"
RECEIPT = ".dev/workflows/2026-09-07-test/evidence/current.json"
HISTORY = ".dev/workflows/2026-09-07-test/evidence/original.yaml"
CRITERIA = ".dev/workflows/2026-09-07-test/criteria.md"
REPORT = ".dev/assessments/ASM-20260907-001/report.md"
INVOCATION = ".dev/assessments/ASM-20260907-001/evidence/invocation.json"


class TargetTerminalAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="target-terminal-audit-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Terminal audit fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.run_git("config", "core.autocrlf", "false")
        self.run_git("config", "commit.gpgsign", "false")
        self.write(".gitignore", "outcome/\n")
        self.write(GATE.ROLE_PATH, "fixture role contract\n")
        self.write(CRITERIA, "Review the exact full tree and pinned authority.\n")
        self.write(HISTORY, "status: pending\n")
        self.contract = {
            "schema_version": "1.0", "required": True,
            "historical_record": {**self.reference(HISTORY), "disposition": "superseded-incomplete"},
            "current_record": RECEIPT,
        }
        self.locator = {"status": "in_progress", "terminal_audit": self.contract}
        self.write_locator()
        self.write_json(RECEIPT, {"schema_version": "1.0", "status": "pending"})
        self.commit("subject fixture")
        self.subject = self.run_git("rev-parse", "HEAD")
        self.tree = self.run_git("rev-parse", "HEAD^{tree}")
        self.write(REPORT, "Independent fixture audit: passed.\n")
        self.invocation = {
            "status": "passed", "subject_commit": self.subject, "subject_tree": self.tree,
            "reviewer_id": "independent-child", "invocation_id": "runtime-invocation-1",
            "role_path": GATE.ROLE_PATH, "started_at": "2026-09-07T01:00:00+08:00",
            "completed_at": "2026-09-07T01:01:00+08:00", "evidence_refs": [REPORT],
        }
        self.write_json(INVOCATION, self.invocation)
        self.receipt = {
            "schema_version": "1.0", **{key: value for key, value in self.invocation.items() if key != "evidence_refs"},
            "criteria": self.reference(CRITERIA), "report": self.reference(REPORT),
            "invocation_evidence": self.reference(INVOCATION),
            "authority_hashes": {GATE.ROLE_PATH: self.reference(GATE.ROLE_PATH)["sha256"]},
        }
        self.run_git("add", "--", REPORT, INVOCATION)

    def run_git(self, *args: str) -> str:
        result = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def write(self, path: str, data: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding="utf-8", newline="\n")

    def write_json(self, path: str, data: object) -> None:
        self.write(path, json.dumps(data, indent=2) + "\n")

    def write_locator(self) -> None:
        self.write(WORKFLOW, yaml.safe_dump(self.locator, sort_keys=False))

    def reference(self, path: str) -> dict[str, str]:
        return {"path": path, "sha256": GATE.digest((self.root / path).read_bytes())}

    def commit(self, message: str) -> None:
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=", "commit", "--no-verify", "-qm", message)

    def validate(self) -> dict:
        return GATE.validate_receipt(self.root, self.receipt)

    def prepare_admission(self) -> Path:
        self.commit("persist reviewed outcome")
        # For a new final audit the full current tree, rather than an ancestor
        # or evidence-filtered projection, is the newly selected subject.
        current = self.run_git("rev-parse", "HEAD")
        tree = self.run_git("rev-parse", "HEAD^{tree}")
        result = copy.deepcopy(self.receipt)
        result.update(subject_commit=current, subject_tree=tree)
        invocation = {**self.invocation, "subject_commit": current, "subject_tree": tree}
        self.write_json("outcome/invocation.json", invocation)
        result["invocation_evidence"] = self.reference("outcome/invocation.json")
        self.write_json("outcome/receipt.json", result)
        return self.root / "outcome/receipt.json"

    def test_retained_audit_does_not_claim_current_head(self) -> None:
        self.write_json(RECEIPT, self.receipt)
        self.locator["status"] = "completed"
        self.write_locator()
        self.commit("persist terminal outcome after reviewed subject")
        self.assertNotEqual(self.subject, self.run_git("rev-parse", "HEAD"))
        self.assertIn("not current-HEAD admission", GATE.validate_workflow(self.root, WORKFLOW))

    def test_pending_is_disclosed_only_while_in_progress(self) -> None:
        self.assertIn("pending", GATE.validate_workflow(self.root, WORKFLOW))
        self.locator["status"] = "completed"
        self.write_locator()
        with self.assertRaisesRegex(ValueError, "only for an in_progress"):
            GATE.validate_workflow(self.root, WORKFLOW)

    def test_failed_and_missing_report_are_rejected(self) -> None:
        self.receipt["status"] = "failed"
        with self.assertRaisesRegex(ValueError, "status passed"):
            self.validate()
        self.receipt["status"] = "passed"
        self.receipt["report"]["path"] = "missing.md"
        with self.assertRaises(OSError):
            self.validate()

    def test_empty_or_missing_identity_and_invocation_are_rejected(self) -> None:
        for key in ("reviewer_id", "invocation_id"):
            with self.subTest(key=key):
                changed = {**self.receipt, key: " "}
                with self.assertRaisesRegex(ValueError, "non-empty"):
                    GATE.validate_receipt(self.root, changed)
        del self.receipt["invocation_evidence"]
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.validate()

    def test_subject_tree_and_nonexistent_commit_are_rejected(self) -> None:
        self.receipt["subject_tree"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.validate()
        self.receipt["subject_commit"] = "1" * 40
        with self.assertRaisesRegex(ValueError, "Git verification"):
            self.validate()

    def test_raw_report_and_invocation_hash_drift_are_rejected(self) -> None:
        for key in ("report", "invocation_evidence"):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.receipt)
                changed[key]["sha256"] = "0" * 64
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    GATE.validate_receipt(self.root, changed)

    def test_authority_drift_cannot_be_hidden_by_repinning_current_bytes(self) -> None:
        self.write(GATE.ROLE_PATH, "modified authority\n")
        with self.assertRaisesRegex(ValueError, "authority hash mismatch"):
            self.validate()
        self.receipt["authority_hashes"][GATE.ROLE_PATH] = self.reference(GATE.ROLE_PATH)["sha256"]
        with self.assertRaisesRegex(ValueError, "reviewed subject evidence"):
            self.validate()

    def test_criteria_must_preexist_in_reviewed_subject(self) -> None:
        self.write(CRITERIA, "changed criteria\n")
        self.receipt["criteria"] = self.reference(CRITERIA)
        with self.assertRaisesRegex(ValueError, "reviewed subject evidence"):
            self.validate()

    def test_invocation_shared_fields_and_report_reference_are_bound(self) -> None:
        self.invocation["invocation_id"] = "different-invocation"
        self.write_json(INVOCATION, self.invocation)
        self.receipt["invocation_evidence"] = self.reference(INVOCATION)
        with self.assertRaisesRegex(ValueError, "does not match receipt"):
            self.validate()
        self.invocation["invocation_id"] = self.receipt["invocation_id"]
        self.invocation["evidence_refs"] = [CRITERIA]
        self.write_json(INVOCATION, self.invocation)
        self.receipt["invocation_evidence"] = self.reference(INVOCATION)
        with self.assertRaisesRegex(ValueError, "include the pinned report"):
            self.validate()

    def test_history_cannot_be_replaced_or_silently_rewritten(self) -> None:
        self.write(HISTORY, "status: passed\n")
        with self.assertRaisesRegex(ValueError, "historical_record hash mismatch"):
            GATE.validate_workflow(self.root, WORKFLOW)

    def test_unsafe_and_untracked_paths_are_rejected(self) -> None:
        for path in ("../escape", "/absolute", "C:/absolute", "foo\\bar", ".git/config", "foo/../bar", "foo./bar"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unsafe"):
                GATE.safe_file(self.root, path, tracked=False)
        self.write("untracked.md", "evidence\n")
        with self.assertRaisesRegex(ValueError, "Git verification"):
            GATE.safe_file(self.root, "untracked.md", tracked=True)

    def test_reparse_point_is_rejected(self) -> None:
        info = SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
        with mock.patch.object(Path, "lstat", return_value=info):
            with self.assertRaisesRegex(ValueError, "reparse-point"):
                GATE.no_links(self.root / REPORT)

    def test_admission_accepts_same_full_tree_after_sha_only_commit(self) -> None:
        receipt = self.prepare_admission()
        self.run_git("-c", "core.hooksPath=", "commit", "--no-verify", "--allow-empty", "-qm", "history only")
        self.assertIn("identical full tree", GATE.admit(self.root, receipt))

    def test_admission_rejects_changed_full_tree_even_for_evidence(self) -> None:
        receipt = self.prepare_admission()
        self.write("new-evidence.md", "evidence-only is still content\n")
        self.run_git("add", "--", "new-evidence.md")
        self.run_git("-c", "core.hooksPath=", "commit", "--no-verify", "-qm", "changed tree")
        with self.assertRaisesRegex(ValueError, "full tree differs"):
            GATE.admit(self.root, receipt)

    def test_admission_rejects_dirty_tracked_checkout(self) -> None:
        receipt = self.prepare_admission()
        self.write(HISTORY, "modified historical evidence\n")
        with self.assertRaisesRegex(ValueError, "clean tracked checkout"):
            GATE.admit(self.root, receipt)

    def test_admission_rejects_nonignored_untracked_files(self) -> None:
        receipt = self.prepare_admission()
        self.write("not-ignored.txt", "untracked content invalidates clean execution\n")
        with self.assertRaisesRegex(ValueError, "non-ignored untracked"):
            GATE.admit(self.root, receipt)

    def test_invented_evidence_exclusion_and_duplicate_fields_fail_closed(self) -> None:
        self.receipt["evidence_only_exclusions"] = [".dev/assessments"]
        with self.assertRaisesRegex(ValueError, "exactly"):
            self.validate()
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            GATE.read_json(b'{"status":"failed","status":"passed"}')

    def test_default_scan_does_not_infer_historical_obligations(self) -> None:
        self.locator = {"status": "completed", "title": "old upgrade without explicit opt-in"}
        self.write_locator()
        self.assertEqual("not-selected", GATE.validate_workflow(self.root, WORKFLOW))
        with mock.patch.object(GATE, "ROOT", self.root), mock.patch("builtins.print"):
            self.assertEqual(0, GATE.main([]))
            self.assertEqual(1, GATE.main(["--workflow-id", "2026-09-07-test"]))


if __name__ == "__main__":
    unittest.main()
