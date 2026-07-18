#!/usr/bin/env python3
"""GWT tests for placeholder-family disposition evidence."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_example_placeholder_disposition", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ExamplePlaceholderDispositionTests(unittest.TestCase):
    def validate(self, outcome: str, *, evidence_tier: str = "reference-only") -> list[str]:
        with tempfile.TemporaryDirectory(prefix="placeholder-disposition-") as temporary:
            root = Path(temporary)
            disposition_path = Path(".dev/examples/placeholder-disposition.yaml")
            evidence_path = Path(".dev/examples/evidence-manifest.yaml")
            (root / disposition_path.parent / "sample").mkdir(parents=True)
            replacement = root / ".dev/standards/canonical.md"
            replacement.parent.mkdir(parents=True)
            replacement.write_text("# Canonical\n", encoding="utf-8")

            evidence_entries = []
            if outcome != "retired":
                evidence_entries.append({"path": "sample/", "tier": "reference-only"})
            (root / evidence_path).write_text(
                yaml.safe_dump({"entries": evidence_entries}, sort_keys=False),
                encoding="utf-8",
            )
            (root / disposition_path).write_text(
                yaml.safe_dump(
                    {
                        "entries": [
                            {
                                "path": "sample/",
                                "disposition": outcome,
                                "evidence_tier": evidence_tier,
                                "canonical_replacements": [
                                    ".dev/standards/canonical.md"
                                ],
                            }
                        ]
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            errors: list[str] = []
            VALIDATOR.validate_example_placeholder_disposition(
                errors,
                root=root,
                disposition_path=disposition_path,
                evidence_path=evidence_path,
            )
            return errors

    def test_gwt_001_given_matching_reference_disposition_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate("reference-only"))

    def test_gwt_002_given_retired_path_absent_from_evidence_when_validated_then_passes(self) -> None:
        self.assertEqual([], self.validate("retired", evidence_tier="historical"))

    def test_gwt_003_given_tier_drift_when_validated_then_fails(self) -> None:
        errors = self.validate("reference-only", evidence_tier="illustrative")
        self.assertTrue(any("does not match manifest" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
