#!/usr/bin/env python3
"""GWT contracts for the canonical profile membership registry."""

from __future__ import annotations

import os
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / ".ai/scripts/validation-profile-registry.sh"
RUNNER = ROOT / ".ai/scripts/check-all.sh"


def bash_executable() -> str | None:
    if os.name == "nt":
        candidates = (
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Git/bin/bash.exe",
        )
        return next((str(candidate) for candidate in candidates if candidate.is_file()), None)
    return shutil.which("bash")


def registry_snapshot() -> tuple[dict[str, tuple[str, str, str]], dict[str, tuple[str, ...]]]:
    bash = bash_executable()
    if not bash:
        raise unittest.SkipTest("Bash is required for validation profile registry tests")
    script = r'''
set -e
declare -ag PROFILE_IDS=()
declare -A PROFILE_PURPOSE=() PROFILE_BUDGET=() PROFILE_ENFORCEMENT=()
declare -ag CHECK_IDS=()
declare -A CHECK_ID_BY_DESCRIPTION=() CHECK_DESCRIPTION=() CHECK_OWNER=()
declare -A CHECK_ENFORCEMENT=() CHECK_TAGS=() CHECK_PROFILES=() CHECK_INPUT_PATHS=()
declare -A CHECK_DEPENDS=() CHECK_ENVIRONMENT=() CHECK_TIMEOUT=() CHECK_RESOURCE_CLASS=()
declare -A CHECK_CACHE_POLICY=() CHECK_DISPOSITION=() CHECK_COMMAND=() CHECK_APPLICABILITY=()
register_profile() { PROFILE_IDS+=("$1"); PROFILE_PURPOSE["$1"]=$2; PROFILE_BUDGET["$1"]=$3; PROFILE_ENFORCEMENT["$1"]=$4; }
register_check() {
  CHECK_IDS+=("$1"); CHECK_ID_BY_DESCRIPTION["$2"]=$1; CHECK_DESCRIPTION["$1"]=$2; CHECK_OWNER["$1"]=ai-context-governance
  CHECK_ENFORCEMENT["$1"]=$3; CHECK_TAGS["$1"]=$4; CHECK_PROFILES["$1"]=$5; CHECK_INPUT_PATHS["$1"]=$6
  CHECK_DEPENDS["$1"]=$7; CHECK_ENVIRONMENT["$1"]=$8; CHECK_TIMEOUT["$1"]=$9; CHECK_RESOURCE_CLASS["$1"]=${10}
  CHECK_CACHE_POLICY["$1"]=${11}; CHECK_DISPOSITION["$1"]=${12}; CHECK_COMMAND["$1"]=${13}; CHECK_APPLICABILITY["$1"]=${14}
}
source "$1"
for profile in "${PROFILE_IDS[@]}"; do
  printf 'P|%s|%s|%s|%s\n' "$profile" "${PROFILE_PURPOSE[$profile]}" "${PROFILE_BUDGET[$profile]}" "${PROFILE_ENFORCEMENT[$profile]}"
done
for id in "${CHECK_IDS[@]}"; do
  printf 'C|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' "$id" "${CHECK_DESCRIPTION[$id]}" "${CHECK_OWNER[$id]}" "${CHECK_ENFORCEMENT[$id]}" "${CHECK_TAGS[$id]}" "${CHECK_PROFILES[$id]}" "${CHECK_INPUT_PATHS[$id]}" "${CHECK_DEPENDS[$id]}" "${CHECK_ENVIRONMENT[$id]}" "${CHECK_TIMEOUT[$id]}" "${CHECK_RESOURCE_CLASS[$id]}" "${CHECK_CACHE_POLICY[$id]}" "${CHECK_DISPOSITION[$id]}" "${CHECK_COMMAND[$id]}"
done
'''
    result = subprocess.run(
        [bash, "-c", script, "validation-profile-registry", str(REGISTRY)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise AssertionError(result.stderr)

    profiles: dict[str, tuple[str, str, str]] = {}
    checks: dict[str, tuple[str, ...]] = {}
    for line in result.stdout.splitlines():
        record = line.split("|")
        if record[0] == "P":
            profiles[record[1]] = (record[2], record[3], record[4])
        elif record[0] == "C":
            checks[record[1]] = tuple(record[2:])
    return profiles, checks


class ValidationProfileRegistryGwtTests(unittest.TestCase):
    def test_gwt_001_given_registry_when_read_then_required_profiles_are_distinct(self) -> None:
        profiles, _ = registry_snapshot()

        self.assertEqual(
            {
                "fast": ("local-development-feedback", "30", "report-and-warn"),
                "pr": ("pull-request-integration", "90", "report-and-warn"),
                "release": ("immutable-candidate-validation", "", "measure-first"),
                "closeout": ("post-publication-administrative-verification", "120", "report-and-warn"),
                "nightly-full": ("full-history-and-compatibility-regression", "", "measure-first"),
            },
            profiles,
        )

    def test_gwt_002_given_registry_when_read_then_every_check_has_explainable_metadata(self) -> None:
        profiles, checks = registry_snapshot()
        self.assertEqual(len(checks), len(set(checks)))
        self.assertGreaterEqual(len(checks), 40)
        profile_ids = set(profiles)
        for check_id, fields in checks.items():
            with self.subTest(check_id=check_id):
                description, owner, enforcement, tags, memberships, inputs, dependencies, environment, timeout, resource, cache, disposition, command = fields
                self.assertTrue(all((description, owner, enforcement, tags, memberships, inputs, environment, resource, cache, disposition, command)))
                self.assertIn(enforcement, {"required", "advisory"})
                self.assertTrue(set(memberships.split()).issubset(profile_ids))
                self.assertTrue(all(dependency in checks for dependency in dependencies.split()))
                self.assertTrue(timeout.isdigit() or timeout == "")

    def test_gwt_003_given_membership_when_compared_then_fast_and_pr_avoid_the_full_package_matrix(self) -> None:
        _, checks = registry_snapshot()
        memberships = {check_id: set(fields[4].split()) for check_id, fields in checks.items()}

        self.assertNotIn("fast", memberships["package-full-matrix"])
        self.assertNotIn("pr", memberships["package-full-matrix"])
        self.assertIn("release", memberships["package-full-matrix"])
        self.assertNotIn("fast", memberships["aggregate-runner-contract"])
        self.assertNotIn("pr", memberships["aggregate-runner-contract"])
        self.assertIn("fast", memberships["ai-context-navigation"])
        self.assertIn("pr", memberships["package-apply"])
        self.assertNotIn("fast", memberships["python-source-entrypoints"])
        self.assertIn("pr", memberships["python-source-entrypoints"])
        self.assertIn("fast", memberships["validation-evidence-contract"])
        self.assertEqual({"closeout"}, memberships["source-release-closeout-contract"])

    def test_gwt_004_given_legacy_flags_when_help_is_requested_then_aliases_are_declared(self) -> None:
        bash = bash_executable()
        if not bash:
            raise unittest.SkipTest("Bash is required for validation profile registry tests")
        result = subprocess.run([bash, str(RUNNER), "--help"], check=False, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--quick       --profile pr", result.stdout)
        self.assertIn("--critical    --profile release", result.stdout)
        self.assertIn("--full        --profile nightly-full", result.stdout)

    def test_gwt_005_given_source_history_contract_when_profiles_are_read_then_routine_and_full_boundaries_are_explicit(self) -> None:
        _, checks = registry_snapshot()
        contract = checks["immutable-history-validation-contract"]
        runner = RUNNER.read_text(encoding="utf-8")
        distribution = (
            ROOT / ".ai/distribution/profiles/dotnet-backend.yaml"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            {"pr", "release", "nightly-full"},
            set(contract[4].split()),
        )
        self.assertEqual("source", contract[11])
        self.assertEqual(
            "python .ai/scripts/tests/test_immutable_history_validation.py -v",
            contract[12],
        )
        self.assertIn("release-candidate", runner)
        self.assertIn("scheduled-governance", runner)
        self.assertIn("IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID", runner)
        self.assertIn(".ai/scripts/validate-immutable-history.py", distribution)
        self.assertIn(
            ".ai/scripts/tests/test_immutable_history_validation.py", distribution
        )

    def test_gwt_006_given_required_profiles_when_inspected_then_framework_sdk_is_not_selected(self) -> None:
        _, checks = registry_snapshot()
        contract = checks["sdk-free-framework-contract"]

        self.assertEqual(
            {"fast", "pr", "release", "nightly-full"},
            set(contract[4].split()),
        )
        self.assertEqual("python>=3.11 git", contract[7])
        self.assertEqual(
            "python .ai/scripts/tests/test_sdk_free_framework_contract.py -v",
            contract[12],
        )
        for check_id, fields in checks.items():
            with self.subTest(check_id=check_id):
                self.assertNotIn("dotnet", fields[7].split())
                self.assertFalse(fields[12].lstrip().startswith("dotnet "))


if __name__ == "__main__":
    unittest.main()
