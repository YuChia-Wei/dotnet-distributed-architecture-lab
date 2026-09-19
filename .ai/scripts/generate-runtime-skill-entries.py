#!/usr/bin/env python3
"""Generate and verify canonical runtime execution entries for selected skills."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from python_prerequisites import guard_direct_entrypoint
from runtime_skill_entries import (
    SELECTED_SKILLS,
    check_entries,
    generated_entries,
    load_skill,
    parity_errors,
    render_entry,
    source_digest,
    source_path,
    wrapper_path,
)


guard_direct_entrypoint(".ai/scripts/generate-runtime-skill-entries.py")


def resolved_root(value: Path) -> Path:
    """Resolve a requested root without relying on a relative Path('.') default."""
    return value.resolve() if value.is_absolute() else (Path.cwd().resolve() / value).resolve()


def write_entries(root: Path) -> list[Path]:
    expected = generated_entries(root)
    changed: list[Path] = []
    for relative, rendered in expected.items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8", newline="\n")
            changed.append(relative)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd().resolve(), help="Absolute repository root to generate or check.")
    parser.add_argument("--check", action="store_true", help="Verify entries without writing.")
    arguments = parser.parse_args(argv)
    root = resolved_root(arguments.root)
    if not root.is_dir():
        print(f"Runtime skill entry generation failed: {root}: root is not a directory")
        return 1
    try:
        if arguments.check:
            errors = check_entries(root)
            if errors:
                print("Runtime skill entry parity failed:")
                for error in errors:
                    print(f"- {error}")
                return 1
            print(f"Runtime skill entry parity passed: {len(SELECTED_SKILLS)} canonical skills, 2 runtime targets each.")
            return 0
        changed = write_entries(root)
    except ValueError as exc:
        print(f"Runtime skill entry generation failed:\n- {exc}")
        return 1
    print(f"Runtime skill entries generated: {len(changed)} changed entries from {len(SELECTED_SKILLS)} canonical skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
