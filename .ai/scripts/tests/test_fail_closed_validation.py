#!/usr/bin/env python3
"""GWT regression tests for fail-closed shell asset validation.

These tests intentionally operate only on synthetic Git repositories. They
must never change executable modes, index entries, or files in the real repo.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_SOURCE = REPO_ROOT / ".ai/scripts/validate-shell-assets.py"
RUNNER_SOURCE = REPO_ROOT / ".ai/scripts/check-all.sh"
TEST_COMPLIANCE_SOURCE = REPO_ROOT / ".ai/scripts/check-test-compliance.sh"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def real_repo_snapshot() -> tuple[str, str, str]:
    head = run(["git", "rev-parse", "HEAD"], REPO_ROOT)
    status = run(["git", "status", "--porcelain=v1"], REPO_ROOT)
    shell_stage = run(
        ["git", "ls-files", "--stage", "*.sh"],
        REPO_ROOT,
    )
    for result in (head, status, shell_stage):
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
    return head.stdout, status.stdout, shell_stage.stdout


def bash_executable() -> str | None:
    if os.name == "nt":
        candidates = (
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Git/bin/bash.exe",
        )
        return next((str(candidate) for candidate in candidates if candidate.is_file()), None)
    return shutil.which("bash")


class SyntheticShellAssetRepo:
    """Own a disposable repository whose shape matches validator assumptions."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="aic007-shell-assets-")
        self.root = Path(self._temporary.name)
        self.scripts = self.root / ".ai/scripts"
        self.scripts.mkdir(parents=True)
        shutil.copy2(VALIDATOR_SOURCE, self.scripts / VALIDATOR_SOURCE.name)
        initialized = run(["git", "init", "--quiet"], self.root)
        if initialized.returncode != 0:
            self.close()
            raise RuntimeError(initialized.stderr.strip())

    def close(self) -> None:
        self._temporary.cleanup()

    def add_shell(self, name: str, mode: str = "100755") -> str:
        relative = f".ai/scripts/{name}"
        path = self.root / relative
        path.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8", newline="\n")
        added = run(["git", "add", "--", relative], self.root)
        self._require_success(added)
        mode_flag = "+x" if mode == "100755" else "-x"
        updated = run(["git", "update-index", f"--chmod={mode_flag}", "--", relative], self.root)
        self._require_success(updated)
        return relative

    def add_runner(self, required_children: list[str]) -> str:
        runner = ".ai/scripts/check-all.sh"
        body = ["#!/bin/bash"]
        for child in required_children:
            body.extend(
                (
                    f'run_check "{child}" \\',
                    f'    "Fixture {child}" \\',
                    '    "required" "true" "true"',
                )
            )
        (self.root / runner).write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
        added = run(["git", "add", "--", runner], self.root)
        self._require_success(added)
        updated = run(["git", "update-index", "--chmod=+x", "--", runner], self.root)
        self._require_success(updated)
        return runner

    def add_command_runner(self, required_commands: list[str]) -> str:
        runner = ".ai/scripts/check-all.sh"
        body = ["#!/bin/bash"]
        for command in required_commands:
            body.extend(
                (
                    f'run_command_check "{command}" \\',
                    f'    "Fixture {command}" \\',
                    '    "required" "true" "true"',
                )
            )
        (self.root / runner).write_text("\n".join(body) + "\n", encoding="utf-8", newline="\n")
        added = run(["git", "add", "--", runner], self.root)
        self._require_success(added)
        updated = run(["git", "update-index", "--chmod=+x", "--", runner], self.root)
        self._require_success(updated)
        return runner

    def write_manifest(
        self,
        *,
        retained: list[str],
        retirement_candidates: list[str] | None = None,
        required_entrypoints: list[str] | None = None,
        check_all_required_scripts: list[str] | None = None,
        check_all_required_commands: list[str] | None = None,
    ) -> None:
        assets = [
            {
                "path": path,
                "role": "context-validator",
                "lifecycle": "active",
                "distribution": "packaged",
                "authority": "structural",
                "replacement": None,
            }
            for path in retained
        ]
        assets.extend(
            {
                "path": path,
                "role": "transitional-helper",
                "lifecycle": "retirement-candidate",
                "distribution": "packaged",
                "authority": "advisory",
                "replacement": "fixture replacement",
            }
            for path in (retirement_candidates or [])
        )
        manifest = {
            "schema_version": "2.0",
            "contract": {
                "distribution_rule": "fixture distribution rule",
                "authority_rule": "fixture authority rule",
            },
            "assets": assets,
            "required_entrypoints": required_entrypoints or [],
            "check_all_required_scripts": check_all_required_scripts or [],
            "check_all_required_commands": check_all_required_commands or [],
        }
        (self.scripts / "shell-assets.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )

    def validate(self) -> subprocess.CompletedProcess[str]:
        return run([sys.executable, str(self.scripts / VALIDATOR_SOURCE.name)], self.root)

    @staticmethod
    def _require_success(result: subprocess.CompletedProcess[str]) -> None:
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())


