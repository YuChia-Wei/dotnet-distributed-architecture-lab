#!/usr/bin/env python3
"""Compatibility entrypoint for the skill-owned acceptance validator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint

guard_direct_entrypoint(".ai/scripts/validate-software-development-orchestrator-acceptance.py")

TARGET = (
    Path(__file__).resolve().parents[1]
    / "assets/skills/software-development-orchestrator/scripts/"
    "validate-software-development-orchestrator-acceptance.py"
)
SPEC = importlib.util.spec_from_file_location(
    "software_development_orchestrator_acceptance", TARGET
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load canonical validator: {TARGET}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

for name in dir(MODULE):
    if not name.startswith("__"):
        globals()[name] = getattr(MODULE, name)


if __name__ == "__main__":
    raise SystemExit(MODULE.main())
