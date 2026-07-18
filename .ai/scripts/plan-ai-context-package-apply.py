#!/usr/bin/env python3
"""Plan an extracted AI context package application; apply only with --apply."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError as exc:
    if exc.name != "yaml":
        raise
    print(
        "AI context package apply requires PyYAML==6.0.3; from the extracted envelope run: "
        "python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2) from exc

# The planner is executed from inside the checksum-governed extracted envelope.
# Prevent the local module import from creating an ungoverned __pycache__ member
# before the envelope checksum set is verified.
sys.dont_write_bytecode = True

from ai_context_package_apply import ApplyError, apply_plan, build_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--previous-files", type=Path)
    parser.add_argument("--acknowledge", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--plan-output", type=Path)
    args = parser.parse_args()
    try:
        if args.plan_output:
            output = args.plan_output.resolve()
            for forbidden_root, label in (
                (args.package_root.resolve(), "extracted package"),
                (args.target_root.resolve(), "target repository"),
            ):
                if output == forbidden_root or output.is_relative_to(forbidden_root):
                    raise ApplyError(f"--plan-output must be outside the {label}")
        plan = build_plan(args.package_root, args.target_root, args.previous_files)
        content = yaml.safe_dump(plan, sort_keys=False, allow_unicode=True)
        if args.plan_output:
            args.plan_output.write_text(content, encoding="utf-8", newline="\n")
        print(content, end="")
        if not args.apply:
            print("Dry run only. Re-run with --apply after reviewing the plan.")
            return 0
        receipt = apply_plan(plan, set(args.acknowledge))
        print(yaml.safe_dump({"apply_receipt": receipt}, sort_keys=False), end="")
        return 0
    except (OSError, ApplyError, ValueError) as exc:
        print(f"AI context package apply failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
