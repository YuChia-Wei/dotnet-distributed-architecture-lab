"""Explicit version-aware public package identity resolution."""

from __future__ import annotations

import re
from typing import Any


POLICY_SCHEMA_VERSION = "1.0"
POLICY_ID = "public-package-identity-v1"
LEGACY_RULE_ID = "through-v0.14"
CURRENT_RULE_ID = "from-v0.15"
LEGACY_IDENTITY_ID = "package.ai-context-dotnet-backend-legacy"
CURRENT_IDENTITY_ID = "package.ai-collaboration-framework"
LEGACY_TEMPLATE = "ai-context-dotnet-backend-v{version}"
CURRENT_TEMPLATE = "ai-collaboration-framework-v{version}"
CURRENT_MINIMUM = "v0.15.0"
VERSION_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class PackageIdentityError(ValueError):
    """Raised when public package identity cannot be resolved unambiguously."""


def normalize_version(value: object) -> str:
    if not isinstance(value, str):
        raise PackageIdentityError("package identity version must be a string")
    match = VERSION_RE.fullmatch(value)
    if match is None:
        raise PackageIdentityError("package identity version must be vMAJOR.MINOR.PATCH")
    return ".".join(match.groups())


def version_key(value: object) -> tuple[int, int, int]:
    return tuple(int(part) for part in normalize_version(value).split("."))


def expected_rule(value: object) -> dict[str, str | None]:
    version = normalize_version(value)
    if version_key(version) < version_key(CURRENT_MINIMUM):
        return {
            "rule_id": LEGACY_RULE_ID,
            "identity_id": LEGACY_IDENTITY_ID,
            "status": "legacy-published-compatible",
            "minimum_version": None,
            "maximum_version_exclusive": CURRENT_MINIMUM,
            "name_template": LEGACY_TEMPLATE,
            "package_id": LEGACY_TEMPLATE.format(version=version),
        }
    return {
        "rule_id": CURRENT_RULE_ID,
        "identity_id": CURRENT_IDENTITY_ID,
        "status": "current-public-canonical",
        "minimum_version": CURRENT_MINIMUM,
        "maximum_version_exclusive": None,
        "name_template": CURRENT_TEMPLATE,
        "package_id": CURRENT_TEMPLATE.format(version=version),
    }


def expected_package_id(value: object) -> str:
    return str(expected_rule(value)["package_id"])


def expected_artifacts(value: object) -> dict[str, str]:
    package_id = expected_package_id(value)
    return {
        "zip": f"{package_id}.zip",
        "zip_checksum": f"{package_id}.zip.sha256",
        "tar_gz": f"{package_id}.tar.gz",
        "tar_gz_checksum": f"{package_id}.tar.gz.sha256",
    }


def _exact_mapping(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PackageIdentityError(f"{label} must be a mapping")
    missing = sorted(keys - set(value))
    extra = sorted(set(value) - keys)
    if missing or extra:
        raise PackageIdentityError(
            f"{label} fields differ: missing={missing!r}; extra={extra!r}"
        )
    return value


def validate_registry_policy(
    registry: dict[str, Any], records: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Require the tracked registry to encode the owner-selected boundary exactly."""
    policy = _exact_mapping(
        registry.get("package_identity_policy"),
        {
            "schema_version",
            "policy_id",
            "issue",
            "resolution",
            "ambiguity",
            "filename_inference",
            "public_canonical_identity_id",
            "rules",
        },
        "registry.package_identity_policy",
    )
    expected_header = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "policy_id": POLICY_ID,
        "issue": 250,
        "resolution": "explicit-version-range",
        "ambiguity": "fail-closed",
        "filename_inference": "forbidden",
        "public_canonical_identity_id": CURRENT_IDENTITY_ID,
    }
    for key, expected in expected_header.items():
        if policy.get(key) != expected:
            raise PackageIdentityError(
                f"registry.package_identity_policy.{key} must be {expected!r}"
            )
    raw_rules = policy["rules"]
    if not isinstance(raw_rules, list) or len(raw_rules) != 2:
        raise PackageIdentityError(
            "registry.package_identity_policy.rules must contain exactly two explicit ranges"
        )
    rule_keys = {
        "rule_id",
        "identity_id",
        "status",
        "minimum_version",
        "maximum_version_exclusive",
    }
    expected_rules = [expected_rule("v0.14.0"), expected_rule(CURRENT_MINIMUM)]
    for index, (raw, expected) in enumerate(zip(raw_rules, expected_rules, strict=True)):
        rule = _exact_mapping(raw, rule_keys, f"package identity rule[{index}]")
        for key in rule_keys:
            if rule.get(key) != expected[key]:
                raise PackageIdentityError(
                    f"package identity rule[{index}].{key} must be {expected[key]!r}"
                )
        record = records.get(str(rule["identity_id"]))
        if record is None or record.get("kind") != "archive-package":
            raise PackageIdentityError(
                f"package identity rule[{index}] references an unknown archive identity"
            )
        expected_record_status = "active" if index == 1 else "legacy-compatible"
        if record.get("status") != expected_record_status:
            raise PackageIdentityError(
                f"package identity {record.get('id')} must be {expected_record_status}"
            )
        if record.get("canonical_value") != expected["name_template"]:
            raise PackageIdentityError(
                f"package identity {record.get('id')} canonical template drifted"
            )
        forms = record.get("forms")
        expected_forms = {
            "package_id_template": expected["name_template"],
            "zip_template": f"{expected['name_template']}.zip",
            "zip_checksum_template": f"{expected['name_template']}.zip.sha256",
            "tar_gz_template": f"{expected['name_template']}.tar.gz",
            "tar_gz_checksum_template": f"{expected['name_template']}.tar.gz.sha256",
        }
        if forms != expected_forms:
            raise PackageIdentityError(
                f"package identity {record.get('id')} forms do not derive from one base"
            )
    active_archives = [
        record
        for record in records.values()
        if record.get("kind") == "archive-package" and record.get("status") == "active"
    ]
    if [record.get("id") for record in active_archives] != [CURRENT_IDENTITY_ID]:
        raise PackageIdentityError(
            "exactly one current public archive identity must remain active"
        )
    return policy


def resolve_registry_identity(
    registry: dict[str, Any], value: object
) -> dict[str, str | None]:
    records = {
        record.get("id"): record
        for record in registry.get("identity_records", [])
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    policy = validate_registry_policy(registry, records)
    resolved = expected_rule(value)
    if not any(
        isinstance(rule, dict)
        and rule.get("rule_id") == resolved["rule_id"]
        and rule.get("identity_id") == resolved["identity_id"]
        for rule in policy["rules"]
    ):
        raise PackageIdentityError("package identity range is absent or ambiguous")
    return {**resolved, "policy_id": POLICY_ID}
