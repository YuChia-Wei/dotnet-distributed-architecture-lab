#!/usr/bin/env python3
"""Validate diagnostic inference prerequisites and retained evidence bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(
    ".ai/assets/skills/diagnostic-analyst/scripts/validate-diagnostic-record.py"
)


class DiagnosticError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DiagnosticError(message)


def shape(value: object, fields: str, label: str) -> dict:
    require(isinstance(value, dict) and set(value) == set(fields.split()),
            f"{label}: missing or unknown fields")
    return value


def text_fields(value: dict, fields: str, label: str) -> None:
    for field in fields.split():
        require(isinstance(value[field], str) and bool(value[field].strip()),
                f"{label}.{field}: nonempty text required")


def choice(value: object, values: str, label: str) -> None:
    require(isinstance(value, str) and value in values.split(), f"{label}: invalid value")


def references(value: object, known: set[str], label: str, required: bool = False) -> None:
    require(isinstance(value, list) and all(isinstance(item, str) for item in value),
            f"{label}: reference list required")
    require(len(set(value)) == len(value) and set(value) <= known,
            f"{label}: duplicate or unknown reference")
    require(not required or bool(value), f"{label}: evidence required")


def reject_links(path: Path) -> None:
    for part in (path, *path.parents):
        require(not part.is_symlink() and not getattr(part, "is_junction", lambda: False)(),
                "evidence: symlink or junction boundary")
        if part.exists():
            require(not getattr(part.lstat(), "st_file_attributes", 0) & 0x400,
                    "evidence: reparse boundary")


def validate(record: object, evidence_root: Path) -> None:
    data = shape(record, "schema_version diagnostic_id symptom hypotheses minimal_reproduction "
                 "causal_isolation root_cause repair_handoff regression_binding evidence", "record")
    require(data["schema_version"] == "1.0", "record: unsupported schema version")
    text_fields(data, "diagnostic_id", "record")
    symptom = shape(data["symptom"], "description expected actual scope", "symptom")
    text_fields(symptom, "description expected actual scope", "symptom")
    require(isinstance(data["evidence"], list), "evidence: list required")
    reject_links(evidence_root.absolute())
    root = evidence_root.resolve(strict=True)
    require(root.is_dir(), "evidence: root must be a directory")
    evidence_ids: set[str] = set()
    for item in data["evidence"]:
        item = shape(item, "id path sha256", "evidence")
        text_fields(item, "id path sha256", "evidence")
        require(item["id"] not in evidence_ids, "evidence: duplicate id")
        evidence_ids.add(item["id"])
        path = PurePosixPath(item["path"])
        require(not path.is_absolute() and path.parts and
                all(part not in {"..", "."} for part in item["path"].split("/")) and
                not any(char in item["path"] for char in "\\:"), "evidence: unsafe relative path")
        candidate = root.joinpath(*path.parts)
        reject_links(candidate)
        require(candidate.resolve(strict=True).is_relative_to(root) and candidate.is_file(),
                "evidence: file must remain inside root")
        require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
                "evidence: invalid digest")
        with candidate.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        require(actual == item["sha256"], "evidence: digest mismatch")

    hypotheses = data["hypotheses"]
    require(isinstance(hypotheses, list) and bool(hypotheses), "hypotheses: nonempty list required")
    by_id: dict[str, dict] = {}
    for item in hypotheses:
        item = shape(item, "id claim falsifying_observation method falsification_strength "
                     "observation_scope coverage result observation evidence_refs", "hypothesis")
        text_fields(item, "id claim falsifying_observation observation_scope observation", "hypothesis")
        require(item["id"] not in by_id, "hypothesis: duplicate id")
        by_id[item["id"]] = item
        choice(item["method"], "interception counting enumeration controlled-experiment sampling static-inspection not-run", "method")
        choice(item["falsification_strength"], "deterministic-complete deterministic-bounded sampling-limited not-executed", "strength")
        choice(item["result"], "supported falsified inconclusive not-tested", "hypothesis.result")
        deterministic = item["falsification_strength"].startswith("deterministic-")
        if deterministic:
            require(item["method"] in {"interception", "counting", "enumeration", "controlled-experiment"},
                    "deterministic strength requires deterministic observation")
        if item["method"] == "sampling":
            require(item["falsification_strength"] == "sampling-limited", "sampling strength cannot be promoted")
        if item["method"] in {"not-run", "static-inspection"}:
            require(item["falsification_strength"] == "not-executed", "inspection is not execution")
        coverage = shape(item["coverage"], "expected_opportunities observed_opportunities complete", "coverage")
        for name in ("expected_opportunities", "observed_opportunities"):
            require(type(coverage[name]) is int and coverage[name] >= 0, "coverage: nonnegative integer required")
        require(type(coverage["complete"]) is bool, "coverage.complete: boolean required")
        require(coverage["observed_opportunities"] <= coverage["expected_opportunities"], "coverage exceeds declared scope")
        if coverage["complete"]:
            require(deterministic and coverage["expected_opportunities"] > 0 and
                    coverage["expected_opportunities"] == coverage["observed_opportunities"],
                    "complete coverage requires all deterministic observation opportunities")
        if item["result"] == "falsified":
            require(deterministic and coverage["complete"], "insufficient observation cannot falsify a hypothesis")
        if item["falsification_strength"] == "not-executed":
            require(item["result"] in {"not-tested", "inconclusive"}, "unexecuted hypothesis cannot support a result")
        references(item["evidence_refs"], evidence_ids, "hypothesis.evidence_refs",
                   item["result"] in {"supported", "falsified"})

    reproduction = shape(data["minimal_reproduction"], "status command environment expected actual evidence_refs", "reproduction")
    text_fields(reproduction, "command environment expected actual", "reproduction")
    choice(reproduction["status"], "reproduced not-reproduced not-run blocked", "reproduction.status")
    references(reproduction["evidence_refs"], evidence_ids, "reproduction.evidence_refs",
               reproduction["status"] in {"reproduced", "not-reproduced"})
    isolation = shape(data["causal_isolation"], "status baseline intervention actual alternatives evidence_refs", "isolation")
    text_fields(isolation, "baseline intervention actual alternatives", "isolation")
    choice(isolation["status"], "isolated not-isolated not-run blocked", "isolation.status")
    references(isolation["evidence_refs"], evidence_ids, "isolation.evidence_refs",
               isolation["status"] in {"isolated", "not-isolated"})
    cause = shape(data["root_cause"], "status hypothesis_ids explanation limitations evidence_refs", "root_cause")
    text_fields(cause, "explanation limitations", "root_cause")
    choice(cause["status"], "confirmed unconfirmed blocked", "root_cause.status")
    confirmed = cause["status"] == "confirmed"
    references(cause["hypothesis_ids"], set(by_id), "root_cause.hypothesis_ids", confirmed)
    references(cause["evidence_refs"], evidence_ids, "root_cause.evidence_refs", confirmed)
    if confirmed:
        require(reproduction["status"] == "reproduced", "confirmed cause requires minimal reproduction")
        require(isolation["status"] == "isolated", "confirmed cause requires controlled causal isolation")
        for identifier in cause["hypothesis_ids"]:
            hypothesis = by_id[identifier]
            require(hypothesis["result"] == "supported" and
                    hypothesis["falsification_strength"].startswith("deterministic-") and
                    hypothesis["coverage"]["complete"], "confirmed cause requires complete deterministic support")
        require(all(item["result"] == "falsified" for identifier, item in by_id.items()
                    if identifier not in cause["hypothesis_ids"]), "unresolved alternative prevents confirmation")
    handoff = shape(data["repair_handoff"], "owner_skill scope authorization_ref", "repair_handoff")
    text_fields(handoff, "owner_skill scope", "repair_handoff")
    require(handoff["authorization_ref"] is None or
            isinstance(handoff["authorization_ref"], str) and bool(handoff["authorization_ref"].strip()),
            "repair_handoff: authorization reference must be null or nonempty text")
    regression = shape(data["regression_binding"], "status command evidence_refs", "regression")
    text_fields(regression, "command", "regression")
    choice(regression["status"], "proposed verified", "regression.status")
    references(regression["evidence_refs"], evidence_ids, "regression.evidence_refs", regression["status"] == "verified")


def unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "record: duplicate JSON key")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        validate(record, args.evidence_root)
    except (DiagnosticError, OSError, ValueError, RuntimeError) as exc:
        message = str(exc) if isinstance(exc, DiagnosticError) else "invalid record or unavailable evidence"
        print(f"Diagnostic record rejected: {message}", file=sys.stderr)
        return 1
    print("Diagnostic record contract passed; causal truth and execution still require evidence review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
