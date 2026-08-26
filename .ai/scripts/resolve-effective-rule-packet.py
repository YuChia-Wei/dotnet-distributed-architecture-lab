#!/usr/bin/env python3
"""Resolve one existing, freshness-validated target-effective rule packet.

The default command is intentionally read-only.  ``--emit-candidate`` is an
explicit reconciliation aid: it prints a deterministic packet candidate but
never writes it and never makes a missing packet available to an action skill.
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
    resolve_effective_rule_packet,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--capability", required=True)
    parser.add_argument("--execution-mode", required=True)
    parser.add_argument("--technology-profile", required=True)
    parser.add_argument("--file-type", required=True)
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
            packet = resolve_effective_rule_packet(args.root, **dimensions)
        print(yaml.safe_dump(packet, sort_keys=False, allow_unicode=True), end="")
        return 0
    except (EffectiveRuleError, OSError, ValueError) as exc:
        print(f"Effective rule packet resolution failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
