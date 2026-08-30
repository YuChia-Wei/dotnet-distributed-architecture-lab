#!/usr/bin/env python3
"""Validate provider-neutral external-task dispatch and completion envelopes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
SCHEMA_PATH = (
    ROOT
    / ".ai/assets/skills/software-development-orchestrator/templates/external-task-delegation.schema.yaml"
)
BEGIN_MARKER = "BEGIN_EXTERNAL_TASK_DELEGATION"
END_MARKER = "END_EXTERNAL_TASK_DELEGATION"
COMPLETION_BEGIN_MARKER = "BEGIN_EXTERNAL_TASK_COMPLETION"
COMPLETION_END_MARKER = "END_EXTERNAL_TASK_COMPLETION"
SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
AGENT_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-agent-execution-guardrails.py"
AGENT_SCHEMA_PATH = ROOT / ".ai/assets/shared/agent-execution-guardrails.schema.yaml"


def load_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def missing_fields(value: object, required: list[str], label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label} must be a mapping"]
    return [f"{label}.{field} is required" for field in required if field not in value]


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: object, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(non_empty_string(item) for item in value)
    )


def iso_with_offset(value: object) -> bool:
    if not non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def contained_path(value: object) -> Path | None:
    if not non_empty_string(value):
        return None
    candidate = Path(str(value))
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (ROOT / candidate).resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        return None
    return resolved


def validate_bound_packet(packet_contract: dict[str, Any], dispatch: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    packet_path = contained_path(packet_contract.get("packet_ref"))
    if packet_path is None:
        return ["dispatch.execution_packet.packet_ref must be a contained repository-relative path"]
    if not packet_path.is_file():
        return ["dispatch.execution_packet.packet_ref does not exist"]
    observed_file_digest = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    if packet_contract.get("packet_sha256") != observed_file_digest:
        errors.append("dispatch.execution_packet.packet_sha256 does not match packet file bytes")
    try:
        packet_record = load_mapping(packet_path)
        spec = importlib.util.spec_from_file_location("agent_execution_guardrails_for_dispatch", AGENT_VALIDATOR_PATH)
        if spec is None or spec.loader is None:
            raise ValueError("canonical agent execution validator cannot be loaded")
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        agent_schema = load_mapping(AGENT_SCHEMA_PATH)
        validator.validate_packet(packet_record, agent_schema)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"dispatch.execution_packet canonical validation failed: {exc}")
        return errors
    subject = dispatch.get("subject", {})
    execution = dispatch.get("execution", {})
    source = dispatch.get("source", {})
    if packet_record.get("execution_kind") != "external":
        errors.append("dispatch.execution_packet execution_kind must be external")
    if packet_record.get("subject", {}).get("exact_sha") != subject.get("commit_sha"):
        errors.append("dispatch.execution_packet content subject must match dispatch subject")
    invocation = packet_record.get("invocation", {})
    if invocation.get("argv") != execution.get("argv") or invocation.get("cwd") != execution.get("working_directory"):
        errors.append("dispatch.execution_packet invocation must match dispatch execution")
    if packet_record.get("integration_owner") != source.get("final_integration_owner"):
        errors.append("dispatch.execution_packet integration_owner must match dispatch source")
    return errors


def validate_schema_definition(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if schema.get("schema_version") != "1.1":
        errors.append("schema.schema_version must be 1.1")
    if schema.get("contract_id") != "external-task-delegation":
        errors.append("schema.contract_id must be external-task-delegation")
    transport = schema.get("prompt_transport")
    errors.extend(
        missing_fields(
            transport,
            ["begin_marker", "end_marker", "dispatch_records_per_prompt"],
            "schema.prompt_transport",
        )
    )
    if isinstance(transport, dict):
        if transport.get("begin_marker") != BEGIN_MARKER:
            errors.append(f"schema.prompt_transport.begin_marker must be {BEGIN_MARKER}")
        if transport.get("end_marker") != END_MARKER:
            errors.append(f"schema.prompt_transport.end_marker must be {END_MARKER}")
        if transport.get("dispatch_records_per_prompt") != 1:
            errors.append("schema.prompt_transport.dispatch_records_per_prompt must be 1")
    completion_transport = schema.get("completion_transport")
    errors.extend(
        missing_fields(
            completion_transport,
            ["begin_marker", "end_marker", "completion_records_per_message"],
            "schema.completion_transport",
        )
    )
    if isinstance(completion_transport, dict):
        if completion_transport.get("begin_marker") != COMPLETION_BEGIN_MARKER:
            errors.append(
                f"schema.completion_transport.begin_marker must be {COMPLETION_BEGIN_MARKER}"
            )
        if completion_transport.get("end_marker") != COMPLETION_END_MARKER:
            errors.append(
                f"schema.completion_transport.end_marker must be {COMPLETION_END_MARKER}"
            )
        if completion_transport.get("completion_records_per_message") != 1:
            errors.append(
                "schema.completion_transport.completion_records_per_message must be 1"
            )
    record_types = schema.get("record_types")
    if record_types != {
        "dispatch": "external-task-dispatch",
        "completion": "external-task-completion",
    }:
        errors.append("schema.record_types must declare dispatch and completion records")
    delivery = schema.get("dispatch", {}).get("completion_delivery", {})
    if delivery.get("primary_modes") != ["source-task-callback", "parent-event-wait"]:
        errors.append("schema dispatch primary delivery modes are invalid")
    if delivery.get("fallback_modes") != [
        "parent-event-wait",
        "single-terminal-readback",
        "none",
    ]:
        errors.append("schema dispatch fallback delivery modes are invalid")
    transport_semantics = schema.get("transport_semantics", {})
    if transport_semantics.get("parent_wait_timeout") != "pending-awaiting-completion":
        errors.append("schema parent wait timeout must remain pending")
    if (
        transport_semantics.get("callback_failure_with_retrievable_terminal_report")
        != "recoverable-by-one-terminal-readback"
    ):
        errors.append("schema callback recovery must permit one terminal readback")
    if transport_semantics.get("repeated_status_polling") != "prohibited":
        errors.append("schema repeated status polling must be prohibited")
    if transport_semantics.get("source_task_progress_delivery") != "terminal-only":
        errors.append("schema source-task progress delivery must remain terminal-only")
    if (
        transport_semantics.get("runtime_local_progress")
        != "runtime-policy-owned-and-not-source-delivery"
    ):
        errors.append("schema runtime-local progress ownership is invalid")
    if transport_semantics.get("pre_send_completion_validation") != "required":
        errors.append("schema pre-send completion validation must be required")
    if transport_semantics.get("post_validation_record_mutation") != "prohibited":
        errors.append("schema post-validation record mutation must be prohibited")
    if transport_semantics.get("callback_payload") != "exact-validated-completion-record":
        errors.append("schema callback payload must be the exact validated completion record")
    return errors


def validate_dispatch(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = missing_fields(record, schema["dispatch"]["required"], "dispatch")
    if record.get("schema_version") != "1.1":
        errors.append("dispatch.schema_version must be 1.1")
    if record.get("record_type") != "external-task-dispatch":
        errors.append("dispatch.record_type must be external-task-dispatch")
    if not non_empty_string(record.get("delegation_id")) or not ID_RE.fullmatch(
        str(record.get("delegation_id", ""))
    ):
        errors.append("dispatch.delegation_id must be a stable bounded identifier")
    if not non_empty_string(record.get("task_kind")):
        errors.append("dispatch.task_kind must be non-empty")

    source = record.get("source")
    errors.extend(missing_fields(source, schema["dispatch"]["source"]["required"], "dispatch.source"))
    if isinstance(source, dict):
        source_kind = source.get("task_id_source")
        if source_kind not in schema["dispatch"]["source"]["task_id_sources"]:
            errors.append("dispatch.source.task_id_source is invalid")
        if source_kind == "explicit" and not non_empty_string(source.get("task_id")):
            errors.append("dispatch.source.task_id is required when task_id_source is explicit")
        if not non_empty_string(source.get("final_integration_owner")):
            errors.append("dispatch.source.final_integration_owner must be non-empty")

    objective = record.get("objective")
    errors.extend(missing_fields(objective, schema["dispatch"]["objective"]["required"], "dispatch.objective"))
    if isinstance(objective, dict):
        if not non_empty_string(objective.get("goal")):
            errors.append("dispatch.objective.goal must be non-empty")
        if not string_list(objective.get("non_goals")):
            errors.append("dispatch.objective.non_goals must be a list of strings")

    subject = record.get("subject")
    errors.extend(missing_fields(subject, schema["dispatch"]["subject"]["required"], "dispatch.subject"))
    if isinstance(subject, dict):
        if not non_empty_string(subject.get("repository_root")):
            errors.append("dispatch.subject.repository_root must be non-empty")
        if not SHA_RE.fullmatch(str(subject.get("commit_sha", ""))):
            errors.append("dispatch.subject.commit_sha must be a full Git SHA")
        if subject.get("clean_worktree_required") is not True:
            errors.append("dispatch.subject.clean_worktree_required must be true")

    execution = record.get("execution")
    errors.extend(missing_fields(execution, schema["dispatch"]["execution"]["required"], "dispatch.execution"))
    if isinstance(execution, dict):
        if not non_empty_string(execution.get("working_directory")):
            errors.append("dispatch.execution.working_directory must be non-empty")
        if not string_list(execution.get("argv"), allow_empty=False):
            errors.append("dispatch.execution.argv must be a non-empty string list")
        timeout = execution.get("timeout_seconds")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            errors.append("dispatch.execution.timeout_seconds must be a positive integer")

    packet = record.get("execution_packet")
    errors.extend(
        missing_fields(
            packet,
            schema["dispatch"]["execution_packet"]["required"],
            "dispatch.execution_packet",
        )
    )
    if isinstance(packet, dict):
        if packet.get("schema_ref") != ".ai/assets/shared/agent-execution-guardrails.schema.yaml":
            errors.append("dispatch.execution_packet.schema_ref is invalid")
        if not non_empty_string(packet.get("packet_ref")):
            errors.append("dispatch.execution_packet.packet_ref must be non-empty")
        if not re.fullmatch(r"[0-9a-f]{64}", str(packet.get("packet_sha256", ""))):
            errors.append("dispatch.execution_packet.packet_sha256 must be lowercase SHA-256")
        if not SHA_RE.fullmatch(str(packet.get("subject_sha", ""))):
            errors.append("dispatch.execution_packet.subject_sha must be a full Git SHA")
        elif isinstance(subject, dict) and packet.get("subject_sha") != subject.get("commit_sha"):
            errors.append("dispatch.execution_packet.subject_sha must match dispatch subject")
        packet_validator = packet.get("validator_argv")
        if (
            not string_list(packet_validator, allow_empty=False)
            or not any(
                str(item).replace("\\", "/").endswith("/validate-agent-execution-guardrails.py")
                for item in packet_validator
            )
            or "--packet" not in packet_validator
            or packet.get("packet_ref") not in packet_validator
        ):
            errors.append("dispatch.execution_packet.validator_argv must validate the bound packet ref")
        if packet.get("validation_outcome") != "passed":
            errors.append("dispatch.execution_packet.validation_outcome must be passed")
        errors.extend(validate_bound_packet(packet, record))

    permissions = record.get("permissions")
    errors.extend(missing_fields(permissions, schema["dispatch"]["permissions"]["required"], "dispatch.permissions"))
    if isinstance(permissions, dict):
        if not string_list(permissions.get("read_scope"), allow_empty=False):
            errors.append("dispatch.permissions.read_scope must be a non-empty string list")
        write_scope = permissions.get("write_scope")
        if not string_list(write_scope) or not set(write_scope) <= {"ignored-validation-artifacts"}:
            errors.append("dispatch.permissions.write_scope may contain only ignored-validation-artifacts")
        if permissions.get("repair_allowed") is not False:
            errors.append("dispatch.permissions.repair_allowed must be false")
        if permissions.get("external_mutations") != []:
            errors.append("dispatch.permissions.external_mutations must be empty")
        if permissions.get("secret_values") != "prohibited":
            errors.append("dispatch.permissions.secret_values must be prohibited")

    delivery = record.get("completion_delivery")
    errors.extend(
        missing_fields(
            delivery,
            schema["dispatch"]["completion_delivery"]["required"],
            "dispatch.completion_delivery",
        )
    )
    if isinstance(delivery, dict):
        contract = schema["dispatch"]["completion_delivery"]
        if delivery.get("primary") not in contract["primary_modes"]:
            errors.append("dispatch.completion_delivery.primary is invalid")
        if delivery.get("fallback") not in contract["fallback_modes"]:
            errors.append("dispatch.completion_delivery.fallback is invalid")
        if delivery.get("destination") != "source-task":
            errors.append("dispatch.completion_delivery.destination must be source-task")
        if delivery.get("progress_updates") != "terminal-only":
            errors.append("dispatch.completion_delivery.progress_updates must be terminal-only")
        if delivery.get("max_terminal_reports") != 1:
            errors.append("dispatch.completion_delivery.max_terminal_reports must be 1")
        if delivery.get("report_schema") != "same-contract#completion":
            errors.append("dispatch.completion_delivery.report_schema is invalid")
        pre_send = delivery.get("pre_send_validation")
        errors.extend(
            missing_fields(
                pre_send,
                contract["pre_send_validation"]["required"],
                "dispatch.completion_delivery.pre_send_validation",
            )
        )
        if isinstance(pre_send, dict):
            if pre_send.get("required") is not True:
                errors.append(
                    "dispatch.completion_delivery.pre_send_validation.required must be true"
                )
            validator_argv = pre_send.get("validator_argv")
            if not string_list(validator_argv, allow_empty=False):
                errors.append(
                    "dispatch.completion_delivery.pre_send_validation.validator_argv "
                    "must be a non-empty string list"
                )
            elif (
                not any(
                    str(item).replace("\\", "/").endswith(
                        "/validate-external-task-delegation.py"
                    )
                    for item in validator_argv
                )
                or "--dispatch" not in validator_argv
            ):
                errors.append(
                    "dispatch.completion_delivery.pre_send_validation.validator_argv "
                    "must invoke the canonical validator with --dispatch"
                )
            for field in ("dispatch_ref", "completion_ref"):
                if not non_empty_string(pre_send.get(field)):
                    errors.append(
                        "dispatch.completion_delivery.pre_send_validation."
                        f"{field} must be non-empty"
                    )
            if pre_send.get("failure_action") != "do-not-deliver-terminal-report":
                errors.append(
                    "dispatch.completion_delivery.pre_send_validation.failure_action is invalid"
                )
            if pre_send.get("payload_binding") != "exact-validated-completion-record":
                errors.append(
                    "dispatch.completion_delivery.pre_send_validation.payload_binding is invalid"
                )

    if not string_list(record.get("stop_conditions"), allow_empty=False):
        errors.append("dispatch.stop_conditions must be a non-empty string list")
    return errors


def validate_completion(
    record: dict[str, Any], schema: dict[str, Any], dispatch: dict[str, Any] | None = None
) -> list[str]:
    errors = missing_fields(record, schema["completion"]["required"], "completion")
    if record.get("schema_version") != "1.1":
        errors.append("completion.schema_version must be 1.1")
    if record.get("record_type") != "external-task-completion":
        errors.append("completion.record_type must be external-task-completion")
    for field in ("delegation_id", "source_task_id", "delegated_task_id"):
        if not non_empty_string(record.get(field)):
            errors.append(f"completion.{field} must be non-empty")

    subject = record.get("subject")
    errors.extend(missing_fields(subject, schema["completion"]["subject"]["required"], "completion.subject"))
    if isinstance(subject, dict):
        expected_sha = str(subject.get("expected_commit_sha", ""))
        observed_sha = str(subject.get("observed_commit_sha", ""))
        if not SHA_RE.fullmatch(expected_sha) or not SHA_RE.fullmatch(observed_sha):
            errors.append("completion subject SHAs must be full Git SHAs")

    preflight = record.get("preflight")
    errors.extend(missing_fields(preflight, schema["completion"]["preflight"]["required"], "completion.preflight"))
    execution = record.get("execution")
    errors.extend(missing_fields(execution, schema["completion"]["execution"]["required"], "completion.execution"))
    if isinstance(execution, dict):
        if not non_empty_string(execution.get("working_directory")):
            errors.append("completion.execution.working_directory must be non-empty")
        if not string_list(execution.get("argv"), allow_empty=False):
            errors.append("completion.execution.argv must be a non-empty string list")

    timing = record.get("timing")
    errors.extend(missing_fields(timing, schema["completion"]["timing"]["required"], "completion.timing"))
    if isinstance(timing, dict):
        if not iso_with_offset(timing.get("started_at")) or not iso_with_offset(timing.get("completed_at")):
            errors.append("completion timing timestamps must be ISO 8601 with offsets")
        duration = timing.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
            errors.append("completion.timing.duration_seconds must be non-negative")

    result = record.get("result")
    errors.extend(missing_fields(result, schema["completion"]["result"]["required"], "completion.result"))
    outcome = result.get("outcome") if isinstance(result, dict) else None
    if isinstance(result, dict):
        if outcome not in schema["completion"]["result"]["outcomes"]:
            errors.append("completion.result.outcome is invalid")
        exit_code = result.get("exit_code")
        if exit_code is not None and (not isinstance(exit_code, int) or isinstance(exit_code, bool)):
            errors.append("completion.result.exit_code must be an integer or null")
        counts = result.get("counts")
        if counts is not None and (
            not isinstance(counts, dict)
            or not all(
                non_empty_string(key)
                and isinstance(value, int)
                and not isinstance(value, bool)
                and value >= 0
                for key, value in counts.items()
            )
        ):
            errors.append("completion.result.counts must be null or non-negative integer counts")

    evidence = record.get("evidence")
    errors.extend(missing_fields(evidence, schema["completion"]["evidence"]["required"], "completion.evidence"))
    if isinstance(evidence, dict):
        refs = evidence.get("refs")
        bounded_output = evidence.get("bounded_output")
        if not string_list(refs) or (not refs and not non_empty_string(bounded_output)):
            errors.append("completion.evidence requires a ref or bounded_output")
        if bounded_output is not None and not isinstance(bounded_output, str):
            errors.append("completion.evidence.bounded_output must be a string")

    final_state = record.get("final_state")
    errors.extend(missing_fields(final_state, schema["completion"]["final_state"]["required"], "completion.final_state"))
    if isinstance(final_state, dict) and not string_list(final_state.get("tracked_changes")):
        errors.append("completion.final_state.tracked_changes must be a string list")

    delivery = record.get("delivery")
    errors.extend(missing_fields(delivery, schema["completion"]["delivery"]["required"], "completion.delivery"))
    if isinstance(delivery, dict):
        if delivery.get("mode") not in schema["completion"]["delivery"]["modes"]:
            errors.append("completion.delivery.mode is invalid")
        if delivery.get("destination") != "source-task":
            errors.append("completion.delivery.destination must be source-task")
        if delivery.get("terminal_report_number") != 1:
            errors.append("completion.delivery.terminal_report_number must be 1")
        schema_validation = delivery.get("schema_validation")
        errors.extend(
            missing_fields(
                schema_validation,
                schema["completion"]["delivery"]["schema_validation"]["required"],
                "completion.delivery.schema_validation",
            )
        )
        if isinstance(schema_validation, dict):
            if schema_validation.get("outcome") != "passed":
                errors.append("completion.delivery.schema_validation.outcome must be passed")
            if schema_validation.get("exit_code") != 0:
                errors.append("completion.delivery.schema_validation.exit_code must be zero")
            if not string_list(
                schema_validation.get("validator_argv"), allow_empty=False
            ):
                errors.append(
                    "completion.delivery.schema_validation.validator_argv must be a non-empty string list"
                )
            for field in ("dispatch_ref", "completion_ref"):
                if not non_empty_string(schema_validation.get(field)):
                    errors.append(
                        f"completion.delivery.schema_validation.{field} must be non-empty"
                    )
            if (
                schema_validation.get("payload_binding")
                != "exact-validated-completion-record"
            ):
                errors.append(
                    "completion.delivery.schema_validation.payload_binding is invalid"
                )

    if outcome == "passed":
        expected_sha = subject.get("expected_commit_sha") if isinstance(subject, dict) else None
        observed_sha = subject.get("observed_commit_sha") if isinstance(subject, dict) else None
        if expected_sha != observed_sha:
            errors.append("passed completion requires matching expected and observed commit SHAs")
        if not isinstance(preflight, dict) or preflight.get("commit_matches") is not True:
            errors.append("passed completion requires preflight.commit_matches true")
        if not isinstance(preflight, dict) or preflight.get("clean_worktree") is not True:
            errors.append("passed completion requires a clean preflight worktree")
        if not isinstance(result, dict) or result.get("exit_code") != 0:
            errors.append("passed completion requires exit_code zero")
        if not isinstance(final_state, dict) or final_state.get("clean_worktree") is not True:
            errors.append("passed completion requires a clean final worktree")
        if not isinstance(final_state, dict) or final_state.get("tracked_changes") != []:
            errors.append("passed completion requires no tracked changes")

    if dispatch is not None:
        if record.get("delegation_id") != dispatch.get("delegation_id"):
            errors.append("completion.delegation_id must match dispatch")
        dispatch_subject = dispatch.get("subject", {})
        if isinstance(subject, dict) and subject.get("expected_commit_sha") != dispatch_subject.get("commit_sha"):
            errors.append("completion expected commit must match dispatch")
        dispatch_execution = dispatch.get("execution", {})
        if isinstance(execution, dict):
            for field in ("working_directory", "argv"):
                if execution.get(field) != dispatch_execution.get(field):
                    errors.append(f"completion.execution.{field} must match dispatch")
        source = dispatch.get("source", {})
        if source.get("task_id_source") == "explicit" and record.get("source_task_id") != source.get("task_id"):
            errors.append("completion.source_task_id must match explicit dispatch source")
        dispatch_delivery = dispatch.get("completion_delivery", {})
        pre_send = dispatch_delivery.get("pre_send_validation", {})
        schema_validation = delivery.get("schema_validation", {}) if isinstance(delivery, dict) else {}
        for field in ("validator_argv", "dispatch_ref", "completion_ref", "payload_binding"):
            if schema_validation.get(field) != pre_send.get(field):
                errors.append(
                    "completion.delivery.schema_validation."
                    f"{field} must match dispatch pre-send validation"
                )
    return errors


def extract_record_from_envelope(
    text: str, begin_marker: str, end_marker: str, label: str
) -> dict[str, Any]:
    if text.count(begin_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError(f"{label} must contain exactly one external-task envelope")
    before, remainder = text.split(begin_marker, 1)
    payload, after = remainder.split(end_marker, 1)
    if end_marker in before or begin_marker in after:
        raise ValueError(f"{label} envelope markers are out of order")
    data = yaml.safe_load(payload.strip())
    if not isinstance(data, dict):
        raise ValueError(f"{label} envelope must contain one YAML mapping")
    return data


def extract_dispatch_from_prompt(text: str) -> dict[str, Any]:
    return extract_record_from_envelope(text, BEGIN_MARKER, END_MARKER, "prompt")


def extract_completion_from_message(text: str) -> dict[str, Any]:
    return extract_record_from_envelope(
        text,
        COMPLETION_BEGIN_MARKER,
        COMPLETION_END_MARKER,
        "completion message",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", type=Path, help="YAML record to validate")
    parser.add_argument("--prompt", type=Path, help="Prompt text containing one marked dispatch envelope")
    parser.add_argument(
        "--completion-message",
        type=Path,
        help="Message text containing one marked completion envelope",
    )
    parser.add_argument("--dispatch", type=Path, help="Dispatch record used to cross-check a completion")
    parser.add_argument("--schema-only", action="store_true", help="Validate only the canonical schema definition")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema = load_mapping(SCHEMA_PATH)
    errors = validate_schema_definition(schema)
    record: dict[str, Any] | None = None
    if args.prompt is not None:
        try:
            record = extract_dispatch_from_prompt(args.prompt.read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
    elif args.completion_message is not None:
        try:
            record = extract_completion_from_message(
                args.completion_message.read_text(encoding="utf-8")
            )
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
    elif args.record is not None:
        try:
            record = load_mapping(args.record)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
    elif not args.schema_only:
        errors.append("provide a record, --prompt, --completion-message, or --schema-only")

    if record is not None:
        record_type = record.get("record_type")
        if record_type == "external-task-dispatch":
            errors.extend(validate_dispatch(record, schema))
        elif record_type == "external-task-completion":
            dispatch = load_mapping(args.dispatch) if args.dispatch is not None else None
            errors.extend(validate_completion(record, schema, dispatch))
        else:
            errors.append("record_type must be external-task-dispatch or external-task-completion")

    if errors:
        print("External-task delegation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("External-task delegation validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
