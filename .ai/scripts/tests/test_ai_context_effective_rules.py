#!/usr/bin/env python3
"""Given-When-Then tests for target-effective rule packet resolution."""

from __future__ import annotations

import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))

import ai_context_effective_rules as RULES  # noqa: E402
import ai_context_target_provenance as TARGET  # noqa: E402


SOURCE = {
    "repository": "owner/framework",
    "release_id": "REL-v1.2.3",
    "version": "v1.2.3",
    "tag": "v1.2.3",
    "commit": "a" * 40,
}
SELECTION = {
    "release_model": "single-versioned-componentized-release",
    "mandatory_components": ["software-development-core", "ai-context-lifecycle-core"],
    "profiles": ["dotnet-backend"],
    "providers": {"repo-backlog": {"enabled": False, "preservation": "preserve-existing-if-recorded"}},
}
REQUEST = {
    "capability": "test-design",
    "execution_mode": "direct",
    "technology_profile": "dotnet-backend",
    "file_type": "csharp-test",
}
REVIEW_REQUEST = {
    "capability": "review",
    "execution_mode": "consumer-route-b",
    "technology_profile": "dotnet-backend",
    "file_type": "csharp-review",
}
CONSUMER_ROUTES = (
    (REQUEST, ["AICTX-EVIDENCE-001", "TEST-GWT-001"]),
    (REVIEW_REQUEST, ["AICTX-EVIDENCE-001"]),
)
DEFAULT_CONSUMER_ROUTES = (CONSUMER_ROUTES[0],)
EVIDENCE = ".dev/decisions/effective-rules.md"


class EffectiveRuleFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="effective-rules-")
        self.root = Path(self._temporary.name)
        self._copy_catalog(RULES.SHARED_CATALOG_PATH)
        self._copy_catalog(RULES._profile_catalog_path("dotnet-backend"))
        context = self.root / ".dev/ai-context"
        context.mkdir(parents=True)
        self.provenance_path = context / "provenance.yaml"
        self.ledger_path = context / "customizations.yaml"
        provenance, ledger = TARGET.build_initialization_documents(
            SOURCE,
            SELECTION,
            "2026-08-05T00:00:00+00:00",
        )
        self.provenance_path.write_text(
            yaml.safe_dump(provenance, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        self.ledger_path.write_text(
            yaml.safe_dump(ledger, sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )

    def close(self) -> None:
        self._temporary.cleanup()

    def _copy_catalog(self, relative: str) -> None:
        source = ROOT / relative
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    def _catalog_records(self) -> list[dict[str, str]]:
        catalogs = RULES._catalogs_for_profile(self.root, "dotnet-backend")
        return [
            {
                "catalog_id": catalog_id,
                "path": (
                    RULES.SHARED_CATALOG_PATH
                    if catalog_id == "shared"
                    else RULES._profile_catalog_path("dotnet-backend")
                ),
                "digest": catalogs[catalog_id]["digest"],
            }
            for catalog_id in ("selected-profile", "shared")
        ]

    def write_ready_state(self, consumer_routes=DEFAULT_CONSUMER_ROUTES) -> dict:
        routing = []
        for selector, required_rule_ids in consumer_routes:
            resolved_selector = dict(selector)
            route_id = RULES.route_id_for_selector(resolved_selector)
            routing.append(
                {
                    "route_id": route_id,
                    "selector": resolved_selector,
                    "required_rule_ids": list(required_rule_ids),
                    "reported_not_applicable_rule_ids": [],
                    "packet": {
                        "path": f"{RULES.PACKET_DIRECTORY}/{route_id}.yaml",
                        "digest": "0" * 64,
                    },
                }
            )
        routing.sort(key=lambda route: route["route_id"])
        state = {
            "schema_version": "1.0",
            "framework": {
                "version": SOURCE["version"],
                "commit": SOURCE["commit"],
                "selected_technology_profile": "dotnet-backend",
            },
            "catalogs": self._catalog_records(),
            "target_authorities": {
                "provenance": {
                    "path": RULES.PROVENANCE_PATH,
                    "digest": RULES._sha256_bytes(self.provenance_path.read_bytes()),
                },
                "customizations": {
                    "path": RULES.CUSTOMIZATIONS_PATH,
                    "digest": RULES._sha256_bytes(self.ledger_path.read_bytes()),
                },
            },
            "rule_dispositions": [
                {
                    "rule_id": "AICTX-EVIDENCE-001",
                    "effective_disposition": "baseline-effective",
                    "applicability": "target uses repository discovery evidence",
                    "evidence": [EVIDENCE],
                    "baseline_acceptance": {
                        "explicit": True,
                        "verification": {"status": "verified", "evidence": [EVIDENCE]},
                    },
                },
                {
                    "rule_id": "TEST-GWT-001",
                    "effective_disposition": "baseline-effective",
                    "applicability": "target test work uses GWT",
                    "evidence": [EVIDENCE],
                    "baseline_acceptance": {
                        "explicit": True,
                        "verification": {"status": "verified", "evidence": [EVIDENCE]},
                    },
                },
            ],
            "routing": routing,
        }
        state["target_state_digest"] = RULES.target_state_digest(state)
        state_path = self.root / RULES.EFFECTIVE_STATE_PATH
        state_path.write_text(
            yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )
        packets_by_route_id = {
            RULES.route_id_for_selector(dict(selector)): RULES.build_packet_candidate(
                self.root, **selector, resolver_evidence=[EVIDENCE]
            )
            for selector, _ in consumer_routes
        }
        for route in state["routing"]:
            route["packet"]["digest"] = packets_by_route_id[route["route_id"]][
                "packet_digest"
            ]
        self.assert_stable_state_digest(state)
        state_path.write_text(
            yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
            newline="\n",
        )
        for route in state["routing"]:
            packet = packets_by_route_id[route["route_id"]]
            packet_path = self.root / route["packet"]["path"]
            packet_path.parent.mkdir(parents=True, exist_ok=True)
            packet_path.write_text(
                yaml.safe_dump(packet, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
                newline="\n",
            )
        return state

    @staticmethod
    def assert_stable_state_digest(state: dict) -> None:
        assert state["target_state_digest"] == RULES.target_state_digest(state)


class EffectiveRuleResolverTests(unittest.TestCase):
    def test_gwt_001_given_verified_explicit_baseline_route_when_resolved_then_packet_has_exact_full_statements(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state()
            packet = RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)

            self.assertEqual(state["routing"][0]["required_rule_ids"], packet["loaded_rule_ids"])
            self.assertEqual("verified", packet["freshness"]["status"])
            self.assertEqual(state["target_state_digest"], packet["target_state"]["digest"])
            self.assertTrue(all(rule["normative_statement"].endswith("\n") for rule in packet["rules"]))
            packet_rules = {rule["rule_id"]: rule for rule in packet["rules"]}
            catalogs = RULES._catalogs_for_profile(fixture.root, "dotnet-backend")
            shared_rule = catalogs["shared"]["rules"]["AICTX-EVIDENCE-001"]
            profile_rule = catalogs["selected-profile"]["rules"]["TEST-GWT-001"]
            self.assertEqual(
                shared_rule["source_governance_provenance"]["normative_text_sha256"],
                packet_rules["AICTX-EVIDENCE-001"]["catalog_normative_statement_digest"],
            )
            self.assertEqual(
                profile_rule["normative_text_sha256"],
                packet_rules["TEST-GWT-001"]["catalog_normative_statement_digest"],
            )
            self.assertEqual(
                state["rule_dispositions"][0],
                packet_rules["AICTX-EVIDENCE-001"]["disposition_record"],
            )
            self.assertEqual([], RULES.validate_effective_rule_state(fixture.root))
        finally:
            fixture.close()

    def test_gwt_001a_given_two_permitted_consumer_routes_for_the_same_rule_when_resolved_then_statement_bytes_and_digest_are_identical(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state(CONSUMER_ROUTES)
            self.assertEqual(2, len(state["routing"]))
            self.assertEqual(
                2,
                len({route["route_id"] for route in state["routing"]}),
            )
            self.assertEqual(
                sorted(route["route_id"] for route in state["routing"]),
                [route["route_id"] for route in state["routing"]],
            )

            shared_rules = []
            for selector, _ in CONSUMER_ROUTES:
                packet = RULES.resolve_effective_rule_packet(fixture.root, **selector)
                shared_rules.append(
                    next(
                        rule
                        for rule in packet["rules"]
                        if rule["rule_id"] == "AICTX-EVIDENCE-001"
                    )
                )

            expected_statement_bytes = shared_rules[0]["normative_statement"].encode(
                "utf-8"
            )
            expected_digest = shared_rules[0]["normative_statement_digest"]
            self.assertEqual(
                RULES._sha256_bytes(expected_statement_bytes),
                expected_digest,
            )
            for rule in shared_rules:
                self.assertEqual("AICTX-EVIDENCE-001", rule["rule_id"])
                self.assertEqual(
                    expected_statement_bytes,
                    rule["normative_statement"].encode("utf-8"),
                )
                self.assertEqual(expected_digest, rule["normative_statement_digest"])
        finally:
            fixture.close()

    def test_gwt_002_given_changed_target_authority_when_resolved_then_state_is_stale_without_default_fallback(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            fixture.write_ready_state()
            fixture.ledger_path.write_text(
                yaml.safe_dump({"schema_version": "1.0", "customizations": []}, sort_keys=False) + "# changed\n",
                encoding="utf-8",
            )

            errors = RULES.validate_effective_rule_state(fixture.root)

            self.assertTrue(any("authority is stale" in error for error in errors))
            with self.assertRaisesRegex(RULES.EffectiveRuleError, "authority is stale"):
                RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
        finally:
            fixture.close()

    def test_gwt_002a_given_malformed_provenance_or_customizations_when_loaded_then_authority_contract_fails_closed_first(self) -> None:
        for authority in ("provenance", "customizations"):
            with self.subTest(authority=authority):
                fixture = EffectiveRuleFixture()
                try:
                    fixture.write_ready_state()
                    if authority == "provenance":
                        document = yaml.safe_load(
                            fixture.provenance_path.read_text(encoding="utf-8")
                        )
                        document.pop("last_migration")
                        path = fixture.provenance_path
                    else:
                        document = {
                            "schema_version": "1.0",
                            "customizations": "malformed",
                        }
                        path = fixture.ledger_path
                    path.write_text(
                        yaml.safe_dump(document, sort_keys=False),
                        encoding="utf-8",
                    )

                    with self.assertRaisesRegex(
                        RULES.EffectiveRuleError,
                        "target authority contract is malformed",
                    ):
                        RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
                finally:
                    fixture.close()

    def test_gwt_003_given_missing_exact_route_when_resolved_then_it_fails_closed_instead_of_scanning_documents(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            fixture.write_ready_state()
            request = {**REQUEST, "file_type": "csharp-production"}

            with self.assertRaisesRegex(RULES.EffectiveRuleError, "no exact route"):
                RULES.resolve_effective_rule_packet(fixture.root, **request)
        finally:
            fixture.close()

    def test_gwt_004_given_packet_statement_or_digest_mismatch_when_resolved_then_it_fails_closed(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state()
            packet_path = fixture.root / state["routing"][0]["packet"]["path"]
            packet = yaml.safe_load(packet_path.read_text(encoding="utf-8"))
            packet["rules"][0]["normative_statement"] = "temporary summary\n"
            packet_path.write_text(yaml.safe_dump(packet, sort_keys=False), encoding="utf-8")

            with self.assertRaisesRegex(RULES.EffectiveRuleError, "exact effective semantics"):
                RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
        finally:
            fixture.close()

    def test_gwt_005_given_unverified_baseline_or_unpacketized_identity_when_prepared_then_it_fails_closed(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state()
            state_path = fixture.root / RULES.EFFECTIVE_STATE_PATH
            invalid = copy.deepcopy(state)
            invalid["rule_dispositions"][0]["baseline_acceptance"]["explicit"] = False
            invalid["target_state_digest"] = RULES.target_state_digest(invalid)
            state_path.write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
            self.assertTrue(any("explicit verified baseline" in error for error in RULES.validate_effective_rule_state(fixture.root)))

            invalid = copy.deepcopy(state)
            invalid["routing"][0]["required_rule_ids"] = ["AICTX-EVIDENCE-001", "UNPACKETIZED-001"]
            invalid["target_state_digest"] = RULES.target_state_digest(invalid)
            state_path.write_text(yaml.safe_dump(invalid, sort_keys=False), encoding="utf-8")
            self.assertTrue(any("unknown, or unpacketized" in error for error in RULES.validate_effective_rule_state(fixture.root)))
        finally:
            fixture.close()

    def test_gwt_005a_given_effective_state_without_exact_provenance_linkage_when_resolved_then_it_fails_closed(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            fixture.write_ready_state()
            provenance = yaml.safe_load(fixture.provenance_path.read_text(encoding="utf-8"))
            provenance.pop("effective_rules")
            fixture.provenance_path.write_text(
                yaml.safe_dump(provenance, sort_keys=False),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RULES.EffectiveRuleError, "provenance linkage"):
                RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
        finally:
            fixture.close()

    def test_gwt_006_given_structural_target_without_effective_state_when_readiness_checked_then_actions_remain_unresolved(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            readiness = TARGET.effective_rule_readiness(fixture.root)

            self.assertFalse(readiness["action_ready"])
            self.assertEqual("unresolved", readiness["status"])
            self.assertEqual("effective-rule-state-missing", readiness["reason"])
        finally:
            fixture.close()

    def test_gwt_006b_given_profile_traversal_or_malformed_state_path_when_validated_then_target_fails_closed(self) -> None:
        for profile in ("../dotnet-backend", "dotnet/backend", "dotnet\\backend", "Dotnet", "dotnet."):
            with self.subTest(profile=profile):
                with self.assertRaisesRegex(
                    RULES.EffectiveRuleError,
                    "lowercase single-segment slug",
                ):
                    RULES._profile_catalog_path(profile)

        fixture = EffectiveRuleFixture()
        try:
            provenance = yaml.safe_load(
                fixture.provenance_path.read_text(encoding="utf-8")
            )
            provenance["selection"]["profiles"] = ["../dotnet-backend"]
            fixture.provenance_path.write_text(
                yaml.safe_dump(provenance, sort_keys=False),
                encoding="utf-8",
            )
            self.assertTrue(
                any(
                    "lowercase single-segment slugs" in error
                    for error in TARGET.validate_target(fixture.root)
                )
            )
        finally:
            fixture.close()

        malformed_fixture = EffectiveRuleFixture()
        try:
            (malformed_fixture.root / RULES.EFFECTIVE_STATE_PATH).mkdir()
            self.assertTrue(
                any(
                    "exists but is not a regular file" in error
                    for error in TARGET.validate_target(malformed_fixture.root)
                )
            )
        finally:
            malformed_fixture.close()

    def test_gwt_006c_given_symlinked_state_leaf_or_packet_parent_when_loaded_then_read_is_rejected(self) -> None:
        for boundary in ("state-leaf", "packet-parent"):
            with self.subTest(boundary=boundary):
                fixture = EffectiveRuleFixture()
                try:
                    state = fixture.write_ready_state()
                    if boundary == "state-leaf":
                        link = fixture.root / RULES.EFFECTIVE_STATE_PATH
                        target = link.with_name("effective-rules.real.yaml")
                        link.replace(target)
                        target_is_directory = False
                    else:
                        packet = fixture.root / state["routing"][0]["packet"]["path"]
                        link = packet.parent
                        target = link.with_name("effective-rule-packets-real")
                        link.replace(target)
                        target_is_directory = True
                    try:
                        link.symlink_to(target, target_is_directory=target_is_directory)
                    except OSError as exc:
                        self.skipTest(f"symlink creation is unavailable: {exc}")

                    with self.assertRaisesRegex(RULES.EffectiveRuleError, "regular"):
                        RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
                finally:
                    fixture.close()

    def test_gwt_006a_given_structural_initialization_or_finalization_without_state_when_returned_then_action_readiness_is_unresolved(self) -> None:
        initialized_temporary = tempfile.TemporaryDirectory(prefix="effective-rules-initialized-")
        initialized_root = Path(initialized_temporary.name)
        finalized_fixture = EffectiveRuleFixture()
        try:
            initialized = TARGET.initialize_context(
                initialized_root,
                SOURCE,
                SELECTION,
                "2026-08-05T00:00:00+00:00",
            )
            self.assertFalse(initialized["effective_rule_readiness"]["action_ready"])
            self.assertEqual(
                "effective-rule-state-missing",
                initialized["effective_rule_readiness"]["reason"],
            )

            provenance, ledger = TARGET.build_initialization_documents(
                SOURCE,
                SELECTION,
                "2026-08-05T00:00:00+00:00",
            )
            finalized = TARGET.finalize_context(
                finalized_fixture.root,
                provenance,
                ledger,
            )
            self.assertEqual("finalized", finalized["status"])
            self.assertFalse(finalized["effective_rule_readiness"]["action_ready"])
            self.assertEqual(
                "effective-rule-state-missing",
                finalized["effective_rule_readiness"]["reason"],
            )
        finally:
            finalized_fixture.close()
            initialized_temporary.cleanup()

    def test_gwt_007_given_package_migration_targets_effective_state_or_packet_when_checked_then_it_is_reserved(self) -> None:
        self.assertTrue(RULES.EFFECTIVE_STATE_PATH.endswith("effective-rules.yaml"))
        sys.path.insert(0, str(ROOT / ".ai/scripts"))
        import ai_context_package_apply as apply

        self.assertTrue(apply.is_target_effective_rule_path(RULES.EFFECTIVE_STATE_PATH))
        self.assertTrue(apply.is_target_effective_rule_path(RULES.PACKET_DIRECTORY))
        self.assertTrue(
            apply.is_target_effective_rule_path(
                f"{RULES.PACKET_DIRECTORY}/ROUTE-ABC.yaml"
            )
        )
        self.assertFalse(apply.is_target_effective_rule_path(".ai/assets/README.MD"))

    def test_gwt_008_given_explicit_reconciliation_candidate_when_staged_packets_first_and_state_last_then_result_is_ready(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            candidate = {
                "schema_version": "1.0",
                "framework": {
                    "version": SOURCE["version"],
                    "commit": SOURCE["commit"],
                    "selected_technology_profile": "dotnet-backend",
                },
                "rule_dispositions": [
                    {
                        "rule_id": "AICTX-EVIDENCE-001",
                        "effective_disposition": "baseline-effective",
                        "applicability": "target uses repository discovery evidence",
                        "evidence": [EVIDENCE],
                        "baseline_acceptance": {
                            "explicit": True,
                            "verification": {"status": "verified", "evidence": [EVIDENCE]},
                        },
                    },
                    {
                        "rule_id": "TEST-GWT-001",
                        "effective_disposition": "baseline-effective",
                        "applicability": "target test work uses GWT",
                        "evidence": [EVIDENCE],
                        "baseline_acceptance": {
                            "explicit": True,
                            "verification": {"status": "verified", "evidence": [EVIDENCE]},
                        },
                    },
                ],
                "routing": [
                    {
                        "selector": REQUEST,
                        "required_rule_ids": ["AICTX-EVIDENCE-001", "TEST-GWT-001"],
                        "reported_not_applicable_rule_ids": [],
                    }
                ],
            }
            state, packets = RULES.build_effective_state_and_packets(
                fixture.root, candidate, resolver_evidence=[EVIDENCE]
            )
            publication = RULES.write_effective_state_and_packets(
                fixture.root, state, packets
            )

            self.assertEqual(state["target_state_digest"], publication["target_state_digest"])
            self.assertEqual(1, len(publication["packet_paths"]))
            self.assertEqual([], RULES.validate_effective_rule_state(fixture.root))
            self.assertEqual(
                ["AICTX-EVIDENCE-001", "TEST-GWT-001"],
                RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)["loaded_rule_ids"],
            )

            state_before = (fixture.root / RULES.EFFECTIVE_STATE_PATH).read_bytes()
            invalid_state = copy.deepcopy(state)
            invalid_state["target_state_digest"] = "0" * 64
            with self.assertRaisesRegex(RULES.EffectiveRuleError, "digest mismatch"):
                RULES.write_effective_state_and_packets(
                    fixture.root, invalid_state, packets
                )
            self.assertEqual(state_before, (fixture.root / RULES.EFFECTIVE_STATE_PATH).read_bytes())
        finally:
            fixture.close()

    def test_gwt_008a_given_non_directory_packet_parent_when_published_then_parent_chain_fails_before_state_replacement(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state()
            packet_path = fixture.root / state["routing"][0]["packet"]["path"]
            packet = yaml.safe_load(packet_path.read_text(encoding="utf-8"))
            packet_path.unlink()
            packet_path.parent.rmdir()
            packet_path.parent.write_text("not a directory\n", encoding="utf-8")
            state_before = (fixture.root / RULES.EFFECTIVE_STATE_PATH).read_bytes()

            with self.assertRaisesRegex(RULES.EffectiveRuleError, "regular directory"):
                RULES.write_effective_state_and_packets(
                    fixture.root,
                    state,
                    {state["routing"][0]["packet"]["path"]: packet},
                )
            self.assertEqual(state_before, (fixture.root / RULES.EFFECTIVE_STATE_PATH).read_bytes())
        finally:
            fixture.close()

    def test_gwt_008b_given_finalized_same_rule_delta_when_resolved_then_packet_is_self_contained_and_binds_catalog_baseline(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state()
            effective_statement = "Target unit-of-work decisions require explicit owner evidence.\n"
            customization = {
                "id": "CUST-ARCH-UOW-001",
                "subject": {"kind": "rule", "id": "ARCH-UOW-001"},
                "relationship": "deviates",
                "reason": "Target requires additional owner evidence.",
                "paths": [EVIDENCE],
                "base_framework": {
                    "version": SOURCE["version"],
                    "commit": SOURCE["commit"],
                    "evidence": [EVIDENCE],
                },
                "dependencies": {"customization_ids": [], "subject_refs": []},
                "owner_reconciliation": {
                    "status": "approved",
                    "owner": "repository-owner",
                    "decided_at": "2026-08-05T00:00:00+00:00",
                    "evidence": EVIDENCE,
                },
                "decision_evidence": {
                    "requirements": [],
                    "adrs": [],
                    "workflows": [EVIDENCE],
                },
                "active_context_audit": {
                    "assessment_id": "ASM-20260804-002",
                    "status": "verified",
                    "evidence": EVIDENCE,
                },
                "incoming": {
                    "version": SOURCE["version"],
                    "status": "conflicting",
                    "evidence": EVIDENCE,
                },
                "disposition": "retain",
                "post_upgrade_audit": {
                    "assessment_id": "ASM-20260804-002",
                    "status": "verified",
                    "evidence": EVIDENCE,
                },
                "validation": ["owner-approved semantic reconciliation"],
            }
            fixture.ledger_path.write_text(
                yaml.safe_dump(
                    {"schema_version": "1.0", "customizations": [customization]},
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            delta_record = {
                "rule_id": "ARCH-UOW-001",
                "effective_disposition": "target-semantic-delta",
                "applicability": "target unit-of-work decisions",
                "evidence": [EVIDENCE],
                "semantic_delta": {
                    "customization_id": customization["id"],
                    "reconciliation_ref": EVIDENCE,
                    "effective_normative_statement": effective_statement,
                    "effective_normative_statement_digest": RULES._sha256_bytes(
                        effective_statement.encode("utf-8")
                    ),
                },
            }
            state["target_authorities"]["customizations"]["digest"] = RULES._sha256_bytes(
                fixture.ledger_path.read_bytes()
            )
            state["rule_dispositions"][1] = delta_record
            state["routing"][0]["required_rule_ids"] = [
                "AICTX-EVIDENCE-001",
                "ARCH-UOW-001",
            ]
            state["routing"][0]["packet"]["digest"] = "0" * 64
            state["target_state_digest"] = RULES.target_state_digest(state)
            state_path = fixture.root / RULES.EFFECTIVE_STATE_PATH
            state_path.write_text(
                yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            packet = RULES.build_packet_candidate(
                fixture.root, **REQUEST, resolver_evidence=[EVIDENCE]
            )
            state["routing"][0]["packet"]["digest"] = packet["packet_digest"]
            state_path.write_text(
                yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            packet_path = fixture.root / state["routing"][0]["packet"]["path"]
            packet_path.write_text(
                yaml.safe_dump(packet, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

            resolved = RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
            delta_packet = next(
                rule for rule in resolved["rules"] if rule["rule_id"] == "ARCH-UOW-001"
            )
            self.assertEqual(effective_statement, delta_packet["normative_statement"])
            self.assertEqual(delta_record, delta_packet["disposition_record"])
            self.assertNotEqual(
                delta_packet["catalog_normative_statement_digest"],
                delta_packet["normative_statement_digest"],
            )
        finally:
            fixture.close()

    def test_gwt_008c_given_not_applicable_rule_when_routed_then_reported_subset_must_be_exact(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            state = fixture.write_ready_state()
            not_applicable = {
                "rule_id": "TEST-GWT-001",
                "effective_disposition": "not-applicable",
                "applicability": "target does not execute test design",
                "evidence": [EVIDENCE],
                "not_applicable": {
                    "predicate": "test-design capability absent",
                    "verification": EVIDENCE,
                },
            }
            state["rule_dispositions"][1] = not_applicable
            state["routing"][0]["reported_not_applicable_rule_ids"] = ["TEST-GWT-001"]
            state["routing"][0]["packet"]["digest"] = "0" * 64
            state["target_state_digest"] = RULES.target_state_digest(state)
            state_path = fixture.root / RULES.EFFECTIVE_STATE_PATH
            state_path.write_text(
                yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            packet = RULES.build_packet_candidate(
                fixture.root, **REQUEST, resolver_evidence=[EVIDENCE]
            )
            state["routing"][0]["packet"]["digest"] = packet["packet_digest"]
            state_path.write_text(
                yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            packet_path = fixture.root / state["routing"][0]["packet"]["path"]
            packet_path.write_text(
                yaml.safe_dump(packet, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            resolved = RULES.resolve_effective_rule_packet(fixture.root, **REQUEST)
            self.assertIn("TEST-GWT-001", resolved["loaded_rule_ids"])

            invalid = copy.deepcopy(state)
            invalid["routing"][0]["reported_not_applicable_rule_ids"] = []
            invalid["target_state_digest"] = RULES.target_state_digest(invalid)
            state_path.write_text(
                yaml.safe_dump(invalid, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            self.assertTrue(
                any(
                    "does not exactly match the not-applicable subset" in error
                    for error in RULES.validate_effective_rule_state(fixture.root)
                )
            )
        finally:
            fixture.close()

    def test_gwt_009_given_existing_effective_state_when_finalization_lacks_regeneration_then_it_fails_before_provenance_mutation(self) -> None:
        fixture = EffectiveRuleFixture()
        try:
            fixture.write_ready_state()
            provenance_before = fixture.provenance_path.read_bytes()
            ledger_before = fixture.ledger_path.read_bytes()

            with self.assertRaisesRegex(
                TARGET.TargetValidationError,
                "requires regeneration candidate",
            ):
                TARGET.finalize_context(fixture.root, {"schema_version": "2.0"}, {})

            self.assertEqual(provenance_before, fixture.provenance_path.read_bytes())
            self.assertEqual(ledger_before, fixture.ledger_path.read_bytes())
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
