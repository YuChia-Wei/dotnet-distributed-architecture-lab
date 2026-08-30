#!/usr/bin/env python3
"""Validate objective, active AI-context navigation and runtime contracts."""

from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-ai-context.py")

import tomllib
import yaml

from ai_context_cli_routing import validate_cli_execution_routing


ROOT = Path(__file__).resolve().parents[2]
TABLE_PATH = re.compile(r"^\|\s*`([^`]+)`\s*\|")
PATH_REFERENCE = re.compile(r"`([^`\n]+)`|\]\(([^)\s]+)\)")
ACTIVE_SCRIPT_REFERENCE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\./)?(?P<path>\.ai/scripts/[A-Za-z0-9._/-]+\.(?:py|sh))"
)
SOURCE_ONLY_SCRIPT_REFERENCES = frozenset(
    {
        Path(".ai/scripts/tests/test_ai_context_packaging.py"),
        Path(".ai/scripts/tests/test_ai_context_version_governance.py"),
        Path(".ai/scripts/tests/test_governance_workflow_contract.py"),
        Path(".ai/scripts/validate-source-governance.py"),
    }
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
NON_ASCII_AGENT_PUNCTUATION = re.compile(r"[：。]")
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
GOVERNANCE_TERM_ID = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
GOVERNANCE_TERM_DISTRIBUTIONS = {"portable", "source-only"}
GOVERNANCE_TERM_PORTABLE_DISPOSITIONS = {
    "available",
    "upstream-only-non-actionable",
}
ASSET_SCHEMA_VERSIONS = {
    "skill.yaml": "1.0",
    "sub-agent.yaml": "1.1",
}
KEBAB_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ASSET_PORTABILITY = {"portable", "repo-portable", "wrapper-specific"}
ASSET_AUDIENCES = {"agent-facing", "human-facing", "mixed"}
ASSET_SOURCES = {"canonical", "wrapper", "generated"}
ASSET_STATUSES = {"draft", "active", "deprecated", "historical"}
WRAPPER_TARGETS = {"claude", "codex", "copilot"}
SKILL_WRAPPER_CONTRACTS = {
    "codex": {
        "root": PurePosixPath(".agents/skills"),
        "entry": "SKILL.md",
        "identity": "Codex",
        "kind_line": "This is a thin current-runtime wrapper.",
        "use_line": "Use this wrapper only as the current runtime entry.",
    },
    "claude": {
        "root": PurePosixPath(".claude/skills"),
        "entry": "SKILL.md",
        "identity": "Claude",
        "kind_line": "This is a thin Claude-compatible wrapper.",
        "use_line": "Use this wrapper only as a compatibility entry.",
    },
}
DEPRECATED_WRAPPER_KIND_LINE = (
    "This identifier is a deprecated compatibility wrapper."
)
DEPRECATED_WRAPPER_USE_LINE = (
    "Use this wrapper only as a deprecated compatibility entry."
)
PACKAGE_PROFILE = Path(".ai/distribution/profiles/dotnet-backend.yaml")
SUB_AGENT_ADAPTER_CONTRACTS = {
    "codex": {
        "root": PurePosixPath(".codex/agents"),
        "format": "toml",
        "suffixes": (".toml",),
    },
    "claude": {
        "root": PurePosixPath(".claude/agents"),
        "format": "markdown-yaml-frontmatter",
        "suffixes": (".md",),
    },
    "copilot": {
        "root": PurePosixPath(".github/agents"),
        "format": "markdown-yaml-frontmatter",
        "suffixes": (".md", ".agent.md"),
    },
}
ROLE_BINDING_ROOT = PurePosixPath(".ai/assets/sub-agent-role-prompts")
ROLE_BINDING_REQUIRED_FIELDS = {
    "role_path",
    "role_asset_id",
    "expected_role_status",
    "binding_kind",
    "applicability",
    "load_obligation",
}
ROLE_BINDING_KINDS = {"primary", "conditional"}
ROLE_BINDING_EXPECTED_STATUS = "active"
ROLE_BINDING_LOAD_OBLIGATION = "mandatory-when-applicable"
SUB_AGENT_SYSTEM = Path(".ai/SUB-AGENT-SYSTEM.MD")
ROLE_BINDING_PROJECTION_HEADING = "## SAG-001 Derived Role-Binding Projection"
ROLE_BINDING_PROJECTION_HEADERS = (
    "Role Asset ID",
    "Derived Owning Skill",
    "Binding Kind",
    "Canonical Applicability (Projection)",
)
CAPABILITY_PROFILE = Path(
    ".ai/assets/skills/software-development-orchestrator/references/capability-profile.yaml"
)
SAG003_ROLE_IDS = frozenset(
    {
        "mechanical-evidence-worker",
        "reconciliation-worker",
        "semantic-governance-analyst",
        "evidence-report-synthesizer",
        "fixed-head-independent-auditor",
    }
)
SAG003_CAPABILITY_REGISTRY = Path(
    ".ai/assets/shared/provider-neutral-capability-registry.yaml"
)
SAG003_CAPABILITY_REGISTRY_SCHEMA = Path(
    ".ai/assets/shared/provider-neutral-capability-registry.schema.yaml"
)
SAG003_PROVIDER_PROJECTION_REGISTRY = Path(
    ".ai/assets/shared/provider-projection-registry.yaml"
)
SAG003_PROVIDER_PROJECTION_REGISTRY_SCHEMA = Path(
    ".ai/assets/shared/provider-projection-registry.schema.yaml"
)
SAG003_UPGRADER_ROLE_BINDINGS = Path(
    ".ai/assets/skills/ai-context-upgrader/references/role-execution-bindings.yaml"
)
SAG003_EXECUTION_CONTRACT = Path(".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md")
SAG003_MUTATION_BOUNDARIES = {
    "read-only",
    "workflow-authorized-output-only",
}
SAG003_CODEX_PROFILE_ROOT = PurePosixPath(".codex/agents")
SAG003_CODEX_PROFILE_KEYS = {
    "name",
    "description",
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
    "developer_instructions",
}
SAG003_CODEX_PROFILE_NAMES = {
    "mechanical-evidence-worker": "bounded-routine-worker",
    "reconciliation-worker": "reconciliation-worker",
    "semantic-governance-analyst": "semantic-governance-analyst",
    "evidence-report-synthesizer": "evidence-report-synthesizer",
    "fixed-head-independent-auditor": "fixed-head-independent-auditor",
}
SAG003_CODEX_SANDBOX_MODE = "read-only"
SAG003_CANONICAL_PROVIDER_FIELDS = {
    "model",
    "model_reasoning_effort",
    "service_tier",
    "service-tier",
    "fast",
    "sandbox",
    "sandbox_mode",
    "runtime_enabled",
    "runtime-enabled",
    "provider",
    "provider_projection",
    "provider-projection",
    "configured_provider",
    "configuration_state",
    "current_session",
    "current_session_availability",
    "runtime_availability",
    "invocation_evidence",
    "actual_invocation",
    "profile_path",
    "runtime_path",
    "adapter_path",
}
SAG003_CANONICAL_PROVIDER_VALUE = re.compile(
    r"(?:^|[^a-z0-9])(?:gpt(?:-[a-z0-9.-]+)?|claude|copilot|codex|"
    r"model_reasoning_effort|service[ _-]?tier|fast|sandbox(?:_mode)?|"
    r"\.codex/agents|\.claude/agents|\.github/agents)(?:$|[^a-z0-9])",
    re.IGNORECASE,
)
SAG003_STATIC_RUNTIME_CLAIMS = {
    "runtime-enabled",
    "runtime-invoked",
    "invoked",
    "invocation-proven",
    "session-available",
}
UPG004_DELEGATION_RUN_CONTRACT = Path(
    ".ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.md"
)
UPG004_DELEGATION_RUN_SCHEMA = Path(
    ".ai/assets/skills/ai-context-upgrader/references/delegation-run-contract.schema.yaml"
)
UPG004_DELEGATION_RUN_TEMPLATE = Path(
    ".ai/assets/skills/ai-context-upgrader/templates/delegation-run-record.template.yaml"
)
UPG004_UPGRADER_SKILL = Path(".ai/assets/skills/ai-context-upgrader/skill.yaml")
UPG004_WRAPPER_PATHS = (
    Path(".agents/skills/ai-context-upgrader/SKILL.md"),
    Path(".claude/skills/ai-context-upgrader/SKILL.md"),
)
UPG004_CANONICAL_STAGE_IDS = (
    "route-and-evidence-discovery",
    "three-way-classification-and-reconciliation",
    "semantic-customization-and-governance-analysis",
    "plan-report-handoff-or-feedback-synthesis",
    "terminal-fixed-head-independent-audit",
)
UPG004_DELEGATION_MODES = ("none", "analysis-only", "full-recommended")
UPG004_ROLE_ASSET_IDS = (
    "mechanical-evidence-worker",
    "reconciliation-worker",
    "semantic-governance-analyst",
    "evidence-report-synthesizer",
    "fixed-head-independent-auditor",
)
UPG004_ANALYSIS_ONLY_ROLE_ASSET_IDS = (
    "semantic-governance-analyst",
    "fixed-head-independent-auditor",
)
UPG004_ANALYSIS_ONLY_ROOT_AUTHORITIES = (
    "mechanical-evidence",
    "checksum",
    "copy",
    "planner",
    "apply",
    "receipt",
    "build",
    "test",
    "git",
)
UPG004_MODE_SEMANTICS = {
    "none": {
        "eligible_role_asset_ids": [],
        "max_concurrent_workers": 0,
        "allowed_execution_path_kinds": ["root-sequential"],
        "terminal_independent_auditor_auto_selected": False,
    },
    "analysis-only": {
        "eligible_role_asset_ids": list(UPG004_ANALYSIS_ONLY_ROLE_ASSET_IDS),
        "max_concurrent_workers": 2,
        "allowed_execution_path_kinds": [
            "delegation-evaluation",
            "root-sequential",
        ],
        "terminal_independent_auditor_auto_selected": False,
        "root_deterministic_authorities": list(
            UPG004_ANALYSIS_ONLY_ROOT_AUTHORITIES
        ),
    },
    "full-recommended": {
        "eligible_role_asset_ids": list(UPG004_ROLE_ASSET_IDS),
        "max_concurrent_workers": 2,
        "allowed_execution_path_kinds": [
            "delegation-evaluation",
            "root-sequential",
        ],
        "terminal_independent_auditor_auto_selected": False,
    },
}
UPG004_ROOT_FALLBACK_SCOPE = "role-evaluation"
UPG004_TERMINAL_FALLBACK_SCOPE = "terminal-independent-audit"
UPG004_EXECUTION_SUPPORT_STATES = {
    "unknown",
    "verified-available",
    "verified-unavailable",
}
UPG004_TERMINAL_AUDIT_STATUSES = {"pending", "passed", "failed", "blocked"}
PROJECT_CONFIG_TEMPLATE = Path(
    ".ai/assets/skills/ai-context-init/templates/project-config.template.yaml"
)
TECHNOLOGY_SELECTION_SCHEMA = Path(
    ".ai/assets/skills/ai-context-init/templates/technology-selection.schema.yaml"
)
WORK_ITEM_BINDING_SCHEMA = Path(
    ".ai/assets/skills/ai-context-init/templates/work-item-binding.schema.yaml"
)
EXAMPLE_EVIDENCE_SCHEMA = Path(
    ".ai/assets/tech-stacks/dotnet-backend/examples/evidence-schema.yaml"
)
EXAMPLE_EVIDENCE_MANIFEST = Path(
    ".ai/assets/tech-stacks/dotnet-backend/examples/evidence-manifest.yaml"
)
EXAMPLE_PLACEHOLDER_DISPOSITION = Path(
    ".ai/assets/tech-stacks/dotnet-backend/examples/placeholder-disposition.yaml"
)
SOURCE_INCLUDE_EVIDENCE_MANIFEST = Path(
    ".ai/assets/tech-stacks/dotnet-backend/source-includes/evidence-manifest.yaml"
)
SOURCE_GOVERNANCE_REGISTRY = Path(".ai/distribution/governance-checks.yaml")
LESSON_ROOT = Path(".dev/lessons")
LESSON_INDEX = LESSON_ROOT / "INDEX.MD"
LESSON_REQUIRED_PATHS = (
    LESSON_ROOT / "README.MD",
    LESSON_INDEX,
    LESSON_ROOT / "templates/lesson-template.md",
    LESSON_ROOT / "environment/INDEX.MD",
)
LESSON_README_HEADINGS = (
    "## Responsibility",
    "## Boundary",
    "## Identity And Lifecycle",
    "## Required Lesson Packet",
    "## Promotion And Supersession",
    "## Distribution Boundary",
)
LESSON_REQUIRED_SECTIONS = (
    "## Origin Evidence",
    "## Context And Symptom",
    "## Confirmed Conditions And Root Cause",
    "## Reusable Conclusion",
    "## Non-Applicable Cases",
    "## Remediation Example",
    "## Verification",
    "## Promotion And Supersession",
    "## Security And Portability Boundary",
)
LESSON_CATALOG_ROW = re.compile(
    r"^\|\s*`(?P<path>[^`]+)`\s*\|\s*"
    r"`(?P<lesson_id>LESSON-[A-Z0-9]+-\d{3})`\s*\|\s*"
    r"\[[^\]]+\]\((?P<link_path>[^)]+)\)\s*\|\s*"
    r"`(?P<category>[a-z0-9]+(?:-[a-z0-9]+)*)`\s*\|\s*"
    r"`(?P<lifecycle>active|promoted|superseded)`\s*\|"
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


def lesson_table_field(text: str, label: str) -> str | None:
    match = re.search(
        rf"^\|\s*{re.escape(label)}\s*\|\s*(.*?)\s*\|\s*$",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def validate_lesson_contract(
    files: list[Path], errors: list[str], root: Path = ROOT
) -> int:
    """Validate the source repository's non-normative lesson catalog."""
    file_set = set(files)
    for required in LESSON_REQUIRED_PATHS:
        if required not in file_set or not (root / required).is_file():
            errors.append(f"{required}: missing required lesson contract path")

    required_entry_paths = (
        LESSON_ROOT / "README.MD",
        LESSON_INDEX,
        LESSON_ROOT / "templates/lesson-template.md",
    )
    if any(not (root / path).is_file() for path in required_entry_paths):
        return 0

    readme_text = (root / LESSON_ROOT / "README.MD").read_text(encoding="utf-8")
    readme_headings = {line.strip() for line in readme_text.splitlines()}
    for heading in LESSON_README_HEADINGS:
        if heading not in readme_headings:
            errors.append(f"{LESSON_ROOT / 'README.MD'}: missing heading {heading}")

    template_path = LESSON_ROOT / "templates/lesson-template.md"
    template_text = (root / template_path).read_text(encoding="utf-8")
    template_lines = {line.strip() for line in template_text.splitlines()}
    for heading in LESSON_REQUIRED_SECTIONS:
        if heading not in template_lines:
            errors.append(f"{template_path}: missing lesson section {heading}")
    for field in (
        "Lesson ID",
        "Category",
        "Lifecycle",
        "Normative Authority",
        "Origin Evidence",
        "Promotion Target",
        "Supersedes",
        "Superseded By",
    ):
        if f"| {field} |" not in template_text:
            errors.append(f"{template_path}: missing lesson field {field}")

    dev_index_path = Path(".dev/INDEX.md")
    if not (root / dev_index_path).is_file():
        errors.append(f"{dev_index_path}: missing .dev lesson navigation owner")
    else:
        dev_index_text = (root / dev_index_path).read_text(encoding="utf-8")
        for reference in (
            "lessons/README.MD",
            "lessons/INDEX.MD",
            "lessons/environment/",
        ):
            if f"`{reference}`" not in dev_index_text:
                errors.append(f"{dev_index_path}: missing lesson navigation {reference}")

    index_text = (root / LESSON_INDEX).read_text(encoding="utf-8")
    catalog: dict[str, tuple[Path, str, str]] = {}
    indexed_paths: set[Path] = set()
    for line_number, line in enumerate(index_text.splitlines(), 1):
        if re.match(r"^\|\s*`[^`]+`\s*\|\s*`LESSON-", line) is None:
            continue
        match = LESSON_CATALOG_ROW.match(line)
        if match is None:
            errors.append(f"{LESSON_INDEX}:{line_number}: invalid lesson catalog row")
            continue

        lesson_id = match.group("lesson_id")
        category = match.group("category")
        lifecycle = match.group("lifecycle")
        path_text = match.group("path")
        link_path_text = match.group("link_path")
        posix_path = PurePosixPath(path_text)
        if (
            posix_path.is_absolute()
            or "\\" in path_text
            or ".." in posix_path.parts
            or len(posix_path.parts) != 2
            or posix_path.parts[0] != category
            or link_path_text != path_text
            or not posix_path.name.startswith(f"{lesson_id}-")
            or posix_path.suffix != ".md"
        ):
            errors.append(
                f"{LESSON_INDEX}:{line_number}: lesson path must be "
                f"<category>/{lesson_id}-<slug>.md and match category {category}"
            )
            continue

        lesson_path = LESSON_ROOT.joinpath(*posix_path.parts)
        if lesson_id in catalog:
            errors.append(f"{LESSON_INDEX}:{line_number}: duplicate lesson ID {lesson_id}")
            continue
        if lesson_path in indexed_paths:
            errors.append(f"{LESSON_INDEX}:{line_number}: duplicate lesson path {lesson_path}")
            continue
        catalog[lesson_id] = (lesson_path, category, lifecycle)
        indexed_paths.add(lesson_path)

        if lesson_path not in file_set or not (root / lesson_path).is_file():
            errors.append(f"{LESSON_INDEX}:{line_number}: missing lesson path {lesson_path}")
            continue

        lesson_text = (root / lesson_path).read_text(encoding="utf-8")
        lesson_lines = {item.strip() for item in lesson_text.splitlines()}
        if not lesson_text.startswith(f"# {lesson_id}: "):
            errors.append(f"{lesson_path}: H1 must begin with '# {lesson_id}: '")
        expected_fields = {
            "Lesson ID": f"`{lesson_id}`",
            "Category": f"`{category}`",
            "Lifecycle": f"`{lifecycle}`",
            "Normative Authority": "`none`",
        }
        for field, expected in expected_fields.items():
            actual = lesson_table_field(lesson_text, field)
            if actual != expected:
                errors.append(
                    f"{lesson_path}: {field} must be {expected}; actual={actual!r}"
                )
        for field in ("Origin Evidence", "Promotion Target", "Supersedes", "Superseded By"):
            if lesson_table_field(lesson_text, field) is None:
                errors.append(f"{lesson_path}: missing lesson field {field}")
        for heading in LESSON_REQUIRED_SECTIONS:
            if heading not in lesson_lines:
                errors.append(f"{lesson_path}: missing lesson section {heading}")

        none_values = {"none", "`none`"}
        promotion_target = lesson_table_field(lesson_text, "Promotion Target")
        superseded_by = lesson_table_field(lesson_text, "Superseded By")
        if lifecycle == "promoted" and promotion_target in none_values:
            errors.append(f"{lesson_path}: promoted lesson requires Promotion Target")
        if lifecycle == "superseded" and superseded_by in none_values:
            errors.append(f"{lesson_path}: superseded lesson requires Superseded By")

        category_index = LESSON_ROOT / category / "INDEX.MD"
        if category_index not in file_set or not (root / category_index).is_file():
            errors.append(f"{lesson_path}: missing category index {category_index}")
            continue
        category_text = (root / category_index).read_text(encoding="utf-8")
        category_row = re.compile(
            rf"^\|\s*`{re.escape(posix_path.name)}`\s*\|\s*"
            rf"`{re.escape(lesson_id)}`\s*\|\s*"
            rf"\[[^\]]+\]\({re.escape(posix_path.name)}\)\s*\|\s*"
            rf"`{re.escape(lifecycle)}`\s*\|",
            flags=re.MULTILINE,
        )
        if category_row.search(category_text) is None:
            errors.append(
                f"{category_index}: missing {lesson_id} with lifecycle {lifecycle} "
                f"and path {posix_path.name}"
            )

    discovered_lessons = {
        path
        for path in files
        if len(path.parts) == 4
        and path.parts[0:2] == (".dev", "lessons")
        and re.fullmatch(r"LESSON-[A-Z0-9]+-\d{3}-.+\.md", path.name)
    }
    for path in sorted(discovered_lessons - indexed_paths):
        errors.append(f"{path}: lesson document is missing from {LESSON_INDEX}")

    return len(catalog)


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
    source_release_context = (
        (root / ".dev/releases").is_dir()
        and (root / ".ai/distribution").is_dir()
        and (root / ".ai/scripts/ai_context_package.py").is_file()
    )
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
                    if (
                        script_path in SOURCE_ONLY_SCRIPT_REFERENCES
                        and not source_release_context
                    ):
                        continue
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


def validate_work_item_binding_contract(
    errors: list[str],
    root: Path = ROOT,
    template_path: Path = PROJECT_CONFIG_TEMPLATE,
    schema_path: Path = WORK_ITEM_BINDING_SCHEMA,
) -> None:
    """Validate the target-owned work-item binding selection contract."""
    try:
        template = yaml.safe_load((root / template_path).read_text(encoding="utf-8"))
        schema = yaml.safe_load((root / schema_path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"work-item binding contract cannot be loaded: {exc}")
        return

    if not isinstance(template, dict):
        errors.append(f"{template_path}: root must be a mapping")
        return
    if not isinstance(schema, dict):
        errors.append(f"{schema_path}: root must be a mapping")
        return

    work_management = template.get("workManagement")
    binding = (
        work_management.get("workItemBinding")
        if isinstance(work_management, dict)
        else None
    )
    expected_binding = {
        "mode": None,
        "purposes": ["traceability", "work-authorization"],
        "mergeGate": None,
    }
    if binding != expected_binding:
        errors.append(
            f"{template_path}: workManagement.workItemBinding must preserve the unresolved target-selection shape"
        )

    expected_fields = {"mode", "purposes", "mergeGate"}
    required_fields = schema.get("required_fields")
    if not isinstance(required_fields, list) or set(required_fields) != expected_fields:
        errors.append(
            f"{schema_path}: required_fields must equal {sorted(expected_fields)}"
        )

    fixed_purposes = schema.get("fixed_purposes")
    if fixed_purposes != ["traceability", "work-authorization"]:
        errors.append(
            f"{schema_path}: fixed_purposes must preserve traceability and work-authorization"
        )

    allowed = {"required", "optional", "disabled"}
    for key in ("allowed_modes", "allowed_merge_gates"):
        values = schema.get(key)
        if not isinstance(values, list) or set(values) != allowed:
            errors.append(f"{schema_path}: {key} must equal {sorted(allowed)}")

    if schema.get("selection_source") != "explicit-target-decision":
        errors.append(
            f"{schema_path}: selection_source must be explicit-target-decision"
        )
    if schema.get("template_unresolved_value", "missing") is not None:
        errors.append(f"{schema_path}: template_unresolved_value must be null")


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
    """Validate reference-only claims for source-includable framework assets."""
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

        if entry.get("tier") != "reference-only":
            errors.append(f"{label}: SDK-free source includes must declare reference-only tier")

        for field in ("claim", "reason"):
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: reference-only tier requires non-empty {field}")

        validators = entry.get("validators")
        if not isinstance(validators, list):
            errors.append(f"{label}: validators must be a list")
        for field in ("build_commands", "test_commands"):
            value = entry.get(field)
            if not isinstance(value, list) or value:
                errors.append(f"{label}: SDK-free reference-only tier requires empty {field}")

        if "test_project" in entry:
            errors.append(f"{label}: SDK-free reference-only tier must not declare test_project")

        target_validation = entry.get("target_validation")
        if not isinstance(target_validation, dict):
            errors.append(f"{label}: target_validation must be a mapping")
        else:
            if target_validation.get("required") is not True:
                errors.append(f"{label}: target_validation.required must be true")
            responsibility = target_validation.get("responsibility")
            if not isinstance(responsibility, str) or not responsibility.strip():
                errors.append(f"{label}: target_validation.responsibility must be non-empty")


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


def validate_language(
    path: Path, errors: list[str], *, root: Path = ROOT
) -> None:
    """Reject Han prose and selected non-ASCII punctuation outside exact exceptions."""
    allowed_lines = LANGUAGE_ALLOWLIST.get(path, frozenset())
    text = (root / path).read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), 1):
        if line in allowed_lines:
            continue
        if HAN.search(line):
            errors.append(f"{path}:{line_number}: unexpected Han text in agent-facing context")
        if NON_ASCII_AGENT_PUNCTUATION.search(line):
            errors.append(
                f"{path}:{line_number}: unexpected non-ASCII punctuation "
                "in agent-facing context"
            )


def markdown_structure(
    path: Path, *, root: Path = ROOT
) -> tuple[list[int], list[str]]:
    """Return heading levels and ordered path-like backtick values in table rows."""
    headings: list[int] = []
    table_paths: list[str] = []
    fenced = False
    for line in (root / path).read_text(encoding="utf-8").splitlines():
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


def markdown_parity_structure(
    path: Path,
    entry_files: frozenset[str],
    *,
    root: Path = ROOT,
) -> dict[str, object]:
    """Return deterministic Markdown structure without claiming prose equivalence."""
    links: list[str] = []
    fences: list[str] = []
    inline_code: list[str] = []
    table_columns: list[int] = []
    list_markers: list[tuple[int, str]] = []
    fenced = False

    def normalize(value: str) -> str:
        return "<bilingual-entry-file>" if value in entry_files else value

    for line in (root / path).read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            fences.append(stripped)
            fenced = not fenced
            continue
        if fenced:
            continue
        links.extend(
            normalize(value)
            for value in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", line)
        )
        inline_code.extend(
            normalize(value) for value in re.findall(r"`([^`\n]+)`", line)
        )
        if stripped.startswith("|"):
            table_columns.append(len(line.strip().split("|")[1:-1]))
        list_match = re.match(r"^(\s*)([-+*]|\d+\.)\s+", line)
        if list_match:
            list_markers.append((len(list_match.group(1)), list_match.group(2)))

    return {
        "links": links,
        "fences": fences,
        "inline_code": Counter(inline_code),
        "table_columns": table_columns,
        "list_markers": list_markers,
    }


def validate_bilingual_entries(
    errors: list[str], *, root: Path = ROOT
) -> None:
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
            if not (root / path).is_file():
                errors.append(f"missing bilingual entry file: {path}")
        if not (root / canonical).is_file() or not (root / translation).is_file():
            continue
        canonical_text = (root / canonical).read_text(encoding="utf-8")
        translation_text = (root / translation).read_text(encoding="utf-8")
        if canonical_link not in canonical_text:
            errors.append(f"{canonical}: missing reciprocal translation link to {translation}")
        if translation_link not in translation_text:
            errors.append(f"{translation}: missing reciprocal canonical link to {canonical}")
        if canonical_marker not in canonical_text:
            errors.append(f"{canonical}: missing canonical ownership marker")
        if translation_marker not in translation_text:
            errors.append(f"{translation}: missing translation ownership marker")
        canonical_headings, canonical_paths = markdown_structure(canonical, root=root)
        translation_headings, translation_paths = markdown_structure(
            translation, root=root
        )
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
        entry_files = frozenset((canonical.as_posix(), translation.as_posix()))
        canonical_parity = markdown_parity_structure(
            canonical, entry_files, root=root
        )
        translation_parity = markdown_parity_structure(
            translation, entry_files, root=root
        )
        parity_labels = {
            "links": "link-target order",
            "fences": "fence-marker order",
            "inline_code": "inline-code identifier multiset",
            "table_columns": "table-column shape",
            "list_markers": "list-marker shape",
        }
        for key, label in parity_labels.items():
            if canonical_parity[key] != translation_parity[key]:
                errors.append(
                    f"{canonical} <-> {translation}: {label} parity mismatch"
                )

    required_agent_rows = {
        "README.md", "README.en.md", "AGENTS.md", "AGENTS.zh-TW.md", "CLAUDE.md"
    }
    for path in (Path("AGENTS.md"), Path("AGENTS.zh-TW.md")):
        if not (root / path).is_file():
            continue
        _, table_paths = markdown_structure(path, root=root)
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

    identity_model = data.get("identity_model")
    declared_canonical_roots: list[Path] = []

    def add_declared_canonical_root(value: object, label: str) -> None:
        if not isinstance(value, str) or not value:
            errors.append(f"{label} must be a non-empty string")
            return
        pure_root = PurePosixPath(value)
        if (
            Path(value).is_absolute()
            or pure_root.is_absolute()
            or "\\" in value
            or any(part in {".", ".."} for part in pure_root.parts)
        ):
            errors.append(f"{label} must be a safe repository-relative root")
            return
        root_parts = pure_root.parts
        if "<profile>" in root_parts:
            if root_parts.count("<profile>") != 1 or root_parts[-1] != "<profile>":
                errors.append(f"{label} has an invalid <profile> placeholder")
                return
            root_parts = root_parts[: root_parts.index("<profile>")]
        if not root_parts:
            errors.append(f"{label} must resolve to a non-empty root")
            return
        declared_canonical_roots.append(Path(*root_parts))

    def validate_catalog_selector(
        catalog_file: Path,
        catalog_selector: object,
        expected_rule_id: str,
        label: str,
        *,
        projected_record: bool = False,
    ) -> None:
        if catalog_selector != {"rule_id": expected_rule_id}:
            errors.append(
                f"{label}: catalog_selector must be exactly rule_id {expected_rule_id}"
            )
        if catalog_file.suffix not in {".yaml", ".yml"}:
            errors.append(f"{label}: catalog selector requires a YAML catalog")
            return
        try:
            catalog_data = yaml.safe_load(catalog_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{label}: invalid canonical catalog YAML: {exc}")
            return
        catalog_rules = (
            catalog_data.get("rules", []) if isinstance(catalog_data, dict) else []
        )
        matches = [
            item
            for item in catalog_rules
            if isinstance(item, dict) and item.get("rule_id") == expected_rule_id
        ]
        if len(matches) != 1:
            errors.append(
                f"{label}: catalog selector must resolve exactly one rule_id in {catalog_file.relative_to(ROOT)}"
            )
        elif projected_record:
            record_projection = matches[0].get("catalog_projection")
            expected_projection = {
                "path": catalog_file.relative_to(ROOT).as_posix(),
                "selector": {"rule_id": expected_rule_id},
            }
            if record_projection != expected_projection:
                errors.append(
                    f"{label}: projected catalog record must bind the same path and rule_id"
                )
        elif matches[0].get("catalog_selector") != {"rule_id": expected_rule_id}:
            errors.append(
                f"{label}: catalog record selector must be exactly rule_id {expected_rule_id}"
            )

    if not isinstance(identity_model, dict):
        errors.append(f"{OWNERSHIP_REGISTRY}: identity_model must be a mapping")
    else:
        source_governance_root = identity_model.get("source_governance_root")
        portable_baseline_roots = identity_model.get("portable_baseline_roots")
        add_declared_canonical_root(
            source_governance_root,
            f"{OWNERSHIP_REGISTRY}: identity_model.source_governance_root",
        )
        if not isinstance(portable_baseline_roots, dict):
            errors.append(
                f"{OWNERSHIP_REGISTRY}: identity_model.portable_baseline_roots must be a mapping"
            )
        else:
            for root_name, root_value in portable_baseline_roots.items():
                add_declared_canonical_root(
                    root_value,
                    f"{OWNERSHIP_REGISTRY}: portable baseline root {root_name!r}",
                )

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
        canonical_pure = PurePosixPath(canonical_value)
        if (
            not canonical_value
            or Path(canonical_value).is_absolute()
            or canonical_pure.is_absolute()
            or "\\" in canonical_value
            or any(part in {".", ".."} for part in canonical_pure.parts)
        ):
            errors.append(f"{label}: canonical_path must be repository-relative and safe")
            continue
        canonical = Path(*canonical_pure.parts)
        if not any(
            canonical_root == canonical or canonical_root in canonical.parents
            for canonical_root in declared_canonical_roots
        ):
            errors.append(
                f"{label}: canonical_path must be under a declared source-governance or portable baseline root"
            )
            continue
        canonical_file = ROOT / canonical
        if not canonical_file.is_file():
            errors.append(f"{label}: missing canonical_path {canonical}")
            continue
        anchor = rule.get("canonical_anchor")
        canonical_text = canonical_file.read_text(encoding="utf-8")
        selector = (
            re.fullmatch(r"rules\[rule_id=([^\]]+)\]", anchor)
            if isinstance(anchor, str)
            else None
        )
        if selector is not None:
            if selector.group(1) != rule_id:
                errors.append(
                    f"{label}: canonical_anchor selector must match rule_id {rule_id}"
                )
            else:
                validate_catalog_selector(
                    canonical_file, rule.get("catalog_selector"), rule_id, label
                )
        elif not isinstance(anchor, str) or anchor not in canonical_text:
            errors.append(f"{label}: canonical_anchor not found in {canonical}")

        if "catalog_projection" in rule:
            projection = rule.get("catalog_projection")
            projection_label = f"{label}: catalog_projection"
            if not isinstance(projection, dict):
                errors.append(f"{projection_label} must be a mapping")
            else:
                projection_path_value = projection.get("path")
                if (
                    not isinstance(projection_path_value, str)
                    or not projection_path_value
                    or Path(projection_path_value).is_absolute()
                    or "\\" in projection_path_value
                    or any(
                        part in {".", ".."}
                        for part in PurePosixPath(projection_path_value).parts
                    )
                ):
                    errors.append(
                        f"{projection_label}.path must be a safe repository-relative path"
                    )
                else:
                    projection_file = ROOT / projection_path_value
                    if not projection_file.is_file():
                        errors.append(
                            f"{projection_label}.path does not exist: {projection_path_value}"
                        )
                    else:
                        validate_catalog_selector(
                            projection_file,
                            projection.get("selector"),
                            rule_id,
                            projection_label,
                            projected_record=True,
                        )

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


def validate_governance_term_routing_data(
    data: object,
    errors: list[str],
    *,
    root: Path = ROOT,
    source_context: bool | None = None,
) -> int:
    """Validate qualified governance-term routes without redefining their owners."""
    if not isinstance(data, dict):
        errors.append(f"{OWNERSHIP_REGISTRY}: root must be a mapping")
        return 0

    routing = data.get("governance_term_routing")
    if not isinstance(routing, dict):
        errors.append(
            f"{OWNERSHIP_REGISTRY}: governance_term_routing must be a mapping"
        )
        return 0
    if routing.get("schema_version") != "1.0":
        errors.append(
            f"{OWNERSHIP_REGISTRY}: governance_term_routing.schema_version must be 1.0"
        )
    if routing.get("registry_role") != "owner-route-index-not-definition-authority":
        errors.append(
            f"{OWNERSHIP_REGISTRY}: governance_term_routing.registry_role must remain an owner route index"
        )

    expected_contract = {
        "qualified_first_use": "required",
        "bare_alias_scope": "same-clearly-qualified-section-only",
        "cross_owner_authority_inference": "forbidden",
        "machine_literal_change": "explicit-versioned-migration-required",
        "historical_rewrite": "forbidden",
    }
    if routing.get("consumer_contract") != expected_contract:
        errors.append(
            f"{OWNERSHIP_REGISTRY}: governance_term_routing.consumer_contract must preserve the qualified fail-closed contract"
        )

    terms = routing.get("terms")
    if not isinstance(terms, list) or not terms:
        errors.append(
            f"{OWNERSHIP_REGISTRY}: governance_term_routing.terms must be a non-empty list"
        )
        return 0

    if source_context is None:
        source_context = (
            root / ".ai/distribution/profiles/dotnet-backend.yaml"
        ).is_file()

    seen_ids: set[str] = set()
    seen_qualified_terms: set[str] = set()
    for index, term in enumerate(terms):
        label = f"{OWNERSHIP_REGISTRY}:governance_term_routing.terms[{index}]"
        if not isinstance(term, dict):
            errors.append(f"{label}: term must be a mapping")
            continue

        term_id = term.get("term_id")
        namespace = term.get("namespace")
        qualified_term = term.get("qualified_term")
        if not isinstance(term_id, str) or not GOVERNANCE_TERM_ID.fullmatch(term_id):
            errors.append(f"{label}: term_id must be a stable qualified identifier")
        elif term_id in seen_ids:
            errors.append(f"{label}: duplicate term_id {term_id}")
        else:
            seen_ids.add(term_id)
        if not isinstance(namespace, str) or not namespace:
            errors.append(f"{label}: namespace must be a non-empty string")
        elif isinstance(term_id, str) and not term_id.startswith(f"{namespace}."):
            errors.append(f"{label}: term_id must begin with namespace {namespace}.")
        if not isinstance(qualified_term, str) or not qualified_term.strip():
            errors.append(f"{label}: qualified_term must be a non-empty string")
        elif qualified_term in seen_qualified_terms:
            errors.append(f"{label}: duplicate qualified_term {qualified_term!r}")
        else:
            seen_qualified_terms.add(qualified_term)

        distribution = term.get("distribution")
        portable_disposition = term.get("portable_disposition")
        if distribution not in GOVERNANCE_TERM_DISTRIBUTIONS:
            errors.append(f"{label}: invalid distribution {distribution!r}")
        if portable_disposition not in GOVERNANCE_TERM_PORTABLE_DISPOSITIONS:
            errors.append(
                f"{label}: invalid portable_disposition {portable_disposition!r}"
            )
        expected_disposition = (
            "available" if distribution == "portable" else "upstream-only-non-actionable"
        )
        if distribution in GOVERNANCE_TERM_DISTRIBUTIONS and portable_disposition != expected_disposition:
            errors.append(
                f"{label}: {distribution} requires portable_disposition {expected_disposition}"
            )

        owner = term.get("canonical_owner")
        if not isinstance(owner, dict):
            errors.append(f"{label}: canonical_owner must be a mapping")
        else:
            owner_value = owner.get("path")
            anchor = owner.get("anchor")
            owner_path: Path | None = None
            if not isinstance(owner_value, str) or not owner_value:
                errors.append(f"{label}: canonical_owner.path must be non-empty")
            else:
                owner_pure = PurePosixPath(owner_value)
                if (
                    Path(owner_value).is_absolute()
                    or owner_pure.is_absolute()
                    or "\\" in owner_value
                    or any(part in {".", ".."} for part in owner_pure.parts)
                ):
                    errors.append(
                        f"{label}: canonical_owner.path must be safe and repository-relative"
                    )
                else:
                    owner_path = root / Path(*owner_pure.parts)
            if not isinstance(anchor, str) or not anchor:
                errors.append(f"{label}: canonical_owner.anchor must be non-empty")
            elif owner_path is not None:
                owner_required = distribution == "portable" or source_context
                if not owner_path.is_file():
                    if owner_required:
                        errors.append(
                            f"{label}: canonical owner is unavailable: {owner_value}"
                        )
                elif anchor not in owner_path.read_text(encoding="utf-8"):
                    errors.append(
                        f"{label}: canonical_owner.anchor not found in {owner_value}"
                    )

        bindings = term.get("machine_bindings")
        if not isinstance(bindings, list):
            errors.append(f"{label}: machine_bindings must be a list")
        else:
            for binding_index, binding in enumerate(bindings):
                binding_label = f"{label}:machine_bindings[{binding_index}]"
                if not isinstance(binding, dict):
                    errors.append(f"{binding_label}: binding must be a mapping")
                    continue
                for field in ("contract", "field"):
                    value = binding.get(field)
                    if not isinstance(value, str) or not value:
                        errors.append(f"{binding_label}: {field} must be non-empty")
                literals = binding.get("literals")
                if (
                    not isinstance(literals, list)
                    or not literals
                    or not all(isinstance(value, str) and value for value in literals)
                    or len(literals) != len(set(literals))
                ):
                    errors.append(
                        f"{binding_label}: literals must be a non-empty unique string list"
                    )

        shorthand = term.get("contextual_shorthand")
        if not isinstance(shorthand, dict):
            errors.append(f"{label}: contextual_shorthand must be a mapping")
        else:
            aliases = shorthand.get("aliases")
            forbidden = shorthand.get("forbidden_authority_claims")
            allowed_scope = shorthand.get("allowed_scope")
            if (
                not isinstance(aliases, list)
                or not aliases
                or not all(isinstance(value, str) and value for value in aliases)
            ):
                errors.append(f"{label}: aliases must be a non-empty string list")
            if not isinstance(allowed_scope, str) or not allowed_scope:
                errors.append(f"{label}: allowed_scope must be non-empty")
            if (
                not isinstance(forbidden, list)
                or not forbidden
                or not all(isinstance(value, str) and value for value in forbidden)
            ):
                errors.append(
                    f"{label}: forbidden_authority_claims must be a non-empty string list"
                )

    return len(terms)


def validate_governance_term_routing(errors: list[str]) -> int:
    """Load and validate the governance-term section of the ownership registry."""
    registry_path = ROOT / OWNERSHIP_REGISTRY
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{OWNERSHIP_REGISTRY}: governance term routing cannot be loaded: {exc}")
        return 0
    return validate_governance_term_routing_data(data, errors)


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


def wrapper_frontmatter(
    path: Path, text: str, errors: list[str]
) -> dict | None:
    """Parse one Markdown YAML frontmatter mapping without prose fallbacks."""
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append(f"{path}: wrapper must start with YAML frontmatter")
        return None
    raw, _ = text[4:].split("\n---\n", 1)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        errors.append(f"{path}: invalid wrapper frontmatter: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{path}: wrapper frontmatter must be a mapping")
        return None
    return data


def canonical_wrapper_references(path: Path, data: dict) -> set[str]:
    """Collect canonical paths that every runtime wrapper must cite."""
    references = {".ai/assets/skills/README.MD", path.as_posix()}
    for key in ("references", "examples"):
        values = data.get(key, [])
        if isinstance(values, list):
            references.update(value for value in values if isinstance(value, str))
    for key in ("human_guide", "report_template"):
        value = data.get(key)
        if isinstance(value, str):
            references.add(value)
    for key in ("workflow_templates", "report_templates", "assessment_template"):
        values = data.get(key)
        if isinstance(values, dict):
            references.update(value for value in values.values() if isinstance(value, str))
    return references


def normalized_wrapper_projection(
    text: str, target: str, *, deprecated: bool = False
) -> str:
    """Normalize only declared runtime identity and compatibility boilerplate."""
    contract = SKILL_WRAPPER_CONTRACTS[target]
    if deprecated:
        normalized = text.replace(
            DEPRECATED_WRAPPER_KIND_LINE,
            "This identifier is a deprecated compatibility wrapper.",
        )
        normalized = normalized.replace(
            DEPRECATED_WRAPPER_USE_LINE,
            "Use this wrapper only as a deprecated compatibility entry.",
        )
    else:
        normalized = text.replace(
            contract["kind_line"], "This is a thin <runtime> wrapper."
        )
        normalized = normalized.replace(
            contract["use_line"], "Use this wrapper only as the <runtime> entry."
        )
    return normalized.replace(contract["identity"], "<runtime>")


def validate_skill_wrapper_semantics(
    path: Path,
    data: dict,
    errors: list[str],
    *,
    root: Path = ROOT,
) -> None:
    """Validate identity, canonical citations, and cross-runtime projection parity."""
    asset_id = data.get("asset_id")
    targets = data.get("wrapper_targets")
    metadata = data.get("wrapper_metadata")
    if (
        not isinstance(asset_id, str)
        or not isinstance(targets, list)
        or not isinstance(metadata, dict)
    ):
        return

    projections: dict[str, str] = {}
    deprecated = data.get("status") == "deprecated"
    for target in sorted(set(targets) & set(SKILL_WRAPPER_CONTRACTS)):
        target_metadata = metadata.get(target)
        if not isinstance(target_metadata, dict):
            continue
        wrapper_value = target_metadata.get("wrapper_path")
        if not isinstance(wrapper_value, str):
            continue
        contract = SKILL_WRAPPER_CONTRACTS[target]
        expected_directory = contract["root"] / asset_id
        actual_directory = PurePosixPath(wrapper_value.rstrip("/"))
        label = f"{path}: wrapper_metadata.{target}"
        if actual_directory != expected_directory:
            errors.append(
                f"{label}.wrapper_path must be the exact {target} skill directory "
                f"{expected_directory.as_posix()}/"
            )
            continue
        entry = Path(actual_directory.as_posix()) / contract["entry"]
        entry_path = root / entry
        if not entry_path.is_file():
            errors.append(f"{label}: missing wrapper entry file {entry}")
            continue
        text = entry_path.read_text(encoding="utf-8")
        frontmatter = wrapper_frontmatter(entry, text, errors)
        if frontmatter is None:
            continue
        if frontmatter.get("name") != asset_id:
            errors.append(
                f"{entry}: frontmatter name must match canonical asset_id {asset_id}"
            )
        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{entry}: frontmatter description must be non-empty")

        required_references = canonical_wrapper_references(path, data)
        cited = set(re.findall(r"`([^`\n]+)`", text))
        missing = sorted(required_references - cited)
        if missing:
            errors.append(f"{entry}: missing canonical references {missing}")
        authority_line = (
            f"If wrapper text and canonical spec differ, follow `{path.as_posix()}`."
        )
        if authority_line not in text:
            errors.append(f"{entry}: missing exact canonical authority fallback")
        kind_line = (
            DEPRECATED_WRAPPER_KIND_LINE
            if deprecated
            else contract["kind_line"]
        )
        use_line = (
            DEPRECATED_WRAPPER_USE_LINE
            if deprecated
            else contract["use_line"]
        )
        if kind_line not in text or use_line not in text:
            errors.append(f"{entry}: missing exact {target} thin-wrapper identity")
        projections[target] = normalized_wrapper_projection(
            text, target, deprecated=deprecated
        )

    if set(projections) >= {"codex", "claude"} and (
        projections["claude"] != projections["codex"]
    ):
        errors.append(
            f"{path}: Codex and Claude wrappers differ outside declared "
            "runtime identity boilerplate"
        )


def yaml_string_list(value: object) -> list[str]:
    """Normalize one YAML string-or-list field without accepting other types."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def package_glob_matches(path: str, pattern: str) -> bool:
    """Match the package builder's repository-relative glob semantics."""
    expression = ""
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 2
                if index < len(pattern) and pattern[index] == "/":
                    expression += "(?:.*/)?"
                    index += 1
                else:
                    expression += ".*"
                continue
            expression += "[^/]*"
        elif char == "?":
            expression += "[^/]"
        else:
            expression += re.escape(char)
        index += 1
    return bool(re.fullmatch(expression, path))


def package_static_prefix(pattern: str) -> str:
    """Return the package builder's non-wildcard source prefix."""
    wildcard = min(
        (pattern.find(token) for token in ("*", "?") if token in pattern),
        default=-1,
    )
    if wildcard < 0:
        return pattern.rsplit("/", 1)[0] + "/" if "/" in pattern else ""
    slash = pattern.rfind("/", 0, wildcard)
    return pattern[: slash + 1] if slash >= 0 else ""


def package_target_path(entry: dict, source_pattern: str, source_path: str) -> str | None:
    """Project one matched source through the package builder's target rules."""
    target_rule = entry.get("target")
    if target_rule == "preserve-relative-path":
        return source_path
    if isinstance(target_rule, str) and target_rule.endswith("/"):
        prefix = package_static_prefix(source_pattern)
        relative = (
            source_path[len(prefix) :]
            if prefix and source_path.startswith(prefix)
            else PurePosixPath(source_path).name
        )
        return f"{target_rule}{relative}"
    sources = yaml_string_list(entry.get("source"))
    if (
        isinstance(target_rule, str)
        and len(sources) == 1
        and "*" not in source_pattern
        and "?" not in source_pattern
    ):
        return target_rule
    return None


def package_profile_includes(
    adapter_path: str,
    errors: list[str],
    *,
    root: Path = ROOT,
    profile_path: Path = PACKAGE_PROFILE,
) -> bool:
    """Return whether the effective package profile includes one exact adapter file."""
    label = f"{profile_path}: package inclusion for {adapter_path}"
    resolved_profile = root / profile_path
    if not resolved_profile.is_file():
        if (root / ".ai/distribution").is_dir():
            errors.append(f"{label}: source distribution profile is missing")
            return False
        return True
    try:
        profile = yaml.safe_load(resolved_profile.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{label}: cannot load profile: {exc}")
        return False
    if not isinstance(profile, dict):
        errors.append(f"{label}: profile root must be a mapping")
        return False
    entries = profile.get("entries")
    exclusions = profile.get("exclusions", [])
    if not isinstance(entries, list) or not isinstance(exclusions, list):
        errors.append(f"{label}: entries and exclusions must be lists")
        return False

    included = False
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or entry.get("ownership") != "framework-managed"
            or entry.get("install_behavior") != "managed"
        ):
            continue
        for pattern in yaml_string_list(entry.get("source")):
            if package_glob_matches(adapter_path, pattern) and package_target_path(
                entry, pattern, adapter_path
            ) == adapter_path:
                included = True
                break
        if included:
            break
    excluded = False
    for exclusion in exclusions:
        if not isinstance(exclusion, dict):
            continue
        patterns = yaml_string_list(exclusion.get("patterns"))
        exceptions = yaml_string_list(exclusion.get("except"))
        if any(
            package_glob_matches(adapter_path, pattern) for pattern in patterns
        ) and not any(
            package_glob_matches(adapter_path, pattern) for pattern in exceptions
        ):
            excluded = True
            break
    if not included or excluded:
        errors.append(
            f"{label}: adapter must be effectively included as framework-managed payload"
        )
        return False
    return True


def markdown_agent_parts(
    adapter_file: Path, label: str, errors: list[str]
) -> tuple[dict, str] | None:
    """Parse one Markdown custom-agent file with YAML frontmatter."""
    try:
        text = adapter_file.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{label}: cannot read adapter: {exc}")
        return None
    if not text.startswith("---"):
        errors.append(f"{label}: Markdown adapter must start with YAML frontmatter")
        return None
    parts = text.split("---", 2)
    if len(parts) != 3:
        errors.append(f"{label}: Markdown adapter frontmatter is not closed")
        return None
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        errors.append(f"{label}: invalid YAML frontmatter: {exc}")
        return None
    if not isinstance(metadata, dict):
        errors.append(f"{label}: YAML frontmatter must be a mapping")
        return None
    return metadata, parts[2].strip()


def validate_sub_agent_adapter_file(
    target: str,
    adapter_file: Path,
    canonical_path: Path,
    asset_id: str,
    errors: list[str],
) -> None:
    """Validate current runtime schema markers and canonical linkage."""
    label = f"{canonical_path}: adapter_metadata.{target}.adapter_path"
    canonical_reference = canonical_path.as_posix()
    if target == "codex":
        try:
            metadata = tomllib.loads(adapter_file.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{label}: invalid Codex TOML adapter: {exc}")
            return
        body = metadata.get("developer_instructions")
        required = ("name", "description", "developer_instructions")
        missing = [
            key
            for key in required
            if not isinstance(metadata.get(key), str) or not metadata.get(key)
        ]
        if missing:
            errors.append(f"{label}: Codex adapter missing non-empty fields {missing}")
            return
    else:
        parsed = markdown_agent_parts(adapter_file, label, errors)
        if parsed is None:
            return
        metadata, body = parsed
        required = ("name", "description") if target == "claude" else ("description",)
        missing = [
            key
            for key in required
            if not isinstance(metadata.get(key), str) or not metadata.get(key)
        ]
        if missing:
            errors.append(f"{label}: {target} adapter missing non-empty fields {missing}")
            return
        if target == "copilot":
            if "infer" in metadata:
                errors.append(
                    f"{label}: Copilot infer is retired; use disable-model-invocation "
                    "and user-invocable"
                )
            for key in ("disable-model-invocation", "user-invocable"):
                if key in metadata and not isinstance(metadata[key], bool):
                    errors.append(f"{label}: Copilot {key} must be boolean")

    if metadata.get("name") != asset_id:
        errors.append(
            f"{label}: adapter name must equal canonical asset_id {asset_id!r}"
        )
    if not isinstance(body, str) or canonical_reference not in body:
        errors.append(
            f"{label}: adapter must cite canonical role {canonical_reference}"
        )


def validate_sub_agent_adapter_metadata(
    path: Path,
    data: dict,
    errors: list[str],
    *,
    root: Path = ROOT,
    profile_path: Path = PACKAGE_PROFILE,
) -> None:
    """Validate one role's dynamic disposition or exact runtime-adapter contract."""
    targets = data.get("wrapper_targets")
    metadata = data.get("adapter_metadata")
    if not isinstance(targets, list) or not all(isinstance(item, str) for item in targets):
        return
    if len(targets) != len(set(targets)):
        errors.append(f"{path}: wrapper_targets must not contain duplicates")
    if not isinstance(metadata, dict):
        errors.append(f"{path}: adapter_metadata must be a mapping")
        return

    target_set = set(targets)
    metadata_keys = list(metadata)
    non_string_keys = [key for key in metadata_keys if not isinstance(key, str)]
    if non_string_keys:
        errors.append(f"{path}: adapter_metadata keys must be strings: {non_string_keys!r}")
    metadata_set = {key for key in metadata_keys if isinstance(key, str)}
    if metadata_set != target_set:
        errors.append(
            f"{path}: adapter_metadata target parity mismatch; "
            f"missing={sorted(target_set - metadata_set)}, "
            f"extra={sorted(metadata_set - target_set)}"
        )
    if not target_set:
        return

    exact_files = {
        candidate.relative_to(root).as_posix().casefold():
        candidate.relative_to(root).as_posix()
        for candidate in root.rglob("*")
        if candidate.is_file()
    }
    root_resolved = root.resolve()
    adapter_values: list[str] = []
    asset_id = data.get("asset_id")
    if not isinstance(asset_id, str) or not asset_id:
        return

    for target in sorted(target_set & metadata_set):
        target_metadata = metadata[target]
        label = f"{path}: adapter_metadata.{target}"
        contract = SUB_AGENT_ADAPTER_CONTRACTS.get(target)
        if contract is None:
            continue
        if not isinstance(target_metadata, dict):
            errors.append(f"{label} must be a mapping")
            continue
        allowed_keys = {"adapter_path", "adapter_format"}
        extra_keys = sorted(
            (repr(key) for key in target_metadata if key not in allowed_keys)
        )
        if extra_keys:
            errors.append(f"{label}: unsupported keys {extra_keys}")
        adapter_value = target_metadata.get("adapter_path")
        adapter_format = target_metadata.get("adapter_format")
        if not isinstance(adapter_value, str) or not adapter_value:
            errors.append(f"{label}.adapter_path must be a non-empty string")
            continue
        if adapter_format != contract["format"]:
            errors.append(
                f"{label}.adapter_format must be {contract['format']!r}"
            )
        if (
            Path(adapter_value).is_absolute()
            or "\\" in adapter_value
            or any(character in adapter_value for character in "<>*?[]{}")
        ):
            errors.append(
                f"{label}.adapter_path must be a repository-relative exact file "
                "path without placeholders or globs"
            )
            continue
        adapter_path = (root / adapter_value).resolve()
        try:
            adapter_path.relative_to(root_resolved)
        except ValueError:
            errors.append(f"{label}.adapter_path escapes the repository: {adapter_value}")
            continue

        posix_value = PurePosixPath(adapter_value)
        expected_root = contract["root"]
        if posix_value.parts[: len(expected_root.parts)] != expected_root.parts:
            errors.append(
                f"{label}.adapter_path must be under {expected_root.as_posix()}"
            )
        if not any(adapter_value.endswith(suffix) for suffix in contract["suffixes"]):
            errors.append(
                f"{label}.adapter_path uses an unsupported {target} filename format"
            )
        canonical_case = exact_files.get(adapter_value.casefold())
        if canonical_case is not None and canonical_case != adapter_value:
            errors.append(
                f"{label}.adapter_path exact-case mismatch: "
                f"{adapter_value} -> {canonical_case}"
            )
            continue
        if canonical_case is None or not adapter_path.is_file():
            errors.append(f"{label}.adapter_path does not exist: {adapter_value}")
            continue

        adapter_values.append(adapter_value)
        package_profile_includes(
            adapter_value, errors, root=root, profile_path=profile_path
        )
        validate_sub_agent_adapter_file(
            target, adapter_path, path, asset_id, errors
        )

    folded_paths = [value.casefold() for value in adapter_values]
    if len(folded_paths) != len(set(folded_paths)):
        errors.append(f"{path}: adapter paths must be unique across runtime targets")


def expected_role_binding_path(role_asset_id: str) -> str:
    """Return the one canonical role-manifest path for a role asset ID."""
    return (ROLE_BINDING_ROOT / role_asset_id / "sub-agent.yaml").as_posix()


def validate_skill_role_bindings(
    path: Path,
    data: dict,
    role_assets_by_path: dict[str, dict],
    errors: list[str],
) -> list[str]:
    """Validate static role reachability declared by one owning skill only.

    A valid result proves that the canonical role is statically reachable from
    the owning skill. It intentionally does not claim that a runtime read,
    application, delegation, or invocation occurred.
    """
    bindings = data.get("role_bindings")
    if bindings is None:
        return []
    if not isinstance(bindings, list):
        errors.append(f"{path}: role_bindings must be a list")
        return []
    if not bindings:
        errors.append(f"{path}: role_bindings must be non-empty when declared")
        return []

    valid_role_ids: list[str] = []
    declared_role_ids: set[str] = set()
    duplicate_role_ids: set[str] = set()
    declared_role_paths: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"{path}: role_bindings[{index}]"
        if not isinstance(binding, dict):
            errors.append(f"{label} must be a mapping")
            continue

        missing = sorted(ROLE_BINDING_REQUIRED_FIELDS - binding.keys())
        if missing:
            errors.append(f"{label}: missing required fields {missing}")
        extra = sorted(
            repr(key) for key in binding if key not in ROLE_BINDING_REQUIRED_FIELDS
        )
        if extra:
            errors.append(f"{label}: unsupported keys {extra}")

        role_path = binding.get("role_path")
        role_asset_id = binding.get("role_asset_id")
        expected_status = binding.get("expected_role_status")
        binding_kind = binding.get("binding_kind")
        applicability = binding.get("applicability")
        load_obligation = binding.get("load_obligation")
        valid = not missing and not extra

        if not isinstance(role_asset_id, str) or not role_asset_id:
            errors.append(f"{label}.role_asset_id must be a non-empty string")
            valid = False
        if not isinstance(role_path, str) or not role_path:
            errors.append(f"{label}.role_path must be a non-empty string")
            valid = False
        elif isinstance(role_asset_id, str) and role_asset_id:
            expected_path = expected_role_binding_path(role_asset_id)
            if role_path != expected_path:
                errors.append(
                    f"{label}.role_path must be the exact canonical role path "
                    f"{expected_path}"
                )
                valid = False
            if (
                Path(role_path).is_absolute()
                or "\\" in role_path
                or ".." in PurePosixPath(role_path).parts
                or any(character in role_path for character in "<>*?[]{}")
            ):
                errors.append(
                    f"{label}.role_path must be repository-relative without "
                    "placeholders, globs, or escapes"
                )
                valid = False

        if expected_status != ROLE_BINDING_EXPECTED_STATUS:
            errors.append(
                f"{label}.expected_role_status must be "
                f"{ROLE_BINDING_EXPECTED_STATUS!r}"
            )
            valid = False
        if (
            not isinstance(binding_kind, str)
            or binding_kind not in ROLE_BINDING_KINDS
        ):
            errors.append(
                f"{label}.binding_kind must be one of "
                f"{sorted(ROLE_BINDING_KINDS)}"
            )
            valid = False
        if not isinstance(applicability, str) or not applicability.strip():
            errors.append(
                f"{label}.applicability must be a non-empty declarative string"
            )
            valid = False
        if load_obligation != ROLE_BINDING_LOAD_OBLIGATION:
            errors.append(
                f"{label}.load_obligation must be "
                f"{ROLE_BINDING_LOAD_OBLIGATION!r}"
            )
            valid = False

        if isinstance(role_asset_id, str) and role_asset_id:
            if role_asset_id in declared_role_ids:
                errors.append(
                    f"{label}: duplicate role binding for {role_asset_id} "
                    f"in owning skill {data.get('asset_id')!r}"
                )
                duplicate_role_ids.add(role_asset_id)
                valid = False
            declared_role_ids.add(role_asset_id)
        if isinstance(role_path, str) and role_path:
            if role_path in declared_role_paths:
                errors.append(f"{label}: duplicate role_path {role_path}")
                valid = False
            declared_role_paths.add(role_path)

        role_data = (
            role_assets_by_path.get(role_path)
            if isinstance(role_path, str)
            else None
        )
        if role_data is None:
            errors.append(f"{label}.role_path is dangling: {role_path!r}")
            valid = False
        else:
            if role_data.get("asset_id") != role_asset_id:
                errors.append(
                    f"{label}.role_asset_id must exactly match target role asset_id "
                    f"{role_data.get('asset_id')!r}"
                )
                valid = False
            if role_data.get("status") != ROLE_BINDING_EXPECTED_STATUS:
                errors.append(
                    f"{label}: target role status must be "
                    f"{ROLE_BINDING_EXPECTED_STATUS!r}"
                )
                valid = False

        if valid and isinstance(role_asset_id, str):
            valid_role_ids.append(role_asset_id)

    return [
        role_asset_id
        for role_asset_id in valid_role_ids
        if role_asset_id not in duplicate_role_ids
    ]


def validate_active_role_binding_coverage(
    role_assets_by_path: dict[str, dict],
    active_owners_by_role: dict[str, list[Path]],
    errors: list[str],
) -> None:
    """Require at least one active owning skill for every active role."""
    active_roles = sorted(
        (
            (role_data.get("asset_id"), role_path)
            for role_path, role_data in role_assets_by_path.items()
            if role_data.get("status") == ROLE_BINDING_EXPECTED_STATUS
            and isinstance(role_data.get("asset_id"), str)
        ),
        key=lambda item: item[0],
    )
    for role_asset_id, role_path in active_roles:
        owners = active_owners_by_role.get(role_asset_id, [])
        if not owners:
            errors.append(
                f"{role_path}: active role is central-only and ownerless; "
                "declare at least one active owning skill role binding"
            )


def projection_cell_value(value: str) -> str | None:
    """Parse one exact inline-code cell from the derived binding table."""
    match = re.fullmatch(r"`([^`]+)`", value.strip())
    return match.group(1) if match else None


def parse_role_binding_projection(
    projection_path: Path, errors: list[str]
) -> set[tuple[str, str, str, str]] | None:
    """Parse the narrow, derived SAG-001 table without granting it authority."""
    try:
        lines = projection_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"{projection_path}: cannot read SAG-001 projection: {exc}")
        return None

    headings = [
        index
        for index, line in enumerate(lines)
        if line == ROLE_BINDING_PROJECTION_HEADING
    ]
    if len(headings) != 1:
        errors.append(
            f"{projection_path}: must contain exactly one "
            f"{ROLE_BINDING_PROJECTION_HEADING!r} heading"
        )
        return None
    index = headings[0] + 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index + 1 >= len(lines):
        errors.append(f"{projection_path}: SAG-001 projection table is incomplete")
        return None

    def table_cells(line: str) -> list[str] | None:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            return None
        return [cell.strip() for cell in stripped[1:-1].split("|")]

    headers = table_cells(lines[index])
    separator = table_cells(lines[index + 1])
    if headers != list(ROLE_BINDING_PROJECTION_HEADERS):
        errors.append(
            f"{projection_path}: SAG-001 projection headers must be "
            f"{list(ROLE_BINDING_PROJECTION_HEADERS)}"
        )
        return None
    if (
        separator is None
        or len(separator) != len(ROLE_BINDING_PROJECTION_HEADERS)
        or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator)
    ):
        errors.append(f"{projection_path}: SAG-001 projection separator is invalid")
        return None

    rows: set[tuple[str, str, str, str]] = set()
    index += 2
    row_index = 0
    while index < len(lines):
        cells = table_cells(lines[index])
        if cells is None:
            break
        label = f"{projection_path}: SAG-001 projection row {row_index + 1}"
        if len(cells) != len(ROLE_BINDING_PROJECTION_HEADERS):
            errors.append(f"{label} must contain four cells")
            index += 1
            row_index += 1
            continue
        role_asset_id = projection_cell_value(cells[0])
        owning_skill = projection_cell_value(cells[1])
        binding_kind = projection_cell_value(cells[2])
        applicability = cells[3]
        if not role_asset_id or not owning_skill or not binding_kind or not applicability:
            errors.append(
                f"{label} must use non-empty inline-code role, owner, and kind cells "
                "plus a non-empty applicability cell"
            )
            index += 1
            row_index += 1
            continue
        row = (role_asset_id, owning_skill, binding_kind, applicability)
        if row in rows:
            errors.append(f"{label} duplicates a derived role-binding row")
        rows.add(row)
        index += 1
        row_index += 1

    if not rows:
        errors.append(f"{projection_path}: SAG-001 projection must contain rows")
    return rows


def validate_derived_role_binding_projection(
    projection_path: Path,
    canonical_rows: set[tuple[str, str, str, str]],
    errors: list[str],
) -> None:
    """Require the central SAG-001 table to be a projection of canonical bindings."""
    derived_rows = parse_role_binding_projection(projection_path, errors)
    if derived_rows is None:
        return

    canonical_by_role: dict[str, set[tuple[str, str, str]]] = {}
    for role_asset_id, owning_skill, binding_kind, applicability in canonical_rows:
        canonical_by_role.setdefault(role_asset_id, set()).add(
            (owning_skill, binding_kind, applicability)
        )
    derived_by_role: dict[str, set[tuple[str, str, str]]] = {}
    for role_asset_id, owning_skill, binding_kind, applicability in derived_rows:
        derived_by_role.setdefault(role_asset_id, set()).add(
            (owning_skill, binding_kind, applicability)
        )

    for role_asset_id in sorted(set(canonical_by_role) | set(derived_by_role)):
        canonical = canonical_by_role.get(role_asset_id, set())
        derived = derived_by_role.get(role_asset_id, set())
        if not canonical:
            errors.append(
                f"{projection_path}: SAG-001 projection has stale or central-only "
                f"role row {role_asset_id!r}"
            )
        elif not derived:
            errors.append(
                f"{projection_path}: SAG-001 projection is missing canonical "
                f"role row {role_asset_id!r}"
            )
        elif canonical != derived:
            errors.append(
                f"{projection_path}: SAG-001 projection has ambiguous or "
                f"conflicting row(s) for {role_asset_id!r}; canonical={sorted(canonical)!r}, "
                f"derived={sorted(derived)!r}"
            )


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
    skill_manifests: list[tuple[Path, dict]] = []
    role_assets_by_path: dict[str, dict] = {}
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
        expected_schema_version = ASSET_SCHEMA_VERSIONS[path.name]
        if data.get("schema_version") != expected_schema_version:
            errors.append(
                f"{path}: schema_version must be {expected_schema_version}"
            )
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
            skill_manifests.append((path, data))
            validate_wrapper_metadata(path, data, errors)
            validate_skill_wrapper_semantics(path, data, errors)
        else:
            role_assets_by_path[path.as_posix()] = data
            validate_sub_agent_adapter_metadata(path, data, errors)
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

    active_owners_by_role: dict[str, list[Path]] = {}
    canonical_projection_rows: set[tuple[str, str, str, str]] = set()
    for path, data in skill_manifests:
        role_ids = validate_skill_role_bindings(
            path, data, role_assets_by_path, errors
        )
        if data.get("status") != ROLE_BINDING_EXPECTED_STATUS:
            continue
        for role_asset_id in role_ids:
            active_owners_by_role.setdefault(role_asset_id, []).append(path)
        unprojected_role_ids = set(role_ids)
        bindings = data.get("role_bindings")
        if isinstance(bindings, list):
            for binding in bindings:
                if not isinstance(binding, dict):
                    continue
                role_asset_id = binding.get("role_asset_id")
                if role_asset_id not in unprojected_role_ids:
                    continue
                canonical_projection_rows.add(
                    (
                        role_asset_id,
                        data["asset_id"],
                        binding["binding_kind"],
                        binding["applicability"],
                    )
                )
                unprojected_role_ids.remove(role_asset_id)
    validate_active_role_binding_coverage(
        role_assets_by_path, active_owners_by_role, errors
    )
    validate_derived_role_binding_projection(
        ROOT / SUB_AGENT_SYSTEM, canonical_projection_rows, errors
    )

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
    schema_version = profile.get("schema_version")
    if schema_version not in {"1.0", "1.1", "1.2", "1.3", "1.4"}:
        errors.append(
            f"{CAPABILITY_PROFILE}: schema_version must be 1.0, 1.1, 1.2, 1.3, or 1.4"
        )
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
    contracts = profile.get("capability_contracts", {})
    if schema_version in {"1.1", "1.2", "1.3", "1.4"}:
        if not isinstance(contracts, dict):
            errors.append(f"{CAPABILITY_PROFILE}: capability_contracts must be a mapping")
        else:
            test_execution = contracts.get("test-execution")
            expected_contract = {
                "provider_order": [
                    "target-profile-commands",
                    "evaluated-external-skill",
                    "fallback-contract",
                ],
                "default_levels": ["unit", "integration"],
                "conditional_levels": [
                    "e2e",
                    "browser",
                    "playwright",
                    "environment-dependent",
                ],
                "outcomes": [
                    "passed",
                    "failed",
                    "blocked-by-environment",
                    "not-applicable",
                    "deferred-with-owner",
                ],
            }
            if not isinstance(test_execution, dict):
                errors.append(f"{CAPABILITY_PROFILE}: test-execution contract is required")
            else:
                for field, expected_values in expected_contract.items():
                    if test_execution.get(field) != expected_values:
                        errors.append(
                            f"{CAPABILITY_PROFILE}: test-execution.{field} must equal {expected_values}"
                        )
            if "test-execution" not in allowed:
                errors.append(f"{CAPABILITY_PROFILE}: test-execution must be an allowed slot")
            if "test-execution" in required:
                errors.append(f"{CAPABILITY_PROFILE}: test-execution must remain optional")
            if "test-execution" in mappings:
                errors.append(f"{CAPABILITY_PROFILE}: test-execution must not map to an unevaluated skill")
            if schema_version == "1.4":
                expected_long_running = {
                    "threshold_seconds": 120,
                    "always_external_profiles": ["release", "nightly-full"],
                    "always_external_scopes": ["full-matrix"],
                    "dispatch_preconditions": [
                        "tracked-mutations-complete",
                        "focused-validation-complete",
                        "clean-immutable-commit",
                        "exact-command-bounded",
                    ],
                    "execution_surface": "separate-external-runtime-task",
                    "executor_cost_policy": "least-expensive-capable",
                    "primary_conversation_wait_policy": "no-repeated-polling",
                    "completion_signal": "one-final-report",
                    "allowed_write_scope": ["ignored-validation-artifacts"],
                    "non_passing": [
                        "timeout",
                        "interrupted",
                        "missing-completion-evidence",
                        "blocked",
                    ],
                    "delegation_contract": {
                        "schema": ".ai/assets/skills/software-development-orchestrator/templates/external-task-delegation.schema.yaml",
                        "dispatch_template": ".ai/assets/skills/software-development-orchestrator/templates/external-task-dispatch.template.yaml",
                        "completion_template": ".ai/assets/skills/software-development-orchestrator/templates/external-task-completion.template.yaml",
                        "validator": ".ai/assets/skills/software-development-orchestrator/scripts/validate-external-task-delegation.py",
                        "prompt_envelope": [
                            "BEGIN_EXTERNAL_TASK_DELEGATION",
                            "END_EXTERNAL_TASK_DELEGATION",
                        ],
                        "completion_envelope": [
                            "BEGIN_EXTERNAL_TASK_COMPLETION",
                            "END_EXTERNAL_TASK_COMPLETION",
                        ],
                        "source_task_identity": "explicit-or-runtime-injected",
                        "primary_delivery_modes": [
                            "source-task-callback",
                            "parent-event-wait",
                        ],
                        "fallback_delivery_modes": [
                            "parent-event-wait",
                            "single-terminal-readback",
                        ],
                        "parent_wait_timeout_state": "pending-awaiting-completion",
                        "pre_send_completion_validation": "required",
                        "callback_payload": "exact-validated-completion-record",
                    },
                    "parallelization_requires": [
                        "dependency-dag",
                        "artifact-isolation",
                        "bounded-concurrency",
                        "deterministic-evidence",
                        "fail-closed-cancellation",
                    ],
                }
                if test_execution.get("long_running") != expected_long_running:
                    errors.append(
                        f"{CAPABILITY_PROFILE}: test-execution.long_running must match "
                        "the v1.4 external-task delegation contract"
                    )
    if schema_version in {"1.2", "1.3", "1.4"}:
        expected_orchestration = {
            "activation": {
                "intent_class": "high-level-multi-stage-software-development",
                "skill_name_required": False,
                "routing_basis": [
                    "requested-outcome",
                    "current-artifacts",
                    "repository-policy",
                    "approval-state",
                ],
            },
            "approval": {
                "gated_transition": "requirement-design-specification-to-implementation",
                "pending_outcome": "pause-before-implementation",
                "authorization_source_required": True,
            },
            "spec_compliance": {
                "default_selected": False,
                "unselected_outcome": "not-applicable",
                "selected_gate": "100-percent-fail-closed-with-evidence",
            },
            "commit": {
                "checkpoint_unit": "validated-durable-stage-or-coherent-bounded-batch",
                "per_skill_invocation_commits": "prohibited",
                "history_compression": "unshared-unpushed-only",
                "preserve": ["approval", "evidence", "review", "checkpoint", "handoff"],
            },
            "fresh_session": {
                "evidence_sources": [
                    "git",
                    "workflow-locator",
                    "current-task",
                    "target-policy",
                    "registered-handoff-checkpoint",
                ],
                "hidden_context_required": False,
            },
            "closeout_evidence": [
                "approved-requirements-and-specifications",
                "implementation",
                "required-tests",
                "selected-compliance",
                "review",
                "validation",
                "task-state",
                "commits",
                "branch-and-handoff",
            ],
        }
        if schema_version in {"1.3", "1.4"}:
            expected_orchestration["routine_validation"] = {
                "authority": ".dev/project-config.yaml#validation.routine",
                "local_default": "manual",
                "local_modes": ["manual", "auto-if-ready", "required"],
                "local_opt_in": ".dev/validation.local.conf",
                "local_opt_in_rule": "strict-one-line-validation.routine.local",
                "local_opt_in_can_only_strengthen": True,
                "environment_override": "prohibited",
                "implicit_local_write": "prohibited",
                "ci_default": "unconfigured",
                "ci_modes": ["unconfigured", "advisory", "required"],
                "unselected_projection": {
                    "outcome": "not-applicable",
                    "selection_reason": "not-run-by-policy",
                },
                "attempt_budget": {
                    "unselected": 0,
                    "selected_preflight": 1,
                    "initial_execution": 1,
                    "retry_after_material_change": 1,
                    "ci_observations": 2,
                },
                "unaffected": [
                    "explicit-cli",
                    "install",
                    "apply",
                    "init",
                    "upgrade",
                    "provenance",
                    "governance",
                    "release",
                    "publication",
                ],
            }
            expected_orchestration["role_execution"] = {
                "contract": ".ai/assets/shared/ROLE-EXECUTION-CONTRACT.md",
                "producer": "owning-skill",
                "aggregator": "software-development-orchestrator",
                "direct_default": True,
                "dispositions": [
                    "direct",
                    "delegated",
                    "unavailable",
                    "not-applicable",
                ],
                "delegated_requires": [
                    "all-safety-gates",
                    "material-value-trigger",
                    "supports-delegation-risk-result",
                    "genuine-invocation-evidence",
                ],
                "no_delegation_runtime": "direct-when-inline-parity-satisfiable",
            }
        if profile.get("orchestration_contract") != expected_orchestration:
            errors.append(
                f"{CAPABILITY_PROFILE}: orchestration_contract must match the "
                f"v{schema_version} deterministic acceptance contract"
            )
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
        (Path(".ai/assets/skills/software-development-orchestrator/references/capability-profile.md"), "## Capability Mapping"),
        (Path(".ai/assets/skills/software-development-orchestrator/references/routing-playbook.md"), "## Local Profile Resolution"),
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


def sag003_load_yaml_mapping(
    root: Path, path: Path, errors: list[str]
) -> dict | None:
    """Load one required SAG-003 YAML mapping beneath an explicit root."""
    absolute = root / path
    if not absolute.is_file():
        errors.append(f"{path}: required SAG-003 contract file is missing")
        return None
    try:
        value = yaml.safe_load(absolute.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: root must be a mapping")
        return None
    return value


def sag003_exact_keys(
    value: object,
    expected: set[str],
    errors: list[str],
    label: str,
) -> dict | None:
    """Require an exact mapping shape for a non-extensible SAG-003 record."""
    if not isinstance(value, dict):
        errors.append(f"{label} must be a mapping")
        return None
    keys = set(value)
    missing = sorted(expected - keys)
    extra = sorted(repr(key) for key in keys - expected)
    if missing:
        errors.append(f"{label}: missing required fields {missing}")
    if extra:
        errors.append(f"{label}: unsupported fields {extra}")
    return value


def sag003_non_empty_string_list(value: object) -> bool:
    """Return whether a list is non-empty and contains only non-empty strings."""
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def sag003_safe_relative_path(
    value: object,
    errors: list[str],
    label: str,
) -> Path | None:
    """Return a safe repository-relative path without silently normalizing it."""
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty repository-relative path")
        return None
    pure = PurePosixPath(value)
    if (
        Path(value).is_absolute()
        or pure.is_absolute()
        or "\\" in value
        or any(part in {".", ".."} for part in pure.parts)
        or any(character in value for character in "<>*?[]{}")
    ):
        errors.append(f"{label} must be a safe repository-relative exact path")
        return None
    return Path(*pure.parts)


def validate_sag003_provider_neutral_value(
    value: object,
    errors: list[str],
    label: str,
) -> None:
    """Reject provider/runtime settings from the canonical capability authority."""
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                errors.append(f"{label}: canonical field names must be strings")
                continue
            normalized = key.casefold().replace(" ", "_").replace("-", "_")
            forbidden = {
                field.casefold().replace(" ", "_").replace("-", "_")
                for field in SAG003_CANONICAL_PROVIDER_FIELDS
            }
            provider_prefixes = (
                "model_",
                "provider_",
                "runtime_",
                "current_session_",
                "invocation_",
                "service_tier_",
                "sandbox_",
                "codex_",
                "claude_",
                "copilot_",
            )
            if normalized in forbidden or normalized.startswith(provider_prefixes):
                errors.append(
                    f"{label}.{key}: provider/runtime field leaks into the canonical registry"
                )
            validate_sag003_provider_neutral_value(item, errors, f"{label}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_sag003_provider_neutral_value(item, errors, f"{label}[{index}]")
        return
    if isinstance(value, str) and SAG003_CANONICAL_PROVIDER_VALUE.search(value):
        errors.append(
            f"{label}: provider/runtime value leaks into the canonical registry"
        )


def upg004_load_yaml_mapping(
    root: Path, path: Path, errors: list[str]
) -> dict | None:
    """Load one required UPG-004 YAML mapping beneath an explicit root."""
    absolute = root / path
    if not absolute.is_file():
        errors.append(f"{path}: required UPG-004 contract file is missing")
        return None
    try:
        value = yaml.safe_load(absolute.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{path}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: root must be a mapping")
        return None
    return value


def upg004_non_empty_string_list(value: object) -> bool:
    """Return whether a value is a non-empty list of non-empty strings."""
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def upg004_has_exact_stages(value: object) -> bool:
    """Return whether one path retains the ordered canonical stage set."""
    return value == list(UPG004_CANONICAL_STAGE_IDS)


def validate_upg004_codex_delegation_advisory(
    value: object,
    errors: list[str],
    label: str,
) -> None:
    """Validate the static Codex-only advisory without claiming session support."""
    advisory = sag003_exact_keys(
        value,
        {
            "schema_version",
            "configuration_scope",
            "max_concurrent_workers",
            "fast_priority",
            "model_mismatch_disposition",
            "mismatch_prompt_limit",
            "mismatch_choice_boundary",
            "root_preflight",
            "worker_preference",
            "terminal_auditor_preference",
        },
        errors,
        label,
    )
    if advisory is None:
        return
    expected = {
        "schema_version": "1.0",
        "configuration_scope": "static-provider-projection",
        "max_concurrent_workers": 2,
        "fast_priority": "disabled",
        "model_mismatch_disposition": "advisory-one-prompt",
        "mismatch_prompt_limit": 1,
        "mismatch_choice_boundary": "current-vs-recommended/continue-or-switch",
    }
    for field, expected_value in expected.items():
        if advisory.get(field) != expected_value:
            errors.append(f"{label}.{field} must be {expected_value!r}")

    root_preflight = sag003_exact_keys(
        advisory.get("root_preflight"),
        {
            "recommended_root",
            "observed_current_state",
            "quota_cost_disclosure",
            "verified_switch_action",
            "unavailable_fallback",
            "owner_run_fast_priority",
        },
        errors,
        f"{label}.root_preflight",
    )
    if root_preflight is not None:
        recommended_root = sag003_exact_keys(
            root_preflight.get("recommended_root"),
            {"model", "model_reasoning_effort", "service_tier"},
            errors,
            f"{label}.root_preflight.recommended_root",
        )
        if recommended_root is not None and recommended_root != {
            "model": "gpt-5.6-sol",
            "model_reasoning_effort": "xhigh",
            "service_tier": "priority",
        }:
            errors.append(
                f"{label}.root_preflight.recommended_root must be the Sol xhigh priority recommendation"
            )
        observed_current_state = sag003_exact_keys(
            root_preflight.get("observed_current_state"),
            {
                "active_model",
                "active_reasoning_effort",
                "active_speed_service_tier",
                "configuration_default_inference",
            },
            errors,
            f"{label}.root_preflight.observed_current_state",
        )
        if observed_current_state is not None and observed_current_state != {
            "active_model": "unknown",
            "active_reasoning_effort": "unknown",
            "active_speed_service_tier": "unknown",
            "configuration_default_inference": "forbidden",
        }:
            errors.append(
                f"{label}.root_preflight.observed_current_state must remain unknown without configuration-default inference"
            )
        if root_preflight.get("quota_cost_disclosure") != "required-before-switch":
            errors.append(
                f"{label}.root_preflight.quota_cost_disclosure must be 'required-before-switch'"
            )
        verified_switch_action = sag003_exact_keys(
            root_preflight.get("verified_switch_action"),
            {
                "verification_state",
                "shortest_verified_ui_or_command",
                "evidence_refs",
            },
            errors,
            f"{label}.root_preflight.verified_switch_action",
        )
        if verified_switch_action is not None:
            verification_state = verified_switch_action.get("verification_state")
            shortest_action = verified_switch_action.get(
                "shortest_verified_ui_or_command"
            )
            evidence_refs = verified_switch_action.get("evidence_refs")
            if verification_state == "not-verified":
                if shortest_action is not None or evidence_refs != []:
                    errors.append(
                        f"{label}.root_preflight.verified_switch_action may name a shortest UI or command only when verified"
                    )
            elif verification_state == "verified":
                if not isinstance(shortest_action, str) or not shortest_action.strip():
                    errors.append(
                        f"{label}.root_preflight.verified_switch_action.verified requires a non-empty shortest UI or command"
                    )
                if not upg004_non_empty_string_list(evidence_refs):
                    errors.append(
                        f"{label}.root_preflight.verified_switch_action.verified requires evidence refs"
                    )
            else:
                errors.append(
                    f"{label}.root_preflight.verified_switch_action.verification_state must be 'verified' or 'not-verified'"
                )
        unavailable_fallback = sag003_exact_keys(
            root_preflight.get("unavailable_fallback"),
            {"prompt_required", "options"},
            errors,
            f"{label}.root_preflight.unavailable_fallback",
        )
        if unavailable_fallback is not None:
            if unavailable_fallback.get("prompt_required") is not True:
                errors.append(
                    f"{label}.root_preflight.unavailable_fallback.prompt_required must be true"
                )
            if unavailable_fallback.get("options") != [
                "gpt-5.6-terra/xhigh",
                "current-model",
            ]:
                errors.append(
                    f"{label}.root_preflight.unavailable_fallback must ask Terra xhigh or the current model"
                )
        owner_run_fast_priority = sag003_exact_keys(
            root_preflight.get("owner_run_fast_priority"),
            {"status", "activation"},
            errors,
            f"{label}.root_preflight.owner_run_fast_priority",
        )
        if owner_run_fast_priority is not None and owner_run_fast_priority != {
            "status": "disabled",
            "activation": "explicit-owner-choice-required",
        }:
            errors.append(
                f"{label}.root_preflight.owner_run_fast_priority must remain disabled until an explicit owner choice"
            )

    for field, expected_model, expected_fallback in (
        ("worker_preference", "gpt-5.6-terra", "root-sequential"),
        (
            "terminal_auditor_preference",
            "gpt-5.6-sol",
            "fresh-sol-high-independent-context",
        ),
    ):
        preference = sag003_exact_keys(
            advisory.get(field),
            {"model", "model_reasoning_effort", "unavailable_fallback"},
            errors,
            f"{label}.{field}",
        )
        if preference is None:
            continue
        if preference.get("model") != expected_model:
            errors.append(f"{label}.{field}.model must be {expected_model!r}")
        if preference.get("model_reasoning_effort") != "max":
            errors.append(f"{label}.{field}.model_reasoning_effort must be 'max'")
        if preference.get("unavailable_fallback") != expected_fallback:
            errors.append(
                f"{label}.{field}.unavailable_fallback must be {expected_fallback!r}"
            )


def validate_upg004_delegation_run_schema(errors: list[str], *, root: Path) -> bool:
    """Validate the non-extensible portable delegation-record schema."""
    schema = upg004_load_yaml_mapping(root, UPG004_DELEGATION_RUN_SCHEMA, errors)
    if schema is None:
        return False
    expected_fields = {
        "schema_version",
        "document",
        "source_of_truth",
        "required",
        "properties",
        "invariants",
        "additional_properties",
    }
    sag003_exact_keys(schema, expected_fields, errors, str(UPG004_DELEGATION_RUN_SCHEMA))
    if schema.get("schema_version") != "1.0":
        errors.append(f"{UPG004_DELEGATION_RUN_SCHEMA}.schema_version must be '1.0'")
    if schema.get("document") != "delegation-run-record.yaml":
        errors.append(f"{UPG004_DELEGATION_RUN_SCHEMA}.document must be delegation-run-record.yaml")
    if schema.get("source_of_truth") != "workflow-execution-evidence":
        errors.append(
            f"{UPG004_DELEGATION_RUN_SCHEMA}.source_of_truth must be workflow-execution-evidence"
        )
    required = schema.get("required")
    expected_required = {
        "schema_version",
        "delegation_run_id",
        "selection",
        "execution_support",
        "canonical_stage_ids",
        "execution_path",
        "fallbacks",
        "terminal_independent_audit",
    }
    if not isinstance(required, list) or set(required) != expected_required:
        errors.append(f"{UPG004_DELEGATION_RUN_SCHEMA}.required must cover the exact run record")
    if schema.get("additional_properties") is not False:
        errors.append(f"{UPG004_DELEGATION_RUN_SCHEMA}.additional_properties must be false")

    properties = sag003_exact_keys(
        schema.get("properties"),
        expected_required,
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties",
    )
    if properties is None:
        return False
    selection = sag003_exact_keys(
        properties.get("selection"),
        {"required", "supported_modes", "prompt", "resume", "mode_semantics"},
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection",
    )
    if selection is not None:
        expected_selection_required = {
            "mode",
            "max_concurrent_workers",
            "decision_source",
            "owner_choice_evidence",
            "eligible_role_asset_ids",
            "terminal_independent_auditor_auto_selected",
            "prompt",
            "resume",
        }
        if set(selection.get("required", [])) != expected_selection_required:
            errors.append(
                f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.required "
                "must retain the exact mode-eligibility fields"
            )
        if selection.get("supported_modes") != list(UPG004_DELEGATION_MODES):
            errors.append(
                f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.supported_modes "
                "must retain none, analysis-only, and full-recommended"
            )
        for field, fields in (
            ("prompt", {"count", "disposition"}),
            ("resume", {"reuse_existing_selection", "repeat_prompt"}),
        ):
            nested = sag003_exact_keys(
                selection.get(field),
                {"required"},
                errors,
                f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.{field}",
            )
            if nested is not None and set(nested.get("required", [])) != fields:
                errors.append(
                    f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.{field}.required "
                    f"must be {sorted(fields)}"
                )
        mode_semantics = sag003_exact_keys(
            selection.get("mode_semantics"),
            set(UPG004_DELEGATION_MODES),
            errors,
            f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.mode_semantics",
        )
        if mode_semantics is not None:
            for mode, expected_semantics in UPG004_MODE_SEMANTICS.items():
                actual = sag003_exact_keys(
                    mode_semantics.get(mode),
                    set(expected_semantics),
                    errors,
                    f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.mode_semantics.{mode}",
                )
                if actual is not None and actual != expected_semantics:
                    errors.append(
                        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.selection.mode_semantics.{mode} "
                        "must retain the exact fail-closed mode semantics"
                    )
    support = sag003_exact_keys(
        properties.get("execution_support"),
        {"required", "states"},
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.execution_support",
    )
    if support is not None and set(support.get("states", [])) != UPG004_EXECUTION_SUPPORT_STATES:
        errors.append(
            f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.execution_support.states "
            "must retain unknown and both verified states"
        )
    stages = sag003_exact_keys(
        properties.get("canonical_stage_ids"),
        {"ordered_const"},
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.canonical_stage_ids",
    )
    if stages is not None and not upg004_has_exact_stages(stages.get("ordered_const")):
        errors.append(
            f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.canonical_stage_ids "
            "must retain the ordered canonical stages"
        )
    execution_path = sag003_exact_keys(
        properties.get("execution_path"),
        {"required", "kinds"},
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.execution_path",
    )
    if execution_path is not None and set(execution_path.get("kinds", [])) != {
        "delegation-evaluation",
        "root-sequential",
    }:
        errors.append(
            f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.execution_path.kinds "
            "must retain delegation-evaluation and root-sequential"
        )
    fallbacks = sag003_exact_keys(
        properties.get("fallbacks"),
        {"type", "record_required"},
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.fallbacks",
    )
    if fallbacks is not None:
        expected_fallback_fields = {
            "scope",
            "disposition",
            "trigger",
            "requested",
            "observed",
            "selected",
            "owner_consent",
            "authorization_evidence",
            "evidence_refs",
            "canonical_stage_ids",
        }
        if fallbacks.get("type") != "ordered-list":
            errors.append(
                f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.fallbacks.type must be ordered-list"
            )
        if set(fallbacks.get("record_required", [])) != expected_fallback_fields:
            errors.append(
                f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.fallbacks.record_required "
                "must retain exact requested, observed, selected, owner-consent, and evidence fields"
            )
    audit = sag003_exact_keys(
        properties.get("terminal_independent_audit"),
        {"required", "statuses"},
        errors,
        f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.terminal_independent_audit",
    )
    if audit is not None and set(audit.get("statuses", [])) != UPG004_TERMINAL_AUDIT_STATUSES:
        errors.append(
            f"{UPG004_DELEGATION_RUN_SCHEMA}.properties.terminal_independent_audit.statuses "
            "must retain all fail-closed audit states"
        )
    expected_invariants = {
        "per-independent-run-selection",
        "explicit-choice-suppresses-prompt",
        "prompt-count-is-at-most-one",
        "resume-never-repeats-prompt",
        "canonical-stage-order-is-identical-across-paths",
        "mode-eligibility-and-concurrency-are-exact",
        "analysis-only-mechanical-authority-remains-root-driven",
        "terminal-auditor-is-never-automatic",
        "unknown-support-does-not-prove-invocation",
        "fallback-requires-exact-request-observed-selected-owner-consent-and-evidence",
        "terminal-audit-is-explicit-and-fail-closed",
        "record-never-enters-target-provenance",
    }
    if not isinstance(schema.get("invariants"), list) or set(schema["invariants"]) != expected_invariants:
        errors.append(f"{UPG004_DELEGATION_RUN_SCHEMA}.invariants must retain the UPG-004 boundaries")
    return True


def validate_upg004_delegation_run_record(
    record: object,
    errors: list[str],
    *,
    label: str,
) -> bool:
    """Validate one portable delegation record without assuming its retained path."""
    if not isinstance(record, dict):
        errors.append(f"{label}: root must be a mapping")
        return False
    # Keep the existing error-path construction local to this reusable validator.
    UPG004_DELEGATION_RUN_TEMPLATE = Path(label)
    expected_fields = {
        "schema_version",
        "delegation_run_id",
        "selection",
        "execution_support",
        "canonical_stage_ids",
        "execution_path",
        "fallbacks",
        "terminal_independent_audit",
    }
    sag003_exact_keys(record, expected_fields, errors, str(UPG004_DELEGATION_RUN_TEMPLATE))
    validate_sag003_provider_neutral_value(record, errors, str(UPG004_DELEGATION_RUN_TEMPLATE))
    if record.get("schema_version") != "1.0":
        errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.schema_version must be '1.0'")
    if not isinstance(record.get("delegation_run_id"), str) or not record["delegation_run_id"].strip():
        errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.delegation_run_id must be non-empty")

    selection = sag003_exact_keys(
        record.get("selection"),
        {
            "mode",
            "max_concurrent_workers",
            "decision_source",
            "owner_choice_evidence",
            "eligible_role_asset_ids",
            "terminal_independent_auditor_auto_selected",
            "prompt",
            "resume",
        },
        errors,
        f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection",
    )
    if selection is not None:
        mode = selection.get("mode")
        if mode not in UPG004_DELEGATION_MODES:
            errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.mode is not supported")
        mode_semantics = UPG004_MODE_SEMANTICS.get(mode)
        if mode_semantics is not None:
            if (
                selection.get("eligible_role_asset_ids")
                != mode_semantics["eligible_role_asset_ids"]
            ):
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.eligible_role_asset_ids "
                    "must retain the exact mode-eligible roles"
                )
            if (
                selection.get("max_concurrent_workers")
                != mode_semantics["max_concurrent_workers"]
            ):
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.max_concurrent_workers "
                    "must retain the exact mode concurrency"
                )
            if (
                selection.get("terminal_independent_auditor_auto_selected")
                is not mode_semantics["terminal_independent_auditor_auto_selected"]
            ):
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.terminal_independent_auditor_auto_selected "
                    "must remain false"
                )
        elif selection.get("max_concurrent_workers") != 2:
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.max_concurrent_workers must be 2"
            )
        if selection.get("decision_source") not in {
            "explicit-owner-choice",
            "prompted-owner-choice",
        }:
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.decision_source is not supported"
            )
        if not upg004_non_empty_string_list(selection.get("owner_choice_evidence")):
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.owner_choice_evidence "
                "must be a non-empty string list"
            )
        prompt = sag003_exact_keys(
            selection.get("prompt"),
            {"count", "disposition"},
            errors,
            f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.prompt",
        )
        if prompt is not None:
            count = prompt.get("count")
            if isinstance(count, bool) or count not in {0, 1}:
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.prompt.count must be 0 or 1"
                )
            if selection.get("decision_source") == "explicit-owner-choice" and prompt != {
                "count": 0,
                "disposition": "suppressed-by-explicit-choice",
            }:
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.prompt must suppress an explicit choice"
                )
            if selection.get("decision_source") == "prompted-owner-choice" and prompt != {
                "count": 1,
                "disposition": "recorded-owner-choice",
            }:
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.prompt must retain one prompted choice"
                )
        resume = sag003_exact_keys(
            selection.get("resume"),
            {"reuse_existing_selection", "repeat_prompt"},
            errors,
            f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.resume",
        )
        if resume is not None and resume != {
            "reuse_existing_selection": True,
            "repeat_prompt": False,
        }:
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.selection.resume must reuse without a repeat prompt"
            )

    support = sag003_exact_keys(
        record.get("execution_support"),
        {"state", "evidence_refs"},
        errors,
        f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_support",
    )
    if support is not None:
        state = support.get("state")
        evidence_refs = support.get("evidence_refs")
        if state not in UPG004_EXECUTION_SUPPORT_STATES:
            errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_support.state is not supported")
        if state == "unknown" and evidence_refs != []:
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_support.unknown must have no evidence refs"
            )
        if state in {"verified-available", "verified-unavailable"} and not upg004_non_empty_string_list(evidence_refs):
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_support verified states require evidence refs"
            )

    if not upg004_has_exact_stages(record.get("canonical_stage_ids")):
        errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.canonical_stage_ids must retain ordered stages")
    execution_path = sag003_exact_keys(
        record.get("execution_path"),
        {"kind", "canonical_stage_ids"},
        errors,
        f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_path",
    )
    if execution_path is not None:
        if execution_path.get("kind") not in {"delegation-evaluation", "root-sequential"}:
            errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_path.kind is not supported")
        if not upg004_has_exact_stages(execution_path.get("canonical_stage_ids")):
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.execution_path must retain ordered stages"
            )

    fallbacks = record.get("fallbacks")
    if not isinstance(fallbacks, list):
        errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.fallbacks must be a list")
        fallbacks = []
    fallback_scopes: set[str] = set()
    for index, fallback in enumerate(fallbacks):
        label = f"{UPG004_DELEGATION_RUN_TEMPLATE}.fallbacks[{index}]"
        mapping = sag003_exact_keys(
            fallback,
            {
                "scope",
                "disposition",
                "trigger",
                "requested",
                "observed",
                "selected",
                "owner_consent",
                "authorization_evidence",
                "evidence_refs",
                "canonical_stage_ids",
            },
            errors,
            label,
        )
        if mapping is None:
            continue
        validate_sag003_provider_neutral_value(mapping, errors, label)
        scope = mapping.get("scope")
        if scope not in {
            UPG004_ROOT_FALLBACK_SCOPE,
            UPG004_TERMINAL_FALLBACK_SCOPE,
        }:
            errors.append(f"{label}.scope is not supported")
            continue
        if scope in fallback_scopes:
            errors.append(f"{label}.scope duplicates {scope!r}")
        fallback_scopes.add(scope)
        expected_disposition = (
            "root-sequential"
            if scope == UPG004_ROOT_FALLBACK_SCOPE
            else "fresh-independent-context"
        )
        if mapping.get("disposition") != expected_disposition:
            errors.append(f"{label}.disposition must be {expected_disposition!r}")
        expected_requested = (
            "delegation-evaluation"
            if scope == UPG004_ROOT_FALLBACK_SCOPE
            else "terminal-independent-audit"
        )
        expected_observed = (
            "delegation-support-unavailable"
            if scope == UPG004_ROOT_FALLBACK_SCOPE
            else "primary-independent-auditor-unavailable"
        )
        if mapping.get("requested") != expected_requested:
            errors.append(f"{label}.requested must be {expected_requested!r}")
        if mapping.get("observed") != expected_observed:
            errors.append(f"{label}.observed must be {expected_observed!r}")
        if mapping.get("selected") != expected_disposition:
            errors.append(f"{label}.selected must be {expected_disposition!r}")
        if selection is not None and mapping.get("owner_consent") != selection.get(
            "decision_source"
        ):
            errors.append(
                f"{label}.owner_consent must exactly match the run decision_source"
            )
        if not isinstance(mapping.get("trigger"), str) or not mapping["trigger"].strip():
            errors.append(f"{label}.trigger must be non-empty")
        for field in ("authorization_evidence", "evidence_refs"):
            if not upg004_non_empty_string_list(mapping.get(field)):
                errors.append(f"{label}.{field} must be a non-empty string list")
        expected_stages = (
            list(UPG004_CANONICAL_STAGE_IDS)
            if scope == UPG004_ROOT_FALLBACK_SCOPE
            else ["terminal-fixed-head-independent-audit"]
        )
        if mapping.get("canonical_stage_ids") != expected_stages:
            errors.append(f"{label}.canonical_stage_ids does not preserve the required stages")

    if selection is not None and execution_path is not None:
        mode = selection.get("mode")
        path_kind = execution_path.get("kind")
        mode_semantics = UPG004_MODE_SEMANTICS.get(mode)
        if mode_semantics is not None and path_kind not in mode_semantics[
            "allowed_execution_path_kinds"
        ]:
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}: {mode} mode must use one of its exact execution paths"
            )
        if mode == "none" and fallbacks:
            errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}: none mode must not record a fallback")
        if (
            mode != "none"
            and path_kind == "root-sequential"
            and UPG004_ROOT_FALLBACK_SCOPE not in fallback_scopes
        ):
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}: root-sequential fallback requires exact evidence"
            )

    audit = sag003_exact_keys(
        record.get("terminal_independent_audit"),
        {
            "required",
            "selection_basis",
            "status",
            "subject_commit",
            "independence",
            "evidence_refs",
        },
        errors,
        f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit",
    )
    if audit is not None:
        if audit.get("required") is not True:
            errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit.required must be true")
        if audit.get("selection_basis") != "explicit-terminal-or-high-risk":
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit "
                "must use an explicit terminal-or-high-risk basis"
            )
        status = audit.get("status")
        if status not in UPG004_TERMINAL_AUDIT_STATUSES:
            errors.append(f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit.status is not supported")
        if audit.get("independence") != "fresh-independent-context":
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit "
                "must retain fresh-independent-context"
            )
        if status == "pending" and (audit.get("subject_commit") is not None or audit.get("evidence_refs") != []):
            errors.append(
                f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit pending state must not claim evidence"
            )
        if status in {"passed", "failed", "blocked"}:
            subject = audit.get("subject_commit")
            if not isinstance(subject, str) or re.fullmatch(r"[0-9a-f]{40}", subject) is None:
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit "
                    "terminal evidence requires a 40-character lowercase subject commit"
                )
            if not upg004_non_empty_string_list(audit.get("evidence_refs")):
                errors.append(
                    f"{UPG004_DELEGATION_RUN_TEMPLATE}.terminal_independent_audit "
                    "terminal evidence requires non-empty evidence refs"
                )
    return True


