#!/usr/bin/env python3
"""Validate downstream AI context provenance without source release history."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCRIPT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_ROOT))

from ai_context_target_provenance import validate_target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--allow-unfinalized", action="store_true")
    args = parser.parse_args()
    errors = validate_target(
        args.root, require_finalized=not args.allow_unfinalized
    )
    if errors:
        print("AI context target validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AI context target validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
