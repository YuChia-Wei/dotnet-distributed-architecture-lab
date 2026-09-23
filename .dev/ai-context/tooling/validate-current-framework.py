"""Current target installation checks; independent adoption review stays separate."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys

BINDING = ".dev/ai-context/framework-binding.json"
MAX_FILE = 16 * 1024 * 1024
MAX_ENTRIES = 4096
OWNER_CAPABILITIES = {
    "slice-implementer": "implementation",
    "local-change-implementer": "local-change",
    "code-reviewer": "review",
    "bdd-gwt-test-designer": "test-design",
    "spec-author": "specification",
    "ddd-ca-hex-architect": "architecture",
    "requirement-author": "requirements",
    "problem-frame-author": "problem-framing",
    "spec-compliance-validator": "compliance-validation",
}


class GateError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise GateError(message)


def exact(left, right):
    """JSON structural equality keeps bool/int distinctions."""
    return json.dumps(left, sort_keys=True, ensure_ascii=False) == json.dumps(right, sort_keys=True, ensure_ascii=False)


def unique(rows, key, label):
    require(type(rows) is list, label + ": expected list")
    values = [key(row) for row in rows]
    require(len(values) == len(set(values)), label + ": duplicate identity")
    return values


def relative(value):
    require(type(value) is str and bool(value) and "\\" not in value and ":" not in value, "unsafe relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and value == path.as_posix()
            and all(part not in {".", ".."} and not part.endswith((" ", ".")) for part in path.parts),
            "unsafe relative path")
    return path.parts


class Files:
    """Bounded read-only observation under the owner's quiescent review window."""

    def __init__(self, root):
        self.root = Path(root).absolute()
        self.names = {}
        self.entries = 0
        self.bytes = 0

    def locate(self, name):
        current = self.root
        for part in relative(name):
            info = current.lstat()
            require(stat.S_ISDIR(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "non-direct ancestor")
            if current not in self.names:
                names = {}
                with os.scandir(current) as entries:
                    for entry in entries:
                        self.entries += 1
                        require(self.entries <= MAX_ENTRIES, "directory observation limit")
                        folded = entry.name.casefold()
                        require(folded not in names, "case alias in required directory")
                        names[folded] = entry.name
                self.names[current] = names
            actual = self.names[current].get(part.casefold())
            if actual is None:
                return None
            require(actual == part, "path spelling differs")
            current = current / part
            info = current.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "non-direct path")
        return current

    def read(self, name):
        path = self.locate(name)
        require(path is not None, "required file missing: " + name)
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= MAX_FILE,
                "unsupported file: " + name)
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            require((before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino), "file identity changed")
            raw = stream.read(MAX_FILE + 1)
            after = os.fstat(stream.fileno())
        self.bytes += len(raw)
        require(self.bytes <= 128 * 1024 * 1024, "total read budget exceeded")
        require(len(raw) == before.st_size and len(raw) <= MAX_FILE and
                (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "file changed during read")
        return raw

    def pinned(self, reference):
        require(type(reference) is dict and set(reference) == {"path", "sha256"}, "invalid pinned reference")
        require(type(reference["sha256"]) is str and re.fullmatch("[0-9a-f]{64}", reference["sha256"]), "invalid digest")
        raw = self.read(reference["path"])
        require(hashlib.sha256(raw).hexdigest() == reference["sha256"], "pinned bytes differ: " + reference["path"])
        return raw

    def inventory(self, name):
        start = self.locate(name)
        require(start is not None and start.is_dir(), "managed directory missing")
        found = []
        pending = [start]
        while pending:
            parent = pending.pop()
            with os.scandir(parent) as entries:
                for entry in entries:
                    self.entries += 1
                    require(self.entries <= MAX_ENTRIES, "directory observation limit")
                    info = entry.stat(follow_symlinks=False)
                    require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                            "non-direct managed entry")
                    if stat.S_ISDIR(info.st_mode):
                        pending.append(Path(entry.path))
                    else:
                        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "nonregular managed entry")
                        found.append(Path(entry.path).relative_to(self.root).as_posix())
        require(len(found) == len({name.casefold() for name in found}), "managed case alias")
        return sorted(found)


