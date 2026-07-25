#!/usr/bin/env python3
"""Validate deterministic, repository-local dependency version consistency."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PROFILE = Path(".ai/distribution/profiles/dotnet-backend.yaml")
MINIMUM_PYTHON = (3, 11)
REQUIREMENT_PIN = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)=="
    r"(?P<version>[A-Za-z0-9][A-Za-z0-9._+!-]*)$"
)
PYTHON_VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
SDK_VERSION = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
NET_TFM = re.compile(r"^net(?P<major>\d+)\.0$")
PIP_INSTALL = re.compile(r"(?:python(?:3)?\s+-m\s+)?pip\s+install\b")
REQUIREMENTS_INSTALL = re.compile(
    r"(?:^|\s)(?:-r\s+requirements\.txt|--requirement(?:=|\s+)requirements\.txt)(?:\s|$)"
)


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_exact_requirements(path: Path, root: Path, errors: list[str]) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{relative(path, root)}: cannot read requirements: {exc}")
        return {}

    resolved: dict[str, str] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = REQUIREMENT_PIN.fullmatch(line)
        if not match:
            errors.append(
                f"{relative(path, root)}:{line_number}: "
                "must use an exact name==version pin"
            )
            continue
        name = match.group("name").lower().replace("_", "-")
        version = match.group("version")
        if name in resolved:
            errors.append(
                f"{relative(path, root)}:{line_number}: "
                f"duplicate requirement {match.group('name')}"
            )
            continue
        resolved[name] = version
    if not resolved:
        errors.append(f"{relative(path, root)}: at least one exact dependency pin is required")
    return resolved


def validate_source_python(root: Path, errors: list[str]) -> int:
    source_requirements = root / "requirements.txt"
    package_requirements = root / ".ai/distribution/templates/requirements.txt"
    source_pins = parse_exact_requirements(source_requirements, root, errors)
    package_pins = parse_exact_requirements(package_requirements, root, errors)

    try:
        if source_requirements.read_bytes() != package_requirements.read_bytes():
            errors.append(
                "requirements.txt and .ai/distribution/templates/requirements.txt: "
                "requirements mirror bytes differ"
            )
    except OSError:
        pass
    if source_pins and package_pins and source_pins != package_pins:
        errors.append("source and package requirement versions differ")

    workflow_root = root / ".github/workflows"
    workflows = sorted(
        (
            *workflow_root.glob("*.yml"),
            *workflow_root.glob("*.yaml"),
        ),
        key=lambda path: relative(path, root).encode("utf-8"),
    )
    setup_versions: list[tuple[str, str]] = []
    install_commands = 0
    for workflow in workflows:
        try:
            text = workflow.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{relative(workflow, root)}: cannot inspect workflow: {exc}")
            continue

        setup_count = len(re.findall(r"uses:\s*actions/setup-python@", text))
        versions = re.findall(r"^\s*python-version:\s*[\"']?([^\"'\s#]+)", text, re.MULTILINE)
        if setup_count and len(versions) != setup_count:
            errors.append(
                f"{relative(workflow, root)}: every actions/setup-python step "
                "must declare one exact python-version"
            )
        for version in versions:
            setup_versions.append((relative(workflow, root), version))

        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            if not PIP_INSTALL.search(line):
                continue
            install_commands += 1
            if not REQUIREMENTS_INSTALL.search(line):
                errors.append(
                    f"{relative(workflow, root)}:{line_number}: "
                    "must install source dependencies with -r requirements.txt"
                )

    if not setup_versions:
        errors.append(".github/workflows: at least one pinned actions/setup-python step is required")
    normalized_versions: set[str] = set()
    for workflow, version in setup_versions:
        if not PYTHON_VERSION.fullmatch(version):
            errors.append(f"{workflow}: python-version must be an exact major.minor or patch version")
            continue
        components = tuple(int(component) for component in version.split("."))
        if components[:2] < MINIMUM_PYTHON:
            errors.append(
                f"{workflow}: Python {version} is below required "
                f"{MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}"
            )
        normalized_versions.add(version)
    if len(normalized_versions) > 1:
        errors.append(
            "GitHub workflow Python setup versions must be consistent: "
            f"{sorted(normalized_versions)}"
        )
    if install_commands == 0:
        errors.append(".github/workflows: a requirements.txt installation step is required")

    return len(source_pins)


def exact_package_version(element: ET.Element) -> str | None:
    version = element.get("Version")
    if version is not None:
        return version.strip()
    for child in element:
        if local_name(child.tag) == "Version" and child.text:
            return child.text.strip()
    return None


def is_exact_package_version(version: str) -> bool:
    if not version or "$(" in version or "*" in version:
        return False
    if version[0] in "[(" or any(operator in version for operator in (">", "<", ",")):
        return False
    return bool(re.fullmatch(r"\d+(?:\.\d+){1,3}(?:-[0-9A-Za-z.-]+)?", version))


def managed_projects(root: Path) -> list[Path]:
    tools = root / "tools"
    if not tools.is_dir():
        return []
    return sorted(
        (
            path
            for path in tools.rglob("*.csproj")
            if not {"bin", "obj"}.intersection(path.relative_to(root).parts)
        ),
        key=lambda path: relative(path, root).encode("utf-8"),
    )


def validate_dotnet(root: Path, errors: list[str]) -> tuple[int, int]:
    projects = managed_projects(root)
    if not projects:
        return 0, 0

    sdk_manifest = root / "global.json"
    try:
        global_json = json.loads(sdk_manifest.read_text(encoding="utf-8"))
        sdk_version = global_json["sdk"]["version"]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        errors.append(f"global.json: cannot resolve sdk.version: {exc}")
        return len(projects), 0
    if not isinstance(sdk_version, str) or not (sdk_match := SDK_VERSION.fullmatch(sdk_version)):
        errors.append("global.json: sdk.version must be an exact major.minor.patch version")
        return len(projects), 0
    sdk_major = int(sdk_match.group("major"))

    package_versions: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    maximum_net_major = 0
    for project in projects:
        project_name = relative(project, root)
        try:
            tree = ET.parse(project)
        except (OSError, ET.ParseError) as exc:
            errors.append(f"{project_name}: invalid project XML: {exc}")
            continue
        project_root = tree.getroot()

        for element in project_root.iter():
            element_name = local_name(element.tag)
            if element_name == "PackageReference":
                package_id = element.get("Include") or element.get("Update")
                if not package_id:
                    errors.append(f"{project_name}: PackageReference must declare Include or Update")
                    continue
                version = exact_package_version(element)
                if version is None:
                    errors.append(
                        f"{project_name}: PackageReference {package_id} has no exact version"
                    )
                    continue
                if not is_exact_package_version(version):
                    errors.append(
                        f"{project_name}: PackageReference {package_id} "
                        f"must use an exact version, found {version!r}"
                    )
                    continue
                package_versions[package_id.lower()].append((project_name, version))
            elif element_name in {"TargetFramework", "TargetFrameworks"} and element.text:
                for tfm in element.text.strip().split(";"):
                    tfm = tfm.strip()
                    match = NET_TFM.fullmatch(tfm)
                    if match:
                        maximum_net_major = max(maximum_net_major, int(match.group("major")))
                    elif tfm.startswith("net") and "$(" not in tfm and not tfm.startswith("netstandard"):
                        errors.append(f"{project_name}: unsupported concrete target framework {tfm!r}")

    for package_id, declarations in sorted(package_versions.items()):
        versions = {version for _, version in declarations}
        if len(versions) > 1:
            locations = ", ".join(f"{path}={version}" for path, version in declarations)
            errors.append(
                f"PackageReference {package_id} resolves to conflicting versions: {locations}"
            )

    if maximum_net_major > sdk_major:
        errors.append(
            f"managed tools require .NET SDK major at least {maximum_net_major}, "
            f"but global.json selects {sdk_major}"
        )
    return len(projects), len(package_versions)


def validate(root: Path) -> tuple[list[str], dict[str, int | bool]]:
    errors: list[str] = []
    source_mode = (root / SOURCE_PROFILE).is_file()
    python_dependencies = validate_source_python(root, errors) if source_mode else 0
    project_count, nuget_dependencies = validate_dotnet(root, errors)
    return errors, {
        "source_mode": source_mode,
        "python_dependencies": python_dependencies,
        "managed_projects": project_count,
        "nuget_dependencies": nuget_dependencies,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate deterministic offline dependency and version consistency."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Repository root to validate (defaults to the current framework repository).",
    )
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    if not root.is_dir():
        print(f"Dependency/version consistency validation failed:\n- {root}: root is not a directory")
        return 1

    errors, counts = validate(root)
    if errors:
        print("Dependency/version consistency validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Dependency/version consistency validation passed: "
        f"source_mode={str(counts['source_mode']).lower()}, "
        f"python_dependencies={counts['python_dependencies']}, "
        f"managed_projects={counts['managed_projects']}, "
        f"nuget_dependencies={counts['nuget_dependencies']}."
    )
    print(
        "Online package currency and vulnerability status are advisory and "
        "are not asserted by this offline gate."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
