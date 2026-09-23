#!/usr/bin/env python3
"""Portable workflow.fs 0.1.0: one owned record, explicit operations, no dispatch."""
from __future__ import annotations
import argparse
import copy
import ctypes
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
import uuid

sys.dont_write_bytecode = True
PACKAGE = "software-development-orchestrator"
ID_PREFIX = "wf-"
SUFFIX = ".workflow.json"
ROLE = PACKAGE + ".record"
OPERATIONS = ("explain", "create", "inspect", "query", "checkpoint", "transition",
              "resume", "retrospect", "render", "retention-preview")
ALL_OPERATIONS = list(OPERATIONS)
SCHEMA_PATH = "schemas/workflow-record.schema.json"
# The executable is the sole operational-default authority. Metadata v2 remains closed.
OPERATIONAL_DEFAULTS = {
    "retention": {"compact_after_days": 30, "archive_after_days": 90, "purge_after_days": None},
    "resume_budget_chars": 12000,
}
VIEW_FIELDS = ("id", "title", "intent", "scope", "state", "acceptance", "tasks",
               "evidence", "decisions", "references", "next_action", "retrospective",
               "history", "storage_notice")
WORKFLOW_TRANSITIONS = {"planned": {"active", "cancelled"},
                       "active": {"blocked", "completed", "cancelled"},
                       "blocked": {"active", "cancelled"}}
TASK_TRANSITIONS = {
    "pending": {"active", "blocked", "deferred", "cancelled"},
    "active": {"completed", "failed", "blocked", "deferred", "cancelled"},
    "failed": {"active", "blocked", "deferred", "cancelled"},
    "blocked": {"active", "deferred", "cancelled"},
    "deferred": {"pending", "cancelled"}, "completed": set(), "cancelled": set(),
}
DESTINATIONS = {"lesson@0.2.0": "create", "adr@0.1.0": "create",
                "standards-promotion@0.1.0": "propose",
                "local-backlog@0.1.0": "create", "pr@0.1.0": "prepare"}
ID = re.compile(r"wf-[0-9a-f]{32}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")
LIMIT = 4 * 1024 * 1024
MAX_FILES = 10000
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
NOTICE = ("Tracking is project intent. Actual Git tracking, backups and cross-person durability "
          "are unverified. Evidence and owner strings are caller-attributed; no task executes.")
MEMBERS = json.loads(r'''["SKILL.md","skill-package.yaml","references/configuration.md","references/operations.md","references/retention.md","references/composition.md","references/example.md","schemas/workflow-record.schema.json","templates/workflow.md","scripts/workflow.py"]''')
DEFAULTS = json.loads(r'''{"store":{"kind":"filesystem","root":"notes/workflows","tracking":"tracked"},"template":{"origin":"package","path":"templates/workflow.md"}}''')
ROLES = json.loads(r'''[{"role":"software-development-orchestrator.record","owner":"project","schema":"software-development-orchestrator.record@1.0.0","read_schemas":["software-development-orchestrator.record@1.0.0"],"store_binding":"software-development-orchestrator.store","identity":"wf-<32 lowercase hex digits>","filename":"<id>.workflow.json","read_operations":["inspect","query","resume","render","retention-preview"],"write_operations":["create","checkpoint","transition","retrospect"]},{"role":"software-development-orchestrator.view","owner":"derived","source_role":"software-development-orchestrator.record","output":"result-only Markdown","persistence":"Caller-selected export is a separate write","produce_operations":["render"]}]''')
RUNTIME = json.loads(r'''[{"id":"skill-instruction-reader","requirement":"Read selected package and resources","for_operations":["explain","create","inspect","query","checkpoint","transition","resume","retrospect","render","retention-preview"],"on_missing":"unavailable"},{"id":"python","version":">=3.11,<4","for_operations":["explain","create","inspect","query","checkpoint","transition","resume","retrospect","render","retention-preview"],"on_missing":"unavailable"},{"id":"pyyaml","version":">=6,<7","for_operations":["explain","create","inspect","query","checkpoint","transition","resume","retrospect","render","retention-preview"],"on_missing":"unavailable"},{"id":"jsonschema","version":">=4.18,<5","for_operations":["create","inspect","query","checkpoint","transition","resume","retrospect","render","retention-preview"],"on_missing":"unavailable"},{"id":"filesystem","requirement":"Selected local files; exclusive creation and same-directory replacement for writes","for_operations":["explain","create","inspect","query","checkpoint","transition","resume","retrospect","render","retention-preview"],"on_missing":"unavailable"},{"id":"git","requirement":"Conditional read-only ignored/untracked selected local-config check","for_operations":["explain","create","inspect","query","checkpoint","transition","resume","retrospect","render","retention-preview"],"on_missing":"unavailable"}]''')
TOOLS = {PACKAGE + ".fs": ("scripts/workflow.py", ALL_OPERATIONS, "references/operations.md")}


class Fault(Exception):
    def __init__(self, outcome, code, message):
        super().__init__(message)
        self.outcome, self.code, self.message = outcome, code, message

    def diagnostic(self):
        return {"code": self.code, "message": self.message}

def fail(code, message, outcome="invalid-input"):
    raise Fault(outcome, code, message)

def fields(value, required, optional=(), label="object"):
    if type(value) is not dict or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        fail("fields", f"Invalid or unknown fields in {label}.")
    return value

def string(value, label):
    if type(value) is not str or not value or not value.strip():
        fail("type", f"{label} must be a nonempty string.")
    return value

def strings(value, label, nonempty=False):
    if type(value) is not list or (nonempty and not value):
        fail("type", f"{label} must be an array of strings.")
    for item in value:
        string(item, label)
    if len(set(value)) != len(value):
        fail("duplicate", f"{label} contains duplicates.")
    return value

def exact_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(exact_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(exact_equal(a, b) for a, b in zip(left, right))
    return left == right

def json_values(value):
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                fail("json-key", "JSON keys must be strings.")
            json_values(key)
            json_values(child)
    elif type(value) is list:
        for child in value:
            json_values(child)
    elif type(value) is str:
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeError:
            fail("unicode", "Unpaired Unicode surrogates are unsupported.")
    elif type(value) is float:
        if not math.isfinite(value):
            fail("number", "Non-finite JSON numbers are invalid.")
    elif value is not None and type(value) not in (int, bool):
        fail("json-type", "Only JSON-compatible values are accepted.")

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate-key", "Duplicate object keys are invalid.")
        result[key] = value
    return result

def parse_json(raw):
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=unique_pairs,
                           parse_constant=lambda _: fail("number", "Non-finite JSON numbers are invalid."))
        json_values(value)
        return value
    except (UnicodeError, ValueError, RecursionError):
        fail("json", "Expected bounded strict UTF-8 JSON without a BOM.")

def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n").encode("utf-8")

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def dependency(name, minimum, maximum):
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        fail("dependency", f"Required runtime {name} is missing.", "unavailable")
    if not re.fullmatch(r"\d+(?:\.\d+){1,3}", version):
        fail("dependency-version", f"Stable {name} runtime version required.", "unavailable")
    parts = tuple(int(p) for p in version.split("."))
    if not minimum <= parts < maximum:
        fail("dependency-version", f"Required {name} runtime range is unavailable.", "unavailable")

def parse_yaml(raw):
    dependency("PyYAML", (6, 0), (7, 0))
    try:
        import yaml
        text = raw.decode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            fail("yaml", "Metadata must be UTF-8 without a BOM.")
        for token in yaml.scan(text):
            if isinstance(token, (yaml.tokens.TagToken, yaml.tokens.AliasToken, yaml.tokens.AnchorToken)):
                fail("yaml-token", "YAML tags, aliases and anchors are forbidden.")
        node = yaml.compose(text, Loader=yaml.SafeLoader)

        def convert(item):
            if isinstance(item, yaml.MappingNode):
                pairs = []
                for key, child in item.value:
                    if key.tag != "tag:yaml.org,2002:str" or key.value == "<<":
                        fail("yaml-key", "YAML keys must be unique strings without merge keys.")
                    pairs.append((key.value, convert(child)))
                return unique_pairs(pairs)
            if isinstance(item, yaml.SequenceNode):
                return [convert(child) for child in item.value]
            if not isinstance(item, yaml.ScalarNode):
                fail("yaml", "Metadata must contain one JSON-compatible document.")
            kind = item.tag.removeprefix("tag:yaml.org,2002:")
            if kind == "str":
                return item.value
            if kind == "null" and item.value == "null":
                return None
            if kind == "bool" and item.value in ("true", "false"):
                return item.value == "true"
            if kind in ("int", "float") and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", item.value):
                return parse_json(item.value.encode("utf-8"))
            fail("yaml-type", "Metadata YAML must use JSON scalar types and spellings.")

        value = convert(node)
        json_values(value)
        return value
    except ImportError:
        fail("dependency", "PyYAML could not be imported.", "unavailable")
    except (UnicodeError, ValueError, RecursionError, yaml.YAMLError):
        fail("yaml", "Invalid bounded UTF-8 package metadata.")

