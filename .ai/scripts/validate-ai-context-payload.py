#!/usr/bin/env python3
"""Validate an extracted incoming AI-context package without source-repo access."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# This command itself runs inside the extracted payload.  Set the process flag
# before importing the sibling validator so validation never creates an
# unchecksummed __pycache__ member in the candidate envelope.
sys.dont_write_bytecode = True

from ai_context_package_validation import PackageValidationError, validate_extracted_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-closed validation for an extracted AI-context package candidate."
    )
    parser.add_argument(
        "--package-root",
        required=True,
        type=Path,
        help="freshly extracted package envelope root",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = validate_extracted_package(args.package_root)
    except PackageValidationError as exc:
        print(f"incoming package validation failed: {exc}", file=sys.stderr)
        return 1
    print(
        "incoming package validation passed: "
        f"package_id={summary['package_id']}; "
        f"payload_file_count={summary['payload_file_count']}; "
        f"portable_entrypoints_verified={summary['portable_entrypoints_verified']}; "
        "source_only_tests=excluded-from-portable-validation"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
