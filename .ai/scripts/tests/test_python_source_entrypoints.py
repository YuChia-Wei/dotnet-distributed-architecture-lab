#!/usr/bin/env python3
"""Contract tests for source-only Python entrypoint prerequisite behavior."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / ".ai/scripts/python-entrypoints.json"
STDLIB_COMPARE = ".ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py"
MARKER = ROOT / ".ai/scripts/tests/.python-source-entrypoints-marker"
RUNNER_LOG_DIRECTORY = os.environ.get("AI_CONTEXT_VALIDATION_RUN_LOG_DIR")
ACTIVE_RUNNER_LOG_DIRECTORY = (
    Path(RUNNER_LOG_DIRECTORY).resolve() if RUNNER_LOG_DIRECTORY else None
)
PROTECTED_ROOTS = (
    ROOT / ".dev/releases/v0.8.0",
    ROOT / "dist",
    ROOT / "artifacts",
    MARKER,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_active_runner_diagnostic(path: Path) -> bool:
    """Exclude only the aggregate runner's own retained diagnostic files."""
    if ACTIVE_RUNNER_LOG_DIRECTORY is None:
        return False
    try:
        path.resolve().relative_to(ACTIVE_RUNNER_LOG_DIRECTORY)
    except ValueError:
        return False
    return True


def protected_snapshot() -> dict[str, str]:
    """Capture artifacts a blocked preflight must never create or change."""
    snapshot: dict[str, str] = {}
    for root in PROTECTED_ROOTS:
        if root.is_file():
            snapshot[root.relative_to(ROOT).as_posix()] = digest(root)
        elif root.is_dir():
            for path in sorted(item for item in root.rglob("*") if item.is_file()):
                if is_active_runner_diagnostic(path):
                    continue
                snapshot[path.relative_to(ROOT).as_posix()] = digest(path)
    for directory, directories, files in os.walk(ROOT):
        directories[:] = [name for name in directories if name != ".git"]
        if Path(directory).name != "__pycache__":
            continue
        for name in sorted(files):
            path = Path(directory) / name
            snapshot[path.relative_to(ROOT).as_posix()] = digest(path)
    return snapshot


class PythonSourceEntrypointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.source_only = [item for item in registry["entrypoints"] if not item["portable"]]
        cls.pyyaml_source_only = [item for item in cls.source_only if item["dependency_profile"] == ["PyYAML"]]
        cls.stdlib_source_only = [item for item in cls.source_only if not item["dependency_profile"]]

    def test_gwt_001_given_source_only_registry_when_help_is_requested_then_all_eighteen_direct_clis_remain_callable(self) -> None:
        self.assertEqual(18, len(self.source_only))
        for item in self.source_only:
            with self.subTest(entrypoint=item["path"]):
                result = subprocess.run(
                    [sys.executable, str(ROOT / item["path"]), "--help"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_gwt_002_given_shadowed_yaml_when_source_only_pyyaml_clis_run_then_each_blocks_before_target_body_or_writes(self) -> None:
        self.assertEqual(17, len(self.pyyaml_source_only))
        before = protected_snapshot()
        with tempfile.TemporaryDirectory(prefix="python-source-entrypoints-") as temporary:
            shadow = Path(temporary) / "yaml.py"
            shadow.write_text("raise ImportError('deterministic shadowed yaml')\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(Path(temporary))
            environment.pop("AI_CONTEXT_PYTHON", None)
            for item in self.pyyaml_source_only:
                with self.subTest(entrypoint=item["path"]):
                    result = subprocess.run(
                        [sys.executable, str(ROOT / item["path"]), "--diagnostic-format=json"],
                        cwd=ROOT,
                        env=environment,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(item["prerequisite_exit_code"], result.returncode, result.stdout + result.stderr)
                    self.assertEqual("", result.stderr)
                    lines = result.stdout.splitlines()
                    self.assertEqual(1, len(lines), result.stdout)
                    diagnostic = json.loads(lines[0])
                    self.assertEqual("blocked-by-environment", diagnostic["outcome"])
                    self.assertEqual("missing-dependency", diagnostic["reason_code"])
                    self.assertEqual(item["path"], diagnostic["entrypoint"])
                    self.assertEqual(["PyYAML==6.0.3"], diagnostic["missing_requirements"])
                    self.assertFalse(diagnostic["mutation_started"])
        self.assertEqual(before, protected_snapshot())

    def test_gwt_003_given_source_only_registry_when_stdlib_entry_is_selected_then_compare_has_an_empty_dependency_profile(self) -> None:
        self.assertEqual(1, len(self.stdlib_source_only))
        self.assertEqual(STDLIB_COMPARE, self.stdlib_source_only[0]["path"])
        self.assertEqual([], self.stdlib_source_only[0]["dependency_profile"])


if __name__ == "__main__":
    unittest.main()