def beneath(path, root):
    return path == root or root in path.parents

def overlap(left, right):
    return beneath(left, right) or beneath(right, left)

def safe_path(value, base=None, *, relative_only=False):
    string(value, "path")
    if any(ord(char) < 32 for char in value):
        fail("path", "Control characters in paths are forbidden.")
    path = Path(value)
    if relative_only and path.is_absolute():
        fail("path", "A package resource must be relative.")
    if ".." in path.parts or (path.drive and not path.is_absolute()):
        fail("path", "Parent traversal and drive-relative paths are forbidden.")
    if os.name == "nt":
        if value.startswith(("\\\\", "//")) or (path.root and not path.drive):
            fail("path", "UNC, device and root-relative paths are unsupported.", "unsupported")
        for part in path.parts[1:] if path.is_absolute() else path.parts:
            if part.endswith((" ", ".")) or re.search(r'[<>:"|?*\x00-\x1f]', part):
                fail("path", "Ambiguous Windows path segment.")
            if re.fullmatch(r"(?i:con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(?:\..*)?", part):
                fail("path", "Reserved Windows path segment.")
    if not path.is_absolute():
        if base is None:
            fail("path", "An explicit absolute root is required.")
        path = base / path
    # Refuse all links/reparse points, including contained ones; this avoids
    # mutable indirection in frozen bindings. Nonexistent tails remain lexical.
    for part in (*reversed(path.parents), path):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & REPARSE:
            fail("path-link", "Symlinks and reparse points are unsupported in selected paths.", "blocked")
    resolved = path.resolve(strict=False)
    if base is not None and not Path(value).is_absolute() and not beneath(resolved, base):
        fail("path-escape", "A relative path escapes its explicit root.", "blocked")
    return resolved

def read_bytes(path, missing="invalid-input"):
    safe_path(str(path))
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            fail("file-type", "A selected input is not a regular file.")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                fail("file-type", "A selected input is not a regular file.")
            raw = stream.read(LIMIT + 1)
            if len(raw) > LIMIT:
                fail("size-limit", "Selected file exceeds the 4 MiB limit.", "unsupported")
            if identity(path.lstat()) != identity(info):
                fail("input-drift", "Input identity changed during read.", "conflict")
            return raw
    except FileNotFoundError:
        fail("missing-file", "An explicitly selected file is missing.", missing)

def identity(info):
    return info.st_dev, info.st_ino

def resource(package, value):
    path = safe_path(value, package, relative_only=True)
    if not beneath(path, package) or not path.is_file():
        fail("resource", "Declared package resource is missing or outside the package.", "unsupported")
    return path