def validate_upg004_delegation_run_record_path(
    errors: list[str],
    *,
    root: Path,
    record_path: Path,
) -> bool:
    """Load and validate any retained portable delegation-run record."""
    record = upg004_load_yaml_mapping(root, record_path, errors)
    if record is None:
        return False
    return validate_upg004_delegation_run_record(
        record,
        errors,
        label=str(record_path),
    )


def validate_upg004_delegation_run_template(errors: list[str], *, root: Path) -> bool:
    """Validate the packaged owner-selection template through the reusable path."""
    return validate_upg004_delegation_run_record_path(
        errors,
        root=root,
        record_path=UPG004_DELEGATION_RUN_TEMPLATE,
    )


def validate_upg004_delegation_run_contract(errors: list[str], *, root: Path = ROOT) -> int:
    """Validate portable UPG-004 records, wrappers, and canonical boundaries."""
    document_path = root / UPG004_DELEGATION_RUN_CONTRACT
    if not document_path.is_file():
        errors.append(f"{UPG004_DELEGATION_RUN_CONTRACT}: required UPG-004 contract file is missing")
    else:
        document = document_path.read_text(encoding="utf-8")
        for marker in (
            "# Delegation Run Contract",
            "## Portable Execution Intent",
            "## Modes",
            "selection.eligible_role_asset_ids",
            "`none`",
            "`analysis-only`",
            "`full-recommended`",
            "## Prompt And Resume",
            "## Support And Fallback Evidence",
            "## Terminal Independent Audit",
        ):
            if marker not in document:
                errors.append(f"{UPG004_DELEGATION_RUN_CONTRACT}: missing required marker {marker!r}")

    validate_upg004_delegation_run_schema(errors, root=root)
    validate_upg004_delegation_run_template(errors, root=root)
    required_references = {
        UPG004_DELEGATION_RUN_CONTRACT.as_posix(),
        UPG004_DELEGATION_RUN_SCHEMA.as_posix(),
        UPG004_DELEGATION_RUN_TEMPLATE.as_posix(),
    }
    skill = upg004_load_yaml_mapping(root, UPG004_UPGRADER_SKILL, errors)
    if skill is not None:
        references = skill.get("references")
        if not isinstance(references, list) or not required_references <= set(references):
            errors.append(f"{UPG004_UPGRADER_SKILL}: missing UPG-004 delegation references")
    for wrapper_path in UPG004_WRAPPER_PATHS:
        absolute = root / wrapper_path
        if not absolute.is_file():
            errors.append(f"{wrapper_path}: required current-runtime wrapper is missing")
            continue
        wrapper = absolute.read_text(encoding="utf-8")
        for reference in required_references:
            if reference not in wrapper:
                errors.append(f"{wrapper_path}: missing UPG-004 delegation reference {reference}")
    return 1


