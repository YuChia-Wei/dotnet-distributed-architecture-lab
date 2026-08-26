#!/usr/bin/env python3
"""Deterministic, fixture-local acceptance for provider-neutral role execution.

This oracle deliberately validates only the acceptance fixture shape.  It is
not a production validator and does not reinterpret #114 loaded-rule packets.
"""

from __future__ import annotations

import copy
import unittest
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[6]
FIXTURE = (
    ROOT
    / ".ai/assets/skills/software-development-orchestrator/fixtures/acceptance/"
    "role-execution-provider-neutral.yaml"
)

ROLE_BINDINGS = {
    "command-sub-agent": "slice-implementer",
    "usecase-test-sub-agent": "slice-implementer",
    "code-review-sub-agent": "code-reviewer",
    "problem-frame-sub-agent": "problem-frame-author",
    "context-translator": "ai-context-init",
}
REQUIRED_RECORD_FIELDS = {
    "role_execution_id",
    "role_asset_id",
    "role_path",
    "owning_skill",
    "stage_id",
    "applicability",
    "selection",
    "input_envelope",
    "permissions",
    "executor",
    "invocation_evidence",
    "output",
    "attempts",
    "fallback",
    "final_integration_owner",
}
SAFETY_GATES = {
    "applicable_role",
    "current_session_runtime_support_verified",
    "bounded_input_output_permissions_stop",
    "approval_security_credential_boundaries_satisfied",
    "disjoint_mutation_scope",
    "named_parent_and_final_integration_owner",
}
INLINE_PARITY_FIELDS = {
    "same_role_path_and_mandatory_references",
    "bounded_input_output_permissions_stop",
    "approval_security_credential_boundaries_satisfied",
    "disjoint_mutation_scope",
    "named_parent_and_final_integration_owner",
    "current_inline_support_verified",
}
MATERIAL_VALUE_TRIGGERS = {
    "independent_parallel_substantive_unit",
    "meaningful_isolation",
    "specialist_context_benefit",
    "elapsed_time_benefit",
}


def load_fixture() -> dict[str, Any]:
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError("role execution fixture must be a mapping")
    return data


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: Any, *, non_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not non_empty)
        and all(is_non_empty_string(item) for item in value)
    )