def git_local_ignored(project, local):
    # A project without a .git marker in its ancestry needs no Git executable.
    if not any((parent / ".git").exists() for parent in (project, *project.parents)):
        return
    env = {key: val for key, val in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        top = subprocess.run(["git", "-C", str(project), "rev-parse", "--show-toplevel"],
                             capture_output=True, timeout=10, env=env, check=False)
        if top.returncode:
            fail("local-ignore", "Cannot establish Git ownership of local config.", "blocked")
        git_root = safe_path(top.stdout.decode("utf-8").strip())
        if not beneath(local, git_root):
            fail("local-ignore", "Local config must be an ignored file in this Git project.", "blocked")
        ignored = subprocess.run(["git", "-C", str(git_root), "check-ignore", "-q", "--", str(local)],
                                 capture_output=True, timeout=10, env=env, check=False)
        if ignored.returncode != 0:
            fail("local-ignore", "Selected local config is not ignored or is tracked.", "blocked")
    except FileNotFoundError:
        fail("git", "Git is required to prove selected local config is ignored.", "unavailable")
    except (subprocess.TimeoutExpired, UnicodeError):
        fail("local-ignore", "Could not establish the selected local config's ignored state.", "blocked")

def load_package(package):
    metadata = parse_yaml(read_bytes(package / "skill-package.yaml", "unsupported"))
    fields(metadata, ("metadata_version", "id", "version", "delivery_status", "entrypoint", "dependencies", "runtime", "configuration", "artifact_roles", "resources", "operations"), label="metadata")
    if type(metadata["metadata_version"]) is not int or metadata["metadata_version"] != 2:
        fail("metadata-version", "This package requires exact metadata_version 2.", "unsupported")
    if (metadata["id"], metadata["version"], metadata["delivery_status"], metadata["entrypoint"]) != (PACKAGE, "0.1.0", "implemented", "SKILL.md"):
        fail("package-identity", "Unsupported package identity or delivery state.", "unsupported")
    if not exact_equal(metadata["dependencies"], {"required": [], "optional": []}):
        fail("dependencies", "This package has no skill dependencies.", "unsupported")
    fields(metadata["configuration"], ("namespace", "defaults"), label="configuration")
    if metadata["configuration"]["namespace"] != PACKAGE or not exact_equal(metadata["configuration"]["defaults"], DEFAULTS):
        fail("defaults", "Package default contract differs from this implementation.", "unsupported")
    if not exact_equal(metadata["artifact_roles"], ROLES) or not exact_equal(metadata["runtime"], RUNTIME):
        fail("metadata-contract", "Runtime or artifact role contract differs.", "unsupported")
    resources=fields(metadata["resources"], ("references","schemas","templates","tools"), label="resources")
    refs=strings(resources["references"], "references", True)
    if type(resources["schemas"]) is not list or len(resources["schemas"]) != 1:
        fail("schemas", "This package has one exact readable/writable schema.")
    schema=fields(resources["schemas"][0], ("id","version","path","owner","migration"))
    if (schema["id"],schema["version"],schema["path"],schema["owner"]) != (ROLE,"1.0.0",SCHEMA_PATH,PACKAGE):
        fail("schemas", "Unsupported schema identity.", "unsupported")
    string(schema["migration"], "migration")
    if type(resources["templates"]) is not list or len(resources["templates"]) != 1:
        fail("template", "Exactly one owned template is required.")
    template=fields(resources["templates"][0],("id","path","input_role","output_role","owner"))
    if not exact_equal(template, {"id":PACKAGE+".default-view","path":DEFAULTS["template"]["path"],"input_role":ROLE,"output_role":PACKAGE+".view","owner":PACKAGE}):
        fail("template", "Unsupported template declaration.")
    if type(resources["tools"]) is not list or len(resources["tools"]) != len(TOOLS):
        fail("tools", "Unexpected tool declarations.")
    paths=["SKILL.md","skill-package.yaml",schema["path"],template["path"],*refs]
    seen=set()
    for tool in resources["tools"]:
        fields(tool,("id","owner","implementation_status","entrypoint","operation_contract","operations"))
        key=string(tool["id"],"tool id")
        if key in seen or key not in TOOLS:
            fail("tools","Unknown or duplicate tool.")
        seen.add(key)
        entrypoint,operations,contract=TOOLS[key]
        if (tool["owner"] != PACKAGE or tool["implementation_status"] != "implemented" or
                tool["entrypoint"] != entrypoint or not exact_equal(tool["operations"],operations) or
                tool["operation_contract"] != contract or contract not in refs):
            fail("tools","Tool operation ownership mismatch.")
        paths.append(entrypoint)
    if len(paths)!=len(set(paths)) or set(paths)!=set(MEMBERS):
        fail("members","Package resources differ from the exact owned member set.")
    for path in paths:
        resource(package,path)
    if resource(package,TOOLS[PACKAGE+".fs"][0]) != Path(__file__).resolve():
        fail("package-binding","Selected package does not own this executable.","blocked")
    if type(metadata["operations"]) is not list:
        fail("operations","Operations must be an array.")
    seen=set()
    for op in metadata["operations"]:
        fields(op,("id","inputs","outputs","tool","implementation_status"))
        key=string(op["id"],"operation id")
        if key in seen or key not in ALL_OPERATIONS:
            fail("operations","Unknown or duplicate operation.")
        seen.add(key)
        strings(op["inputs"],"inputs",True)
        strings(op["outputs"],"outputs",True)
        tool_id=string(op["tool"],"tool")
        if tool_id not in TOOLS or key not in TOOLS[tool_id][1] or op["implementation_status"]!="implemented":
            fail("operations","Operation/tool ownership differs.")
    if seen != set(ALL_OPERATIONS):
        fail("operations","Missing operation.")
    return metadata

def config(path, local=False):
    value=parse_json(read_bytes(path))
    fields(value,("config_version",),("skills",) if local else ("skills","constraints"),"config")
    if type(value["config_version"]) is not int or value["config_version"] != 2:
        fail("config-version","Selected config must use exact integer version 2.","unsupported")
    for field in ("skills","constraints"):
        namespaces=value.get(field,{})
        if type(namespaces) is not dict:
            fail("namespace","Namespace container must be an object.")
        for key, child in namespaces.items():
            if not re.fullmatch(r"[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)*",key) or type(child) is not dict:
                fail("namespace","Each namespace must be a valid ID and object.")
    chosen=settings(value.get("skills",{}).get(PACKAGE,{}))
    rules=fields(value.get("constraints",{}).get(PACKAGE,{}),(),("write_roots","locked_fields"),"selected constraints")
    if "write_roots" in rules:
        strings(rules["write_roots"],"write_roots",True)
    if not set(strings(rules.get("locked_fields",[]),"locked_fields")) <= {"store.root","store.tracking","template","retention","resume_budget_chars"}:
        fail("locked-fields","Unknown selected locked field.")
    return chosen,rules

def schema_refs(schema):
    # Only bounded, acyclic same-document definitions; never remote resolution.
    remaining = [100000]
    def visit(value, active=(), depth=0):
        remaining[0] -= 1
        if remaining[0] < 0:
            fail("schema-ref", "Schema reference traversal exceeds the bound.", "unsupported")
        if depth > 64:
            fail("schema-ref","Schema nesting/reference depth exceeds the bound.","unsupported")
        if type(value) is dict:
            if any(key in value for key in ("$id","$dynamicRef","$recursiveRef")):
                fail("schema-ref","Schema rebasing/dynamic references are unsupported.","unsupported")
            if "$ref" in value:
                ref=value["$ref"]
                if type(ref) is not str or not ref.startswith("#/$defs/") or ref in active:
                    fail("schema-ref","Only acyclic same-document definition references are supported.","unsupported")
                target=schema
                try:
                    for part in ref[2:].split("/"):
                        target=target[part.replace("~1","/").replace("~0","~")]
                except (KeyError,TypeError):
                    fail("schema-ref","Missing local definition.")
                visit(target,(*active,ref),depth+1)
            for key, child in value.items():
                if key!="$ref":
                    visit(child,active,depth+1)
        elif type(value) is list:
            for child in value:
                visit(child,active,depth+1)
    visit(schema)

def validate_template(template):
    found=set(TOKEN.findall(template))
    if found != set(VIEW_FIELDS) or "{{" in TOKEN.sub("",template) or "}}" in TOKEN.sub("",template):
        fail("template-token","Template must contain each required token and no unknown/malformed tokens.")

def reference(record):
    return {"role":ROLE,"id":record["id"]}

class Binding:
    def __init__(self, request):
        self.project = safe_path(request["project_root"])
        self.package = safe_path(request["package_root"])
        if not self.project.is_dir() or not self.package.is_dir():
            fail("root", "Explicit project and package roots must exist as directories.")
        self.frozen = {resource(self.package, name): read_bytes(resource(self.package, name)) for name in MEMBERS}
        self.metadata = load_package(self.package)
        self.settings = copy.deepcopy(self.metadata["configuration"]["defaults"])
        self.settings.update(copy.deepcopy(OPERATIONAL_DEFAULTS))
        self.sources = {key: "package-metadata" for key in ("store.kind", "store.root", "store.tracking", "template")}
        self.sources.update({key: "owned-executable" for key in ("retention.compact_after_days", "retention.archive_after_days", "retention.purge_after_days", "resume_budget_chars")})
        self.foreign_names = set()
        self.config_paths = []
        project_layer, rules = {}, {}
        if "project_config" in request:
            project_path = safe_path(request["project_config"], self.project)
            self.config_paths.append(project_path)
            self.capture_config(project_path)
            project_layer, rules = config(project_path)
        merge_settings(self.settings, project_layer, self.sources, "project")
        self.project_settings = copy.deepcopy(self.settings)
        self.locks = rules.get("locked_fields", [])
        self.allowed = [safe_path(value, self.project) for value in rules.get("write_roots", [self.settings["store"]["root"]])]
        self.caller_allowed = None
        if "write_roots" in request:
            self.caller_allowed = [safe_path(value, self.project) for value in strings(request["write_roots"], "caller write_roots", True)]
        # Absolute external stores require explicit project roots, even when
        # the root originated in project settings rather than an override.
        self.explicit_roots = "write_roots" in rules
        layers = []
        if "local_config" in request:
            local_path = safe_path(request["local_config"], self.project)
            self.config_paths.append(local_path)
            self.capture_config(local_path)
            git_local_ignored(self.project, local_path)
            layers.append(("local", config(local_path, local=True)[0]))
        if "overrides" in request:
            layers.append(("invocation", settings(request["overrides"])))
        for source, layer in layers:
            merge_settings(self.settings, layer, self.sources, source)
            for locked in self.locks:
                if not exact_equal(field_value(self.settings, locked), field_value(self.project_settings, locked)):
                    fail("locked-field", f"Override changes project-locked field {locked}.", "blocked")
        self.store = safe_path(self.settings["store"]["root"], self.project)
        self.store_identity = identity(self.store.stat()) if self.store.exists() else None
        template = self.settings["template"]
        template_root = self.package if template["origin"] == "package" else self.project
        self.template_path = safe_path(template["path"], template_root)
        if not beneath(self.template_path, template_root):
            fail("template-boundary", "Template must stay within its declared root.", "blocked")
        if template["origin"] == "package" and self.template_path != resource(self.package, self.metadata["resources"]["templates"][0]["path"]):
            fail("template-resource", "A package template must be a declared template resource.")
        self.check_paths()
        try:
            template_raw = read_bytes(self.template_path)
            self.frozen[self.template_path] = template_raw
            self.template_sha256 = digest(template_raw)
            self.template = template_raw.decode("utf-8", errors="strict")
        except UnicodeError:
            fail("template-encoding", "Template must be UTF-8.")
        validate_template(self.template)
        self.check_paths()
        self.validator = None
        if request["operation"] != "explain":
            dependency("jsonschema", (4, 18), (5, 0))
            try:
                from jsonschema import Draft202012Validator, FormatChecker
                schema = parse_json(read_bytes(resource(self.package, self.metadata["resources"]["schemas"][0]["path"])))
                schema_refs(schema)
                Draft202012Validator.check_schema(schema)
                self.validator = Draft202012Validator(schema, format_checker=FormatChecker())
            except ImportError:
                fail("dependency", "jsonschema could not be imported.", "unavailable")
            except Exception as exc:
                if isinstance(exc, Fault):
                    raise
                fail("schema", "Invalid owned record schema.")

    def capture_config(self, path):
        self.frozen[path] = read_bytes(path)
        data = parse_json(self.frozen[path])
        if type(data) is dict:
            for key in ("skills", "constraints"):
                if type(data.get(key)) is dict:
                    self.foreign_names.update(name for name in data[key] if name != PACKAGE)

    def check_paths(self):
        for path, raw in self.frozen.items():
            if read_bytes(path) != raw:
                fail("binding-bytes-drift", "Selected package/config/template bytes changed.", "conflict")
        for path in (self.project, self.package, self.store, self.template_path, *self.config_paths, *self.allowed, *(self.caller_allowed or [])):
            if safe_path(str(path)) != path:
                fail("binding-drift", "Frozen path binding changed.", "conflict")
        if self.store == Path(self.store.anchor):
            fail("store-root", "Volume-root stores are forbidden.", "blocked")
        if self.store.exists() and not self.store.is_dir():
            fail("store-type", "Store must be a directory.")
        if self.store_identity is not None and (not self.store.exists() or identity(self.store.stat()) != self.store_identity):
            fail("store-drift", "Frozen store directory identity changed.", "conflict")
        if not any(beneath(self.store, root) for root in self.allowed):
            fail("write-boundary", "Selected store exceeds project write roots.", "blocked")
        if self.caller_allowed is not None and not any(beneath(self.store, root) for root in self.caller_allowed):
            fail("caller-boundary", "Selected store exceeds caller write roots.", "blocked")
        if not beneath(self.store, self.project) and not self.explicit_roots:
            fail("external-store", "An external store requires explicit project write_roots.", "blocked")
        if any(overlap(self.store, protected) for protected in (self.package, self.template_path, *self.config_paths)):
            fail("overlap", "Store overlaps installed package, config or template content.", "blocked")

    def explain(self):
        return {"settings": self.settings, "sources": self.sources, "project_root": str(self.project),
                "package_root": str(self.package), "store_root": str(self.store), "template_path": str(self.template_path),
                "locked_fields": self.locks, "write_roots": [str(p) for p in self.allowed],
                "caller_write_roots": None if self.caller_allowed is None else [str(p) for p in self.caller_allowed],
                "runtime_capability": "not-probed", "tracking": "intent-only", "storage_notice": NOTICE, "ignored_namespaces": sorted(self.foreign_names), "operational_default_authority": "owned-executable", "unsupported_reasons": []}

    def record_path(self, ref):
        fields(ref, ("role", "id"), label="record reference")
        if ref["role"] != ROLE or type(ref["id"]) is not str or not ID.fullmatch(ref["id"]):
            fail("reference", "Invalid store-scoped record reference.")
        return safe_path(ref["id"] + SUFFIX, self.store, relative_only=True)

def inspect_record(binding, ref):
    path = binding.record_path(ref)
    raw = read_bytes(path)
    record = validate_record(binding, parse_json(raw), ref["id"])
    return record, raw

def _windows_handle_filesystem(directory, volume, kernel):
    """Error-144 fallback: observe this direct directory, never substitute a drive.

    The mount-path answer must be an ancestor on the same device. All ancestors
    and the opened directory retain their identities; no link/reparse traversal
    or short-name substitution is admitted. This is not a filesystem lease.
    """
    import ctypes
    import msvcrt
    from ctypes import wintypes as w

    def snapshot():
        rows = []
        for current in (directory, *directory.parents):
            info = current.lstat()
            if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
                    or getattr(info, "st_file_attributes", 0) & 0x400
                    or not info.st_dev or not info.st_ino):
                raise OSError("direct directory identity unavailable")
            rows.append((info.st_dev, info.st_ino))
        return rows

    if (not directory.is_absolute() or str(directory).startswith(("\\\\", "//"))
            or ".." in directory.parts or Path(volume) not in (directory, *directory.parents)):
        raise OSError("direct volume path unavailable")
    before = snapshot()
    if len({device for device, _ in before}) != 1:
        raise OSError("volume identity differs across ancestors")
    # A long-name query alone does not expand SUBST/DOS-device aliases.
    kernel.QueryDosDeviceW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.QueryDosDeviceW.restype = w.DWORD
    device = ctypes.create_unicode_buffer(32768)
    length = kernel.QueryDosDeviceW(directory.drive, device, len(device))
    if not 0 < length < len(device) or re.fullmatch(r"\\Device\\[^\\]+", device.value) is None:
        raise OSError("direct drive mapping unavailable")
    kernel.GetLongPathNameW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.GetLongPathNameW.restype = w.DWORD
    canonical = ctypes.create_unicode_buffer(32768)
    length = kernel.GetLongPathNameW(str(directory), canonical, len(canonical))
    if not 0 < length < len(canonical) or Path(canonical.value) != directory:
        raise OSError("canonical directory identity unavailable")
    kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
    kernel.CreateFileW.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.CloseHandle.restype = w.BOOL
    kernel.GetVolumeInformationByHandleW.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, ctypes.POINTER(w.DWORD),
                                                    ctypes.c_void_p, ctypes.c_void_p, w.LPWSTR, w.DWORD]
    kernel.GetVolumeInformationByHandleW.restype = w.BOOL
    # Metadata-only OPEN_EXISTING, BACKUP_SEMANTICS | OPEN_REPARSE_POINT.
    handle = kernel.CreateFileW(str(directory), 0, 7, None, 3, 0x02200000, None)
    if handle in (None, ctypes.c_void_p(-1).value):
        raise OSError("directory handle unavailable")
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY)
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    try:
        info = os.fstat(descriptor)
        if ((info.st_dev, info.st_ino) != before[0] or not stat.S_ISDIR(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 0x400):
            raise OSError("opened directory identity differs")
        filesystem, serial = ctypes.create_unicode_buffer(64), w.DWORD()
        if not kernel.GetVolumeInformationByHandleW(handle, None, 0, ctypes.byref(serial), None, None,
                                                   filesystem, len(filesystem)):
            raise OSError("handle filesystem observation failed")
        if serial.value != (info.st_dev & 0xffffffff) or snapshot() != before:
            raise OSError("directory volume identity changed")
        return filesystem.value
    finally:
        os.close(descriptor)


def local_write_backend(store):
    ancestor = store
    while not ancestor.exists():
        ancestor = ancestor.parent
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        root = ctypes.create_unicode_buffer(32768)
        kernel.GetVolumePathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetVolumePathNameW.restype = ctypes.c_int
        if not kernel.GetVolumePathNameW(str(ancestor), root, len(root)):
            fail("filesystem", "Cannot identify the local write volume.", "unsupported")
        kernel.GetDriveTypeW.argtypes = [ctypes.c_wchar_p]
        kernel.GetDriveTypeW.restype = ctypes.c_uint32
        if kernel.GetDriveTypeW(root.value) not in (3, 6):
            fail("filesystem", "Only local fixed or RAM volumes are supported for writes.", "unsupported")
        filesystem = ctypes.create_unicode_buffer(64)
        kernel.GetVolumeInformationW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32,
                                               ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                               ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetVolumeInformationW.restype = ctypes.c_int
        if not kernel.GetVolumeInformationW(root.value, None, 0, None, None, None, filesystem, len(filesystem)):
            if ctypes.get_last_error() != 144:  # ERROR_DIR_NOT_ROOT only
                fail("filesystem", "Cannot observe the local write filesystem.", "unsupported")
            try:
                filesystem.value = _windows_handle_filesystem(ancestor, root.value, kernel)
            except OSError:
                fail("filesystem", "Cannot verify the direct write volume.", "unsupported")
        if filesystem.value != "NTFS":
            fail("filesystem", "Initial Windows writes require local NTFS.", "unsupported")
        return "local-ntfs"
    if sys.platform.startswith("linux"):
        try:
            mounts = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
            candidates = []
            for line in mounts:
                left, right = line.split(" - ", 1)
                mount_path = re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), left.split()[4])
                if beneath(ancestor, Path(mount_path)):
                    candidates.append((len(Path(mount_path).parts), right.split()[0]))
            filesystem = max(candidates)[1] if candidates else ""
        except (OSError, ValueError, IndexError):
            fail("filesystem", "Cannot identify the local write mount.", "unsupported")
        if filesystem not in {"ext2", "ext3", "ext4", "xfs", "btrfs", "tmpfs", "ramfs"}:
            fail("filesystem", "Unproven, shared or network write backend is unsupported.", "unsupported")
        return "local-" + filesystem
    fail("filesystem", "Write publication semantics are unsupported on this platform.", "unsupported")

