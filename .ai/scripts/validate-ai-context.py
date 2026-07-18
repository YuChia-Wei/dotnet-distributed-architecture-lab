#!/usr/bin/env python3
"""Validate objective, active AI-context navigation and runtime contracts."""

from __future__ import annotations

import posixpath
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
TABLE_PATH = re.compile(r"^\|\s*`([^`]+)`\s*\|")
PATH_REFERENCE = re.compile(r"`([^`\n]+)`|\]\(([^)\s]+)\)")
ACTIVE_SCRIPT_REFERENCE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\./)?(?P<path>\.ai/scripts/[A-Za-z0-9._/-]+\.(?:py|sh))"
)
ACTIVE_RUNTIME_ROOTS = (Path(".agents/skills"), Path(".claude/skills"))
PLANNED_RUNTIME_ROOTS = (
    Path(".github/prompts"),
    Path(".github/copilot-instructions.md"),
)
SKIP_PARTS = {"workflows", "archive", "archived", "migrations"}
LANGUAGE_SKIP_PARTS = SKIP_PARTS | {"examples", "example", "generated"}
PRODUCT_ROOTS = {"src", "test", "tests"}
LANGUAGE_EXTENSIONS = {".md", ".yaml", ".yml", ".json"}
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LANGUAGE_ROOTS = (
    Path(".ai"),
    Path(".agents"),
    Path(".claude"),
    Path(".codex"),
    Path(".github/agents"),
    Path(".dev/standards"),
    Path(".dev/specs"),
    Path(".dev/problem-frames"),
)
EXPLICIT_LANGUAGE_FILES = {Path(".dev/ARCHITECTURE.md")}
LANGUAGE_ALLOWLIST: dict[Path, frozenset[str]] = {
    Path(".ai/assets/skills/ai-context-auditor/skill.yaml"): frozenset(
        {'  - "自檢 AI context"', '  - "檢查 AI context 品質"'}
    ),
    Path(".dev/standards/WORKFLOW-GATE-POLICY.md"): frozenset(
        {
            '- the user uses wording such as "workflow", "規劃", "整理", "重構", '
            '"標準化", "治理", or "拆分" for repo-wide documentation or context work.'
        }
    ),
}
OWNERSHIP_REGISTRY = Path(".dev/standards/AI-CONTEXT-OWNERSHIP.yaml")
RULE_STRENGTHS = {"invariant", "profile-default", "conditional", "example", "historical"}
RULE_STATUSES = {"active", "deprecated", "historical"}
ASSET_SCHEMA_VERSION = "1.0"
KEBAB_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ASSET_PORTABILITY = {"portable", "repo-portable", "wrapper-specific"}
ASSET_AUDIENCES = {"agent-facing", "human-facing", "mixed"}
ASSET_SOURCES = {"canonical", "wrapper", "generated"}
ASSET_STATUSES = {"draft", "active", "deprecated", "historical"}
WRAPPER_TARGETS = {"claude", "codex", "copilot"}
CAPABILITY_PROFILE = Path(
    ".ai/assets/skills/dev-workflow/references/capability-profile.yaml"
)
PROJECT_CONFIG_TEMPLATE = Path(
    ".ai/assets/skills/repo-structure-sync/templates/project-config.template.yaml"
)
TECHNOLOGY_SELECTION_SCHEMA = Path(
    ".ai/assets/skills/repo-structure-sync/templates/technology-selection.schema.yaml"
)
EXAMPLE_EVIDENCE_SCHEMA = Path(".dev/standards/examples/evidence-schema.yaml")
EXAMPLE_EVIDENCE_MANIFEST = Path(".dev/standards/examples/evidence-manifest.yaml")
EXAMPLE_PLACEHOLDER_DISPOSITION = Path(
    ".dev/standards/examples/placeholder-disposition.yaml"
)
SOURCE_INCLUDE_EVIDENCE_MANIFEST = Path(
    ".ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml"
)
CLAUDE_ENTRY_TEMPLATE = """# Claude Code Project Instructions

@AGENTS.md

This file is a thin Claude Code project-memory entry. `AGENTS.md` is the
canonical repository collaboration guide; do not duplicate its rules here.
"""


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [Path(line) for line in result.stdout.splitlines() if line]
    return [path for path in paths if (ROOT / path).is_file()]


def active_indexes(files: list[Path]) -> list[Path]:
    return [
        path
        for path in files
        if path.name.lower() == "index.md"
        and not any(part.lower() in SKIP_PARTS for part in path.parts)
        and (not path.parts or path.parts[0].lower() not in PRODUCT_ROOTS)
    ]


def is_catalog_path(value: str) -> bool:
    return not (
        not value
        or "<" in value
        or ">" in value
        or "*" in value
        or value.startswith(("http://", "https://"))
    )


