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


if __name__ == "__main__":
    unittest.main()
