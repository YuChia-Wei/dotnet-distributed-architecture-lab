#!/usr/bin/env python3
"""Plan, apply, resume, or roll back an extracted AI context package."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The planner is executed from inside the checksum-governed extracted envelope.
# Prevent the local module import from creating an ungoverned __pycache__ member
# before the envelope checksum set is verified.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/plan-ai-context-package-apply.py")

import yaml

from ai_context_package_apply import (
    ApplyError,
    apply_plan,
    atomic_write_bytes,
    build_plan,
    build_upgrade_remediation_packet,
    canonical_json_bytes,
    is_upgrade_plan,
    load_upgrade_remediation_decision,
    record_target_validation_receipt,
    recover_transaction,
    render_upgrade_remediation_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--previous-files", type=Path)
    parser.add_argument(
        "--previous-version",
        help=(
            "Exact source version for schema 2 upgrades; must be supplied with "
            "--previous-files"
        ),
    )
    parser.add_argument("--acknowledge", action="append", default=[])
    parser.add_argument(
        "--enable-provider",
        action="append",
        default=[],
        choices=["repo-backlog"],
        help="Enable an optional provider for a clean installation.",
    )
    lifecycle = parser.add_mutually_exclusive_group()
    lifecycle.add_argument("--apply", action="store_true")
    lifecycle.add_argument("--resume", metavar="TRANSACTION_ID")
    lifecycle.add_argument("--rollback", metavar="TRANSACTION_ID")
    lifecycle.add_argument(
        "--record-target-validation-receipt",
        metavar="TRANSACTION_ID",
        help=(
            "Bind a supplied canonical target-validation receipt after apply; "
            "this mode never executes or routes target commands."
        ),
    )
    parser.add_argument("--plan-output", type=Path)
    parser.add_argument(
        "--remediation-packet-output",
        type=Path,
        help="Write the canonical upgrade remediation packet outside the package and target.",
    )
    parser.add_argument(
        "--remediation-report-output",
        type=Path,
        help="Write the report derived from the canonical remediation packet.",
    )
    parser.add_argument(
        "--remediation-decision",
        type=Path,
        help="Explicit owner decision for an upgrade apply; never inferred from a proposal.",
    )
    parser.add_argument(
        "--target-validation-receipt",
        type=Path,
        help=(
            "Canonical target-validation-receipt/v1 produced by an explicit "
            "external target-validation execution."
        ),
    )
    args = parser.parse_args()
    try:
        if (
            args.resume
            or args.rollback
            or args.record_target_validation_receipt
        ):
            if (
                args.plan_output
                or args.remediation_packet_output
                or args.remediation_report_output
                or args.remediation_decision
                or args.previous_files
                or args.previous_version
                or args.acknowledge
                or args.enable_provider
            ):
                raise ApplyError(
                    "recovery cannot change the sealed plan, decision, selection, or acknowledgements"
                )
            if args.record_target_validation_receipt:
                if args.package_root is not None:
                    raise ApplyError(
                        "recording a target validation receipt does not accept --package-root"
                    )
                if args.target_validation_receipt is None:
                    raise ApplyError(
                        "--record-target-validation-receipt requires --target-validation-receipt"
                    )
                result = record_target_validation_receipt(
                    args.target_root,
                    args.record_target_validation_receipt,
                    args.target_validation_receipt,
                )
                print(
                    yaml.safe_dump(
                        {"target_validation_receipt": result}, sort_keys=False
                    ),
                    end="",
                )
                return 0
            if args.target_validation_receipt is not None:
                raise ApplyError(
                    "--target-validation-receipt requires --record-target-validation-receipt"
                )
            if args.resume and args.package_root is None:
                raise ApplyError("--resume requires --package-root")
            result = recover_transaction(
                args.target_root,
                args.resume or args.rollback,
                "resume" if args.resume else "rollback",
                args.package_root,
            )
            label = "apply_receipt" if args.resume else "rollback_journal"
            print(yaml.safe_dump({label: result}, sort_keys=False), end="")
            return 0
        if args.target_validation_receipt is not None:
            raise ApplyError(
                "--target-validation-receipt requires --record-target-validation-receipt"
            )
        if args.package_root is None:
            raise ApplyError("planning and --apply require --package-root")
        for configured_output, option_name in (
            (args.plan_output, "--plan-output"),
            (args.remediation_packet_output, "--remediation-packet-output"),
            (args.remediation_report_output, "--remediation-report-output"),
        ):
            if configured_output is None:
                continue
            output = configured_output.resolve()
            for forbidden_root, root_label in (
                (args.package_root.resolve(), "extracted package"),
                (args.target_root.resolve(), "target repository"),
            ):
                if output == forbidden_root or output.is_relative_to(forbidden_root):
                    raise ApplyError(f"{option_name} must be outside the {root_label}")
        plan = build_plan(
            args.package_root,
            args.target_root,
            args.previous_files,
            args.previous_version,
            args.enable_provider,
        )
        content = yaml.safe_dump(plan, sort_keys=False, allow_unicode=True)
        if args.plan_output:
            atomic_write_bytes(args.plan_output, content.encode("utf-8"))
        packet = build_upgrade_remediation_packet(plan) if is_upgrade_plan(plan) else None
        if packet is None and (
            args.remediation_packet_output or args.remediation_report_output
        ):
            raise ApplyError("remediation packet and report outputs require an upgrade plan")
        if packet is not None and args.remediation_packet_output:
            atomic_write_bytes(
                args.remediation_packet_output, canonical_json_bytes(packet)
            )
        if packet is not None and args.remediation_report_output:
            atomic_write_bytes(
                args.remediation_report_output,
                render_upgrade_remediation_report(packet).encode("utf-8"),
            )
        print(content, end="")
        if not args.apply:
            if args.remediation_decision:
                raise ApplyError("--remediation-decision requires --apply")
            if packet is not None:
                print(
                    "Upgrade remediation packet prepared: "
                    f"{packet['canonical_digest']}",
                )
            print("Dry run only. Re-run with --apply after reviewing the plan.")
            return 0
        decision = None
        if is_upgrade_plan(plan):
            if args.remediation_decision is None:
                raise ApplyError("upgrade --apply requires --remediation-decision")
            if args.acknowledge:
                raise ApplyError(
                    "upgrade --apply records reconciliation only in --remediation-decision"
                )
            decision = load_upgrade_remediation_decision(args.remediation_decision)
        elif args.remediation_decision is not None:
            raise ApplyError("clean-install --apply does not accept --remediation-decision")
        receipt = apply_plan(
            plan,
            set(args.acknowledge),
            remediation_decision=decision,
        )
        print(yaml.safe_dump({"apply_receipt": receipt}, sort_keys=False), end="")
        return 0
    except (OSError, ApplyError, ValueError) as exc:
        print(f"AI context package apply failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