class Writer:
    """Own only an exclusive token lock and temp inode; never recover others."""
    def __init__(self, binding):
        self.binding = binding
        self.token = uuid.uuid4().hex
        self.lock = binding.store / ".workflow-write.lock"
        self.temp = binding.store / (".workflow-" + self.token + ".tmp")
        self.owned = {}
        self.mutation_state = "none"
        self.directories_created = []

    def exclusive(self, path, raw):
        self.binding.check_paths()
        safe_path(str(path))
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        # Register ownership before I/O so partial-write failures can be cleaned.
        self.owned[path] = (identity(os.fstat(fd)), raw, False)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.owned[path] = (self.owned[path][0], raw, True)

    def acquire(self, allow_create):
        self.binding.check_paths()
        local_write_backend(self.binding.store)
        if not self.binding.store.exists() and not allow_create:
            fail("missing-store", "Update requires an existing workflow store and record.")
        missing = []
        cursor = self.binding.store
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        for path in reversed(missing):
            self.binding.check_paths()
            if not any(beneath(path, root) for root in self.binding.allowed):
                fail("parent-permission", "Missing store parent is outside project write_roots; provision it separately.", "blocked")
            if self.binding.caller_allowed is not None and not any(beneath(path, root) for root in self.binding.caller_allowed):
                fail("parent-permission", "Missing store parent is outside caller write_roots.", "blocked")
            try:
                path.mkdir()
                self.directories_created.append(str(path))
            except FileExistsError:
                if not path.is_dir():
                    raise
        self.binding.store_identity = identity(self.binding.store.stat())
        try:
            self.exclusive(self.lock, (self.token + "\n").encode("ascii"))
        except FileExistsError:
            fail("writer-lock", "Store has an existing writer lock; no stale-lock recovery attempted.", "conflict")
        self.binding.check_paths()

    def publish(self, path, raw, replacing, expected=None):
        if len(raw) > LIMIT:
            fail("size-limit", "Serialized record exceeds the 4 MiB limit.", "unsupported")
        self.exclusive(self.temp, raw)
        self.binding.check_paths()
        safe_path(str(path))
        if replacing and digest(read_bytes(path)) != expected:
            fail("digest-conflict", "Record changed immediately before replacement.", "conflict")
        self.mutation_state = "unknown"
        try:
            if replacing:
                os.replace(self.temp, path)
                del self.owned[self.temp]
            else:
                os.link(self.temp, path)  # Atomic complete-file, exclusive publish.
        except FileExistsError:
            self.mutation_state = "none"
            fail("record-collision", "Create identity already exists; no overwrite.", "conflict")
        if read_bytes(path) != raw:
            self.mutation_state = "unknown"
            fail("publication-readback", "Published bytes could not be confirmed; reread before retry.", "failed")
        self.mutation_state = "committed"

    def cleanup(self):
        failures = []
        for path in (self.temp, self.lock):
            if path not in self.owned:
                continue
            expected_identity, raw, complete = self.owned[path]
            try:
                self.binding.check_paths()
                safe_path(str(path))
                info = path.lstat()
                if identity(info) != expected_identity or not stat.S_ISREG(info.st_mode):
                    fail("cleanup-identity", "Owned transient file identity changed.", "failed")
                actual = read_bytes(path)
                # A partial lock is not a matching-token lock: preserve it for
                # explicit recovery. Temp partial bytes remain ours by inode.
                if (path == self.lock or complete) and actual != raw:
                    fail("cleanup-content", "Owned transient content changed; preserved.", "failed")
                path.unlink()
            except Exception:
                failures.append({"code": "cleanup-failed", "resource": "lock" if path == self.lock else "temporary-file",
                                 "message": "Owned transient cleanup failed; inspect before retry."})
        return failures

