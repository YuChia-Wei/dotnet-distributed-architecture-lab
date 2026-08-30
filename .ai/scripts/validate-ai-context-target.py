#!/usr/bin/env python3
"""Validate downstream AI context provenance without source release history."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-context-target.py")

from ai_context_target_provenance import effective_rule_readiness, validate_target
from ai_context_cli_routing import validate_cli_execution_routing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--allow-unfinalized", action="store_true")
    parser.add_argument(
        "--require-effective-rules",
        action="store_true",
        help="Require a fresh target-effective state and every indexed packet.",
    )
    args = parser.parse_args()
    errors = validate_target(
        args.root,
        require_finalized=not args.allow_unfinalized,
        require_effective_rules=args.require_effective_rules,
    )
    cli_routes = validate_cli_execution_routing(
        errors,
        root=args.root,
    )
    if errors:
        print("AI context target validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "AI context target validation passed: "
        f"{cli_routes} local CLI routes."
    )
    readiness = effective_rule_readiness(args.root)
    if readiness["action_ready"]:
        print("Effective rule action readiness: ready.")
    else:
        print(
            "Effective rule action readiness: "
            f"{readiness['status']} ({readiness['reason']})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
