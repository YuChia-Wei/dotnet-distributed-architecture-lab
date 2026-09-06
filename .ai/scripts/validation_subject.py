#!/usr/bin/env python3
"""Canonical subject-manifest and final-head rebind implementation."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping

import importlib.metadata
import yaml


CLASSIFICATION_REF = ".ai/assets/shared/validation-gate-classification.yaml"
CONTRACT_REF = ".ai/assets/shared/VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md"
SCHEMA_REF = ".ai/assets/shared/validation-evidence-lifecycle.schema.yaml"
RUNNER_REF = ".ai/scripts/check-all.sh"
REGISTRY_REF = ".ai/scripts/validation-profile-registry.sh"
EVIDENCE_REF = ".ai/scripts/validation-evidence.py"
LIFECYCLE_VALIDATOR_REF = ".ai/scripts/validate-validation-lifecycle.py"
SUBJECT_IMPLEMENTATION_REF = ".ai/scripts/validation_subject.py"
MANIFEST_SCHEMA = "subject-manifest/v1"
IDENTITY_SCHEMA = "subject-identity/v1"
CLOSURE_SCHEMA = "validation-tracked-closure/v1"
RUNTIME_RECEIPT_SCHEMA = "validation-runtime-receipt/v1"
REBIND_SCHEMA = "subject-evidence-rebind/v1"
CLASSIFICATION_SCHEMA = "validation-gate-classification/v1"
REPOSITORY_IDENTITY = "runtime-worktree-digest/v1"
SENSITIVITIES = ["identity", "input", "environment", "provider"]
ELIGIBILITY = ["pilot-approved", "candidate-disabled", "not-reusable"]
REUSABLE_PROFILES = {"fast", "pr"}
REQUIRED_FRESH_GATES = [
    "actual-upgrade-evidence",
    "current-head-review-binding",
    "hosted-required-contexts",
    "live-merge-admission",
    "mutable-provider-state",
    "tag-release-binding",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9._+-]{0,127}$")
CONTRACT_RE = re.compile(r"^[a-z0-9][a-z0-9._+/-]{0,127}$")
FORBIDDEN_KEYS = {"private_path", "username", "hostname", "secret", "token", "machine_id"}


class SubjectError(ValueError):
    """Fail-closed subject identity or rebind violation."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SubjectError(f"{label} must be a mapping")
    return value


