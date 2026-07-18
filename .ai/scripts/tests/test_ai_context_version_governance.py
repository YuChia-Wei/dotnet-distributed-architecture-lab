#!/usr/bin/env python3
"""Given-When-Then regression tests for AI context version governance."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]


def load_script(name: str):
    path = ROOT / ".ai" / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


COMPARE = load_script("compare-ai-context-versions.py")
VALIDATE = load_script("validate-ai-context-versions.py")


class AiContextVersionGovernanceGwtTests(unittest.TestCase):
    def test_gwt_001_given_published_records_when_validated_then_tags_match_commits(self):
        # Given the repository's published release records
        # When version governance validation runs
        errors = VALIDATE.validate(ROOT)
        # Then every published tag resolves to its recorded commit
        self.assertEqual([], errors)

    def test_gwt_002_given_valid_target_manifest_when_validated_then_it_passes(self):
        # Given a target manifest with coherent source and migration identity
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "AI-CONTEXT-SOURCE.yaml"
            path.write_text(yaml.safe_dump({
                "schema_version": "1.0",
                "source": {"repository": "owner/repo", "release_id": "REL-v0.2.0", "version": "v0.2.0", "tag": "v0.2.0", "commit": "9abc75b543ae201865c1e119d29fac2bcd2f4542"},
                "installation": {"initialized_by": "repo-structure-sync", "imported_at": "2026-07-14T21:26:05+08:00", "last_upgraded_at": None},
                "previous_source": None,
                "local_overrides": [],
                "reconciliation": {"unresolved": []},
                "last_migration": {"status": "completed", "from_version": "v0.1.0", "to_version": "v0.2.0", "completed_at": "2026-07-14T21:26:05+08:00", "evidence": "check-all"},
            }, sort_keys=False), encoding="utf-8")
            # When the manifest is validated
            errors: list[str] = []
            VALIDATE.validate_manifest(path, errors)
            # Then no invariant fails
            self.assertEqual([], errors)

    def test_gwt_003_given_incoherent_target_manifest_when_validated_then_it_fails_closed(self):
        # Given a manifest whose version, tag, release ID, and commit disagree
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "AI-CONTEXT-SOURCE.yaml"
            path.write_text("source:\n  repository: owner/repo\n  release_id: REL-v9.0.0\n  version: v0.2.0\n  tag: v0.1.0\n  commit: short\n", encoding="utf-8")
            # When the manifest is validated
            errors: list[str] = []
            VALIDATE.validate_manifest(path, errors)
            # Then multiple source and lifecycle invariants fail
            self.assertGreaterEqual(len(errors), 4)

    def test_gwt_004_given_target_without_source_release_history_when_validated_then_manifest_is_sufficient(self):
        # Given a target repository that intentionally excludes source release history
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / ".dev" / "AI-CONTEXT-SOURCE.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(yaml.safe_dump({
                "schema_version": "1.0",
                "source": {"repository": "owner/repo", "release_id": "REL-v0.2.0", "version": "v0.2.0", "tag": "v0.2.0", "commit": "9abc75b543ae201865c1e119d29fac2bcd2f4542"},
                "installation": {"initialized_by": "repo-structure-sync", "imported_at": "2026-07-14T21:26:05+08:00", "last_upgraded_at": None},
                "previous_source": None,
                "local_overrides": [],
                "reconciliation": {"unresolved": []},
                "last_migration": {"status": "completed", "from_version": "v0.1.0", "to_version": "v0.2.0", "completed_at": "2026-07-14T21:26:05+08:00", "evidence": "check-all"},
            }, sort_keys=False), encoding="utf-8")
            # When the repository-level validator runs in target mode
            errors = VALIDATE.validate(root)
            # Then the target manifest is sufficient and source release records are not required
            self.assertEqual([], errors)

    def test_gwt_005_given_unchanged_reusable_target_path_when_compared_then_it_is_automatic_candidate(self):
        # Given a reusable target file that is byte-identical to the base
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            target_file = target / ".ai" / "assets" / "shared" / "rule.md"
            target_file.parent.mkdir(parents=True)
            base = COMPARE.git_blob(ROOT, "v0.1.0", ".ai/assets/shared/README.MD")
            self.assertIsNotNone(base)
            target_file.write_bytes(base)
            # When it is classified using that base blob under a reusable path
            original = COMPARE.git_blob
            COMPARE.git_blob = lambda *_: base
            try:
                category, _ = COMPARE.classify_change(ROOT, "v0.1.0", "M", ".ai/assets/shared/rule.md", target)
            finally:
                COMPARE.git_blob = original
            # Then it may be proposed as an automatic candidate
            self.assertEqual("automatic-candidate", category)

    def test_gwt_006_given_local_or_target_owned_change_when_compared_then_it_requires_reconciliation(self):
        # Given target-owned AGENTS and a locally modified reusable path
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            local_file = target / ".ai" / "assets" / "shared" / "rule.md"
            local_file.parent.mkdir(parents=True)
            local_file.write_text("local", encoding="utf-8")
            # When both paths are classified
            owned, _ = COMPARE.classify_change(ROOT, "v0.1.0", "M", "AGENTS.md", target)
            local, _ = COMPARE.classify_change(ROOT, "v0.1.0", "M", ".ai/assets/shared/rule.md", target)
            # Then neither is silently replaceable
            self.assertEqual("reconcile", owned)
            self.assertEqual("reconcile", local)

    def test_gwt_007_given_source_history_or_product_path_when_compared_then_it_is_excluded(self):
        # Given source workflow, release history, and product paths
        paths = [".dev/workflows/2026-01-01-old/workflow.yaml", ".dev/releases/v0.2.0/release.yaml", "src/App.cs", "tests/AppTests.cs"]
        # When each path is classified
        categories = [COMPARE.classify_change(ROOT, "v0.1.0", "M", path, None)[0] for path in paths]
        # Then all are excluded from AI context upgrade
        self.assertEqual(["exclude"] * len(paths), categories)

    def test_gwt_008_given_reusable_assessment_governance_when_compared_then_it_is_not_excluded(self):
        # Given reusable assessment navigation rather than an assessment instance
        # When the path is classified without a target tree
        category, _ = COMPARE.classify_change(ROOT, "v0.1.0", "A", ".dev/assessments/README.MD", None)
        # Then it remains available for normal reconciliation
        self.assertEqual("reconcile", category)

    def test_gwt_009_given_reusable_history_readmes_and_target_indexes_when_compared_then_none_are_excluded(self):
        # Given reusable workflow/backlog documentation and target-owned catalogs
        paths = [".dev/workflows/README.MD", ".dev/backlog/README.MD", ".dev/workflows/INDEX.MD", ".dev/backlog/INDEX.MD"]
        # When each path is classified without a target tree
        categories = [COMPARE.classify_change(ROOT, "v0.1.0", "M", path, None)[0] for path in paths]
        # Then all require normal reconciliation instead of disappearing from the plan
        self.assertEqual(["reconcile"] * len(paths), categories)

    def test_gwt_010_given_real_release_tags_when_compared_then_cli_is_read_only_and_resolves_both(self):
        # Given the historical v0.1.0 and v0.2.0 tags
        before = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        # When a read-only comparison report is built
        report = COMPARE.build_report(ROOT, "v0.1.0", "v0.2.0", None)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        # Then refs resolve, changes are classified, and the worktree is untouched
        self.assertEqual("69c285077708dfb96ee49bb39258aec83eb7f1a9", report["from"]["commit"])
        self.assertEqual("9abc75b543ae201865c1e119d29fac2bcd2f4542", report["to"]["commit"])
        self.assertTrue(report["changes"])
        self.assertEqual(before, after)

    def test_gwt_011_given_governed_package_candidate_when_validated_then_distribution_identity_matches_version(
        self,
    ):
        # Given a planned governed release with coherent package and publication metadata
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".dev" / "releases" / "v0.3.0" / "release.yaml"
            release.parent.mkdir(parents=True)
            for artifact in ("release-notes.md", "migration-guide.md"):
                (release.parent / artifact).write_text("candidate\n", encoding="utf-8")
            release.write_text(yaml.safe_dump({
                "release_id": "REL-v0.3.0",
                "version": "v0.3.0",
                "status": "planned",
                "record_origin": "governed",
                "distribution_kind": "governed-package",
                "installable": True,
                "tag": None,
                "commit": None,
                "compatibility": {
                    "breaking_changes": True,
                    "minimum_source_version": "v0.1.0",
                    "reconciliation_sources": ["v0.1.0", "v0.2.0"],
                    "automatic_upgrade_sources": [],
                },
                "distribution": {
                    "profile_id": "dotnet-backend",
                    "package_id": "ai-context-dotnet-backend-v0.3.0",
                    "schema_versions": {
                        "package": "1.0.0",
                        "files": "1.0.0",
                        "migration": "1.0.0",
                    },
                    "artifacts": {
                        "zip": "ai-context-dotnet-backend-v0.3.0.zip",
                        "zip_checksum": "ai-context-dotnet-backend-v0.3.0.zip.sha256",
                        "tar_gz": "ai-context-dotnet-backend-v0.3.0.tar.gz",
                        "tar_gz_checksum": "ai-context-dotnet-backend-v0.3.0.tar.gz.sha256",
                    },
                    "migration": {
                        "default_mode": "dry-run",
                        "apply_requires_clean_worktree": True,
                        "apply_requires_acknowledged_reconciliation": True,
                    },
                    "publication": {
                        "tag_owner": "user",
                        "trigger": "user-created-tag",
                        "automation": "github-actions",
                        "creates_or_moves_tag": False,
                    },
                },
            }, sort_keys=False), encoding="utf-8")
            # When the candidate release record is validated
            errors: list[str] = []
            VALIDATE.validate_release(release, root, errors, verify_git=False)
            # Then its package, upgrade, and manual-tag identities are coherent
            self.assertEqual([], errors)

    def test_gwt_012_given_governed_candidate_with_drift_when_validated_then_it_fails_closed(
        self,
    ):
        # Given a governed candidate whose package version drifts and automation may move tags
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".dev" / "releases" / "v0.3.0" / "release.yaml"
            release.parent.mkdir(parents=True)
            for artifact in ("release-notes.md", "migration-guide.md"):
                (release.parent / artifact).write_text("candidate\n", encoding="utf-8")
            release.write_text(yaml.safe_dump({
                "release_id": "REL-v0.3.0",
                "version": "v0.3.0",
                "status": "planned",
                "record_origin": "governed",
                "distribution_kind": "governed-package",
                "installable": False,
                "tag": "v0.3.0",
                "commit": None,
                "compatibility": {
                    "breaking_changes": True,
                    "minimum_source_version": "v0.1.0",
                    "reconciliation_sources": ["v0.2.0"],
                    "automatic_upgrade_sources": ["v0.0.1"],
                },
                "distribution": {
                    "profile_id": "dotnet-backend",
                    "package_id": "ai-context-dotnet-backend-v9.0.0",
                    "schema_versions": {},
                    "artifacts": {},
                    "migration": {},
                    "publication": {"creates_or_moves_tag": True},
                },
            }, sort_keys=False), encoding="utf-8")
            # When the candidate release record is validated
            errors: list[str] = []
            VALIDATE.validate_release(release, root, errors, verify_git=False)
            # Then identity, safety, compatibility, and pre-publication invariants fail
            self.assertGreaterEqual(len(errors), 10)

    def test_gwt_013_given_retrospective_source_snapshot_when_validated_then_it_is_not_installable(self):
        # Given a retrospective tag retained only as a source/provenance anchor.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".dev" / "releases" / "v0.1.0" / "release.yaml"
            release.parent.mkdir(parents=True)
            for artifact in ("release-notes.md", "migration-guide.md"):
                (release.parent / artifact).write_text("historical snapshot\n", encoding="utf-8")
            release.write_text(yaml.safe_dump({
                "release_id": "REL-v0.1.0",
                "version": "v0.1.0",
                "status": "published",
                "record_origin": "retrospective",
                "distribution_kind": "source-snapshot-only",
                "installable": False,
                "tag": "v0.1.0",
                "commit": "69c285077708dfb96ee49bb39258aec83eb7f1a9",
                "compatibility": {"breaking_changes": False},
            }, sort_keys=False), encoding="utf-8")
            # When the record is validated without resolving fixture Git refs.
            errors: list[str] = []
            VALIDATE.validate_release(release, root, errors, verify_git=False)
            # Then the historical non-installable semantics are coherent.
            self.assertEqual([], errors)

    def test_gwt_014_given_historical_snapshot_claims_installability_when_validated_then_it_fails_closed(self):
        # Given a retrospective source snapshot falsely claims package installability.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            release = root / ".dev" / "releases" / "v0.1.0" / "release.yaml"
            release.parent.mkdir(parents=True)
            for artifact in ("release-notes.md", "migration-guide.md"):
                (release.parent / artifact).write_text("historical snapshot\n", encoding="utf-8")
            release.write_text(yaml.safe_dump({
                "release_id": "REL-v0.1.0",
                "version": "v0.1.0",
                "status": "published",
                "record_origin": "retrospective",
                "distribution_kind": "governed-package",
                "installable": True,
                "tag": "v0.1.0",
                "commit": "69c285077708dfb96ee49bb39258aec83eb7f1a9",
                "compatibility": {"breaking_changes": False},
                "distribution": {},
            }, sort_keys=False), encoding="utf-8")
            # When release validation checks origin and distribution semantics.
            errors: list[str] = []
            VALIDATE.validate_release(release, root, errors, verify_git=False)
            # Then the false package claim and incomplete distribution both fail.
            self.assertGreaterEqual(len(errors), 5)
            self.assertTrue(any("retrospective releases" in error for error in errors))

    def test_gwt_015_given_v001_source_when_v030_is_inspected_then_only_reconciliation_is_supported(self):
        # Given the confirmed retrospective v0.0.1 source snapshot.
        historical = yaml.safe_load(
            (ROOT / ".dev/releases/v0.0.1/release.yaml").read_text(encoding="utf-8")
        )
        candidate = yaml.safe_load(
            (ROOT / ".dev/releases/v0.3.0/release.yaml").read_text(encoding="utf-8")
        )

        # When the v0.3.0 compatibility boundary is inspected.
        compatibility = candidate["compatibility"]

        # Then v0.0.1 is non-installable and can only enter manual reconciliation.
        self.assertEqual("source-snapshot-only", historical["distribution_kind"])
        self.assertFalse(historical["installable"])
        self.assertIn("v0.0.1", compatibility["reconciliation_sources"])
        self.assertNotIn("v0.0.1", compatibility["automatic_upgrade_sources"])


if __name__ == "__main__":
    unittest.main()
