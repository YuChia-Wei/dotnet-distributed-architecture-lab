#!/usr/bin/env python3
"""Sealed S2 orchestration for evidence-bound multi-hop target upgrades.

The module deliberately composes the existing #203 child transaction rather
than creating a second package-apply or provenance authority.  Durable route
state belongs only under the target Git administrative directory; portable
packages and target provenance never receive route-only evidence.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Callable

import yaml

import ai_context_package_apply as APPLY
import ai_context_target_provenance as TARGET
import ai_context_upgrade_routes as ROUTES


ROUTE_INTENT_PATH = "route-intent.json"
ROUTE_MATRIX_PATH = "route-matrix.yaml"
ROUTE_RESOLVER_RESULT_PATH = TARGET.MULTI_HOP_RESOLVER_RESULT_PATH
ROUTE_JOURNAL_PATH = "journal.yaml"
ROUTE_CHECKPOINT_DIRECTORY = "checkpoints"
ROUTE_HOP_DIRECTORY = "hops"
ROUTE_PREPARING_DIRECTORY = ".preparing-hops"
ROUTE_FAILED_PREPARING_DIRECTORY = "failed-preparations"
ROUTE_PREPARATION_PATH = "preparation.json"
ROUTE_HOP_EVIDENCE_PATH = "evidence.json"
ROUTE_STATES = {
    "planned",
    "awaiting-owner-decision",
    "applying",
    "awaiting-target-validation",
    "validating",
    "finalizing",
    "checkpointing",
    "checkpointed",
    "rolling-back",
    "completed",
    "rolled-back",
}


class MultiHopUpgradeError(APPLY.ApplyError):
    """A route-level safety contract violation."""


def _canonical_json_bytes(value: object) -> bytes:
    return APPLY.canonical_json_bytes(value)


def _canonical_digest(value: object) -> str:
    return APPLY.canonical_digest(value)


def _route_error(message: str) -> MultiHopUpgradeError:
    return MultiHopUpgradeError(message)


def _require_sha256(value: object, label: str, *, allow_none: bool = False) -> str | None:
    try:
        return APPLY.require_sha256(value, label, allow_none=allow_none)
    except APPLY.ApplyError as exc:
        raise _route_error(str(exc)) from exc


def _safe_relative(value: object, label: str) -> str:
    try:
        return APPLY.safe_path(value, label)
    except APPLY.ApplyError as exc:
        raise _route_error(str(exc)) from exc


def _edge_identity(edge: object, label: str = "route edge") -> dict:
    if not isinstance(edge, dict):
        raise _route_error(f"{label} must be a mapping")
    edge_id = edge.get("edge_id")
    order = edge.get("order")
    from_version = edge.get("from_version")
    to_version = edge.get("to_version")
    if (
        not isinstance(edge_id, str)
        or not edge_id
        or type(order) is not int
        or order < 1
        or not isinstance(from_version, str)
        or not isinstance(to_version, str)
    ):
        raise _route_error(f"{label} identity is invalid")
    return {
        "edge_id": edge_id,
        "order": order,
        "from_version": from_version,
        "to_version": to_version,
        "identity_sha256": _canonical_digest(edge),
    }


def _sealed_edge_identity(edge: object, label: str = "sealed route edge") -> dict:
    required = {"edge_id", "order", "from_version", "to_version", "identity_sha256"}
    if not isinstance(edge, dict) or set(edge) != required:
        raise _route_error(f"{label} fields are invalid")
    identity = {
        "edge_id": edge.get("edge_id"),
        "order": edge.get("order"),
        "from_version": edge.get("from_version"),
        "to_version": edge.get("to_version"),
    }
    if (
        not isinstance(identity["edge_id"], str)
        or not identity["edge_id"]
        or type(identity["order"]) is not int
        or identity["order"] < 1
        or not isinstance(identity["from_version"], str)
        or not isinstance(identity["to_version"], str)
    ):
        raise _route_error(f"{label} identity is invalid")
    _require_sha256(edge.get("identity_sha256"), f"{label} SHA-256")
    return deepcopy(edge)


def _expected_edge_identity(edge: object, label: str = "route edge") -> dict:
    """Accept a full resolver edge or the exact compact identity already sealed."""
    sealed_keys = {"edge_id", "order", "from_version", "to_version", "identity_sha256"}
    if isinstance(edge, dict) and set(edge) == sealed_keys:
        return _sealed_edge_identity(edge, label)
    return _edge_identity(edge, label)


def _normalized_resolver_result(
    result: object,
    matrix_raw: bytes,
    *,
    origin: str,
    target: str,
) -> dict:
    """Retain only the verified S1 selection, never its source-local locator.

    ``resolve_matrix_file`` is the only operation that can attest source asset
    readiness.  Its returned mapping is still an in-process boundary, so the
    outer transaction normalizes the selected route into one exact canonical
    record instead of retaining arbitrary resolver fields or an absolute source
    matrix path.
    """
    if not isinstance(result, dict):
        raise _route_error("resolved multi-hop route result is invalid")
    # Route kind is an admission decision, not a consequence of the selected
    # edge bytes.  Reject direct/reconciliation/unsupported results before
    # attempting to normalize an optional or differently-shaped selection.
    if result.get("route_kind") != "orchestrated-multi-hop":
        raise _route_error("multi-hop upgrade requires an orchestrated-multi-hop route")
    matrix = result.get("matrix")
    selected = result.get("selected_route")
    if (
        result.get("origin") != origin
        or result.get("target") != target
        or not isinstance(matrix, dict)
        or matrix.get("sha256") != APPLY.sha256_bytes(matrix_raw)
        or matrix.get("byte_length") != len(matrix_raw)
        or not isinstance(matrix.get("matrix_id"), str)
        or not matrix["matrix_id"]
        or not isinstance(selected, dict)
        or not isinstance(selected.get("route_id"), str)
        or not selected["route_id"]
        or not isinstance(selected.get("edges"), list)
    ):
        raise _route_error("resolved multi-hop route identity differs from supplied bytes")
    edges = [_edge_identity(item, "resolved multi-hop route edge") for item in selected["edges"]]
    if (
        len(edges) < 2
        or [item["order"] for item in edges] != list(range(1, len(edges) + 1))
        or selected.get("edge_count", len(edges)) != len(edges)
    ):
        raise _route_error("resolved multi-hop route edges are invalid")
    return {
        "schema_version": TARGET.MULTI_HOP_RESOLVER_RESULT_SCHEMA,
        "origin": origin,
        "target": target,
        "matrix": {
            "matrix_id": matrix["matrix_id"],
            "sha256": matrix["sha256"],
            "byte_length": matrix["byte_length"],
        },
        "route_kind": "orchestrated-multi-hop",
        "selected_route": {
            "route_id": selected["route_id"],
            "edge_count": len(edges),
            "edges": deepcopy(selected["edges"]),
        },
    }


def _read_regular(path: Path, label: str) -> bytes:
    if path.is_symlink() or APPLY.is_reparse_point(path) or not path.is_file():
        raise _route_error(f"{label} must be a regular file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise _route_error(f"cannot read {label}: {exc}") from exc


def _read_canonical_json(path: Path, label: str) -> tuple[dict, bytes]:
    raw = _read_regular(path, label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _route_error(f"{label} is not canonical JSON") from exc
    if not isinstance(value, dict) or _canonical_json_bytes(value) != raw:
        raise _route_error(f"{label} is not canonical JSON")
    return value, raw


def _read_journal(path: Path) -> tuple[dict, bytes]:
    raw = _read_regular(path, "multi-hop route journal")
    try:
        value = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise _route_error("multi-hop route journal cannot be parsed") from exc
    if not isinstance(value, dict) or APPLY.deterministic_yaml_bytes(value) != raw:
        raise _route_error("multi-hop route journal is not deterministic YAML")
    return value, raw


def _write_json(path: Path, value: dict) -> str:
    raw = _canonical_json_bytes(value)
    APPLY.atomic_write_bytes(path, raw)
    return APPLY.sha256_bytes(raw)


def _write_journal(path: Path, value: dict) -> None:
    APPLY.atomic_write_yaml(path, value)


def _route_root(target: Path, route_transaction_id: str) -> Path:
    try:
        return APPLY.multi_hop_route_root(target, route_transaction_id)
    except APPLY.ApplyError as exc:
        raise _route_error(str(exc)) from exc


def _journal_fields_valid(journal: object, intent: dict) -> dict:
    required = {
        "schema_version",
        "route_transaction_id",
        "route_intent_sha256",
        "target_root",
        "target_starting_commit",
        "state",
        "next_hop_index",
        "last_checkpoint_index",
        "last_checkpoint_sha256",
        "active_hop",
    }
    if not isinstance(journal, dict) or set(journal) != required:
        raise _route_error("multi-hop route journal fields are invalid")
    if (
        journal.get("schema_version") != APPLY.MULTI_HOP_ROUTE_JOURNAL_SCHEMA_VERSION
        or journal.get("route_transaction_id") != intent.get("route_transaction_id")
        or journal.get("route_intent_sha256")
        != APPLY.sha256_bytes(_canonical_json_bytes(intent))
        or journal.get("target_root") != intent.get("target_root")
        or journal.get("target_starting_commit") != intent.get("target_starting_commit")
        or journal.get("state") not in ROUTE_STATES
    ):
        raise _route_error("multi-hop route journal identity is invalid")
    if type(journal.get("next_hop_index")) is not int or journal["next_hop_index"] < 0:
        raise _route_error("multi-hop route journal next hop is invalid")
    checkpoint_index = journal.get("last_checkpoint_index")
    checkpoint_sha = journal.get("last_checkpoint_sha256")
    if (checkpoint_index is None) != (checkpoint_sha is None):
        raise _route_error("multi-hop route journal checkpoint binding is incomplete")
    if checkpoint_index is not None:
        if type(checkpoint_index) is not int or checkpoint_index < 0:
            raise _route_error("multi-hop route journal checkpoint index is invalid")
        _require_sha256(checkpoint_sha, "multi-hop route journal checkpoint SHA-256")
    active = journal.get("active_hop")
    if active is not None and not isinstance(active, dict):
        raise _route_error("multi-hop route journal active hop is invalid")
    return journal


def _load_route(target: Path, route_transaction_id: str) -> tuple[Path, dict, dict]:
    root = _route_root(target, route_transaction_id)
    if root.is_symlink() or APPLY.is_reparse_point(root) or not root.is_dir():
        raise _route_error("multi-hop route transaction directory is missing or unsafe")
    intent, intent_raw = _read_canonical_json(root / ROUTE_INTENT_PATH, "multi-hop route intent")
    required_intent = {
        "schema_version",
        "route_transaction_id",
        "target_root",
        "target_starting_commit",
        "origin",
        "target",
        "matrix",
        "resolver_result",
        "route",
    }
    if set(intent) != required_intent or intent.get("schema_version") != APPLY.MULTI_HOP_ROUTE_INTENT_SCHEMA_VERSION:
        raise _route_error("multi-hop route intent fields are invalid")
    if intent.get("route_transaction_id") != route_transaction_id:
        raise _route_error("multi-hop route intent transaction ID differs")
    intent_seed = deepcopy(intent)
    if intent_seed.pop("route_transaction_id", None) != route_transaction_id or _canonical_digest(intent_seed) != route_transaction_id:
        raise _route_error("multi-hop route intent transaction identity differs")
    if intent.get("target_root") != str(target.resolve()):
        raise _route_error("multi-hop route intent target differs")
    head = intent.get("target_starting_commit")
    if not isinstance(head, str) or len(head) != 40:
        raise _route_error("multi-hop route intent target HEAD is invalid")
    matrix = intent.get("matrix")
    if (
        not isinstance(matrix, dict)
        or set(matrix) != {"path", "sha256", "byte_length"}
        or matrix.get("path") != ROUTE_MATRIX_PATH
        or type(matrix.get("byte_length")) is not int
        or matrix["byte_length"] < 0
    ):
        raise _route_error("multi-hop route intent matrix is invalid")
    _require_sha256(matrix.get("sha256"), "multi-hop route intent matrix SHA-256")
    matrix_raw = _read_regular(root / ROUTE_MATRIX_PATH, "multi-hop route matrix")
    if len(matrix_raw) != matrix["byte_length"] or APPLY.sha256_bytes(matrix_raw) != matrix["sha256"]:
        raise _route_error("multi-hop route matrix bytes differ")
    route = intent.get("route")
    if not isinstance(route, dict) or set(route) != {"route_id", "edges"}:
        raise _route_error("multi-hop route intent route is invalid")
    if not isinstance(route.get("route_id"), str) or not route["route_id"]:
        raise _route_error("multi-hop route intent route ID is invalid")
    edges = route.get("edges")
    if not isinstance(edges, list) or len(edges) < 2:
        raise _route_error("multi-hop route intent edges are invalid")
    identities = [_sealed_edge_identity(item, "multi-hop route intent edge") for item in edges]
    if identities != edges or [item["order"] for item in identities] != list(range(1, len(identities) + 1)):
        raise _route_error("multi-hop route intent ordered edges are invalid")
    journal, _ = _read_journal(root / ROUTE_JOURNAL_PATH)
    _journal_fields_valid(journal, intent)
    if journal["next_hop_index"] > len(identities):
        raise _route_error("multi-hop route journal exceeds the sealed route")
    _resolve_sealed_route_edges(root, intent)
    _cleanup_bound_proposal(target, root, intent, journal)
    return root, intent, journal


def _persist_route_journal(root: Path, intent: dict, journal: dict) -> None:
    _journal_fields_valid(journal, intent)
    _write_journal(root / ROUTE_JOURNAL_PATH, journal)


def _resolve_sealed_route_edges(route_root: Path, intent: dict) -> list[dict]:
    """Load the path-free S1 result sealed beside the retained raw matrix."""
    errors: list[str] = []
    edges = TARGET.sealed_multi_hop_resolver_edges(route_root, intent, errors)
    if errors or edges is None:
        raise _route_error(
            "sealed multi-hop resolver result is invalid: " + "; ".join(errors)
        )
    return edges


def _resolve_prepare_route_edges(
    route_root: Path, intent: dict, matrix_root: Path
) -> list[dict]:
    """Recheck live source assets only while materializing the next hop.

    The source matrix directory is deliberately not retained in target Git
    administration.  A caller must supply it for preparation; the newly
    resolved route must exactly equal the already sealed full S1 selection.
    """
    retained_raw = _read_regular(route_root / ROUTE_MATRIX_PATH, "sealed route matrix")
    try:
        matrix, parsed_raw = ROUTES.load_route_matrix(route_root / ROUTE_MATRIX_PATH)
        if parsed_raw != retained_raw:
            raise _route_error("sealed route matrix bytes changed while preparing")
        fresh = ROUTES.resolve_upgrade_route(
            matrix,
            origin=intent["origin"],
            target=intent["target"],
            matrix_bytes=retained_raw,
            asset_root=matrix_root,
            matrix_reference=(route_root / ROUTE_MATRIX_PATH).as_posix(),
        )
        normalized = _normalized_resolver_result(
            fresh,
            retained_raw,
            origin=intent["origin"],
            target=intent["target"],
        )
    except ROUTES.UpgradeRouteError as exc:
        raise _route_error(f"multi-hop source route revalidation failed: {exc}") from exc
    sealed = _resolve_sealed_route_edges(route_root, intent)
    selected = normalized["selected_route"]
    if (
        selected["route_id"] != intent["route"]["route_id"]
        or selected["edges"] != sealed
    ):
        raise _route_error("fresh multi-hop source route differs from sealed resolver result")
    return sealed


def _matrix_asset(matrix_root: Path, artifact: object, label: str) -> tuple[Path, bytes, dict]:
    if not isinstance(artifact, dict) or set(artifact) != {"asset_id", "path", "sha256"}:
        raise _route_error(f"{label} identity is invalid")
    relative = _safe_relative(artifact.get("path"), f"{label} path")
    expected = _require_sha256(artifact.get("sha256"), f"{label} SHA-256")
    try:
        APPLY.reject_symlink_boundary(matrix_root, relative)
    except APPLY.ApplyError as exc:
        raise _route_error(str(exc)) from exc
    path = matrix_root / Path(*PurePosixPath(relative).parts)
    raw = _read_regular(path, label)
    if APPLY.sha256_bytes(raw) != expected:
        raise _route_error(f"{label} bytes differ")
    return path, raw, deepcopy(artifact)


def _safe_archive_members(path: Path) -> dict[str, tuple[bytes, int]]:
    """Read a portable package archive without extraction or builder imports."""
    files: dict[str, tuple[bytes, int]] = {}
    casefolded: dict[str, str] = {}

    def add(name: object, content: bytes, mode: object) -> None:
        try:
            relative = _safe_relative(name, "route archive member")
        except MultiHopUpgradeError as exc:
            raise _route_error(f"unsafe route archive member: {name!r}") from exc
        if relative != name:
            raise _route_error(f"route archive member is not a raw relative POSIX path: {name!r}")
        if not isinstance(mode, int) or not 0 <= mode <= 0o777:
            raise _route_error(f"route archive member mode is invalid: {name!r}")
        if relative in files:
            raise _route_error(f"duplicate route archive member: {relative}")
        folded = relative.casefold()
        if folded in casefolded:
            raise _route_error(
                "case-insensitive route archive member collision: "
                f"{casefolded[folded]} and {relative}"
            )
        casefolded[folded] = relative
        files[relative] = (content, mode)

    try:
        if path.name.endswith(".zip"):
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    raw_mode = info.external_attr >> 16
                    kind = raw_mode & 0o170000
                    if kind not in {0, 0o100000}:
                        raise _route_error(f"unsupported ZIP route archive member type: {info.filename}")
                    add(info.filename, archive.read(info), raw_mode & 0o777)
        elif path.name.endswith(".tar.gz"):
            with tarfile.open(path, "r:gz") as archive:
                for info in archive.getmembers():
                    if info.isdir():
                        continue
                    if not info.isfile():
                        raise _route_error(f"unsupported TAR route archive member type: {info.name}")
                    stream = archive.extractfile(info)
                    if stream is None:
                        raise _route_error(f"cannot read TAR route archive member: {info.name}")
                    add(info.name, stream.read(), info.mode & 0o777)
        else:
            raise _route_error(f"unsupported route archive type: {path.name}")
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as exc:
        raise _route_error(f"cannot safely read route archive: {exc}") from exc
    roots = {PurePosixPath(name).parts[0] for name in files}
    if not files or len(roots) != 1:
        raise _route_error("route archive must contain exactly one envelope root")
    return files


def _checksum_binds_archive(checksum_raw: bytes, archive_raw: bytes, archive_name: str) -> bool:
    try:
        match = ROUTES.CHECKSUM_SIDECAR_RE.fullmatch(checksum_raw.decode("utf-8"))
    except UnicodeDecodeError:
        return False
    return (
        match is not None
        and match.group("sha256") == APPLY.sha256_bytes(archive_raw)
        and match.group("filename") == archive_name
    )


def _materialize_package(
    route_root: Path,
    matrix_root: Path,
    edge: dict,
    hop_index: int,
) -> dict:
    """Validate and materialize one exact package without archive extraction APIs."""
    artifacts = edge.get("artifacts")
    validation = edge.get("validation")
    if not isinstance(artifacts, dict) or not isinstance(validation, dict):
        raise _route_error("route edge artifacts or validation are invalid")
    archive_source, archive_raw, archive_identity = _matrix_asset(
        matrix_root, artifacts.get("archive"), "route edge archive"
    )
    checksum_source, checksum_raw, checksum_identity = _matrix_asset(
        matrix_root, artifacts.get("checksum"), "route edge checksum"
    )
    manifest_source, manifest_raw, manifest_identity = _matrix_asset(
        matrix_root, artifacts.get("manifest"), "route edge manifest"
    )
    _validator_source, validator_raw, validator_identity = _matrix_asset(
        matrix_root, artifacts.get("validator"), "route edge validator"
    )
    if not _checksum_binds_archive(checksum_raw, archive_raw, archive_source.name):
        raise _route_error("route edge checksum bytes do not bind the archive")
    hop_root = route_root / ROUTE_HOP_DIRECTORY / f"{hop_index:04d}"
    if hop_root.exists() or hop_root.is_symlink() or APPLY.is_reparse_point(hop_root):
        raise _route_error("route hop package evidence already exists")
    archive_path = hop_root / archive_source.name
    extracted_root = hop_root / "extracted"
    hop_root.mkdir(parents=True, exist_ok=False)
    APPLY.atomic_write_bytes(archive_path, archive_raw)
    APPLY.atomic_write_bytes(hop_root / "checksum.sha256", checksum_raw)
    APPLY.atomic_write_bytes(hop_root / "migration.yaml", manifest_raw)
    # The external source validator executes only during preparation, but its
    # exact bytes remain as promoted evidence for later target-side review.
    APPLY.atomic_write_bytes(hop_root / "validator.asset", validator_raw)
    members = _safe_archive_members(archive_path)
    envelope_roots = {PurePosixPath(name).parts[0] for name in members}
    if len(envelope_roots) != 1:
        raise _route_error("route edge archive has no unique package envelope")
    envelope = next(iter(envelope_roots))
    for name, (content, mode) in sorted(members.items(), key=lambda item: item[0].encode("utf-8")):
        relative = _safe_relative(name, "validated route package member")
        destination = extracted_root / Path(*PurePosixPath(relative).parts)
        APPLY.atomic_write_bytes(destination, content, mode)
    package_root = extracted_root / envelope
    try:
        package, _incoming, _migration, package_manifest_sha = APPLY.validate_package_root(package_root)
    except APPLY.ApplyError as exc:
        raise _route_error(f"materialized route package is invalid: {exc}") from exc
    migration_raw = _read_regular(package_root / "metadata/migration.yaml", "materialized package migration")
    if migration_raw != manifest_raw or APPLY.sha256_bytes(migration_raw) != manifest_identity["sha256"]:
        raise _route_error("route edge manifest differs from materialized package migration")
    return {
        "archive_path": (Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / archive_source.name).as_posix(),
        "archive_sha256": APPLY.sha256_bytes(archive_raw),
        "checksum_sha256": checksum_identity["sha256"],
        "migration_artifact_sha256": manifest_identity["sha256"],
        "validator_path": (Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "validator.asset").as_posix(),
        "validator_artifact_sha256": validator_identity["sha256"],
        "extracted_root": (Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "extracted" / envelope).as_posix(),
        "package_id": package.get("package_id"),
        "package_version": package.get("version"),
        "package_manifest_sha256": package_manifest_sha,
        "migration_sha256": APPLY.sha256_bytes(migration_raw),
        "files_manifest_sha256": APPLY.sha256_bytes(
            _read_regular(package_root / "metadata/files.yaml", "materialized package files manifest")
        ),
    }


def _execute_edge_validator(
    route_root: Path, matrix_root: Path, edge: dict, hop_index: int
) -> dict:
    validation = edge.get("validation")
    artifacts = edge.get("artifacts")
    if not isinstance(validation, dict) or not isinstance(artifacts, dict):
        raise _route_error("route edge validation contract is invalid")
    argv = validation.get("validator_argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
        raise _route_error("route edge validator argv is invalid")
    _validator_path, validator_raw, validator = _matrix_asset(
        matrix_root, artifacts.get("validator"), "route edge validator"
    )
    if validator.get("path") not in argv or argv.count(validator["path"]) != 1:
        raise _route_error("route edge validator argv does not bind its exact asset")
    _output_path, expected_output, output = _matrix_asset(
        matrix_root, validation.get("output"), "route edge validator expected output"
    )
    execution_root = route_root / ROUTE_HOP_DIRECTORY / f"{hop_index:04d}"
    if execution_root.is_symlink() or APPLY.is_reparse_point(execution_root) or not execution_root.is_dir():
        raise _route_error("route hop evidence root is missing or unsafe")
    stdout_path = execution_root / "validator.stdout.log"
    stderr_path = execution_root / "validator.stderr.log"
    record_path = execution_root / "validator-execution.json"
    try:
        result = subprocess.run(
            list(argv),
            cwd=matrix_root,
            check=False,
            shell=False,
            capture_output=True,
            timeout=60,
        )
        stdout = result.stdout
        stderr = result.stderr
        return_code = result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        stdout = b""
        stderr = str(exc).encode("utf-8", errors="replace")
        return_code = None
    # The command ran from the external matrix root.  Do not attribute that
    # execution to a sealed validator asset unless its declared bytes still
    # match after the subprocess returns.  Preserve argv verbatim in the
    # eventual evidence rather than rewriting it to a copied path.
    _validator_after_path, validator_after_raw, validator_after = _matrix_asset(
        matrix_root, artifacts.get("validator"), "route edge validator after execution"
    )
    _output_after_path, expected_output_after, output_after = _matrix_asset(
        matrix_root,
        validation.get("output"),
        "route edge validator expected output after execution",
    )
    if (
        validator_after != validator
        or validator_after_raw != validator_raw
        or output_after != output
        or expected_output_after != expected_output
    ):
        raise _route_error("route edge validator assets changed during execution")
    APPLY.atomic_write_bytes(stdout_path, stdout)
    APPLY.atomic_write_bytes(stderr_path, stderr)
    record = {
        "schema_version": "multi-hop-edge-validator-execution/v1",
        "hop_index": hop_index,
        "edge_id": edge.get("edge_id"),
        "validator_argv": list(argv),
        "validator_sha256": APPLY.sha256_bytes(validator_raw),
        "expected_output_sha256": output.get("sha256"),
        "stdout_sha256": APPLY.sha256_bytes(stdout),
        "stderr_sha256": APPLY.sha256_bytes(stderr),
        "return_code": return_code,
        "outcome": "passed"
        if return_code == 0 and not stderr and stdout == expected_output
        else "failed",
    }
    record_sha = _write_json(record_path, record)
    if record["outcome"] != "passed":
        raise _route_error("route edge validator execution did not match exact retained output")
    return {
        "record_path": (Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "validator-execution.json").as_posix(),
        "record_sha256": record_sha,
        "stdout_path": (Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "validator.stdout.log").as_posix(),
        "stdout_sha256": record["stdout_sha256"],
    }


def _checkpoint_path(route_root: Path, index: int) -> Path:
    return route_root / ROUTE_CHECKPOINT_DIRECTORY / f"{index:04d}.json"


def _read_checkpoint(route_root: Path, index: int) -> tuple[dict, str]:
    checkpoint, raw = _read_canonical_json(_checkpoint_path(route_root, index), "multi-hop route checkpoint")
    unsigned = deepcopy(checkpoint)
    if unsigned.pop("digest", None) != _canonical_digest(unsigned):
        raise _route_error("multi-hop route checkpoint digest is invalid")
    return checkpoint, APPLY.sha256_bytes(raw)


def _next_context(route_root: Path, intent: dict, journal: dict) -> dict:
    index = journal["next_hop_index"]
    if index == 0:
        edge = intent["route"]["edges"][0]
        return {
            "schema_version": APPLY.MULTI_HOP_INITIAL_ROUTE_CONTEXT_SCHEMA_VERSION,
            "route_transaction_id": intent["route_transaction_id"],
            "route_intent_sha256": APPLY.sha256_bytes(_canonical_json_bytes(intent)),
            "next_hop_index": 0,
            "edge_id": edge["edge_id"],
            "edge_order": edge["order"],
            "from_version": edge["from_version"],
            "to_version": edge["to_version"],
        }
    checkpoint, checkpoint_sha = _read_checkpoint(route_root, index - 1)
    edge = intent["route"]["edges"][index]
    if checkpoint.get("edge") != intent["route"]["edges"][index - 1]:
        raise _route_error("preceding route checkpoint edge differs")
    return {
        "schema_version": APPLY.MULTI_HOP_ROUTE_CONTEXT_SCHEMA_VERSION,
        "route_transaction_id": intent["route_transaction_id"],
        "route_intent_sha256": APPLY.sha256_bytes(_canonical_json_bytes(intent)),
        "checkpoint_index": index - 1,
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_predecessor_sha256": checkpoint.get("predecessor_checkpoint_sha256"),
        "next_hop_index": index,
        "edge_id": edge["edge_id"],
        "edge_order": edge["order"],
        "from_version": edge["from_version"],
        "to_version": edge["to_version"],
    }


def _package_root(route_root: Path, package: dict) -> Path:
    relative = _safe_relative(package.get("extracted_root"), "route materialized package root")
    return route_root / Path(*PurePosixPath(relative).parts)


def _previous_files_for_hop(
    target: Path,
    route_root: Path,
    journal: dict,
    *,
    initial_previous_files_path: Path | None,
    initial_previous_version: str | None,
    context: dict,
) -> tuple[Path, str]:
    index = journal["next_hop_index"]
    if index == 0:
        if initial_previous_files_path is None or initial_previous_version is None:
            raise _route_error("first route hop requires exact previous files and previous version")
        if initial_previous_files_path.is_symlink() or not initial_previous_files_path.is_file():
            raise _route_error("first route hop previous files must be a regular file")
        return initial_previous_files_path.resolve(), initial_previous_version
    # The caller holds the same plan-admission snapshot that build_plan reuses,
    # so the complete retained checkpoint is admitted before reading any
    # predecessor package bytes without creating another Git snapshot.
    APPLY.verify_multi_hop_checkpoint_for_planning(target, context)
    checkpoint, _ = _read_checkpoint(route_root, index - 1)
    package = checkpoint.get("package")
    if not isinstance(package, dict):
        raise _route_error("preceding route checkpoint package identity is invalid")
    package_root = _package_root(route_root, package)
    files = package_root / "metadata/files.yaml"
    expected = package.get("files_manifest_sha256")
    if APPLY.sha256_bytes(_read_regular(files, "preceding route package files manifest")) != expected:
        raise _route_error("preceding route package files manifest differs")
    edge = checkpoint.get("edge")
    if not isinstance(edge, dict) or not isinstance(edge.get("to_version"), str):
        raise _route_error("preceding route checkpoint edge is invalid")
    return files, edge["to_version"]


def _planned_hop_path(hop_index: int) -> str:
    return (
        Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / ROUTE_PREPARATION_PATH
    ).as_posix()


def _hop_root(route_root: Path, hop_index: int) -> Path:
    if type(hop_index) is not int or hop_index < 0:
        raise _route_error("route hop index is invalid")
    return route_root / ROUTE_HOP_DIRECTORY / f"{hop_index:04d}"


def _hop_evidence_path(hop_index: int) -> str:
    return (
        Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / ROUTE_HOP_EVIDENCE_PATH
    ).as_posix()


def _rebase_plan_package_root(plan: dict, route_root: Path, package: dict) -> dict:
    """Bind a staged package plan to the final immutable route-admin path."""
    try:
        APPLY.plan_digest(plan)
    except APPLY.ApplyError as exc:
        raise _route_error(f"staged route child plan is invalid: {exc}") from exc
    rebased = deepcopy(plan)
    rebased["package_root"] = str(_package_root(route_root, package))
    unsigned = deepcopy(rebased)
    unsigned.pop("plan_sha256", None)
    rebased["plan_sha256"] = APPLY.canonical_digest(unsigned)
    return rebased


def _write_hop_evidence(
    route_root: Path,
    hop_index: int,
    edge: dict,
    package: dict,
    execution: dict,
    plan: dict,
) -> str:
    evidence = {
        "schema_version": "multi-hop-prepared-hop/v1",
        "hop_index": hop_index,
        "edge": deepcopy(_edge_identity(edge)),
        "package": deepcopy(package),
        "validator_execution": deepcopy(execution),
        "plan_sha256": APPLY.plan_digest(plan),
    }
    path = route_root / Path(*PurePosixPath(_hop_evidence_path(hop_index)).parts)
    if path.exists() or path.is_symlink() or APPLY.is_reparse_point(path):
        raise _route_error("route prepared-hop evidence already exists")
    return _write_json(path, evidence)


def _validate_prepared_hop(
    route_root: Path, hop_index: int, edge: dict
) -> tuple[dict, dict, dict, str, str]:
    """Re-open only exact promoted preparation evidence for an interrupted retry."""
    hop_root = _hop_root(route_root, hop_index)
    if hop_root.is_symlink() or APPLY.is_reparse_point(hop_root) or not hop_root.is_dir():
        raise _route_error("route prepared-hop evidence is missing or unsafe")
    evidence_path = hop_root / ROUTE_HOP_EVIDENCE_PATH
    evidence, _ = _read_canonical_json(evidence_path, "route prepared-hop evidence")
    if (
        set(evidence)
        != {"schema_version", "hop_index", "edge", "package", "validator_execution", "plan_sha256"}
        or evidence.get("schema_version") != "multi-hop-prepared-hop/v1"
        or evidence.get("hop_index") != hop_index
        or evidence.get("edge") != _expected_edge_identity(edge, "prepared route edge")
        or not isinstance(evidence.get("package"), dict)
        or not isinstance(evidence.get("validator_execution"), dict)
    ):
        raise _route_error("route prepared-hop evidence identity is invalid")
    plan_sha = _require_sha256(evidence.get("plan_sha256"), "prepared-hop plan SHA-256")
    proposal_path = route_root / Path(*PurePosixPath(_planned_hop_path(hop_index)).parts)
    proposal_sha = APPLY.sha256_bytes(
        _read_regular(proposal_path, "route prepared-hop proposal plan")
    )
    plan = _load_planned_hop(route_root, hop_index, plan_sha, proposal_sha)
    if plan.get("package_root") != str(_package_root(route_root, evidence["package"])):
        raise _route_error("route prepared-hop plan package root differs")
    package = evidence["package"]
    archive_relative = _safe_relative(package.get("archive_path"), "prepared route archive path")
    archive_raw = _read_regular(
        route_root / Path(*PurePosixPath(archive_relative).parts), "prepared route archive"
    )
    if APPLY.sha256_bytes(archive_raw) != package.get("archive_sha256"):
        raise _route_error("prepared route archive bytes differ")
    checksum_raw = _read_regular(hop_root / "checksum.sha256", "prepared route checksum")
    if (
        APPLY.sha256_bytes(checksum_raw) != package.get("checksum_sha256")
        or not _checksum_binds_archive(
            checksum_raw, archive_raw, Path(archive_relative).name
        )
    ):
        raise _route_error("prepared route checksum evidence differs")
    migration_artifact = _read_regular(
        hop_root / "migration.yaml", "prepared route migration artifact"
    )
    expected_validator_relative = (
        Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "validator.asset"
    ).as_posix()
    validator_relative = _safe_relative(
        package.get("validator_path"), "prepared route validator path"
    )
    if validator_relative != expected_validator_relative:
        raise _route_error("prepared route validator path differs")
    validator_raw = _read_regular(
        route_root / Path(*PurePosixPath(validator_relative).parts),
        "prepared route validator asset",
    )
    if APPLY.sha256_bytes(validator_raw) != package.get("validator_artifact_sha256"):
        raise _route_error("prepared route validator asset differs")
    package_root = _package_root(route_root, package)
    try:
        package_document, _incoming, _migration, manifest_sha = APPLY.validate_package_root(package_root)
    except APPLY.ApplyError as exc:
        raise _route_error(f"prepared route package is invalid: {exc}") from exc
    migration_raw = _read_regular(
        package_root / "metadata/migration.yaml", "prepared route package migration"
    )
    if (
        package.get("package_manifest_sha256") != manifest_sha
        or package.get("migration_sha256") != APPLY.sha256_bytes(migration_raw)
        or package.get("migration_artifact_sha256")
        != APPLY.sha256_bytes(migration_artifact)
        or migration_artifact != migration_raw
        or package.get("files_manifest_sha256")
        != APPLY.sha256_bytes(
            _read_regular(package_root / "metadata/files.yaml", "prepared route files manifest")
        )
        or package.get("package_id") != package_document.get("package_id")
        or package.get("package_version") != package_document.get("version")
    ):
        raise _route_error("prepared route package identity differs")
    execution = evidence["validator_execution"]
    expected_record_path = (
        Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "validator-execution.json"
    ).as_posix()
    expected_stdout_path = (
        Path(ROUTE_HOP_DIRECTORY) / f"{hop_index:04d}" / "validator.stdout.log"
    ).as_posix()
    expected_stderr_path = hop_root / "validator.stderr.log"
    _require_sha256(execution.get("record_sha256"), "prepared validator record SHA-256")
    _require_sha256(execution.get("stdout_sha256"), "prepared validator output SHA-256")
    if (
        set(execution) != {"record_path", "record_sha256", "stdout_path", "stdout_sha256"}
        or execution.get("record_path") != expected_record_path
        or execution.get("stdout_path") != expected_stdout_path
    ):
        raise _route_error("prepared route validator execution identity is invalid")
    record_relative = _safe_relative(execution.get("record_path"), "prepared validator record path")
    record, record_raw = _read_canonical_json(
        route_root / Path(*PurePosixPath(record_relative).parts), "prepared route validator record"
    )
    stdout_relative = _safe_relative(execution.get("stdout_path"), "prepared validator output path")
    stdout = _read_regular(
        route_root / Path(*PurePosixPath(stdout_relative).parts), "prepared route validator output"
    )
    stderr = _read_regular(expected_stderr_path, "prepared route validator error output")
    validation = edge.get("validation")
    artifacts = edge.get("artifacts")
    if (
        not isinstance(validation, dict)
        or not isinstance(artifacts, dict)
        or set(record)
        != {
            "schema_version",
            "hop_index",
            "edge_id",
            "validator_argv",
            "validator_sha256",
            "expected_output_sha256",
            "stdout_sha256",
            "stderr_sha256",
            "return_code",
            "outcome",
        }
        or record.get("schema_version") != "multi-hop-edge-validator-execution/v1"
        or APPLY.sha256_bytes(record_raw) != execution.get("record_sha256")
        or APPLY.sha256_bytes(stdout) != execution.get("stdout_sha256")
        or APPLY.sha256_bytes(stderr) != record.get("stderr_sha256")
        or record.get("outcome") != "passed"
        or type(record.get("return_code")) is not int
        or record.get("return_code") != 0
        or stderr != b""
        or record.get("hop_index") != hop_index
        or record.get("edge_id") != edge.get("edge_id")
        or not isinstance(record.get("validator_argv"), list)
        or not all(isinstance(item, str) and item for item in record["validator_argv"])
        or record.get("validator_argv") != validation.get("validator_argv")
        or record.get("validator_sha256") != artifacts.get("validator", {}).get("sha256")
        or package.get("validator_artifact_sha256")
        != artifacts.get("validator", {}).get("sha256")
        or record.get("expected_output_sha256") != validation.get("output", {}).get("sha256")
        or record.get("stdout_sha256") != execution.get("stdout_sha256")
        or record.get("expected_output_sha256") != record.get("stdout_sha256")
    ):
        raise _route_error("prepared route validator evidence differs")
    return package, execution, plan, plan_sha, proposal_sha


def _validate_active_prepared_hop(
    route_root: Path, intent: dict, journal: dict, active: dict
) -> tuple[dict, dict, dict, str, str, dict]:
    """Cross-bind an owner-ready proposal to its retained route state exactly."""
    index = journal.get("next_hop_index")
    if (
        type(index) is not int
        or not isinstance(active.get("hop_index"), int)
        or active.get("hop_index") != index
        or index < 0
        or index >= len(intent.get("route", {}).get("edges", []))
        or active.get("edge") != intent["route"]["edges"][index]
    ):
        raise _route_error("multi-hop route active hop identity differs")
    expected_context = _next_context(route_root, intent, journal)
    full_edge = _resolve_sealed_route_edges(route_root, intent)[index]
    package, execution, plan, plan_sha, proposal_sha = _validate_prepared_hop(
        route_root, index, full_edge
    )
    if (
        plan_sha != active.get("plan_sha256")
        or proposal_sha != active.get("proposal_plan_sha256")
        or APPLY.plan_digest(plan) != plan_sha
        or active.get("package") != package
        or active.get("validator_execution") != execution
        or APPLY.route_checkpoint_context(plan) != expected_context
    ):
        raise _route_error("multi-hop prepared-hop evidence differs from active route intent")
    return package, execution, plan, plan_sha, proposal_sha, expected_context


def _revalidate_bound_hop_evidence(
    route_root: Path, intent: dict, journal: dict, active: dict
) -> None:
    """Fail closed on altered promoted evidence after child binding.

    Once a child exists the temporary proposal is intentionally gone.  The
    retained S1 result, promoted evidence, and active route binding are enough
    to reprove the exact validator contract before accepting a target receipt
    or advancing target authority.
    """
    index = journal.get("next_hop_index")
    if (
        type(index) is not int
        or index < 0
        or index >= len(intent["route"]["edges"])
        or active.get("hop_index") != index
        or active.get("edge") != intent["route"]["edges"][index]
        or not isinstance(active.get("package"), dict)
        or not isinstance(active.get("validator_execution"), dict)
    ):
        raise _route_error("bound multi-hop promoted evidence identity is invalid")
    full_edge = _resolve_sealed_route_edges(route_root, intent)[index]
    errors: list[str] = []
    TARGET.validate_promoted_multi_hop_evidence(
        route_root,
        index,
        intent["route"]["edges"][index],
        full_edge,
        active["package"],
        active["validator_execution"],
        active.get("plan_sha256"),
        errors,
    )
    if errors:
        raise _route_error(
            "bound multi-hop promoted evidence is invalid: " + "; ".join(errors)
        )


def _validate_bound_proposal(
    target: Path, route_root: Path, intent: dict, journal: dict, active: dict
) -> bool:
    """Validate the one crash-only duplicate proposal after child binding.

    A child-bound hop normally has no proposal.  The only tolerated residue is
    the exact post-journal-persist/pre-unlink crash window, whose state and
    child lifecycle must still agree with the proposal bytes.
    """
    transaction_id = active.get("child_transaction_id")
    if transaction_id is None:
        return False
    _require_sha256(transaction_id, "bound multi-hop child transaction ID")
    index = journal.get("next_hop_index")
    if (
        type(index) is not int
        or active.get("hop_index") != index
        or index < 0
        or index >= len(intent["route"]["edges"])
        or active.get("edge") != intent["route"]["edges"][index]
        or active.get("plan_sha256") != transaction_id
        or not isinstance(active.get("package"), dict)
    ):
        raise _route_error("bound multi-hop proposal active identity is invalid")
    proposal_path = route_root / Path(*PurePosixPath(_planned_hop_path(index)).parts)
    if proposal_path.is_symlink() or APPLY.is_reparse_point(proposal_path):
        raise _route_error("bound multi-hop proposal path is unsafe")
    if not proposal_path.exists():
        return False
    if journal.get("state") not in {"awaiting-target-validation", "finalizing"}:
        raise _route_error("bound multi-hop proposal exists outside its crash recovery state")
    proposal = _load_planned_hop(
        route_root,
        index,
        transaction_id,
        active.get("proposal_plan_sha256"),
    )
    expected_context = _next_context(route_root, intent, journal)
    package = active["package"]
    try:
        package_root = _package_root(route_root, package)
    except MultiHopUpgradeError:
        raise
    if (
        APPLY.plan_digest(proposal) != transaction_id
        or APPLY.route_checkpoint_context(proposal) != expected_context
        or proposal.get("package_root") != str(package_root)
        or proposal.get("package_manifest_sha256")
        != package.get("package_manifest_sha256")
        or proposal.get("migration_sha256") != package.get("migration_sha256")
    ):
        raise _route_error("bound multi-hop proposal differs from active child identity")
    try:
        _child_root, child_plan, child_journal = APPLY.load_transaction(
            target,
            transaction_id,
            allow_unbound_target_validation_receipt=True,
        )
    except APPLY.ApplyError as exc:
        raise _route_error(f"bound multi-hop child evidence is invalid: {exc}") from exc
    expected_child_state = (
        "awaiting-target-validation"
        if journal["state"] == "awaiting-target-validation"
        else "validated"
    )
    if (
        child_plan != proposal
        or APPLY.plan_digest(child_plan) != transaction_id
        or APPLY.route_checkpoint_context(child_plan) != expected_context
        or child_journal.get(APPLY.MULTI_HOP_ROUTE_CONTEXT_KEY) != expected_context
        or child_journal.get("state") != expected_child_state
    ):
        raise _route_error("bound multi-hop proposal differs from child transaction")
    return True


def _cleanup_bound_proposal(
    target: Path, route_root: Path, intent: dict, journal: dict
) -> None:
    active = journal.get("active_hop")
    if not isinstance(active, dict) or active.get("child_transaction_id") is None:
        return
    if _validate_bound_proposal(target, route_root, intent, journal, active):
        _remove_planned_hop(route_root, journal["next_hop_index"])


def _require_valid_retained_route(target: Path, label: str) -> None:
    """Do not return a resumable sealed route until target-side validation agrees."""
    errors: list[str] = []
    TARGET.validate_multi_hop_route_transactions(target, errors)
    if errors:
        raise _route_error(f"{label} is invalid: " + "; ".join(errors))


def _restore_unbound_active_child(
    target: Path, route_root: Path, intent: dict, journal: dict, active: dict
) -> dict:
    """Recover the bounded crash window after child creation before outer binding.

    The only derivation is the already-sealed semantic plan digest.  The child
    must prove that same plan, retained package, and route context before the
    missing outer fields are restored.
    """
    index = journal.get("next_hop_index")
    plan_sha = active.get("plan_sha256")
    if (
        type(index) is not int
        or active.get("hop_index") != index
        or index < 0
        or index >= len(intent["route"]["edges"])
        or active.get("edge") != intent["route"]["edges"][index]
        or active.get("child_transaction_id") is not None
        or not isinstance(active.get("package"), dict)
    ):
        raise _route_error("interrupted multi-hop active hop identity is invalid")
    _require_sha256(plan_sha, "interrupted multi-hop child plan SHA-256")
    assert isinstance(plan_sha, str)
    package = active["package"]
    expected_context = _next_context(route_root, intent, journal)
    child_root = APPLY.transaction_root(target, plan_sha)
    if child_root.is_symlink() or APPLY.is_reparse_point(child_root) or not child_root.is_dir():
        _validate_active_prepared_hop(route_root, intent, journal, active)
        raise _route_error("interrupted multi-hop route lacks the derived child transaction")
    try:
        _loaded_root, child_plan, child_journal = APPLY.load_transaction(
            target,
            plan_sha,
            allow_unbound_target_validation_receipt=True,
        )
    except APPLY.ApplyError as exc:
        raise _route_error(f"interrupted multi-hop child evidence is invalid: {exc}") from exc
    if (
        APPLY.plan_digest(child_plan) != plan_sha
        or APPLY.route_checkpoint_context(child_plan) != expected_context
        or child_journal.get(APPLY.MULTI_HOP_ROUTE_CONTEXT_KEY) != expected_context
        or child_plan.get("package_root") != str(_package_root(route_root, package))
        or child_plan.get("package_manifest_sha256")
        != package.get("package_manifest_sha256")
        or child_plan.get("migration_sha256") != package.get("migration_sha256")
    ):
        raise _route_error("interrupted multi-hop child plan differs from route proposal")
    child_state = child_journal.get("state")
    proposal_path = route_root / Path(*PurePosixPath(_planned_hop_path(index)).parts)
    if proposal_path.is_symlink() or APPLY.is_reparse_point(proposal_path):
        raise _route_error("interrupted multi-hop proposal path is unsafe")
    if child_state in {"applying", "interrupted"}:
        _validate_active_prepared_hop(route_root, intent, journal, active)
        try:
            APPLY.recover_transaction_locked(
                target,
                plan_sha,
                "resume",
                _package_root(route_root, package),
                None,
            )
            _loaded_root, child_plan, child_journal = APPLY.load_transaction(
                target,
                plan_sha,
                allow_unbound_target_validation_receipt=True,
            )
        except APPLY.ApplyError as exc:
            raise _route_error(f"interrupted multi-hop child resume failed: {exc}") from exc
        child_state = child_journal.get("state")
    if child_state == "rejected":
        # The child itself is now the authoritative zero-mutation evidence.
        # A crash may already have deleted the temporary proposal, so require
        # it only when bytes still exist; retained bytes must still match.
        if proposal_path.exists():
            _validate_active_prepared_hop(route_root, intent, journal, active)
        rejected_errors: list[str] = []
        TARGET.validate_rejected_upgrade_transaction(
            target, plan_sha, child_journal, rejected_errors
        )
        if rejected_errors:
            raise _route_error(
                "interrupted rejected multi-hop child evidence is invalid: "
                + "; ".join(rejected_errors)
            )
        _remove_planned_hop(route_root, journal["next_hop_index"])
        journal["state"] = (
            "checkpointed" if journal["last_checkpoint_index"] is not None else "planned"
        )
        journal["active_hop"] = None
        _persist_route_journal(route_root, intent, journal)
        return {
            "route_transaction_id": intent["route_transaction_id"],
            "state": journal["state"],
            "next_hop_index": journal["next_hop_index"],
            "resumable": True,
            "recovered_owner_rejection": True,
        }
    _validate_active_prepared_hop(route_root, intent, journal, active)
    if child_state not in {"awaiting-target-validation", "validated"} or not isinstance(
        child_journal.get("final_receipt_sha256"), str
    ):
        raise _route_error("interrupted multi-hop child has no recoverable pending validation receipt")
    _require_sha256(child_journal["final_receipt_sha256"], "interrupted multi-hop child pending receipt SHA-256")
    active["child_transaction_id"] = plan_sha
    active["pending_receipt_sha256"] = child_journal["final_receipt_sha256"]
    active["child_evidence_path"] = f"ai-context-package-apply/{plan_sha}"
    journal["state"] = (
        "finalizing" if child_state == "validated" else "awaiting-target-validation"
    )
    _persist_route_journal(route_root, intent, journal)
    _remove_planned_hop(route_root, journal["next_hop_index"])
    return {
        "route_transaction_id": intent["route_transaction_id"],
        "state": journal["state"],
        "next_hop_index": journal["next_hop_index"],
        "resumable": True,
        "recovered_child_transaction_id": plan_sha,
    }


def _preserve_failed_preparation(route_root: Path, preparation: Path, exc: BaseException) -> None:
    """Retain an interrupted/failed attempt without presenting it as an active hop."""
    if not preparation.exists() or preparation.is_symlink() or APPLY.is_reparse_point(preparation):
        return
    try:
        _write_json(
            preparation / "failure.json",
            {
                "schema_version": "multi-hop-preparation-failure/v1",
                "exception_type": type(exc).__name__,
                "message": str(exc),
            },
        )
        failed_root = route_root / ROUTE_FAILED_PREPARING_DIRECTORY
        failed_root.mkdir(parents=True, exist_ok=True)
        destination = failed_root / preparation.name
        if destination.exists() or destination.is_symlink() or APPLY.is_reparse_point(destination):
            raise _route_error("route failed-preparation destination already exists")
        os.replace(preparation, destination)
        APPLY.fsync_directory(failed_root)
    except Exception:
        # The original failure remains authoritative; do not mask it with a
        # best-effort evidence-retention failure.
        return


def _write_planned_hop(route_root: Path, hop_index: int, plan: dict) -> str:
    """Persist a pre-decision proposal only until the child transaction exists."""
    path = route_root / Path(*PurePosixPath(_planned_hop_path(hop_index)).parts)
    if path.exists() or path.is_symlink() or APPLY.is_reparse_point(path):
        raise _route_error("multi-hop route proposal plan already exists")
    return _write_json(path, plan)


def _load_planned_hop(
    route_root: Path,
    hop_index: int,
    expected_plan_sha: str,
    expected_proposal_sha: str,
) -> dict:
    path = route_root / Path(*PurePosixPath(_planned_hop_path(hop_index)).parts)
    plan, raw = _read_canonical_json(path, "multi-hop route proposal plan")
    if (
        APPLY.sha256_bytes(raw) != expected_proposal_sha
        or plan.get("plan_sha256") != expected_plan_sha
    ):
        raise _route_error("multi-hop route proposal plan identity differs")
    return plan


def _remove_planned_hop(route_root: Path, hop_index: int) -> None:
    path = route_root / Path(*PurePosixPath(_planned_hop_path(hop_index)).parts)
    if path.exists():
        # The sealed child plan now exists in ai-context-package-apply.  This
        # temporary proposal is intentionally not duplicate route evidence.
        APPLY.durable_unlink(path, route_root)


def _prepare_or_reuse_hop(
    target: Path,
    route_root: Path,
    intent: dict,
    journal: dict,
    edge: dict,
    *,
    matrix_root: Path,
    previous_files: Path,
    previous_version: str,
    context: dict | None,
) -> tuple[dict, dict, dict, str]:
    """Promote one sealed preparation atomically or reopen its exact retry form."""
    hop_index = journal["next_hop_index"]
    promoted = _hop_root(route_root, hop_index)
    if promoted.exists() or promoted.is_symlink() or APPLY.is_reparse_point(promoted):
        package, execution, plan, _plan_sha, proposal_sha = _validate_prepared_hop(
            route_root, hop_index, edge
        )
        return package, execution, plan, proposal_sha
    preparing_root = route_root / ROUTE_PREPARING_DIRECTORY
    preparing_root.mkdir(parents=True, exist_ok=True)
    preparation = Path(
        tempfile.mkdtemp(prefix=f"{hop_index:04d}-", dir=preparing_root)
    )
    try:
        package = _materialize_package(preparation, matrix_root, edge, hop_index)
        execution = _execute_edge_validator(preparation, matrix_root, edge, hop_index)
        try:
            staged_plan = APPLY.build_plan(
                _package_root(preparation, package),
                target,
                previous_files,
                previous_version,
                multi_hop_checkpoint_context=context,
            )
        except APPLY.ApplyError as exc:
            raise _route_error(f"route child plan was rejected: {exc}") from exc
        plan = _rebase_plan_package_root(staged_plan, route_root, package)
        proposal_sha = _write_planned_hop(preparation, hop_index, plan)
        _write_hop_evidence(preparation, hop_index, edge, package, execution, plan)
        staged_hop = _hop_root(preparation, hop_index)
        promoted.parent.mkdir(parents=True, exist_ok=True)
        if promoted.exists() or promoted.is_symlink() or APPLY.is_reparse_point(promoted):
            raise _route_error("route prepared-hop promotion destination already exists")
        os.replace(staged_hop, promoted)
        APPLY.fsync_directory(promoted.parent)
        try:
            preparation.rmdir()
        except OSError:
            pass
        return package, execution, plan, proposal_sha
    except Exception as exc:
        _preserve_failed_preparation(route_root, preparation, exc)
        raise


def begin_multi_hop_upgrade(
    target_root: Path,
    matrix_path: Path,
    *,
    origin: str,
    target_version: str,
) -> dict:
    """Create one sealed, route-only transaction for an S1 multi-hop route."""
    target = target_root.resolve()
    matrix_path = matrix_path.resolve()
    result = ROUTES.resolve_matrix_file(matrix_path, origin=origin, target=target_version)
    matrix_raw = _read_regular(matrix_path, "route matrix")
    resolver_result = _normalized_resolver_result(
        result, matrix_raw, origin=origin, target=target_version
    )
    selected = resolver_result["selected_route"]
    edges = [_edge_identity(item) for item in selected["edges"]]
    matrix = resolver_result["matrix"]
    resolver_result_raw = _canonical_json_bytes(resolver_result)
    resolver_result_identity = {
        "path": ROUTE_RESOLVER_RESULT_PATH,
        "sha256": APPLY.sha256_bytes(resolver_result_raw),
        "byte_length": len(resolver_result_raw),
    }
    with APPLY.transaction_lock(target):
        # Read the target identity and derive the route ID while holding the
        # same lock used by every child transition.  This prevents a plan from
        # being sealed against a HEAD observed before another transition.
        head = APPLY.clean_target_head(target)
        seed = {
            "schema_version": APPLY.MULTI_HOP_ROUTE_INTENT_SCHEMA_VERSION,
            "target_root": str(target),
            "target_starting_commit": head,
            "origin": result.get("origin"),
            "target": result.get("target"),
            "matrix": {
                "path": ROUTE_MATRIX_PATH,
                "sha256": matrix["sha256"],
                "byte_length": matrix["byte_length"],
            },
            "resolver_result": resolver_result_identity,
            "route": {"route_id": selected.get("route_id"), "edges": edges},
        }
        route_transaction_id = _canonical_digest(seed)
        intent = {"route_transaction_id": route_transaction_id, **seed}
        intent_sha = APPLY.sha256_bytes(_canonical_json_bytes(intent))
        journal = {
            "schema_version": APPLY.MULTI_HOP_ROUTE_JOURNAL_SCHEMA_VERSION,
            "route_transaction_id": route_transaction_id,
            "route_intent_sha256": intent_sha,
            "target_root": str(target),
            "target_starting_commit": head,
            "state": "planned",
            "next_hop_index": 0,
            "last_checkpoint_index": None,
            "last_checkpoint_sha256": None,
            "active_hop": None,
        }
        base = APPLY.git_admin_multi_hop_route_base(target)
        base.mkdir(parents=True, exist_ok=True)
        route_root = base / route_transaction_id
        if route_root.exists() or route_root.is_symlink() or APPLY.is_reparse_point(route_root):
            raise _route_error("multi-hop route transaction already exists")
        preparation = Path(tempfile.mkdtemp(prefix=f".{route_transaction_id}.preparing-", dir=base))
        try:
            _write_json(preparation / ROUTE_INTENT_PATH, intent)
            APPLY.atomic_write_bytes(preparation / ROUTE_MATRIX_PATH, matrix_raw)
            APPLY.atomic_write_bytes(
                preparation / ROUTE_RESOLVER_RESULT_PATH, resolver_result_raw
            )
            _write_journal(preparation / ROUTE_JOURNAL_PATH, journal)
            APPLY.fsync_directory(preparation)
            os.replace(preparation, route_root)
            APPLY.fsync_directory(base)
        except Exception:
            if preparation.exists():
                shutil.rmtree(preparation)
            raise
    return {
        "route_transaction_id": route_transaction_id,
        "route_intent_sha256": intent_sha,
        "route_kind": result["route_kind"],
        "route_id": selected["route_id"],
        "edge_count": len(edges),
    }


def prepare_next_hop(
    target_root: Path,
    route_transaction_id: str,
    *,
    matrix_root: Path,
    initial_previous_files_path: Path | None = None,
    initial_previous_version: str | None = None,
) -> dict:
    """Seal exact package and route-validator evidence before owner decision."""
    target = target_root.resolve()
    matrix_root = matrix_root.resolve()
    admission_snapshot = APPLY.capture_target_git_snapshot(
        target,
        [],
        phase="plan-admission",
        require_clean=False,
    )
    with APPLY.target_git_snapshot_scope(admission_snapshot), APPLY.transaction_lock(target):
        admission_snapshot.changed_paths(full_worktree_scan=True)
        route_root, intent, journal = _load_route(target, route_transaction_id)
        if journal["state"] not in {"planned", "checkpointed", "rolled-back"} or journal["active_hop"] is not None:
            raise _route_error("multi-hop route is not ready to prepare its next hop")
        index = journal["next_hop_index"]
        edges = intent["route"]["edges"]
        if index >= len(edges):
            raise _route_error("multi-hop route has no remaining hop")
        resolved_edges = _resolve_prepare_route_edges(route_root, intent, matrix_root)
        context = _next_context(route_root, intent, journal)
        if context is None:
            raise _route_error("multi-hop route has no sealed context for its next hop")
        previous_files, previous_version = _previous_files_for_hop(
            target,
            route_root,
            journal,
            initial_previous_files_path=initial_previous_files_path,
            initial_previous_version=initial_previous_version,
            context=context,
        )
        package, execution, plan, proposal_sha = _prepare_or_reuse_hop(
            target,
            route_root,
            intent,
            journal,
            resolved_edges[index],
            matrix_root=matrix_root,
            previous_files=previous_files,
            previous_version=previous_version,
            context=context,
        )
        plan_sha = APPLY.plan_digest(plan)
        active = {
            "hop_index": index,
            "edge": edges[index],
            "package": package,
            "validator_execution": execution,
            "plan_sha256": plan_sha,
            "proposal_plan_sha256": proposal_sha,
            "child_transaction_id": None,
        }
        journal.update({"state": "awaiting-owner-decision", "active_hop": active})
        _persist_route_journal(route_root, intent, journal)
        packet = APPLY.build_upgrade_remediation_packet(plan)
        return {
            "route_transaction_id": route_transaction_id,
            "hop_index": index,
            "edge": deepcopy(edges[index]),
            "plan": plan,
            "remediation_packet": packet,
        }


def apply_prepared_hop(
    target_root: Path,
    route_transaction_id: str,
    remediation_decision: dict,
    *,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    """Apply one planned child only after its exact owner decision is supplied."""
    target = target_root.resolve()
    with APPLY.transaction_lock(target):
        route_root, intent, journal = _load_route(target, route_transaction_id)
        active = journal.get("active_hop")
        if journal["state"] not in {"awaiting-owner-decision", "applying"} or not isinstance(active, dict):
            raise _route_error("multi-hop route has no owner-decision-ready hop")
        index = journal["next_hop_index"]
        if active.get("hop_index") != index or active.get("edge") != intent["route"]["edges"][index]:
            raise _route_error("multi-hop route active hop identity differs")
        plan_sha = active.get("plan_sha256")
        proposal_sha = active.get("proposal_plan_sha256")
        _require_sha256(plan_sha, "multi-hop active child plan SHA-256")
        _require_sha256(proposal_sha, "multi-hop active proposal plan SHA-256")
        (
            package,
            execution,
            plan,
            prepared_plan_sha,
            prepared_proposal_sha,
            expected_route_context,
        ) = _validate_active_prepared_hop(route_root, intent, journal, active)
        transaction_id = plan_sha
        child_root = APPLY.transaction_root(target, transaction_id)
        if child_root.exists() or child_root.is_symlink() or APPLY.is_reparse_point(child_root):
            try:
                _loaded_root, child_plan, child_journal = APPLY.load_transaction(
                    target,
                    transaction_id,
                    allow_unbound_target_validation_receipt=True,
                )
            except APPLY.ApplyError as exc:
                raise _route_error(f"interrupted multi-hop child evidence is invalid: {exc}") from exc
            if (
                APPLY.plan_digest(child_plan) != plan_sha
                or APPLY.route_checkpoint_context(child_plan) != expected_route_context
                or child_journal.get(APPLY.MULTI_HOP_ROUTE_CONTEXT_KEY)
                != expected_route_context
                or child_plan.get("package_root")
                != str(_package_root(route_root, active.get("package", {})))
            ):
                raise _route_error("interrupted multi-hop child plan differs from route proposal")
            if child_journal.get("state") in {"applying", "interrupted"}:
                try:
                    APPLY.recover_transaction_locked(
                        target,
                        transaction_id,
                        "resume",
                        _package_root(route_root, active.get("package", {})),
                        boundary_hook,
                    )
                except APPLY.ApplyError as exc:
                    raise _route_error(f"interrupted multi-hop child resume failed: {exc}") from exc
                _loaded_root, child_plan, child_journal = APPLY.load_transaction(target, transaction_id)
            elif child_journal.get("state") == "rejected":
                # A rejected child is terminal evidence of an owner refusing
                # the write before target mutation.  It is not a rollback of a
                # finalized hop and must not strand the outer route in
                # rolling-back.
                _remove_planned_hop(route_root, index)
                journal["state"] = (
                    "checkpointed"
                    if journal["last_checkpoint_index"] is not None
                    else "planned"
                )
                journal["active_hop"] = None
                _persist_route_journal(route_root, intent, journal)
                return {
                    "route_transaction_id": route_transaction_id,
                    "hop_index": index,
                    "transaction_id": transaction_id,
                    "state": journal["state"],
                    "outcome": "owner-rejected-before-target-mutation",
                    "retained_child_evidence_path": f"ai-context-package-apply/{transaction_id}",
                }
            elif child_journal.get("state") not in {"awaiting-target-validation", "validated"}:
                raise _route_error("interrupted multi-hop child cannot accept the supplied owner decision")
        else:
            if journal["state"] != "applying":
                journal["state"] = "applying"
                _persist_route_journal(route_root, intent, journal)
            try:
                APPLY.apply_plan_locked(
                    plan,
                    remediation_decision=remediation_decision,
                    boundary_hook=boundary_hook,
                )
            except APPLY.ApplyError as exc:
                if not child_root.exists():
                    # A malformed, missing, or stale decision is rejected by
                    # the child before it creates durable child evidence.  Do
                    # not strand the outer route in ``applying``: retain the
                    # sealed proposal and make the next explicit owner
                    # decision/resume path truthful again.
                    journal["state"] = "awaiting-owner-decision"
                    _persist_route_journal(route_root, intent, journal)
                    raise _route_error(
                        "multi-hop child apply rejected before child transaction creation; "
                        f"an exact owner decision is still required: {exc}"
                    ) from exc
                try:
                    _loaded_root, child_plan, child_journal = APPLY.load_transaction(
                        target,
                        transaction_id,
                        allow_unbound_target_validation_receipt=True,
                    )
                except APPLY.ApplyError:
                    raise _route_error(f"multi-hop child apply failed: {exc}") from exc
                if (
                    child_journal.get("state") == "rejected"
                    and APPLY.plan_digest(child_plan) == plan_sha
                    and APPLY.route_checkpoint_context(child_plan)
                    == expected_route_context
                ):
                    _remove_planned_hop(route_root, index)
                    journal["state"] = (
                        "checkpointed"
                        if journal["last_checkpoint_index"] is not None
                        else "planned"
                    )
                    journal["active_hop"] = None
                    _persist_route_journal(route_root, intent, journal)
                    return {
                        "route_transaction_id": route_transaction_id,
                        "hop_index": index,
                        "transaction_id": transaction_id,
                        "state": journal["state"],
                        "outcome": "owner-rejected-before-target-mutation",
                        "retained_child_evidence_path": f"ai-context-package-apply/{transaction_id}",
                    }
                raise _route_error(f"multi-hop child apply failed: {exc}") from exc
            _loaded_root, child_plan, child_journal = APPLY.load_transaction(target, transaction_id)
        if (
            child_journal.get("state") not in {"awaiting-target-validation", "validated"}
            or not isinstance(child_journal.get("final_receipt_sha256"), str)
        ):
            raise _route_error("applied multi-hop child did not retain a pending validation receipt")
        active["child_transaction_id"] = transaction_id
        active["pending_receipt_sha256"] = child_journal["final_receipt_sha256"]
        active["child_evidence_path"] = f"ai-context-package-apply/{transaction_id}"
        journal["state"] = (
            "finalizing"
            if child_journal.get("state") == "validated"
            else "awaiting-target-validation"
        )
        _persist_route_journal(route_root, intent, journal)
        _remove_planned_hop(route_root, index)
        return {
            "route_transaction_id": route_transaction_id,
            "hop_index": index,
            "transaction_id": transaction_id,
            "pending_receipt_sha256": child_journal["final_receipt_sha256"],
            "child_evidence_path": f"ai-context-package-apply/{transaction_id}",
        }


def record_hop_target_validation(
    target_root: Path,
    route_transaction_id: str,
    supplied_receipt_path: Path,
    *,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    """Bind externally executed validation; this function never executes it."""
    target = target_root.resolve()
    with APPLY.transaction_lock(target):
        route_root, intent, journal = _load_route(target, route_transaction_id)
        active = journal.get("active_hop")
        if journal["state"] not in {"awaiting-target-validation", "validating"} or not isinstance(active, dict):
            raise _route_error("multi-hop route is not awaiting target validation")
        transaction_id = active.get("child_transaction_id")
        _require_sha256(transaction_id, "multi-hop active child transaction ID")
        _revalidate_bound_hop_evidence(route_root, intent, journal, active)
        journal["state"] = "validating"
        _persist_route_journal(route_root, intent, journal)
        try:
            receipt = APPLY.record_target_validation_receipt_locked(
                target,
                transaction_id,
                supplied_receipt_path,
                boundary_hook,
            )
        except APPLY.ApplyError as exc:
            raise _route_error(f"multi-hop child target validation was rejected: {exc}") from exc
        journal["state"] = "finalizing"
        _persist_route_journal(route_root, intent, journal)
        return receipt


def _child_checkpoint_evidence(
    target: Path,
    transaction_id: str,
    package: dict,
    expected_route_context: dict,
) -> tuple[dict, bytes]:
    child_root, plan, child_journal = APPLY.load_transaction(target, transaction_id)
    if (
        plan.get("schema_version") != APPLY.APPLY_PLAN_SCHEMA_VERSION
        or child_journal.get("schema_version") != APPLY.JOURNAL_SCHEMA_VERSION
        or child_journal.get("state") != "finalized"
        or child_journal.get("terminal_receipt_path") != "terminal-receipt.json"
    ):
        raise _route_error("multi-hop child is not terminally finalized")
    if (
        APPLY.route_checkpoint_context(plan) != expected_route_context
        or child_journal.get(APPLY.MULTI_HOP_ROUTE_CONTEXT_KEY)
        != expected_route_context
    ):
        raise _route_error("multi-hop child route context differs from active route hop")
    pending_path = target / APPLY.PENDING_RECEIPT_PATH
    pending_raw = _read_regular(pending_path, "multi-hop child pending receipt")
    pending_sha = APPLY.sha256_bytes(pending_raw)
    if child_journal.get("final_receipt_sha256") != pending_sha:
        raise _route_error("multi-hop child pending receipt digest differs")
    fields = {
        "transaction_id": transaction_id,
        "plan_sha256": plan.get("plan_sha256"),
        "evidence_path": f"ai-context-package-apply/{transaction_id}",
        "package_manifest_sha256": plan.get("package_manifest_sha256"),
        "migration_sha256": plan.get("migration_sha256"),
        "remediation_packet_sha256": child_journal.get("remediation_packet_sha256"),
        "remediation_decision_sha256": child_journal.get("remediation_decision_sha256"),
        "incoming_validation_receipt_sha256": child_journal.get("incoming_validation_receipt_sha256"),
        "target_validation_receipt_sha256": child_journal.get("target_validation_receipt_sha256"),
        "terminal_receipt_sha256": child_journal.get("terminal_receipt_sha256"),
    }
    for key, value in fields.items():
        if key != "evidence_path":
            _require_sha256(value, f"multi-hop child {key}")
    if fields["package_manifest_sha256"] != package.get("package_manifest_sha256") or fields["migration_sha256"] != package.get("migration_sha256"):
        raise _route_error("multi-hop child package evidence differs from route package")
    return fields, pending_raw


def _ensure_exact_route_bytes(path: Path, expected: bytes, label: str) -> None:
    """Write one route-admin byte record once, or prove its exact retry bytes."""
    if path.exists() or path.is_symlink() or APPLY.is_reparse_point(path):
        actual = _read_regular(path, label)
        if actual != expected:
            raise _route_error(f"{label} differs from its sealed retry bytes")
        return
    APPLY.atomic_write_bytes(path, expected)


def _checkpoint_matches_active(
    checkpoint: dict,
    intent: dict,
    journal: dict,
    active: dict,
) -> tuple[dict, bytes]:
    """Validate a pre-existing checkpoint before idempotent pending clearance."""
    index = journal["next_hop_index"]
    if (
        checkpoint.get("schema_version") != APPLY.MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA_VERSION
        or checkpoint.get("route_transaction_id") != intent.get("route_transaction_id")
        or checkpoint.get("route_intent_sha256")
        != APPLY.sha256_bytes(_canonical_json_bytes(intent))
        or checkpoint.get("checkpoint_index") != index
        or checkpoint.get("predecessor_checkpoint_sha256")
        != journal.get("last_checkpoint_sha256")
        or checkpoint.get("edge") != intent["route"]["edges"][index]
        or checkpoint.get("package") != active.get("package")
    ):
        raise _route_error("multi-hop retry checkpoint identity differs from active hop")
    child = checkpoint.get("child_transaction")
    pending = checkpoint.get("pending_receipt")
    if (
        not isinstance(child, dict)
        or child.get("transaction_id") != active.get("child_transaction_id")
        or not isinstance(pending, dict)
        or pending.get("path") != APPLY.PENDING_RECEIPT_PATH
        or pending.get("sha256") != active.get("pending_receipt_sha256")
        or not isinstance(pending.get("archive_path"), str)
    ):
        raise _route_error("multi-hop retry checkpoint child receipt differs")
    return child, pending["sha256"]


def _checkpoint_hop(
    target: Path,
    route_root: Path,
    intent: dict,
    journal: dict,
) -> dict:
    active = journal.get("active_hop")
    if not isinstance(active, dict):
        raise _route_error("multi-hop route checkpoint has no active hop")
    index = journal["next_hop_index"]
    transaction_id = active.get("child_transaction_id")
    _require_sha256(transaction_id, "multi-hop checkpoint child transaction ID")
    package = active.get("package")
    if not isinstance(package, dict):
        raise _route_error("multi-hop checkpoint package evidence is invalid")
    expected_route_context = _next_context(route_root, intent, journal)
    previous_sha = journal.get("last_checkpoint_sha256")
    archive_relative = (Path(ROUTE_CHECKPOINT_DIRECTORY) / f"{index:04d}.pending-receipt.yaml").as_posix()
    archive_path = route_root / Path(*PurePosixPath(archive_relative).parts)
    checkpoint_path = _checkpoint_path(route_root, index)
    if checkpoint_path.exists() or checkpoint_path.is_symlink() or APPLY.is_reparse_point(checkpoint_path):
        checkpoint, checkpoint_sha = _read_checkpoint(route_root, index)
        _child, pending_sha = _checkpoint_matches_active(checkpoint, intent, journal, active)
        archived = _read_regular(archive_path, "multi-hop retry checkpoint pending receipt archive")
        if APPLY.sha256_bytes(archived) != pending_sha:
            raise _route_error("multi-hop retry checkpoint archive differs")
        pending_path = target / APPLY.PENDING_RECEIPT_PATH
        if pending_path.is_symlink() or APPLY.is_reparse_point(pending_path):
            raise _route_error("multi-hop retry pending receipt is unsafe")
        if pending_path.exists():
            pending_raw = _read_regular(pending_path, "multi-hop retry child pending receipt")
            if pending_raw != archived:
                raise _route_error("multi-hop retry pending receipt differs from archive")
    else:
        child, pending_raw = _child_checkpoint_evidence(
            target, transaction_id, package, expected_route_context
        )
        pending_sha = APPLY.sha256_bytes(pending_raw)
        _ensure_exact_route_bytes(
            archive_path, pending_raw, "multi-hop checkpoint pending receipt archive"
        )
        authority_paths = {
            "provenance_sha256": APPLY.sha256_bytes(
                _read_regular(target / ".dev/ai-context/provenance.yaml", "checkpoint provenance")
            ),
            "customizations_sha256": APPLY.sha256_bytes(
                _read_regular(target / ".dev/ai-context/customizations.yaml", "checkpoint customizations")
            ),
        }
        checkpoint_unsigned = {
            "schema_version": APPLY.MULTI_HOP_ROUTE_CHECKPOINT_SCHEMA_VERSION,
            "route_transaction_id": intent["route_transaction_id"],
            "route_intent_sha256": APPLY.sha256_bytes(_canonical_json_bytes(intent)),
            "checkpoint_index": index,
            "predecessor_checkpoint_sha256": previous_sha,
            "edge": intent["route"]["edges"][index],
            "package": deepcopy(package),
            "child_transaction": child,
            "pending_receipt": {
                "path": APPLY.PENDING_RECEIPT_PATH,
                "sha256": pending_sha,
                "archive_path": archive_relative,
            },
            "authority": authority_paths,
            "target_surface": {
                "starting_commit": intent["target_starting_commit"],
                "paths": APPLY.route_checkpoint_surface(target),
            },
        }
        checkpoint = {**checkpoint_unsigned, "digest": _canonical_digest(checkpoint_unsigned)}
        checkpoint_sha = _write_json(checkpoint_path, checkpoint)
    # Keep the outer journal in checkpointing with the active child until the
    # archived pending receipt has been cleared (or its exact post-clear retry
    # state has been proven).  Only then promote the route checkpoint.
    try:
        APPLY.clear_checkpointed_pending_receipt_locked(
            target,
            transaction_id,
            pending_sha,
            route_transaction_id=intent["route_transaction_id"],
            route_intent_sha256=APPLY.sha256_bytes(_canonical_json_bytes(intent)),
            checkpoint_index=index,
            expected_child_route_context=expected_route_context,
        )
    except APPLY.ApplyError as exc:
        raise _route_error(f"multi-hop checkpoint pending receipt clearance failed: {exc}") from exc
    journal.update(
        {
            "state": "checkpointed",
            "next_hop_index": index + 1,
            "last_checkpoint_index": index,
            "last_checkpoint_sha256": checkpoint_sha,
            "active_hop": None,
        }
    )
    _persist_route_journal(route_root, intent, journal)
    return checkpoint


def finalize_hop(
    target_root: Path,
    route_transaction_id: str,
    candidate_provenance: dict,
    candidate_ledger: dict,
    *,
    effective_state_candidate: dict | None = None,
    effective_resolver_evidence: list[str] | None = None,
) -> dict:
    """Advance target authority only after target validation, then checkpoint it."""
    target = target_root.resolve()
    with APPLY.transaction_lock(target):
        route_root, intent, journal = _load_route(target, route_transaction_id)
        if journal["state"] != "finalizing" or not isinstance(journal.get("active_hop"), dict):
            raise _route_error("multi-hop route is not ready for target finalization")
        active = journal["active_hop"]
        transaction_id = active.get("child_transaction_id")
        _require_sha256(transaction_id, "multi-hop finalization child transaction ID")
        _revalidate_bound_hop_evidence(route_root, intent, journal, active)
        try:
            TARGET.finalize_context(
                target,
                candidate_provenance,
                candidate_ledger,
                effective_state_candidate=effective_state_candidate,
                effective_resolver_evidence=effective_resolver_evidence,
            )
        except TARGET.TargetValidationError as exc:
            raise _route_error(f"multi-hop child finalization was rejected: {exc}") from exc
        journal["state"] = "checkpointing"
        _persist_route_journal(route_root, intent, journal)
        checkpoint = _checkpoint_hop(target, route_root, intent, journal)
        if journal["next_hop_index"] == len(intent["route"]["edges"]):
            journal["state"] = "completed"
            _persist_route_journal(route_root, intent, journal)
        return {
            "route_transaction_id": route_transaction_id,
            "checkpoint_index": checkpoint["checkpoint_index"],
            "checkpoint_digest": checkpoint["digest"],
            "completed": journal["state"] == "completed",
        }


def _rollback_active_hop_locked(
    target: Path,
    route_transaction_id: str,
    boundary_hook: Callable[[str, dict], None] | None,
) -> dict:
    """Rollback one active child while the shared package lock is held."""
    route_root, intent, journal = _load_route(target, route_transaction_id)
    active = journal.get("active_hop")
    if journal["state"] not in {
        "applying",
        "awaiting-target-validation",
        "validating",
        "rolling-back",
    } or not isinstance(active, dict):
        raise _route_error("multi-hop route has no active unfinalized hop to roll back")
    transaction_id = active.get("child_transaction_id")
    derived_child_binding = False
    if transaction_id is None:
        transaction_id = active.get("plan_sha256")
        _require_sha256(transaction_id, "multi-hop rollback proposal plan SHA-256")
        child_root = APPLY.transaction_root(target, transaction_id)
        if not child_root.exists():
            journal["state"] = "checkpointed" if journal["last_checkpoint_index"] is not None else "planned"
            journal["active_hop"] = None
            _persist_route_journal(route_root, intent, journal)
            return {
                "route_transaction_id": route_transaction_id,
                "scope": "no-child-created-before-rollback",
                "state": journal["state"],
                "next_hop_index": journal["next_hop_index"],
            }
        active["child_transaction_id"] = transaction_id
        derived_child_binding = True
    _require_sha256(transaction_id, "multi-hop rollback child transaction ID")
    # A bound child has already promoted its package and validator evidence.
    # Reject a self-consistent forged copy before changing the route state or
    # delegating rollback to the child transaction.
    _revalidate_bound_hop_evidence(route_root, intent, journal, active)
    if derived_child_binding:
        journal["active_hop"] = active
        _persist_route_journal(route_root, intent, journal)
    package = active.get("package")
    if not isinstance(package, dict):
        raise _route_error("multi-hop rollback package identity is invalid")
    try:
        _child_root, _child_plan, child_journal = APPLY.load_transaction(target, transaction_id)
    except APPLY.ApplyError as exc:
        raise _route_error(f"multi-hop rollback child evidence is invalid: {exc}") from exc
    if child_journal.get("state") == "finalized":
        raise _route_error("finalized multi-hop child cannot be rolled back")
    if child_journal.get("state") == "rolled-back":
        journal["state"] = "checkpointed" if journal["last_checkpoint_index"] is not None else "planned"
        journal["active_hop"] = None
        _persist_route_journal(route_root, intent, journal)
        return {
            "route_transaction_id": route_transaction_id,
            "scope": "active-unfinalized-hop-only",
            "state": journal["state"],
            "next_hop_index": journal["next_hop_index"],
        }
    if journal["state"] != "rolling-back":
        journal["state"] = "rolling-back"
        _persist_route_journal(route_root, intent, journal)
    try:
        result = APPLY.recover_transaction_locked(
            target,
            transaction_id,
            "rollback",
            _package_root(route_root, package),
            boundary_hook,
        )
    except APPLY.ApplyError as exc:
        raise _route_error(f"multi-hop active child rollback failed: {exc}") from exc
    if result.get("state") != "rolled-back":
        raise _route_error("multi-hop active child rollback did not reach rolled-back")
    journal["state"] = "checkpointed" if journal["last_checkpoint_index"] is not None else "planned"
    journal["active_hop"] = None
    _persist_route_journal(route_root, intent, journal)
    return {
        "route_transaction_id": route_transaction_id,
        "scope": "active-unfinalized-hop-only",
        "state": journal["state"],
        "next_hop_index": journal["next_hop_index"],
    }


def rollback_active_hop(
    target_root: Path,
    route_transaction_id: str,
    *,
    boundary_hook: Callable[[str, dict], None] | None = None,
) -> dict:
    """Rollback only the active unfinalized child to its last checkpoint."""
    target = target_root.resolve()
    with APPLY.transaction_lock(target):
        return _rollback_active_hop_locked(target, route_transaction_id, boundary_hook)


def resume_multi_hop_upgrade(target_root: Path, route_transaction_id: str) -> dict:
    """Read durable state and fail closed rather than guessing missing evidence."""
    target = target_root.resolve()
    with APPLY.transaction_lock(target):
        route_root, intent, journal = _load_route(target, route_transaction_id)
        state = journal["state"]
        active = journal.get("active_hop")
        if state == "checkpointing":
            if not isinstance(active, dict):
                raise _route_error("checkpointing multi-hop route has no active-hop evidence")
            # This is the post-finalization crash recovery path.  It must not
            # turn forged promoted package/validator evidence into a durable
            # checkpoint merely because the child journal can be loaded.
            _revalidate_bound_hop_evidence(route_root, intent, journal, active)
            checkpoint = _checkpoint_hop(target, route_root, intent, journal)
            if journal["next_hop_index"] == len(intent["route"]["edges"]):
                journal["state"] = "completed"
                _persist_route_journal(route_root, intent, journal)
            return {
                "route_transaction_id": route_transaction_id,
                "state": journal["state"],
                "next_hop_index": journal["next_hop_index"],
                "resumable": journal["state"] != "completed",
                "recovered_checkpoint_index": checkpoint["checkpoint_index"],
            }
        if state == "rolling-back":
            result = _rollback_active_hop_locked(target, route_transaction_id, None)
            return {**result, "resumed_rollback": True, "resumable": True}
        if state == "checkpointed" and journal["next_hop_index"] == len(intent["route"]["edges"]):
            last_index = journal.get("last_checkpoint_index")
            last_sha = journal.get("last_checkpoint_sha256")
            if last_index != len(intent["route"]["edges"]) - 1:
                raise _route_error("final multi-hop checkpoint index is invalid")
            _checkpoint, observed_sha = _read_checkpoint(route_root, last_index)
            if observed_sha != last_sha:
                raise _route_error("final multi-hop checkpoint digest differs")
            _require_valid_retained_route(target, "final multi-hop checkpoint evidence")
            journal["state"] = "completed"
            _persist_route_journal(route_root, intent, journal)
            return {
                "route_transaction_id": route_transaction_id,
                "state": "completed",
                "next_hop_index": journal["next_hop_index"],
                "resumable": False,
                "recovered_final_checkpoint": last_index,
            }
        if state in {"checkpointed", "completed"}:
            _require_valid_retained_route(target, f"{state} multi-hop route evidence")
        if state in {"planned", "checkpointed", "completed", "rolled-back"}:
            return {
                "route_transaction_id": route_transaction_id,
                "state": state,
                "next_hop_index": journal["next_hop_index"],
                "resumable": state != "completed",
            }
        if not isinstance(active, dict):
            raise _route_error("interrupted multi-hop route has no active-hop evidence")
        transaction_id = active.get("child_transaction_id")
        if state == "awaiting-owner-decision":
            _validate_active_prepared_hop(route_root, intent, journal, active)
            return {
                "route_transaction_id": route_transaction_id,
                "state": state,
                "next_hop_index": journal["next_hop_index"],
                "resumable": True,
                "requires": "same-exact-owner-decision",
            }
        if state == "applying" and transaction_id is None:
            return _restore_unbound_active_child(target, route_root, intent, journal, active)
        if not isinstance(transaction_id, str):
            raise _route_error("interrupted multi-hop route lacks child transaction identity")
        _require_sha256(transaction_id, "interrupted multi-hop child transaction ID")
        _child_root, _plan, child_journal = APPLY.load_transaction(
            target,
            transaction_id,
            allow_unbound_target_validation_receipt=True,
        )
        if state == "applying" and child_journal.get("state") in {"awaiting-target-validation", "validated"}:
            journal["state"] = "awaiting-target-validation"
            _persist_route_journal(route_root, intent, journal)
            state = journal["state"]
        # A child-bound route can retain no proposal after promotion, so a
        # resumable target-validation/finalization state must reprobe the
        # sealed full edge and its promoted package/validator evidence here.
        # Loading the child journal alone is not sufficient: an attacker could
        # otherwise make the mutable promoted evidence self-consistent between
        # a crash and the next public resume call.
        if state in {"awaiting-target-validation", "validating", "finalizing"}:
            _revalidate_bound_hop_evidence(route_root, intent, journal, active)
        if state in {"awaiting-target-validation", "validating"} and child_journal.get("state") in {"awaiting-target-validation", "validated"}:
            return {
                "route_transaction_id": route_transaction_id,
                "state": state,
                "next_hop_index": journal["next_hop_index"],
                "resumable": True,
                "requires": "exact-external-target-validation-receipt",
            }
        if state == "finalizing" and child_journal.get("state") == "finalized":
            return {
                "route_transaction_id": route_transaction_id,
                "state": state,
                "next_hop_index": journal["next_hop_index"],
                "resumable": True,
                "requires": "same-candidate-authority-for-checkpoint-completion",
            }
        raise _route_error("multi-hop resume evidence is inconsistent; no state was inferred")


def run_multi_hop_upgrade(
    action: str,
    target_root: Path,
    **kwargs: object,
) -> dict:
    """Single explicit operation dispatcher; no shell fallback is provided."""
    actions = {
        "begin": begin_multi_hop_upgrade,
        "prepare-next-hop": prepare_next_hop,
        "apply-prepared-hop": apply_prepared_hop,
        "record-target-validation": record_hop_target_validation,
        "finalize-hop": finalize_hop,
        "resume": resume_multi_hop_upgrade,
        "rollback-active-hop": rollback_active_hop,
    }
    function = actions.get(action)
    if function is None:
        raise _route_error("multi-hop operation action is unsupported")
    return function(target_root, **kwargs)
