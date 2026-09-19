"""Pure canonical-to-runtime projection helpers for the selected COST-001 pilot."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

import yaml


SELECTED_SKILLS = ("code-reviewer", "local-change-implementer")
RUNTIME_ENTRY_VERSION = "1.0"
INITIALIZED_TARGET_SELECTOR_INVENTORY = ".dev/ai-context/effective-rules.yaml"


def source_path(skill_id: str) -> Path:
    return Path(".ai/assets/skills") / skill_id / "skill.yaml"


def wrapper_path(skill_id: str, target: str) -> Path:
    runtime_root = ".agents/skills" if target == "codex" else ".claude/skills"
    return Path(runtime_root) / skill_id / "SKILL.md"


def normalize_git_text_bytes(raw: bytes) -> bytes:
    """Normalize text as Git's LF worktree input for stable wrapper provenance."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("canonical skill source must be UTF-8 text") from exc
    normalized = text.replace("\r\n", "\n")
    if "\r" in normalized:
        raise ValueError("canonical skill source contains a bare carriage return")
    return normalized.encode("utf-8")


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def require_strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    return [require_string(item, f"{label}[{index}]") for index, item in enumerate(value, start=1)]


def load_skill_document(raw: bytes, source: Path) -> tuple[dict[str, Any], bytes]:
    normalized = normalize_git_text_bytes(raw)
    try:
        data = yaml.safe_load(normalized)
    except yaml.YAMLError as exc:
        raise ValueError(f"{source.as_posix()}: cannot load canonical skill source: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{source.as_posix()}: root must be a mapping")
    skill_id = source.parent.name
    if data.get("asset_id") != skill_id:
        raise ValueError(f"{source.as_posix()}: asset_id must be {skill_id!r}")
    return data, normalized


def load_skill(root: Path, skill_id: str) -> tuple[dict[str, Any], bytes]:
    relative = source_path(skill_id)
    try:
        return load_skill_document((root / relative).read_bytes(), relative)
    except OSError as exc:
        raise ValueError(f"{relative.as_posix()}: cannot load canonical skill source: {exc}") from exc


def load_runtime_entry(data: dict[str, Any], skill_id: str) -> dict[str, Any]:
    entry = data.get("runtime_entry")
    label = f"{source_path(skill_id).as_posix()}: runtime_entry"
    if not isinstance(entry, dict):
        raise ValueError(f"{label} must be a mapping")
    if entry.get("format_version") != RUNTIME_ENTRY_VERSION:
        raise ValueError(f"{label}.format_version must be {RUNTIME_ENTRY_VERSION!r}")
    if entry.get("execution_authority") != "canonical-runtime-entry":
        raise ValueError(f"{label}.execution_authority must be 'canonical-runtime-entry'")
    require_string(entry.get("summary"), f"{label}.summary")
    require_strings(entry.get("steps"), f"{label}.steps")
    require_strings(entry.get("stop_conditions"), f"{label}.stop_conditions")
    require_strings(entry.get("output"), f"{label}.output")
    expansions = entry.get("conditional_expansion")
    if not isinstance(expansions, list) or not expansions:
        raise ValueError(f"{label}.conditional_expansion must be a non-empty list")
    for index, expansion in enumerate(expansions, start=1):
        expansion_label = f"{label}.conditional_expansion[{index}]"
        if not isinstance(expansion, dict):
            raise ValueError(f"{expansion_label} must be a mapping")
        require_string(expansion.get("when"), f"{expansion_label}.when")
        require_strings(expansion.get("read"), f"{expansion_label}.read")
        if "use" in expansion:
            require_strings(expansion.get("use"), f"{expansion_label}.use")
        require_string(expansion.get("why"), f"{expansion_label}.why")
    return entry


def allowed_applicability_modes(data: dict[str, Any], skill_id: str) -> list[str]:
    consumption = data.get("effective_rule_consumption")
    label = f"{source_path(skill_id).as_posix()}: effective_rule_consumption"
    if not isinstance(consumption, dict):
        raise ValueError(f"{label} must be a mapping")
    applicability = consumption.get("applicability")
    if not isinstance(applicability, dict):
        raise ValueError(f"{label}.applicability must be a mapping")
    modes = applicability.get("modes")
    if not isinstance(modes, dict) or not modes:
        raise ValueError(f"{label}.applicability.modes must be a non-empty mapping")
    return [require_string(mode, f"{label}.applicability.modes key") for mode in modes]


def projected_capability_slots(data: dict[str, Any], skill_id: str) -> list[str]:
    """Project the canonical capability slots without creating route aliases."""
    return require_strings(data.get("capability_slots"), f"{source_path(skill_id).as_posix()}: capability_slots")