def validate_index(index: Path, errors: list[str]) -> None:
    text = (ROOT / index).read_text(encoding="utf-8")
    if "|`n|" in text:
        errors.append(f"{index}: contains literal table corruption |`n|")
    for line_number, line in enumerate(text.splitlines(), 1):
        match = TABLE_PATH.match(line)
        if not match or not is_catalog_path(match.group(1)):
            continue
        target = (ROOT / index.parent / match.group(1)).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{index}:{line_number}: catalog path escapes repository: {match.group(1)}")
            continue
        if not target.exists():
            errors.append(f"{index}:{line_number}: missing catalog path: {match.group(1)}")


def validate_exact_case_references(
    files: list[Path], errors: list[str], root: Path = ROOT
) -> None:
    """Reject active internal references whose casing differs from the Git path."""
    exact_paths: set[str] = set()
    for path in files:
        exact_paths.add(path.as_posix())
        parent = path.parent
        while parent != Path("."):
            exact_paths.add(parent.as_posix())
            parent = parent.parent

    canonical_by_case = {path.casefold(): path for path in exact_paths}
    active_files = [
        path
        for path in files
        if path.suffix.lower() in LANGUAGE_EXTENSIONS
        and path.parts
        and path.parts[0].lower() in {".ai", ".agents", ".claude", ".codex", ".dev", ".github"}
        and not any(part.lower() in LANGUAGE_SKIP_PARTS for part in path.parts)
        and Path(".ai/scripts/tests") not in (path, *path.parents)
        and path.parts[0].lower() not in PRODUCT_ROOTS
    ]

    for source in active_files:
        text = (root / source).read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), 1):
            for match in PATH_REFERENCE.finditer(line):
                value = (match.group(1) or match.group(2)).strip("<>")
                value = value.split("#", 1)[0].rstrip("/.,;:")
                if not value or any(marker in value for marker in ("<", ">", "*", "{", "}")):
                    continue
                if value.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if value.startswith((".ai/", ".dev/", ".agents/", ".claude/", ".codex/", ".github/")):
                    candidate = posixpath.normpath(value)
                elif value.startswith(("./", "../")):
                    candidate = posixpath.normpath((source.parent / Path(value)).as_posix())
                else:
                    continue
                canonical = canonical_by_case.get(candidate.casefold())
                if canonical is not None and canonical != candidate:
                    errors.append(
                        f"{source}:{line_number}: exact-case mismatch: {value} -> {canonical}"
                    )


def validate_active_script_references(
    files: list[Path], errors: list[str], root: Path = ROOT
) -> None:
    """Reject active AI-context commands that point to missing local scripts."""
    indexes = set(active_indexes(files))
    active_files = [
        path
        for path in files
        if is_language_surface(path, indexes)
        and Path(".ai/scripts/tests") not in (path, *path.parents)
    ]

    for source in active_files:
        text = (root / source).read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), 1):
            for match in ACTIVE_SCRIPT_REFERENCE.finditer(line):
                script_path = Path(match.group("path"))
                if not (root / script_path).is_file():
                    errors.append(
                        f"{source}:{line_number}: active script reference does not exist: "
                        f"{script_path.as_posix()}"
                    )


