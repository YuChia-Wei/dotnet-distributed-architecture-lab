#!/usr/bin/env python3
"""Compose the published commit policy with exact target historical boundaries."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[4]
CONFIG_PATH = ROOT / ".dev/ai-context/tooling/target-validation-policy.yaml"
PACKAGE_VALIDATOR_PATH = ROOT / ".ai/scripts/validate-git-commits.py"
EXPECTED_CONFIG_FIELDS = {
    "schema_version",
    "package_policy",
    "package_validator",
    "commit_subject",
    "ai_signature",
    "assessment_historical_exceptions",
}
EXPECTED_EXCEPTION_FIELDS = {
    "commit",
    "assessment_id",
    "waived_error",
    "reason",
    "evidence",
}
SUPPORTED_WAIVER = "missing-matching-trailer"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_package_validator(config: dict[str, object] | None = None) -> Any:
    config = load_target_config() if config is None else config
    validator = config.get("package_validator")
    if not isinstance(validator, dict):
        raise ValueError("package_validator must be a mapping")
    path = ROOT / str(validator.get("path", ""))
    if path != PACKAGE_VALIDATOR_PATH:
        raise ValueError("package_validator.path must identify the canonical validator")
    actual = sha256(path)
    if actual != str(validator.get("sha256", "")):
        raise ValueError(
            f"package validator hash mismatch: expected={validator.get('sha256')} actual={actual}"
        )
    spec = importlib.util.spec_from_file_location(
        "framework_validate_git_commits",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load package validator: {PACKAGE_VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_target_config(path: Path = CONFIG_PATH) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("target validation policy must be a mapping")
    return value


def validate_target_config(config: dict[str, object]) -> list[str]:
    errors: list[str] = []
    unknown = sorted(set(config) - EXPECTED_CONFIG_FIELDS)
    missing = sorted(EXPECTED_CONFIG_FIELDS - set(config))
    if unknown:
        errors.append(f"unknown target validation policy fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"missing target validation policy fields: {', '.join(missing)}")
    if unknown or missing:
        return errors

    if str(config["schema_version"]) != "1.1":
        errors.append("target validation policy schema_version must be 1.1")

    package = config["package_policy"]
    if not isinstance(package, dict) or set(package) != {
        "path",
        "expected_schema_version",
        "sha256",
    }:
        errors.append(
            "package_policy must contain exactly path, expected_schema_version, and sha256"
        )
    elif str(package["path"]) != ".dev/standards/GIT-COMMIT-POLICY.yaml":
        errors.append("package_policy.path must identify the canonical published policy")
    elif not (ROOT / str(package["path"])).is_file():
        errors.append("package commit policy is missing")
    elif sha256(ROOT / str(package["path"])) != str(package["sha256"]):
        errors.append("package commit policy hash mismatch")

    validator = config["package_validator"]
    if not isinstance(validator, dict) or set(validator) != {"path", "sha256"}:
        errors.append("package_validator must contain exactly path and sha256")
    elif str(validator["path"]) != ".ai/scripts/validate-git-commits.py":
        errors.append("package_validator.path must identify the canonical validator")
    elif not (ROOT / str(validator["path"])).is_file():
        errors.append("package commit validator is missing")
    elif sha256(ROOT / str(validator["path"])) != str(validator["sha256"]):
        errors.append("package commit validator hash mismatch")

    commit_subject = config["commit_subject"]
    if not isinstance(commit_subject, dict) or set(commit_subject) != {
        "effective_at_override"
    }:
        errors.append("commit_subject must contain exactly effective_at_override")
    else:
        try:
            effective_at = datetime.fromisoformat(
                str(commit_subject["effective_at_override"])
            )
            if effective_at.tzinfo is None:
                errors.append(
                    "commit_subject.effective_at_override must include a timezone"
                )
        except ValueError:
            errors.append("commit_subject.effective_at_override must be ISO 8601")

    signature = config["ai_signature"]
    if not isinstance(signature, dict) or set(signature) != {"effective_at_override"}:
        errors.append("ai_signature must contain exactly effective_at_override")
    else:
        try:
            effective_at = datetime.fromisoformat(str(signature["effective_at_override"]))
            if effective_at.tzinfo is None:
                errors.append("ai_signature.effective_at_override must include a timezone")
        except ValueError:
            errors.append("ai_signature.effective_at_override must be ISO 8601")

    exceptions = config["assessment_historical_exceptions"]
    if not isinstance(exceptions, list):
        errors.append("assessment_historical_exceptions must be a list")
        return errors

    seen: set[str] = set()
    for index, exception in enumerate(exceptions):
        label = f"assessment_historical_exceptions[{index}]"
        if not isinstance(exception, dict):
            errors.append(f"{label} must be a mapping")
            continue
        unknown_fields = sorted(set(exception) - EXPECTED_EXCEPTION_FIELDS)
        missing_fields = sorted(EXPECTED_EXCEPTION_FIELDS - set(exception))
        if unknown_fields:
            errors.append(f"{label} has unknown fields: {', '.join(unknown_fields)}")
        if missing_fields:
            errors.append(f"{label} is missing fields: {', '.join(missing_fields)}")
        if unknown_fields or missing_fields:
            continue
        commit = str(exception["commit"])
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            errors.append(f"{label}.commit must be a full lowercase Git SHA")
        elif commit in seen:
            errors.append(f"duplicate historical exception commit: {commit}")
        seen.add(commit)
        if not re.fullmatch(r"ASM-[0-9]{8}-[0-9]{3}", str(exception["assessment_id"])):
            errors.append(f"{label}.assessment_id is invalid")
        if str(exception["waived_error"]) != SUPPORTED_WAIVER:
            errors.append(f"{label}.waived_error is unsupported")
        if not str(exception["reason"]).strip() or not str(exception["evidence"]).strip():
            errors.append(f"{label}.reason and evidence must be non-empty")
        evidence = ROOT / str(exception["evidence"])
        if not evidence.is_file():
            errors.append(f"{label}.evidence does not exist: {exception['evidence']}")
    return errors


def package_policy(config: dict[str, object]) -> dict[str, object]:
    package = config["package_policy"]
    assert isinstance(package, dict)
    path = ROOT / str(package["path"])
    actual = sha256(path)
    if actual != str(package["sha256"]):
        raise ValueError(
            f"package policy hash mismatch: expected={package['sha256']} actual={actual}"
        )
    policy = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("package commit policy must be a mapping")
    if str(policy.get("schema_version")) != str(package["expected_schema_version"]):
        raise ValueError(
            "package commit policy schema mismatch: "
            f"expected={package['expected_schema_version']} actual={policy.get('schema_version')}"
        )
    composed = copy.deepcopy(policy)
    subject_override = config["commit_subject"]
    assert isinstance(subject_override, dict)
    composed["subject_pattern_effective_at"] = str(
        subject_override["effective_at_override"]
    )
    signature = composed.get("ai_signature")
    if not isinstance(signature, dict):
        raise ValueError("package commit policy ai_signature must be a mapping")
    override = config["ai_signature"]
    assert isinstance(override, dict)
    signature["effective_at"] = str(override["effective_at_override"])
    return composed


def filter_exact_waivers(
    errors: list[str],
    config: dict[str, object],
) -> list[str]:
    waived: set[str] = set()
    exceptions = config["assessment_historical_exceptions"]
    assert isinstance(exceptions, list)
    for exception in exceptions:
        assert isinstance(exception, dict)
        waived.add(
            f"{exception['commit']}: subject assessment ID lacks matching "
            f"Assessment-Id trailer: {exception['assessment_id']}"
        )
    return [error for error in errors if error not in waived]


def validate_target_message(
    sha: str,
    message: str,
    config: dict[str, object],
    *,
    workflow_id: str | None = None,
    committed_at: datetime | None = None,
) -> list[str]:
    config_errors = validate_target_config(config)
    if config_errors:
        return config_errors
    validator = load_package_validator(config)
    errors: list[str] = []
    validator.validate_message(
        sha,
        message,
        package_policy(config),
        errors,
        workflow_id,
        committed_at=committed_at,
    )
    return filter_exact_waivers(errors, config)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--range", dest="commit_range")
    selector.add_argument("--commit")
    parser.add_argument("--workflow-id")
    args = parser.parse_args()

    try:
        config = load_target_config()
        config_errors = validate_target_config(config)
        if config_errors:
            raise ValueError("; ".join(config_errors))
        validator = load_package_validator(config)
        policy = package_policy(config)
        shas = validator.selected_commits(
            args.commit_range,
            args.commit,
            root=ROOT,
            first_parent=bool(args.workflow_id and args.commit_range),
        )
        if not shas:
            raise ValueError("selected range contains no commits")
        errors = validator.validate_commits(shas, policy, args.workflow_id, root=ROOT)
        errors = filter_exact_waivers(errors, config)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Target Git commit validation failed: {exc}")
        return 1

    if errors:
        print("Target Git commit validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Target Git commit validation passed for {len(shas)} commit(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
