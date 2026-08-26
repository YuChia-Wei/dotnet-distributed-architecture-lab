#!/usr/bin/env python3
"""GWT tests for canonical sub-agent runtime-adapter metadata validation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_sub_agent_adapters", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SubAgentAdapterFixture:
    """Own a disposable canonical role, runtime adapters, and package profile."""

    canonical_path = Path(".ai/assets/sub-agent-role-prompts/example-role/sub-agent.yaml")
    profile_path = Path(".ai/distribution/profiles/dotnet-backend.yaml")
    adapter_paths = {
        "codex": ".codex/agents/example-role.toml",
        "claude": ".claude/agents/example-role.md",
        "copilot": ".github/agents/example-role.agent.md",
    }

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="aicr003-sub-agent-adapters-")
        self.root = Path(self._temporary.name)
        self._write_adapters()
        self._write_profile(list(self.adapter_paths.values()))

    def close(self) -> None:
        self._temporary.cleanup()

    def validate(self, data: dict) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_sub_agent_adapter_metadata(
            self.canonical_path,
            data,
            errors,
            root=self.root,
            profile_path=self.profile_path,
        )
        return errors

    def _write_adapters(self) -> None:
        reference = self.canonical_path.as_posix()
        self.write_adapter(
            "codex",
            'name = "example-role"\n'
            'description = "Example role"\n'
            f'developer_instructions = "Read `{reference}`."\n',
        )
        self.write_adapter(
            "claude",
            "---\nname: example-role\ndescription: Example role\n---\n"
            f"Read `{reference}`.\n",
        )
        self.write_adapter(
            "copilot",
            "---\nname: example-role\ndescription: Example role\n"
            "disable-model-invocation: false\nuser-invocable: true\n---\n"
            f"Read `{reference}`.\n",
        )

    def write_adapter(self, target: str, content: str, *, path: str | None = None) -> None:
        adapter = self.root / (path or self.adapter_paths[target])
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text(content, encoding="utf-8")

    def _write_profile(
        self,
        included_paths: list[str],
        *,
        target: str = "preserve-relative-path",
        exclusions: list[str] | None = None,
    ) -> None:
        profile = self.root / self.profile_path
        profile.parent.mkdir(parents=True, exist_ok=True)
        sources = "\n".join(
            f"      - {Path(path).parent.as_posix()}/**" for path in included_paths
        )
        excluded = "\n".join(f"      - {path}" for path in exclusions or [])
        exclusion_document = (
            "exclusions:\n"
            "  - patterns:\n"
            f"{excluded}\n"
            if excluded
            else "exclusions: []\n"
        )
        profile.write_text(
            "entries:\n"
            "  - ownership: framework-managed\n"
            "    install_behavior: managed\n"
            f"    target: {target}\n"
            "    source:\n"
            f"{sources}\n"
            f"{exclusion_document}",
            encoding="utf-8",
        )

    @classmethod
    def valid_data(cls) -> dict:
        return {
            "asset_id": "example-role",
            "wrapper_targets": ["codex", "claude", "copilot"],
            "adapter_metadata": {
                "codex": {"adapter_path": cls.adapter_paths["codex"], "adapter_format": "toml"},
                "claude": {
                    "adapter_path": cls.adapter_paths["claude"],
                    "adapter_format": "markdown-yaml-frontmatter",
                },
                "copilot": {
                    "adapter_path": cls.adapter_paths["copilot"],
                    "adapter_format": "markdown-yaml-frontmatter",
                },
            },
        }


class RoleBindingFixture:
    """Build one canonical role and an owning skill's static binding."""

    role_id = "example-role"
    role_path = ".ai/assets/sub-agent-role-prompts/example-role/sub-agent.yaml"

    @classmethod
    def role_assets(cls, *, status: str = "active") -> dict[str, dict]:
        return {
            cls.role_path: {
                "asset_id": cls.role_id,
                "status": status,
            }
        }

    @classmethod
    def valid_binding(cls) -> dict:
        return {
            "role_path": cls.role_path,
            "role_asset_id": cls.role_id,
            "expected_role_status": "active",
            "binding_kind": "primary",
            "applicability": "The owning skill selects the example role.",
            "load_obligation": "mandatory-when-applicable",
        }

    @classmethod
    def valid_owner(cls, *, status: str = "active") -> dict:
        return {
            "asset_id": "example-owner",
            "status": status,
            "role_bindings": [cls.valid_binding()],
        }

    @classmethod
    def validate(
        cls, data: dict, *, role_assets: dict[str, dict] | None = None
    ) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        role_ids = VALIDATOR.validate_skill_role_bindings(
            Path(".ai/assets/skills/example-owner/skill.yaml"),
            data,
            role_assets or cls.role_assets(),
            errors,
        )
        return errors, role_ids

    @staticmethod
    def projection_text(rows: list[tuple[str, str, str, str]]) -> str:
        body = "\n".join(
            f"| `{role_id}` | `{owner}` | `{binding_kind}` | {applicability} |"
            for role_id, owner, binding_kind, applicability in rows
        )
        return (
            "# Derived table fixture\n\n"
            "## SAG-001 Derived Role-Binding Projection\n\n"
            "| Role Asset ID | Derived Owning Skill | Binding Kind | Canonical Applicability (Projection) |\n"
            "| --- | --- | --- | --- |\n"
            f"{body}\n"
        )

    @classmethod
    def validate_projection(
        cls,
        rows: list[tuple[str, str, str, str]],
        canonical_rows: set[tuple[str, str, str, str]],
    ) -> list[str]:
        with tempfile.TemporaryDirectory(
            prefix="sar94-role-binding-projection-"
        ) as directory:
            projection_path = Path(directory) / "SUB-AGENT-SYSTEM.MD"
            projection_path.write_text(cls.projection_text(rows), encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.validate_derived_role_binding_projection(
                projection_path, canonical_rows, errors
            )
            return errors


class SubAgentAdapterMetadataValidationTests(unittest.TestCase):
    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_gwt_001_given_valid_three_runtime_adapters_when_validated_then_passes(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            self.assertEqual([], fixture.validate(fixture.valid_data()))
        finally:
            fixture.close()

    def test_gwt_002_given_dynamic_empty_targets_and_metadata_when_validated_then_passes(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["wrapper_targets"] = []
            data["adapter_metadata"] = {}
            self.assertEqual([], fixture.validate(data))
        finally:
            fixture.close()

    def test_gwt_003_given_missing_target_metadata_when_validated_then_parity_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            del data["adapter_metadata"]["claude"]
            self.assert_error(fixture.validate(data), "missing=['claude']")
        finally:
            fixture.close()

    def test_gwt_004_given_extra_target_metadata_when_validated_then_parity_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["future"] = {}
            self.assert_error(fixture.validate(data), "extra=['future']")
        finally:
            fixture.close()

    def test_gwt_005_given_duplicate_runtime_adapter_path_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["claude"]["adapter_path"] = fixture.adapter_paths["codex"]
            data["adapter_metadata"]["claude"]["adapter_format"] = "markdown-yaml-frontmatter"
            self.assert_error(fixture.validate(data), "adapter paths must be unique")
        finally:
            fixture.close()

    def test_gwt_006_given_placeholder_or_glob_adapter_path_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["codex"]["adapter_path"] = ".codex/agents/<role>*.toml"
            self.assert_error(fixture.validate(data), "without placeholders or globs")
        finally:
            fixture.close()

    def test_gwt_007_given_escaping_adapter_path_when_validated_then_boundary_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["codex"]["adapter_path"] = "../outside.toml"
            self.assert_error(fixture.validate(data), "escapes the repository")
        finally:
            fixture.close()

    def test_gwt_008_given_nonexistent_adapter_path_when_validated_then_existence_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["codex"]["adapter_path"] = ".codex/agents/missing.toml"
            self.assert_error(fixture.validate(data), "adapter_path does not exist")
        finally:
            fixture.close()

    def test_gwt_009_given_wrong_runtime_root_and_format_when_validated_then_both_fail(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["codex"] = {
                "adapter_path": ".claude/agents/example-role.toml",
                "adapter_format": "markdown-yaml-frontmatter",
            }
            fixture.write_adapter("codex", 'name = "example-role"\ndescription = "Example role"\ndeveloper_instructions = "Read `.ai/assets/sub-agent-role-prompts/example-role/sub-agent.yaml`."\n', path=".claude/agents/example-role.toml")
            errors = fixture.validate(data)
            self.assert_error(errors, "must be 'toml'")
            self.assert_error(errors, "must be under .codex/agents")
        finally:
            fixture.close()

    def test_gwt_010_given_adapter_without_canonical_role_reference_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            fixture.write_adapter("codex", 'name = "example-role"\ndescription = "Example role"\ndeveloper_instructions = "No link."\n')
            self.assert_error(fixture.validate(fixture.valid_data()), "adapter must cite canonical role")
        finally:
            fixture.close()

    def test_gwt_011_given_profile_omits_adapter_when_validated_then_package_inclusion_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            fixture._write_profile([fixture.adapter_paths["claude"], fixture.adapter_paths["copilot"]])
            self.assert_error(fixture.validate(fixture.valid_data()), "adapter must be effectively included")
        finally:
            fixture.close()

    def test_gwt_012_given_retired_copilot_infer_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            fixture.write_adapter(
                "copilot",
                "---\nname: example-role\ndescription: Example role\ninfer: true\n---\n"
                "Read `.ai/assets/sub-agent-role-prompts/example-role/sub-agent.yaml`.\n",
            )
            self.assert_error(fixture.validate(fixture.valid_data()), "Copilot infer is retired")
        finally:
            fixture.close()

    def test_gwt_013_given_adapter_path_case_mismatch_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"]["codex"]["adapter_path"] = ".codex/agents/EXAMPLE-role.toml"
            self.assert_error(fixture.validate(data), "adapter_path exact-case mismatch")
        finally:
            fixture.close()

    def test_gwt_014_given_duplicate_wrapper_target_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["wrapper_targets"].append("codex")
            self.assert_error(
                fixture.validate(data), "wrapper_targets must not contain duplicates"
            )
        finally:
            fixture.close()

    def test_gwt_015_given_non_mapping_adapter_metadata_when_validated_then_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            data = fixture.valid_data()
            data["adapter_metadata"] = None
            self.assert_error(
                fixture.validate(data), "adapter_metadata must be a mapping"
            )
        finally:
            fixture.close()

    def test_gwt_016_given_profile_remaps_adapter_when_validated_then_package_inclusion_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            fixture._write_profile(
                list(fixture.adapter_paths.values()), target=".relocated/agents/"
            )
            self.assert_error(
                fixture.validate(fixture.valid_data()),
                "adapter must be effectively included",
            )
        finally:
            fixture.close()

    def test_gwt_017_given_profile_excludes_adapter_when_validated_then_package_inclusion_fails(self) -> None:
        fixture = SubAgentAdapterFixture()
        try:
            fixture._write_profile(
                list(fixture.adapter_paths.values()),
                exclusions=[fixture.adapter_paths["codex"]],
            )
            self.assert_error(
                fixture.validate(fixture.valid_data()),
                "adapter must be effectively included",
            )
        finally:
            fixture.close()

    def test_gwt_018_given_repository_role_inventory_when_inspected_then_only_translator_is_native(self) -> None:
        import yaml

        roles = {}
        for manifest in sorted(
            (REPO_ROOT / ".ai/assets/sub-agent-role-prompts").glob(
                "*/sub-agent.yaml"
            )
        ):
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            roles[data["asset_id"]] = {
                "targets": data["wrapper_targets"],
                "metadata": data["adapter_metadata"],
            }

        self.assertEqual(18, len(roles))
        promoted = {
            role: disposition
            for role, disposition in roles.items()
            if disposition["targets"]
        }
        self.assertEqual({"context-translator"}, set(promoted))
        self.assertEqual(
            {"codex", "claude", "copilot"},
            set(promoted["context-translator"]["targets"]),
        )
        self.assertEqual(
            set(promoted["context-translator"]["targets"]),
            set(promoted["context-translator"]["metadata"]),
        )


    def test_gwt_019_given_exact_active_role_binding_when_validated_then_static_reachability_passes(self) -> None:
        errors, role_ids = RoleBindingFixture.validate(RoleBindingFixture.valid_owner())

        self.assertEqual([], errors)
        self.assertEqual([RoleBindingFixture.role_id], role_ids)

    def test_gwt_020_given_declared_empty_role_bindings_when_validated_then_mandatory_binding_fails(self) -> None:
        data = RoleBindingFixture.valid_owner()
        data["role_bindings"] = []

        errors, role_ids = RoleBindingFixture.validate(data)

        self.assert_error(errors, "must be non-empty when declared")
        self.assertEqual([], role_ids)

    def test_gwt_021_given_noncanonical_or_dangling_role_path_when_validated_then_exact_linkage_fails(self) -> None:
        data = RoleBindingFixture.valid_owner()
        data["role_bindings"][0]["role_path"] = (
            ".ai/assets/sub-agent-role-prompts/missing-role/sub-agent.yaml"
        )

        errors, role_ids = RoleBindingFixture.validate(data)

        self.assert_error(errors, "must be the exact canonical role path")
        self.assert_error(errors, "role_path is dangling")
        self.assertEqual([], role_ids)

    def test_gwt_022_given_mismatched_target_role_identity_when_validated_then_identity_fails(self) -> None:
        data = RoleBindingFixture.valid_owner()
        other_path = ".ai/assets/sub-agent-role-prompts/other-role/sub-agent.yaml"
        data["role_bindings"][0]["role_path"] = other_path
        roles = RoleBindingFixture.role_assets()
        roles[other_path] = {"asset_id": "other-role", "status": "active"}

        errors, role_ids = RoleBindingFixture.validate(data, role_assets=roles)

        self.assert_error(errors, "must exactly match target role asset_id")
        self.assertEqual([], role_ids)

    def test_gwt_023_given_inactive_target_role_when_validated_then_active_status_fails(self) -> None:
        errors, role_ids = RoleBindingFixture.validate(
            RoleBindingFixture.valid_owner(),
            role_assets=RoleBindingFixture.role_assets(status="deprecated"),
        )

        self.assert_error(errors, "target role status must be 'active'")
        self.assertEqual([], role_ids)

    def test_gwt_024_given_invalid_binding_fields_when_validated_then_static_contract_fails(self) -> None:
        data = RoleBindingFixture.valid_owner()
        binding = data["role_bindings"][0]
        binding["expected_role_status"] = "not-applicable"
        binding["binding_kind"] = "not-applicable"
        binding["applicability"] = " "
        binding["load_obligation"] = "not-applicable"

        errors, role_ids = RoleBindingFixture.validate(data)

        self.assert_error(errors, "expected_role_status must be 'active'")
        self.assert_error(errors, "binding_kind must be one of")
        self.assert_error(errors, "applicability must be a non-empty declarative string")
        self.assert_error(errors, "load_obligation must be 'mandatory-when-applicable'")
        self.assertEqual([], role_ids)

    def test_gwt_025_given_duplicate_role_binding_when_validated_then_duplicate_fails(self) -> None:
        data = RoleBindingFixture.valid_owner()
        data["role_bindings"].append(RoleBindingFixture.valid_binding())

        errors, role_ids = RoleBindingFixture.validate(data)

        self.assert_error(errors, "duplicate role binding")
        self.assert_error(errors, "duplicate role_path")
        self.assertEqual([], role_ids)

    def test_gwt_026_given_unowned_active_role_when_coverage_is_checked_then_central_only_fails(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_active_role_binding_coverage(
            RoleBindingFixture.role_assets(), {}, errors
        )

        self.assert_error(errors, "central-only and ownerless")

    def test_gwt_027_given_multiple_explicit_active_owners_when_coverage_is_checked_then_passes(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_active_role_binding_coverage(
            RoleBindingFixture.role_assets(),
            {
                RoleBindingFixture.role_id: [
                    Path(".ai/assets/skills/owner-one/skill.yaml"),
                    Path(".ai/assets/skills/owner-two/skill.yaml"),
                ]
            },
            errors,
        )

        self.assertEqual([], errors)

    def test_gwt_028_given_live_role_bindings_when_inspected_then_all_active_roles_have_exact_owners(self) -> None:
        import yaml

        owners: dict[str, dict[str, str]] = {}
        for manifest in sorted((REPO_ROOT / ".ai/assets/skills").glob("*/skill.yaml")):
            data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            bindings = data.get("role_bindings", [])
            owners[data["asset_id"]] = {
                binding["role_asset_id"]: binding["binding_kind"]
                for binding in bindings
            }

        self.assertEqual(
            {
                "slice-implementer": {
                    "command-sub-agent": "primary",
                    "query-sub-agent": "primary",
                    "reactor-sub-agent": "primary",
                    "aggregate-sub-agent": "conditional",
                    "controller-sub-agent": "conditional",
                    "outbox-sub-agent": "conditional",
                    "profile-config-sub-agent": "conditional",
                    "usecase-test-sub-agent": "conditional",
                    "aggregate-test-sub-agent": "conditional",
                    "controller-test-sub-agent": "conditional",
                    "reactor-test-sub-agent": "conditional",
                    "mutation-testing-sub-agent": "conditional",
                },
                "code-reviewer": {
                    "code-review-sub-agent": "primary",
                    "aggregate-code-review-sub-agent": "conditional",
                    "controller-code-review-sub-agent": "conditional",
                    "reactor-code-review-sub-agent": "conditional",
                },
                "problem-frame-author": {"problem-frame-sub-agent": "primary"},
                "ai-context-init": {"context-translator": "conditional"},
            },
            {owner: bindings for owner, bindings in owners.items() if bindings},
        )

    def test_gwt_029_given_matching_multi_owner_derived_projection_when_validated_then_parity_passes(self) -> None:
        primary_row = (
            RoleBindingFixture.role_id,
            "example-owner",
            "primary",
            "The owning skill selects the example role.",
        )
        conditional_row = (
            RoleBindingFixture.role_id,
            "alternate-owner",
            "conditional",
            "The alternate owning skill needs the example role.",
        )

        errors = RoleBindingFixture.validate_projection(
            [primary_row, conditional_row], {primary_row, conditional_row}
        )

        self.assertEqual([], errors)

    def test_gwt_030_given_stale_bdd_owner_projection_when_validated_then_conflicting_parity_fails(self) -> None:
        canonical_row = (
            RoleBindingFixture.role_id,
            "example-owner",
            "primary",
            "The owning skill selects the example role.",
        )
        stale_row = (
            RoleBindingFixture.role_id,
            "bdd-gwt-test-designer",
            "primary",
            "The owning skill selects the example role.",
        )

        errors = RoleBindingFixture.validate_projection([stale_row], {canonical_row})

        self.assert_error(errors, "ambiguous or conflicting row")

    def test_gwt_031_given_central_only_or_missing_projection_rows_when_validated_then_parity_fails(self) -> None:
        canonical_row = (
            RoleBindingFixture.role_id,
            "example-owner",
            "primary",
            "The owning skill selects the example role.",
        )
        central_only_row = (
            "central-only-role",
            "example-owner",
            "conditional",
            "A row exists only in the derived projection.",
        )

        errors = RoleBindingFixture.validate_projection([central_only_row], {canonical_row})

        self.assert_error(errors, "stale or central-only role row")
        self.assert_error(errors, "missing canonical role row")


if __name__ == "__main__":
    unittest.main()