def validate_technology_selection_contract(
    errors: list[str],
    root: Path = ROOT,
    template_path: Path = PROJECT_CONFIG_TEMPLATE,
    schema_path: Path = TECHNOLOGY_SELECTION_SCHEMA,
) -> None:
    """Validate the target-owned generic technology-selection template contract."""
    try:
        template = yaml.safe_load((root / template_path).read_text(encoding="utf-8"))
        schema = yaml.safe_load((root / schema_path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"technology selection contract cannot be loaded: {exc}")
        return

    if not isinstance(template, dict):
        errors.append(f"{template_path}: root must be a mapping")
        return
    if not isinstance(schema, dict):
        errors.append(f"{schema_path}: root must be a mapping")
        return

    if template.get("technologySelections") != []:
        errors.append(
            f"{template_path}: technologySelections must default to an empty collection"
        )
    architecture = template.get("architecture")
    if not isinstance(architecture, dict) or architecture.get("capabilitySelections") != []:
        errors.append(
            f"{template_path}: architecture.capabilitySelections must default to an empty collection"
        )

    expected_fields = {"slot", "value", "status", "source", "evidence", "reason"}
    required_fields = schema.get("required_fields")
    if not isinstance(required_fields, list) or set(required_fields) != expected_fields:
        errors.append(
            f"{schema_path}: required_fields must equal {sorted(expected_fields)}"
        )

    for key, expected in (
        ("allowed_statuses", {"selected", "not-applicable", "unresolved"}),
        ("allowed_sources", {"repository-evidence", "explicit-target-decision"}),
    ):
        values = schema.get(key)
        if not isinstance(values, list) or set(values) != expected:
            errors.append(f"{schema_path}: {key} must equal {sorted(expected)}")

    slot_pattern = schema.get("slot_pattern")
    if not isinstance(slot_pattern, str):
        errors.append(f"{schema_path}: slot_pattern must be a string")
    else:
        try:
            re.compile(slot_pattern)
        except re.error as exc:
            errors.append(f"{schema_path}: invalid slot_pattern: {exc}")


def validate_example_evidence_contract(
    errors: list[str],
    root: Path = ROOT,
    manifest_path: Path = EXAMPLE_EVIDENCE_MANIFEST,
    schema_path: Path = EXAMPLE_EVIDENCE_SCHEMA,
) -> None:
    """Validate machine-readable example tiers and fail closed on evidence inflation."""
    try:
        manifest = yaml.safe_load((root / manifest_path).read_text(encoding="utf-8"))
        schema = yaml.safe_load((root / schema_path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"example evidence contract cannot be loaded: {exc}")
        return

    if not isinstance(manifest, dict) or not isinstance(schema, dict):
        errors.append("example evidence manifest and schema roots must be mappings")
        return

    expected_tiers = {
        "executable-tested",
        "structure-validated",
        "illustrative",
        "reference-only",
        "historical",
    }
    allowed_tiers = schema.get("allowed_tiers")
    if not isinstance(allowed_tiers, list) or set(allowed_tiers) != expected_tiers:
        errors.append(f"{schema_path}: allowed_tiers must equal {sorted(expected_tiers)}")
        return

    default_allowed = schema.get("default_allowed_tiers")
    default_tier = manifest.get("default_tier")
    if (
        not isinstance(default_allowed, list)
        or set(default_allowed) != {"illustrative", "historical"}
        or default_tier not in default_allowed
    ):
        errors.append(
            f"{manifest_path}: default_tier must be illustrative or historical"
        )

    required_fields = schema.get("required_entry_fields")
    if not isinstance(required_fields, list):
        errors.append(f"{schema_path}: required_entry_fields must be a list")
        return
    required = set(required_fields)
    tier_requirements = schema.get("tier_requirements")
    if not isinstance(tier_requirements, dict):
        errors.append(f"{schema_path}: tier_requirements must be a mapping")
        return

    entries = manifest.get("entries")
    if not isinstance(entries, list):
        errors.append(f"{manifest_path}: entries must be a list")
        return

    seen: set[str] = set()
    example_root = root / manifest_path.parent
    for index, entry in enumerate(entries):
        label = f"{manifest_path}:entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: entry must be a mapping")
            continue
        missing = sorted(required - set(entry))
        if missing:
            errors.append(f"{label}: missing required fields: {missing}")
            continue

        path_value = entry.get("path")
        tier = entry.get("tier")
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"{label}: path must be a non-empty string")
            continue
        if path_value in seen:
            errors.append(f"{label}: duplicate path {path_value}")
        seen.add(path_value)
        candidate = Path(path_value)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"{label}: path must remain under examples: {path_value}")
        elif not (example_root / candidate).exists():
            errors.append(f"{label}: classified path does not exist: {path_value}")

        if tier not in expected_tiers:
            errors.append(f"{label}: invalid tier {tier!r}")
            continue
        requirement = tier_requirements.get(tier)
        if not isinstance(requirement, dict):
            errors.append(f"{schema_path}: missing requirement for tier {tier}")
            continue
        for field in requirement.get("required_nonempty", []):
            value = entry.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{label}: tier {tier} requires non-empty {field}")

        if tier == "structure-validated":
            for validator in entry.get("validators", []):
                if not isinstance(validator, str) or not (root / validator).is_file():
                    errors.append(f"{label}: declared validator does not exist: {validator}")

    readme = root / manifest_path.parent / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        for claim in ("Verified Templates", "Single Source of Truth"):
            if claim in readme_text:
                errors.append(f"{readme.relative_to(root)}: unsupported claim remains: {claim}")

    stale_versions = root / manifest_path.parent / ".versions.json"
    if stale_versions.exists():
        errors.append(
            f"{stale_versions.relative_to(root)}: stale source-sync metadata must be retired"
        )


def validate_source_include_evidence(
    errors: list[str],
    root: Path = ROOT,
    manifest_path: Path = SOURCE_INCLUDE_EVIDENCE_MANIFEST,
) -> None:
    """Validate executable-tested claims for source-includable framework assets."""
    try:
        manifest = yaml.safe_load((root / manifest_path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"source-include evidence manifest cannot be loaded: {exc}")
        return

    if not isinstance(manifest, dict) or not isinstance(manifest.get("entries"), list):
        errors.append(f"{manifest_path}: entries must be a list")
        return

    asset_root = root / manifest_path.parent
    for index, entry in enumerate(manifest["entries"]):
        label = f"{manifest_path}:entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: entry must be a mapping")
            continue

        path_value = entry.get("path")
        candidate = Path(path_value) if isinstance(path_value, str) else None
        if (
            candidate is None
            or candidate.is_absolute()
            or ".." in candidate.parts
            or not (asset_root / candidate).is_dir()
        ):
            errors.append(f"{label}: source-include path must be an existing local directory")

        if entry.get("tier") != "executable-tested":
            errors.append(f"{label}: source includes must declare executable-tested tier")

        for field in ("build_commands", "test_commands"):
            value = entry.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{label}: executable-tested tier requires non-empty {field}")

        test_project = entry.get("test_project")
        if not isinstance(test_project, str) or not (root / test_project).is_file():
            errors.append(f"{label}: declared test_project does not exist: {test_project}")


