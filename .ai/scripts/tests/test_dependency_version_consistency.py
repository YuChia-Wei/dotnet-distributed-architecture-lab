#!/usr/bin/env python3
"""GWT tests for dependency-version consistency validation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-dependency-versions.py"


class DependencyVersionConsistencyTests(unittest.TestCase):
    """Exercise the CLI against small source and target repository fixtures."""

    def create_fixture(
        self,
        root: Path,
        *,
        source: bool = True,
        requirements: str = "requests==2.32.3\n",
        template_requirements: str | None = None,
        workflow_python_versions: tuple[str, ...] = ("3.11",),
        workflow_steps: str | None = None,
        projects: dict[str, str] | None = None,
        sdk_version: str = "10.0.100",
    ) -> None:
        if source:
            self.write(
                root,
                ".ai/distribution/profiles/dotnet-backend.yaml",
                "schema_version: 1.0.0\nprofile:\n  id: dotnet-backend\n",
            )
            self.write(root, "requirements.txt", requirements)
            self.write(
                root,
                ".ai/distribution/templates/requirements.txt",
                template_requirements if template_requirements is not None else requirements,
            )
            setup_python = "\n".join(
                f"      - uses: actions/setup-python@v5\n        with:\n          python-version: '{version}'"
                for version in workflow_python_versions
            )
            self.write(
                root,
                ".github/workflows/validate.yml",
                "name: validate\non: [push]\njobs:\n  validate:\n    runs-on: ubuntu-latest\n"
                "    steps:\n"
                f"{setup_python}\n"
                + (
                    workflow_steps
                    if workflow_steps is not None
                    else "      - run: python -m pip install -r requirements.txt\n"
                ),
            )

        self.write(root, "global.json", '{"sdk":{"version":"' + sdk_version + '"}}\n')
        for relative_path, content in (projects or {"tools/App/App.csproj": self.csproj()}).items():
            self.write(root, relative_path, content)

    @staticmethod
    def csproj(*, tfm: str = "net10.0", references: str = "") -> str:
        return (
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            "  <PropertyGroup><TargetFramework>" + tfm + "</TargetFramework></PropertyGroup>\n"
            + references
            + "</Project>\n"
        )

    @staticmethod
    def write(root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), "--root", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def validate_fixture(self, **kwargs: object) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="dependency-version-consistency-") as temporary:
            root = Path(temporary)
            self.create_fixture(root, **kwargs)
            return self.run_validator(root)

    def assert_validation_failure(
        self,
        result: subprocess.CompletedProcess[str],
        expected: str,
    ) -> None:
        output = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, output)
        self.assertIn("Dependency/version consistency validation failed:", output)
        self.assertIn(expected, output)

    def test_gwt_001_given_valid_source_fixture_when_validated_then_passes(self) -> None:
        # Given a source repository with one pinned requirements contract and matching SDK/TFM.
        result = self.validate_fixture()

        # When the dependency validator runs, then the fixture passes.
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_002_given_source_requirements_template_drift_when_validated_then_fails(self) -> None:
        # Given source and distribution requirements that differ by exact bytes or version.
        for template_requirements in ("requests==2.32.3\n\n", "requests==2.32.4\n"):
            with self.subTest(template_requirements=template_requirements):
                result = self.validate_fixture(template_requirements=template_requirements)

                # When validated, then source/distribution drift is rejected.
                self.assert_validation_failure(result, "requirements mirror bytes differ")

    def test_gwt_003_given_unpinned_python_requirement_when_validated_then_fails(self) -> None:
        # Given a source requirement without an exact version pin.
        result = self.validate_fixture(requirements="requests>=2.32.3\n")

        # When validated, then the unpinned requirement is rejected.
        self.assert_validation_failure(result, "must use an exact name==version pin")

    def test_gwt_004_given_inline_workflow_package_install_when_validated_then_fails(self) -> None:
        # Given a source workflow that bypasses requirements.txt with a pinned inline install.
        result = self.validate_fixture(workflow_steps="      - run: python -m pip install requests==2.32.3\n")

        # When validated, then the workflow is rejected despite its exact pin.
        self.assert_validation_failure(
            result,
            "must install source dependencies with -r requirements.txt",
        )

    def test_gwt_005_given_repeated_nuget_reference_versions_when_validated_then_fails(self) -> None:
        # Given non-example projects that reference one package at different exact versions.
        references_v1 = '  <ItemGroup><PackageReference Include="MediatR" Version="12.2.0" /></ItemGroup>\n'
        references_v2 = '  <ItemGroup><PackageReference Include="MediatR" Version="12.3.0" /></ItemGroup>\n'
        result = self.validate_fixture(
            projects={
                "tools/One/One.csproj": self.csproj(references=references_v1),
                "tools/Two/Two.csproj": self.csproj(references=references_v2),
            }
        )

        # When validated, then conflicting PackageReference versions are rejected.
        self.assert_validation_failure(
            result,
            "PackageReference mediatr resolves to conflicting versions",
        )

    def test_gwt_006_given_nuget_reference_without_version_when_validated_then_fails(self) -> None:
        # Given a non-example PackageReference without an exact Version attribute.
        result = self.validate_fixture(
            projects={
                "tools/App/App.csproj": self.csproj(
                    references='  <ItemGroup><PackageReference Include="MediatR" /></ItemGroup>\n'
                )
            }
        )

        # When validated, then the unresolved package version is rejected.
        self.assert_validation_failure(result, "PackageReference MediatR has no exact version")

    def test_gwt_007_given_sdk_and_net_tfm_major_mismatch_when_validated_then_fails(self) -> None:
        # Given a selected SDK that is too old to build a managed tool TFM.
        result = self.validate_fixture(
            sdk_version="9.0.100",
            projects={"tools/App/App.csproj": self.csproj(tfm="net10.0")},
        )

        # When validated, then the incompatible SDK/TFM selection is rejected.
        self.assert_validation_failure(result, "require .NET SDK major at least 10")

    def test_gwt_008_given_netstandard_project_when_validated_then_it_is_allowed(self) -> None:
        # Given a netstandard2.0 project, which has no SDK-major parity requirement.
        result = self.validate_fixture(
            projects={"tools/Library/Library.csproj": self.csproj(tfm="netstandard2.0")}
        )

        # When validated, then the compatible netstandard project passes.
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_009_given_old_or_inconsistent_workflow_python_when_validated_then_fails(self) -> None:
        # Given source workflows with a below-minimum or inconsistent Python setup version.
        for versions in (("3.10",), ("3.11", "3.12")):
            with self.subTest(versions=versions):
                result = self.validate_fixture(workflow_python_versions=versions)

                # When validated, then the Python-version policy fails closed.
                expected = (
                    "is below required 3.11"
                    if versions == ("3.10",)
                    else "Python setup versions must be consistent"
                )
                self.assert_validation_failure(result, expected)

    def test_gwt_010_given_target_without_source_distribution_control_when_validated_then_own_dotnet_contract_passes(self) -> None:
        # Given a target fixture without source-only requirements or workflow/distribution controls.
        result = self.validate_fixture(
            source=False,
            projects={"tools/Target/Target.csproj": self.csproj(tfm="net10.0")},
        )

        # When validated, then its own csproj/global.json contract is sufficient.
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_011_given_newer_sdk_and_older_tfm_when_validated_then_it_is_allowed(self) -> None:
        # Given a newer SDK that can build a lower managed-tool target framework.
        result = self.validate_fixture(
            sdk_version="10.0.100",
            projects={"tools/Target/Target.csproj": self.csproj(tfm="net9.0")},
        )

        # When validated, then compatibility is not mistaken for exact-major equality.
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_012_given_source_profile_without_package_requirements_when_validated_then_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dependency-version-consistency-") as temporary:
            root = Path(temporary)
            self.create_fixture(root)
            (root / ".ai/distribution/templates/requirements.txt").unlink()

            # Given source distribution control remains but its requirements
            # mirror was deleted, when validation runs, then source checks
            # cannot silently downgrade to target mode.
            result = self.run_validator(root)
            self.assert_validation_failure(result, "cannot read requirements")


if __name__ == "__main__":
    unittest.main()
