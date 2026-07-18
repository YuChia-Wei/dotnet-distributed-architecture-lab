#!/usr/bin/env python3
"""GWT integration tests for deterministic packaging and release workflows."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))
import ai_context_package as PACKAGE  # noqa: E402


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


class SyntheticPackageRepo:
    """Own a minimal Git-backed package source and isolated output roots."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="ai-context-packaging-")
        self.root = Path(self._temporary.name) / "source"
        self.root.mkdir()
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Fixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        (self.root / ".ai/distribution/templates").mkdir(parents=True)
        (self.root / ".ai/distribution/profiles").mkdir(parents=True)
        (self.root / ".ai/scripts").mkdir(parents=True)
        (self.root / "docs").mkdir()
        (self.root / ".ai/distribution/templates/INSTALL.md").write_text(
            "# Install fixture\n", encoding="utf-8", newline="\n"
        )
        (self.root / ".ai/distribution/templates/requirements.txt").write_text(
            "PyYAML==6.0.3\n", encoding="utf-8", newline="\n"
        )
        (self.root / "docs/rule.md").write_text("committed rule\n", encoding="utf-8", newline="\n")
        for script in ("ai_context_package_apply.py", "plan-ai-context-package-apply.py"):
            (self.root / ".ai/scripts" / script).write_bytes((SCRIPTS / script).read_bytes())
        profile = {
            "schema_version": "1.0.0",
            "profile": {"id": "fixture"},
            "package": {
                "source_repository": "fixture/repository",
                "name_template": "fixture-v{version}",
            },
            "reference_integrity": {
                "text_extensions": [".md", ".yaml", ".py"],
                "forbidden_source_lifecycle_patterns": [
                    ".dev/workflows/20*/**",
                    ".dev/assessments/ASM-*/**",
                    ".dev/releases/v*/**",
                    ".dev/backlog/items/**",
                ],
            },
            "entries": [
                {
                    "id": "fixture-docs",
                    "source": "docs/**",
                    "target": "preserve-relative-path",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                },
                {
                    "id": "fixture-apply-scripts",
                    "source": ".ai/scripts/**",
                    "target": "preserve-relative-path",
                    "ownership": "framework-managed",
                    "install_behavior": "managed",
                }
            ],
            "exclusions": [],
        }
        (self.root / ".ai/distribution/profiles/fixture.yaml").write_text(
            yaml.safe_dump(profile, sort_keys=False), encoding="utf-8", newline="\n"
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "fixture package source")
        self.profile = ".ai/distribution/profiles/fixture.yaml"

    def close(self) -> None:
        self._temporary.cleanup()

    def output(self, name: str) -> Path:
        return Path(self._temporary.name) / name

    def build(self, name: str) -> dict[str, Path | str]:
        return PACKAGE.build_package(self.root, "HEAD", "1.0.0", self.output(name), self.profile)


def rewrite_zip_member(source: Path, target: Path, suffix: str, replacement: bytes) -> None:
    with zipfile.ZipFile(source) as archive:
        records = [(info, archive.read(info)) for info in archive.infolist()]
    with zipfile.ZipFile(target, "w") as archive:
        for info, content in records:
            if info.filename.endswith(suffix):
                content = replacement
            copied = zipfile.ZipInfo(info.filename, info.date_time)
            copied.create_system = info.create_system
            copied.external_attr = info.external_attr
            copied.compress_type = info.compress_type
            archive.writestr(copied, content)