def validate_example_placeholder_disposition(
    errors: list[str],
    root: Path = ROOT,
    disposition_path: Path = EXAMPLE_PLACEHOLDER_DISPOSITION,
    evidence_path: Path = EXAMPLE_EVIDENCE_MANIFEST,
) -> None:
    """Validate placeholder outcomes against evidence tiers and canonical replacements."""
    try:
        disposition = yaml.safe_load((root / disposition_path).read_text(encoding="utf-8"))
        evidence = yaml.safe_load((root / evidence_path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"example placeholder disposition cannot be loaded: {exc}")
        return

    if not isinstance(disposition, dict) or not isinstance(disposition.get("entries"), list):
        errors.append(f"{disposition_path}: entries must be a list")
        return
    if not isinstance(evidence, dict) or not isinstance(evidence.get("entries"), list):
        errors.append(f"{evidence_path}: entries must be a list")
        return

    evidence_tiers = {
        entry.get("path"): entry.get("tier")
        for entry in evidence["entries"]
        if isinstance(entry, dict)
    }
    allowed_dispositions = {
        "bounded-rewrite",
        "reference-only",
        "historical",
        "retired",
    }
    for index, entry in enumerate(disposition["entries"]):
        label = f"{disposition_path}:entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: entry must be a mapping")
            continue

        path_value = entry.get("path")
        outcome = entry.get("disposition")
        tier = entry.get("evidence_tier")
        replacements = entry.get("canonical_replacements")
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"{label}: path must be a non-empty string")
            continue
        if outcome not in allowed_dispositions:
            errors.append(f"{label}: invalid disposition {outcome!r}")
        if outcome == "retired":
            if path_value in evidence_tiers:
                errors.append(f"{label}: retired path must not remain in evidence manifest")
        elif evidence_tiers.get(path_value) != tier:
            errors.append(
                f"{label}: evidence_tier {tier!r} does not match manifest "
                f"{evidence_tiers.get(path_value)!r}"
            )

        if not isinstance(replacements, list) or not replacements:
            errors.append(f"{label}: canonical_replacements must be non-empty")
        else:
            for replacement in replacements:
                if not isinstance(replacement, str) or not (root / replacement).exists():
                    errors.append(
                        f"{label}: canonical replacement does not exist: {replacement}"
                    )


def is_language_surface(path: Path, indexes: set[Path]) -> bool:
    """Return whether a tracked file is active agent-facing execution context."""
    if path in indexes:
        return True
    if path.parts and path.parts[0].lower() in PRODUCT_ROOTS:
        return False
    if path.suffix.lower() not in LANGUAGE_EXTENSIONS:
        return False
    if any(part.lower() in LANGUAGE_SKIP_PARTS for part in path.parts):
        return False
    return path in EXPLICIT_LANGUAGE_FILES or any(
        path == root or root in path.parents for root in LANGUAGE_ROOTS
    )


def validate_language(path: Path, errors: list[str]) -> None:
    """Reject Han prose except exact, path-scoped routing trigger fragments."""
    allowed_lines = LANGUAGE_ALLOWLIST.get(path, frozenset())
    text = (ROOT / path).read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), 1):
        if HAN.search(line) and line not in allowed_lines:
            errors.append(f"{path}:{line_number}: unexpected Han text in agent-facing context")


def markdown_structure(path: Path) -> tuple[list[int], list[str]]:
    """Return heading levels and ordered path-like backtick values in table rows."""
    headings: list[int] = []
    table_paths: list[str] = []
    fenced = False
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        heading = re.match(r"^(#{1,6})\s+", line)
        if heading:
            headings.append(len(heading.group(1)))
        if line.lstrip().startswith("|"):
            for value in re.findall(r"`([^`]+)`", line):
                if "/" in value or value.lower().endswith(".md"):
                    table_paths.append(value)
    return headings, table_paths