def escape_markdown(text):
    escaped = html.escape(text, quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escaped)

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        fail("arguments", "Use --request <explicit JSON file or ->.")

def main():
    operation = None
    try:
        parser = ArgumentParser(description=__doc__, allow_abbrev=False)
        parser.add_argument("--request", required=True, help="Absolute JSON request filename, or - for stdin")
        args = parser.parse_args()
        if args.request == "-":
            raw = sys.stdin.buffer.read(LIMIT + 1)
            if len(raw) > LIMIT:
                fail("size-limit", "Request exceeds the 4 MiB limit.", "unsupported")
        else:
            raw = read_bytes(safe_path(args.request))
        request = parse_json(raw)
        if type(request) is dict and type(request.get("operation")) is str and request["operation"] in OPERATIONS:
            operation = request["operation"]
        result = execute(request)
    except Fault as exc:
        result = {"outcome": exc.outcome, "diagnostics": [exc.diagnostic()]}
    except OSError:
        result = {"outcome": "blocked", "diagnostics": [{"code": "read-io", "message": "Selected input is inaccessible."}]}
    except Exception:
        result = {"outcome": "failed", "diagnostics": [{"code": "internal", "message": "Unexpected failure; inputs were not echoed."}]}
    result = {"operation": operation, "mutation_state": "none", **result}
    response_bytes = encode(result)
    if len(response_bytes) > LIMIT:
        result = {"operation": operation, "outcome": "unsupported", "mutation_state": result.get("mutation_state", "none"),
                  "diagnostics": [{"code": "result-limit", "message": "Result exceeds the 4 MiB limit; inspect the selected identity before retry."}],
                  **{key: result[key] for key in ("reference", "sha256", "store_root", "directories_created") if key in result}}
        response_bytes = encode(result)
    sys.stdout.buffer.write(response_bytes)
    return 0 if result["outcome"] == "succeeded" else 1


def settings(value, complete=False):
    keys = ("store", "template", "retention", "resume_budget_chars")
    fields(value, keys if complete else (), () if complete else keys, "skill settings")
    if "store" in value:
        store = fields(value["store"], ("kind", "root", "tracking") if complete else (),
                       () if complete else ("kind", "root", "tracking"), "store")
        if "kind" in store and store["kind"] != "filesystem":
            fail("store-kind", "Only filesystem stores are supported.", "unsupported")
        if "root" in store:
            string(store["root"], "store.root")
        if "tracking" in store and store["tracking"] not in ("tracked", "ignored"):
            fail("tracking", "Tracking must be tracked or ignored.")
    if "template" in value:
        template = fields(value["template"], ("origin", "path"), label="template")
        if template["origin"] not in ("package", "project"):
            fail("template-origin", "Unsupported template origin.")
        string(template["path"], "template.path")
    if "retention" in value:
        keys = tuple(OPERATIONAL_DEFAULTS["retention"])
        retention = fields(value["retention"], keys if complete else (),
                           () if complete else keys, "retention")
        for age in retention.values():
            if age is not None and (type(age) is not int or not 1 <= age <= 36500):
                fail("retention-age", "Age must be null or an exact integer from 1 to 36500.")
    if "resume_budget_chars" in value:
        budget = value["resume_budget_chars"]
        if type(budget) is not int or not 2000 <= budget <= 64000:
            fail("resume-budget", "Resume budget must be an exact integer from 2000 to 64000.")
    return value


def merge_settings(target, layer, sources, source):
    for group in ("store", "retention"):
        for key, value in layer.get(group, {}).items():
            target[group][key] = value
            sources[group + "." + key] = source
    for key in ("template", "resume_budget_chars"):
        if key in layer:
            target[key] = copy.deepcopy(layer[key])
            sources[key] = source


def field_value(value, field):
    if "." in field:
        group, leaf = field.split(".", 1)
        return value[group][leaf]
    return value[field]


