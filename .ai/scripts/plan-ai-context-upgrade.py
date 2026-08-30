#!/usr/bin/env python3
"""Emit canonical, read-only AI-context upgrade-route evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ai_context_upgrade_routes import MatrixValidationError, canonical_json, resolve_matrix_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve one explicit AI-context upgrade route without target mutation."
    )
    parser.add_argument("--matrix", required=True, type=Path, help="Explicit upgrade-route matrix YAML")
    parser.add_argument("--origin", required=True, help="Explicit installed source version")
    parser.add_argument("--target", required=True, help="Explicit requested source version")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = resolve_matrix_file(args.matrix, origin=args.origin, target=args.target)
    except MatrixValidationError as exc:
        sys.stderr.buffer.write(canonical_json({"error": str(exc)}).encode("utf-8"))
        return 2
    sys.stdout.buffer.write(canonical_json(result).encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