def validate_bilingual_entries(errors: list[str]) -> None:
    """Validate entry-file ownership and reciprocal links, not semantic parity."""
    contracts = (
        (
            Path("README.md"),
            "[English](README.en.md)",
            "canonical",
            Path("README.en.md"),
            "[繁體中文](README.md)",
            "translation",
        ),
        (
            Path("AGENTS.md"),
            "[Traditional Chinese](AGENTS.zh-TW.md)",
            "canonical English",
            Path("AGENTS.zh-TW.md"),
            "[English](AGENTS.md)",
            "翻譯",
        ),
    )
    for (
        canonical,
        canonical_link,
        canonical_marker,
        translation,
        translation_link,
        translation_marker,
    ) in contracts:
        for path in (canonical, translation):
            if not (ROOT / path).is_file():
                errors.append(f"missing bilingual entry file: {path}")
        if not (ROOT / canonical).is_file() or not (ROOT / translation).is_file():
            continue
        canonical_text = (ROOT / canonical).read_text(encoding="utf-8")
        translation_text = (ROOT / translation).read_text(encoding="utf-8")
        if canonical_link not in canonical_text:
            errors.append(f"{canonical}: missing reciprocal translation link to {translation}")
        if translation_link not in translation_text:
            errors.append(f"{translation}: missing reciprocal canonical link to {canonical}")
        if canonical_marker not in canonical_text:
            errors.append(f"{canonical}: missing canonical ownership marker")
        if translation_marker not in translation_text:
            errors.append(f"{translation}: missing translation ownership marker")
        canonical_headings, canonical_paths = markdown_structure(canonical)
        translation_headings, translation_paths = markdown_structure(translation)
        if canonical_headings != translation_headings:
            errors.append(
                f"{canonical} <-> {translation}: heading-level structural parity mismatch"
            )
        if Counter(canonical_paths) != Counter(translation_paths):
            errors.append(
                f"{canonical} <-> {translation}: backtick table-path multiset parity mismatch"
            )
        elif canonical_paths != translation_paths:
            errors.append(
                f"{canonical} <-> {translation}: backtick table-path order parity mismatch"
            )

    required_agent_rows = {
        "README.md", "README.en.md", "AGENTS.md", "AGENTS.zh-TW.md", "CLAUDE.md"
    }
    for path in (Path("AGENTS.md"), Path("AGENTS.zh-TW.md")):
        if not (ROOT / path).is_file():
            continue
        _, table_paths = markdown_structure(path)
        missing = sorted(required_agent_rows - set(table_paths))
        if missing:
            errors.append(f"{path}: missing required root entry table rows: {missing}")


def validate_runtime_entries(
    files: list[Path], errors: list[str], *, root: Path = ROOT
) -> None:
    """Validate case-safe canonical and runtime-specific root entry files."""
    root_files = {path.as_posix() for path in files if len(path.parts) == 1}
    for required in ("AGENTS.md", "CLAUDE.md"):
        if required not in root_files:
            errors.append(f"missing case-sensitive root runtime entry: {required}")
    if "agents.md" in root_files:
        errors.append("lowercase agents.md is not a portable Codex root entry; use AGENTS.md")

    claude_path = root / "CLAUDE.md"
    if not claude_path.is_file():
        return
    claude_text = claude_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if claude_text != CLAUDE_ENTRY_TEMPLATE:
        errors.append(
            "CLAUDE.md: must exactly match the thin @AGENTS.md adapter template"
        )


def skill_names(root: Path, entry: str) -> set[str]:
    absolute = ROOT / root
    return {
        child.name
        for child in absolute.iterdir()
        if child.is_dir() and (child / entry).is_file()
    }


def validate_rule_ownership(errors: list[str]) -> int:
    """Validate structural ownership contracts without claiming semantic parity."""
    registry_path = ROOT / OWNERSHIP_REGISTRY
    if not registry_path.is_file():
        errors.append(f"missing rule ownership registry: {OWNERSHIP_REGISTRY}")
        return 0
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        errors.append(f"{OWNERSHIP_REGISTRY}: invalid YAML: {exc}")
        return 0
    rules = data.get("rules", []) if isinstance(data, dict) else []
    if not isinstance(rules, list):
        errors.append(f"{OWNERSHIP_REGISTRY}: rules must be a list")
        return 0

    seen: set[str] = set()
    for index, rule in enumerate(rules, 1):
        label = f"{OWNERSHIP_REGISTRY}:rules[{index}]"
        if not isinstance(rule, dict):
            errors.append(f"{label}: rule must be a mapping")
            continue
        rule_id = rule.get("rule_id")
        if not isinstance(rule_id, str) or not rule_id:
            errors.append(f"{label}: missing rule_id")
            continue
        if rule_id in seen:
            errors.append(f"{label}: duplicate rule_id {rule_id}")
        seen.add(rule_id)
        strength = rule.get("strength")
        status = rule.get("status")
        override = rule.get("override_policy")
        if strength not in RULE_STRENGTHS:
            errors.append(f"{label}: invalid strength {strength!r}")
        if status not in RULE_STATUSES:
            errors.append(f"{label}: invalid status {status!r}")
        expected_override = {
            "invariant": "forbidden",
            "profile-default": "explicit-target-decision",
            "conditional": "not-applicable",
        }.get(strength)
        if expected_override and override != expected_override:
            errors.append(
                f"{label}: {strength} requires override_policy {expected_override}"
            )
        if strength == "conditional" and not rule.get("applicability"):
            errors.append(f"{label}: conditional rule requires applicability")

        canonical_value = rule.get("canonical_path")
        if not isinstance(canonical_value, str):
            errors.append(f"{label}: missing canonical_path")
            continue
        canonical = Path(canonical_value)
        if Path(".dev/standards") not in canonical.parents:
            errors.append(f"{label}: canonical_path must be under .dev/standards")
        canonical_file = ROOT / canonical
        if not canonical_file.is_file():
            errors.append(f"{label}: missing canonical_path {canonical}")
            continue
        anchor = rule.get("canonical_anchor")
        canonical_text = canonical_file.read_text(encoding="utf-8")
        if not isinstance(anchor, str) or anchor not in canonical_text:
            errors.append(f"{label}: canonical_anchor not found in {canonical}")

        consumers = rule.get("derived_consumers", [])
        if not isinstance(consumers, list):
            errors.append(f"{label}: derived_consumers must be a list")
            continue
        for consumer_value in consumers:
            consumer = Path(consumer_value)
            consumer_file = ROOT / consumer
            if not consumer_file.is_file():
                errors.append(f"{label}: missing derived consumer {consumer}")
            elif rule_id not in consumer_file.read_text(encoding="utf-8"):
                errors.append(f"{label}: derived consumer {consumer} does not cite {rule_id}")
    return len(rules)


