#!/usr/bin/env python3
"""Resolve one explicit framework-source or initialized-target rule packet.

The command is intentionally read-only.  The mandatory applicability mode is
never inferred from repository contents.  ``--emit-candidate`` remains an
initialized-target reconciliation aid: it prints a deterministic packet
candidate but never writes it and never makes a missing packet available to an
action skill.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/resolve-effective-rule-packet.py")

import yaml

from ai_context_effective_rules import (
    EffectiveRuleError,
    build_packet_candidate,
    initialized_target_diagnostic,
    resolve_effective_rule_packet_for_mode,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--applicability-mode",
        required=True,
        choices=("framework-source", "initialized-target"),
        help="Explicit repository applicability mode; it is never inferred.",
    )
    parser.add_argument("--capability", required=True)
    parser.add_argument("--execution-mode", required=True)
    parser.add_argument("--technology-profile", required=True)
    parser.add_argument("--file-type", required=True)
    parser.add_argument(
        "--source-rule-id",
        action="append",
        default=None,
        help="Repeatable explicit framework-source rule ID; required only in framework-source mode.",
    )
    parser.add_argument(
        "--selection-evidence",
        action="append",
        default=None,
        help="Repeatable explicit framework-source selection evidence; required only in framework-source mode.",
    )
    parser.add_argument(
        "--emit-candidate",
        action="store_true",
        help="Print a reconciliation candidate only; it does not write or activate a packet.",
    )
    parser.add_argument(
        "--resolver-evidence",
        action="append",
        default=[],
        help="Repository-relative reconciliation evidence; required with --emit-candidate.",
    )
    args = parser.parse_args()
    try:
        dimensions = {
            "capability": args.capability,
            "execution_mode": args.execution_mode,
            "technology_profile": args.technology_profile,
            "file_type": args.file_type,
        }
        if args.applicability_mode == "framework-source":
            if args.emit_candidate or args.resolver_evidence:
                raise EffectiveRuleError(
                    "source-applicability: --emit-candidate and --resolver-evidence are initialized-target-only"
                )
            packet = resolve_effective_rule_packet_for_mode(
                args.root,
                applicability_mode=args.applicability_mode,
                **dimensions,
                source_rule_ids=args.source_rule_id,
                selection_evidence=args.selection_evidence,
            )
        else:
            if args.source_rule_id is not None or args.selection_evidence is not None:
                raise EffectiveRuleError(
                    "downstream-semantics-unresolved: --source-rule-id and --selection-evidence are framework-source-only"
                )
            if args.emit_candidate:
                packet = build_packet_candidate(
                    args.root,
                    **dimensions,
                    resolver_evidence=args.resolver_evidence,
                )
            else:
                if args.resolver_evidence:
                    raise EffectiveRuleError(
                        "--resolver-evidence is only valid with --emit-candidate"
                    )
                packet = resolve_effective_rule_packet_for_mode(
                    args.root,
                    applicability_mode=args.applicability_mode,
                    **dimensions,
                )
        print(yaml.safe_dump(packet, sort_keys=False, allow_unicode=True), end="")
        return 0
    except (EffectiveRuleError, OSError, ValueError) as exc:
        detail = str(exc)
        if (
            isinstance(exc, EffectiveRuleError)
            and args.applicability_mode == "initialized-target"
        ):
            detail = initialized_target_diagnostic(exc)
        print(f"Effective rule packet resolution failed: {detail}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