def add_if_missing_mapping(
    value: Any,
    required: set[str],
    errors: list[str],
    label: str,
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be a mapping")
        return None
    missing = required - set(value)
    if missing:
        errors.append(f"{label} missing {', '.join(sorted(missing))}")
    return value


def validate_executor(
    executor: Any,
    disposition: str,
    errors: list[str],
    label: str,
) -> None:
    if disposition in {"not-applicable", "unavailable"} and executor is None:
        return
    mapping = add_if_missing_mapping(
        executor, {"kind", "identity", "runtime_support_verified"}, errors, label
    )
    if mapping is None:
        return
    expected_kind = "runtime-worker" if disposition == "delegated" else "parent-inline"
    if mapping.get("kind") != expected_kind:
        errors.append(f"{label}.kind must be {expected_kind}")
    if not is_non_empty_string(mapping.get("identity")):
        errors.append(f"{label}.identity must be a session-safe non-empty reference")
    if mapping.get("runtime_support_verified") is not True:
        errors.append(f"{label}.runtime_support_verified must be true")


def validate_invocation(value: Any, errors: list[str], label: str) -> None:
    invocation = add_if_missing_mapping(
        value,
        {"invocation_id", "started_at", "completed_at", "outcome", "evidence_refs"},
        errors,
        label,
    )
    if invocation is None:
        return
    for field in ("invocation_id", "started_at", "completed_at", "outcome"):
        if not is_non_empty_string(invocation.get(field)):
            errors.append(f"{label}.{field} must be non-empty")
    if not is_string_list(invocation.get("evidence_refs")):
        errors.append(f"{label}.evidence_refs must be non-empty")


def validate_role_execution(
    record: Any,
    errors: list[str],
    *,
    label: str = "role_execution",
) -> None:
    """Fail-close a single fixture record against the canonical acceptance shape."""
    mapping = add_if_missing_mapping(record, REQUIRED_RECORD_FIELDS, errors, label)
    if mapping is None:
        return
    for field in ("role_execution_id", "role_asset_id", "role_path", "owning_skill", "stage_id"):
        if not is_non_empty_string(mapping.get(field)):
            errors.append(f"{label}.{field} must be non-empty")

    role_asset_id = mapping.get("role_asset_id")
    expected_owner = ROLE_BINDINGS.get(role_asset_id)
    expected_path = ".ai/assets/sub-agent-role-prompts/{}/sub-agent.yaml".format(role_asset_id)
    if expected_owner is None:
        errors.append(f"{label}.role_asset_id must be an existing #118 binding")
    else:
        if mapping.get("owning_skill") != expected_owner:
            errors.append(f"{label}.owning_skill must match the #118 role binding")
        if mapping.get("role_path") != expected_path:
            errors.append(f"{label}.role_path must be the exact canonical sub-agent.yaml path")
        manifest_path = ROOT / mapping.get("role_path", "")
        if not manifest_path.is_file():
            errors.append(f"{label}.role_path must resolve to an existing role manifest")
        else:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict) or manifest.get("references") is None:
                errors.append(f"{label}.role_path must resolve to a role manifest with references")
            else:
                expected_references = manifest["references"]
                actual_envelope = mapping.get("input_envelope")
                actual_references = actual_envelope.get("mandatory_references") if isinstance(actual_envelope, dict) else None
                if actual_references != expected_references:
                    errors.append(f"{label}.input_envelope.mandatory_references must match the role manifest references")
    if mapping.get("owning_skill") == "software-development-orchestrator":
        errors.append("software-development-orchestrator cannot own a domain stage output")

    applicability = add_if_missing_mapping(
        mapping.get("applicability"), {"result", "reason"}, errors, f"{label}.applicability"
    )
    selection = add_if_missing_mapping(
        mapping.get("selection"), {"disposition", "reason", "delegation_evaluation"}, errors, f"{label}.selection"
    )
    if applicability is None or selection is None:
        return
    applies = applicability.get("result")
    disposition = selection.get("disposition")
    if applies not in {"applies", "does-not-apply"}:
        errors.append(f"{label}.applicability.result is invalid")
    if not is_non_empty_string(applicability.get("reason")) or not is_non_empty_string(selection.get("reason")):
        errors.append(f"{label} applicability and selection reasons must be evidence-backed")
    if applies == "does-not-apply":
        if disposition != "not-applicable":
            errors.append(f"{label} does-not-apply requires not-applicable disposition")
        if selection.get("delegation_evaluation") is not None:
            errors.append(f"{label} does-not-apply requires null delegation_evaluation")
    else:
        if disposition not in {"direct", "delegated", "unavailable"}:
            errors.append(f"{label} applies requires direct, delegated, or unavailable disposition")
        evaluation = add_if_missing_mapping(
            selection.get("delegation_evaluation"),
            {"safety_gates", "material_value_triggers", "cost_failure_retry_risk"},
            errors,
            f"{label}.selection.delegation_evaluation",
        )
        if evaluation is not None:
            gates = add_if_missing_mapping(
                evaluation.get("safety_gates"), SAFETY_GATES, errors, f"{label}.selection.safety_gates"
            )
            triggers = evaluation.get("material_value_triggers")
            risk = add_if_missing_mapping(
                evaluation.get("cost_failure_retry_risk"), {"result", "reason"}, errors, f"{label}.selection.cost_failure_retry_risk"
            )
            if not isinstance(triggers, list) or any(item not in MATERIAL_VALUE_TRIGGERS for item in triggers):
                errors.append(f"{label}.selection.material_value_triggers is invalid")
            if risk is not None and (risk.get("result") not in {"supports-delegation", "favors-direct"} or not is_non_empty_string(risk.get("reason"))):
                errors.append(f"{label}.selection.cost_failure_retry_risk is invalid")
            if disposition == "delegated" and (
                gates is None
                or not all(gates.get(key) is True for key in SAFETY_GATES)
                or not triggers
                or risk is None
                or risk.get("result") != "supports-delegation"
            ):
                errors.append(f"{label} delegated selection requires all safety gates, material value, and supports-delegation")

    envelope = add_if_missing_mapping(
        mapping.get("input_envelope"),
        {"goal", "scope", "non_goals", "source_refs", "mandatory_references", "constraints", "stop_conditions"},
        errors,
        f"{label}.input_envelope",
    )
    if envelope is not None:
        if not is_non_empty_string(envelope.get("goal")):
            errors.append(f"{label}.input_envelope.goal must be non-empty")
        for field in ("scope", "source_refs", "mandatory_references", "constraints", "stop_conditions"):
            if not is_string_list(envelope.get(field)):
                errors.append(f"{label}.input_envelope.{field} must be non-empty")
        if not is_string_list(envelope.get("non_goals"), non_empty=False):
            errors.append(f"{label}.input_envelope.non_goals must be a string list")
    permissions = add_if_missing_mapping(
        mapping.get("permissions"), {"read_scope", "write_scope", "external_actions", "secret_handling"}, errors, f"{label}.permissions"
    )
    if permissions is not None:
        for field in ("read_scope", "write_scope", "external_actions"):
            if not is_string_list(permissions.get(field), non_empty=False):
                errors.append(f"{label}.permissions.{field} must be a string list")
        if permissions.get("secret_handling") != "no-secret-values":
            errors.append(f"{label}.permissions.secret_handling must be no-secret-values")

    output = add_if_missing_mapping(
        mapping.get("output"), {"expected", "returned", "evidence_refs", "bounded"}, errors, f"{label}.output"
    )
    if output is not None:
        for field in ("expected", "returned"):
            if not is_string_list(output.get(field), non_empty=False):
                errors.append(f"{label}.output.{field} must be a string list")
        if not is_string_list(output.get("evidence_refs")) or output.get("bounded") is not True:
            errors.append(f"{label}.output requires evidence_refs and bounded true")

    final_owner = add_if_missing_mapping(
        mapping.get("final_integration_owner"), {"owner", "decision", "evidence_refs"}, errors, f"{label}.final_integration_owner"
    )
    if final_owner is not None:
        if not is_non_empty_string(final_owner.get("owner")):
            errors.append(f"{label}.final_integration_owner must name a parent/integration owner")
        if final_owner.get("decision") not in {"pending", "accepted", "rejected", "reconciled"}:
            errors.append(f"{label}.final_integration_owner.decision is invalid")
        if not is_string_list(final_owner.get("evidence_refs")):
            errors.append(f"{label}.final_integration_owner.evidence_refs must be non-empty")

    attempts = mapping.get("attempts")
    if not isinstance(attempts, list):
        errors.append(f"{label}.attempts must be a list")
        attempts = []

    top_executor = mapping.get("executor")
    top_invocation = mapping.get("invocation_evidence")
    if disposition == "direct":
        validate_executor(top_executor, "direct", errors, f"{label}.executor")
        if top_invocation is not None:
            errors.append("direct selection must not carry invocation_evidence")
    elif disposition == "delegated":
        validate_executor(top_executor, "delegated", errors, f"{label}.executor")
        if top_invocation is None:
            errors.append("delegated selection requires genuine invocation_evidence")
        else:
            validate_invocation(top_invocation, errors, f"{label}.invocation_evidence")
    elif disposition == "not-applicable":
        if top_executor is not None or top_invocation is not None:
            errors.append(f"{label} not-applicable requires null top-level executor and invocation_evidence")
    elif disposition == "unavailable" and not attempts:
        if top_executor is not None or top_invocation is not None:
            errors.append(f"{label} unavailable before execution requires null top-level executor and invocation_evidence")
    if disposition == "not-applicable" and attempts:
        errors.append(f"{label} not-applicable must have no attempts")
    if disposition in {"direct", "delegated"} and not attempts:
        errors.append(f"{label} selected execution requires attempt 1")
    for index, attempt in enumerate(attempts, start=1):
        attempt_label = f"{label}.attempts[{index}]"
        attempt_map = add_if_missing_mapping(
            attempt,
            {"number", "disposition", "executor", "invocation_evidence", "outcome", "correctable_failure", "material_state_change", "authorization_source", "evidence_refs"},
            errors,
            attempt_label,
        )
        if attempt_map is None:
            continue
        if attempt_map.get("number") != index:
            errors.append(f"{attempt_label}.number must be {index}")
        attempt_disposition = attempt_map.get("disposition")
        if attempt_disposition not in {"direct", "delegated", "unavailable"}:
            errors.append(f"{attempt_label}.disposition is invalid")
            continue
        validate_executor(attempt_map.get("executor"), attempt_disposition, errors, f"{attempt_label}.executor")
        invocation = attempt_map.get("invocation_evidence")
        if attempt_disposition == "delegated":
            if invocation is None:
                errors.append("delegated attempt requires genuine invocation_evidence")
            else:
                validate_invocation(invocation, errors, f"{attempt_label}.invocation_evidence")
        elif invocation is not None:
            errors.append(f"{attempt_label} {attempt_disposition} must not carry invocation_evidence")
        if not is_non_empty_string(attempt_map.get("outcome")) or not isinstance(attempt_map.get("correctable_failure"), bool):
            errors.append(f"{attempt_label} outcome and correctable_failure are invalid")
        if not isinstance(attempt_map.get("material_state_change"), str):
            errors.append(f"{attempt_label}.material_state_change must be a string")
        if not is_string_list(attempt_map.get("authorization_source"), non_empty=False) or not is_string_list(attempt_map.get("evidence_refs")):
            errors.append(f"{attempt_label} authorization_source/evidence_refs are invalid")
        if index == 2:
            prior = attempts[0] if isinstance(attempts[0], dict) else {}
            if prior.get("correctable_failure") is not True or not is_non_empty_string(prior.get("material_state_change")):
                errors.append("attempt 2 requires attempt 1 correctable_failure and material_state_change")
        if index >= 3:
            current_authorization = attempt_map.get("authorization_source")
            if not is_string_list(current_authorization):
                errors.append(f"attempt {index} requires fresh authorization")
            else:
                prior_authorization = set()
                for prior_attempt in attempts[: index - 1]:
                    if not isinstance(prior_attempt, dict):
                        continue
                    prior_sources = prior_attempt.get("authorization_source")
                    if isinstance(prior_sources, list):
                        prior_authorization.update(
                            reference for reference in prior_sources if is_non_empty_string(reference)
                        )
                if not any(reference not in prior_authorization for reference in current_authorization):
                    errors.append(
                        f"attempt {index} authorization must include a reference not used by an earlier attempt"
                    )

    if attempts:
        last_attempt = attempts[-1] if isinstance(attempts[-1], dict) else {}
        if mapping.get("executor") != last_attempt.get("executor") or mapping.get("invocation_evidence") != last_attempt.get("invocation_evidence"):
            errors.append(f"{label} top-level executor and invocation_evidence must summarize the final attempt")

    fallback = add_if_missing_mapping(
        mapping.get("fallback"), {"considered", "reason", "resulting_disposition", "inline_contract_evidence"}, errors, f"{label}.fallback"
    )
    if fallback is not None:
        result = fallback.get("resulting_disposition")
        if not isinstance(fallback.get("considered"), bool):
            errors.append(f"{label}.fallback.considered must be boolean")
        if not is_non_empty_string(fallback.get("reason")) or result not in {None, "direct", "unavailable"}:
            errors.append(f"{label}.fallback is invalid")
        parity = add_if_missing_mapping(
            fallback.get("inline_contract_evidence"),
            INLINE_PARITY_FIELDS | {"evidence_refs"},
            errors,
            f"{label}.fallback.inline_contract_evidence",
        )
        if parity is not None and not is_string_list(parity.get("evidence_refs"), non_empty=False):
            errors.append(f"{label}.fallback.inline_contract_evidence.evidence_refs must be a string list")
        if result is None:
            if fallback.get("considered") is not False or (
                parity is not None and any(parity.get(field) is not False for field in INLINE_PARITY_FIELDS)
            ):
                errors.append(f"{label}.fallback no-result requires considered false and all parity gates false")
        if result == "direct":
            has_failed_delegated_attempt = any(
                isinstance(item, dict)
                and item.get("disposition") == "delegated"
                and item.get("outcome") == "failed"
                for item in attempts
            )
            if fallback.get("considered") is not True:
                errors.append(f"{label}.fallback direct requires considered true")
            if disposition != "direct" or not has_failed_delegated_attempt:
                errors.append(f"{label}.fallback direct requires a failed delegated attempt and final direct disposition")
            if parity is not None and (
                not all(parity.get(field) is True for field in INLINE_PARITY_FIELDS)
                or not is_string_list(parity.get("evidence_refs"))
            ):
                errors.append(f"{label}.fallback direct requires complete inline parity evidence")
        elif result == "unavailable":
            if fallback.get("considered") is not True or disposition != "unavailable":
                errors.append(f"{label}.fallback unavailable requires final unavailable disposition")
            if not any(
                isinstance(item, dict)
                and item.get("disposition") == "delegated"
                and item.get("outcome") == "failed"
                for item in attempts
            ):
                errors.append(f"{label}.fallback unavailable requires a failed delegated attempt")
            if parity is not None and all(parity.get(field) is True for field in INLINE_PARITY_FIELDS):
                errors.append(f"{label}.fallback unavailable requires at least one inline parity gate to be false")


class RoleExecutionAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = load_fixture()
        self.scenarios = self.fixture["scenarios"]

    def test_gwt_001_given_acceptance_fixture_when_records_are_checked_then_each_expected_outcome_matches(self) -> None:
        for scenario in self.scenarios:
            record = scenario.get("role_execution")
            if record is None:
                continue
            errors: list[str] = []
            validate_role_execution(record, errors, label=scenario["scenario_id"])
            if scenario["expected_valid"]:
                self.assertEqual([], errors, scenario["scenario_id"])
            else:
                self.assertIn(scenario["expected_error"], errors, scenario["scenario_id"])

    def test_gwt_002_given_aggregate_when_parent_integrates_then_stage_outputs_remain_owned_and_preserved(self) -> None:
        records = {
            scenario["role_execution"]["role_execution_id"]: scenario["role_execution"]
            for scenario in self.scenarios
            if "role_execution" in scenario and scenario["expected_valid"]
        }
        aggregate = next(scenario["aggregate"] for scenario in self.scenarios if "aggregate" in scenario)
        self.assertEqual("workflow-parent", aggregate["final_integration_owner"]["owner"])
        self.assertEqual("accepted", aggregate["final_integration_owner"]["decision"])
        self.assertTrue(aggregate["final_integration_owner"]["evidence_refs"])
        for record_id, stage_id in zip(aggregate["records"], aggregate["preserved_stage_outputs"]):
            record = records[record_id]
            self.assertEqual(stage_id, record["stage_id"])
            self.assertNotEqual("software-development-orchestrator", record["owning_skill"])
            self.assertEqual("workflow-parent", record["final_integration_owner"]["owner"])

    def test_gwt_003_given_bdd_design_when_concrete_test_role_is_selected_then_bdd_stays_a_source_not_a_role_execution(self) -> None:
        record = next(
            scenario["role_execution"]
            for scenario in self.scenarios
            if scenario["scenario_id"] == "test-design-to-generic-slice-implementation-handoff"
        )
        self.assertEqual("usecase-test-sub-agent", record["role_asset_id"])
        self.assertEqual("slice-implementer", record["owning_skill"])
        self.assertTrue(any(ref.startswith("bdd-design-output:") for ref in record["input_envelope"]["source_refs"]))
        self.assertFalse(any(
            scenario.get("role_execution", {}).get("owning_skill") == "bdd-gwt-test-designer"
            for scenario in self.scenarios
        ))

    def test_gwt_004_given_loaded_rule_packet_reference_when_fixture_is_checked_then_it_stays_opaque(self) -> None:
        record = self.scenarios[0]["role_execution"]
        self.assertNotIn("loaded_rule_ids", record)
        self.assertIn("loaded-rule-packet:opaque", record["input_envelope"]["source_refs"])
        errors: list[str] = []
        validate_role_execution(record, errors)
        self.assertEqual([], errors)

    def test_gwt_005_given_orchestrator_domain_ownership_when_mutated_then_the_fixture_oracle_fails_closed(self) -> None:
        record = copy.deepcopy(self.scenarios[0]["role_execution"])
        record["owning_skill"] = "software-development-orchestrator"
        errors: list[str] = []
        validate_role_execution(record, errors)
        self.assertIn("software-development-orchestrator cannot own a domain stage output", errors)

    def test_gwt_006_given_parity_summary_or_binding_mutations_when_checked_then_the_oracle_fails_closed(self) -> None:
        fallback_record = copy.deepcopy(next(
            scenario["role_execution"]
            for scenario in self.scenarios
            if scenario["scenario_id"] == "delegated-failure-fallback-equivalent-direct"
        ))
        fallback_record["fallback"]["inline_contract_evidence"]["current_inline_support_verified"] = False
        errors: list[str] = []
        validate_role_execution(fallback_record, errors)
        self.assertIn("role_execution.fallback direct requires complete inline parity evidence", errors)

        summary_record = copy.deepcopy(self.scenarios[0]["role_execution"])
        summary_record["executor"] = {
            **summary_record["executor"],
            "identity": "parent-session:mismatched-summary",
        }
        errors = []
        validate_role_execution(summary_record, errors)
        self.assertIn("role_execution top-level executor and invocation_evidence must summarize the final attempt", errors)

        binding_record = copy.deepcopy(self.scenarios[0]["role_execution"])
        binding_record["owning_skill"] = "code-reviewer"
        errors = []
        validate_role_execution(binding_record, errors)
        self.assertIn("role_execution.owning_skill must match the #118 role binding", errors)

        fallback_record = copy.deepcopy(next(
            scenario["role_execution"]
            for scenario in self.scenarios
            if scenario["scenario_id"] == "delegated-failure-fallback-equivalent-direct"
        ))
        fallback_record["fallback"]["considered"] = False
        errors = []
        validate_role_execution(fallback_record, errors)
        self.assertIn("role_execution.fallback direct requires considered true", errors)

        unavailable_record = copy.deepcopy(next(
            scenario["role_execution"]
            for scenario in self.scenarios
            if scenario["scenario_id"] == "delegated-failure-fallback-unavailable-without-inline-parity"
        ))
        unavailable_record["attempts"][0]["outcome"] = "completed"
        errors = []
        validate_role_execution(unavailable_record, errors)
        self.assertIn("role_execution.fallback unavailable requires a failed delegated attempt", errors)


if __name__ == "__main__":
    unittest.main()
