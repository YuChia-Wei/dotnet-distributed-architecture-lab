#!/usr/bin/env python3
"""Given-When-Then tests for fail-closed AI context package application."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / ".ai/scripts/ai_context_package_apply.py"
SPEC = importlib.util.spec_from_file_location("ai_context_package_apply", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load package apply module: {MODULE_PATH}")
APPLY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = APPLY
SPEC.loader.exec_module(APPLY)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


class PackageApplyFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="ai-context-package-apply-")
        self.root = Path(self._temporary.name)
        self.target = self.root / "target"
        self.package = self.root / "package"
        self.target.mkdir()
        (self.package / "metadata").mkdir(parents=True)
        (self.package / "payload").mkdir()
        git(self.target, "init", "-q")
        git(self.target, "config", "user.name", "Fixture")
        git(self.target, "config", "user.email", "fixture@example.invalid")
        (self.target / "README.md").write_text("fixture\n", encoding="utf-8")
        git(self.target, "add", "README.md")
        git(self.target, "commit", "-qm", "fixture baseline")
        self.previous_path: Path | None = None

    def close(self) -> None:
        self._temporary.cleanup()

    def add_target(self, path: str, content: bytes, executable: bool = False) -> None:
        target = self.target / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        if executable:
            os.chmod(target, 0o755)
        git(self.target, "add", "--", path)
        if executable:
            git(self.target, "update-index", "--chmod=+x", "--", path)

    def commit_target(self, message: str = "target files") -> None:
        git(self.target, "commit", "-qm", message)

    @staticmethod
    def record(
        path: str,
        content: bytes,
        ownership: str = "framework-managed",
        mode: str = "0644",
        component_id: str | None = None,
    ) -> dict:
        record = {
            "path": path,
            "source_path": path,
            "sha256": APPLY.sha256_bytes(content),
            "size": len(content),
            "mode": mode,
            "ownership": ownership,
            "install_behavior": "seed" if ownership == "target-template" else "managed",
            "entry_id": "fixture",
        }
        if component_id is not None:
            record["component_id"] = component_id
        return record

    def reseal(self) -> None:
        checksum_lines = []
        for path in sorted(
            (
                item
                for item in self.package.rglob("*")
                if item.is_file() and item.name != "SHA256SUMS.txt"
            ),
            key=lambda item: item.relative_to(self.package).as_posix().encode("utf-8"),
        ):
            relative = path.relative_to(self.package).as_posix()
            checksum_lines.append(
                f"{APPLY.sha256_bytes(path.read_bytes())}  {relative}\n"
            )
        (self.package / "metadata/SHA256SUMS.txt").write_text(
            "".join(checksum_lines), encoding="utf-8", newline="\n"
        )

    def make_package(
        self,
        incoming: dict[str, tuple[bytes, str, str]],
        operations: list[dict],
        previous: dict[str, tuple[bytes, str, str]] | None = None,
    ) -> None:
        incoming_records = []
        for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
            content, ownership, mode = incoming[path]
            payload = self.package / "payload" / path
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(content)
            incoming_records.append(self.record(path, content, ownership, mode))
        files = {"schema_version": "1.0.0", "package_id": "fixture-v1.0.0", "files": incoming_records}
        files_path = self.package / "metadata/files.yaml"
        files_path.write_text(yaml.safe_dump(files, sort_keys=False), encoding="utf-8", newline="\n")
        previous_sha = None
        previous_version = None
        if previous is not None:
            previous_records = [
                self.record(path, *previous[path])
                for path in sorted(previous, key=lambda item: item.encode("utf-8"))
            ]
            previous_document = {
                "schema_version": "1.0.0",
                "package_id": "fixture-v0.9.0",
                "files": previous_records,
            }
            self.previous_path = self.root / "previous-files.yaml"
            self.previous_path.write_text(
                yaml.safe_dump(previous_document, sort_keys=False), encoding="utf-8", newline="\n"
            )
            previous_sha = APPLY.sha256_bytes(self.previous_path.read_bytes())
            previous_version = "0.9.0"
        package = {"schema_version": "1.0.0", "package_id": "fixture-v1.0.0", "version": "1.0.0"}
        migration = {
            "schema_version": "1.0.0",
            "package_id": "fixture-v1.0.0",
            "from": {"version": previous_version, "manifest_sha256": previous_sha},
            "to": {"version": "1.0.0", "manifest_sha256": APPLY.sha256_bytes(files_path.read_bytes())},
            "operations": operations,
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        (self.package / "metadata/package.yaml").write_text(
            yaml.safe_dump(package, sort_keys=False), encoding="utf-8", newline="\n"
        )
        (self.package / "metadata/migration.yaml").write_text(
            yaml.safe_dump(migration, sort_keys=False), encoding="utf-8", newline="\n"
        )
        self.reseal()

    def plan(self, previous_version: str | None = None) -> dict:
        return APPLY.build_plan(self.package, self.target, self.previous_path, previous_version)

    def make_schema_v2_migration(
        self,
        clean_install_operations: list[dict],
        sources: list[dict],
    ) -> None:
        """Replace the fixture migration with schema v2 and re-seal its envelope."""
        files_path = self.package / "metadata/files.yaml"
        migration = {
            "schema_version": "2.0.0",
            "package_id": "fixture-v1.0.0",
            "to": {"version": "1.0.0", "manifest_sha256": APPLY.sha256_bytes(files_path.read_bytes())},
            "clean_install": {"operations": clean_install_operations},
            "sources": sources,
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        (self.package / "metadata/migration.yaml").write_text(
            yaml.safe_dump(migration, sort_keys=False), encoding="utf-8", newline="\n"
        )
        self.reseal()

    def make_component_package(
        self,
        incoming: dict[str, tuple[bytes, str, str, str]],
        clean_operations: list[dict],
        sources: list[dict] | None = None,
    ) -> None:
        records = []
        for path in sorted(incoming, key=lambda item: item.encode("utf-8")):
            content, ownership, mode, component_id = incoming[path]
            payload = self.package / "payload" / path
            payload.parent.mkdir(parents=True, exist_ok=True)
            payload.write_bytes(content)
            records.append(
                self.record(path, content, ownership, mode, component_id)
            )
        files = {
            "schema_version": "2.0.0",
            "package_id": "fixture-v1.0.0",
            "files": records,
        }
        files_path = self.package / "metadata/files.yaml"
        files_path.write_text(
            yaml.safe_dump(files, sort_keys=False), encoding="utf-8", newline="\n"
        )
        selection = yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION))
        package = {
            "schema_version": "2.0.0",
            "package_id": "fixture-v1.0.0",
            "version": "1.0.0",
            "selection": selection,
        }
        migration = {
            "schema_version": "3.0.0",
            "package_id": "fixture-v1.0.0",
            "selection": selection,
            "to": {
                "version": "1.0.0",
                "manifest_sha256": APPLY.sha256_bytes(files_path.read_bytes()),
            },
            "clean_install": {"operations": clean_operations},
            "sources": sources or [],
            "safety": {
                "dry_run_default": True,
                "clean_worktree_required": True,
                "starting_commit_required": True,
                "abort_on_unacknowledged_reconciliation": True,
            },
        }
        (self.package / "metadata/package.yaml").write_text(
            yaml.safe_dump(package, sort_keys=False), encoding="utf-8", newline="\n"
        )
        (self.package / "metadata/migration.yaml").write_text(
            yaml.safe_dump(migration, sort_keys=False), encoding="utf-8", newline="\n"
        )
        self.reseal()

    def write_provenance(self, enabled: bool) -> None:
        path = self.target / ".dev/ai-context/provenance.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        selection = yaml.safe_load(yaml.safe_dump(APPLY.DEFAULT_COMPONENT_SELECTION))
        selection["providers"]["repo-backlog"]["enabled"] = enabled
        path.write_text(
            yaml.safe_dump(
                {"schema_version": "2.0", "selection": selection}, sort_keys=False
            ),
            encoding="utf-8",
            newline="\n",
        )
        git(self.target, "add", "--", ".dev/ai-context/provenance.yaml")


def operation(
    identifier: str,
    kind: str,
    path: str,
    ownership: str = "framework-managed",
    from_path: str | None = None,
    component_id: str | None = None,
) -> dict:
    preconditions = {
        "add": ["destination_absent"],
        "replace": ["current_sha256_equals_previous_release"],
        "remove": ["current_sha256_equals_previous_release"],
        "rename": ["source_sha256_equals_previous_release", "destination_absent"],
        "reconcile": ["human_acknowledgement"],
    }[kind]
    value = {"id": identifier, "kind": kind, "path": path, "ownership": ownership, "preconditions": preconditions}
    if from_path is not None:
        value["from_path"] = from_path
    if component_id is not None:
        value["component_id"] = component_id
    return value


class AiContextPackageApplyGwtTests(unittest.TestCase):
    def test_gwt_000a_given_component_archive_when_clean_installed_then_default_skips_backlog_and_cli_can_enable_it(self) -> None:
        fixture = PackageApplyFixture()
        try:
            core = operation(
                "001-core",
                "add",
                ".ai/rule.md",
                component_id="software-development-core",
            )
            backlog = operation(
                "002-backlog",
                "add",
                ".dev/backlog/README.MD",
                component_id="repo-backlog",
            )
            fixture.make_component_package(
                {
                    ".ai/rule.md": (
                        b"core\n",
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    ),
                    ".dev/backlog/README.MD": (
                        b"provider\n",
                        "framework-managed",
                        "0644",
                        "repo-backlog",
                    ),
                },
                [core, backlog],
            )

            default_plan = fixture.plan()
            self.assertFalse(
                default_plan["selection"]["providers"]["repo-backlog"]["enabled"]
            )
            self.assertEqual([".ai/rule.md"], [
                item["path"] for item in default_plan["operations"]
            ])
            self.assertEqual(
                {"repo-backlog": 1},
                default_plan["component_operation_counts"]["would_skip"],
            )

            enabled_plan = APPLY.build_plan(
                fixture.package,
                fixture.target,
                enable_providers=["repo-backlog"],
            )
            self.assertEqual(
                [".ai/rule.md", ".dev/backlog/README.MD"],
                [item["path"] for item in enabled_plan["operations"]],
            )
            receipt = APPLY.apply_plan(enabled_plan)
            self.assertEqual(
                "explicit-cli-provider",
                receipt["selection_resolution"]["source"],
            )
            self.assertEqual(
                {"repo-backlog": 1, "software-development-core": 1},
                receipt["component_operation_counts"]["applied"],
            )
        finally:
            fixture.close()

    def test_gwt_000b_given_component_upgrade_without_provenance_when_planned_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            old = b"old\n"
            previous = {
                "schema_version": "2.0.0",
                "package_id": "fixture-v0.9.0",
                "files": [
                    fixture.record(
                        ".ai/rule.md",
                        old,
                        component_id="software-development-core",
                    )
                ],
            }
            fixture.previous_path = fixture.root / "previous-files.yaml"
            fixture.previous_path.write_text(
                yaml.safe_dump(previous, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            source = {
                "version": "0.9.0",
                "manifest_sha256": APPLY.sha256_bytes(
                    fixture.previous_path.read_bytes()
                ),
                "operations": [
                    operation(
                        "001-replace",
                        "replace",
                        ".ai/rule.md",
                        component_id="software-development-core",
                    )
                ],
            }
            fixture.make_component_package(
                {
                    ".ai/rule.md": (
                        b"new\n",
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    )
                },
                [],
                [source],
            )
            fixture.add_target(".ai/rule.md", old)
            fixture.commit_target()
            with self.assertRaisesRegex(
                APPLY.ApplyError, "component-aware upgrade requires"
            ):
                fixture.plan("0.9.0")
        finally:
            fixture.close()

    def test_gwt_000c_given_provenance_disables_provider_when_upgraded_then_all_provider_operations_are_filtered(self) -> None:
        fixture = PackageApplyFixture()
        try:
            previous_records = [
                fixture.record(
                    ".ai/rule.md",
                    b"old\n",
                    component_id="software-development-core",
                ),
                fixture.record(
                    ".dev/backlog/README.MD",
                    b"old provider\n",
                    component_id="repo-backlog",
                ),
            ]
            previous = {
                "schema_version": "2.0.0",
                "package_id": "fixture-v0.9.0",
                "files": sorted(
                    previous_records, key=lambda item: item["path"].encode("utf-8")
                ),
            }
            fixture.previous_path = fixture.root / "previous-files.yaml"
            fixture.previous_path.write_text(
                yaml.safe_dump(previous, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )
            source = {
                "version": "0.9.0",
                "manifest_sha256": APPLY.sha256_bytes(
                    fixture.previous_path.read_bytes()
                ),
                "operations": [
                    operation(
                        "001-core",
                        "replace",
                        ".ai/rule.md",
                        component_id="software-development-core",
                    ),
                    operation(
                        "002-provider",
                        "replace",
                        ".dev/backlog/README.MD",
                        component_id="repo-backlog",
                    ),
                ],
            }
            fixture.make_component_package(
                {
                    ".ai/rule.md": (
                        b"new\n",
                        "framework-managed",
                        "0644",
                        "software-development-core",
                    ),
                    ".dev/backlog/README.MD": (
                        b"new provider\n",
                        "framework-managed",
                        "0644",
                        "repo-backlog",
                    ),
                },
                [],
                [source],
            )
            fixture.add_target(".ai/rule.md", b"old\n")
            fixture.add_target(".dev/backlog/README.MD", b"old provider\n")
            fixture.write_provenance(False)
            fixture.commit_target()
            plan = fixture.plan("0.9.0")
            self.assertEqual([".ai/rule.md"], [
                item["path"] for item in plan["operations"]
            ])
            self.assertEqual(
                {"repo-backlog": 1},
                plan["component_operation_counts"]["would_skip"],
            )
            APPLY.apply_plan(plan)
            self.assertEqual(
                b"old provider\n",
                (fixture.target / ".dev/backlog/README.MD").read_bytes(),
            )
        finally:
            fixture.close()

    def test_gwt_000d_given_legacy_inventory_contains_backlog_when_upgraded_then_provider_is_preserved(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.add_target(".dev/backlog/README.MD", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {
                    ".dev/backlog/README.MD": (
                        b"new\n",
                        "framework-managed",
                        "0644",
                    )
                },
                [
                    operation(
                        "001-provider",
                        "replace",
                        ".dev/backlog/README.MD",
                    )
                ],
                {
                    ".dev/backlog/README.MD": (
                        b"old\n",
                        "framework-managed",
                        "0644",
                    )
                },
            )
            plan = fixture.plan()
            self.assertTrue(
                plan["selection"]["providers"]["repo-backlog"]["enabled"]
            )
            self.assertEqual(
                "legacy-schema1-inventory", plan["selection_resolution"]["source"]
            )
        finally:
            fixture.close()

    def test_gwt_000e_given_dual_provenance_when_planned_then_selection_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            fixture.make_component_package({}, [])
            fixture.write_provenance(False)
            legacy = fixture.target / ".dev/AI-CONTEXT-SOURCE.yaml"
            legacy.write_text('schema_version: "1.0"\n', encoding="utf-8")
            git(fixture.target, "add", "--", ".dev/AI-CONTEXT-SOURCE.yaml")
            fixture.commit_target()
            with self.assertRaisesRegex(APPLY.ApplyError, "cannot coexist"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_000_given_schema_v1_upgrade_envelope_when_exact_previous_manifest_is_supplied_then_reader_compatibility_remains(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a legacy schema v1 package and its governed previous inventory.
            fixture.add_target(".ai/rule.md", b"old\n")
            fixture.commit_target()
            fixture.make_package(
                {".ai/rule.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/rule.md")],
                {".ai/rule.md": (b"old\n", "framework-managed", "0644")},
            )
            # When the schema v1 reader plans without a schema v2 version argument.
            plan = fixture.plan()
            # Then the legacy source identity and operation remain usable.
            self.assertEqual(["replace"], [item["action"] for item in plan["operations"]])
        finally:
            fixture.close()

    def test_gwt_001_given_schema_v2_clean_install_when_planned_without_previous_identity_then_it_uses_clean_operations(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a v2 envelope with an independent clean-install route.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [],
            )
            fixture.make_schema_v2_migration([operation("001-clean", "add", ".ai/rule.md")], [])
            # When no previous inventory or version is supplied.
            plan = fixture.plan()
            # Then the planner selects only the clean-install operation.
            self.assertEqual(["add"], [item["action"] for item in plan["operations"]])
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
        finally:
            fixture.close()

    def test_gwt_002_given_schema_v2_source_when_exact_version_and_sha_match_then_that_source_is_selected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a v2 migration source bound to the governed prior manifest.
            previous = {".ai/rule.md": (b"old\n", "framework-managed", "0644")}
            fixture.add_target(".ai/rule.md", b"old\n")
            fixture.commit_target()
            fixture.make_package({".ai/rule.md": (b"new\n", "framework-managed", "0644")}, [], previous)
            assert fixture.previous_path is not None
            fixture.make_schema_v2_migration(
                [],
                [{
                    "version": "0.9.0",
                    "manifest_sha256": APPLY.sha256_bytes(fixture.previous_path.read_bytes()),
                    "operations": [operation("001-replace", "replace", ".ai/rule.md")],
                }],
            )
            # When the exact source version and manifest are supplied.
            plan = fixture.plan("0.9.0")
            # Then only the matched source is used.
            self.assertEqual(["replace"], [item["action"] for item in plan["operations"]])
        finally:
            fixture.close()

    def test_gwt_003_given_schema_v2_unknown_mismatched_or_duplicate_source_when_planned_then_it_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a v2 package with a governed prior inventory.
            previous = {".ai/rule.md": (b"old\n", "framework-managed", "0644")}
            fixture.make_package({".ai/rule.md": (b"new\n", "framework-managed", "0644")}, [], previous)
            assert fixture.previous_path is not None
            source = {
                "version": "0.9.0",
                "manifest_sha256": APPLY.sha256_bytes(fixture.previous_path.read_bytes()),
                "operations": [operation("001-replace", "replace", ".ai/rule.md")],
            }
            fixture.make_schema_v2_migration([], [source, dict(source)])
            # When the sources are ambiguous, then selection fails before target mutation.
            with self.assertRaisesRegex(APPLY.ApplyError, "duplicate|ambiguous"):
                fixture.plan("0.9.0")

            # Given one source with a different declared identity.
            fixture.make_schema_v2_migration([], [source])
            # When the caller provides an unknown version or a manifest paired with the wrong version.
            with self.assertRaisesRegex(APPLY.ApplyError, "unknown|source"):
                fixture.plan("0.8.0")
            with self.assertRaisesRegex(APPLY.ApplyError, "SHA|source|manifest"):
                wrong_manifest = fixture.root / "not-the-source.yaml"
                wrong_manifest.write_text("files: []\n", encoding="utf-8")
                APPLY.build_plan(fixture.package, fixture.target, wrong_manifest, "0.9.0")
        finally:
            fixture.close()

    def test_gwt_001_given_absent_paths_when_clean_install_is_planned_then_dry_run_binds_without_writes(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a clean committed target and an absent managed path.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            # When a dry-run plan is built.
            plan = fixture.plan()
            # Then it binds package, HEAD, and observations without writing target bytes.
            self.assertEqual("add", plan["operations"][0]["action"])
            self.assertEqual(git(fixture.target, "rev-parse", "HEAD").stdout.strip(), plan["target_starting_commit"])
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
            self.assertFalse((fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").exists())
        finally:
            fixture.close()

    def test_gwt_002_given_existing_seed_when_acknowledged_then_it_is_preserved_and_safe_add_applies(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an existing target-template plus one absent managed path.
            fixture.add_target("AGENTS.md", b"target truth\n")
            fixture.commit_target()
            fixture.make_package(
                {
                    ".ai/rule.md": (b"managed\n", "framework-managed", "0644"),
                    "AGENTS.md": (b"seed\n", "target-template", "0644"),
                },
                [
                    operation("001-managed", "add", ".ai/rule.md"),
                    operation("002-seed", "add", "AGENTS.md", "target-template"),
                ],
            )
            # When the reconcile is acknowledged and the plan is applied.
            plan = fixture.plan()
            with self.assertRaisesRegex(APPLY.ApplyError, "unacknowledged reconciliation"):
                APPLY.apply_plan(plan)
            receipt = APPLY.apply_plan(plan, {"002-seed"})
            # Then acknowledgement skips the seed rather than authorizing overwrite.
            self.assertEqual(b"target truth\n", (fixture.target / "AGENTS.md").read_bytes())
            self.assertEqual(b"managed\n", (fixture.target / ".ai/rule.md").read_bytes())
            self.assertEqual(["002-seed"], receipt["skipped_reconciliation_ids"])
            self.assertFalse((fixture.target / ".dev/AI-CONTEXT-SOURCE.yaml").exists())
            self.assertTrue((fixture.target / ".dev/AI-CONTEXT-APPLY-PENDING.yaml").is_file())
        finally:
            fixture.close()

    def test_gwt_003_given_unchanged_managed_base_when_upgraded_then_replace_remove_and_rename_apply(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given managed target files match the previous hashes and modes.
            fixture.add_target(".ai/replace.md", b"old replace\n")
            fixture.add_target(".ai/remove.md", b"old remove\n")
            fixture.add_target(".ai/old-name.md", b"old name\n")
            fixture.commit_target()
            previous = {
                ".ai/old-name.md": (b"old name\n", "framework-managed", "0644"),
                ".ai/remove.md": (b"old remove\n", "framework-managed", "0644"),
                ".ai/replace.md": (b"old replace\n", "framework-managed", "0644"),
            }
            fixture.make_package(
                {
                    ".ai/new-name.md": (b"renamed incoming\n", "framework-managed", "0644"),
                    ".ai/replace.md": (b"new replace\n", "framework-managed", "0644"),
                },
                [
                    operation("001-rename", "rename", ".ai/new-name.md", from_path=".ai/old-name.md"),
                    operation("002-remove", "remove", ".ai/remove.md"),
                    operation("003-replace", "replace", ".ai/replace.md"),
                ],
                previous,
            )
            # When the upgrade is planned and applied.
            plan = fixture.plan()
            APPLY.apply_plan(plan)
            # Then only explicitly gated operations mutate the managed paths.
            self.assertEqual(["rename", "remove", "replace"], [item["action"] for item in plan["operations"]])
            self.assertFalse((fixture.target / ".ai/old-name.md").exists())
            self.assertFalse((fixture.target / ".ai/remove.md").exists())
            self.assertEqual(b"renamed incoming\n", (fixture.target / ".ai/new-name.md").read_bytes())
            self.assertEqual(b"new replace\n", (fixture.target / ".ai/replace.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_004_given_local_managed_change_when_replace_or_remove_is_planned_then_reconcile_preserves_it(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given committed target content differs from the previous release bytes.
            fixture.add_target(".ai/remove.md", b"local remove override\n")
            fixture.add_target(".ai/replace.md", b"local replace override\n")
            fixture.commit_target()
            previous = {
                ".ai/remove.md": (b"base remove\n", "framework-managed", "0644"),
                ".ai/replace.md": (b"base replace\n", "framework-managed", "0644"),
            }
            fixture.make_package(
                {".ai/replace.md": (b"incoming\n", "framework-managed", "0644")},
                [
                    operation("001-remove", "remove", ".ai/remove.md"),
                    operation("002-replace", "replace", ".ai/replace.md"),
                ],
                previous,
            )
            # When the plan compares current hash and mode to the previous inventory.
            plan = fixture.plan()
            # Then both changes require reconciliation and remain byte-identical after acknowledgement.
            self.assertEqual(["reconcile", "reconcile"], [item["action"] for item in plan["operations"]])
            APPLY.apply_plan(plan, {"001-remove", "002-replace"})
            self.assertEqual(b"local remove override\n", (fixture.target / ".ai/remove.md").read_bytes())
            self.assertEqual(b"local replace override\n", (fixture.target / ".ai/replace.md").read_bytes())
        finally:
            fixture.close()

    def test_gwt_005_given_dirty_or_unborn_target_when_planning_then_git_gate_fails(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a target has an untracked change.
            fixture.make_package({}, [])
            (fixture.target / "dirty.txt").write_text("dirty", encoding="utf-8")
            # When planning starts, then it fails before classification.
            with self.assertRaisesRegex(APPLY.ApplyError, "worktree must be clean"):
                fixture.plan()
            # Given a separate repository has no committed HEAD, when planning starts, then it fails closed.
            unborn = fixture.root / "unborn"
            unborn.mkdir()
            git(unborn, "init", "-q")
            with self.assertRaisesRegex(APPLY.ApplyError, "committed HEAD"):
                APPLY.build_plan(fixture.package, unborn)
        finally:
            fixture.close()

    def test_gwt_006_given_target_changes_after_plan_when_apply_runs_then_stale_plan_is_rejected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a valid plan was created against one clean target state.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            plan = fixture.plan()
            (fixture.target / "later.txt").write_text("changed", encoding="utf-8")
            # When apply rechecks the target, then it rejects the stale plan without writes.
            with self.assertRaisesRegex(APPLY.ApplyError, "worktree must be clean"):
                APPLY.apply_plan(plan)
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
        finally:
            fixture.close()

    def test_gwt_007_given_casefold_collision_when_planning_then_portable_path_safety_fails(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given the target owns a differently cased path.
            fixture.add_target("Rules/Policy.md", b"target\n")
            fixture.commit_target()
            fixture.make_package(
                {"rules/policy.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", "rules/policy.md")],
            )
            # When portable path validation runs, then the case-fold collision is rejected.
            with self.assertRaisesRegex(APPLY.ApplyError, "case-fold collision"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_008_given_symlink_parent_when_planning_then_escape_is_rejected(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a package destination is below a target symlink.
            outside = fixture.root / "outside"
            outside.mkdir()
            try:
                (fixture.target / "linked").symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            git(fixture.target, "add", "linked")
            git(fixture.target, "commit", "-qm", "symlink fixture")
            fixture.make_package(
                {"linked/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", "linked/rule.md")],
            )
            # When planning resolves the path boundary, then it refuses the escape.
            with self.assertRaisesRegex(APPLY.ApplyError, "symlink boundary"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_009_given_mid_apply_failure_when_transaction_aborts_then_all_paths_are_restored(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given two safe additions and a simulated failure on the second write.
            fixture.make_package(
                {
                    ".ai/first.md": (b"first\n", "framework-managed", "0644"),
                    ".ai/second.md": (b"second\n", "framework-managed", "0644"),
                },
                [operation("001-first", "add", ".ai/first.md"), operation("002-second", "add", ".ai/second.md")],
            )
            plan = fixture.plan()
            original = APPLY.write_payload
            calls = 0

            def failing_write(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated write failure")
                return original(*args, **kwargs)

            APPLY.write_payload = failing_write
            # When apply fails midway, then every file and created parent is rolled back.
            try:
                with self.assertRaisesRegex(APPLY.ApplyError, "rolled back"):
                    APPLY.apply_plan(plan)
            finally:
                APPLY.write_payload = original
            self.assertFalse((fixture.target / ".ai").exists())
            self.assertFalse((fixture.target / ".dev").exists())
            self.assertEqual("", git(fixture.target, "status", "--porcelain", "--untracked-files=all").stdout)
        finally:
            fixture.close()

    def test_gwt_010_given_wrong_previous_manifest_when_upgrade_plans_then_identity_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given an upgrade package whose supplied previous manifest changed after migration creation.
            fixture.make_package(
                {".ai/rule.md": (b"new\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/rule.md")],
                {".ai/rule.md": (b"old\n", "framework-managed", "0644")},
            )
            fixture.previous_path.write_text("files: []\n", encoding="utf-8")
            # When planning verifies the previous identity, then it fails before target mutation.
            with self.assertRaisesRegex(APPLY.ApplyError, "previous files manifest SHA"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_011_given_migration_targets_provenance_when_planning_then_reserved_path_fails_closed(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a malicious package attempts to install validated provenance directly.
            path = ".dev/AI-CONTEXT-SOURCE.yaml"
            fixture.make_package(
                {path: (b"source: forged\n", "framework-managed", "0644")},
                [operation("001-forged", "add", path)],
            )
            # When planning validates reserved ownership, then provenance mutation is rejected.
            with self.assertRaisesRegex(APPLY.ApplyError, "cannot manage provenance"):
                fixture.plan()
        finally:
            fixture.close()

    def test_gwt_011a_given_migration_targets_schema_2_context_state_when_planning_then_reserved_paths_fail_closed(self) -> None:
        for path in (
            ".dev/ai-context/provenance.yaml",
            ".dev/ai-context/customizations.yaml",
        ):
            with self.subTest(path=path):
                fixture = PackageApplyFixture()
                try:
                    fixture.make_package(
                        {path: (b"target-owned: true\n", "framework-managed", "0644")},
                        [operation("001-forged", "add", path)],
                    )
                    with self.assertRaisesRegex(APPLY.ApplyError, "cannot manage provenance"):
                        fixture.plan()
                finally:
                    fixture.close()

    def test_gwt_012_given_previous_bytes_match_but_git_mode_differs_when_planned_then_it_reconciles(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given target bytes match the base but the tracked executable mode differs.
            fixture.add_target(".ai/tool.sh", b"same bytes\n", executable=True)
            fixture.commit_target()
            fixture.make_package(
                {".ai/tool.sh": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-replace", "replace", ".ai/tool.sh")],
                {".ai/tool.sh": (b"same bytes\n", "framework-managed", "0644")},
            )
            # When planning compares the governed previous state, then mode drift blocks replacement.
            plan = fixture.plan()
            self.assertEqual("reconcile", plan["operations"][0]["action"])
            self.assertIn("hash or mode", plan["operations"][0]["reason"])
        finally:
            fixture.close()

    def test_gwt_013_given_cli_without_apply_when_executed_then_it_remains_dry_run(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a package with one safe addition and the target CLI entrypoint.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            # When the CLI runs without the explicit --apply flag.
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                    "--package-root",
                    str(fixture.package),
                    "--target-root",
                    str(fixture.target),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            # Then it prints a dry-run plan and leaves the target untouched.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Dry run only", result.stdout)
            self.assertFalse((fixture.target / ".ai/rule.md").exists())
            self.assertEqual("", git(fixture.target, "status", "--porcelain", "--untracked-files=all").stdout)
        finally:
            fixture.close()

    def test_gwt_014_given_plan_output_inside_package_or_target_when_cli_runs_then_it_fails_before_writing(self) -> None:
        fixture = PackageApplyFixture()
        try:
            # Given a valid package and output paths that would invalidate the envelope or clean target.
            fixture.make_package(
                {".ai/rule.md": (b"incoming\n", "framework-managed", "0644")},
                [operation("001-add", "add", ".ai/rule.md")],
            )
            for output in (fixture.package / "plan.yaml", fixture.target / "plan.yaml"):
                # When the CLI is asked to write a plan inside either protected root.
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / ".ai/scripts/plan-ai-context-package-apply.py"),
                        "--package-root",
                        str(fixture.package),
                        "--target-root",
                        str(fixture.target),
                        "--plan-output",
                        str(output),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                # Then it fails closed before creating the ungoverned file.
                self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                self.assertIn("--plan-output must be outside", result.stderr)
                self.assertFalse(output.exists())
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