def initialized_target_route_selection(data: dict[str, Any], skill_id: str) -> tuple[list[str], str] | None:
    """Return canonical selector metadata only when the target mode is declared."""
    label = f"{source_path(skill_id).as_posix()}: effective_rule_consumption"
    consumption = data.get("effective_rule_consumption")
    if not isinstance(consumption, dict):
        raise ValueError(f"{label} must be a mapping")
    applicability = consumption.get("applicability")
    if not isinstance(applicability, dict):
        raise ValueError(f"{label}.applicability must be a mapping")
    modes = applicability.get("modes")
    if not isinstance(modes, dict):
        raise ValueError(f"{label}.applicability.modes must be a mapping")
    target_mode = modes.get("initialized-target")
    if target_mode is None:
        return None
    if not isinstance(target_mode, dict):
        raise ValueError(f"{label}.applicability.modes.initialized-target must be a mapping")
    if require_string(
        target_mode.get("rule_selection"),
        f"{label}.applicability.modes.initialized-target.rule_selection",
    ) != "exact target effective-state route":
        raise ValueError(f"{label}.applicability.modes.initialized-target must select an exact target effective-state route")
    selectors = require_strings(consumption.get("selectors"), f"{label}.selectors")
    unresolved_outcome = require_string(consumption.get("unresolved_outcome"), f"{label}.unresolved_outcome")
    return selectors, unresolved_outcome


def projected_role_bindings(data: dict[str, Any], skill_id: str) -> list[dict[str, str]]:
    """Project declared role-selection metadata without creating role authority."""
    bindings = data.get("role_bindings")
    label = f"{source_path(skill_id).as_posix()}: role_bindings"
    if bindings is None:
        return []
    if not isinstance(bindings, list):
        raise ValueError(f"{label} must be a list when declared")
    projection: list[dict[str, str]] = []
    for index, binding in enumerate(bindings, start=1):
        binding_label = f"{label}[{index}]"
        if not isinstance(binding, dict):
            raise ValueError(f"{binding_label} must be a mapping")
        projection.append(
            {
                "role_asset_id": require_string(binding.get("role_asset_id"), f"{binding_label}.role_asset_id"),
                "role_path": require_string(binding.get("role_path"), f"{binding_label}.role_path"),
                "binding_kind": require_string(binding.get("binding_kind"), f"{binding_label}.binding_kind"),
                "applicability": require_string(binding.get("applicability"), f"{binding_label}.applicability"),
                "load_obligation": require_string(binding.get("load_obligation"), f"{binding_label}.load_obligation"),
            }
        )
    return projection


def source_digest(raw: bytes) -> str:
    return hashlib.sha256(normalize_git_text_bytes(raw)).hexdigest()


def frontmatter(data: dict[str, Any]) -> str:
    metadata = {
        "name": require_string(data.get("asset_id"), "asset_id"),
        "description": require_string(data.get("purpose"), "purpose"),
    }
    rendered = yaml.safe_dump(metadata, allow_unicode=False, default_flow_style=False, sort_keys=False).rstrip()
    return f"---\n{rendered}\n---\n"


