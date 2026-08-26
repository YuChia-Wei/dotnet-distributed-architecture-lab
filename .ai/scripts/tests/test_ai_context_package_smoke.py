#!/usr/bin/env python3
"""Fast package smoke coverage kept separate from the release migration matrix."""

from __future__ import annotations

import unittest

from test_ai_context_packaging import PACKAGE, SyntheticPackageRepo


class AiContextPackageSmokeGwtTests(unittest.TestCase):
    def test_gwt_001_given_one_candidate_when_smoke_runs_then_archives_and_metadata_are_valid(self) -> None:
        fixture = SyntheticPackageRepo()
        try:
            result = fixture.build("smoke")

            # One build is sufficient for PR smoke: validate both archive
            # formats, their embedded checksums, and package metadata.
            zip_members = PACKAGE.validate_archive(result["zip"])
            tar_members = PACKAGE.validate_archive(result["tar_gz"])
            self.assertEqual(zip_members, tar_members)
            self.assertIn(f"{result['package_id']}/metadata/package.yaml", zip_members)
            self.assertIn(f"{result['package_id']}/metadata/migration.yaml", zip_members)
        finally:
            fixture.close()


if __name__ == "__main__":
    unittest.main()
