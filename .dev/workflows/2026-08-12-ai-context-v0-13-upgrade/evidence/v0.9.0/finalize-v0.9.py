#!/usr/bin/env python3
"""Finalize the audited v0.9 target authorities and effective-rule state."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml


ROOT = Path.cwd().resolve()
WORKFLOW_ROOT = ROOT / ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade"
EVIDENCE_ROOT = WORKFLOW_ROOT / "evidence/v0.9.0"
PROVENANCE_PATH = ROOT / ".dev/ai-context/provenance.yaml"
LEDGER_PATH = ROOT / ".dev/ai-context/customizations.yaml"
DECISION_PATH = EVIDENCE_ROOT / "effective-rule-decisions.yaml"
RECEIPT_PATH = ROOT / ".dev/AI-CONTEXT-APPLY-PENDING.yaml"
EXPECTED_RECEIPT_SHA256 = (
    "b5a87952fc3e6f59714b20f0df74cbf283072ba83652a799c672b8902d2039df"
)
REPORT_03 = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "reports/03-v0.9.0-reconciliation.md"
)
OWNER_DECISION_2 = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.9.0/owner-decision-2.yaml"
)
OWNER_DECISION_3 = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "evidence/v0.9.0/owner-decision-3.yaml"
)
REPORT_02 = (
    ".dev/workflows/2026-08-12-ai-context-v0-13-upgrade/"
    "reports/02-v0.8.0-reconciliation.md"
)
TARGET_GATE = (
    "python -B .dev/ai-context/tooling/validate-target-ai-context.py "
    "--require-effective-rules --commit-range main..HEAD "
    "--workflow-id 2026-08-12-ai-context-v0-13-upgrade"
)


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected YAML mapping: {path}")
    return value


def entry_index(ledger: dict) -> dict[str, dict]:
    entries = ledger.get("customizations")
    if not isinstance(entries, list):
        raise RuntimeError("customization ledger entries are unavailable")
    result = {
        entry.get("id"): entry
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    expected = {
        "CUST-DOTNET-MQ-GOVERNANCE",
        "CUST-DOTNET-MQ-VALIDATION",
        "CUST-DOTNET-MQ-REPO-TRUTH",
        "CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION",
    }
    if set(result) != expected:
        raise RuntimeError(f"unexpected customization IDs: {sorted(result)}")
    return result


def reconcile_entry(
    entry: dict,
    *,
    relationship: str,
    reason: str,
    paths: list[str],
    incoming_status: str,
    disposition: str,
    decision_workflows: list[str],
    validation: list[str],
) -> None:
    entry["relationship"] = relationship
    entry["reason"] = reason
    entry["paths"] = paths
    entry["owner_reconciliation"] = {
        "status": "approved",
        "owner": "dotnet-mq-arch-lab maintainer via GitHub Issue #1",
        "decided_at": "2026-08-13T07:56:18+08:00",
        "evidence": OWNER_DECISION_3,
    }
    entry["decision_evidence"] = {
        "requirements": [],
        "adrs": [],
        "workflows": decision_workflows,
    }
    entry["active_context_audit"] = {
        "assessment_id": "ASM-20260812-002",
        "status": "verified",
        "evidence": ".dev/assessments/ASM-20260812-002/report.md",
    }
    entry["incoming"] = {
        "version": "v0.9.0",
        "status": incoming_status,
        "evidence": REPORT_03,
    }
    entry["disposition"] = disposition
    entry["post_upgrade_audit"] = {
        "assessment_id": "ASM-20260813-002",
        "status": "verified",
        "evidence": ".dev/assessments/ASM-20260813-002/report.md",
    }
    entry["validation"] = validation


def main() -> int:
    if not (ROOT / ".git").exists():
        raise RuntimeError("run this script from the repository root")
    receipt_sha = hashlib.sha256(RECEIPT_PATH.read_bytes()).hexdigest()
    if receipt_sha != EXPECTED_RECEIPT_SHA256:
        raise RuntimeError(f"pending receipt SHA-256 drifted: {receipt_sha}")
    if (ROOT / ".dev/ai-context/effective-rules.yaml").exists():
        raise RuntimeError("live effective-rule state already exists")
    if (ROOT / ".dev/ai-context/effective-rule-packets").exists():
        raise RuntimeError("live effective-rule packet directory already exists")

    provenance = load_yaml(PROVENANCE_PATH)
    ledger = load_yaml(LEDGER_PATH)
    decision = load_yaml(DECISION_PATH)
    if provenance.get("source", {}).get("version") != "v0.8.0":
        raise RuntimeError("v0.9 finalization requires a finalized v0.8 authority")
    if decision.get("status") != "approved-and-independently-verified":
        raise RuntimeError("effective-rule decision is not independently verified")

    finalized_at = datetime.now().astimezone().isoformat(timespec="seconds")

    previous_source = copy.deepcopy(provenance["source"])
    if previous_source != {
        "repository": "https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend.git",
        "release_id": "REL-v0.8.0",
        "version": "v0.8.0",
        "tag": "v0.8.0",
        "commit": "97ccc9e9f218ec681bb726d2e1b4edbb3e14fb25",
    }:
        raise RuntimeError("unexpected v0.8 source authority")
    provenance["template_metadata"]["template_version"] = "2.1.0"
    provenance["template_metadata"]["updated_at"] = finalized_at
    provenance["source"] = {
        "repository": "https://github.com/YuChia-Wei/ai-collaboration-framework.git",
        "release_id": "REL-v0.9.0",
        "version": "v0.9.0",
        "tag": "v0.9.0",
        "commit": "c14a3260cba7d0a9e2b67b73df9e221280d2d2ef",
    }
    provenance["installation"]["last_upgraded_at"] = finalized_at
    provenance["previous_source"] = previous_source
    provenance["reconciliation"] = {"unresolved": []}
    provenance["last_migration"] = {
        "status": "completed",
        "from_version": "v0.8.0",
        "to_version": "v0.9.0",
        "completed_at": finalized_at,
        "evidence": REPORT_03,
    }

    ledger["template_metadata"]["template_version"] = "1.1.0"
    ledger["template_metadata"]["updated_at"] = finalized_at
    entries = entry_index(ledger)

    reconcile_entry(
        entries["CUST-DOTNET-MQ-GOVERNANCE"],
        relationship="extends",
        reason=(
            "Retain target Issue-first authorization, repository governance and "
            "skill routing, directory-scoped .codex/agents tracking, exact-package "
            "defect handling, the repository LF policy, and the inactive-provider "
            "boundary while merging the byte-exact v0.9 framework lifecycle."
        ),
        paths=[
            ".gitignore",
            ".gitattributes",
            ".github/pull_request_template.md",
            "AGENTS.md",
            "AGENTS.zh-TW.md",
            ".dev/project-config.yaml",
            ".dev/ai-context/tooling/README.md",
        ],
        incoming_status="partial",
        disposition="merge",
        decision_workflows=[REPORT_03, OWNER_DECISION_3],
        validation=[
            TARGET_GATE,
            "python -B .dev/ai-context/tooling/tests/test_effective_rule_decisions.py",
        ],
    )

    tooling_paths = [
        ".dev/ai-context/tooling/README.md",
        ".dev/ai-context/tooling/git-commit-policy/validate-target-git-commits.py",
        ".dev/ai-context/tooling/target-gate-manifest.yaml",
        ".dev/ai-context/tooling/target-validation-policy.yaml",
        ".dev/ai-context/tooling/tests/test_downstream_package_projection.py",
        ".dev/ai-context/tooling/tests/test_effective_rule_decisions.py",
        ".dev/ai-context/tooling/tests/test_target_git_commit_policy.py",
        ".dev/ai-context/tooling/validate-target-ai-context.py",
    ]
    reconcile_entry(
        entries["CUST-DOTNET-MQ-VALIDATION"],
        relationship="deviates",
        reason=(
            "AICU-V090-PROJECTION-001 and AICU-V090-DOC-001 prove that the v0.9 "
            "stock source-only projection and dead target command cannot truthfully "
            "validate a downstream package. Use the SHA-pinned, "
            "downstream-applicable target gate and fail-closed overlays without "
            "claiming the stock validator or check-all gate passed."
        ),
        paths=tooling_paths,
        incoming_status="conflicting",
        disposition="merge",
        decision_workflows=[REPORT_03, OWNER_DECISION_2, OWNER_DECISION_3],
        validation=[
            TARGET_GATE,
            "python -B -m unittest discover -s .dev/ai-context/tooling/tests -p 'test_*.py' -v",
        ],
    )

    reconcile_entry(
        entries["CUST-DOTNET-MQ-REPO-TRUTH"],
        relationship="target-only",
        reason=(
            "Preserve repository identity, SDK and product truth, target catalogs "
            "and workflow authorities, the complete analyzer/tools retirement, and "
            "the canonical bundled provider's source-available inactive state."
        ),
        paths=[
            ".dev/ARCHITECTURE.md",
            ".dev/INDEX.md",
            ".dev/README.MD",
            ".dev/adr/INDEX.md",
            ".dev/backlog/INDEX.MD",
            ".dev/problem-frames/INDEX.md",
            ".dev/project-config.yaml",
            ".dev/specs/INDEX.MD",
            ".dev/workflows/INDEX.MD",
            ".editorconfig",
            ".gitattributes",
            ".gitignore",
            "AGENTS.md",
            "AGENTS.zh-TW.md",
            "CLAUDE.md",
            "README.md",
            "README.en.md",
            "global.json",
            "MQArchLab.slnx",
        ],
        incoming_status="conflicting",
        disposition="retain",
        decision_workflows=[REPORT_03, OWNER_DECISION_2, OWNER_DECISION_3],
        validation=[
            TARGET_GATE,
            "dotnet build MQArchLab.slnx --no-restore --disable-build-servers -m:1",
        ],
    )

    reconcile_entry(
        entries["CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION"],
        relationship="deviates",
        reason=(
            "Adopt execution provenance prospectively from "
            "2026-08-12T22:08:09+08:00 and preserve only the exact "
            "ad194beb3fb61a18b6870093b704264746c1516b / ASM-20260812-002 / "
            "missing-matching-trailer waiver in the target-owned fail-closed "
            "overlay while canonical v0.9 framework bytes remain exact."
        ),
        paths=[
            ".dev/ai-context/tooling/README.md",
            ".dev/ai-context/tooling/target-validation-policy.yaml",
            ".dev/ai-context/tooling/validate-target-ai-context.py",
            ".dev/ai-context/tooling/git-commit-policy/validate-target-git-commits.py",
            ".dev/ai-context/tooling/tests/test_target_git_commit_policy.py",
            "AGENTS.md",
            "AGENTS.zh-TW.md",
        ],
        incoming_status="conflicting",
        disposition="merge",
        decision_workflows=[REPORT_02, REPORT_03, OWNER_DECISION_3],
        validation=[
            TARGET_GATE,
            "python -B .dev/ai-context/tooling/tests/test_target_git_commit_policy.py",
        ],
    )

    state_candidate = copy.deepcopy(decision.get("state_candidate"))
    if not isinstance(state_candidate, dict):
        raise RuntimeError("effective-rule state candidate is unavailable")
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
            "v0.9.0/validation-summary.yaml",
            ".dev/assessments/ASM-20260813-002/report.md",
        ],
    )
    if result.get("status") != "finalized":
        raise RuntimeError(f"unexpected finalization result: {result}")
    readiness = result.get("effective_rule_readiness")
    if not isinstance(readiness, dict) or readiness.get("action_ready") is not True:
        raise RuntimeError(f"effective-rule state is not ready: {readiness}")
    packet_count = len(list((ROOT / ".dev/ai-context/effective-rule-packets").glob("*.yaml")))
    if packet_count != 20:
        raise RuntimeError(f"expected 20 effective-rule packets, found {packet_count}")
    print(
        json.dumps(
            {
                "finalized_at": finalized_at,
                "receipt_sha256": receipt_sha,
                "packet_count": packet_count,
                "result": result,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