def bullet_items(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def render_entry(data: dict[str, Any], raw: bytes) -> str:
    """Render one exact cross-runtime wrapper from its canonical YAML source."""
    skill_id = require_string(data.get("asset_id"), "asset_id")
    entry = load_runtime_entry(data, skill_id)
    modes = allowed_applicability_modes(data, skill_id)
    capability_slots = projected_capability_slots(data, skill_id)
    target_route_selection = initialized_target_route_selection(data, skill_id)
    role_bindings = projected_role_bindings(data, skill_id)
    source = source_path(skill_id).as_posix()
    mode_list = ", ".join(f"`{mode}`" for mode in modes)
    output = [frontmatter(data), f"# {require_string(data.get('title'), 'title')}", ""]
    output.extend(
        [
            "This runtime execution entry is generated. Do not edit it by hand.",
            "",
            "## Authority and provenance",
            "",
            f"- Execution authority: `{source}` `runtime_entry`.",
            "- Runtime frontmatter is discovery metadata generated from canonical `asset_id` and `purpose`; it does not add execution authority.",
            f"- Generator: `.ai/scripts/generate-runtime-skill-entries.py`; canonical source SHA-256: `{source_digest(raw)}`.",
            "- Regenerate after canonical changes, then verify exact parity with `python .ai/scripts/generate-runtime-skill-entries.py --root <absolute-repository-root> --check`.",
            "- This entry does not promise zero additional reads. Load the listed canonical material only when its condition applies.",
            "",
            "## Use this entry when",
            "",
            require_string(entry.get("summary"), "runtime_entry.summary"),
            "",
            "## Execute",
            "",
        ]
    )
    output.extend(f"{index}. {step}" for index, step in enumerate(require_strings(entry.get("steps"), "runtime_entry.steps"), start=1))
    output.extend(
        [
            "",
            "## Canonical capability slots",
            "",
            f"- Generated from `{source}` `capability_slots`: {', '.join(f'`{slot}`' for slot in capability_slots)}.",
        ]
    )
    output.extend(
        [
            "",
            "## Effective-rule preflight",
            "",
            f"- Select only an applicability mode declared by this canonical payload: {mode_list}.",
        ]
    )
    if target_route_selection is not None:
        selectors, unresolved_outcome = target_route_selection
        output.extend(
            [
                f"- When `initialized-target`, before the resolver invocation, inspect only `{INITIALIZED_TARGET_SELECTOR_INVENTORY}` routing selector inventory.",
                f"- For each task partition, select an existing exact tuple of {', '.join(f'`{selector}`' for selector in selectors)}; do not derive selectors from this skill ID, an action label, or a file suffix.",
                f"- If no exact existing tuple is available, preserve canonical unresolved outcome `{unresolved_outcome}`; do not use aliases or default routes.",
            ]
        )
    output.extend(
        [
            "- Use the request-authorized effective-rule resolver invocation. Run `.ai/scripts/resolve-effective-rule-packet.py --help` only when its supported interface is needed.",
            "",
        ]
    )
    if role_bindings:
        output.extend(
            [
                "## Canonical role bindings",
                "",
                f"- Generated from `{source}` `role_bindings`; this selection metadata does not execute, delegate, or replace a canonical role contract.",
            ]
        )
        for binding in role_bindings:
            output.extend(
                [
                    f"- `{binding['role_asset_id']}` — `{binding['role_path']}`",
                    f"  - Binding kind: `{binding['binding_kind']}`",
                    f"  - Applies when: {binding['applicability']}",
                    f"  - Load obligation: `{binding['load_obligation']}`",
                ]
            )
        output.append("")
    output.extend(["## Conditional expansion", ""])
    for expansion in entry["conditional_expansion"]:
        output.append(f"- When: {require_string(expansion.get('when'), 'conditional expansion when')}")
        if "use" in expansion:
            output.append(f"  - Use: {'; '.join(require_strings(expansion.get('use'), 'conditional expansion use'))}")
        reads = require_strings(expansion.get("read"), "conditional expansion read")
        output.append(f"  - Read: {', '.join(f'`{path}`' for path in reads)}")
        output.append(f"  - Why: {require_string(expansion.get('why'), 'conditional expansion why')}")
    output.extend(["", "## Stop or hand off", ""])
    output.extend(bullet_items(require_strings(entry.get("stop_conditions"), "runtime_entry.stop_conditions")))
    output.extend(["", "## Return", ""])
    output.extend(bullet_items(require_strings(entry.get("output"), "runtime_entry.output")))
    return "\n".join(output) + "\n"


def generated_entries(root: Path) -> dict[Path, str]:
    entries: dict[Path, str] = {}
    for skill_id in SELECTED_SKILLS:
        data, raw = load_skill(root, skill_id)
        targets = data.get("wrapper_targets")
        if not isinstance(targets, list) or set(targets) != {"claude", "codex"}:
            raise ValueError(f"{source_path(skill_id).as_posix()}: selected pilot requires exactly Claude and Codex wrapper targets")
        rendered = render_entry(data, raw)
        for target in ("codex", "claude"):
            entries[wrapper_path(skill_id, target)] = rendered
    return entries


def parity_errors(expected: Mapping[Path, str], actual: Mapping[Path, str]) -> list[str]:
    return [
        f"{relative.as_posix()}: differs from its canonical generated runtime entry"
        for relative, rendered in expected.items()
        if actual.get(relative) != rendered
    ]


def check_entries(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        expected = generated_entries(root)
    except ValueError as exc:
        return [str(exc)]
    actual: dict[Path, str] = {}
    for relative in expected:
        path = root / relative
        try:
            actual[relative] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{relative.as_posix()}: cannot read generated runtime entry: {exc}")
    return [*errors, *parity_errors(expected, actual)]


def render_payload_entries(payload_contents: Mapping[str, bytes]) -> dict[str, bytes]:
    """Render selected wrappers from final package skill bytes, never source bytes."""
    rendered: dict[str, bytes] = {}
    for skill_id in SELECTED_SKILLS:
        source = source_path(skill_id)
        source_key = source.as_posix()
        raw = payload_contents.get(source_key)
        if raw is None:
            continue
        data, normalized = load_skill_document(raw, source)
        targets = data.get("wrapper_targets")
        if not isinstance(targets, list) or set(targets) != {"claude", "codex"}:
            raise ValueError(f"{source_key}: selected pilot requires exactly Claude and Codex wrapper targets")
        entry = render_entry(data, normalized).encode("utf-8")
        for target in ("codex", "claude"):
            target_key = wrapper_path(skill_id, target).as_posix()
            if target_key not in payload_contents:
                raise ValueError(f"{source_key}: package payload is missing generated wrapper {target_key}")
            rendered[target_key] = entry
    return rendered
