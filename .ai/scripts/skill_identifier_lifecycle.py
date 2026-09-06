"""Portable, explicit runtime versus historical skill identifier resolution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

import yaml

RETIREMENT = Path(".ai/assets/skills/transitions/v0.16.0.yaml")
REPLACEMENTS = {
    "repo-structure-sync": "ai-context-init",
    "dev-workflow": "software-development-orchestrator",
}


def load_retirement(root: Path) -> dict:
    """Reject unknown or incomplete lifecycle authority before routing."""
    data = yaml.safe_load((root / RETIREMENT).read_text(encoding="utf-8"))
    expected = {
        "schema_version": "1.0",
        "transition_id": "SKILL-004-v0.16.0",
        "release_target": "v0.16.0",
        "state": "retired",
        "owner_skill": "ai-context-governance",
        "historical_activation": ".ai/assets/skills/transitions/v0.6.0.yaml",
        "historical_identifier_rewrite": False,
        "new_request_policy": "reject-with-replacement",
        "historical_reference_policy": "preserve-as-evidence",
    }
    if not isinstance(data, dict) or any(
        type(data.get(key)) is not type(value) or data.get(key) != value
        for key, value in expected.items()
    ):
        raise ValueError("invalid skill retirement lifecycle authority")
    entries = data.get("transitions")
    if not isinstance(entries, list) or len(entries) != len(REPLACEMENTS):
        raise ValueError("invalid skill retirement transition set")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("invalid skill retirement entry")
        identifier = entry.get("identifier")
        if not isinstance(identifier, str) or identifier in seen or identifier not in REPLACEMENTS:
            raise ValueError("unknown or duplicate retired identifier")
        seen.add(identifier)
        if entry != dict(identifier=identifier, replacement=REPLACEMENTS[identifier],
                         removal_target="v0.16.0", lifecycle="retired"):
            raise ValueError(f"invalid retirement or replacement for {identifier}")
    if data.get("upgrade_policy") != {
        "unchanged_framework_owned": "remove-with-previous-manifest-hash",
        "modified_framework_owned": "reconcile-with-owner",
        "target_owned": "preserve-and-reconcile-with-owner",
        "missing_previous_manifest": "blocked",
    }:
        raise ValueError("invalid skill retirement upgrade policy")
    return data


def resolve_identifier(root: Path, identifier: str, context: str = "runtime") -> dict:
    if context not in {"runtime", "historical"}:
        raise ValueError("context must be runtime or historical")
    # Never use caller input as an unchecked filesystem path.
    if not identifier or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in identifier):
        raise ValueError("identifier must be a lowercase skill identifier")
    load_retirement(root)
    if identifier in REPLACEMENTS:
        replacement = REPLACEMENTS[identifier]
        historical = context == "historical"
        return {
            "identifier": identifier,
            "context": context,
            "status": "historical-evidence" if historical else "retired",
            "accepted": historical,
            "replacement": replacement,
            "removal_release": "v0.16.0",
            "message": (
                f"Preserve historical identifier '{identifier}' unchanged; it is evidence, not an active skill."
                if historical else
                f"Skill '{identifier}' was retired in v0.16.0. Use '{replacement}' for a new request."
            ),
        }
    spec = root / ".ai/assets/skills" / identifier / "skill.yaml"
    data = yaml.safe_load(spec.read_text(encoding="utf-8")) if spec.is_file() else None
    active = isinstance(data, dict) and data.get("asset_id") == identifier and data.get("status") == "active"
    return {"identifier": identifier, "context": context, "status": "active" if active else "unknown",
            "accepted": active, "message": f"Skill '{identifier}' is {'active' if active else 'unknown'}."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identifier")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--context", choices=("runtime", "historical"), default="runtime")
    args = parser.parse_args(argv)
    try:
        result = resolve_identifier(args.root.resolve(), args.identifier, args.context)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "invalid", "accepted": False, "message": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
