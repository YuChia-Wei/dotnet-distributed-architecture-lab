#!/usr/bin/env python3
"""Run the sealed direct-upgrade target validation profile once without binding it."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


sys.dont_write_bytecode = True
FRAMEWORK_ROOT = Path(__file__).resolve().parents[5]
RUNTIME_SCRIPTS = FRAMEWORK_ROOT / ".ai/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(
    ".ai/assets/skills/ai-context-upgrader/scripts/run-target-validation.py"
)

import ai_context_package_apply as APPLY


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def path_is_present(path: Path) -> bool:
    return path.exists() or path.is_symlink() or APPLY.is_reparse_point(path)


def require_absent(path: Path, label: str) -> None:
    if path_is_present(path):
        raise APPLY.ApplyError(
            f"{label} already exists; preserve the retained unbound attempt through "
            "an explicitly authorized recovery before retrying"
        )


def write_attempt(root: Path, attempt: dict) -> Path:
    """Retain a non-authoritative record when no passing receipt can be produced."""
    path = root / f"target-validation-attempt-{uuid.uuid4().hex}.json"
    require_absent(path, "target validation attempt metadata")
    APPLY.atomic_write_bytes(path, APPLY.canonical_json_bytes(attempt))
    return path


def execution_record(
    argv: list[str],
    outcome: str,
    exit_code: int | None,
    started_at: str,
    completed_at: str,
    output_sha256: str,
    transaction_id: str,
) -> dict:
    return {
        "argv": argv,
        "outcome": outcome,
        "exit_code": exit_code,
        "started_at": started_at,
        "completed_at": completed_at,
        "output_sha256": output_sha256,
        "evidence": (
            f".git/ai-context-package-apply/{transaction_id}/"
            f"{APPLY.TARGET_VALIDATION_OUTPUT_PATH}"
        ),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pending_receipt_identity(target: Path) -> dict:
    pending_path = target / APPLY.PENDING_RECEIPT_PATH
    APPLY.reject_symlink_boundary(target, APPLY.PENDING_RECEIPT_PATH)
    if (
        not pending_path.is_file()
        or pending_path.is_symlink()
        or APPLY.is_reparse_point(pending_path)
    ):
        raise APPLY.ApplyError("pending apply receipt is unavailable for target validation")
    return {
        "path": APPLY.PENDING_RECEIPT_PATH,
        "sha256": APPLY.sha256_bytes(pending_path.read_bytes()),
    }


def next_record_command(transaction_id: str) -> str:
    receipt = (
        f".git/ai-context-package-apply/{transaction_id}/"
        f"{APPLY.TARGET_VALIDATION_RECEIPT_PATH}"
    )
    return (
        "python .ai/scripts/plan-ai-context-package-apply.py --target-root . "
        f"--record-target-validation-receipt {transaction_id} "
        f"--target-validation-receipt {receipt}"
    )


def run_target_validation(target: Path, transaction_id: str) -> tuple[dict | None, int, str]:
    """Execute exactly the sealed profile and leave authority/journal state unchanged."""
    with APPLY.transaction_lock(target):
        root, plan, journal = APPLY.load_transaction(
            target,
            transaction_id,
            allow_unbound_target_validation_receipt=True,
        )
        if not APPLY.is_upgrade_plan(plan):
            raise APPLY.ApplyError("clean-install transactions do not run target validation")
        if APPLY.route_checkpoint_context(plan) is not None:
            raise APPLY.ApplyError(
                "multi-hop child target validation must be run by the sealed route orchestrator"
            )
        if journal.get("state") != "awaiting-target-validation":
            raise APPLY.ApplyError(
                "target validation requires an applied direct upgrade awaiting target validation"
            )
        if journal.get("target_validation_receipt_sha256") is not None:
            raise APPLY.ApplyError("target validation receipt is already bound")
        remediation = APPLY.validate_upgrade_remediation_artifacts(
            root,
            plan,
            journal,
            allow_unbound_target_validation_receipt=True,
        )
        if remediation is None:
            raise APPLY.ApplyError("upgrade remediation evidence is unavailable")
        packet, decision = remediation
        snapshot_paths = (
            set(plan.get("observed", {}))
            | {item["path"] for item in plan.get("required_framework_paths", [])}
            | set(APPLY.touched_paths(plan))
            | set(APPLY.protected_target_paths(target))
            | {APPLY.PENDING_RECEIPT_PATH}
            | {item["path"] for item in APPLY.target_staging_records(plan)}
        )
        snapshot = APPLY.capture_target_git_snapshot(
            target,
            snapshot_paths,
            phase="target-validation-runner",
            require_clean=False,
        )
        with APPLY.target_git_snapshot_scope(snapshot):
            APPLY.verify_recovery_surface(target, plan, journal, full_worktree_scan=True)

        output_path = root / APPLY.TARGET_VALIDATION_OUTPUT_PATH
        receipt_path = root / APPLY.TARGET_VALIDATION_RECEIPT_PATH
        require_absent(output_path, "target validation output")
        require_absent(receipt_path, "target validation receipt")

        profile = packet["target_validation_profile"]
        argv = profile["argv"]
        started_at = timestamp()
        launch_error: OSError | None = None
        interrupted = False
        with output_path.open("xb") as output_stream:
            try:
                child = subprocess.run(
                    argv,
                    cwd=target,
                    stdout=output_stream,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                exit_code: int | None = child.returncode
            except OSError as error:
                launch_error = error
                exit_code = None
            except KeyboardInterrupt:
                interrupted = True
                exit_code = 130
        completed_at = timestamp()
        output_sha256 = sha256_file(output_path)

        if exit_code != 0:
            outcome = (
                "interrupted"
                if interrupted
                else "blocked"
                if launch_error is not None
                else "failed"
            )
            execution = execution_record(
                argv,
                outcome,
                exit_code,
                started_at,
                completed_at,
                output_sha256,
                transaction_id,
            )
            attempt = {
                "schema_version": "target-validation-attempt/v1",
                "transaction_id": transaction_id,
                "plan_sha256": transaction_id,
                "packet_sha256": APPLY.packet_digest(packet),
                "decision_sha256": journal["remediation_decision_sha256"],
                "target_validation_profile_digest": packet[
                    "target_validation_profile_digest"
                ],
                "execution": execution,
                "receipt_outcome": "not-produced",
                "reason": (
                    "target-validation-interrupted"
                    if interrupted
                    else "target-validation-launch-failed"
                    if launch_error is not None
                    else "target-validation-exit-nonzero"
                ),
            }
            attempt_path = write_attempt(root, attempt)
            return None, exit_code if isinstance(exit_code, int) and exit_code > 0 else 1, (
                f"Target validation did not pass; raw evidence is retained at "
                f"{output_path.name} and attempt metadata at {attempt_path.name}."
            )

        execution = execution_record(
            argv,
            "passed",
            0,
            started_at,
            completed_at,
            output_sha256,
            transaction_id,
        )
        receipt = {
            "schema_version": APPLY.TARGET_VALIDATION_RECEIPT_SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "plan_sha256": transaction_id,
            "packet_sha256": APPLY.packet_digest(packet),
            "decision_sha256": journal["remediation_decision_sha256"],
            "target": {
                "root": packet["target"]["root"],
                "starting_commit": packet["target"]["starting_commit"],
                "observed_prestate_sha256": packet["target"][
                    "observed_prestate_sha256"
                ],
            },
            "target_validation_profile": profile,
            "target_validation_profile_digest": packet[
                "target_validation_profile_digest"
            ],
            "pending_receipt": pending_receipt_identity(target),
            "execution": execution,
        }
        try:
            APPLY.validate_target_validation_receipt(
                receipt, plan, journal, packet, decision
            )
            require_absent(receipt_path, "target validation receipt")
            APPLY.atomic_write_bytes(receipt_path, APPLY.canonical_json_bytes(receipt))
        except (APPLY.ApplyError, OSError, ValueError) as error:
            attempt = {
                "schema_version": "target-validation-attempt/v1",
                "transaction_id": transaction_id,
                "plan_sha256": transaction_id,
                "packet_sha256": APPLY.packet_digest(packet),
                "decision_sha256": journal["remediation_decision_sha256"],
                "target_validation_profile_digest": packet[
                    "target_validation_profile_digest"
                ],
                "execution": execution,
                "receipt_outcome": "not-produced",
                "reason": "target-validation-receipt-validation-failed",
                "error": str(error),
            }
            write_attempt(root, attempt)
            raise
        return receipt, 0, (
            "Target validation passed and an unbound canonical receipt was retained.\n"
            f"Next, from the target root, run:\n{next_record_command(transaction_id)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    try:
        _receipt, exit_code, message = run_target_validation(
            args.target_root.resolve(), args.transaction_id
        )
    except (APPLY.ApplyError, OSError, ValueError) as error:
        print(f"Target validation runner failed: {error}", file=sys.stderr)
        return 2
    print(message)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
