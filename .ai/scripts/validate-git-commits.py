#!/usr/bin/env python3
"""Validate selected Git commit messages against repository policy."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-git-commits.py")

import yaml


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".dev/standards/GIT-COMMIT-POLICY.yaml"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DEFAULT_SUBJECT_GRAMMAR_POLICY_ID = "git-commit-subject/v2"


def git(*args: str, root: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def selected_commits(
    commit_range: str | None,
    commit: str | None,
    root: Path = ROOT,
    *,
    first_parent: bool = False,
) -> list[str]:
    if commit_range:
        arguments = ["rev-list"]
        if first_parent:
            arguments.append("--first-parent")
        arguments.extend(["--reverse", commit_range])
        return [line for line in git(*arguments, root=root).splitlines() if line]
    return [git("rev-parse", commit or "HEAD", root=root).strip()]


def section_positions(message: str, required: list[str]) -> dict[str, int]:
    positions: dict[str, int] = {}
    for index, line in enumerate(message.splitlines()):
        normalized = line.strip().removesuffix(":")
        if normalized in required and normalized not in positions:
            positions[normalized] = index
    return positions


def safe_repo_reference(value: object) -> bool:
    """Accept a repository-relative path, optionally followed by a fragment."""
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    raw_path = value.split("#", 1)[0]
    parts = raw_path.split("/")
    path = PurePosixPath(raw_path)
    return (
        bool(raw_path)
        and ":" not in raw_path
        and all(parts)
        and not path.is_absolute()
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def policy_sha256(path: Path = POLICY_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subject_grammar_adoption_from_provenance(provenance: object) -> dict[str, object] | None:
    """Return the optional target adoption record without silently repairing it."""
    if not isinstance(provenance, dict):
        raise ValueError("target provenance must be a mapping")
    adoptions = provenance.get("policy_adoptions")
    if adoptions is None:
        return None
    if not isinstance(adoptions, dict):
        raise ValueError("target provenance policy_adoptions must be a mapping")
    adoption = adoptions.get("commit_subject_grammar")
    if adoption is None:
        return None
    if not isinstance(adoption, dict):
        raise ValueError(
            "target provenance policy_adoptions.commit_subject_grammar must be a mapping"
        )
    return adoption


def git_returncode(*args: str, root: Path) -> int:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise ValueError(f"cannot inspect target Git history: {exc}") from exc
    return result.returncode


def validate_subject_grammar_adoption(
    adoption: object,
    policy: dict[str, object],
    *,
    root: Path,
    incoming_policy_sha256: str,
) -> dict[str, str]:
    """Validate target-owned prospective grammar evidence before using it.

    The history tip is an immutable boundary only when it still resolves and is
    reachable from the target HEAD.  `adopted_at` is audit evidence; it never
    selects a commit grammar.
    """
    if not isinstance(adoption, dict):
        raise ValueError("commit subject grammar adoption must be a mapping")
    required = {
        "policy_id",
        "legacy_history_tip",
        "adopted_at",
        "incoming_policy_sha256",
        "decision_evidence",
    }
    if set(adoption) != required:
        raise ValueError("commit subject grammar adoption fields are invalid")
    expected_policy_id = str(
        policy.get("subject_grammar_policy_id", DEFAULT_SUBJECT_GRAMMAR_POLICY_ID)
    )
    if adoption.get("policy_id") != expected_policy_id:
        raise ValueError("commit subject grammar adoption policy_id differs")
    tip = adoption.get("legacy_history_tip")
    if not isinstance(tip, str) or not SHA_RE.fullmatch(tip):
        raise ValueError("commit subject grammar adoption legacy_history_tip is invalid")
    adopted_at = adoption.get("adopted_at")
    if not isinstance(adopted_at, str):
        raise ValueError("commit subject grammar adoption adopted_at is invalid")
    try:
        if datetime.fromisoformat(adopted_at).tzinfo is None:
            raise ValueError
    except ValueError as exc:
        raise ValueError(
            "commit subject grammar adoption adopted_at must use ISO 8601 with an offset"
        ) from exc
    declared_policy_sha = adoption.get("incoming_policy_sha256")
    if (
        not isinstance(declared_policy_sha, str)
        or not SHA256_RE.fullmatch(declared_policy_sha)
        or declared_policy_sha != incoming_policy_sha256
    ):
        raise ValueError("commit subject grammar adoption incoming policy SHA-256 differs")
    if not safe_repo_reference(adoption.get("decision_evidence")):
        raise ValueError("commit subject grammar adoption decision_evidence is invalid")
    if git_returncode("rev-parse", "--verify", f"{tip}^{{commit}}", root=root) != 0:
        raise ValueError("commit subject grammar adoption legacy_history_tip does not resolve")
    if git_returncode("rev-parse", "--verify", "HEAD^{commit}", root=root) != 0:
        raise ValueError("cannot inspect target HEAD for commit subject grammar adoption")
    if git_returncode("merge-base", "--is-ancestor", tip, "HEAD", root=root) != 0:
        raise ValueError(
            "commit subject grammar adoption legacy_history_tip is not reachable from target HEAD"
        )
    return {
        "policy_id": expected_policy_id,
        "legacy_history_tip": tip,
        "adopted_at": adopted_at,
        "incoming_policy_sha256": declared_policy_sha,
        "decision_evidence": str(adoption["decision_evidence"]),
    }


def commit_is_reachable_from_legacy_tip(
    sha: str, adoption: dict[str, str], *, root: Path
) -> bool:
    result = git_returncode(
        "merge-base",
        "--is-ancestor",
        sha,
        adoption["legacy_history_tip"],
        root=root,
    )
    if result == 0:
        return True
    if result == 1:
        return False
    raise ValueError(
        "cannot inspect commit reachability for commit subject grammar adoption"
    )


def subject_pattern_for_commit(
    policy: dict[str, object],
    committed_at: datetime | None,
    use_legacy_subject_grammar: bool | None = None,
) -> str:
    """Select an explicit target boundary or the source-history timestamp rule."""
    if use_legacy_subject_grammar is not None:
        return str(
            policy["legacy_subject_pattern"]
            if use_legacy_subject_grammar
            else policy["subject_pattern"]
        )
    effective_at = datetime.fromisoformat(str(policy["subject_pattern_effective_at"]))
    if committed_at is not None and committed_at < effective_at:
        return str(policy["legacy_subject_pattern"])
    return str(policy["subject_pattern"])


def validate_message(
    sha: str,
    message: str,
    policy: dict[str, object],
    errors: list[str],
    workflow_id: str | None = None,
    committed_at: datetime | None = None,
    use_legacy_subject_grammar: bool | None = None,
) -> None:
    lines = message.rstrip().splitlines()
    subject = lines[0] if lines else ""
    if not re.fullmatch(
        subject_pattern_for_commit(
            policy, committed_at, use_legacy_subject_grammar
        ),
        subject,
    ):
        errors.append(f"{sha}: subject does not match policy: {subject}")

    signature = policy["ai_signature"]
    assert isinstance(signature, dict)
    trailer_name = str(signature["trailer"])
    effective_at = datetime.fromisoformat(str(signature["effective_at"]))
    use_legacy_pattern = committed_at is not None and committed_at < effective_at
    pattern_key = "legacy_value_pattern" if use_legacy_pattern else "value_pattern"
    trailer_pattern = re.compile(str(signature[pattern_key]))
    final_line = lines[-1] if lines else ""
    prefix = f"{trailer_name}: "
    if not final_line.startswith(prefix) or not trailer_pattern.fullmatch(final_line[len(prefix):]):
        errors.append(f"{sha}: final non-empty line must be a valid {trailer_name} trailer")

    trailer_values = [
        line[len(prefix):]
        for line in lines
        if line.startswith(prefix)
    ]
    trailer_matches: list[re.Match[str] | None] = []
    for value in trailer_values:
        match = trailer_pattern.fullmatch(value)
        trailer_matches.append(match)
        if not match:
            errors.append(f"{sha}: invalid {trailer_name} trailer value: {value}")

    if not use_legacy_pattern:
        subagent_suffix = str(signature["additional_trailer_runtime_suffix"])
        for index, match in enumerate(trailer_matches):
            if index == 0 or match is None:
                continue
            runtime = match.groupdict().get("runtime", "")
            if not runtime.endswith(subagent_suffix):
                errors.append(
                    f"{sha}: additional {trailer_name} trailer must mark the runtime with{subagent_suffix}"
                )

    assessment = policy["assessment"]
    assert isinstance(assessment, dict)
    assessment_ids = re.findall(str(assessment["subject_id_pattern"]), subject)
    if assessment_ids:
        assessment_trailers = [
            line.split(":", 1)[1].strip()
            for line in lines
            if line.startswith(f"{assessment['trailer']}:")
        ]
        for assessment_id in assessment_ids:
            if assessment_id not in assessment_trailers:
                errors.append(f"{sha}: subject assessment ID lacks matching Assessment-Id trailer: {assessment_id}")

    # A standalone assessment keeps its assessment commit contract even when a
    # later workflow merges the assessment branch and validates the combined
    # range. Only workflow-stage commits require workflow body sections.
    if workflow_id and not assessment_ids:
        workflow = policy["workflow"]
        assert isinstance(workflow, dict)
        required = [str(value) for value in workflow["required_sections"]]
        positions = section_positions(message, required)
        missing = [section for section in required if section not in positions]
        if missing:
            errors.append(f"{sha}: missing workflow body sections: {', '.join(missing)}")
        elif [positions[section] for section in required] != sorted(positions.values()):
            errors.append(f"{sha}: workflow body sections are out of order")
        workflow_start = positions.get("Workflow")
        workflow_text = "\n".join(lines[workflow_start + 1 :]) if workflow_start is not None else ""
        if workflow_id not in workflow_text:
            errors.append(f"{sha}: Workflow section does not identify {workflow_id}")


def validate_commits(
    shas: list[str],
    policy: dict[str, object],
    workflow_id: str | None = None,
    root: Path = ROOT,
    adoption_evidence: object | None = None,
    incoming_policy_sha256: str | None = None,
) -> list[str]:
    errors: list[str] = []
    adoption: dict[str, str] | None = None
    if adoption_evidence is not None:
        if incoming_policy_sha256 is None:
            return [
                "commit subject grammar adoption is invalid: "
                "incoming policy SHA-256 is required"
            ]
        try:
            adoption = validate_subject_grammar_adoption(
                adoption_evidence,
                policy,
                root=root,
                incoming_policy_sha256=incoming_policy_sha256,
            )
        except ValueError as exc:
            return [f"commit subject grammar adoption is invalid: {exc}"]
    for sha in shas:
        message = git("show", "-s", "--format=%B", sha, root=root)
        committed_at = datetime.fromisoformat(
            git("show", "-s", "--format=%cI", sha, root=root).strip()
        )
        try:
            legacy_subject_grammar = (
                commit_is_reachable_from_legacy_tip(sha, adoption, root=root)
                if adoption is not None
                else None
            )
        except ValueError as exc:
            errors.append(f"{sha}: commit subject grammar adoption is invalid: {exc}")
            continue
        validate_message(
            sha,
            message,
            policy,
            errors,
            workflow_id,
            committed_at=committed_at,
            use_legacy_subject_grammar=legacy_subject_grammar,
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--range", dest="commit_range", help="Git revision range, for example main..HEAD")
    selector.add_argument("--commit", help="Single commit-ish; defaults to HEAD")
    selector.add_argument(
        "--message-file",
        type=Path,
        help="Validate a planned UTF-8 commit message before git commit",
    )
    parser.add_argument("--workflow-id", help="Require workflow sections and this workflow identity")
    adoption_source = parser.add_mutually_exclusive_group()
    adoption_source.add_argument(
        "--target-provenance",
        type=Path,
        help="Read policy_adoptions.commit_subject_grammar from this target provenance YAML",
    )
    adoption_source.add_argument(
        "--adoption-evidence",
        type=Path,
        help="Read a standalone commit-subject-grammar adoption YAML mapping",
    )
    args = parser.parse_args()

    policy_bytes = POLICY_PATH.read_bytes()
    policy = yaml.safe_load(policy_bytes.decode("utf-8"))
    if not isinstance(policy, dict):
        print(f"Git commit validation failed: {POLICY_PATH} must be a mapping")
        return 1
    adoption_evidence: object | None = None
    try:
        if args.target_provenance is not None:
            adoption_evidence = subject_grammar_adoption_from_provenance(
                yaml.safe_load(args.target_provenance.read_text(encoding="utf-8"))
            )
        elif args.adoption_evidence is not None:
            adoption_evidence = yaml.safe_load(
                args.adoption_evidence.read_text(encoding="utf-8")
            )
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        print(f"Git commit validation failed: cannot load adoption evidence: {exc}")
        return 1
    if args.message_file is not None:
        if adoption_evidence is not None:
            print(
                "Git commit validation failed: planned messages cannot select "
                "target-history adoption evidence"
            )
            return 1
        try:
            message = args.message_file.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Git commit validation failed: cannot read planned message: {exc}")
            return 1
        errors: list[str] = []
        validate_message(
            "planned-message",
            message,
            policy,
            errors,
            args.workflow_id,
            committed_at=datetime.now().astimezone(),
            use_legacy_subject_grammar=False,
        )
        if errors:
            print("Git commit validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Git commit validation passed for planned message.")
        return 0
    shas = selected_commits(
        args.commit_range,
        args.commit,
        first_parent=bool(args.workflow_id and args.commit_range),
    )
    if not shas:
        print("Git commit validation failed: selected range contains no commits")
        return 1
    errors = validate_commits(
        shas,
        policy,
        args.workflow_id,
        adoption_evidence=adoption_evidence,
        incoming_policy_sha256=hashlib.sha256(policy_bytes).hexdigest(),
    )
    if errors:
        print("Git commit validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Git commit validation passed for {len(shas)} commit(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
