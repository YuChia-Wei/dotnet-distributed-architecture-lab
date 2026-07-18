#!/usr/bin/env python3
"""GWT tests for fail-closed active AI-context script references."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / ".ai/scripts/validate-ai-context.py"
SPEC = importlib.util.spec_from_file_location(
    "validate_ai_context_active_script_references", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ActiveScriptReferenceValidationTests(unittest.TestCase):
    def validate(
        self,
        rendered: str,
        *,
        source: Path = Path(
            ".ai/assets/skills/sample-validator/references/validation-command-templates.md"
        ),
        existing_scripts: tuple[str, ...] = (),
    ) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="ai-context-script-reference-") as temporary:
            root = Path(temporary)
            (root / source).parent.mkdir(parents=True)
            (root / source).write_text(rendered, encoding="utf-8")
            files = [source]
            for value in existing_scripts:
                script = Path(value)
                (root / script).parent.mkdir(parents=True, exist_ok=True)
                (root / script).write_text("#!/usr/bin/env bash\n", encoding="utf-8")
                files.append(script)

            errors: list[str] = []
            VALIDATOR.validate_active_script_references(files, errors, root=root)
            return errors

    def test_gwt_001_given_missing_active_script_when_validated_then_fails(self) -> None:
        errors = self.validate("./.ai/scripts/missing-command.sh <path>\n")

        self.assertTrue(any("active script reference does not exist" in error for error in errors))
        self.assertTrue(any(".ai/scripts/missing-command.sh" in error for error in errors))

    def test_gwt_002_given_existing_active_script_when_validated_then_passes(self) -> None:
        errors = self.validate(
            "./.ai/scripts/current-command.sh <path>\n",
            existing_scripts=(".ai/scripts/current-command.sh",),
        )

        self.assertEqual([], errors)

    def test_gwt_003_given_historical_workflow_reference_when_validated_then_ignored(self) -> None:
        errors = self.validate(
            "./.ai/scripts/removed-command.sh <path>\n",
            source=Path(".dev/workflows/legacy/report.md"),
        )

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
