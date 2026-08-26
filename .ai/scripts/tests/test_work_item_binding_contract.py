#!/usr/bin/env python3
"""GWT tests for the target-owned work-item binding selection contract."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_work_item_binding", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class WorkItemBindingContractTests(unittest.TestCase):
    def validate(self, template: dict, schema: dict) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="work-item-binding-contract-") as temporary:
            root = Path(temporary)
            template_path = Path("project-config.template.yaml")
            schema_path = Path("work-item-binding.schema.yaml")
            (root / template_path).write_text(
                yaml.safe_dump(template, sort_keys=False), encoding="utf-8"
            )
            (root / schema_path).write_text(
                yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.validate_work_item_binding_contract(
                errors,
                root=root,
                template_path=template_path,
                schema_path=schema_path,
            )
            return errors

    @staticmethod
    def valid_template() -> dict:
        return {
            "workManagement": {
                "workItemBinding": {
                    "mode": None,
                    "purposes": ["traceability", "work-authorization"],
                    "mergeGate": None,
                }
            }
        }

    @staticmethod
    def valid_schema() -> dict:
        return {
            "required_fields": ["mode", "purposes", "mergeGate"],
            "fixed_purposes": ["traceability", "work-authorization"],
            "allowed_modes": ["required", "optional", "disabled"],
            "allowed_merge_gates": ["required", "optional", "disabled"],
            "selection_source": "explicit-target-decision",
            "template_unresolved_value": None,
        }

    def test_gwt_001_given_unresolved_target_selection_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(self.valid_template(), self.valid_schema()))

    def test_gwt_002_given_source_optional_mode_copied_to_target_template_when_validated_then_fails(self) -> None:
        template = self.valid_template()
        template["workManagement"]["workItemBinding"]["mode"] = "optional"

        errors = self.validate(template, self.valid_schema())

        self.assertTrue(any("unresolved target-selection shape" in error for error in errors))

    def test_gwt_003_given_authorization_purpose_missing_when_validated_then_fails(self) -> None:
        schema = self.valid_schema()
        schema["fixed_purposes"] = ["traceability"]

        errors = self.validate(self.valid_template(), schema)

        self.assertTrue(any("traceability and work-authorization" in error for error in errors))

    def test_gwt_004_given_merge_gate_mode_missing_when_validated_then_fails(self) -> None:
        schema = self.valid_schema()
        schema["allowed_merge_gates"] = ["required", "disabled"]

        errors = self.validate(self.valid_template(), schema)

        self.assertTrue(any("allowed_merge_gates must equal" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