def load_yaml_mapping(path: Path, errors: list[str]) -> dict | None:
    try:
        value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: root must be a mapping")
        return None
    return value


def validate_wrapper_metadata(
    path: Path,
    data: dict,
    errors: list[str],
    *,
    root: Path = ROOT,
) -> None:
    """Validate one skill's canonical-to-runtime wrapper path contract."""
    targets = data.get("wrapper_targets")
    metadata = data.get("wrapper_metadata")
    if not isinstance(targets, list) or not all(isinstance(item, str) for item in targets):
        return
    if len(targets) != len(set(targets)):
        errors.append(f"{path}: wrapper_targets must not contain duplicates")
    if not isinstance(metadata, dict):
        errors.append(f"{path}: wrapper_metadata must be a mapping")
        return

    target_set = set(targets)
    metadata_keys = list(metadata)
    non_string_keys = [key for key in metadata_keys if not isinstance(key, str)]
    if non_string_keys:
        errors.append(f"{path}: wrapper_metadata keys must be strings: {non_string_keys!r}")
    metadata_set = {key for key in metadata_keys if isinstance(key, str)}
    if metadata_set != target_set:
        errors.append(
            f"{path}: wrapper_metadata target parity mismatch; "
            f"missing={sorted(target_set - metadata_set)}, "
            f"extra={sorted(metadata_set - target_set)}"
        )

    root_resolved = root.resolve()
    for target in sorted(target_set & metadata_set):
        target_metadata = metadata[target]
        label = f"{path}: wrapper_metadata.{target}"
        if not isinstance(target_metadata, dict):
            errors.append(f"{label} must be a mapping")
            continue
        if "runtime_wrapper_path" in target_metadata:
            errors.append(f"{label}: runtime_wrapper_path is legacy; use wrapper_path")
        wrapper_value = target_metadata.get("wrapper_path")
        if not isinstance(wrapper_value, str) or not wrapper_value:
            errors.append(f"{label}.wrapper_path must be a non-empty string")
            continue
        if (
            Path(wrapper_value).is_absolute()
            or "\\" in wrapper_value
            or any(character in wrapper_value for character in "<>*?[]{}")
        ):
            errors.append(
                f"{label}.wrapper_path must be a repository-relative path "
                "without placeholders or globs"
            )
            continue
        wrapper_path = (root / wrapper_value).resolve()
        try:
            wrapper_path.relative_to(root_resolved)
        except ValueError:
            errors.append(f"{label}.wrapper_path escapes the repository: {wrapper_value}")
            continue
        if not wrapper_path.exists():
            errors.append(f"{label}.wrapper_path does not exist: {wrapper_value}")