def load_binding(files, expected):
    require(type(expected) is str and re.fullmatch("[0-9a-f]{64}", expected), "explicit accepted binding digest required")
    raw = files.read(BINDING)
    require(hashlib.sha256(raw).hexdigest() == expected, "binding differs from caller-selected subject")
    binding = json.loads(raw)
    require(type(binding) is dict and binding.get("schema_version") == "target-framework-binding/v1",
            "unsupported target binding")
    require(binding.get("state") == "pilot-review", "binding is not a prepared pilot review subject")
    require(binding.get("runtime") == "codex" and binding.get("legacy_baseline_role") == "retained-target-rules-and-legacy-package-support",
            "candidate and legacy authority roles unresolved")
    return binding


def candidate_check(files, binding):
    selected = binding["candidate"]
    selection = json.loads(files.pinned(selected["selection"]))
    inventory = json.loads(files.pinned(selected["inventory"]))
    build = json.loads(files.pinned(selected["build"]))
    lock = json.loads(files.pinned(selected["lock"]))
    require(type(lock.get("lock_version")) is int and lock["lock_version"] == 1, "unsupported lock")
    require(exact(lock["selection"], selection) and exact(lock["inventory"], inventory), "lock metadata differs from candidate")
    require(lock["candidate_identity"] == build["candidate_identity"] == selected["identity"], "candidate identity differs")
    require(selection["mode"] == "versioned" and selection["release_version"] == selected["version"], "candidate version differs")
    require(selection["source"]["commit"] == selected["source_commit"] == build["source_commit"], "candidate source differs")
    require(exact(lock["engine"], binding["engine"]), "installation engine differs")
    require(lock["mode_policy"] == "windows-inventory-only", "unselected mode policy")
    components = selection["components"]
    identifiers = unique(components, lambda row: row["id"], "components")
    require(len(identifiers) == 18 and set(identifiers) == set(selected["packages"]), "complete package set differs")
    require({row["id"]: row["version"] for row in components} == selected["packages"], "package versions differ")
    rows = inventory["files"]
    destinations = unique(rows, lambda row: row["destination"], "managed inventory")
    require(len(rows) == 131 and len({name.casefold() for name in destinations}) == len(rows), "managed inventory differs")
    runtime = [row for row in rows if row["kind"] == "runtime"]
    require(sorted(row["destination"] for row in runtime) ==
            sorted(".agents/skills/framework-" + identifier + "/SKILL.md" for identifier in identifiers), "Codex entry set differs")
    for row in rows:
        raw = files.read(row["destination"])
        require(type(row["size"]) is int and len(raw) == row["size"] and hashlib.sha256(raw).hexdigest() == row["sha256"],
                "managed bytes differ: " + row["destination"])
    expected_core = sorted(name for name in destinations if name.startswith(".ai/core/skills/"))
    require(files.inventory(".ai/core/skills") == expected_core, "unexpected or missing core member")
    for identifier in identifiers:
        expected = ".agents/skills/framework-" + identifier + "/SKILL.md"
        require(files.inventory(".agents/skills/framework-" + identifier) == [expected], "unexpected Codex entry member")
    for marker in [".ai/framework.operation", ".ai/config-transition.operation"]:
        require(files.locate(marker) is None, "maintenance marker remains")
    return {"packages": len(components), "managed_members": len(rows), "project_readiness": "not-assessed"}


def retained_check(files, binding):
    inventory = json.loads(files.pinned(binding["retained_inventory"]))
    paths = unique(inventory["files"], lambda row: row["path"], "retained inventory")
    require(inventory["baseline_commit"] == binding["baseline_commit"], "retained baseline differs")
    for row in inventory["files"]:
        files.pinned({"path": row["path"], "sha256": row["sha256"]})
    require(sum(path.startswith(".ai/assets/tech-stacks/dotnet-backend/") for path in paths) == 194,
            ".NET retained asset set differs")
    return {"exact_retained_files": len(paths), "net_assets": 194}


def routes_check(files, binding):
    for row in binding["withdrawn_entries"]:
        require(files.locate(row["old"]) is None, "superseded runtime entry remains")
        require(type(row["archived_files"]) is list and bool(row["archived_files"]), "empty runtime history")
        for reference in row["archived_files"]:
            files.pinned(reference)
    require(len(binding["withdrawn_entries"]) == 26, "withdrawal set incomplete")
    unique(binding["withdrawn_entries"], lambda row: row["old"], "withdrawals")
    for row in binding["legacy_entries"]:
        files.pinned(row)
    require(len(binding["legacy_entries"]) == 4, "legacy lifecycle entry set differs")
    for reference in binding["current_authorities"]:
        files.pinned(reference)
    return {"withdrawn_entries": 26, "legacy_only_entries": 4}


