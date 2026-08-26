#!/usr/bin/env python3
"""Finalize independently audited v0.13 target authorities and rule state."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml


ROOT = Path.cwd().resolve()
WORKFLOW = ROOT / ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade"
PROVENANCE = ROOT / ".dev/ai-context/provenance.yaml"
LEDGER = ROOT / ".dev/ai-context/customizations.yaml"
RECEIPT = ROOT / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
DECISIONS = WORKFLOW / "evidence/v0.9.0/effective-rule-decisions.yaml"
REPORT = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "reports/07-v0.13.0-reconciliation.md"
)
PREFLIGHT = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.13.0/preflight.yaml"
)
SUMMARY = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.13.0/validation-summary.yaml"
)
REMEDIATION = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.13.0/aggregate-es-001-remediation.yaml"
)
ASSESSMENT = ".dev/assessments/ASM-20260813-006/report.md"
EXPECTED = {
    PROVENANCE: "cafc2657be1b60e3418b6ab4c5e08e212ebaf4250006b66d47117eafb14a659b",
    LEDGER: "a4cfdeb723d9276f6187d7f7d23248cae781465da36c9519b00399e6f55a2287",
    RECEIPT: "094840edc10744c12397a905e1783f8200a498081a492d5fae0f13f41b979ec0",
}
EXPECTED_IDS = {
    "CUST-DOTNET-MQ-GOVERNANCE",
    "CUST-DOTNET-MQ-VALIDATION",
    "CUST-DOTNET-MQ-REPO-TRUTH",
    "CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION",
}


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected YAML mapping: {path}")
    return value


def require_hashes() -> None:
    for path, expected in EXPECTED.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"authority/receipt drift at {path}: {actual}")


def append_unique(values: list, additions: tuple[str, ...]) -> None:
    for value in additions:
        if value not in values:
            values.append(value)


def main() -> int:
    require_hashes()
    provenance = load_yaml(PROVENANCE)
    ledger = load_yaml(LEDGER)
    decisions = load_yaml(DECISIONS)
    assessment = load_yaml(ROOT / ".dev/assessments/ASM-20260813-006/assessment.yaml")
    if provenance.get("source", {}).get("version") != "v0.12.0":
        raise RuntimeError("v0.13 finalization requires exact finalized v0.12 authority")
    if decisions.get("status") != "approved-and-independently-verified":
        raise RuntimeError("effective-rule decisions are not independently verified")
    if (
        assessment.get("status") != "final"
        or assessment.get("subject_ref", {}).get("commit")
        != "a3389994bf52f9265b7fe0a079ccd4041efc8997"
    ):
        raise RuntimeError("ASM-20260813-006 does not bind the audited fixed HEAD")

    entries = ledger.get("customizations")
    if not isinstance(entries, list):
        raise RuntimeError("customization entries are unavailable")
    by_id = {entry.get("id"): entry for entry in entries if isinstance(entry, dict)}
    if set(by_id) != EXPECTED_IDS:
        raise RuntimeError(f"unexpected customization IDs: {sorted(by_id)}")

    finalized_at = datetime.now().astimezone().isoformat(timespec="seconds")
    previous_source = copy.deepcopy(provenance["source"])
    expected_previous = {
        "repository": "https://github.com/YuChia-Wei/ai-collaboration-framework.git",
        "release_id": "REL-v0.12.0",
        "version": "v0.12.0",
        "tag": "v0.12.0",
        "commit": "a4fd14f0f08ad53859df1c860db0eb9643cdb2de",
    }
    if previous_source != expected_previous:
        raise RuntimeError(f"unexpected v0.12 source authority: {previous_source}")

    provenance["template_metadata"]["updated_at"] = finalized_at
    provenance["source"] = {
        "repository": "https://github.com/YuChia-Wei/ai-collaboration-framework.git",
        "release_id": "REL-v0.13.0",
        "version": "v0.13.0",
        "tag": "v0.13.0",
        "commit": "8584337b47295da1af914180baf2b3f815b9dcc7",
    }
    provenance["installation"]["last_upgraded_at"] = finalized_at
    provenance["previous_source"] = previous_source
    provenance["reconciliation"] = {"unresolved": []}
    provenance["last_migration"] = {
        "status": "completed",
        "from_version": "v0.12.0",
        "to_version": "v0.13.0",
        "completed_at": finalized_at,
        "evidence": REPORT,
    }

    ledger["template_metadata"]["updated_at"] = finalized_at
    for entry in entries:
        entry_id = entry["id"]
        current_status = entry.get("incoming", {}).get("status")
        if current_status not in {"partial", "conflicting"}:
            raise RuntimeError(f"unexpected incoming status for {entry_id}: {current_status}")
        entry["incoming"] = {
            "version": "v0.13.0",
            "status": current_status,
            "evidence": REPORT,
        }
        entry["post_upgrade_audit"] = {
            "assessment_id": "ASM-20260813-006",
            "status": "verified",
            "evidence": ASSESSMENT,
        }
        workflows = entry.setdefault("decision_evidence", {}).setdefault("workflows", [])
        append_unique(workflows, (PREFLIGHT, REPORT))

    validation = by_id["CUST-DOTNET-MQ-VALIDATION"]
    validation_paths = validation.setdefault("paths", [])
    append_unique(
        validation_paths,
        (".dev/ai-context/tooling/tests/test_code_reviewer_routing_projection.py",),
    )
    append_unique(
        validation.setdefault("decision_evidence", {}).setdefault("workflows", []),
        (
            ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
            "evidence/v0.13.0/preaction-packet-analysis.yaml",
            REMEDIATION,
        ),
    )

    by_id["CUST-DOTNET-MQ-GOVERNANCE"]["reason"] = (
        "Merge the byte-exact v0.13 framework evolution while retaining target "
        "Issue-first authorization, repository governance and skill routing, "
        "directory-scoped .codex/agents tracking, the repository LF policy, "
        "and inactive profile/reuse/recipe boundaries. Adopt compact code-review "
        "routing without allowing package examples to replace target truth."
    )
    validation["reason"] = (
        "AICU-V010-PROJECTION-001, AICU-V011-SELECTION-001, "
        "AICU-V012-PROFILE-REGISTRY-PROJECTION-001, "
        "AICU-V012-COMMIT-CUTOVER-001, AICU-V012-COMMIT-DOC-001, "
        "AICU-V013-ROUTING-PROJECTION-001, "
        "AICU-V013-COMPONENT-OWNERSHIP-001, and "
        "AICU-V013-PREACTION-PACKET-BOOTSTRAP-001 require the SHA-pinned "
        "downstream-applicable target gate and prospective target policy. Do not "
        "claim stock profiles, changed-path execution, reuse, or source-only tests passed."
    )
    by_id["CUST-DOTNET-MQ-REPO-TRUTH"]["reason"] = (
        "Preserve repository identity, .NET SDK and product truth, target catalogs "
        "and workflow authorities, complete analyzer/tools retirement, and inactive "
        "recipe boundaries while adopting v0.13 exact framework paths and removal "
        "of the bundled provider payload."
    )
    by_id["CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION"]["reason"] = (
        "Adopt AI execution provenance prospectively from "
        "2026-08-12T22:08:09+08:00 and commit-subject grammar from "
        "2026-08-13T11:05:12+08:00 without history rewrite. Preserve only the "
        "exact ad194beb3fb61a18b6870093b704264746c1516b / ASM-20260812-002 / "
        "missing-matching-trailer waiver in the target-owned fail-closed overlay "
        "while canonical v0.13 framework bytes remain exact."
    )

    state_candidate = copy.deepcopy(decisions.get("state_candidate"))
    if not isinstance(state_candidate, dict):
        raise RuntimeError("effective-rule state candidate is unavailable")
    state_candidate["framework"] = {
        "version": "v0.13.0",
        "commit": "8584337b47295da1af914180baf2b3f815b9dcc7",
        "selected_technology_profile": "dotnet-backend",
    }
    state_candidate["generated_at"] = finalized_at
    dispositions = state_candidate.get("rule_dispositions")
    if not isinstance(dispositions, list):
        raise RuntimeError("rule dispositions are unavailable")
    aggregate = next(
        (item for item in dispositions if item.get("rule_id") == "AGGREGATE-ES-001"),
        None,
    )
    if not isinstance(aggregate, dict) or aggregate.get("effective_disposition") != "baseline-effective":
        raise RuntimeError("AGGREGATE-ES-001 baseline disposition is unavailable")
    append_unique(aggregate["evidence"], (REMEDIATION, ASSESSMENT))
    append_unique(
        aggregate["baseline_acceptance"]["verification"]["evidence"],
        (REMEDIATION, ASSESSMENT),
    )

    sys.path.insert(0, str(ROOT / ".ai/scripts"))
    from ai_context_target_provenance import finalize_context

    result = finalize_context(
        ROOT,
        provenance,
        ledger,
        require_finalized=True,
        allow_existing=True,
        effective_state_candidate=state_candidate,
        effective_resolver_evidence=[
            ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
            "evidence/v0.9.0/effective-rule-decisions.yaml",
            SUMMARY,
            ASSESSMENT,
        ],
    )
    readiness = result.get("effective_rule_readiness", {})
    if result.get("status") != "finalized" or readiness.get("action_ready") is not True:
        raise RuntimeError(f"unexpected finalization result: {result}")
    packets = list((ROOT / ".dev/ai-context/effective-rule-packets").glob("*.yaml"))
    if len(packets) != 20:
        raise RuntimeError(f"expected 20 packets, found {len(packets)}")
    print(
        json.dumps(
            {
                "finalized_at": finalized_at,
                "receipt_sha256": EXPECTED[RECEIPT],
                "packet_count": len(packets),
                "result": result,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
