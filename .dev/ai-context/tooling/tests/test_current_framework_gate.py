"""Focused safety/subject regressions for the target-owned current gate."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
ENTRY = ROOT / ".dev/ai-context/tooling/validate-current-framework.py"
spec = importlib.util.spec_from_file_location("current_target_gate", ENTRY)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CurrentGateTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / ".dev/ai-context/local/current-gate-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.fixture = tempfile.TemporaryDirectory(prefix="case-", dir=parent)
        self.addCleanup(self.fixture.cleanup)
        self.root = Path(self.fixture.name)

    def put(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def test_pinned_payload_rejects_changed_bytes(self):
        self.put("payload.txt", b"accepted")
        reference = {"path": "payload.txt", "sha256": hashlib.sha256(b"accepted").hexdigest()}
        self.assertEqual(gate.Files(self.root).pinned(reference), b"accepted")
        self.put("payload.txt", b"replaced")
        with self.assertRaisesRegex(gate.GateError, "pinned bytes differ"):
            gate.Files(self.root).pinned(reference)

    def test_changed_binding_cannot_repin_itself(self):
        binding = {"schema_version": "target-framework-binding/v1", "state": "pilot-review",
                   "runtime": "codex", "legacy_baseline_role": "retained-target-rules-and-legacy-package-support"}
        raw = json.dumps(binding).encode()
        self.put(gate.BINDING, raw)
        accepted = hashlib.sha256(raw).hexdigest()
        self.assertEqual(gate.load_binding(gate.Files(self.root), accepted), binding)
        binding["extra_unreviewed_authority"] = True
        self.put(gate.BINDING, json.dumps(binding).encode())
        with self.assertRaisesRegex(gate.GateError, "caller-selected subject"):
            gate.load_binding(gate.Files(self.root), accepted)

    def test_incomplete_binding_remains_blocked(self):
        raw = json.dumps({"schema_version": "target-framework-binding/v1", "state": "preparation-blocked"}).encode()
        self.put(gate.BINDING, raw)
        with self.assertRaisesRegex(gate.GateError, "not a prepared pilot"):
            gate.load_binding(gate.Files(self.root), hashlib.sha256(raw).hexdigest())

    def test_duplicate_packages_cannot_preserve_count(self):
        with self.assertRaisesRegex(gate.GateError, "duplicate identity"):
            gate.unique([{"id": "lesson"}, {"id": "lesson"}], lambda row: row["id"], "components")

    def test_case_spelling_hardlink_and_traversal_refuse(self):
        first = self.put("Actual.txt", b"one")
        with self.assertRaisesRegex(gate.GateError, "spelling"):
            gate.Files(self.root).read("actual.txt")
        os.link(first, self.root / "linked.txt")
        with self.assertRaisesRegex(gate.GateError, "unsupported file"):
            gate.Files(self.root).read("Actual.txt")
        for name in ["../escape", "/absolute", "a/../b", "a//b", "C:/host", r"a\b"]:
            with self.subTest(name=name), self.assertRaises(gate.GateError):
                gate.relative(name)

    def test_listing_overflow_never_returns_partial_inventory(self):
        for name in ["one", "two", "three"]:
            self.put(name, b"x")
        previous = gate.MAX_ENTRIES
        gate.MAX_ENTRIES = 2
        self.addCleanup(setattr, gate, "MAX_ENTRIES", previous)
        files = gate.Files(self.root)
        with self.assertRaisesRegex(gate.GateError, "observation limit"):
            files.locate("one")
        self.assertEqual(files.names, {})

    def test_exact_json_comparison_rejects_boolean_and_float_versions(self):
        self.assertFalse(gate.exact({"version": 1}, {"version": True}))
        self.assertFalse(gate.exact({"version": 1}, {"version": 1.0}))

    def test_valid_review_selector_cannot_be_assigned_to_adr(self):
        binding = json.loads((ROOT / gate.BINDING).read_bytes())
        review = next(row for row in binding["route_bindings"] if row["package"] == "code-reviewer")
        review["package"] = "adr"
        with self.assertRaisesRegex(gate.GateError, "wrong package"):
            gate.rules_check(gate.Files(ROOT), binding)

    def test_dropping_a_required_rule_refuses_before_resolver(self):
        binding = json.loads((ROOT / gate.BINDING).read_bytes())
        binding["rule_ids"].remove("MESSAGING-TX-001")
        with self.assertRaisesRegex(gate.GateError, "dispositions differ"):
            gate.rules_check(gate.Files(ROOT), binding)


if __name__ == "__main__":
    unittest.main(verbosity=2)
