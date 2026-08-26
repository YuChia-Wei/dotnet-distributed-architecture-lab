#!/usr/bin/env python3
"""Finalize the independently audited v0.10 target authorities and rule state."""

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
EVIDENCE = WORKFLOW / "evidence/v0.10.0"
PROVENANCE = ROOT / ".dev/ai-context/provenance.yaml"
LEDGER = ROOT / ".dev/ai-context/customizations.yaml"
RECEIPT = ROOT / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
DECISIONS = WORKFLOW / "evidence/v0.9.0/effective-rule-decisions.yaml"
REPORT = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "reports/04-v0.10.0-reconciliation.md"
)
PREFLIGHT = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.10.0/preflight.yaml"
)
ASSESSMENT = ".dev/assessments/ASM-20260813-003/report.md"
EXPECTED = {
    PROVENANCE: "a3ed2a41a8b6653f1a385dab89e88685bf46786857b16ca97ebbfa4599ce0091",
    LEDGER: "aa2ad492b49e8ef7ad5db7147d9d0e42d20408de106f15fddbe87f8d1bf45428",
    RECEIPT: "8056ef55523c20f91228e2c02351b18761f8173e0a2366e8c7bbb133e06b29d0",
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
    if provenance.get("source", {}).get("version") != "v0.9.0":
        raise RuntimeError("v0.10 finalization requires exact finalized v0.9 authority")
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
        "release_id": "REL-v0.9.0",
        "version": "v0.9.0",
        "tag": "v0.9.0",
        "commit": "c14a3260cba7d0a9e2b67b73df9e221280d2d2ef",
    }
    if previous_source != expected_previous:
        raise RuntimeError(f"unexpected v0.9 source authority: {previous_source}")

    provenance["template_metadata"]["updated_at"] = finalized_at
    provenance["source"] = {
        "repository": "https://github.com/YuChia-Wei/ai-collaboration-framework.git",
        "release_id": "REL-v0.10.0",
        "version": "v0.10.0",
        "tag": "v0.10.0",
        "commit": "5878f213b50bdbb4b3123a60525cdc206fd5be04",
    }
    provenance["installation"]["last_upgraded_at"] = finalized_at
    provenance["previous_source"] = previous_source
    provenance["reconciliation"] = {"unresolved": []}
    provenance["last_migration"] = {
        "status": "completed",
        "from_version": "v0.9.0",
        "to_version": "v0.10.0",
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
            "version": "v0.10.0",
            "status": current_status,
            "evidence": REPORT,
        }
        entry["post_upgrade_audit"] = {
            "assessment_id": "ASM-20260813-003",
            "status": "verified",
            "evidence": ASSESSMENT,
        }
        workflows = entry.setdefault("decision_evidence", {}).setdefault("workflows", [])
        for evidence in (PREFLIGHT, REPORT):
            if evidence not in workflows:
                workflows.append(evidence)

    by_id["CUST-DOTNET-MQ-GOVERNANCE"]["reason"] = (
        "Retain target Issue-first authorization, repository governance and skill "
        "routing, directory-scoped .codex/agents tracking, exact-package defect "
        "handling, the repository LF policy, and inactive provider/profile/reuse "
        "boundaries while merging the byte-exact v0.10 framework lifecycle."
    )
    by_id["CUST-DOTNET-MQ-VALIDATION"]["reason"] = (
        "AICU-V010-PROJECTION-001 and carried AICU-V090-DOC-001 prove that the "
        "v0.10 stock source-only projection and dead target command cannot "
        "truthfully validate this downstream package. Use the SHA-pinned target "
        "gate without claiming stock profiles or check-all passed."
    )
    by_id["CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION"]["reason"] = (
        "Adopt execution provenance prospectively from 2026-08-12T22:08:09+08:00 "
        "and preserve only the exact ad194beb3fb61a18b6870093b704264746c1516b / "
        "ASM-20260812-002 / missing-matching-trailer waiver in the target-owned "
        "fail-closed overlay while canonical v0.10 framework bytes remain exact."
    )

    state_candidate = copy.deepcopy(decisions.get("state_candidate"))
    if not isinstance(state_candidate, dict):
        raise RuntimeError("effective-rule state candidate is unavailable")
    state_candidate["framework"] = {
        "version": "v0.10.0",
        "commit": "5878f213b50bdbb4b3123a60525cdc206fd5be04",
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
            ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/evidence/"
            "v0.10.0/validation-summary.yaml",
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
