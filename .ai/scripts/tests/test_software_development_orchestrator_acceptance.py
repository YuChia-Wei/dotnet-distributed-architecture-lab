#!/usr/bin/env python3
"""Compatibility entrypoint for the skill-owned acceptance test suite."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


TARGET = (
    Path(__file__).resolve().parents[2]
    / "assets/skills/software-development-orchestrator/scripts/tests/"
    "test_software_development_orchestrator_acceptance.py"
)
SPEC = importlib.util.spec_from_file_location(
    "software_development_orchestrator_acceptance_tests", TARGET
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load canonical tests: {TARGET}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

for name in dir(MODULE):
    if not name.startswith("__"):
        globals()[name] = getattr(MODULE, name)


if __name__ == "__main__":
    unittest.main(module=MODULE)
