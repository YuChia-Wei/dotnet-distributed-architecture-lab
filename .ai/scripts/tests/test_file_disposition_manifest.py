#!/usr/bin/env python3
"""GWT regression tests for file-disposition manifest validation."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = ROOT / ".ai/scripts/validate-file-disposition-manifest.py"
SPEC = importlib.util.spec_from_file_location("file_disposition_validator", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def valid_manifest() -> dict:
    return {
        "contract": {"allowed_dispositions": sorted(VALIDATOR.ALLOWED_DISPOSITIONS)},
        "coverage": {
            "base_commit": "a" * 40,
            "included_roots": [".ai/", ".dev/standards/"],
        },
        "entries": [
            {
                "path": ".ai/kept.md",
                "disposition": "kept",
                "destination": None,
                "change_summary": "Keep the canonical path.",
                "target_migration": "three-way",
            },
            {
                "path": ".dev/standards/old.md",
                "disposition": "moved-to",
                "destination": ".dev/standards/new.md",
                "change_summary": "Move the standard.",
                "target_migration": "reconcile-move",
            },
        ],
    }


def valid_v2_manifest() -> dict:
    return {
        "schema_version": "2.0",
        "manifest_id": "v050-published-path-disposition",
        "target_release": "v0.5.0",
        "subject_commit": "b" * 40,
        "profile": {
            "id": "dotnet-backend",
            "path": ".ai/distribution/profiles/dotnet-backend.yaml",
        },
        "published_versions": ["v0.3.0", "v0.4.0", "v0.4.1", "v0.4.2"],
        "approval": {
            "authority": "repository-owner",
            "authorized_at": "2026-07-21T00:00:00+08:00",
            "scope": "Execute all v0.5.0 development work.",
        },
        "contract": {
            "allowed_decisions": sorted(VALIDATOR.V2_DECISIONS),
            "removal_rule": "Removal requires retained downstream evidence.",
            "compatibility_rule": "Deprecation retains the published path.",
        },
        "coverage": {
            "base_commit": "a" * 40,
            "included_roots": [".ai/"],
            "candidate_paths": [".ai/kept.md", ".ai/deprecated.sh"],
        },
        "entries": [
            {
                "path": ".ai/kept.md",
                "lifecycle_before": "compatibility",
                "decision": "retain",
                "lifecycle_after": "compatibility",
                "distribution_after": "packaged",
                "published_bytes": "identical",
                "destination": None,
                "replacement": None,
                "compatibility_impact": "Existing consumers keep the same path.",
                "migration": "No target migration is required.",
                "consumer_refs": [".ai/consumer.md"],
                "evidence_refs": [".ai/evidence.md"],
                "downstream_evidence": [],
                "decision_ref": ".ai/decision.md",
            },
            {
                "path": ".ai/deprecated.sh",
                "lifecycle_before": "transitional",
                "decision": "deprecate",
                "lifecycle_after": "deprecated",
                "distribution_after": "packaged",
                "published_bytes": "identical",
                "destination": None,
                "replacement": "Use the compiled validator.",
                "compatibility_impact": "The compatibility path remains available.",
                "migration": "Move callers to the compiled validator.",
                "consumer_refs": [".ai/consumer.md"],
                "evidence_refs": [".ai/evidence.md"],
                "downstream_evidence": [],
                "decision_ref": ".ai/decision.md",
            },
        ],
    }


class FileDispositionManifestTests(unittest.TestCase):
    def validate(
        self,
        data: dict,
        *,
        changed: set[str] | None = None,
    ) -> list[str]:
        return VALIDATOR.validate_manifest_data(
            data,
            current_paths={".ai/kept.md", ".dev/standards/new.md"},
            base_paths={".ai/kept.md", ".dev/standards/old.md"},
            changed_paths=changed or {".ai/kept.md", ".dev/standards/old.md"},
        )

    def test_gwt_001_given_complete_exact_case_manifest_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(valid_manifest()))

    def test_gwt_002_given_changed_path_without_disposition_when_validated_then_fails(self) -> None:
        errors = self.validate(valid_manifest(), changed={".ai/uncovered.md"})
        self.assertIn("coverage missing changed path: .ai/uncovered.md", errors)

    def test_gwt_003_given_move_without_existing_destination_when_validated_then_fails(self) -> None:
        data = valid_manifest()
        data["entries"][1]["destination"] = ".dev/standards/Missing.md"
        errors = self.validate(data)
        self.assertTrue(any("destination does not exist" in error for error in errors))

    def test_gwt_004_given_retired_path_absent_from_base_when_validated_then_fails(self) -> None:
        data = valid_manifest()
        data["entries"][1]["disposition"] = "retired"
        data["entries"][1]["destination"] = None
        data["entries"][1]["path"] = ".dev/standards/unknown.md"
        errors = self.validate(data, changed={".dev/standards/unknown.md"})
        self.assertTrue(any("absent from the coverage base commit" in error for error in errors))


class FileDispositionManifestV2Tests(unittest.TestCase):
    versions = ("v0.3.0", "v0.4.0", "v0.4.1", "v0.4.2")
    candidates = {".ai/kept.md", ".ai/deprecated.sh"}
    supporting = {
        ".ai/distribution/profiles/dotnet-backend.yaml",
        ".ai/consumer.md",
        ".ai/evidence.md",
        ".ai/decision.md",
    }

    def validate(
        self,
        data: dict,
        *,
        current_paths: set[str] | None = None,
        published_paths: dict[str, set[str]] | None = None,
        packaged_paths: set[str] | None = None,
        subject_match_paths: set[str] | None = None,
        published_identical_paths: set[str] | None = None,
        published_evolved_paths: set[str] | None = None,
        latest_published_match_paths: set[str] | None = None,
    ) -> list[str]:
        current = current_paths or self.candidates | self.supporting
        published = published_paths or {
            version: set(self.candidates) for version in self.versions
        }
        return VALIDATOR.validate_manifest_data(
            data,
            current_paths=current,
            subject_paths=set(self.candidates),
            published_paths=published,
            packaged_paths=packaged_paths or set(self.candidates),
            subject_match_paths=subject_match_paths or set(self.candidates),
            published_identical_paths=(
                set(self.candidates)
                if published_identical_paths is None
                else published_identical_paths
            ),
            published_evolved_paths=published_evolved_paths or set(),
            latest_published_match_paths=latest_published_match_paths or set(),
            base_matches_latest_published=True,
            actual_profile_id="dotnet-backend",
            actual_lifecycles={".ai/deprecated.sh": "deprecated"},
        )

    def test_gwt_005_given_complete_v2_manifest_when_validated_then_passes(self) -> None:
        # Given an evidence-rich manifest with exact candidate and release coverage.
        # When v2 validation runs, then it passes.
        self.assertEqual([], self.validate(valid_v2_manifest()))

    def test_gwt_006_given_candidate_without_entry_when_validated_then_parity_fails(self) -> None:
        # Given one governed candidate has no disposition entry.
        data = valid_v2_manifest()
        data["entries"].pop()

        # When validation runs, then exact candidate parity fails.
        errors = self.validate(data)
        self.assertTrue(any("candidate/entry parity mismatch" in error for error in errors))

    def test_gwt_007_given_deprecation_without_replacement_when_validated_then_fails(self) -> None:
        # Given a deprecated-in-place path has no replacement direction.
        data = valid_v2_manifest()
        data["entries"][1]["replacement"] = None

        # When validation runs, then migration intent fails closed.
        errors = self.validate(data)
        self.assertTrue(any("deprecate requires a replacement" in error for error in errors))

    def test_gwt_008_given_remove_without_downstream_evidence_when_validated_then_fails(self) -> None:
        # Given a published path is marked for removal without downstream proof.
        data = valid_v2_manifest()
        entry = data["entries"][1]
        entry.update(
            {
                "decision": "remove",
                "lifecycle_after": "removed",
                "distribution_after": "excluded",
                "replacement": None,
            }
        )

        # When validation runs, then removal is rejected.
        errors = self.validate(data)
        self.assertTrue(any("remove requires retained downstream evidence" in error for error in errors))

    def test_gwt_009_given_retain_not_packaged_when_validated_then_fails(self) -> None:
        # Given a retain decision is missing from the package projection.
        # When validation runs, then distribution evidence fails closed.
        errors = self.validate(
            valid_v2_manifest(), packaged_paths={".ai/deprecated.sh"}
        )
        self.assertTrue(any("retain must remain packaged" in error for error in errors))

    def test_gwt_010_given_path_absent_from_published_version_when_validated_then_fails(self) -> None:
        # Given one declared published version lacks a candidate path.
        published = {version: set(self.candidates) for version in self.versions}
        published["v0.4.0"].remove(".ai/kept.md")

        # When validation runs, then published-path evidence fails closed.
        errors = self.validate(valid_v2_manifest(), published_paths=published)
        self.assertTrue(any("absent from published version v0.4.0" in error for error in errors))

    def test_gwt_011_given_current_bytes_drift_from_subject_when_validated_then_fails(self) -> None:
        # Given one candidate no longer matches the pinned immutable subject.
        # When validation runs, then unreviewed content drift fails closed.
        errors = self.validate(
            valid_v2_manifest(), subject_match_paths={".ai/deprecated.sh"}
        )
        self.assertTrue(any("differs from the pinned subject_commit" in error for error in errors))

    def test_gwt_012_given_profile_identity_drift_when_validated_then_fails(self) -> None:
        # Given the manifest names a profile other than the loaded profile.
        data = valid_v2_manifest()
        data["profile"]["id"] = "other"

        # When validation runs, then profile truth wins.
        errors = self.validate(data)
        self.assertTrue(any("differs from profile truth" in error for error in errors))

    def test_gwt_013_given_missing_evidence_reference_when_validated_then_fails(self) -> None:
        # Given a decision cites an exact path absent from repository truth.
        data = valid_v2_manifest()
        data["entries"][0]["evidence_refs"] = [".ai/missing.md"]

        # When validation runs, then evidence existence fails closed.
        errors = self.validate(data)
        self.assertTrue(any("does not exist with exact Git casing" in error for error in errors))

    def test_gwt_014_given_lifecycle_differs_from_registry_when_validated_then_fails(self) -> None:
        # Given the disposition says deprecated but the current registry still says transitional.
        data = valid_v2_manifest()

        # When validation sees the registry truth, then lifecycle drift fails.
        errors = VALIDATOR.validate_manifest_data(
            data,
            current_paths=self.candidates | self.supporting,
            subject_paths=set(self.candidates),
            published_paths={
                version: set(self.candidates) for version in self.versions
            },
            packaged_paths=set(self.candidates),
            subject_match_paths=set(self.candidates),
            published_identical_paths=set(self.candidates),
            published_evolved_paths=set(),
            latest_published_match_paths=set(),
            base_matches_latest_published=True,
            actual_profile_id="dotnet-backend",
            actual_lifecycles={".ai/deprecated.sh": "transitional"},
        )
        self.assertTrue(any("differs from registry truth" in error for error in errors))

    def test_gwt_015_given_evolved_history_matching_latest_release_when_validated_then_passes(self) -> None:
        # Given one path evolved before the latest published release and now matches it.
        data = valid_v2_manifest()
        data["entries"][0]["published_bytes"] = "evolved"

        # When the evidence sets agree, then the reviewed evolution is accepted.
        self.assertEqual(
            [],
            self.validate(
                data,
                published_identical_paths={".ai/deprecated.sh"},
                published_evolved_paths={".ai/kept.md"},
                latest_published_match_paths={".ai/kept.md"},
            ),
        )

    def test_gwt_016_given_evolved_declaration_without_blob_evolution_when_validated_then_fails(self) -> None:
        # Given a path declares evolution but Git evidence contains one blob.
        data = valid_v2_manifest()
        data["entries"][0]["published_bytes"] = "evolved"

        # When validation runs, then the declaration fails closed.
        errors = self.validate(data)
        self.assertTrue(any("does not show an evolved blob history" in error for error in errors))

    def test_gwt_017_given_evolved_history_not_matching_latest_release_when_validated_then_fails(self) -> None:
        # Given an evolved path's subject differs from the newest published release.
        data = valid_v2_manifest()
        data["entries"][0]["published_bytes"] = "evolved"

        # When validation runs, then the subject cannot silently redefine release truth.
        errors = self.validate(
            data,
            published_identical_paths={".ai/deprecated.sh"},
            published_evolved_paths={".ai/kept.md"},
        )
        self.assertTrue(any("latest published version differs" in error for error in errors))

    def test_gwt_018_given_base_commit_not_latest_published_when_validated_then_fails(self) -> None:
        # Given the recorded baseline does not resolve to the newest published tag.
        data = valid_v2_manifest()

        # When validation runs, then fabricated or stale baseline identity fails closed.
        errors = VALIDATOR.validate_manifest_data(
            data,
            current_paths=self.candidates | self.supporting,
            subject_paths=set(self.candidates),
            published_paths={
                version: set(self.candidates) for version in self.versions
            },
            packaged_paths=set(self.candidates),
            subject_match_paths=set(self.candidates),
            published_identical_paths=set(self.candidates),
            published_evolved_paths=set(),
            latest_published_match_paths=set(),
            base_matches_latest_published=False,
            actual_profile_id="dotnet-backend",
            actual_lifecycles={".ai/deprecated.sh": "deprecated"},
        )
        self.assertTrue(any("newest published version commit" in error for error in errors))

    def test_gwt_019_given_nonexistent_base_commit_when_git_facts_are_collected_then_it_fails(self) -> None:
        # Given the manifest records a well-shaped but nonexistent baseline SHA.
        data = valid_v2_manifest()

        def fake_git(_root: Path, *args: str) -> list[str]:
            if args[0] == "ls-files":
                return sorted(self.candidates | self.supporting)
            if args[0] == "cat-file" and args[-1] == f"{'a' * 40}^{{commit}}":
                raise RuntimeError("fatal: bad object")
            return []

        # When immutable Git facts are collected, then existence fails closed.
        with mock.patch.object(VALIDATOR, "run_git", side_effect=fake_git):
            with self.assertRaisesRegex(RuntimeError, "bad object"):
                VALIDATOR.collect_v2_git_facts(ROOT, data)

    def test_gwt_020_given_single_star_profile_when_nested_path_is_evaluated_then_it_is_not_packaged(self) -> None:
        # Given the package profile uses one star at one directory depth.
        profile = {
            "entries": [{"source": ".ai/scripts/*.sh"}],
            "exclusions": [],
        }
        paths = {".ai/scripts/top.sh", ".ai/scripts/nested/deep.sh"}

        # When package projection runs, then one star does not cross a slash.
        self.assertEqual(
            {".ai/scripts/top.sh"},
            VALIDATOR.profile_packaged_paths(profile, paths),
        )


if __name__ == "__main__":
    unittest.main()