def timestamp(value):
    if type(value) is not str or not re.fullmatch(
            r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)", value):
        fail("time", "RFC3339 timestamp with seconds and explicit offset required.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail("time", "Invalid timestamp.")
    if parsed.tzinfo is None:
        fail("time", "Timestamp needs a zone.")
    return parsed


def indexed(rows):
    result = {}
    for row in rows:
        if row["id"] in result:
            fail("duplicate-id", "Record contains a repeated stable identity.")
        result[row["id"]] = row
    return result


def require_refs(values, available):
    if len(values) != len(set(values)) or not set(values) <= available.keys():
        fail("reference", "An internal reference is missing or duplicated.")


def content_digest(content):
    normalized = copy.deepcopy(content)
    normalized["next_action"] = None
    return digest(encode(normalized))


def snapshot(record):
    return copy.deepcopy({key: record[key] for key in
                          ("state", "state_reason", "content", "retrospective")})


def check_content(content, state, observed):
    tasks = indexed(content["tasks"])
    evidence = indexed(content["evidence"])
    references = indexed(content["references"])
    indexed(content["acceptance"])
    indexed(content["decisions"])
    for reference_item in references.values():
        if reference_item["kind"] == "same-store-workflow" and not ID.fullmatch(reference_item["target"]):
            fail("workflow-reference", "Same-store workflow references require an exact workflow ID.")
    for item in evidence.values():
        if item["task_id"] is not None and item["task_id"] not in tasks:
            fail("evidence-task", "Evidence names a missing task.")
        require_refs(item["source_refs"], references)
        if item["disposition"] in ("succeeded", "failed") and (
                not item["source_refs"] or item["observed_at"] is None):
            fail("evidence-source", "Success/failure reports need an actual source reference and reported observation time.")
        if item["observed_at"] is not None and timestamp(item["observed_at"]) > observed:
            fail("evidence-time", "Reported evidence time is later than the record observation.")
    for task in tasks.values():
        require_refs(task["depends_on"], tasks)
        require_refs(task["evidence_ids"], evidence)
        if task["id"] in task["depends_on"]:
            fail("dependency-self", "A task cannot depend on itself.")
        if task["state"] in ("active", "completed") and any(
                tasks[key]["state"] != "completed" for key in task["depends_on"]):
            fail("dependency-state", "Only completed dependencies satisfy active/completed tasks.")
        if task["state"] not in ("pending", "active"):
            string(task["reason"], "task reason")
            string(task["result"], "task result")
        if (task["state"] == "deferred") != (task["deferral"] is not None):
            fail("task-deferral", "Deferred tasks require an explicit deferral; other states require null.")
        if task["state"] == "completed":
            if not task["evidence_ids"] or not any(evidence[key]["disposition"] == "succeeded"
                                                for key in task["evidence_ids"]):
                fail("task-result", "Completed tasks need retained reported success evidence.")
            if any(evidence[key]["task_id"] not in (None, task["id"]) for key in task["evidence_ids"]):
                fail("task-evidence", "Task evidence belongs to a different task.")
    # Iterative topological traversal avoids recursion on a long but bounded task list.
    outstanding = {key: len(row["depends_on"]) for key, row in tasks.items()}
    successors = {key: [] for key in tasks}
    for key, task in tasks.items():
        for dependency_id in task["depends_on"]:
            successors[dependency_id].append(key)
    ready = [key for key, count in outstanding.items() if not count]
    visited = 0
    while ready:
        key = ready.pop()
        visited += 1
        for successor in successors[key]:
            outstanding[successor] -= 1
            if not outstanding[successor]:
                ready.append(successor)
    if visited != len(tasks):
        fail("dependency-cycle", "Task dependencies must be acyclic.")
    for item in content["acceptance"]:
        require_refs(item["evidence_ids"], evidence)
        if item["disposition"] in ("succeeded", "failed") and (
                not item["evidence_ids"] or not any(evidence[key]["disposition"] == item["disposition"]
                                                  for key in item["evidence_ids"])):
            fail("acceptance-evidence", "Reported acceptance outcome needs matching evidence.")
        if item["disposition"] in ("not-applicable", "deferred", "blocked", "failed"):
            string(item["reason"], "acceptance reason")
        if (item["disposition"] == "deferred") != (item["deferral"] is not None):
            fail("acceptance-deferral", "Deferred acceptance needs a deferral; other dispositions require null.")
    for decision in content["decisions"]:
        require_refs(decision["source_refs"], references)
        if decision["state"] == "open":
            string(decision["next_action"], "decision next action")
        elif decision["resolution"] is None or not decision["source_refs"] or decision["next_action"] is not None:
            fail("decision-resolution", "Resolved decisions require resolution/source references and null next action.")
    action = content["next_action"]
    if state in ("completed", "cancelled"):
        if action is not None:
            fail("terminal-action", "Terminal workflows cannot retain an active next action.")
    elif action is None:
        fail("next-action", "Nonterminal workflows need a concrete next action.")
    if action is not None and action["task_id"] is not None and action["task_id"] not in tasks:
        fail("next-task", "Next action names a missing task.")


def check_retrospective(value, content, observed):
    if value is None:
        return
    if timestamp(value["recorded_at"]) > observed or value["content_sha256"] != content_digest(content):
        fail("retrospective-binding", "Retrospective does not bind the current content/time.")
    if (value["outcome"] == "no-new-knowledge") != (len(value["candidates"]) == 0):
        fail("retrospective-outcome", "No-new-knowledge has no candidates; candidates outcome needs candidates.")
    indexed(value["candidates"])
    evidence = indexed(content["evidence"])
    references = indexed(content["references"])
    for candidate in value["candidates"]:
        if DESTINATIONS[candidate["destination"]] != candidate["operation"]:
            fail("candidate-operation", "Candidate operation does not belong to the selected destination.")
        require_refs(candidate["source_evidence_ids"], evidence)
        require_refs(candidate["result_refs"], references)
        if candidate["state"] == "open":
            string(candidate["next_action"], "candidate next action")
            if candidate["result_refs"]:
                fail("candidate-result", "Open candidates cannot claim returned artifacts.")
        elif candidate["state"] == "handed-off" and not candidate["result_refs"]:
            fail("candidate-result", "Handed-off candidates need actual returned references.")
        elif candidate["state"] == "declined" and candidate["result_refs"]:
            fail("candidate-result", "Declined candidates do not have returned artifacts.")


def completion_ready(content, retrospective):
    if any(t["state"] not in ("completed", "deferred", "cancelled") for t in content["tasks"]):
        fail("unfinished-tasks", "Complete, explicitly defer or cancel every task before completion.", "blocked")
    if any(a["disposition"] not in ("succeeded", "not-applicable", "deferred") for a in content["acceptance"]):
        fail("unfinished-acceptance", "Required failed/blocked/unexecuted acceptance keeps work open.", "blocked")
    if any(d["state"] == "open" for d in content["decisions"]) or any(
            r["blocking"] and r["resolution"] != "resolved" for r in content["references"]):
        fail("unresolved", "Open decisions or unresolved blocking references keep work open.", "blocked")
    if retrospective is None or retrospective["content_sha256"] != content_digest(content):
        fail("retrospective-required", "Current content needs a retained retrospective before completion.", "blocked")


def check_content_change(old, new):
    for collection, immutable_keys in (
            ("tasks", ()), ("acceptance", ("criterion",)), ("decisions", ("question",)),
            ("references", ("kind", "target", "schema", "sha256"))):
        previous, current = indexed(old[collection]), indexed(new[collection])
        if not previous.keys() <= current.keys():
            fail("lost-identity", "Stable task/acceptance/decision/reference identities cannot be removed.")
        for key, before in previous.items():
            after = current[key]
            if any(not exact_equal(before[field], after[field]) for field in immutable_keys):
                fail("identity-meaning", "Changed stable meaning needs a new identity.")
            if collection == "tasks":
                if before["state"] in ("completed", "cancelled") and not exact_equal(before, after):
                    fail("terminal-task", "Terminal tasks are immutable; add a new task.", "unsupported")
                if after["state"] != before["state"] and after["state"] not in TASK_TRANSITIONS[before["state"]]:
                    fail("task-transition", "Unsupported task state transition.", "unsupported")
        if collection == "tasks" and any(row["state"] != "pending" for key, row in current.items()
                                          if key not in previous):
            fail("new-task-state", "New tasks must start pending.")
    if len(new["evidence"]) < len(old["evidence"]) or not exact_equal(
            old["evidence"], new["evidence"][:len(old["evidence"])]):
        fail("evidence-immutable", "Evidence is append-only; corrections require a new observation.")


def check_delta(before, after, operation):
    if before["state"] in ("completed", "cancelled"):
        fail("terminal-record", "Terminal workflows are immutable.", "unsupported")
    if operation == "checkpoint":
        if (after["state"] != before["state"] or after["state_reason"] != before["state_reason"]
                or after["retrospective"] is not None):
            fail("checkpoint-shape", "Checkpoint changes authored content and invalidates the retrospective only.")
        check_content_change(before["content"], after["content"])
    elif operation == "transition":
        if after["state"] not in WORKFLOW_TRANSITIONS[before["state"]]:
            fail("transition", "Unsupported workflow state transition.", "unsupported")
        expected = copy.deepcopy(before["content"])
        if after["state"] in ("completed", "cancelled"):
            expected["next_action"] = None
        if not exact_equal(after["content"], expected) or not exact_equal(after["retrospective"], before["retrospective"]):
            fail("transition-content", "Transition cannot replace authored content or retrospective.")
    elif operation == "retrospect":
        if any(not exact_equal(before[key], after[key]) for key in ("state", "state_reason", "content")) or after["retrospective"] is None:
            fail("retrospect-content", "Retrospect changes only the owned retrospective.")
        if before["retrospective"] is not None:
            prior = indexed(before["retrospective"]["candidates"])
            latest = indexed(after["retrospective"]["candidates"])
            if not prior.keys() <= latest.keys():
                fail("lost-candidate", "Disposition existing candidates explicitly; do not erase identities.")
            for key, candidate in prior.items():
                if any(not exact_equal(candidate[name], latest[key][name])
                       for name in ("destination", "operation", "source_evidence_ids", "applicability")):
                    fail("candidate-identity", "Changed candidate meaning needs a new identity.")
    else:
        fail("history-operation", "Unknown history operation.")


def validate_record(binding, record, expected_id=None):
    if type(record) is not dict or record.get("schema_version") != "1.0.0":
        fail("record-version", "Unsupported record version; original bytes preserved.", "unsupported")
    if next(binding.validator.iter_errors(record), None) is not None:
        fail("record-schema", "Record does not satisfy the selected owned schema.")
    if type(record["revision"]) is not int or any(type(row["from_revision"]) is not int for row in record["history"]):
        fail("record-revision", "Revision numbers must be exact integers.")
    if expected_id is not None and record["id"] != expected_id:
        fail("record-id", "Record ID and filename disagree.")
    created, updated = timestamp(record["created_at"]), timestamp(record["updated_at"])
    if updated < created or updated > datetime.now(timezone.utc):
        fail("record-time", "Record chronology is invalid or in the future.")
    history = record["history"]
    if record["revision"] != len(history) + 1:
        fail("record-history", "Revision and history length disagree.")
    states = [row["previous_state"] for row in history] + [snapshot(record)]
    previous_time = created
    for index, state_value in enumerate(states):
        state_time = created if index == 0 else timestamp(history[index - 1]["recorded_at"])
        if state_time < previous_time or state_time > updated:
            fail("history-time", "History times must be ordered within record lifetime.")
        previous_time = state_time
        check_content(state_value["content"], state_value["state"], state_time)
        check_retrospective(state_value["retrospective"], state_value["content"], state_time)
        if state_value["retrospective"] is not None and timestamp(state_value["retrospective"]["recorded_at"]) < created:
            fail("retrospective-time", "Retrospective time cannot precede workflow creation.")
        if state_value["state"] == "completed":
            completion_ready(state_value["content"], state_value["retrospective"])
        if index:
            row = history[index - 1]
            if row["from_revision"] != index:
                fail("history-revision", "History revisions must be contiguous.")
            check_delta(states[index - 1], state_value, row["operation"])
    if previous_time != updated:
        fail("history-time", "Last history event must match updated_at.")
    initial = states[0]
    if initial["state"] != "planned" or initial["retrospective"] is not None or any(
            row["state"] != "pending" for row in initial["content"]["tasks"]) or initial["content"]["evidence"]:
        fail("initial-state", "Initial record must be planned with pending tasks and no fabricated evidence.")
    historical_candidates(record)
    return record


def create_record(request):
    content = fields(request["content"], ("title", "intent", "scope", "acceptance", "first_action"),
                     label="minimal create content")
    string(content["title"], "title")
    string(content["intent"], "intent")
    action = fields(content["first_action"], ("action", "completion_condition", "owner"), label="first action")
    for value in action.values():
        string(value, "first action field")
    if type(content["acceptance"]) is not list or not content["acceptance"]:
        fail("acceptance", "Create needs nonempty acceptance.")
    acceptance = []
    for row in content["acceptance"]:
        fields(row, ("id", "criterion"), label="initial acceptance")
        acceptance.append({**copy.deepcopy(row), "disposition": "not-executed", "evidence_ids": [],
                           "reason": "Not executed by this tool.", "deferral": None})
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    record = {"schema_version": "1.0.0", "kind": "workflow", "owner": "project",
              "id": ID_PREFIX + uuid.uuid4().hex, "revision": 1, "created_at": now, "updated_at": now,
              "state": "planned", "state_reason": "Created as planned work.", "history": [],
              "retrospective": None,
              "content": {"title": content["title"], "intent": content["intent"],
                          "scope": copy.deepcopy(content["scope"]), "acceptance": acceptance,
                          "tasks": [{"id": "T001", "title": action["action"], "action": action["action"],
                                     "completion_condition": action["completion_condition"], "depends_on": [],
                                     "state": "pending", "reason": "", "result": "", "evidence_ids": [], "deferral": None}],
                          "evidence": [], "decisions": [], "references": [],
                          "next_action": {"task_id": "T001", "owner": action["owner"],
                                          "action": action["action"], "condition": "After actual task authorization."}}}
    if "extensions" in request:
        record["extensions"] = copy.deepcopy(request["extensions"])
    return record


def write_operation(binding, request):
    operation = request["operation"]
    creating = operation == "create"
    candidate = create_record(request) if creating else None
    if creating:
        validate_record(binding, candidate)
    else:
        binding.record_path(request["reference"])
        expected = string(request["expected_sha256"], "expected_sha256")
        if not SHA256.fullmatch(expected):
            fail("expected-digest", "Expected an actual raw-byte SHA-256.")
    writer = Writer(binding)
    result = {"outcome": "failed"}
    publication = {}
    try:
        writer.acquire(creating)
        if creating:
            record, changed = candidate, True
            raw = encode(record)
            publication = {"reference": reference(record), "sha256": digest(raw), "store_root": str(binding.store)}
            writer.publish(binding.record_path(reference(record)), raw, False)
        else:
            current, original = inspect_record(binding, request["reference"])
            if digest(original) != expected:
                fail("digest-conflict", "Record bytes changed; inspect before retry.", "conflict")
            if current["state"] in ("completed", "cancelled"):
                fail("terminal-record", "Terminal workflows are immutable; use a linked successor.", "unsupported")
            record = copy.deepcopy(current)
            now = datetime.now(timezone.utc)
            if now < timestamp(current["updated_at"]):
                fail("clock-regression", "Clock precedes the previous update.", "blocked")
            event_time = now.isoformat(timespec="microseconds")
            if operation == "checkpoint":
                reason = string(request["reason"], "reason")
                if exact_equal(request["content"], current["content"]):
                    changed = False
                else:
                    record["content"] = copy.deepcopy(request["content"])
                    record["retrospective"] = None
                    changed = True
            elif operation == "transition":
                reason = string(request["reason"], "reason")
                if request["expected_state"] != current["state"]:
                    fail("state-conflict", "Workflow state changed.", "conflict")
                target = string(request["target_state"], "target_state")
                if target not in WORKFLOW_TRANSITIONS[current["state"]]:
                    fail("transition", "Unsupported workflow transition.", "unsupported")
                record.update(state=target, state_reason=reason)
                if target in ("completed", "cancelled"):
                    record["content"]["next_action"] = None
                changed = True
            else:
                value = fields(request["retrospective"], ("outcome", "reflection", "rationale", "candidates"),
                               label="authored retrospective")
                reason = string(value["rationale"], "retrospective rationale")
                authored_prior = None if current["retrospective"] is None else {
                    key: current["retrospective"][key] for key in value}
                changed = not exact_equal(value, authored_prior)
                if changed:
                    record["retrospective"] = {**copy.deepcopy(value), "basis": "caller-supplied",
                                               "recorded_at": event_time,
                                               "content_sha256": content_digest(current["content"])}
            if changed:
                record["revision"] += 1
                record["updated_at"] = event_time
                record["history"].append({"from_revision": current["revision"], "operation": operation,
                                          "recorded_at": event_time, "reason": reason,
                                          "previous_sha256": expected, "previous_state": snapshot(current)})
                validate_record(binding, record, current["id"])
                raw = encode(record)
                publication = {"reference": reference(record), "sha256": digest(raw), "store_root": str(binding.store)}
                binding.check_paths()
                writer.publish(binding.record_path(request["reference"]), raw, True, expected)
            else:
                binding.check_paths()
                if read_bytes(binding.record_path(request["reference"])) != original:
                    fail("digest-conflict", "Record changed before no-op read-back.", "conflict")
                raw = original
        result = {"outcome": "succeeded", "reference": reference(record), "sha256": digest(raw),
                  "store_root": str(binding.store), "changed": changed}
    except Fault as exc:
        result = {"outcome": exc.outcome, "diagnostics": [exc.diagnostic()]}
    except OSError:
        result = {"outcome": "blocked" if writer.mutation_state == "none" else "failed",
                  "diagnostics": [{"code": "write-io", "message": "Write failed; no fallback or rollback claimed."}]}
    except (Exception, KeyboardInterrupt):
        result = {"outcome": "failed", "diagnostics": [{"code": "write-failure", "message": "Write interrupted or failed; inspect before retry."}]}
    finally:
        if writer.mutation_state != "none":
            result.update(publication)
        cleanup = writer.cleanup()
        if cleanup:
            result["outcome"] = "failed"
            result.setdefault("diagnostics", []).extend(cleanup)
        result["mutation_state"] = writer.mutation_state
        result["directories_created"] = writer.directories_created
    return result


def scan_store(binding, visitor):
    """Read each direct candidate once. This is a scoped, non-atomic observation."""
    binding.check_paths()
    selected = []
    try:
        for path in binding.store.iterdir() if binding.store.exists() else ():
            if path.name.endswith(SUFFIX):
                selected.append(path)
                if len(selected) > MAX_FILES:
                    fail("scan-limit", "Store exceeds 10000 direct candidates; no complete scan available.", "unsupported")
    except OSError:
        fail("scan-store", "Cannot enumerate the selected store.", "blocked")
    selected.sort(key=lambda path: path.name)
    inventory, diagnostics = [], []
    for path in selected:
        item = {"filename": path.name}
        try:
            record_id = path.name.removesuffix(SUFFIX)
            if not ID.fullmatch(record_id):
                fail("filename", "Invalid workflow filename.")
            raw = read_bytes(path)
            item["sha256"] = digest(raw)
            record = validate_record(binding, parse_json(raw), record_id)
        except (Fault, OSError) as exc:
            diagnostic = exc.diagnostic() if isinstance(exc, Fault) else {
                "code": "read-error", "message": "Selected record is unreadable."}
            item["error"] = diagnostic["code"]
            diagnostics.append({"filename": path.name, **diagnostic})
        else:
            visitor(record, raw)
        inventory.append(item)
    binding.check_paths()
    return {"store_root": str(binding.store), "scope": "direct workflow filenames in selected store only",
            "selected_count": len(selected), "partial": bool(diagnostics), "diagnostics": diagnostics,
            "inventory_sha256": digest(encode(inventory)), "observation": "non-atomic; external references unscanned"}


def query(binding, text):
    if type(text) is not str:
        fail("query-text", "Query text must be a string.")
    matches = []
    output_size = 0
    def visit(record, raw):
        nonlocal output_size
        if any(text.casefold() in record["content"][key].casefold() for key in ("title", "intent")):
            item = {"reference": reference(record), "title": record["content"]["title"],
                    "state": record["state"], "revision": record["revision"], "sha256": digest(raw)}
            output_size += len(encode(item))
            if output_size > LIMIT // 2:
                fail("query-output", "Query matches exceed the result bound; narrow the literal query.", "unsupported")
            matches.append(item)
    observed = scan_store(binding, visit)
    return {"text": text, "matches": matches, **observed}


def historical_candidates(record):
    candidates = {}
    values = [row["previous_state"]["retrospective"] for row in record["history"]] + [record["retrospective"]]
    for value in values:
        if value is not None:
            for candidate in value["candidates"]:
                prior = candidates.get(candidate["id"])
                if prior is not None and any(not exact_equal(prior[key], candidate[key])
                        for key in ("destination", "operation", "source_evidence_ids", "applicability")):
                    fail("candidate-history", "Candidate identity was reused with different meaning.")
                candidates[candidate["id"]] = candidate
    return list(candidates.values())


def changed_values(before, after):
    changes = {}
    for key in before.keys() | after.keys():
        if not exact_equal(before.get(key), after.get(key)):
            changes[key] = {"before": before.get(key), "after": after.get(key)}
    return changes


def continuation(binding, record, raw):
    history = []
    snapshots = [item["previous_state"] for item in record["history"]] + [snapshot(record)]
    for index, event in enumerate(record["history"]):
        before, after = snapshots[index], snapshots[index + 1]
        changes = {}
        for key in ("state", "state_reason", "retrospective"):
            if not exact_equal(before[key], after[key]):
                changes[key] = {"before": before[key], "after": after[key]}
        changes["content"] = changed_values(before["content"], after["content"])
        history.append({"from_revision": event["from_revision"], "operation": event["operation"],
                        "reason": event["reason"], "recorded_at": event["recorded_at"],
                        "previous_sha256": event["previous_sha256"], "changes": changes})
    disposition = None
    if record["state"] == "completed":
        disposition = "with-deferrals" if any(a["disposition"] == "deferred" for a in record["content"]["acceptance"]) or any(
            t["state"] == "deferred" for t in record["content"]["tasks"]) else "without-deferrals"
    view = {"reference": reference(record), "store_root": str(binding.store), "schema_version": "1.0.0",
            "revision": record["revision"], "sha256": digest(raw), "state": record["state"],
            "state_reason": record["state_reason"], "content": record["content"],
            "retrospective": record["retrospective"], "retained_candidates": historical_candidates(record),
            "history_changes": history, "omitted_history": [],
            "completion_disposition": disposition, "tracking_intent": binding.settings["store"]["tracking"],
            "storage_notice": NOTICE, "evidence_basis": "caller-supplied; not independently verified"}
    if len(encode(view).decode("utf-8")) > binding.settings["resume_budget_chars"]:
        fail("resume-limit", "Required continuation meaning exceeds the selected summary budget; inspect the full record.", "unsupported")
    return view



def retention_preview(binding, request):
    mode = request["mode"]
    if mode not in ("compact", "archive", "purge"):
        fail("retention-mode", "Only compact/archive/purge previews are supported.", "unsupported")
    selection = strings(request["selection"], "selection", True)
    if len(selection) > 100 or any(not ID.fullmatch(key) for key in selection):
        fail("retention-selection", "Select between 1 and 100 exact workflow IDs.")
    selected = set(selection)
    records, inbound = {}, {key: [] for key in selection}
    def visit(record, raw):
        if record["id"] in selected:
            records[record["id"]] = (record, raw)
        for item in record["content"]["references"]:
            if item["kind"] == "same-store-workflow" and item["target"] in selected:
                inbound[item["target"]].append({"source": reference(record), "source_sha256": digest(raw),
                                                "reference_id": item["id"]})
    scan = scan_store(binding, visit)
    now = datetime.now(timezone.utc)
    threshold = binding.settings["retention"][mode + "_after_days"]
    items = []
    for key in selection:
        protections = []
        item = {"reference": {"role": ROLE, "id": key}, "disposition": "protected", "protections": protections,
                "external_inbound_references": "unknown; a one-store scan cannot prove absence",
                "source_removal_authorized": False, "inbound_same_store": inbound[key]}
        items.append(item)
        if key not in records:
            protections.append("missing-unreadable-or-unsupported-selected-record")
            continue
        record, raw = records[key]
        item["sha256"] = digest(raw)
        item["schema_version"] = record["schema_version"]
        item["revision"] = record["revision"]
        item["threshold_days"] = threshold
        if record["state"] not in ("completed", "cancelled"):
            protections.append("nonterminal-workflow")
        age = (now - timestamp(record["updated_at"])).total_seconds() / 86400
        item["closed_age_days"] = age if record["state"] in ("completed", "cancelled") else None
        if threshold is None:
            protections.append("mode-disabled")
        elif age < threshold:
            protections.append("retention-age-not-reached")
        content = record["content"]
        if any(t["state"] not in ("completed", "cancelled") for t in content["tasks"]):
            protections.append("active-failed-blocked-or-deferred-task")
        if any(a["disposition"] in ("deferred", "planned", "not-executed", "failed", "blocked")
               for a in content["acceptance"]):
            protections.append("unresolved-acceptance-or-deferral")
        if any(d["state"] == "open" for d in content["decisions"]):
            protections.append("open-decision")
        if any(c["state"] == "open" for c in historical_candidates(record)):
            protections.append("open-current-or-historical-knowledge-candidate")
        if any(r["resolution"] != "resolved" or r["blocking"] for r in content["references"]):
            protections.append("unresolved-or-blocking-reference")
        if any(r["evidence_value"] != "replaceable" for r in content["references"]):
            protections.append("irreplaceable-or-unknown-evidence")
        if mode != "compact" and inbound[key]:
            protections.append("referenced-same-store-target")
        if scan["partial"]:
            protections.append("incomplete-reference-scan")
        try:
            item["summary"] = continuation(binding, record, raw)
        except Fault as exc:
            if exc.code != "resume-limit":
                raise
            protections.append("required-summary-over-budget")
            item["summary_diagnostic"] = exc.diagnostic()
        # Re-read selected bytes after the scan; this is still no global atomic snapshot.
        try:
            if read_bytes(binding.record_path(reference(record))) != raw:
                protections.append("selected-record-drift")
        except (Fault, OSError):
            protections.append("selected-record-no-longer-readable")
        if not protections:
            item["disposition"] = "summary-available-original-retained" if mode == "compact" else "needs-owner-reconciliation"
        if mode in ("archive", "purge"):
            item["required_external_evidence"] = [
                "Actual cleanup owner decision for these exact source bytes and retention obligations",
                "External inbound-reference reconciliation; scoped scan is not proof of absence",
                "Explicit durable destination, exact-byte copy digest/read-back and compatible reader",
                "Recovery and resume/reference continuity; a linked successor alone is insufficient",
            ]
            if mode == "purge":
                item["would_lose"] = ["Complete authoritative workflow bytes/history and all sole retained observations",
                                      "Locators, dependency/decision provenance and any unresolved follow-up"]
    binding.check_paths()
    return {"mode": mode, "observed_at": now.isoformat(timespec="microseconds"), "scan": scan,
            "items": items, "execution": "preview-only; no mutation, scheduling or deletion permission"}


def render(binding, record):
    values = {**record["content"], "id": record["id"],
              "state": {"state": record["state"], "reason": record["state_reason"]},
              "retrospective": record["retrospective"], "history": record["history"], "storage_notice": NOTICE}
    def display(value):
        if isinstance(value, (dict, list)):
            return escape_markdown(encode(value).decode("utf-8").rstrip())
        return escape_markdown("None supplied" if value is None else str(value))
    return TOKEN.sub(lambda match: display(values[match[1]]), binding.template)


def execute(request):
    if type(request) is not dict or type(request.get("operation")) is not str:
        fail("request", "Request must name an operation.")
    operation = request["operation"]
    if operation not in OPERATIONS:
        fail("operation", "Unsupported operation.", "unsupported")
    required = {"explain": (), "create": ("content",), "inspect": ("reference",), "query": (),
                "checkpoint": ("reference", "expected_sha256", "content", "reason"),
                "transition": ("reference", "expected_sha256", "expected_state", "target_state", "reason"),
                "resume": ("reference",), "retrospect": ("reference", "expected_sha256", "retrospective"),
                "render": ("reference",), "retention-preview": ("mode", "selection")}[operation]
    extra = ("text",) if operation == "query" else (("extensions",) if operation == "create" else ())
    fields(request, ("operation", "project_root", "package_root", *required),
           ("project_config", "local_config", "overrides", "write_roots", *extra), "request")
    if not (3, 11) <= sys.version_info[:2] < (4, 0):
        fail("python-version", "Python >=3.11,<4 is required.", "unavailable")
    binding = Binding(request)
    if operation == "explain":
        return {"outcome": "succeeded", **binding.explain(), "config_version": 2, "namespace": PACKAGE}
    if operation == "query":
        return {"outcome": "succeeded", **query(binding, request.get("text", ""))}
    if operation == "retention-preview":
        return {"outcome": "succeeded", **retention_preview(binding, request)}
    if operation in ("create", "checkpoint", "transition", "retrospect"):
        return write_operation(binding, request)
    record, raw = inspect_record(binding, request["reference"])
    historical_candidates(record)
    result = {"outcome": "succeeded", "reference": reference(record), "sha256": digest(raw),
              "store_root": str(binding.store), "freshness": "historical-caller-reports"}
    if operation == "inspect":
        result["record"] = record
    elif operation == "resume":
        result["continuation"] = continuation(binding, record, raw)
    else:
        markdown = render(binding, record)
        body = markdown.encode("utf-8")
        if len(body) > LIMIT:
            fail("render-limit", "Rendered output exceeds the bound.", "unsupported")
        result.update(template_sha256=binding.template_sha256, body_sha256=digest(body),
                      view={"role": PACKAGE + ".view", "source": reference(record), "markdown": markdown})
    binding.check_paths()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
