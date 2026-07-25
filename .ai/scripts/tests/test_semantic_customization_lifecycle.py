#!/usr/bin/env python3
"""GWT lifecycle tests for semantic customization governance."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
import ai_context_target_provenance as TARGET  # noqa: E402


SOURCE_V060 = {
    "repository": "owner/framework",
    "release_id": "REL-v0.6.0",
    "version": "v0.6.0",
    "tag": "v0.6.0",
    "commit": "a" * 40,
}
SELECTION = {
    "release_model": "single-versioned-componentized-release",
    "mandatory_components": [
        "software-development-core",
        "ai-context-lifecycle-core",
    ],
    "profiles": ["dotnet-backend"],
    "providers": {
        "repo-backlog": {
            "enabled": False,
            "preservation": "preserve-existing-if-recorded",
        }
    },
}
AT = "2026-07-24T08:00:00+08:00"


def valid_customization() -> dict:
    return {
        "id": "CUST-TEAM-001",
        "subject": {"kind": "contract", "id": "enterprise-test-execution"},
        "relationship": "deviates",
        "reason": "Enterprise execution controls change the framework test contract.",
        "paths": [".dev/operations/test-policy.md"],
        "base_framework": {
            "version": "v0.6.0",
            "commit": "a" * 40,
            "evidence": [".dev/ai-context/provenance.yaml#source"],
        },
        "dependencies": {"customization_ids": [], "subject_refs": []},
        "owner_reconciliation": {
            "status": "approved",
            "owner": "platform-team",
            "decided_at": "2026-07-24T08:10:00+08:00",
            "evidence": ".dev/workflows/customization/plan.md#approval",
        },
        "decision_evidence": {
            "requirements": [".dev/requirement/test-policy.md"],
            "adrs": [],
            "workflows": [".dev/workflows/customization/plan.md"],
        },
        "active_context_audit": {
            "assessment_id": "ASM-20260724-001",
            "status": "verified",
            "evidence": ".dev/assessments/ASM-20260724-001/report.md",
        },
        "incoming": {
            "version": "v0.7.0",
            "status": "equivalent-candidate",
            "evidence": ".dev/workflows/customization/equivalence.md",
        },
        "disposition": "merge",
        "post_upgrade_audit": {
            "assessment_id": "ASM-20260724-002",
            "status": "verified",
            "evidence": ".dev/assessments/ASM-20260724-002/report.md",
        },
        "validation": ["python .ai/scripts/validate-ai-context-target.py"],
    }


class SemanticCustomizationLifecycleTests(unittest.TestCase):
    def test_gwt_001_given_credible_init_and_verified_reconciliation_when_finalized_then_target_validates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-lifecycle-") as value:
            root = Path(value)
            initialized = TARGET.initialize_context(
                root, SOURCE_V060, SELECTION, AT
            )
            self.assertEqual("initialized", initialized["status"])

            provenance_path = root / ".dev/ai-context/provenance.yaml"
            ledger_path = root / ".dev/ai-context/customizations.yaml"
            provenance = TARGET.load_mapping(provenance_path, [])
            assert provenance is not None
            customization = valid_customization()
            customization["owner_reconciliation"] = {
                "status": "pending",
                "owner": "",
                "decided_at": None,
                "evidence": "",
            }
            customization["active_context_audit"] = {
                "assessment_id": None,
                "status": "not-run",
                "evidence": "",
            }
            customization["incoming"] = {
                "version": "v0.7.0",
                "status": "absent",
                "evidence": ".dev/workflows/customization/equivalence.md",
            }
            customization["disposition"] = "unresolved"
            customization["post_upgrade_audit"] = {
                "assessment_id": None,
                "status": "not-run",
                "evidence": "",
            }
            # Governance records semantic intent before paths are used for comparison.
            ledger = {
                "schema_version": "1.0",
                "customizations": [customization],
            }
            # The auditor records an independent active-context baseline.
            customization["active_context_audit"] = {
                "assessment_id": "ASM-20260724-001",
                "status": "verified",
                "evidence": ".dev/assessments/ASM-20260724-001/report.md",
            }
            # The upgrader records incoming equivalence.
            customization["incoming"]["status"] = "equivalent-candidate"
            # Governance records the explicit owner reconciliation.
            customization["owner_reconciliation"] = {
                "status": "approved",
                "owner": "platform-team",
                "decided_at": "2026-07-24T08:10:00+08:00",
                "evidence": ".dev/workflows/customization/plan.md#approval",
            }
            customization["disposition"] = "merge"
            # A separate auditor assessment verifies the post-upgrade active context.
            customization["post_upgrade_audit"] = {
                "assessment_id": "ASM-20260724-002",
                "status": "verified",
                "evidence": ".dev/assessments/ASM-20260724-002/report.md",
            }
            upgraded = copy.deepcopy(provenance)
            upgraded["previous_source"] = upgraded["source"]
            upgraded["source"] = {
                "repository": "owner/framework",
                "release_id": "REL-v0.7.0",
                "version": "v0.7.0",
                "tag": "v0.7.0",
                "commit": "b" * 40,
            }
            upgraded["installation"]["last_upgraded_at"] = AT
            upgraded["last_migration"] = {
                "status": "completed",
                "from_version": "v0.6.0",
                "to_version": "v0.7.0",
                "completed_at": AT,
                "evidence": ".dev/assessments/ASM-20260724-002/report.md",
            }

            # Target validation succeeds before provenance finalization.
            ledger_candidate = root / "ledger-candidate.yaml"
            ledger_candidate.write_text(
                __import__("yaml").safe_dump(ledger, sort_keys=False),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(ledger_candidate, errors)
            self.assertEqual([], errors)
            # Finalization publishes both validated documents.
            TARGET.finalize_context(root, upgraded, ledger)
            self.assertEqual([], TARGET.validate_target(root))
            self.assertIn(
                "CUST-TEAM-001", ledger_path.read_text(encoding="utf-8")
            )

    def test_gwt_002_given_failed_post_upgrade_verification_when_finalized_then_prior_provenance_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-rollback-") as value:
            root = Path(value)
            TARGET.initialize_context(root, SOURCE_V060, SELECTION, AT)
            provenance_path = root / ".dev/ai-context/provenance.yaml"
            before = provenance_path.read_bytes()
            provenance = TARGET.load_mapping(provenance_path, [])
            assert provenance is not None
            customization = valid_customization()
            customization["disposition"] = "retire"
            customization["post_upgrade_audit"] = {
                "assessment_id": None,
                "status": "not-run",
                "evidence": "",
            }
            with self.assertRaises(TARGET.TargetValidationError):
                TARGET.finalize_context(
                    root,
                    provenance,
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                )
            self.assertEqual(before, provenance_path.read_bytes())

    def test_gwt_003_given_legacy_overrides_when_converted_then_each_becomes_one_unresolved_item_without_semantics(self) -> None:
        legacy = {
            "schema_version": "1.0",
            "local_overrides": [
                {
                    "id": "LOCAL-1",
                    "paths": [".ai/rule.md"],
                    "owner": "team",
                    "reason": "local policy",
                    "disposition": "preserve",
                },
                {
                    "id": "LOCAL-2",
                    "paths": [".dev/operations/runbook.md"],
                    "owner": "ops",
                    "reason": "operations truth",
                    "disposition": "preserve",
                },
            ],
        }
        unresolved = TARGET.legacy_override_reconciliation(legacy)
        self.assertEqual(2, len(unresolved))
        self.assertTrue(
            all(item["reason"] == "legacy-local-override" for item in unresolved)
        )
        self.assertTrue(all("subject" not in item for item in unresolved))

    def test_gwt_004_given_unproven_source_when_initialized_then_no_authority_is_written(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-unresolved-") as value:
            root = Path(value)
            result = TARGET.initialize_context(
                root, {"repository": "owner/framework"}, SELECTION, AT
            )
            self.assertEqual("unresolved", result["status"])
            self.assertFalse((root / ".dev/ai-context/provenance.yaml").exists())
            self.assertFalse(
                (root / ".dev/ai-context/customizations.yaml").exists()
            )

    def test_gwt_005_given_unsafe_path_or_missing_dependency_when_validated_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-invalid-") as value:
            path = Path(value) / "customizations.yaml"
            customization = valid_customization()
            customization["paths"] = [
                "../outside.md",
                "C:/outside.md",
                ".dev//operations/policy.md",
            ]
            customization["dependencies"]["customization_ids"] = ["CUST-MISSING"]
            path.write_text(
                __import__("yaml").safe_dump(
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(path, errors)
            self.assertTrue(any(".paths" in error for error in errors))
            self.assertTrue(any("missing customization dependency" in error for error in errors))

    def test_gwt_006_given_unfinalized_retirement_without_owner_approval_when_validated_then_it_still_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-retire-") as value:
            path = Path(value) / "customizations.yaml"
            customization = valid_customization()
            customization["disposition"] = "retire"
            customization["owner_reconciliation"] = {
                "status": "pending",
                "owner": "platform-team",
                "decided_at": None,
                "evidence": "",
            }
            path.write_text(
                __import__("yaml").safe_dump(
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(path, errors, require_finalized=False)
            self.assertTrue(
                any(
                    "requires approved owner reconciliation" in error
                    for error in errors
                )
            )

    def test_gwt_007_given_customization_reason_is_missing_when_validated_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="customization-reason-") as value:
            path = Path(value) / "customizations.yaml"
            customization = valid_customization()
            del customization["reason"]
            path.write_text(
                __import__("yaml").safe_dump(
                    {
                        "schema_version": "1.0",
                        "customizations": [customization],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            TARGET.validate_customizations(path, errors)
            self.assertTrue(any(".reason must be a non-empty string" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