class DeterministicPackageGwtTests(unittest.TestCase):
    def test_gwt_001_given_one_immutable_commit_when_built_twice_then_archives_are_byte_identical(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given one immutable package source commit.
            # When independent output directories build the same version.
            first = fixture.build("first")
            second = fixture.build("second")
            # Then each archive format and its sidecar are byte-identical.
            for key in ("zip", "tar_gz"):
                first_path, second_path = Path(first[key]), Path(second[key])
                self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
                self.assertEqual(Path(f"{first_path}.sha256").read_bytes(), Path(f"{second_path}.sha256").read_bytes())
        finally:
            fixture.close()

    def test_gwt_002_given_dirty_checkout_bytes_when_head_is_built_then_git_blob_truth_wins(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given a tracked checkout file differs from its committed Git blob.
            (fixture.root / "docs/rule.md").write_text("dirty checkout\n", encoding="utf-8", newline="\n")
            # When the package is built from HEAD.
            result = fixture.build("dirty")
            members = PACKAGE.validate_archive(Path(result["zip"]))
            # Then the payload contains committed bytes and the checkout stays dirty.
            self.assertEqual(
                b"committed rule\n",
                members["fixture-v1.0.0/payload/docs/rule.md"][0],
            )
            self.assertIn("docs/rule.md", git(fixture.root, "status", "--short").stdout)
        finally:
            fixture.close()

    def test_gwt_003_given_existing_outputs_when_build_repeats_then_overwrite_is_refused(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given the governed archive names already exist after one build.
            fixture.build("existing")
            # When another build targets the same directory, then it fails closed.
            with self.assertRaisesRegex(PACKAGE.PackageError, "refusing to overwrite"):
                fixture.build("existing")
        finally:
            fixture.close()

    def test_gwt_004_given_zip_member_tampering_when_validated_then_checksum_contract_fails(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given a valid package whose payload member is changed without metadata updates.
            result = fixture.build("valid")
            tampered = fixture.output("tampered.zip")
            rewrite_zip_member(Path(result["zip"]), tampered, "payload/docs/rule.md", b"tampered\n")
            # When archive validation recomputes envelope checksums, then it rejects the package.
            with self.assertRaisesRegex(PACKAGE.PackageError, "SHA256SUMS"):
                PACKAGE.validate_archive(tampered)
        finally:
            fixture.close()

    def test_gwt_005_given_zip_and_tar_from_one_build_when_validated_then_payload_and_modes_match(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given both governed archive formats from one build.
            result = fixture.build("parity")
            # When sidecars and archives are validated.
            PACKAGE.validate_sidecar(Path(result["zip"]))
            PACKAGE.validate_sidecar(Path(result["tar_gz"]))
            zip_members = PACKAGE.validate_archive(Path(result["zip"]))
            tar_members = PACKAGE.validate_archive(Path(result["tar_gz"]))
            # Then every member byte and normalized mode is identical by path.
            self.assertEqual(zip_members, tar_members)
        finally:
            fixture.close()

    def test_gwt_006_given_extracted_envelope_when_packaged_planner_runs_then_bytecode_does_not_break_checksums(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given a validated archive extracted beside a clean committed target.
            result = fixture.build("packaged-cli")
            extracted = fixture.output("extracted")
            target = fixture.output("target")
            with zipfile.ZipFile(Path(result["zip"])) as archive:
                archive.extractall(extracted)
            target.mkdir()
            git(target, "init", "-q")
            git(target, "config", "user.name", "Fixture")
            git(target, "config", "user.email", "fixture@example.invalid")
            (target / "baseline.txt").write_text("baseline\n", encoding="utf-8", newline="\n")
            git(target, "add", "baseline.txt")
            git(target, "commit", "-qm", "target baseline")
            package_root = extracted / "fixture-v1.0.0"
            planner = package_root / "payload/.ai/scripts/plan-ai-context-package-apply.py"
            # And the envelope declares the exact target-side dependency.
            self.assertEqual("PyYAML==6.0.3\n", (package_root / "requirements.txt").read_text(encoding="utf-8"))
            missing_dependency = subprocess.run(
                [sys.executable, "-S", str(planner), "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(2, missing_dependency.returncode)
            self.assertIn("pip install -r requirements.txt", missing_dependency.stderr)
            # When the planner imports its packaged helper before checksum validation.
            completed = subprocess.run(
                [sys.executable, str(planner), "--package-root", str(package_root), "--target-root", str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            # Then dry-run succeeds and does not add ungoverned bytecode to the envelope.
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("Dry run only", completed.stdout)
            self.assertFalse(any(package_root.rglob("*.pyc")))
            self.assertFalse(any(package_root.rglob("__pycache__")))
        finally:
            fixture.close()


class ReleaseWorkflowContractGwtTests(unittest.TestCase):
    @staticmethod
    def load(name: str) -> tuple[dict, str]:
        path = ROOT / ".github/workflows" / name
        text = path.read_text(encoding="utf-8")
        document = yaml.load(text, Loader=yaml.BaseLoader)
        if not isinstance(document, dict):
            raise AssertionError(f"workflow root must be a mapping: {name}")
        return document, text

    def test_gwt_007_given_candidate_workflow_when_inspected_then_it_only_builds_read_only_artifacts(self) -> None:
        # Given the candidate packaging workflow.
        workflow, text = self.load("package-candidate.yml")
        # When its triggers, permissions, and commands are inspected.
        triggers = workflow["on"]
        jobs = workflow["jobs"]
        # Then PR/manual execution is read-only and cannot publish or mutate tags.
        self.assertEqual({"pull_request", "workflow_dispatch"}, set(triggers))
        self.assertEqual({}, workflow["permissions"])
        self.assertEqual({"contents": "read"}, jobs["package"]["permissions"])
        self.assertIn("actions/upload-artifact@", text)
        self.assertNotIn("gh release", text)
        self.assertNotRegex(text, r"(?m)^\s*(?:git\s+(?:tag|push|update-ref)|gh\s+api\s+.*git/refs)\b")

    def test_gwt_008_given_publish_workflow_when_inspected_then_only_user_tags_authorize_release_writes(self) -> None:
        # Given the release publication workflow.
        workflow, text = self.load("publish-release.yml")
        # When its tag trigger and job permissions are inspected.
        jobs = workflow["jobs"]
        # Then only pushed v-tags trigger it and contents:write is isolated to publish.
        self.assertEqual(["v*"], workflow["on"]["push"]["tags"])
        self.assertEqual({}, workflow["permissions"])
        self.assertEqual({"contents": "read"}, jobs["build"]["permissions"])
        self.assertEqual({"contents": "write"}, jobs["publish"]["permissions"])
        self.assertEqual("ai-context-release", jobs["publish"]["environment"])
        self.assertIn(r"^v[0-9]+\.[0-9]+\.[0-9]+$", text)
        self.assertIn('--ref "refs/tags/${GITHUB_REF_NAME}"', text)

    def test_gwt_009_given_publish_commands_when_inspected_then_draft_precedes_publish_and_tags_never_mutate(self) -> None:
        # Given the commands used to create, verify, and publish a release.
        _, text = self.load("publish-release.yml")
        # When mutation boundaries and ordering are inspected.
        draft_position = text.find("gh release create")
        publish_position = text.find("--draft=false")
        # Then an owned draft is created/resumed before publication, while Git refs remain read-only.
        self.assertGreaterEqual(draft_position, 0)
        self.assertGreater(publish_position, draft_position)
        self.assertIn("gh release view", text)
        self.assertIn("ai-context-release-automation:", text)
        self.assertNotRegex(text, r"(?m)^\s*(?:git\s+(?:tag|push|update-ref)|gh\s+api\s+.*git/refs)\b")


class PayloadReferenceIntegrityGwtTests(unittest.TestCase):
    def test_gwt_010_given_packaged_text_links_excluded_source_workflow_when_built_then_it_fails_closed(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given an allowlisted Markdown file links to a concrete excluded source workflow instance.
            (fixture.root / "docs/rule.md").write_text(
                "See `.dev/workflows/2026-05-source-only/report.md`.\n",
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "add forbidden source backlink")
            # When the deterministic builder validates payload references.
            # Then it rejects the backlink even though the referring file itself is allowlisted.
            with self.assertRaisesRegex(PACKAGE.PackageError, "excluded source lifecycle"):
                fixture.build("forbidden-reference")
        finally:
            fixture.close()

    def test_gwt_011_given_generic_lifecycle_placeholders_when_built_then_they_remain_portable(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            # Given portable documentation uses placeholders and globs rather than a source instance.
            (fixture.root / "docs/rule.md").write_text(
                "Use `.dev/workflows/<workflow-id>/report.md` and `.dev/backlog/items/*.yaml`.\n",
                encoding="utf-8",
                newline="\n",
            )
            git(fixture.root, "add", "docs/rule.md")
            git(fixture.root, "commit", "-qm", "add portable lifecycle placeholders")
            # When the package is built, then generic target-side contracts remain valid.
            result = fixture.build("portable-placeholders")
            self.assertTrue(Path(result["zip"]).is_file())
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