def sag003_active_role_binding_owners(
    root: Path,
    errors: list[str],
) -> dict[str, list[tuple[str, Path]]]:
    """Collect only exact, active canonical owners for the five SAG-003 roles."""
    owners: dict[str, list[tuple[str, Path]]] = {
        role_id: [] for role_id in SAG003_ROLE_IDS
    }
    for skill_path in sorted((root / ".ai/assets/skills").glob("*/skill.yaml")):
        try:
            skill = yaml.safe_load(skill_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(skill, dict) or skill.get("status") != "active":
            continue
        skill_id = skill.get("asset_id")
        if not isinstance(skill_id, str) or not skill_id:
            continue
        bindings = skill.get("role_bindings", [])
        if not isinstance(bindings, list):
            continue
        relative_skill_path = skill_path.relative_to(root)
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                continue
            role_id = binding.get("role_asset_id")
            if role_id not in SAG003_ROLE_IDS:
                continue
            label = f"{relative_skill_path}: role_bindings[{index}]"
            expected_path = expected_role_binding_path(role_id)
            valid = True
            if set(binding) != ROLE_BINDING_REQUIRED_FIELDS:
                errors.append(
                    f"{label}: SAG-003 owner binding must use the exact canonical role_binding fields"
                )
                valid = False
            if binding.get("role_path") != expected_path:
                errors.append(
                    f"{label}.role_path must be the exact canonical role path {expected_path}"
                )
                valid = False
            if binding.get("expected_role_status") != ROLE_BINDING_EXPECTED_STATUS:
                errors.append(
                    f"{label}.expected_role_status must be {ROLE_BINDING_EXPECTED_STATUS!r}"
                )
                valid = False
            if binding.get("binding_kind") not in ROLE_BINDING_KINDS:
                errors.append(
                    f"{label}.binding_kind must be one of {sorted(ROLE_BINDING_KINDS)}"
                )
                valid = False
            if not isinstance(binding.get("applicability"), str) or not binding[
                "applicability"
            ].strip():
                errors.append(f"{label}.applicability must be a non-empty declarative string")
                valid = False
            if binding.get("load_obligation") != ROLE_BINDING_LOAD_OBLIGATION:
                errors.append(
                    f"{label}.load_obligation must be {ROLE_BINDING_LOAD_OBLIGATION!r}"
                )
                valid = False
            if valid:
                owners[role_id].append((skill_id, relative_skill_path))
    return owners


def validate_sag003_capability_registry(
    errors: list[str], *, root: Path = ROOT
) -> tuple[dict[str, dict], dict[str, list[tuple[str, Path]]]]:
    """Validate the provider-neutral role authority without making it provider-aware."""
    for schema_path in (
        SAG003_CAPABILITY_REGISTRY_SCHEMA,
        SAG003_PROVIDER_PROJECTION_REGISTRY_SCHEMA,
    ):
        if not (root / schema_path).is_file():
            errors.append(f"{schema_path}: required SAG-003 schema file is missing")

    registry = sag003_load_yaml_mapping(root, SAG003_CAPABILITY_REGISTRY, errors)
    if registry is None:
        return {}, {role_id: [] for role_id in SAG003_ROLE_IDS}
    sag003_exact_keys(
        registry,
        {"schema_version", "registry_id", "source_of_truth", "capabilities"},
        errors,
        str(SAG003_CAPABILITY_REGISTRY),
    )
    if registry.get("schema_version") != "1.0":
        errors.append(f"{SAG003_CAPABILITY_REGISTRY}: schema_version must be '1.0'")
    for field in ("registry_id",):
        if not isinstance(registry.get(field), str) or not registry[field].strip():
            errors.append(f"{SAG003_CAPABILITY_REGISTRY}.{field} must be a non-empty string")
    if registry.get("source_of_truth") != "canonical":
        errors.append(f"{SAG003_CAPABILITY_REGISTRY}.source_of_truth must be 'canonical'")

    capabilities = registry.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append(f"{SAG003_CAPABILITY_REGISTRY}.capabilities must be a list")
        return {}, {role_id: [] for role_id in SAG003_ROLE_IDS}

    capability_by_role: dict[str, dict] = {}
    seen_capability_ids: set[str] = set()
    expected_fields = {
        "capability_id",
        "role_path",
        "role_asset_id",
        "capability_tags",
        "default_mutation_boundary",
        "deterministic_authority",
        "execution_contract",
    }
    for index, capability in enumerate(capabilities):
        label = f"{SAG003_CAPABILITY_REGISTRY}: capabilities[{index}]"
        mapping = sag003_exact_keys(capability, expected_fields, errors, label)
        if mapping is None:
            continue
        validate_sag003_provider_neutral_value(mapping, errors, label)
        capability_id = mapping.get("capability_id")
        if not isinstance(capability_id, str) or not KEBAB_ID.fullmatch(capability_id):
            errors.append(f"{label}.capability_id must be a non-empty kebab-case string")
        elif capability_id in seen_capability_ids:
            errors.append(f"{label}.capability_id duplicates {capability_id!r}")
        else:
            seen_capability_ids.add(capability_id)

        role_id = mapping.get("role_asset_id")
        if not isinstance(role_id, str) or role_id not in SAG003_ROLE_IDS:
            errors.append(f"{label}.role_asset_id must be one of {sorted(SAG003_ROLE_IDS)}")
            continue
        if role_id in capability_by_role:
            errors.append(f"{label}.role_asset_id duplicates {role_id!r}")
            continue
        capability_by_role[role_id] = mapping

        expected_path = expected_role_binding_path(role_id)
        role_path = mapping.get("role_path")
        if role_path != expected_path:
            errors.append(f"{label}.role_path must be the exact canonical role path {expected_path}")
        relative_role_path = sag003_safe_relative_path(role_path, errors, f"{label}.role_path")
        if relative_role_path is not None:
            manifest_path = root / relative_role_path
            if not manifest_path.is_file():
                errors.append(f"{label}.role_path is dangling: {role_path!r}")
            else:
                try:
                    role_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                except (OSError, yaml.YAMLError) as exc:
                    errors.append(f"{label}.role_path cannot load role manifest: {exc}")
                else:
                    if not isinstance(role_manifest, dict):
                        errors.append(f"{label}.role_path role manifest must be a mapping")
                    else:
                        if role_manifest.get("asset_id") != role_id:
                            errors.append(
                                f"{label}.role_asset_id must exactly match the role manifest"
                            )
                        if role_manifest.get("status") != "active":
                            errors.append(f"{label}: target role must be active")
                        if role_manifest.get("wrapper_targets") != [] or role_manifest.get(
                            "adapter_metadata"
                        ) != {}:
                            errors.append(
                                f"{label}: SAG-003 role manifests must remain dynamically loaded "
                                "with empty wrapper_targets and adapter_metadata"
                            )
                        validate_sag003_provider_neutral_value(
                            role_manifest, errors, f"{label}.role_manifest"
                        )

        if not sag003_non_empty_string_list(mapping.get("capability_tags")):
            errors.append(f"{label}.capability_tags must be a non-empty string list")
        elif len(mapping["capability_tags"]) != len(set(mapping["capability_tags"])):
            errors.append(f"{label}.capability_tags must not contain duplicates")
        if mapping.get("default_mutation_boundary") not in SAG003_MUTATION_BOUNDARIES:
            errors.append(
                f"{label}.default_mutation_boundary must be one of "
                f"{sorted(SAG003_MUTATION_BOUNDARIES)}"
            )
        authority = sag003_exact_keys(
            mapping.get("deterministic_authority"),
            {"required", "surfaces", "agent_boundary"},
            errors,
            f"{label}.deterministic_authority",
        )
        if authority is not None:
            if authority.get("required") is not True:
                errors.append(
                    f"{label}.deterministic_authority.required must be true"
                )
            if not sag003_non_empty_string_list(authority.get("surfaces")):
                errors.append(
                    f"{label}.deterministic_authority.surfaces must be a non-empty string list"
                )
            if not isinstance(authority.get("agent_boundary"), str) or not authority[
                "agent_boundary"
            ].strip():
                errors.append(
                    f"{label}.deterministic_authority.agent_boundary must be a non-empty string"
                )
        if mapping.get("execution_contract") != SAG003_EXECUTION_CONTRACT.as_posix():
            errors.append(
                f"{label}.execution_contract must be "
                f"{SAG003_EXECUTION_CONTRACT.as_posix()!r}"
            )

    if set(capability_by_role) != SAG003_ROLE_IDS:
        errors.append(
            f"{SAG003_CAPABILITY_REGISTRY}: role_asset_ids must be exactly "
            f"{sorted(SAG003_ROLE_IDS)}; actual={sorted(capability_by_role)}"
        )

    owners = sag003_active_role_binding_owners(root, errors)
    for role_id in sorted(SAG003_ROLE_IDS):
        matching_owners = owners[role_id]
        if not matching_owners:
            errors.append(
                f"{SAG003_CAPABILITY_REGISTRY}: {role_id} is central-only and ownerless; "
                "require at least one active owning-skill role_binding"
            )
    return capability_by_role, owners


def validate_sag003_codex_profile(
    root: Path,
    profile: dict,
    errors: list[str],
    label: str,
) -> None:
    """Validate one static Codex projection without claiming it was loaded."""
    profile_path = profile.get("profile_path")
    relative = sag003_safe_relative_path(profile_path, errors, f"{label}.profile_path")
    if relative is None:
        return
    expected_root = SAG003_CODEX_PROFILE_ROOT.parts
    if PurePosixPath(profile_path).parts[: len(expected_root)] != expected_root:
        errors.append(
            f"{label}.profile_path must be under {SAG003_CODEX_PROFILE_ROOT.as_posix()}"
        )
        return
    if not str(profile_path).endswith(".toml"):
        errors.append(f"{label}.profile_path must name a TOML file")
        return
    file_path = root / relative
    if not file_path.is_file():
        errors.append(f"{label}.profile_path does not exist: {profile_path}")
        return
    exact_paths = {
        item.relative_to(root).as_posix().casefold(): item.relative_to(root).as_posix()
        for item in (root / Path(*expected_root)).rglob("*.toml")
        if item.is_file()
    }
    exact_path = exact_paths.get(str(profile_path).casefold())
    if exact_path != profile_path:
        errors.append(
            f"{label}.profile_path has an exact-case mismatch: {profile_path!r} -> {exact_path!r}"
        )
        return
    try:
        toml = tomllib.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"{label}.profile_path is not valid Codex TOML: {exc}")
        return
    missing = sorted(SAG003_CODEX_PROFILE_KEYS - set(toml))
    extra = sorted(repr(key) for key in set(toml) - SAG003_CODEX_PROFILE_KEYS)
    if missing:
        errors.append(f"{label}.profile_path is missing Codex profile fields {missing}")
    if extra:
        errors.append(f"{label}.profile_path has unsupported Codex profile fields {extra}")
    for field in SAG003_CODEX_PROFILE_KEYS:
        if not isinstance(toml.get(field), str) or not toml[field].strip():
            errors.append(f"{label}.profile_path.{field} must be a non-empty string")
    role_id = profile.get("role_asset_id")
    expected_profile_name = (
        SAG003_CODEX_PROFILE_NAMES.get(role_id) if isinstance(role_id, str) else None
    )
    if expected_profile_name is None:
        errors.append(f"{label}.role_asset_id has no allowed Codex profile-name projection")
    elif (
        profile.get("profile_name") != expected_profile_name
        or toml.get("name") != expected_profile_name
    ):
        errors.append(
            f"{label}: profile_name and TOML name must equal the allowed Codex projection "
            f"{expected_profile_name!r}"
        )
    for field in ("model", "model_reasoning_effort", "sandbox_mode"):
        if toml.get(field) != profile.get(field):
            errors.append(f"{label}: TOML {field} must match the static projection registry")
    canonical_role_path = expected_role_binding_path(role_id) if isinstance(role_id, str) else ""
    if canonical_role_path and canonical_role_path not in str(toml.get("developer_instructions", "")):
        errors.append(f"{label}.profile_path must cite canonical role {canonical_role_path}")
    instructions = str(toml.get("developer_instructions", "")).casefold()
    if any(claim in instructions for claim in SAG003_STATIC_RUNTIME_CLAIMS):
        errors.append(f"{label}.profile_path must not fabricate runtime-enabled or invoked evidence")


