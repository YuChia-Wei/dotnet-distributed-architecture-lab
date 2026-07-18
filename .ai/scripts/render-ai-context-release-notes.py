#!/usr/bin/env python3
"""Validate a governed release candidate and render its GitHub Release body."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_CANDIDATE_STATUSES = {"planned", "validated"}


class ReleaseNotesError(ValueError):
    """Raised when release metadata cannot safely produce a release body."""


def load_mapping(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ReleaseNotesError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseNotesError(f"{path} must contain a YAML mapping")
    return value


def normalize_version(value: str) -> str:
    version = value.strip()
    if not VERSION_RE.fullmatch(version):
        raise ReleaseNotesError("version must use stable vMAJOR.MINOR.PATCH form")
    return version


def discover_candidate(root: Path) -> str:
    candidates: list[str] = []
    releases = root / ".dev" / "releases"
    for path in sorted(releases.glob("v*/release.yaml")):
        data = load_mapping(path)
        version = data.get("version")
        if (
            isinstance(version, str)
            and VERSION_RE.fullmatch(version)
            and data.get("record_origin") == "governed"
            and data.get("status") in ALLOWED_CANDIDATE_STATUSES
        ):
            candidates.append(version)
    if len(candidates) != 1:
        joined = ", ".join(candidates) if candidates else "none"
        raise ReleaseNotesError(
            "candidate discovery requires exactly one governed planned or "
            f"validated release; found {joined}"
        )
    return candidates[0]


def resolve_artifact(path: Path, release_dir: Path, label: str) -> Path:
    if not isinstance(path, str) or not path.strip():
        raise ReleaseNotesError(f"artifacts.{label} must be a repository file name")
    candidate = (release_dir / path).resolve()
    resolved_dir = release_dir.resolve()
    if candidate.parent != resolved_dir or not candidate.is_file():
        raise ReleaseNotesError(
            f"artifacts.{label} must resolve to an existing file in {release_dir}"
        )
    return candidate


def validate_release(root: Path, version: str, commit: str, mode: str) -> tuple[dict, Path, Path]:
    if not SHA_RE.fullmatch(commit):
        raise ReleaseNotesError("commit must be a full lowercase 40-character Git SHA")
    release_dir = root / ".dev" / "releases" / version
    record_path = release_dir / "release.yaml"
    data = load_mapping(record_path)
    expected_id = f"REL-{version}"
    if data.get("version") != version or data.get("release_id") != expected_id:
        raise ReleaseNotesError(f"{record_path} identity does not match {expected_id}")
    if data.get("record_origin") != "governed":
        raise ReleaseNotesError("automatic publication accepts governed releases only")
    status = data.get("status")
    allowed = {"validated"} if mode == "publish" else ALLOWED_CANDIDATE_STATUSES
    if status not in allowed:
        raise ReleaseNotesError(
            f"release status {status!r} is not allowed in {mode} mode; expected {sorted(allowed)}"
        )
    if mode == "publish" and (data.get("tag") is not None or data.get("commit") is not None):
        raise ReleaseNotesError(
            "the validated tagged-tree record must leave tag and commit unset until publication"
        )
    compatibility = data.get("compatibility")
    if not isinstance(compatibility, dict) or not isinstance(
        compatibility.get("breaking_changes"), bool
    ):
        raise ReleaseNotesError("compatibility.breaking_changes must be boolean")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ReleaseNotesError("artifacts must be a mapping")
    notes = resolve_artifact(artifacts.get("release_notes"), release_dir, "release_notes")
    migration = resolve_artifact(
        artifacts.get("migration_guide"), release_dir, "migration_guide"
    )
    return data, notes, migration


def render_body(data: dict, notes: Path, migration: Path, commit: str) -> str:
    version = data["version"]
    release_id = data["release_id"]
    package_id = f"ai-context-dotnet-backend-{version}"
    notes_text = notes.read_text(encoding="utf-8").strip()
    migration_text = migration.read_text(encoding="utf-8").strip()
    return "\n".join(
        [
            f"<!-- ai-context-release-automation: {release_id} -->",
            "",
            notes_text,
            "",
            "## Release provenance",
            "",
            f"- Release ID: `{release_id}`",
            f"- Tag: `{version}`",
            f"- Commit: `{commit}`",
            "- Distribution profile: `dotnet-backend`",
            f"- Package: `{package_id}`",
            "- Archive integrity: verify each archive against its adjacent `.sha256` asset.",
            "",
            "## Migration guide",
            "",
            migration_text,
            "",
        ]
    )


def append_github_outputs(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise ReleaseNotesError(f"GitHub output {key} must be single-line")
            stream.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--version")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--mode", choices=("candidate", "publish"), default="candidate")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    try:
        root = args.root.resolve()
        version = normalize_version(args.version) if args.version else discover_candidate(root)
        commit = args.commit.strip()
        data, notes, migration = validate_release(root, version, commit, args.mode)
        body = render_body(data, notes, migration, commit)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8", newline="\n")
        outputs = {
            "version": version,
            "package_version": version.removeprefix("v"),
            "release_id": data["release_id"],
            "title": data["release_id"],
            "commit": commit,
            "package_id": f"ai-context-dotnet-backend-{version}",
        }
        if args.github_output:
            append_github_outputs(args.github_output, outputs)
    except (OSError, ReleaseNotesError) as exc:
        print(f"Release-note rendering failed: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered {data['release_id']} release body to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