def validate_canonical_assets(errors: list[str]) -> tuple[int, dict[str, dict]]:
    """Validate versioned skill and sub-agent manifests against the canonical contract."""
    manifests = sorted(Path(".ai/assets/skills").glob("*/skill.yaml")) + sorted(
        Path(".ai/assets/sub-agent-role-prompts").glob("*/sub-agent.yaml")
    )
    required = {
        "schema_version", "asset_id", "asset_type", "title", "purpose",
        "portability", "audience", "wrapper_targets", "source_of_truth",
        "inputs", "outputs", "constraints", "references", "examples", "status",
    }
    expected_types = {
        "skill.yaml": "skill-spec",
        "sub-agent.yaml": "sub-agent-role-prompt",
    }
    seen: set[str] = set()
    skill_assets: dict[str, dict] = {}
    for path in manifests:
        data = load_yaml_mapping(path, errors)
        if data is None:
            continue
        missing = sorted(required - data.keys())
        if missing:
            errors.append(f"{path}: missing canonical fields: {missing}")
        asset_id = data.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id:
            errors.append(f"{path}: asset_id must be a non-empty string")
            continue
        if asset_id in seen:
            errors.append(f"{path}: duplicate asset_id {asset_id}")
        seen.add(asset_id)
        if not KEBAB_ID.fullmatch(asset_id):
            errors.append(f"{path}: asset_id must use kebab-case")
        if asset_id != path.parent.name:
            errors.append(f"{path}: asset_id must match parent folder {path.parent.name}")
        if data.get("schema_version") != ASSET_SCHEMA_VERSION:
            errors.append(f"{path}: schema_version must be {ASSET_SCHEMA_VERSION}")
        if data.get("asset_type") != expected_types[path.name]:
            errors.append(f"{path}: unexpected asset_type {data.get('asset_type')!r}")
        for key in ("title", "purpose"):
            if not isinstance(data.get(key), str) or not data.get(key):
                errors.append(f"{path}: {key} must be a non-empty string")
        if data.get("portability") not in ASSET_PORTABILITY:
            errors.append(f"{path}: invalid portability {data.get('portability')!r}")
        if data.get("audience") not in ASSET_AUDIENCES:
            errors.append(f"{path}: invalid audience {data.get('audience')!r}")
        if data.get("source_of_truth") not in ASSET_SOURCES:
            errors.append(f"{path}: invalid source_of_truth {data.get('source_of_truth')!r}")
        if data.get("status") not in ASSET_STATUSES:
            errors.append(f"{path}: invalid status {data.get('status')!r}")
        for key in ("wrapper_targets", "inputs", "outputs", "constraints", "references", "examples"):
            values = data.get(key)
            if not isinstance(values, list) or not all(
                isinstance(item, str) and item for item in values
            ):
                errors.append(f"{path}: {key} must be a list of non-empty strings")
        targets = data.get("wrapper_targets", [])
        if isinstance(targets, list) and not set(targets) <= WRAPPER_TARGETS:
            errors.append(f"{path}: unsupported wrapper_targets {sorted(set(targets) - WRAPPER_TARGETS)}")
        for key in ("references", "examples"):
            values = data.get(key, [])
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str) and value and "<" not in value and not (ROOT / value).exists():
                        errors.append(f"{path}: missing {key} path {value}")
        if path.name == "skill.yaml":
            skill_assets[asset_id] = data
            validate_wrapper_metadata(path, data, errors)
        for key in ("triggers", "workflow"):
            if key not in data:
                errors.append(f"{path}: missing type-specific field {key}")
        triggers = data.get("triggers")
        if not isinstance(triggers, list) or not triggers or not all(
            isinstance(item, str) and item for item in triggers
        ):
            errors.append(f"{path}: triggers must be a non-empty list of strings")
        if path.name == "sub-agent.yaml" and not (
            isinstance(data.get("role_kind"), str) and data.get("role_kind")
        ):
            errors.append(f"{path}: role_kind must be a non-empty string")
        workflow = data.get("workflow")
        if not isinstance(workflow, list) or not workflow:
            errors.append(f"{path}: workflow must be a non-empty list")
        else:
            step_ids: list[int] = []
            for step in workflow:
                if not isinstance(step, dict):
                    errors.append(f"{path}: each workflow step must be a mapping")
                    continue
                step_id = step.get("step")
                description = step.get("description")
                if not isinstance(step_id, int) or step_id < 1:
                    errors.append(f"{path}: workflow step must be a positive integer")
                else:
                    step_ids.append(step_id)
                if not isinstance(description, str) or not description:
                    errors.append(f"{path}: workflow step description must be non-empty")
            if step_ids != list(range(1, len(step_ids) + 1)):
                errors.append(f"{path}: workflow steps must be unique and sequential from 1")

    templates = ROOT / ".ai/assets/templates"
    legacy = sorted(path.name for path in templates.glob("*.template.yaml"))
    if legacy:
        errors.append(f".ai/assets/templates: legacy duplicate templates remain: {legacy}")
    for name in (
        "skill-template.yaml", "sub-agent-role-prompt-template.yaml",
        "command-template.yaml", "prompt-package-template.yaml",
    ):
        if not (templates / name).is_file():
            errors.append(f".ai/assets/templates: missing canonical template {name}")
    return len(manifests), skill_assets