def validate_sag003_provider_projection_registry(
    capability_by_role: dict[str, dict],
    errors: list[str],
    *,
    root: Path = ROOT,
) -> list[str]:
    """Validate static provider projections while retaining an unknown session state."""
    registry = sag003_load_yaml_mapping(root, SAG003_PROVIDER_PROJECTION_REGISTRY, errors)
    if registry is None:
        return []
    expected_fields = {
        "schema_version",
        "registry_id",
        "source_of_truth",
        "canonical_contract",
        "provider_projections",
        "current_session",
        "package_projection",
    }
    sag003_exact_keys(registry, expected_fields, errors, str(SAG003_PROVIDER_PROJECTION_REGISTRY))
    if registry.get("schema_version") != "1.0":
        errors.append(f"{SAG003_PROVIDER_PROJECTION_REGISTRY}: schema_version must be '1.0'")
    if not isinstance(registry.get("registry_id"), str) or not registry["registry_id"].strip():
        errors.append(f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.registry_id must be a non-empty string")
    if registry.get("source_of_truth") != "canonical":
        errors.append(f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.source_of_truth must be 'canonical'")

    canonical = sag003_exact_keys(
        registry.get("canonical_contract"),
        {"availability", "registry_path", "role_asset_ids", "delegation_intent"},
        errors,
        f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.canonical_contract",
    )
    if canonical is not None:
        validate_sag003_provider_neutral_value(
            canonical,
            errors,
            f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.canonical_contract",
        )
        if canonical.get("availability") != "canonical-contract-available":
            errors.append("provider projection canonical_contract.availability must be canonical-contract-available")
        if canonical.get("registry_path") != SAG003_CAPABILITY_REGISTRY.as_posix():
            errors.append("provider projection canonical_contract.registry_path must bind the capability registry")
        role_ids = canonical.get("role_asset_ids")
        if not isinstance(role_ids, list) or len(role_ids) != len(set(role_ids)) or set(role_ids) != SAG003_ROLE_IDS:
            errors.append("provider projection canonical_contract.role_asset_ids must be the exact five SAG-003 roles")
        intent = sag003_exact_keys(
            canonical.get("delegation_intent"),
            {
                "root_capability",
                "delegated_capability",
                "quality_posture",
                "delegation",
                "quota_sensitivity",
                "fallback",
            },
            errors,
            f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.canonical_contract.delegation_intent",
        )
        if intent is not None and intent != {
            "root_capability": "frontier",
            "delegated_capability": "balanced",
            "quality_posture": "quality-first",
            "delegation": "optional",
            "quota_sensitivity": "quota-sensitive",
            "fallback": "disclosed",
        }:
            errors.append(
                "provider projection canonical_contract.delegation_intent must retain only the portable frontier/balanced/quality-first optional quota-sensitive disclosed intent"
            )
    if set(capability_by_role) != SAG003_ROLE_IDS:
        errors.append("provider projection cannot be valid while the canonical capability set is incomplete")

    projections = sag003_exact_keys(
        registry.get("provider_projections"),
        {"codex", "claude", "copilot"},
        errors,
        f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.provider_projections",
    )
    codex_paths: list[str] = []
    if projections is not None:
        codex = sag003_exact_keys(
            projections.get("codex"),
            {"configuration_state", "delegation_advisory", "profiles"},
            errors,
            f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.provider_projections.codex",
        )
        if codex is not None:
            if codex.get("configuration_state") != "codex-runtime-configured":
                errors.append("Codex projection must be statically configured, not runtime-enabled")
            validate_upg004_codex_delegation_advisory(
                codex.get("delegation_advisory"),
                errors,
                f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.provider_projections.codex.delegation_advisory",
            )
            profiles = codex.get("profiles")
            if not isinstance(profiles, list):
                errors.append("Codex projection profiles must be a list")
            else:
                seen_roles: set[str] = set()
                seen_paths: set[str] = set()
                profile_fields = {
                    "role_asset_id",
                    "profile_path",
                    "profile_name",
                    "model",
                    "model_reasoning_effort",
                    "sandbox_mode",
                }
                for index, profile in enumerate(profiles):
                    label = f"Codex projection profiles[{index}]"
                    mapping = sag003_exact_keys(profile, profile_fields, errors, label)
                    if mapping is None:
                        continue
                    role_id = mapping.get("role_asset_id")
                    if not isinstance(role_id, str) or role_id not in SAG003_ROLE_IDS:
                        errors.append(f"{label}.role_asset_id must be one of the five SAG-003 roles")
                    elif role_id in seen_roles:
                        errors.append(f"{label}.role_asset_id duplicates {role_id!r}")
                    else:
                        seen_roles.add(role_id)
                    for field in ("profile_path", "profile_name", "model", "model_reasoning_effort"):
                        if not isinstance(mapping.get(field), str) or not mapping[field].strip():
                            errors.append(f"{label}.{field} must be a non-empty string")
                    if mapping.get("sandbox_mode") != SAG003_CODEX_SANDBOX_MODE:
                        errors.append(
                            f"{label}.sandbox_mode must remain read-only for SAG-003"
                        )
                    profile_path = mapping.get("profile_path")
                    if isinstance(profile_path, str):
                        if profile_path in seen_paths:
                            errors.append(f"{label}.profile_path duplicates {profile_path!r}")
                        else:
                            seen_paths.add(profile_path)
                            codex_paths.append(profile_path)
                    validate_sag003_codex_profile(root, mapping, errors, label)
                if seen_roles != SAG003_ROLE_IDS:
                    errors.append("Codex projection profiles must cover the exact five SAG-003 roles")

        for provider in ("claude", "copilot"):
            mapping = sag003_exact_keys(
                projections.get(provider),
                {"configuration_state", "profiles", "deferred_reason"},
                errors,
                f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.provider_projections.{provider}",
            )
            if mapping is None:
                continue
            if mapping.get("configuration_state") != f"{provider}-runtime-deferred":
                errors.append(f"{provider} projection must remain runtime-deferred, never unsupported")
            if mapping.get("profiles") != []:
                errors.append(f"{provider} deferred projection profiles must be an empty list")
            if not isinstance(mapping.get("deferred_reason"), str) or not mapping[
                "deferred_reason"
            ].strip():
                errors.append(f"{provider} deferred projection requires a non-empty deferred_reason")

    current_session = sag003_exact_keys(
        registry.get("current_session"),
        {"availability", "invocation_evidence"},
        errors,
        f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.current_session",
    )
    if current_session is not None and current_session != {
        "availability": "unknown",
        "invocation_evidence": "not-claimed",
    }:
        errors.append("provider projection current_session must remain unknown with invocation not-claimed")

    package_projection = sag003_exact_keys(
        registry.get("package_projection"),
        {"configured_provider", "profile_paths", "deferred_provider_runtime_paths"},
        errors,
        f"{SAG003_PROVIDER_PROJECTION_REGISTRY}.package_projection",
    )
    if package_projection is not None:
        if package_projection.get("configured_provider") != "codex":
            errors.append("package_projection.configured_provider must be codex")
        paths = package_projection.get("profile_paths")
        if not isinstance(paths, list) or len(paths) != len(set(paths)) or set(paths) != set(codex_paths):
            errors.append("package_projection.profile_paths must exactly equal configured Codex paths")
        if package_projection.get("deferred_provider_runtime_paths") != []:
            errors.append("package_projection must not include Claude or Copilot deferred runtime paths")

    def reject_static_claims(value: object, label: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(key, str) and key.casefold() in {"invoked", "runtime_enabled", "runtime-enabled"}:
                    errors.append(f"{label}.{key}: static configuration cannot claim invocation or runtime enabled")
                reject_static_claims(item, f"{label}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_static_claims(item, f"{label}[{index}]")
        elif isinstance(value, str) and value.casefold() in SAG003_STATIC_RUNTIME_CLAIMS:
            errors.append(f"{label}: static configuration cannot claim {value!r}")

    reject_static_claims(registry, str(SAG003_PROVIDER_PROJECTION_REGISTRY))
    return codex_paths


def validate_sag003_upgrader_role_bindings(
    owners: dict[str, list[tuple[str, Path]]],
    errors: list[str],
    *,
    root: Path = ROOT,
) -> int:
    """Validate the upgrader's bounded-role plan against canonical skill bindings."""
    manifest = sag003_load_yaml_mapping(root, SAG003_UPGRADER_ROLE_BINDINGS, errors)
    if manifest is None:
        return 0
    expected_fields = {
        "schema_version",
        "binding_manifest_id",
        "owning_skill",
        "role_binding_authority",
        "execution_contract",
        "role_bindings",
    }
    sag003_exact_keys(manifest, expected_fields, errors, str(SAG003_UPGRADER_ROLE_BINDINGS))
    if manifest.get("schema_version") != "1.0":
        errors.append(f"{SAG003_UPGRADER_ROLE_BINDINGS}: schema_version must be '1.0'")
    if not isinstance(manifest.get("binding_manifest_id"), str) or not manifest[
        "binding_manifest_id"
    ].strip():
        errors.append(f"{SAG003_UPGRADER_ROLE_BINDINGS}.binding_manifest_id must be non-empty")
    if manifest.get("owning_skill") != "ai-context-upgrader":
        errors.append(f"{SAG003_UPGRADER_ROLE_BINDINGS}.owning_skill must be ai-context-upgrader")
    if not isinstance(manifest.get("role_binding_authority"), str) or not manifest[
        "role_binding_authority"
    ].strip():
        errors.append(f"{SAG003_UPGRADER_ROLE_BINDINGS}.role_binding_authority must be non-empty")
    if manifest.get("execution_contract") != SAG003_EXECUTION_CONTRACT.as_posix():
        errors.append(
            f"{SAG003_UPGRADER_ROLE_BINDINGS}.execution_contract must be "
            f"{SAG003_EXECUTION_CONTRACT.as_posix()!r}"
        )

    bindings = manifest.get("role_bindings")
    if not isinstance(bindings, list):
        errors.append(f"{SAG003_UPGRADER_ROLE_BINDINGS}.role_bindings must be a list")
        return 0
    binding_fields = {
        "role_asset_id",
        "role_path",
        "recommendation",
        "stage",
        "inputs",
        "outputs",
        "mutation_boundary",
        "concurrency",
        "stop_and_escalation",
        "direct_sequential_fallback",
        "selection_guard",
    }
    seen_roles: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"{SAG003_UPGRADER_ROLE_BINDINGS}: role_bindings[{index}]"
        mapping = sag003_exact_keys(binding, binding_fields, errors, label)
        if mapping is None:
            continue
        role_id = mapping.get("role_asset_id")
        if not isinstance(role_id, str) or role_id not in SAG003_ROLE_IDS:
            errors.append(f"{label}.role_asset_id must be one of the five SAG-003 roles")
            continue
        if role_id in seen_roles:
            errors.append(f"{label}.role_asset_id duplicates {role_id!r}")
        seen_roles.add(role_id)
        expected_path = expected_role_binding_path(role_id)
        if mapping.get("role_path") != expected_path:
            errors.append(f"{label}.role_path must be the exact canonical role path {expected_path}")
        if mapping.get("recommendation") not in {"recommended", "optional"}:
            errors.append(f"{label}.recommendation must be recommended or optional")
        for field in ("stage", "inputs", "outputs", "stop_and_escalation", "selection_guard"):
            if not sag003_non_empty_string_list(mapping.get(field)):
                errors.append(f"{label}.{field} must be a non-empty string list")
        if mapping.get("mutation_boundary") not in SAG003_MUTATION_BOUNDARIES:
            errors.append(f"{label}.mutation_boundary must be a supported SAG-003 boundary")
        concurrency = sag003_exact_keys(
            mapping.get("concurrency"),
            {"maximum_parallel_instances", "disjoint_scope_required"},
            errors,
            f"{label}.concurrency",
        )
        if concurrency is not None:
            maximum = concurrency.get("maximum_parallel_instances")
            if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
                errors.append(f"{label}.concurrency.maximum_parallel_instances must be an integer >= 1")
            if not isinstance(concurrency.get("disjoint_scope_required"), bool):
                errors.append(f"{label}.concurrency.disjoint_scope_required must be boolean")
        fallback = sag003_exact_keys(
            mapping.get("direct_sequential_fallback"),
            {"allowed", "same_contract_required"},
            errors,
            f"{label}.direct_sequential_fallback",
        )
        if fallback is not None and fallback != {
            "allowed": True,
            "same_contract_required": True,
        }:
            errors.append(f"{label}.direct_sequential_fallback must allow only same-contract direct fallback")

        if role_id == "fixed-head-independent-auditor":
            guard = " ".join(mapping.get("selection_guard", [])).casefold()
            has_terminal_high_risk = "terminal" in guard and "high-risk" in guard
            has_routine_profile_prohibition = (
                "routine" in guard
                and "profile" in guard
                and any(token in guard for token in ("only", "not", "reject", "prohibit"))
            )
            if not has_terminal_high_risk or not has_routine_profile_prohibition:
                errors.append(
                    f"{label}.selection_guard must restrict the terminal auditor to explicit "
                    "terminal/high-risk gates and reject routine task/profile presence"
                )

        owner_records = owners.get(role_id, [])
        upgrader_records = [
            record for record in owner_records if record[0] == "ai-context-upgrader"
        ]
        if upgrader_records != [
            ("ai-context-upgrader", Path(".ai/assets/skills/ai-context-upgrader/skill.yaml"))
        ]:
            errors.append(
                f"{label}: ai-context-upgrader must have exactly one active canonical role_binding; "
                f"actual={[(owner, str(path)) for owner, path in owner_records]!r}"
            )

    if seen_roles != SAG003_ROLE_IDS:
        errors.append(
            f"{SAG003_UPGRADER_ROLE_BINDINGS}.role_bindings must cover the exact five SAG-003 roles"
        )
    return len(seen_roles)


def validate_sag003_provider_role_projection_contract(
    errors: list[str], *, root: Path = ROOT
) -> int:
    """Bind provider-neutral roles, static projections, and upgrader use without runtime claims."""
    capability_by_role, owners = validate_sag003_capability_registry(errors, root=root)
    validate_sag003_provider_projection_registry(capability_by_role, errors, root=root)
    return validate_sag003_upgrader_role_bindings(owners, errors, root=root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    errors: list[str] = []
    files = tracked_files()
    indexes = active_indexes(files)

    validate_exact_case_references(files, errors)
    validate_active_script_references(files, errors)
    validate_technology_selection_contract(errors)
    validate_work_item_binding_contract(errors)
    validate_example_evidence_contract(errors)
    validate_example_placeholder_disposition(errors)
    validate_source_include_evidence(errors)
    cli_routes = validate_cli_execution_routing(errors, root=ROOT)
    lesson_count = 0
    if (ROOT / SOURCE_GOVERNANCE_REGISTRY).is_file():
        lesson_count = validate_lesson_contract(files, errors)

    for index in indexes:
        validate_index(index, errors)

    index_set = set(indexes)
    language_files = [path for path in files if is_language_surface(path, index_set)]
    for path in language_files:
        validate_language(path, errors)

    validate_bilingual_entries(errors)
    validate_runtime_entries(files, errors)
    ownership_rules = validate_rule_ownership(errors)
    governance_terms = validate_governance_term_routing(errors)
    canonical_assets, skill_assets = validate_canonical_assets(errors)
    capability_mappings = validate_capability_profile(skill_assets, errors)
    sag003_role_bindings = validate_sag003_provider_role_projection_contract(errors)
    upg004_delegation_contracts = validate_upg004_delegation_run_contract(errors)

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
        f"{governance_terms} qualified governance terms, {canonical_assets} canonical manifests, "
        f"{capability_mappings} capability mappings, "
        f"{sag003_role_bindings} SAG-003 role bindings, "
        f"{upg004_delegation_contracts} UPG-004 delegation contracts, "
        f"{cli_routes} local CLI routes, and {lesson_count} governed lessons."
    )
    print(
        "Root bilingual entry ownership, links, and structural parity passed "
        "(semantic parity is not asserted)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
