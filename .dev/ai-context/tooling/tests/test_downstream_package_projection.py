#!/usr/bin/env python3
"""Validate the explicit v0.14 downstream package applicability boundary."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[4]
MANIFEST_PATH = ROOT / ".dev/ai-context/tooling/target-gate-manifest.yaml"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DownstreamPackageProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.defect = next(
            record
            for record in cls.manifest["package_projection_defects"]
            if record["id"] == "AICU-V014-TARGET-GATE-PROJECTION-001"
        )

    def test_gwt_001_framework_dependencies_are_v014_pinned(self) -> None:
        self.assertEqual("v0.14.0", self.manifest["framework_version"])
        self.assertEqual(
            "412bb14a16fe75ee65a020b16680def0acc0ff1b",
            self.manifest["framework_commit"],
        )
        for record in self.manifest["checks"]:
            path = ROOT / record["path"]
            with self.subTest(path=record["path"]):
                self.assertTrue(path.is_file())
                self.assertEqual(record["sha256"], digest(path))

    def test_gwt_002_generic_projection_failure_is_exact_and_excluded(self) -> None:
        validator = self.defect["generic_validator"]
        self.assertEqual(validator["sha256"], digest(ROOT / validator["path"]))
        selected_paths = {record["path"] for record in self.manifest["checks"]}
        self.assertNotIn(validator["path"], selected_paths)
        self.assertEqual("blocked-by-package-projection", validator["outcome"])

    def test_gwt_003_entrypoint_projection_counts_remain_exact(self) -> None:
        record = self.defect["python_entrypoints"]
        path = ROOT / record["path"]
        self.assertEqual(record["sha256"], digest(path))
        registry = json.loads(path.read_text(encoding="utf-8"))
        portable = [item for item in registry["entrypoints"] if item["portable"]]
        source_only = [item for item in registry["entrypoints"] if not item["portable"]]
        self.assertEqual(record["portable_count"], len(portable))
        self.assertEqual(record["source_only_count"], len(source_only))
        self.assertEqual(
            record["missing_source_only_count"],
            sum(not (ROOT / item["path"]).is_file() for item in source_only),
        )
        for item in portable:
            with self.subTest(path=item["path"]):
                self.assertTrue((ROOT / item["path"]).is_file())

    def test_gwt_004_removed_stock_checks_are_absent_and_not_selected(self) -> None:
        selected_paths = {record["path"] for record in self.manifest["checks"]}
        for path in self.defect["removed_target_checks"]:
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists())
                self.assertNotIn(path, selected_paths)

    def test_gwt_005_semantic_lifecycle_and_target_validator_remain_present(self) -> None:
        shared = (
            ".ai/assets/skills/ai-context-governance/references/"
            "semantic-customization-lifecycle.md"
        )
        for skill in (
            "ai-context-governance",
            "ai-context-auditor",
            "ai-context-upgrader",
            "ai-context-init",
        ):
            spec = yaml.safe_load(
                (ROOT / f".ai/assets/skills/{skill}/skill.yaml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertIn(shared, spec["references"], skill)
        self.assertTrue((ROOT / ".ai/scripts/validate-ai-context-target.py").is_file())


if __name__ == "__main__":
    unittest.main()