def _exact_keys(value: Mapping[str, object], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise SubjectError(f"{label} fields are invalid")


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise SubjectError(f"{label} must be a SHA-256 digest")
    return value


def _token(value: object, label: str) -> str:
    if not isinstance(value, str) or not TOKEN_RE.fullmatch(value):
        raise SubjectError(f"{label} is invalid")
    return value


def _reject_private(value: object, label: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise SubjectError(f"{label} contains forbidden private field: {key}")
            _reject_private(child, label)
    elif isinstance(value, list):
        for child in value:
            _reject_private(child, label)


def _run(repo: Path, argv: list[str], label: str) -> bytes:
    result = subprocess.run(
        argv,
        cwd=repo,
        check=False,
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise SubjectError(f"{label} failed")
    return result.stdout


def _git(repo: Path, *arguments: str, label: str = "Git command") -> bytes:
    return _run(repo, ["git", "-C", str(repo), *arguments], label)


def repository_root(value: Path) -> Path:
    try:
        root = Path(
            _git(value.resolve(), "rev-parse", "--show-toplevel", label="repository root")
            .decode("utf-8", errors="strict")
            .strip()
        ).resolve(strict=True)
    except (OSError, UnicodeDecodeError) as exc:
        raise SubjectError("repository root is unavailable") from exc
    if not root.is_dir():
        raise SubjectError("repository root is invalid")
    return root


def runtime_repository_identity(repo: Path) -> str:
    normalized = os.path.normcase(str(repo.resolve()))
    return f"{REPOSITORY_IDENTITY}:{sha256_bytes(os.fsencode(normalized))}"


def _safe_ref(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SubjectError(f"{label} must be a repository-relative reference")
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
        raise SubjectError(f"{label} must be a repository-relative reference")
    parts = PurePosixPath(value).parts
    if ".." in parts or "." in parts or any(not part for part in parts):
        raise SubjectError(f"{label} must be normalized")
    return value


def _repo_path(repo: Path, value: Path | str, label: str, *, must_exist: bool = True) -> tuple[str, Path]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = repo / candidate
    try:
        resolved = candidate.resolve(strict=must_exist)
        ref = resolved.relative_to(repo).as_posix()
    except (OSError, ValueError) as exc:
        raise SubjectError(f"{label} is unavailable or outside the repository") from exc
    _safe_ref(ref, label)
    if must_exist and (resolved.is_symlink() or not resolved.is_file()):
        raise SubjectError(f"{label} must be a regular non-symlink file")
    return ref, resolved


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SubjectError(f"{label} is unreadable") from exc
    result = _mapping(value, label)
    _reject_private(result, label)
    return result


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8", errors="strict"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise SubjectError(f"{label} is unreadable") from exc
    result = _mapping(value, label)
    _reject_private(result, label)
    return result


def _write_json_create_only(path: Path, value: object) -> None:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SubjectError("subject evidence output already exists") from exc
    except OSError as exc:
        raise SubjectError("subject evidence output cannot be published") from exc


def _resolve_bash() -> str:
    for candidate in (
        Path("C:/Program Files/Git/bin/bash.exe"),
        Path("C:/Program Files/Git/usr/bin/bash.exe"),
    ):
        if candidate.is_file():
            return str(candidate)
    discovered = shutil.which("bash")
    if discovered:
        return discovered
    raise SubjectError("canonical validation registry requires Bash")


def registry_snapshot(repo: Path) -> dict[str, dict[str, object]]:
    registry = repo / REGISTRY_REF
    script = r'''
set -e
declare -ag PROFILE_IDS=() CHECK_IDS=()
declare -A PROFILE_PURPOSE=() PROFILE_BUDGET=() PROFILE_ENFORCEMENT=()
declare -A CHECK_ID_BY_DESCRIPTION=() CHECK_DESCRIPTION=() CHECK_OWNER=()
declare -A CHECK_ENFORCEMENT=() CHECK_TAGS=() CHECK_PROFILES=() CHECK_INPUT_PATHS=()
declare -A CHECK_DEPENDS=() CHECK_ENVIRONMENT=() CHECK_TIMEOUT=() CHECK_RESOURCE_CLASS=()
declare -A CHECK_CACHE_POLICY=() CHECK_DISPOSITION=() CHECK_COMMAND=() CHECK_APPLICABILITY=()
register_profile() { PROFILE_IDS+=("$1"); PROFILE_PURPOSE["$1"]=$2; PROFILE_BUDGET["$1"]=$3; PROFILE_ENFORCEMENT["$1"]=$4; }
register_check() {
  CHECK_IDS+=("$1"); CHECK_ID_BY_DESCRIPTION["$2"]=$1; CHECK_DESCRIPTION["$1"]=$2; CHECK_OWNER["$1"]=ai-context-governance
  CHECK_ENFORCEMENT["$1"]=$3; CHECK_TAGS["$1"]=$4; CHECK_PROFILES["$1"]=$5; CHECK_INPUT_PATHS["$1"]=$6
  CHECK_DEPENDS["$1"]=$7; CHECK_ENVIRONMENT["$1"]=$8; CHECK_TIMEOUT["$1"]=$9; CHECK_RESOURCE_CLASS["$1"]=${10}
  CHECK_CACHE_POLICY["$1"]=${11}; CHECK_DISPOSITION["$1"]=${12}; CHECK_COMMAND["$1"]=${13}; CHECK_APPLICABILITY["$1"]=${14}
}
source "$1"
for id in "${CHECK_IDS[@]}"; do
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$id" "${CHECK_PROFILES[$id]}" "${CHECK_INPUT_PATHS[$id]}" "${CHECK_DEPENDS[$id]}" "${CHECK_ENVIRONMENT[$id]}" "${CHECK_CACHE_POLICY[$id]}" "${CHECK_DISPOSITION[$id]}" "${CHECK_COMMAND[$id]}"
done
'''
    result = subprocess.run(
        [_resolve_bash(), "-c", script, "validation-subject", str(registry)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if result.returncode != 0:
        raise SubjectError("canonical validation registry is unavailable")
    checks: dict[str, dict[str, object]] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) != 8:
            raise SubjectError("canonical validation registry output is malformed")
        gate_id, profiles, inputs, dependencies, environment, cache_policy, disposition, command = fields
        if gate_id in checks or not TOKEN_RE.fullmatch(gate_id):
            raise SubjectError("canonical validation registry contains an invalid gate")
        checks[gate_id] = {
            "profiles": profiles.split(),
            "input_paths": inputs.split(),
            "dependencies": dependencies.split(),
            "environment_capabilities": environment.split(),
            "cache_policy": cache_policy,
            "disposition": disposition,
            "command": command,
        }
    if not checks:
        raise SubjectError("canonical validation registry is empty")
    return checks


def load_classification_authority(repo: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    authority = _load_yaml(repo / CLASSIFICATION_REF, "gate classification authority")
    _exact_keys(
        authority,
        {
            "schema_version",
            "authority_id",
            "repository_identity",
            "sensitivities",
            "reuse_eligibility_values",
            "groups",
            "external_fresh_gates",
        },
        "gate classification authority",
    )
    if (
        authority["schema_version"] != CLASSIFICATION_SCHEMA
        or authority["repository_identity"] != REPOSITORY_IDENTITY
        or authority["sensitivities"] != SENSITIVITIES
        or authority["reuse_eligibility_values"] != ELIGIBILITY
    ):
        raise SubjectError("gate classification authority identity is invalid")
    checks = registry_snapshot(repo)
    classifications: dict[str, dict[str, Any]] = {}
    groups = authority["groups"]
    if not isinstance(groups, list) or not groups:
        raise SubjectError("gate classification groups are empty")
    for group_value in groups:
        group = _mapping(group_value, "gate classification group")
        _exact_keys(
            group,
            {
                "group_id",
                "sensitivities",
                "reuse_eligibility",
                "reusable_profiles",
                "environment_contract",
                "gate_ids",
                "reason",
            },
            "gate classification group",
        )
        group_id = _token(group["group_id"], "gate classification group id")
        sensitivities = group["sensitivities"]
        if (
            not isinstance(sensitivities, list)
            or not sensitivities
            or sensitivities != [item for item in SENSITIVITIES if item in sensitivities]
            or len(set(sensitivities)) != len(sensitivities)
        ):
            raise SubjectError("gate classification sensitivities are invalid")
        eligibility = group["reuse_eligibility"]
        if eligibility not in ELIGIBILITY:
            raise SubjectError("gate reuse eligibility is invalid")
        profiles = group["reusable_profiles"]
        if (
            not isinstance(profiles, list)
            or profiles != sorted(set(profiles))
            or not set(profiles).issubset(REUSABLE_PROFILES)
            or (eligibility == "pilot-approved") != bool(profiles)
        ):
            raise SubjectError("gate reusable profiles are invalid")
        environment_contract = group["environment_contract"]
        if environment_contract is not None:
            if not isinstance(environment_contract, str) or not CONTRACT_RE.fullmatch(environment_contract):
                raise SubjectError("gate environment contract is invalid")
        gate_ids = group["gate_ids"]
        if not isinstance(gate_ids, list) or not gate_ids or gate_ids != sorted(set(gate_ids)):
            raise SubjectError("gate classification ids must be sorted and unique")
        if not isinstance(group["reason"], str) or not group["reason"]:
            raise SubjectError("gate classification reason is missing")
        for gate_id_value in gate_ids:
            gate_id = _token(gate_id_value, "classified gate id")
            if gate_id in classifications:
                raise SubjectError("gate classification is duplicated")
            core = {
                "schema_version": "gate-sensitivity/v1",
                "gate_id": gate_id,
                "group_id": group_id,
                "sensitivities": sensitivities,
                "reuse_eligibility": eligibility,
                "reusable_profiles": profiles,
                "environment_contract": environment_contract,
            }
            classifications[gate_id] = {**core, "classification_digest": canonical_sha256(core)}
    if set(classifications) != set(checks):
        raise SubjectError("gate classification does not exactly cover the validation registry")
    external = authority["external_fresh_gates"]
    if not isinstance(external, list) or [item.get("gate_id") for item in external if isinstance(item, dict)] != REQUIRED_FRESH_GATES:
        raise SubjectError("external fresh gate classification is invalid")
    for item_value in external:
        item = _mapping(item_value, "external fresh gate")
        _exact_keys(item, {"gate_id", "sensitivities", "reason"}, "external fresh gate")
        sensitivities = item["sensitivities"]
        if (
            not isinstance(sensitivities, list)
            or not sensitivities
            or sensitivities != [value for value in SENSITIVITIES if value in sensitivities]
            or len(set(sensitivities)) != len(sensitivities)
        ):
            raise SubjectError("external fresh gate sensitivities are invalid")
        if not isinstance(item["reason"], str) or not item["reason"]:
            raise SubjectError("external fresh gate reason is missing")
    return classifications, authority


def classification_for_gate(repo: Path, gate_id: str) -> tuple[dict[str, Any], dict[str, object]]:
    checks = registry_snapshot(repo)
    classifications, _authority = load_classification_authority(repo)
    if gate_id not in checks or gate_id not in classifications:
        raise SubjectError("gate classification is unknown")
    classification = dict(classifications[gate_id])
    authority_bytes = (repo / CLASSIFICATION_REF).read_bytes()
    classification["authority"] = {
        "ref": CLASSIFICATION_REF,
        "sha256": sha256_bytes(authority_bytes),
        "bytes": len(authority_bytes),
    }
    return classification, checks[gate_id]


def _head_identity(repo: Path, *, require_clean: bool) -> dict[str, str]:
    values = _git(repo, "rev-parse", "HEAD", "HEAD^{tree}", label="subject identity").decode("ascii").splitlines()
    if len(values) != 2 or not all(GIT_OBJECT_RE.fullmatch(value) for value in values):
        raise SubjectError("subject identity is invalid")
    if require_clean:
        status = _git(
            repo,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            label="subject cleanliness",
        ).decode("utf-8", errors="replace")
        if status:
            raise SubjectError("subject manifest requires a clean tracked and untracked repository")
    return {"commit": values[0], "tree": values[1]}


def _git_file_record(repo: Path, subject: str, ref: str) -> dict[str, object]:
    output = _git(repo, "ls-tree", "-z", subject, "--", ref, label="subject authority identity")
    records = [item for item in output.split(b"\0") if item]
    if len(records) != 1:
        raise SubjectError("subject authority file is absent or ambiguous")
    try:
        metadata, path = records[0].split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split()
        observed_ref = path.decode("utf-8", errors="strict")
    except (ValueError, UnicodeDecodeError) as exc:
        raise SubjectError("subject authority identity is malformed") from exc
    if observed_ref != ref or object_type != "blob" or mode == "120000" or not GIT_OBJECT_RE.fullmatch(object_id):
        raise SubjectError("subject authority file is not a regular tracked blob")
    content = _git(repo, "show", f"{subject}:{ref}", label="subject authority bytes")
    return {
        "path": ref,
        "mode": mode,
        "object_type": object_type,
        "object_id": object_id,
        "sha256": sha256_bytes(content),
        "bytes": len(content),
    }


def _resolve_closure_paths(repo: Path, gate_id: str, subject: str) -> list[str]:
    result = subprocess.run(
        [_resolve_bash(), RUNNER_REF, "--resolve-input-closure", gate_id, "--subject", subject],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if result.returncode != 0:
        raise SubjectError("canonical tracked closure is unresolved")
    paths = [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]
    if not paths or paths != sorted(set(paths)):
        raise SubjectError("canonical tracked closure is incomplete or noncanonical")
    for path in paths:
        _safe_ref(path, "tracked closure path")
    return paths


def build_closure_receipt(repo: Path, gate_id: str, identity: Mapping[str, str]) -> dict[str, Any]:
    paths = _resolve_closure_paths(repo, gate_id, identity["commit"])
    entries = [_git_file_record(repo, identity["commit"], path) for path in paths]
    core = {
        "schema_version": CLOSURE_SCHEMA,
        "gate_id": gate_id,
        "subject": dict(identity),
        "resolver_argv": ["bash", RUNNER_REF, "--resolve-input-closure", gate_id, "--subject", identity["commit"]],
        "complete": True,
        "unknown_paths": [],
        "path_count": len(paths),
        "paths_sha256": canonical_sha256(paths),
        "entries_digest": canonical_sha256(entries),
        "entries": entries,
    }
    return {**core, "receipt_sha256": canonical_sha256(core)}


def runtime_identity() -> dict[str, object]:
    try:
        yaml_distribution = importlib.metadata.version("PyYAML")
        yaml_module_version = getattr(yaml, "__version__", None)
        implementation = platform.python_implementation()
        cache_tag = sys.implementation.cache_tag
        soabi = sysconfig.get_config_var("SOABI")
    except Exception as exc:
        raise SubjectError("validation runtime identity is unavailable") from exc
    if not all(isinstance(item, str) and item for item in (yaml_distribution, yaml_module_version, implementation, cache_tag, soabi)):
        raise SubjectError("validation runtime identity is incomplete")
    if yaml_distribution != yaml_module_version:
        raise SubjectError("validation runtime dependency identity is inconsistent")
    return {
        "schema_version": "validation-runtime-identity/v1",
        "python": {
            "implementation": implementation,
            "version": list(sys.version_info[:3]),
            "cache_tag": cache_tag,
            "abi_flags": getattr(sys, "abiflags", ""),
            "soabi": soabi,
        },
        "dependencies": {"PyYAML": yaml_distribution},
    }


def runtime_receipt() -> dict[str, object]:
    identity = runtime_identity()
    core = {"schema_version": RUNTIME_RECEIPT_SCHEMA, "identity": identity, "identity_digest": canonical_sha256(identity)}
    return {**core, "receipt_sha256": canonical_sha256(core)}


def _filesystem_semantics(repo: Path) -> str:
    probe_root = repo / ".dev/ai-context/local/validation"
    probe_root.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="subject-environment-probe-", dir=probe_root))
    try:
        lower = directory / "case-probe"
        upper = directory / "CASE-PROBE"
        lower.write_bytes(b"probe")
        return "case-insensitive" if upper.exists() else "case-sensitive"
    except OSError as exc:
        raise SubjectError("repository filesystem semantic class is unknown") from exc
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def environment_identity(repo: Path, contract_id: str) -> dict[str, object]:
    git_version = _git(repo, "--version", label="Git runtime identity").decode("utf-8", errors="strict").strip()
    if not git_version.startswith("git version "):
        raise SubjectError("Git runtime identity is invalid")
    value = {
        "schema_version": "validation-environment-identity/v1",
        "contract_id": contract_id,
        "dimensions": {
            "os_family": platform.system().lower(),
            "filesystem_semantics": _filesystem_semantics(repo),
            "git_version": git_version.removeprefix("git version "),
        },
    }
    _reject_private(value, "environment identity")
    return value


def _authority_dimensions(repo: Path, subject: str) -> dict[str, str]:
    records = {
        ref: _git_file_record(repo, subject, ref)
        for ref in (
            CLASSIFICATION_REF,
            CONTRACT_REF,
            EVIDENCE_REF,
            LIFECYCLE_VALIDATOR_REF,
            REGISTRY_REF,
            RUNNER_REF,
            SCHEMA_REF,
            SUBJECT_IMPLEMENTATION_REF,
        )
    }

    def component(*refs: str) -> str:
        return canonical_sha256([records[ref] for ref in refs])

    return {
        "runner": component(RUNNER_REF, EVIDENCE_REF),
        "registry": component(REGISTRY_REF),
        "resolver": component(RUNNER_REF, SUBJECT_IMPLEMENTATION_REF),
        "policy": component(CONTRACT_REF, SCHEMA_REF, LIFECYCLE_VALIDATOR_REF),
        "configuration": component(CLASSIFICATION_REF),
    }


def _artifact(repo: Path, value: Path | str, label: str) -> dict[str, object]:
    ref, path = _repo_path(repo, value, label)
    content = path.read_bytes()
    return {"ref": ref, "sha256": sha256_bytes(content), "bytes": len(content)}


def _ignored_output(repo: Path, value: Path | str, label: str) -> tuple[str, Path]:
    ref, path = _repo_path(repo, value, label, must_exist=False)
    result = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "-q", "--", ref],
        cwd=repo,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SubjectError(f"{label} must be inside an ignored evidence root")
    return ref, path


def _validate_evidence_record(path: Path, gate_id: str, profile: str) -> None:
    try:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8", errors="strict").splitlines() if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SubjectError("source evidence is unreadable") from exc
    matches = [item for item in records if isinstance(item, dict) and item.get("validator_id") == gate_id]
    if len(matches) != 1:
        raise SubjectError("source evidence does not contain exactly one gate record")
    record = matches[0]
    if record.get("outcome") != "passed" or record.get("execution_disposition") != "executed" or record.get("profile") != profile:
        raise SubjectError("source evidence is not an executed passing gate result")


def build_subject_manifest(
    repo_value: Path,
    *,
    gate_id: str,
    profile: str,
    output: Path | str,
    closure_output: Path | str,
    runtime_output: Path | str,
    source_evidence: Path | str | None = None,
) -> tuple[dict[str, Any], set[Path]]:
    repo = repository_root(repo_value)
    identity = _head_identity(repo, require_clean=True)
    classification, check = classification_for_gate(repo, gate_id)
    if profile not in check["profiles"]:
        raise SubjectError("selected profile does not contain the gate")
    closure_ref, closure_path = _ignored_output(repo, closure_output, "tracked closure output")
    runtime_ref, runtime_path = _ignored_output(repo, runtime_output, "runtime identity output")
    _manifest_ref, manifest_path = _ignored_output(repo, output, "subject manifest output")
    closure = build_closure_receipt(repo, gate_id, identity)
    runtime = runtime_receipt()
    environment_contract = classification.get("environment_contract")
    if not isinstance(environment_contract, str) or not environment_contract:
        raise SubjectError("gate environment contract is unknown")
    environment = environment_identity(repo, environment_contract)
    command = str(check["command"])
    invocation_core = {
        "schema_version": "validation-invocation-identity/v1",
        "argv": shlex.split(command, posix=True),
        "working_directory": ".",
        "profile": profile,
    }
    authority_dimensions = _authority_dimensions(repo, identity["commit"])
    classification_core = {key: value for key, value in classification.items() if key not in {"classification_digest", "authority"}}
    if classification["classification_digest"] != canonical_sha256(classification_core):
        raise SubjectError("gate classification digest is invalid")
    source_artifact = None
    source_path: Path | None = None
    if source_evidence is not None:
        source_artifact = _artifact(repo, source_evidence, "source evidence")
        source_path = repo / str(source_artifact["ref"])
        _validate_evidence_record(source_path, gate_id, profile)
    _write_json_create_only(closure_path, closure)
    _write_json_create_only(runtime_path, runtime)
    closure_artifact = _artifact(repo, closure_path, "tracked closure receipt")
    runtime_artifact = _artifact(repo, runtime_path, "runtime identity receipt")
    if closure_artifact["ref"] != closure_ref or runtime_artifact["ref"] != runtime_ref:
        raise SubjectError("subject component output reference drifted")
    identity_projection = {
        "schema_version": IDENTITY_SCHEMA,
        "gate_id": gate_id,
        "classification_digest": classification["classification_digest"],
        "tracked_closure_digest": closure["entries_digest"],
        "invocation_digest": canonical_sha256(invocation_core),
        "authority_digest": canonical_sha256(authority_dimensions),
        "runtime_digest": runtime["identity_digest"],
        "environment_digest": canonical_sha256(environment),
    }
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "gate_id": gate_id,
        "classification": classification,
        "identity_projection": identity_projection,
        "subject_digest": canonical_sha256(identity_projection),
        "components": {
            "tracked_closure": {**closure_artifact, "entries_digest": closure["entries_digest"]},
            "invocation": {**invocation_core, "digest": identity_projection["invocation_digest"]},
            "authority": {"dimensions": authority_dimensions, "digest": identity_projection["authority_digest"]},
            "runtime": {**runtime_artifact, "digest": identity_projection["runtime_digest"]},
            "environment": {**environment, "digest": identity_projection["environment_digest"]},
        },
        "provenance": {
            "repository": runtime_repository_identity(repo),
            "commit": identity["commit"],
            "tree": identity["tree"],
            "generated_at": utc_now(),
            "source_evidence": source_artifact,
        },
        "digest_rule": {
            "algorithm": "sha256",
            "canonicalization": "utf8-json-sorted-keys-no-insignificant-whitespace-v1",
            "included": "identity_projection",
            "excluded": ["components.*.ref", "provenance"],
        },
    }
    _write_json_create_only(manifest_path, manifest)
    paths = {manifest_path, closure_path, runtime_path}
    if source_path is not None:
        paths.add(source_path)
    return manifest, paths


def _validate_artifact(repo: Path, value: object, label: str) -> Path:
    artifact = _mapping(value, label)
    _exact_keys(artifact, {"ref", "sha256", "bytes"}, label)
    ref = _safe_ref(artifact["ref"], f"{label}.ref")
    _digest(artifact["sha256"], f"{label}.sha256")
    if not isinstance(artifact["bytes"], int) or isinstance(artifact["bytes"], bool) or artifact["bytes"] < 0:
        raise SubjectError(f"{label}.bytes is invalid")
    _observed_ref, path = _repo_path(repo, ref, label)
    content = path.read_bytes()
    if sha256_bytes(content) != artifact["sha256"] or len(content) != artifact["bytes"]:
        raise SubjectError(f"{label} bytes are not authenticated")
    return path


def validate_subject_manifest(
    repo_value: Path,
    manifest: Mapping[str, object],
    *,
    fresh: bool,
) -> set[Path]:
    repo = repository_root(repo_value)
    record = dict(manifest)
    _reject_private(record, "subject manifest")
    _exact_keys(record, {"schema_version", "gate_id", "classification", "identity_projection", "subject_digest", "components", "provenance", "digest_rule"}, "subject manifest")
    if record["schema_version"] != MANIFEST_SCHEMA:
        raise SubjectError("subject manifest schema is invalid")
    gate_id = _token(record["gate_id"], "subject manifest gate id")
    classification = _mapping(record["classification"], "subject manifest classification")
    _exact_keys(classification, {"schema_version", "gate_id", "group_id", "sensitivities", "reuse_eligibility", "reusable_profiles", "environment_contract", "classification_digest", "authority"}, "subject manifest classification")
    authority_artifact = classification["authority"]
    _exact_keys(_mapping(authority_artifact, "classification authority"), {"ref", "sha256", "bytes"}, "classification authority")
    classification_core = {key: classification[key] for key in classification if key not in {"classification_digest", "authority"}}
    if classification.get("gate_id") != gate_id or _digest(classification.get("classification_digest"), "classification digest") != canonical_sha256(classification_core):
        raise SubjectError("subject manifest classification is invalid")
    projection = _mapping(record["identity_projection"], "subject identity projection")
    _exact_keys(projection, {"schema_version", "gate_id", "classification_digest", "tracked_closure_digest", "invocation_digest", "authority_digest", "runtime_digest", "environment_digest"}, "subject identity projection")
    if projection.get("schema_version") != IDENTITY_SCHEMA or projection.get("gate_id") != gate_id:
        raise SubjectError("subject identity projection is invalid")
    for key in ("classification_digest", "tracked_closure_digest", "invocation_digest", "authority_digest", "runtime_digest", "environment_digest"):
        _digest(projection.get(key), f"subject identity projection {key}")
    if projection["classification_digest"] != classification["classification_digest"] or _digest(record["subject_digest"], "subject digest") != canonical_sha256(projection):
        raise SubjectError("subject digest is invalid")
    components = _mapping(record["components"], "subject manifest components")
    _exact_keys(components, {"tracked_closure", "invocation", "authority", "runtime", "environment"}, "subject manifest components")
    closure_component = _mapping(components["tracked_closure"], "tracked closure component")
    _exact_keys(closure_component, {"ref", "sha256", "bytes", "entries_digest"}, "tracked closure component")
    closure_artifact = {key: closure_component[key] for key in ("ref", "sha256", "bytes")}
    closure_path = _validate_artifact(repo, closure_artifact, "tracked closure receipt")
    closure = _load_json(closure_path, "tracked closure receipt")
    closure_core = {key: closure[key] for key in closure if key != "receipt_sha256"}
    if closure.get("schema_version") != CLOSURE_SCHEMA or closure.get("gate_id") != gate_id or closure.get("receipt_sha256") != canonical_sha256(closure_core):
        raise SubjectError("tracked closure receipt is invalid")
    entries = closure.get("entries")
    if (
        closure.get("complete") is not True
        or closure.get("unknown_paths") != []
        or not isinstance(entries, list)
        or closure.get("path_count") != len(entries)
        or closure.get("entries_digest") != canonical_sha256(entries)
        or closure_component.get("entries_digest") != closure.get("entries_digest")
        or projection["tracked_closure_digest"] != closure.get("entries_digest")
    ):
        raise SubjectError("tracked closure is incomplete or unauthenticated")
    paths = [item.get("path") for item in entries if isinstance(item, dict)]
    if len(paths) != len(entries) or paths != sorted(set(paths)) or closure.get("paths_sha256") != canonical_sha256(paths):
        raise SubjectError("tracked closure entries are invalid")
    invocation = _mapping(components["invocation"], "subject invocation")
    _exact_keys(invocation, {"schema_version", "argv", "working_directory", "profile", "digest"}, "subject invocation")
    invocation_core = {key: invocation[key] for key in invocation if key != "digest"}
    if invocation.get("schema_version") != "validation-invocation-identity/v1" or invocation.get("working_directory") != "." or not isinstance(invocation.get("argv"), list) or not invocation["argv"] or not all(isinstance(item, str) and item for item in invocation["argv"]):
        raise SubjectError("subject invocation is invalid")
    if invocation.get("digest") != canonical_sha256(invocation_core) or projection["invocation_digest"] != invocation.get("digest"):
        raise SubjectError("subject invocation digest is invalid")
    authority = _mapping(components["authority"], "subject authority")
    _exact_keys(authority, {"dimensions", "digest"}, "subject authority")
    dimensions = _mapping(authority["dimensions"], "subject authority dimensions")
    if set(dimensions) != {"runner", "registry", "resolver", "policy", "configuration"} or not all(SHA256_RE.fullmatch(str(value)) for value in dimensions.values()):
        raise SubjectError("subject authority dimensions are invalid")
    if authority.get("digest") != canonical_sha256(dimensions) or projection["authority_digest"] != authority.get("digest"):
        raise SubjectError("subject authority digest is invalid")
    runtime_component = _mapping(components["runtime"], "subject runtime")
    _exact_keys(runtime_component, {"ref", "sha256", "bytes", "digest"}, "subject runtime")
    runtime_artifact = {key: runtime_component[key] for key in ("ref", "sha256", "bytes")}
    runtime_path = _validate_artifact(repo, runtime_artifact, "runtime identity receipt")
    runtime = _load_json(runtime_path, "runtime identity receipt")
    runtime_core = {key: runtime[key] for key in runtime if key != "receipt_sha256"}
    if runtime.get("schema_version") != RUNTIME_RECEIPT_SCHEMA or runtime.get("receipt_sha256") != canonical_sha256(runtime_core) or runtime.get("identity_digest") != canonical_sha256(runtime.get("identity")) or runtime_component.get("digest") != runtime.get("identity_digest") or projection["runtime_digest"] != runtime.get("identity_digest"):
        raise SubjectError("runtime identity receipt is invalid")
    environment = _mapping(components["environment"], "subject environment")
    _exact_keys(environment, {"schema_version", "contract_id", "dimensions", "digest"}, "subject environment")
    environment_core = {key: environment[key] for key in environment if key != "digest"}
    if environment.get("schema_version") != "validation-environment-identity/v1" or environment.get("contract_id") != classification.get("environment_contract") or environment.get("digest") != canonical_sha256(environment_core) or projection["environment_digest"] != environment.get("digest"):
        raise SubjectError("subject environment identity is invalid")
    provenance = _mapping(record["provenance"], "subject provenance")
    _exact_keys(provenance, {"repository", "commit", "tree", "generated_at", "source_evidence"}, "subject provenance")
    if not all(isinstance(provenance.get(key), str) and provenance[key] for key in ("repository", "generated_at")) or not GIT_OBJECT_RE.fullmatch(str(provenance.get("commit"))) or not GIT_OBJECT_RE.fullmatch(str(provenance.get("tree"))):
        raise SubjectError("subject provenance is invalid")
    artifacts = {closure_path, runtime_path}
    source_evidence = provenance["source_evidence"]
    if source_evidence is not None:
        source_path = _validate_artifact(repo, source_evidence, "subject source evidence")
        _validate_evidence_record(source_path, gate_id, str(invocation["profile"]))
        artifacts.add(source_path)
    digest_rule = _mapping(record["digest_rule"], "subject digest rule")
    if digest_rule != {"algorithm": "sha256", "canonicalization": "utf8-json-sorted-keys-no-insignificant-whitespace-v1", "included": "identity_projection", "excluded": ["components.*.ref", "provenance"]}:
        raise SubjectError("subject digest rule is invalid")
    if fresh:
        current = _head_identity(repo, require_clean=True)
        if current != {"commit": provenance["commit"], "tree": provenance["tree"]}:
            raise SubjectError("current subject manifest is not bound to the clean HEAD")
        current_classification, current_check = classification_for_gate(repo, gate_id)
        if current_classification != classification:
            raise SubjectError("current gate classification drifted")
        if invocation["profile"] not in current_check["profiles"] or invocation["argv"] != shlex.split(str(current_check["command"]), posix=True):
            raise SubjectError("current subject invocation drifted")
        if build_closure_receipt(repo, gate_id, current) != closure:
            raise SubjectError("current tracked closure drifted")
        if runtime_receipt() != runtime:
            raise SubjectError("current runtime identity drifted")
        fresh_environment = environment_identity(repo, str(classification["environment_contract"]))
        if environment_core != fresh_environment:
            raise SubjectError("current environment identity drifted")
        if _authority_dimensions(repo, current["commit"]) != dimensions:
            raise SubjectError("current subject authority drifted")
    return artifacts


def validate_subject_manifest_file(repo_value: Path, path_value: Path | str, *, fresh: bool) -> tuple[dict[str, Any], set[Path], Path]:
    repo = repository_root(repo_value)
    _ref, path = _repo_path(repo, path_value, "subject manifest")
    manifest = _load_json(path, "subject manifest")
    artifacts = validate_subject_manifest(repo, manifest, fresh=fresh)
    return manifest, artifacts | {path}, path


def _seal_artifacts(repo: Path, seal_path: Path, expected_sha256: str) -> tuple[dict[str, Any], dict[str, dict[str, object]]]:
    content = seal_path.read_bytes()
    if sha256_bytes(content) != _digest(expected_sha256, "original seal digest"):
        raise SubjectError("original invocation seal bytes are not authenticated")
    seal = _load_json(seal_path, "original invocation seal")
    required = {"schema_version", "invocation_id", "profile", "outcome", "sealed_at", "repository", "cardinality", "control_plane", "terminal_supervision", "artifacts", "manifest_digest"}
    _exact_keys(seal, required, "original invocation seal")
    core = {key: seal[key] for key in seal if key != "manifest_digest"}
    if seal.get("schema_version") != "validation-invocation/v1" or seal.get("outcome") != "passed" or seal.get("manifest_digest") != canonical_sha256(core):
        raise SubjectError("original invocation seal is not an authenticated passing seal")
    artifacts = seal.get("artifacts")
    if not isinstance(artifacts, list):
        raise SubjectError("original invocation seal artifacts are invalid")
    by_ref: dict[str, dict[str, object]] = {}
    for item_value in artifacts:
        item = _mapping(item_value, "original invocation artifact")
        _exact_keys(item, {"ref", "sha256", "bytes"}, "original invocation artifact")
        ref = _safe_ref(item["ref"], "original invocation artifact ref")
        _digest(item["sha256"], "original invocation artifact digest")
        if ref in by_ref:
            raise SubjectError("original invocation seal artifact is duplicated")
        by_ref[ref] = item
    if list(by_ref) != sorted(by_ref):
        raise SubjectError("original invocation seal artifacts are noncanonical")
    return seal, by_ref


def _require_sealed_file(repo: Path, by_ref: Mapping[str, Mapping[str, object]], path: Path, label: str) -> dict[str, object]:
    ref = path.resolve().relative_to(repo).as_posix()
    content = path.read_bytes()
    expected = {"ref": ref, "sha256": sha256_bytes(content), "bytes": len(content)}
    if by_ref.get(ref) != expected:
        raise SubjectError(f"{label} is absent from the original invocation seal")
    return expected


def _rebind_reason(original: Mapping[str, object], current: Mapping[str, object]) -> str:
    original_projection = _mapping(original["identity_projection"], "original identity projection")
    current_projection = _mapping(current["identity_projection"], "current identity projection")
    reasons = {
        "classification_digest": "classification-drift",
        "tracked_closure_digest": "tracked-input-or-dependency-drift",
        "invocation_digest": "invocation-drift",
        "authority_digest": "authority-or-policy-drift",
        "runtime_digest": "runtime-drift",
        "environment_digest": "environment-drift",
    }
    for key, reason in reasons.items():
        if original_projection.get(key) != current_projection.get(key):
            return reason
    return "subject-digest-drift"


def decide_rebind(
    original: Mapping[str, object],
    current: Mapping[str, object],
    *,
    classification_approved: bool,
    profile_allowlisted: bool,
    original_authentication_valid: bool,
    current_closure_complete: bool,
    current_unknown_paths: list[str],
) -> tuple[str, str]:
    """Return one deterministic fail-closed rebind decision."""
    if not classification_approved or not profile_allowlisted:
        return "blocked", "classification-or-profile-not-approved"
    if not original_authentication_valid:
        return "blocked", "original-authentication-unknown"
    if not current_closure_complete or current_unknown_paths:
        return "blocked", "dependency-closure-unknown"
    if original.get("subject_digest") == current.get("subject_digest"):
        return "reused-with-proof", "approved-subject-manifests-equivalent"
    return "re-executed", _rebind_reason(original, current)


def build_rebind_receipt(
    repo_value: Path,
    *,
    original_manifest_value: Path | str,
    current_manifest_value: Path | str,
    original_seal_value: Path | str,
    original_seal_sha256: str,
    output: Path | str,
) -> dict[str, Any]:
    repo = repository_root(repo_value)
    original, original_paths, original_manifest_path = validate_subject_manifest_file(repo, original_manifest_value, fresh=False)
    current, _current_paths, current_manifest_path = validate_subject_manifest_file(repo, current_manifest_value, fresh=True)
    if original["gate_id"] != current["gate_id"]:
        raise SubjectError("original and current manifests name different gates")
    gate_id = str(current["gate_id"])
    classification = _mapping(current["classification"], "current gate classification")
    profile = _mapping(current["components"], "current components")["invocation"]["profile"]
    if classification.get("reuse_eligibility") != "pilot-approved" or profile not in classification.get("reusable_profiles", []):
        raise SubjectError("current gate or profile is not allowlisted for subject-digest reuse")
    if any(item in classification.get("sensitivities", []) for item in ("identity", "provider")):
        raise SubjectError("identity-sensitive or provider-sensitive acceptance cannot be rebound")
    _seal_ref, seal_path = _repo_path(repo, original_seal_value, "original invocation seal")
    seal, sealed = _seal_artifacts(repo, seal_path, original_seal_sha256)
    original_manifest_artifact = _require_sealed_file(repo, sealed, original_manifest_path, "original subject manifest")
    for path in original_paths - {original_manifest_path}:
        _require_sealed_file(repo, sealed, path, "original subject component")
    original_provenance = _mapping(original["provenance"], "original provenance")
    original_source = original_provenance.get("source_evidence")
    if original_source is None:
        raise SubjectError("original subject manifest lacks executed source evidence")
    original_evidence_path = repo / str(original_source["ref"])
    original_evidence_artifact = _require_sealed_file(repo, sealed, original_evidence_path, "original source evidence")
    original_invocation = _mapping(original["components"], "original components")["invocation"]
    _validate_evidence_record(original_evidence_path, gate_id, str(original_invocation["profile"]))
    seal_repository = _mapping(seal.get("repository"), "original seal repository")
    if seal_repository.get("commit") != original_provenance.get("commit") or seal_repository.get("tree") != original_provenance.get("tree"):
        raise SubjectError("original invocation seal and subject provenance differ")
    original_classification = _mapping(original["classification"], "original classification")
    equivalent = original.get("subject_digest") == current.get("subject_digest")
    if original_classification.get("classification_digest") != classification.get("classification_digest"):
        equivalent = False
    decision_outcome, decision_reason = decide_rebind(
        original,
        current,
        classification_approved=classification.get("reuse_eligibility") == "pilot-approved",
        profile_allowlisted=profile in classification.get("reusable_profiles", []),
        original_authentication_valid=True,
        current_closure_complete=True,
        current_unknown_paths=[],
    )
    if not equivalent and decision_outcome == "reused-with-proof":
        decision_outcome = "re-executed"
        decision_reason = "classification-drift"
    decision = {
        "outcome": decision_outcome,
        "reason": decision_reason,
        "truthful_statement": (
            f"Evidence executed at {original_provenance['commit']} applies to the subject at {current['provenance']['commit']}; "
            f"it was not executed or audited at {current['provenance']['commit']}."
            if equivalent
            else "A governed subject component changed; execute the gate again for the current subject."
        ),
    }
    fresh_gates = [{"gate": gate, "required": True, "replaceable_by_reuse": False} for gate in REQUIRED_FRESH_GATES]
    original_manifest_ref = original_manifest_path.relative_to(repo).as_posix()
    current_manifest_ref = current_manifest_path.relative_to(repo).as_posix()
    current_manifest_artifact = _artifact(repo, current_manifest_path, "current subject manifest")
    seal_artifact = _artifact(repo, seal_path, "original invocation seal")
    core = {
        "schema_version": REBIND_SCHEMA,
        "record_type": "subject-evidence-rebind",
        "gate_id": gate_id,
        "original": {
            "commit": original_provenance["commit"],
            "tree": original_provenance["tree"],
            "subject_manifest": {**original_manifest_artifact, "subject_digest": original["subject_digest"]},
            "evidence": {"outcome": "passed", "execution_disposition": "executed", **original_evidence_artifact},
            "authentication": {"mode": "sealed-at-original-execution", "verified": True, "seal": seal_artifact},
        },
        "current": {
            "commit": current["provenance"]["commit"],
            "tree": current["provenance"]["tree"],
            "subject_manifest": {**current_manifest_artifact, "subject_digest": current["subject_digest"], "generated_fresh": True},
        },
        "verification": {
            "classification_approved": classification.get("reuse_eligibility") == "pilot-approved",
            "allowlisted": profile in classification.get("reusable_profiles", []),
            "original_authentication_valid": True,
            "current_closure_complete": True,
            "current_unknown_paths": [],
            "subject_digest_equal": equivalent,
            "provenance_preserved": original_manifest_ref != current_manifest_ref or original_provenance["commit"] == current["provenance"]["commit"],
            "required_fresh_gates": fresh_gates,
        },
        "decision": decision,
    }
    receipt = {**core, "receipt_sha256": canonical_sha256(core)}
    _output_ref, output_path = _ignored_output(repo, output, "subject rebind output")
    _write_json_create_only(output_path, receipt)
    return receipt


def validate_rebind_receipt(record: Mapping[str, object]) -> None:
    value = dict(record)
    _reject_private(value, "subject rebind receipt")
    _exact_keys(value, {"schema_version", "record_type", "gate_id", "original", "current", "verification", "decision", "receipt_sha256"}, "subject rebind receipt")
    if value.get("schema_version") != REBIND_SCHEMA or value.get("record_type") != "subject-evidence-rebind":
        raise SubjectError("subject rebind receipt identity is invalid")
    _token(value.get("gate_id"), "subject rebind gate id")
    original = _mapping(value.get("original"), "subject rebind original")
    current = _mapping(value.get("current"), "subject rebind current")
    _exact_keys(original, {"commit", "tree", "subject_manifest", "evidence", "authentication"}, "subject rebind original")
    _exact_keys(current, {"commit", "tree", "subject_manifest"}, "subject rebind current")
    for label, subject in (("original", original), ("current", current)):
        if not GIT_OBJECT_RE.fullmatch(str(subject.get("commit"))) or not GIT_OBJECT_RE.fullmatch(str(subject.get("tree"))):
            raise SubjectError(f"subject rebind {label} provenance is invalid")
    original_manifest = _mapping(original.get("subject_manifest"), "original subject manifest reference")
    current_manifest = _mapping(current.get("subject_manifest"), "current subject manifest reference")
    _exact_keys(original_manifest, {"ref", "sha256", "bytes", "subject_digest"}, "original subject manifest reference")
    _exact_keys(current_manifest, {"ref", "sha256", "bytes", "subject_digest", "generated_fresh"}, "current subject manifest reference")
    for label, manifest in (("original", original_manifest), ("current", current_manifest)):
        _safe_ref(manifest.get("ref"), f"{label} subject manifest ref")
        _digest(manifest.get("sha256"), f"{label} subject manifest bytes digest")
        _digest(manifest.get("subject_digest"), f"{label} subject digest")
        if not isinstance(manifest.get("bytes"), int) or isinstance(manifest.get("bytes"), bool) or manifest["bytes"] <= 0:
            raise SubjectError(f"{label} subject manifest size is invalid")
    if current_manifest.get("generated_fresh") is not True:
        raise SubjectError("current subject manifest is not marked freshly generated")
    evidence = _mapping(original.get("evidence"), "original subject evidence")
    _exact_keys(evidence, {"outcome", "execution_disposition", "ref", "sha256", "bytes"}, "original subject evidence")
    if evidence.get("outcome") != "passed" or evidence.get("execution_disposition") != "executed":
        raise SubjectError("original subject evidence is not an executed pass")
    _safe_ref(evidence.get("ref"), "original subject evidence ref")
    _digest(evidence.get("sha256"), "original subject evidence digest")
    authentication = _mapping(original.get("authentication"), "original subject authentication")
    _exact_keys(authentication, {"mode", "verified", "seal"}, "original subject authentication")
    if authentication.get("mode") != "sealed-at-original-execution" or authentication.get("verified") is not True:
        raise SubjectError("original subject authentication is invalid")
    seal = _mapping(authentication.get("seal"), "original invocation seal reference")
    _exact_keys(seal, {"ref", "sha256", "bytes"}, "original invocation seal reference")
    _safe_ref(seal.get("ref"), "original invocation seal ref")
    _digest(seal.get("sha256"), "original invocation seal digest")
    verification = _mapping(value.get("verification"), "subject rebind verification")
    _exact_keys(
        verification,
        {
            "classification_approved",
            "allowlisted",
            "original_authentication_valid",
            "current_closure_complete",
            "current_unknown_paths",
            "subject_digest_equal",
            "provenance_preserved",
            "required_fresh_gates",
        },
        "subject rebind verification",
    )
    expected_fresh = [{"gate": gate, "required": True, "replaceable_by_reuse": False} for gate in REQUIRED_FRESH_GATES]
    if verification.get("required_fresh_gates") != expected_fresh:
        raise SubjectError("subject rebind fresh gates are missing or replaceable")
    decision = _mapping(value.get("decision"), "subject rebind decision")
    if decision.get("outcome") not in {"reused-with-proof", "re-executed", "blocked"} or not isinstance(decision.get("reason"), str) or not isinstance(decision.get("truthful_statement"), str):
        raise SubjectError("subject rebind decision is invalid")
    if decision.get("outcome") == "reused-with-proof":
        if not all(verification.get(key) is True for key in ("classification_approved", "allowlisted", "original_authentication_valid", "current_closure_complete", "subject_digest_equal", "provenance_preserved")) or verification.get("current_unknown_paths") != []:
            raise SubjectError("reused subject rebind lacks complete proof")
        current = _mapping(value.get("current"), "subject rebind current")
        current_commit = str(current.get("commit", ""))
        if "not executed or audited at" not in str(decision.get("truthful_statement")) or current_commit not in str(decision.get("truthful_statement")):
            raise SubjectError("subject rebind wording misrepresents execution identity")
        if original_manifest["subject_digest"] != current_manifest["subject_digest"]:
            raise SubjectError("reused subject rebind manifest digests differ")
    elif verification.get("subject_digest_equal") is not False:
        raise SubjectError("non-reused subject rebind must not claim digest equality")
    core = {key: value[key] for key in value if key != "receipt_sha256"}
    if _digest(value.get("receipt_sha256"), "subject rebind receipt digest") != canonical_sha256(core):
        raise SubjectError("subject rebind receipt digest is invalid")


def validated_rebind_source(
    repo_value: Path,
    receipt_value: Path | str,
    *,
    expected_gate_id: str | None = None,
    expected_profile: str | None = None,
) -> tuple[dict[str, Any], list[Path]]:
    """Re-authenticate a persisted rebind receipt for runner consumption."""
    repo = repository_root(repo_value)
    _receipt_ref, receipt_path = _repo_path(repo, receipt_value, "subject rebind receipt")
    receipt = _load_json(receipt_path, "subject rebind receipt")
    validate_rebind_receipt(receipt)
    if receipt["decision"]["outcome"] != "reused-with-proof":
        raise SubjectError("subject rebind receipt does not authorize reuse")
    gate_id = str(receipt["gate_id"])
    if expected_gate_id is not None and gate_id != expected_gate_id:
        raise SubjectError("subject rebind gate does not match the selected validator")
    current_ref = receipt["current"]["subject_manifest"]["ref"]
    current, current_paths, current_path = validate_subject_manifest_file(repo, current_ref, fresh=True)
    current_artifact = _artifact(repo, current_path, "current subject manifest")
    expected_current = {
        **current_artifact,
        "subject_digest": current["subject_digest"],
        "generated_fresh": True,
    }
    if receipt["current"]["subject_manifest"] != expected_current:
        raise SubjectError("current subject manifest differs from its rebind receipt")
    current_profile = str(current["components"]["invocation"]["profile"])
    if expected_profile is not None and current_profile != expected_profile:
        raise SubjectError("subject rebind profile does not match the active profile")
    if current["gate_id"] != gate_id:
        raise SubjectError("current subject manifest gate differs from the rebind receipt")
    current_provenance = current["provenance"]
    if (
        receipt["current"]["commit"] != current_provenance["commit"]
        or receipt["current"]["tree"] != current_provenance["tree"]
    ):
        raise SubjectError("current subject provenance differs from the rebind receipt")
    original_ref = receipt["original"]["subject_manifest"]["ref"]
    original, original_paths, original_path = validate_subject_manifest_file(repo, original_ref, fresh=False)
    original_artifact = _artifact(repo, original_path, "original subject manifest")
    expected_original = {**original_artifact, "subject_digest": original["subject_digest"]}
    if receipt["original"]["subject_manifest"] != expected_original:
        raise SubjectError("original subject manifest differs from its rebind receipt")
    if original["gate_id"] != gate_id:
        raise SubjectError("original subject manifest gate differs from the rebind receipt")
    original_provenance = original["provenance"]
    if (
        receipt["original"]["commit"] != original_provenance["commit"]
        or receipt["original"]["tree"] != original_provenance["tree"]
    ):
        raise SubjectError("original subject provenance differs from the rebind receipt")
    evidence_value = receipt["original"]["evidence"]
    evidence_path = _validate_artifact(
        repo,
        {key: evidence_value[key] for key in ("ref", "sha256", "bytes")},
        "original source evidence",
    )
    _validate_evidence_record(evidence_path, gate_id, str(original["components"]["invocation"]["profile"]))
    if original_provenance["source_evidence"] != {
        key: evidence_value[key] for key in ("ref", "sha256", "bytes")
    }:
        raise SubjectError("original source evidence differs from subject provenance")
    seal_value = receipt["original"]["authentication"]["seal"]
    seal_path = _validate_artifact(repo, seal_value, "original invocation seal")
    seal, sealed_artifacts = _seal_artifacts(repo, seal_path, str(seal_value["sha256"]))
    if (
        seal["repository"].get("commit") != original_provenance["commit"]
        or seal["repository"].get("tree") != original_provenance["tree"]
    ):
        raise SubjectError("original invocation seal provenance differs from the subject")
    for path in original_paths:
        _require_sealed_file(repo, sealed_artifacts, path, "original subject artifact")
    _require_sealed_file(repo, sealed_artifacts, evidence_path, "original source evidence")
    normalized = {
        "kind": "subject-rebind",
        "gate_id": gate_id,
        "profile": current_profile,
        "rebind_receipt": _artifact(repo, receipt_path, "subject rebind receipt"),
        "original_subject_manifest": expected_original,
        "current_subject_manifest": expected_current,
        "original_evidence": {
            "ref": evidence_value["ref"],
            "sha256": evidence_value["sha256"],
            "bytes": evidence_value["bytes"],
        },
        "original_invocation_seal": dict(seal_value),
        "original_commit": original_provenance["commit"],
        "current_commit": current_provenance["commit"],
        "subject_digest": current["subject_digest"],
        "decision": dict(receipt["decision"]),
        "required_fresh_gates": list(receipt["verification"]["required_fresh_gates"]),
    }
    paths = {
        receipt_path,
        seal_path,
        evidence_path,
        original_path,
        current_path,
        *original_paths,
        *current_paths,
    }
    return normalized, sorted(paths, key=lambda item: item.relative_to(repo).as_posix())


def sealable_subject_manifest_paths(repo_value: Path, path_values: Iterable[Path | str], evidence_path: Path) -> set[Path]:
    repo = repository_root(repo_value)
    result: set[Path] = set()
    expected_evidence = _artifact(repo, evidence_path, "invocation evidence")
    for path_value in path_values:
        manifest, paths, manifest_path = validate_subject_manifest_file(repo, path_value, fresh=True)
        source = _mapping(manifest["provenance"], "subject provenance").get("source_evidence")
        if source != expected_evidence:
            raise SubjectError("subject manifest source evidence does not match the invocation evidence")
        result.update(paths)
        result.add(manifest_path)
    return result