def validate_capability_profile(skill_assets: dict[str, dict], errors: list[str]) -> int:
    """Validate deterministic development-slot routing against declared skill metadata."""
    profile = load_yaml_mapping(CAPABILITY_PROFILE, errors)
    if profile is None:
        return 0
    if profile.get("schema_version") != "1.0":
        errors.append(f"{CAPABILITY_PROFILE}: schema_version must be 1.0")
    if not isinstance(profile.get("profile_id"), str) or not profile.get("profile_id"):
        errors.append(f"{CAPABILITY_PROFILE}: profile_id must be a non-empty string")
    if profile.get("status") != "active":
        errors.append(f"{CAPABILITY_PROFILE}: status must be active")
    allowed = profile.get("allowed_slots")
    required = profile.get("required_slots")
    mappings = profile.get("mappings")
    if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
        errors.append(f"{CAPABILITY_PROFILE}: allowed_slots must be a list of strings")
        return 0
    if len(allowed) != len(set(allowed)):
        errors.append(f"{CAPABILITY_PROFILE}: allowed_slots contains duplicates")
    if not isinstance(required, list) or not set(required) <= set(allowed):
        errors.append(f"{CAPABILITY_PROFILE}: required_slots must be a subset of allowed_slots")
        required = []
    if not isinstance(mappings, dict):
        errors.append(f"{CAPABILITY_PROFILE}: mappings must be a mapping")
        return 0
    unknown = sorted(set(mappings) - set(allowed))
    missing = sorted(set(required) - set(mappings))
    if unknown:
        errors.append(f"{CAPABILITY_PROFILE}: unknown mapped slots {unknown}")
    if missing:
        errors.append(f"{CAPABILITY_PROFILE}: missing required mappings {missing}")
    for slot, skill_id in mappings.items():
        if not isinstance(skill_id, str) or skill_id not in skill_assets:
            errors.append(f"{CAPABILITY_PROFILE}: {slot} maps missing skill {skill_id!r}")
            continue
        skill = skill_assets[skill_id]
        if skill.get("status") != "active":
            errors.append(f"{CAPABILITY_PROFILE}: {slot} maps inactive skill {skill_id}")
        slots = skill.get("capability_slots", [])
        if not isinstance(slots, list) or slot not in slots:
            errors.append(f"{CAPABILITY_PROFILE}: {skill_id} does not declare slot {slot}")
    expected = {str(slot): str(skill) for slot, skill in mappings.items()}
    for markdown_path, heading in (
        (Path(".ai/assets/skills/dev-workflow/references/capability-profile.md"), "## Capability Mapping"),
        (Path(".ai/assets/skills/dev-workflow/references/routing-playbook.md"), "## Local Profile Resolution"),
    ):
        text = (ROOT / markdown_path).read_text(encoding="utf-8")
        section = text.split(heading, 1)[1].split("\n## ", 1)[0] if heading in text else ""
        pairs = {
            match.group(1): match.group(2)
            for line in section.splitlines()
            if (match := re.match(r"^\| `([^`]+)` \| `([^`]+)` \|", line))
        }
        if pairs != expected:
            errors.append(
                f"{markdown_path}: capability table differs from {CAPABILITY_PROFILE}; "
                f"expected={expected}, actual={pairs}"
            )
    return len(mappings)


def main() -> int:
    errors: list[str] = []
    files = tracked_files()
    indexes = active_indexes(files)

    validate_exact_case_references(files, errors)
    validate_active_script_references(files, errors)
    validate_technology_selection_contract(errors)
    validate_example_evidence_contract(errors)
    validate_example_placeholder_disposition(errors)
    validate_source_include_evidence(errors)

    for index in indexes:
        validate_index(index, errors)

    index_set = set(indexes)
    language_files = [path for path in files if is_language_surface(path, index_set)]
    for path in language_files:
        validate_language(path, errors)

    validate_bilingual_entries(errors)
    validate_runtime_entries(files, errors)
    ownership_rules = validate_rule_ownership(errors)
    canonical_assets, skill_assets = validate_canonical_assets(errors)
    capability_mappings = validate_capability_profile(skill_assets, errors)

    for runtime_root in ACTIVE_RUNTIME_ROOTS:
        if not (ROOT / runtime_root).is_dir():
            errors.append(f"declared current runtime root is missing: {runtime_root}")

    # Future adapters must be deliberately promoted to the current-runtime contract.
    present_planned = [str(path) for path in PLANNED_RUNTIME_ROOTS if (ROOT / path).exists()]
    if present_planned:
        errors.append(
            "planned runtime path exists but is not declared current: " + ", ".join(present_planned)
        )

    canonical = skill_names(Path(".ai/assets/skills"), "skill.yaml")
    agents = skill_names(Path(".agents/skills"), "SKILL.md")
    claude = skill_names(Path(".claude/skills"), "SKILL.md")
    for label, inventory in (("Agents/Codex", agents), ("Claude", claude)):
        if inventory != canonical:
            missing = sorted(canonical - inventory)
            extra = sorted(inventory - canonical)
            errors.append(f"{label} wrapper parity mismatch; missing={missing}, extra={extra}")

    if errors:
        print("AI context validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"AI context validation passed: {len(indexes)} active indexes, "
        f"{len(canonical)} canonical skills, {len(ACTIVE_RUNTIME_ROOTS)} current runtime roots, "
        f"{len(language_files)} language-policy files, {ownership_rules} owned rules, "
        f"{canonical_assets} canonical manifests, and {capability_mappings} capability mappings."
    )
    print(
        "Root bilingual entry ownership, links, and structural parity passed "
        "(semantic parity is not asserted)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
