#!/usr/bin/env python3
"""Validate the explicit v0.13 downstream package applicability boundary."""

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
        defects = {
            record["id"]: record
            for record in cls.manifest["package_projection_defects"]
        }
        cls.defect = defects["AICU-V010-PROJECTION-001"]
        cls.documentation_defect = defects["AICU-V090-DOC-001"]
        cls.profile_registry_defect = defects[
            "AICU-V012-PROFILE-REGISTRY-PROJECTION-001"
        ]
        cls.routing_projection_defect = defects[
            "AICU-V013-ROUTING-PROJECTION-001"
        ]
        cls.selection_defect = cls.manifest["validation_selection_defects"][0]
        cls.commit_cutover_defect = cls.manifest["commit_policy_defects"][0]
        cls.component_ownership_defect = cls.manifest["package_metadata_defects"][0]
        cls.provider_resolution = cls.manifest["resolved_framework_conflicts"][0]

    def test_gwt_001_framework_dependencies_are_version_pinned(self) -> None:
        self.assertEqual("v0.13.0", self.manifest["framework_version"])
        for record in self.manifest["checks"]:
            path = ROOT / record["path"]
            with self.subTest(path=record["path"]):
                self.assertTrue(path.is_file())
                self.assertEqual(record["sha256"], digest(path))

    def test_gwt_002_canonical_defect_inputs_remain_exact_and_source_context_absent(self) -> None:
        validator = self.defect["validator"]
        self.assertEqual(validator["sha256"], digest(ROOT / validator["path"]))
        for record in self.defect["canonical_tests"]:
            with self.subTest(path=record["path"]):
                self.assertEqual(record["sha256"], digest(ROOT / record["path"]))
        for path in self.defect["unavailable_source_context"]:
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists())

    def test_gwt_003_registry_projects_thirteen_portable_and_eighteen_source_only_entries(self) -> None:
        record = self.defect["registry"]
        path = ROOT / record["path"]
        self.assertEqual(record["sha256"], digest(path))
        registry = json.loads(path.read_text(encoding="utf-8"))
        portable = [item for item in registry["entrypoints"] if item["portable"]]
        source_only = [item for item in registry["entrypoints"] if not item["portable"]]
        self.assertEqual(record["portable_count"], len(portable))
        self.assertEqual(record["source_only_count"], len(source_only))
        missing_source_only = [
            item for item in source_only if not (ROOT / item["path"]).is_file()
        ]
        self.assertEqual(record["missing_source_only_count"], len(missing_source_only))
        self.assertEqual(
            record["target_available_source_only_paths"],
            [item["path"] for item in source_only if (ROOT / item["path"]).is_file()],
        )
        for item in portable:
            with self.subTest(path=item["path"]):
                self.assertTrue((ROOT / item["path"]).is_file())

    def test_gwt_004_downstream_skill_colocation_remains_valid_without_source_profile(self) -> None:
        canonical = (
            ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py",
            ".ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py",
        )
        for path in canonical:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())
        self.assertFalse((ROOT / ".ai/scripts/compare-ai-context-versions.py").exists())

    def test_gwt_005_downstream_semantic_lifecycle_and_target_validator_remain_present(self) -> None:
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

    def test_gwt_006_dead_tool_command_is_resolved_by_exact_v013_document(self) -> None:
        defect = self.documentation_defect
        self.assertEqual("AICU-V090-DOC-001", defect["id"])
        self.assertEqual("resolved-by-v0.13.0", defect["status"])
        document = defect["document"]
        path = ROOT / document["path"]
        self.assertEqual(document["sha256"], digest(path))
        self.assertNotIn(defect["dead_command"], path.read_text(encoding="utf-8"))
        self.assertTrue((ROOT / defect["replacement_recipe"]).is_file())

    def test_gwt_007_changed_path_dependency_expansion_defect_is_pinned_and_inactive(self) -> None:
        defect = self.selection_defect
        self.assertEqual("AICU-V011-SELECTION-001", defect["id"])
        self.assertEqual("blocked-by-selector-defect", defect["status"])
        for key in ("selector", "evidence_helper", "product_source_contract"):
            record = defect[key]
            self.assertEqual(record["sha256"], digest(ROOT / record["path"]))
        selector = (ROOT / defect["selector"]["path"]).read_text(encoding="utf-8")
        self.assertIn('[ -n "${SELECTED_CHECK_IDS[$id]:-}" ] && return 0', selector)
        self.assertIn('SELECTED_CHECK_IDS["$id"]=selected', selector)
        self.assertIn('select_with_dependencies "$id"', selector)
        self.assertIn("Keep changed-path profile execution and evidence reuse inactive", defect["disposition"])

    def test_gwt_008_profile_registry_source_dependency_is_pinned_and_excluded(self) -> None:
        defect = self.profile_registry_defect
        self.assertEqual("AICU-V012-PROFILE-REGISTRY-PROJECTION-001", defect["id"])
        record = defect["canonical_test"]
        self.assertEqual(record["sha256"], digest(ROOT / record["path"]))
        self.assertFalse((ROOT / defect["unavailable_dependency"]).exists())
        selected_paths = {record["path"] for record in self.manifest["checks"]}
        self.assertNotIn(record["path"], selected_paths)

    def test_gwt_009_commit_cutover_is_prospective_and_history_preserving(self) -> None:
        defect = self.commit_cutover_defect
        self.assertEqual("AICU-V012-COMMIT-CUTOVER-001", defect["id"])
        self.assertEqual(
            "ca17969c539836ea6b42de2de361367041d57d84",
            defect["last_legacy_commit"],
        )
        self.assertLess(defect["package_effective_at"], defect["target_effective_at"])
        self.assertIn("without rewriting", defect["disposition"])

    def test_gwt_010_stock_routing_test_is_pinned_and_downstream_projection_selected(self) -> None:
        defect = self.routing_projection_defect
        self.assertEqual("AICU-V013-ROUTING-PROJECTION-001", defect["id"])
        record = defect["canonical_test"]
        self.assertEqual(record["sha256"], digest(ROOT / record["path"]))
        self.assertFalse((ROOT / defect["unavailable_dependency"]).exists())
        self.assertTrue((ROOT / defect["downstream_test"]).is_file())
        selected_paths = {record["path"] for record in self.manifest["checks"]}
        self.assertNotIn(record["path"], selected_paths)
        self.assertEqual("GWT8", defect["source_release_only_case"])

    def test_gwt_011_component_ownership_inconsistency_remains_explicit(self) -> None:
        defect = self.component_ownership_defect
        self.assertEqual("AICU-V013-COMPONENT-OWNERSHIP-001", defect["id"])
        portable_manifest = yaml.safe_load(
            (ROOT / ".ai/assets/shared/governance/portable-policy-manifest.yaml").read_text(
                encoding="utf-8"
            )
        )
        mapping = next(
            record
            for record in portable_manifest["mappings"]
            if record["source"] == "AI-CONTEXT-VERSION-POLICY.md"
        )
        self.assertEqual(defect["portable_policy_component"], mapping["component_id"])
        self.assertNotEqual(
            defect["portable_policy_component"],
            defect["package_inventory_component"],
        )
        self.assertTrue((ROOT / defect["evidence"]).is_file())

    def test_gwt_012_bundled_provider_conflict_is_resolved_without_activation(self) -> None:
        resolution = self.provider_resolution
        self.assertEqual("resolved-by-v0.13.0", resolution["status"])
        self.assertTrue((ROOT / resolution["recipe_manifest"]).is_file())
        self.assertFalse(
            (
                ROOT
                / ".ai/assets/tech-stacks/dotnet-backend/tooling/"
                "bundled-mechanical-validation"
            ).exists()
        )
        manifest = yaml.safe_load(
            (ROOT / resolution["recipe_manifest"]).read_text(encoding="utf-8")
        )
        serialized = str(manifest).lower()
        self.assertIn("reference-only", serialized)
        self.assertIn("not-selected", serialized)
        for path in (
            "README.md",
            "README.en.md",
            ".dev/ARCHITECTURE.md",
            ".dev/project-config.yaml",
        ):
            with self.subTest(target_truth=path):
                target_truth = (ROOT / path).read_text(encoding="utf-8").lower()
                self.assertNotIn("bundled-mechanical-validation/", target_truth)
                self.assertIn("on-demand", target_truth)
                self.assertIn("reference-only", target_truth)


if __name__ == "__main__":
    unittest.main()
