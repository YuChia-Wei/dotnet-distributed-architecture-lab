#!/usr/bin/env python3
"""Finalize the independently audited v0.12 target authorities and rule state."""

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
    "reports/06-v0.12.0-reconciliation.md"
)
PREFLIGHT = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.12.0/preflight.yaml"
)
SUMMARY = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.12.0/validation-summary.yaml"
)
ASSESSMENT = ".dev/assessments/ASM-20260813-005/report.md"
EXPECTED = {
    PROVENANCE: "8987aa576d22e53748544f5883adfe545a42869fc0795fa375621d0470952a8f",
    LEDGER: "53b96a9d5063a92ac84debaebbc55e6f6ed0fa426f050349fb076d832c4e794e",
    RECEIPT: "bd4d6dea53520c7c91b84a770c105a1d53c889faeb07ba8306c3925d7b3bfda9",
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


def main() -> int:
    require_hashes()
    provenance = load_yaml(PROVENANCE)
    ledger = load_yaml(LEDGER)
    decisions = load_yaml(DECISIONS)
    if provenance.get("source", {}).get("version") != "v0.11.0":
        raise RuntimeError("v0.12 finalization requires exact finalized v0.11 authority")
    if decisions.get("status") != "approved-and-independently-verified":
        raise RuntimeError("effective-rule decisions are not independently verified")

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
        "release_id": "REL-v0.11.0",
        "version": "v0.11.0",
        "tag": "v0.11.0",
        "commit": "05199ed0a9ed509ef1696df014fce244f8e7cffa",
    }
    if previous_source != expected_previous:
        raise RuntimeError(f"unexpected v0.11 source authority: {previous_source}")

    provenance["template_metadata"]["updated_at"] = finalized_at
    provenance["source"] = {
        "repository": "https://github.com/YuChia-Wei/ai-collaboration-framework.git",
        "release_id": "REL-v0.12.0",
        "version": "v0.12.0",
        "tag": "v0.12.0",
        "commit": "a4fd14f0f08ad53859df1c860db0eb9643cdb2de",
    }
    provenance["installation"]["last_upgraded_at"] = finalized_at
    provenance["previous_source"] = previous_source
    provenance["reconciliation"] = {"unresolved": []}
    provenance["last_migration"] = {
        "status": "completed",
        "from_version": "v0.11.0",
        "to_version": "v0.12.0",
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
            "version": "v0.12.0",
            "status": current_status,
            "evidence": REPORT,
        }
        entry["post_upgrade_audit"] = {
            "assessment_id": "ASM-20260813-005",
            "status": "verified",
            "evidence": ASSESSMENT,
        }
        workflows = entry.setdefault("decision_evidence", {}).setdefault("workflows", [])
        for evidence in (PREFLIGHT, REPORT):
            if evidence not in workflows:
                workflows.append(evidence)

    validation_paths = by_id["CUST-DOTNET-MQ-VALIDATION"].setdefault("paths", [])
    candidate_test = ".dev/ai-context/tooling/tests/test_target_gate_candidate_diagnostics.py"
    if candidate_test not in validation_paths:
        validation_paths.append(candidate_test)

    by_id["CUST-DOTNET-MQ-GOVERNANCE"]["reason"] = (
        "Merge the byte-exact v0.12 framework evolution while retaining target "
        "Issue-first authorization, repository governance and skill routing, "
        "directory-scoped .codex/agents tracking, the repository LF policy, "
        "and inactive provider/profile/reuse boundaries. Project the new "
        "issue-only or scope-only commit grammar prospectively into root AGENTS."
    )
    by_id["CUST-DOTNET-MQ-VALIDATION"]["reason"] = (
        "AICU-V010-PROJECTION-001, AICU-V090-DOC-001, "
        "AICU-V011-SELECTION-001, AICU-V012-PROFILE-REGISTRY-PROJECTION-001, "
        "AICU-V012-COMMIT-CUTOVER-001, and AICU-V012-COMMIT-DOC-001 prove "
        "that the v0.12 stock downstream projection, changed-path selector, "
        "and global title cutoff cannot be the authoritative target gate. Use "
        "the SHA-pinned fail-closed target gate and prospective target cutoff "
        "without claiming stock profiles, reuse, or check-all passed."
    )
    by_id["CUST-DOTNET-MQ-REPO-TRUTH"]["reason"] = (
        "Preserve repository identity, .NET SDK and product truth, target "
        "catalogs and workflow authorities, complete analyzer/tools retirement, "
        "and inactive provider boundaries while adopting v0.12 framework-owned "
        "example cleanup and exact required paths."
    )
    by_id["CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION"]["reason"] = (
        "Adopt AI execution provenance prospectively from "
        "2026-08-12T22:08:09+08:00 and v0.12 commit-subject grammar from "
        "2026-08-13T11:05:12+08:00 without history rewrite. Preserve only the "
        "exact ad194beb3fb61a18b6870093b704264746c1516b / ASM-20260812-002 / "
        "missing-matching-trailer waiver in the target-owned fail-closed overlay "
        "while canonical v0.12 framework bytes remain exact."
    )

    state_candidate = copy.deepcopy(decisions.get("state_candidate"))
    if not isinstance(state_candidate, dict):
        raise RuntimeError("effective-rule state candidate is unavailable")
    state_candidate["framework"] = {
        "version": "v0.12.0",
        "commit": "a4fd14f0f08ad53859df1c860db0eb9643cdb2de",
        "selected_technology_profile": "dotnet-backend",
    }
    state_candidate["generated_at"] = finalized_at

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
            ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/evidence/"
            "v0.9.0/effective-rule-decisions.yaml",
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
    print(json.dumps({
        "finalized_at": finalized_at,
        "receipt_sha256": EXPECTED[RECEIPT],
        "packet_count": len(packets),
        "result": result,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
