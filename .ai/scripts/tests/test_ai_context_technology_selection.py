#!/usr/bin/env python3
"""GWT tests for the generic target technology-selection contract."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_technology_selection", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class TechnologySelectionContractTests(unittest.TestCase):
    def validate(self, template: dict, schema: dict) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="technology-selection-contract-") as temporary:
            root = Path(temporary)
            template_path = Path("project-config.template.yaml")
            schema_path = Path("technology-selection.schema.yaml")
            (root / template_path).write_text(
                yaml.safe_dump(template, sort_keys=False), encoding="utf-8"
            )
            (root / schema_path).write_text(
                yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
            )
            errors: list[str] = []
            VALIDATOR.validate_technology_selection_contract(
                errors,
                root=root,
                template_path=template_path,
                schema_path=schema_path,
            )
            return errors

    @staticmethod
    def valid_template() -> dict:
        return {
            "technologySelections": [],
            "architecture": {"capabilitySelections": []},
        }

    @staticmethod
    def valid_schema() -> dict:
        return {
            "required_fields": [
                "slot",
                "value",
                "status",
                "source",
                "evidence",
                "reason",
            ],
            "allowed_statuses": ["selected", "not-applicable", "unresolved"],
            "allowed_sources": ["repository-evidence", "explicit-target-decision"],
            "slot_pattern": r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$",
        }

    def test_gwt_001_given_valid_generic_selection_contract_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate(self.valid_template(), self.valid_schema()))

    def test_gwt_002_given_nonempty_template_selection_when_validated_then_fails(self) -> None:
        template = self.valid_template()
        template["technologySelections"] = [{"slot": "testing.mocking"}]

        errors = self.validate(template, self.valid_schema())

        self.assertTrue(any("must default to an empty collection" in error for error in errors))

    def test_gwt_003_given_incomplete_record_schema_when_validated_then_fails(self) -> None:
        schema = self.valid_schema()
        schema["required_fields"].remove("reason")

        errors = self.validate(self.valid_template(), schema)

        self.assertTrue(any("required_fields must equal" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