class SyntheticRunnerRepo:
    """Run an unmodified copied check-all.sh against deterministic stubs."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="aic007-check-all-")
        self.root = Path(self._temporary.name)
        self.scripts = self.root / ".ai/scripts"
        self.bin = self.root / "bin"
        self.scripts.mkdir(parents=True)
        self.bin.mkdir()
        shutil.copy2(RUNNER_SOURCE, self.scripts / RUNNER_SOURCE.name)
        self.add_python_stub("python")
        self._write_stub(self.bin / "dotnet", 'printf "dotnet %s\\n" "$*" >> .aic-sentinel\nexit "${DOTNET_STUB_EXIT:-0}"')
        self._write_child("check-coding-standards.sh", "CODING_STUB_EXIT")
        self._write_child("check-spec-compliance.sh", "SPEC_STUB_EXIT")

    def close(self) -> None:
        self._temporary.cleanup()

    def remove_child(self, name: str) -> None:
        (self.scripts / name).unlink()

    def add_python_stub(self, name: str) -> None:
        self._write_stub(
            self.bin / name,
            f'printf "{name} %s\\n" "$*" >> .aic-sentinel\nexit "${{PYTHON_STUB_EXIT:-0}}"',
        )

    def enable_source_release_context(self) -> None:
        (self.root / ".dev/releases").mkdir(parents=True)
        (self.root / ".ai/distribution").mkdir(parents=True)
        (self.scripts / "ai_context_package.py").write_text(
            "# source-only package builder marker\n",
            encoding="utf-8",
            newline="\n",
        )

    def enable_source_governance_context(self) -> None:
        workflow = self.root / ".github/workflows/governance.yml"
        registry = self.root / ".ai/distribution/governance-checks.yaml"
        validator = self.scripts / "validate-source-governance.py"
        workflow.parent.mkdir(parents=True)
        registry.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("# source-only governance workflow marker\n", encoding="utf-8")
        registry.write_text("# source-only governance registry marker\n", encoding="utf-8")
        validator.write_text("# source-only governance validator marker\n", encoding="utf-8")

    def execute(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        bash = bash_executable()
        if not bash:
            raise unittest.SkipTest("Bash is required for check-all.sh fixture tests")
        merged_environment = dict(os.environ)
        merged_environment["PATH"] = str(self.bin) + os.pathsep + merged_environment["PATH"]
        merged_environment.pop("SPEC_FILE", None)
        merged_environment.pop("TASK_NAME", None)
        merged_environment.pop("COMMIT_RANGE", None)
        merged_environment.pop("WORKFLOW_ID", None)
        merged_environment.pop("AI_CONTEXT_PYTHON", None)
        if environment:
            merged_environment.update(environment)
        return subprocess.run(
            [bash, str(self.scripts / RUNNER_SOURCE.name), *arguments],
            cwd=self.root,
            env=merged_environment,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def sentinel(self) -> list[str]:
        path = self.root / ".aic-sentinel"
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def _write_child(self, name: str, exit_variable: str) -> None:
        self._write_stub(
            self.scripts / name,
            f'printf "{name} %s\\n" "$*" >> .aic-sentinel\nexit "${{{exit_variable}:-0}}"',
        )

    @staticmethod
    def _write_stub(path: Path, body: str) -> None:
        path.write_text(f"#!/bin/bash\n{body}\n", encoding="utf-8", newline="\n")
        path.chmod(0o755)


class CheckAllRunnerGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_before = real_repo_snapshot()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.real_before != real_repo_snapshot():
            raise AssertionError("check-all fixture tests mutated the real repository")

    def test_gwt_001_given_required_script_missing_when_critical_runs_then_gate_fails(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the selected required child script is absent.
            fixture.remove_child("check-coding-standards.sh")

            # When critical mode executes the copied runner.
            result = fixture.execute("--critical")

            # Then the aggregate fails and records an unexecuted required check.
            self.assertEqual(1, result.returncode)
            self.assertIn("FAILED", result.stdout)
            self.assertIn("check-coding-standards.sh not found", result.stdout)
            self.assertIn("Required Selected:", result.stdout)
            self.assertIn("Required Executed:", result.stdout)
            self.assertIn("Required Failed:", result.stdout)
        finally:
            fixture.close()

    def test_gwt_003_given_required_script_nonzero_when_selected_then_counted_once(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the required coding check returns 17.
            # When critical mode executes.
            result = fixture.execute("--critical", environment={"CODING_STUB_EXIT": "17"})

            # Then the aggregate fails exactly one required check.
            self.assertEqual(1, result.returncode)
            self.assertIn("Coding Standards Structural Integrity returned non-zero", result.stdout)
            self.assertRegex(result.stdout, r"Required Failed: .*1")
        finally:
            fixture.close()

    def test_gwt_004_given_required_command_unavailable_when_selected_then_gate_fails(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given deterministic dotnet command stubs return command-not-found semantics.
            # When critical mode executes all required dotnet checks.
            result = fixture.execute("--critical", environment={"DOTNET_STUB_EXIT": "127"})

            # Then all three selected command checks fail without workstation dependency.
            self.assertEqual(1, result.returncode)
            self.assertRegex(result.stdout, r"Required Failed: .*3")
            self.assertEqual(3, sum(line.startswith("dotnet ") for line in fixture.sentinel()))
        finally:
            fixture.close()

    def test_gwt_005_given_retirement_candidate_when_modes_run_then_it_is_never_selected(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the stale helper is a packaged retirement candidate.
            # When every supported mode executes.
            results = (
                fixture.execute("--critical"),
                fixture.execute("--quick"),
                fixture.execute("--full"),
            )

            # Then no aggregate mode routes to its obsolete policy.
            for result in results:
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertNotIn("Test Standards Compliance", result.stdout)
                self.assertRegex(result.stdout, r"Advisory Warnings: .*0")
        finally:
            fixture.close()

    def test_gwt_006_given_no_spec_inputs_when_quick_runs_then_spec_is_not_applicable(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given both conditional spec inputs and source release context are absent.
            # When quick mode reaches spec compliance.
            result = fixture.execute("--quick")

            # Then target-inapplicable checks and optional inputs record N/A without failing.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("source release context not packaged", result.stdout)
            self.assertIn("source package builder not packaged", result.stdout)
            self.assertIn("source governance registry not packaged", result.stdout)
            self.assertIn("source CI workflow not packaged", result.stdout)
            self.assertRegex(result.stdout, r"Not Applicable: .*6")
            self.assertRegex(result.stdout, r"Required Failed: .*0")
            self.assertFalse(
                any(
                    "test_ai_context_version_governance.py" in line
                    or "test_ai_context_packaging.py" in line
                    or "validate-source-governance.py" in line
                    or "test_governance_workflow_contract.py" in line
                    for line in fixture.sentinel()
                )
            )
        finally:
            fixture.close()

    def test_gwt_007_given_partial_spec_inputs_when_quick_runs_then_configuration_fails(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            for environment in ({"SPEC_FILE": "spec.json"}, {"TASK_NAME": "task"}):
                with self.subTest(environment=environment):
                    # Given exactly one conditional-required input is present.
                    # When quick mode reaches spec compliance.
                    result = fixture.execute("--quick", environment=environment)

                    # Then configuration fails before the spec child launches.
                    self.assertEqual(1, result.returncode)
                    self.assertIn("requires both SPEC_FILE and TASK_NAME", result.stdout)
                    self.assertFalse(
                        any(line.startswith("check-spec-compliance.sh") for line in fixture.sentinel())
                    )
        finally:
            fixture.close()

    def test_gwt_007a_given_source_governance_paths_without_release_context_then_checks_are_not_applicable(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given a downstream happens to retain the two source governance paths.
            fixture.enable_source_governance_context()

            # When the critical gate runs without source release/build identity.
            result = fixture.execute("--critical")

            # Then source-pinned Git/tag validation remains not applicable.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("source governance registry not packaged", result.stdout)
            self.assertFalse(
                any(
                    "validate-source-governance.py" in line
                    or "test_governance_workflow_contract.py" in line
                    for line in fixture.sentinel()
                )
            )
        finally:
            fixture.close()

    def test_gwt_008_given_complete_spec_inputs_when_quick_runs_then_child_result_is_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            base = {"SPEC_FILE": "spec.json", "TASK_NAME": "task"}
            # Given both inputs exist, when the spec child passes, then the gate passes.
            passing = fixture.execute("--quick", environment=base)
            self.assertEqual(0, passing.returncode, passing.stdout + passing.stderr)

            # Given both inputs exist, when the spec child fails, then the gate fails.
            failing = fixture.execute("--quick", environment={**base, "SPEC_STUB_EXIT": "4"})
            self.assertEqual(1, failing.returncode)
            self.assertIn("Spec Implementation Compliance (.NET) returned non-zero", failing.stdout)
        finally:
            fixture.close()

    def test_gwt_009_given_dependency_gate_when_quick_runs_then_it_is_required_not_deferred(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the offline dependency validator and its fixtures are declared required.
            # When quick mode reaches the dependency gate.
            result = fixture.execute("--quick")

            # Then both commands execute and no dependency deferral remains.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("DEFERRED: Dependencies and Versions", result.stdout)
            self.assertIn("Offline Dependency And Version Consistency", result.stdout)
            self.assertIn("Dependency And Version Consistency Fail-Closed Tests", result.stdout)
            self.assertTrue(
                any("validate-dependency-versions.py" in line for line in fixture.sentinel())
            )
            self.assertTrue(
                any("test_dependency_version_consistency.py" in line for line in fixture.sentinel())
            )
            self.assertRegex(result.stdout, r"Deferred: .*0")
            self.assertRegex(result.stdout, r"Required Failed: .*0")
        finally:
            fixture.close()

    def test_gwt_009_language_gate_when_quick_runs_then_it_is_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the language and bilingual parity fixtures are a required gate.
            # When quick mode reaches the AI context validators.
            result = fixture.execute("--quick")

            # Then the language suite executes and remains fail closed.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "AI Context Language And Bilingual Parity Fail-Closed Tests",
                result.stdout,
            )
            self.assertTrue(
                any(
                    "test_ai_context_language_policy.py -v" in line
                    for line in fixture.sentinel()
                )
            )
            self.assertRegex(result.stdout, r"Required Failed: .*0")
        finally:
            fixture.close()

    def test_gwt_010_given_modes_when_each_runs_then_selection_and_default_are_truthful(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given identical passing stubs, when each supported mode executes.
            critical = fixture.execute("--critical")
            quick = fixture.execute("--quick")
            full = fixture.execute("--full")
            default = fixture.execute()

            # Then all pass, mode labels are truthful, and default selects full behavior.
            for result in (critical, quick, full, default):
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("Mode: ", critical.stdout)
            self.assertIn("critical", critical.stdout)
            self.assertIn("quick", quick.stdout)
            self.assertIn("full", full.stdout)
            self.assertEqual(
                [line for line in full.stdout.splitlines() if "Running:" in line],
                [line for line in default.stdout.splitlines() if "Running:" in line],
            )
            self.assertNotIn("Test Standards Compliance", critical.stdout)
            self.assertNotIn("Test Standards Compliance", quick.stdout)
            self.assertNotIn("Test Standards Compliance", full.stdout)
        finally:
            fixture.close()

    def test_gwt_011_given_invalid_cli_when_runner_starts_then_no_check_launches(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given invalid arguments, when the runner parses them.
            unknown = fixture.execute("--unknown")
            extra = fixture.execute("--quick", "--full")
            help_result = fixture.execute("--help")

            # Then invalid forms exit 2, help exits 0, and no checks launch.
            self.assertEqual(2, unknown.returncode)
            self.assertEqual(2, extra.returncode)
            self.assertEqual(0, help_result.returncode)
            self.assertIn("Usage:", unknown.stderr)
            self.assertIn("Usage:", extra.stderr)
            self.assertIn("Usage:", help_result.stdout)
            self.assertEqual([], fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_012_given_source_release_context_when_critical_runs_then_source_tests_are_required(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the runner can prove it is executing in the source release repository.
            fixture.enable_source_release_context()
            fixture.enable_source_governance_context()

            # When the critical gate executes.
            result = fixture.execute("--critical")

            # Then both source-only suites and the downstream-safe apply suite execute.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            commands = fixture.sentinel()
            self.assertTrue(
                any("test_ai_context_version_governance.py -v" in line for line in commands)
            )
            self.assertTrue(any("test_ai_context_packaging.py -v" in line for line in commands))
            self.assertTrue(
                any("validate-source-governance.py" in line for line in commands)
            )
            self.assertTrue(
                any("test_governance_workflow_contract.py -v" in line for line in commands)
            )
            self.assertTrue(
                any("test_ai_context_package_apply.py -v" in line for line in commands)
            )
            self.assertNotIn("source release context not packaged", result.stdout)
            self.assertNotIn("source governance registry not packaged", result.stdout)
        finally:
            fixture.close()

    def test_gwt_013_given_explicit_python3_when_critical_runs_then_runner_uses_it(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the host selects a usable python3 executable explicitly.
            fixture.add_python_stub("python3")

            # When the critical gate executes with the supported override.
            result = fixture.execute(
                "--critical",
                environment={"AI_CONTEXT_PYTHON": "python3"},
            )

            # Then required Python commands use that interpreter and the gate passes.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(
                any(line.startswith("python3 ") for line in fixture.sentinel())
            )
        finally:
            fixture.close()

    def test_gwt_014_given_explicit_python_missing_when_gate_starts_then_it_fails_closed(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given an explicit interpreter selection cannot be resolved.
            # When the critical gate starts.
            result = fixture.execute(
                "--critical",
                environment={"AI_CONTEXT_PYTHON": "missing-aic-python"},
            )

            # Then the runner fails before launching any required check.
            self.assertEqual(1, result.returncode)
            self.assertIn("Python 3.11 or newer is required", result.stderr)
            self.assertEqual([], fixture.sentinel())
        finally:
            fixture.close()

    def test_gwt_015_given_parent_python_override_when_fixture_runs_then_path_stub_remains_authoritative(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the host exports a real interpreter for its outer gate.
            with mock.patch.dict(
                os.environ,
                {"AI_CONTEXT_PYTHON": sys.executable},
            ):
                # When a synthetic fixture runs without its own explicit override.
                result = fixture.execute("--quick")

            # Then the fixture isolates the host override and retains its PATH stub.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(
                any(line.startswith("python ") for line in fixture.sentinel())
            )
        finally:
            fixture.close()


class AdvisoryRootResolutionGwtTests(unittest.TestCase):
    def test_gwt_001_given_retained_script_when_run_from_ai_scripts_then_repo_src_is_scanned(self) -> None:
        bash = bash_executable()
        if not bash:
            raise unittest.SkipTest("Bash is required for advisory path fixture tests")

        with tempfile.TemporaryDirectory(prefix="aic005-test-root-") as temporary:
            # Given the retained script is at .ai/scripts and a repository test exists.
            root = Path(temporary)
            scripts = root / ".ai/scripts"
            target = root / "src/Example/Tests/SampleTest.cs"
            scripts.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            script = scripts / TEST_COMPLIANCE_SOURCE.name
            shutil.copy2(TEST_COMPLIANCE_SOURCE, script)
            script.chmod(0o755)
            target.write_text(
                "// Gherkin-style sample\npublic sealed class SampleTest { }\n",
                encoding="utf-8",
                newline="\n",
            )
            environment = dict(os.environ)
            if os.name == "nt":
                git_usr_bin = Path(bash).parent.parent / "usr/bin"
                environment["PATH"] = (
                    str(git_usr_bin) + os.pathsep + environment["PATH"]
                )

            # When the advisory helper resolves its repository root.
            result = subprocess.run(
                [bash, str(script)],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # Then it scans the repository src tree instead of the repository parent.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn("No target files found", result.stdout)
            self.assertIn("All checks passed", result.stdout)


class ShellAssetValidationGwtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.real_before = real_repo_snapshot()

    @classmethod
    def tearDownClass(cls) -> None:
        # Then the real checkout HEAD, status, and shell index are unchanged.
        cls.real_after = real_repo_snapshot()
        if cls.real_before != cls.real_after:
            raise AssertionError("synthetic fixture tests mutated the real repository")

    def test_gwt_002_given_tracked_asset_mode_100644_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        fixture_root = fixture.root
        try:
            # Given a classified shell tracked with Git mode 100644.
            script = fixture.add_shell("required.sh", mode="100644")
            fixture.write_manifest(retained=[script], required_entrypoints=[script])

            # When shell asset validation runs against the synthetic index.
            result = fixture.validate()

            # Then index truth rejects the path regardless of host executability.
            self.assertEqual(1, result.returncode)
            self.assertIn(script, result.stdout)
            self.assertIn("tracked shell asset must use Git mode 100755, found 100644", result.stdout)
        finally:
            fixture.close()
        self.assertFalse(fixture_root.exists())

    def test_gwt_012_given_manifest_coverage_mismatch_when_validated_then_lists_both_sides(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given one unclassified tracked shell and one nonexistent manifest path.
            classified = fixture.add_shell("classified.sh")
            missing = fixture.add_shell("missing-from-manifest.sh")
            extra = ".ai/scripts/extra-in-manifest.sh"
            fixture.write_manifest(retained=[classified, extra])

            # When shell asset validation compares manifest and index coverage.
            result = fixture.validate()

            # Then it fails with deterministic missing and extra lists.
            self.assertEqual(1, result.returncode)
            self.assertIn(f"missing=['{missing}']", result.stdout)
            self.assertIn(f"extra=['{extra}']", result.stdout)
        finally:
            fixture.close()

    def test_gwt_013_given_invalid_asset_records_when_validated_then_invariants_fail(self) -> None:
        cases = (
            ("overlap", ["assets contains duplicate path"]),
            ("duplicate", ["assets contains duplicate path"]),
            ("required-outside", ["required_entrypoints contains non-runnable lifecycle path"]),
        )
        for case, messages in cases:
            with self.subTest(case=case):
                fixture = SyntheticShellAssetRepo()
                try:
                    # Given a manifest violating one asset-record invariant.
                    retained = fixture.add_shell("retained.sh")
                    outside = fixture.add_shell("outside.sh")
                    if case == "overlap":
                        fixture.write_manifest(
                            retained=[retained, outside],
                            retirement_candidates=[retained],
                        )
                    elif case == "duplicate":
                        fixture.write_manifest(
                            retained=[retained, retained],
                            retirement_candidates=[outside],
                        )
                    else:
                        fixture.write_manifest(
                            retained=[retained],
                            retirement_candidates=[outside],
                            required_entrypoints=[outside],
                        )

                    # When shell asset validation checks role and lifecycle ownership.
                    result = fixture.validate()

                    # Then the matching invariant is reported as a failure.
                    self.assertEqual(1, result.returncode)
                    for message in messages:
                        self.assertIn(message, result.stdout)
                finally:
                    fixture.close()

    def test_gwt_014_given_valid_manifest_when_validated_then_counts_and_exit_pass(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given complete classification, executable active paths, and valid subsets.
            entrypoint = fixture.add_shell("entrypoint.sh")
            child = fixture.add_shell("child.sh")
            fixture.write_manifest(
                retained=[entrypoint, child],
                required_entrypoints=[entrypoint],
                check_all_required_scripts=[child],
            )

            # When shell asset validation runs.
            result = fixture.validate()

            # Then it passes with truthful role, lifecycle, and tracked counts.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("passed for 2 tracked asset(s)", result.stdout)
            self.assertIn("'active': 2", result.stdout)
            self.assertIn("'context-validator': 2", result.stdout)
        finally:
            fixture.close()

    def test_gwt_017_given_transitional_asset_without_replacement_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given a transitional helper that omits its replacement direction.
            script = fixture.add_shell("transitional.sh")
            fixture.write_manifest(retained=[script])
            manifest_path = fixture.scripts / "shell-assets.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"][0].update(
                {
                    "role": "transitional-helper",
                    "lifecycle": "transitional",
                    "authority": "advisory",
                    "replacement": None,
                }
            )
            manifest_path.write_text(
                yaml.safe_dump(manifest, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )

            # When lifecycle validation runs.
            result = fixture.validate()

            # Then packaging retention cannot hide an unspecified replacement.
            self.assertEqual(1, result.returncode)
            self.assertIn("replacement is required for non-active lifecycle", result.stdout)
        finally:
            fixture.close()

    def test_gwt_019_given_deprecated_helper_with_replacement_when_validated_then_passes(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given a deprecated-in-place helper with an explicit replacement.
            script = fixture.add_shell("deprecated.sh")
            fixture.write_manifest(retained=[script])
            manifest_path = fixture.scripts / "shell-assets.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["assets"][0].update(
                {
                    "role": "transitional-helper",
                    "lifecycle": "deprecated",
                    "authority": "advisory",
                    "replacement": "Use the compiled validator.",
                }
            )
            manifest_path.write_text(
                yaml.safe_dump(manifest, sort_keys=False),
                encoding="utf-8",
                newline="\n",
            )

            # When lifecycle validation runs, then explicit deprecation is valid.
            result = fixture.validate()
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("'deprecated': 1", result.stdout)
        finally:
            fixture.close()

    def test_given_required_runner_child_omitted_when_validated_then_parity_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given the runner has two required children but the manifest declares one.
            coding = fixture.add_shell("check-coding-standards.sh")
            spec = fixture.add_shell("check-spec-compliance.sh")
            runner = fixture.add_runner(["check-coding-standards.sh", "check-spec-compliance.sh"])
            fixture.write_manifest(
                retained=[runner, coding, spec],
                required_entrypoints=[runner],
                check_all_required_scripts=[coding],
            )

            # When runner declarations and manifest ownership are compared.
            result = fixture.validate()

            # Then the undeclared conditional-required child blocks validation.
            self.assertEqual(1, result.returncode)
            self.assertIn("check_all required-script coverage mismatch", result.stdout)
            self.assertIn(f"missing=['{spec}']", result.stdout)
        finally:
            fixture.close()

    def test_gwt_016_given_required_command_omitted_when_validated_then_parity_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given the runner invokes two literal required commands but declares one.
            runner = fixture.add_command_runner(["python first.py", "python second.py"])
            fixture.write_manifest(
                retained=[runner],
                required_entrypoints=[runner],
                check_all_required_commands=["python first.py"],
            )

            # When aggregate command registration is compared by set.
            result = fixture.validate()

            # Then the missing command fails closed without relying on a fixed count.
            self.assertEqual(1, result.returncode)
            self.assertIn("check_all required-command coverage mismatch", result.stdout)
            self.assertIn("python second.py", result.stdout)
        finally:
            fixture.close()

    def test_gwt_018_given_required_command_format_changes_when_validated_then_parity_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        try:
            # Given the manifest owns one command but the runner call no longer
            # follows the retained literal multiline format.
            runner = fixture.add_command_runner(["python first.py"])
            fixture.write_manifest(
                retained=[runner],
                required_entrypoints=[runner],
                check_all_required_commands=["python first.py"],
            )
            (fixture.root / runner).write_text(
                "#!/bin/bash\n"
                'run_command_check "python first.py" "Fixture" "required" "true" "true"\n',
                encoding="utf-8",
                newline="\n",
            )

            # When the shell registry validator compares the retained grammar.
            result = fixture.validate()

            # Then formatting drift fails closed rather than silently removing
            # a required command from the governed set.
            self.assertEqual(1, result.returncode)
            self.assertIn("check_all required-command coverage mismatch", result.stdout)
            self.assertIn("extra=['python first.py']", result.stdout)
        finally:
            fixture.close()

    def test_gwt_015_given_failed_fixture_when_cleaned_then_real_repo_and_temp_root_are_safe(self) -> None:
        # Given a real-repository snapshot and a synthetic failing fixture.
        real_before = real_repo_snapshot()
        fixture = SyntheticShellAssetRepo()
        fixture_root = fixture.root
        script = fixture.add_shell("non-executable.sh", mode="100644")
        fixture.write_manifest(retained=[script])

        # When validation fails and fixture cleanup runs through finally.
        try:
            result = fixture.validate()
            self.assertEqual(1, result.returncode)
        finally:
            fixture.close()

        # Then temporary state is removed and the real Git state is unchanged.
        self.assertFalse(fixture_root.exists())
        self.assertEqual(real_before, real_repo_snapshot())


if __name__ == "__main__":
    unittest.main()
