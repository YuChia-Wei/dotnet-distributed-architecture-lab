#!/usr/bin/env python3
"""Validate the explicit v0.15.1 downstream package applicability boundary."""

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
            if record["id"] == "AICU-V015-TARGET-GATE-PROJECTION-001"
        )
        cls.selection = next(
            record
            for record in cls.manifest["validation_selection_defects"]
            if record["id"] == "AICU-V011-SELECTION-001"
        )

    def test_gwt_001_framework_dependencies_are_v0151_pinned(self) -> None:
        self.assertEqual("v0.15.1", self.manifest["framework_version"])
        self.assertEqual(
            "f2b5fa7c13550efaeb65ab9fcaeb0403baa2a5af",
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

    def test_gwt_006_validation_selection_resolution_is_exact(self) -> None:
        self.assertEqual("resolved-upstream", self.selection["status"])
        self.assertEqual("v0.15.0", self.selection["resolved_in"])
        self.assertEqual("v0.15.1", self.selection["verified_through"])
        for key in ("selector", "evidence_helper"):
            record = self.selection[key]
            self.assertEqual(record["sha256"], digest(ROOT / record["path"]))


if __name__ == "__main__":
    unittest.main()