def rules_check(files, binding):
    import yaml
    state = yaml.safe_load(files.read(".dev/ai-context/effective-rules.yaml"))
    ledger = yaml.safe_load(files.read(".dev/ai-context/customizations.yaml"))
    require([row["id"] for row in ledger["customizations"]] == binding["customization_ids"]
            and len(binding["customization_ids"]) == 4, "customization set differs")
    rules = unique(state["rule_dispositions"], lambda row: row["rule_id"], "rules")
    require(rules == binding["rule_ids"] and len(rules) == 14
            and all(row["effective_disposition"] == "baseline-effective" for row in state["rule_dispositions"]), "rule dispositions differ")
    routes = state["routing"]
    unique(routes, lambda row: json.dumps(row["selector"], sort_keys=True), "selectors")
    require(len(routes) == 20, "target selector count differs")
    owners = binding["route_bindings"]
    unique(owners, lambda row: row["route_id"], "route ownership")
    require({row["route_id"] for row in owners} == {row["route_id"] for row in routes}, "route ownership incomplete")
    by_id = {row["route_id"]: row for row in routes}
    for row in owners:
        route = by_id[row["route_id"]]
        require(OWNER_CAPABILITIES.get(row["package"]) == route["selector"]["capability"],
                "target selector assigned to wrong package")
        require(exact(route["selector"], row["selector"]), "selector binding differs")
    packages = set(binding["candidate"]["packages"])
    require(set(binding["project_scope_packages"]) == packages - set(OWNER_CAPABILITIES), "project-scope package set differs")
    script_root = files.root / ".ai/scripts"
    sys.path.insert(0, str(script_root))
    try:
        import ai_context_effective_rules as resolver
        resolved = []
        for route in routes:
            packet = resolver.resolve_effective_rule_packet_for_mode(
                files.root, applicability_mode="initialized-target", **route["selector"])
            require(exact(packet["request"], {"route_id": route["route_id"], **route["selector"]}), "resolved selector differs")
            require(packet["loaded_rule_ids"] == rules == route["required_rule_ids"], "resolved rule set differs")
            require(packet["packet_digest"] == route["packet"]["digest"], "resolved packet differs")
            resolved.append({"route_id": route["route_id"], "packet_digest": packet["packet_digest"]})
    finally:
        sys.path.pop(0)
    return {"rule_ids": rules, "customizations": 4, "actual_resolutions": resolved,
            "baseline_role": "v0.18-derived target rule authority; not installed candidate provenance"}


def git_check(files, binding, revision_range):
    reference = binding["git_validator"]
    files.pinned(reference)
    command = [sys.executable, "-B", str(files.root / reference["path"]),
               "--range", revision_range, "--workflow-id", binding["workflow_id"]]
    process = subprocess.run(command, cwd=files.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    require(process.returncode == 0, "target Git policy failed: " + process.stdout.decode("utf-8", "replace")[-3000:])
    return {"command": command, "outcome": "passed",
            "stdout_sha256": hashlib.sha256(process.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(process.stderr).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--binding-sha256", required=True)
    parser.add_argument("--git-range", required=True)
    args = parser.parse_args()
    files = Files(args.root)
    results = {}
    try:
        binding = load_binding(files, args.binding_sha256)
        # Authority hashes are checked before any retained executable is imported.
        results["retained_target"] = retained_check(files, binding)
        results["candidate"] = candidate_check(files, binding)
        results["runtime_and_current_authority"] = routes_check(files, binding)
        results["effective_rules"] = rules_check(files, binding)
        results["git_policy"] = git_check(files, binding, args.git_range)
        result = {"outcome": "selected-checks-passed", "checks": results,
                  "independent_review": "required-separately; not established by this command",
                  "activation": "not-authorized-by-this-result"}
        status = 0
    except (GateError, ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        result = {"outcome": "failed", "checks_completed": results, "diagnostic": str(error),
                  "independent_review": "not-established", "activation": "blocked"}
        status = 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
