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

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_SOURCE = REPO_ROOT / ".ai/scripts/validate-shell-assets.py"
RUNNER_SOURCE = REPO_ROOT / ".ai/scripts/check-all.sh"


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

    def write_manifest(
        self,
        *,
        retained: list[str],
        retirement_candidates: list[str] | None = None,
        required_entrypoints: list[str] | None = None,
        check_all_required_scripts: list[str] | None = None,
    ) -> None:
        manifest = {
            "schema_version": "1.0",
            "retained": retained,
            "retirement_candidates": retirement_candidates or [],
            "required_entrypoints": required_entrypoints or [],
            "check_all_required_scripts": check_all_required_scripts or [],
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
        self._write_stub(self.bin / "python", 'printf "python %s\\n" "$*" >> .aic-sentinel\nexit "${PYTHON_STUB_EXIT:-0}"')
        self._write_stub(self.bin / "dotnet", 'printf "dotnet %s\\n" "$*" >> .aic-sentinel\nexit "${DOTNET_STUB_EXIT:-0}"')
        self._write_child("check-coding-standards.sh", "CODING_STUB_EXIT")
        self._write_child("check-spec-compliance.sh", "SPEC_STUB_EXIT")
        self._write_child("check-test-compliance.sh", "ADVISORY_STUB_EXIT")

    def close(self) -> None:
        self._temporary.cleanup()

    def remove_child(self, name: str) -> None:
        (self.scripts / name).unlink()

    def execute(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        bash = None
        if os.name == "nt":
            candidates = (
                Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Git/bin/bash.exe",
            )
            bash = next((str(candidate) for candidate in candidates if candidate.is_file()), None)
        else:
            bash = shutil.which("bash")
        if not bash:
            raise unittest.SkipTest("Bash is required for check-all.sh fixture tests")
        merged_environment = dict(os.environ)
        merged_environment["PATH"] = str(self.bin) + os.pathsep + merged_environment["PATH"]
        merged_environment.pop("SPEC_FILE", None)
        merged_environment.pop("TASK_NAME", None)
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
            self.assertIn("Coding Standards Compliance returned non-zero", result.stdout)
            self.assertRegex(result.stdout, r"Required Failed: .*1")
        finally:
            fixture.close()

    def test_gwt_004_given_required_command_unavailable_when_selected_then_gate_fails(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given deterministic dotnet command stubs return command-not-found semantics.
            # When critical mode executes both required dotnet checks.
            result = fixture.execute("--critical", environment={"DOTNET_STUB_EXIT": "127"})

            # Then both selected command checks fail without workstation dependency.
            self.assertEqual(1, result.returncode)
            self.assertRegex(result.stdout, r"Required Failed: .*2")
            self.assertEqual(2, sum(line.startswith("dotnet ") for line in fixture.sentinel()))
        finally:
            fixture.close()

    def test_gwt_005_given_advisory_failure_when_full_runs_then_visible_but_nonblocking(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given all required stubs pass and the advisory child returns nonzero.
            # When full mode executes.
            result = fixture.execute("--full", environment={"ADVISORY_STUB_EXIT": "9"})

            # Then the gate passes with a visible advisory warning.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("ADVISORY", result.stdout)
            self.assertRegex(result.stdout, r"Advisory Warnings: .*1")
            self.assertRegex(result.stdout, r"Required Failed: .*0")
            self.assertIn("Passed with 1 Advisory Warning", result.stdout)
        finally:
            fixture.close()

    def test_gwt_006_given_no_spec_inputs_when_quick_runs_then_spec_is_not_applicable(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given both conditional spec inputs are absent.
            # When quick mode reaches spec compliance.
            result = fixture.execute("--quick")

            # Then it records N/A without selecting or failing another required check.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("NOT APPLICABLE", result.stdout)
            self.assertRegex(result.stdout, r"Not Applicable: .*1")
            self.assertRegex(result.stdout, r"Required Failed: .*0")
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

    def test_gwt_009_given_deferred_check_when_quick_runs_then_only_deferred_count_increments(self) -> None:
        fixture = SyntheticRunnerRepo()
        try:
            # Given the dependency check has no implementation script.
            # When quick mode reaches the declared deferred entry.
            result = fixture.execute("--quick")

            # Then it is explicitly deferred and cannot fail the gate.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("DEFERRED: Dependencies and Versions", result.stdout)
            self.assertRegex(result.stdout, r"Deferred: .*1")
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
            self.assertIn("Test Standards Compliance", full.stdout)
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

    def test_gwt_002_given_retained_mode_100644_when_validated_then_it_fails(self) -> None:
        fixture = SyntheticShellAssetRepo()
        fixture_root = fixture.root
        try:
            # Given a retained shell tracked with Git mode 100644.
            script = fixture.add_shell("required.sh", mode="100644")
            fixture.write_manifest(retained=[script], required_entrypoints=[script])

            # When shell asset validation runs against the synthetic index.
            result = fixture.validate()

            # Then index truth rejects the path regardless of host executability.
            self.assertEqual(1, result.returncode)
            self.assertIn(script, result.stdout)
            self.assertIn("must use Git mode 100755, found 100644", result.stdout)
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

    def test_gwt_013_given_invalid_lifecycle_groups_when_validated_then_invariants_fail(self) -> None:
        cases = (
            ("overlap", ["lifecycle groups overlap"]),
            ("duplicate", ["retained contains duplicate paths"]),
            ("required-outside", ["required_entrypoints must be a subset of retained"]),
        )
        for case, messages in cases:
            with self.subTest(case=case):
                fixture = SyntheticShellAssetRepo()
                try:
                    # Given a manifest violating one lifecycle invariant.
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

                    # When shell asset validation checks lifecycle ownership.
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
            # Given complete classification, executable retained paths, and valid subsets.
            entrypoint = fixture.add_shell("entrypoint.sh")
            child = fixture.add_shell("child.sh")
            fixture.write_manifest(
                retained=[entrypoint, child],
                required_entrypoints=[entrypoint],
                check_all_required_scripts=[child],
            )

            # When shell asset validation runs.
            result = fixture.validate()

            # Then it passes with truthful retained, retirement, and tracked counts.
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn(
                "passed for 2 retained executable asset(s), 0 retirement candidate(s), "
                "and 2 tracked shell asset(s)",
                result.stdout,
            )
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
