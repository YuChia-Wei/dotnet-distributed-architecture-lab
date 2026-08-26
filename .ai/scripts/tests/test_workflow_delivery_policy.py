#!/usr/bin/env python3
"""GWT contract tests for workflow value, delivery cohesion, and Git topology."""

from __future__ import annotations

import unittest
from pathlib import Path
import re

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_POLICY = REPO_ROOT / ".dev/standards/WORKFLOW-GATE-POLICY.md"
TEAM_POLICY = REPO_ROOT / ".dev/TEAM-GIT-FLOW-RULES.MD"
PORTABLE_WORKFLOW_POLICY = (
    REPO_ROOT / ".ai/assets/shared/governance/WORKFLOW-GATE-POLICY.md"
)
PORTABLE_TEAM_POLICY = (
    REPO_ROOT / ".ai/assets/shared/governance/TEAM-GIT-FLOW-RULES.MD"
)
ORCHESTRATOR_SPEC = (
    REPO_ROOT / ".ai/assets/skills/software-development-orchestrator/skill.yaml"
)
GOVERNANCE_SPEC = REPO_ROOT / ".ai/assets/skills/ai-context-governance/skill.yaml"
AUDITOR_SPEC = REPO_ROOT / ".ai/assets/skills/ai-context-auditor/skill.yaml"


def normalized(text: str) -> str:
    """Collapse Markdown line wrapping while preserving semantic wording."""
    return re.sub(r"\s+", " ", text).strip()


class WorkflowDeliveryPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_policy = WORKFLOW_POLICY.read_text(encoding="utf-8")
        cls.team_policy = TEAM_POLICY.read_text(encoding="utf-8")
        cls.portable_workflow_policy = PORTABLE_WORKFLOW_POLICY.read_text(
            encoding="utf-8"
        )
        cls.portable_team_policy = PORTABLE_TEAM_POLICY.read_text(encoding="utf-8")
        cls.orchestrator = yaml.safe_load(ORCHESTRATOR_SPEC.read_text(encoding="utf-8"))
        cls.governance = yaml.safe_load(GOVERNANCE_SPEC.read_text(encoding="utf-8"))
        cls.auditor = yaml.safe_load(AUDITOR_SPEC.read_text(encoding="utf-8"))

    def test_gwt_001_given_mode_selection_when_read_then_four_decisions_are_independent(self) -> None:
        for decision in (
            "Execution record",
            "Delivery grouping",
            "Integration gate",
            "Git topology",
        ):
            with self.subTest(decision=decision):
                self.assertIn(decision, self.workflow_policy)
        self.assertIn(
            "Workflow mode does not imply one workflow per Issue",
            self.workflow_policy,
        )
        self.assertIn(
            "a pull request does not imply a merge commit",
            normalized(self.portable_workflow_policy),
        )

    def test_gwt_002_given_fewer_than_three_tasks_when_evaluated_then_value_is_required_without_padding(self) -> None:
        for policy in (self.workflow_policy, self.portable_workflow_policy):
            with self.subTest(policy=policy[:32]):
                self.assertIn("fewer than three substantive tasks", policy)
                self.assertIn("Do not invent tasks", policy)
                self.assertIn("generic validation", policy.lower())
        orchestrator_constraints = "\n".join(self.orchestrator["constraints"])
        self.assertIn("workflow-value review signal", orchestrator_constraints)
        self.assertIn("never as a reason to invent", orchestrator_constraints)

    def test_gwt_003_given_multiple_issues_when_delivery_boundaries_match_then_one_delivery_is_allowed(self) -> None:
        expected_dimensions = (
            "outcome",
            "branch",
            "validation",
            "approval",
            "release",
            "rollback",
        )
        for dimension in expected_dimensions:
            with self.subTest(dimension=dimension):
                self.assertIn(dimension, self.workflow_policy.lower())
                self.assertIn(dimension, self.portable_workflow_policy.lower())
        self.assertIn(
            "Issue count is traceability input, not delivery cardinality",
            self.workflow_policy,
        )
        self.assertIn(
            "one workflow or direct delivery and one integration path",
            self.portable_workflow_policy,
        )

    def test_gwt_004_given_repository_integration_when_selected_then_linear_and_merge_are_normal_paths(self) -> None:
        self.assertIn("### Linear Integration", self.team_policy)
        self.assertIn("### Merge-Commit Integration", self.team_policy)
        self.assertIn("GitHub **Rebase and merge**", self.team_policy)
        self.assertIn("git merge --ff-only <branch>", self.team_policy)
        self.assertIn("merge commit (`--no-ff`", self.team_policy)
        self.assertIn("Choose linear integration", self.portable_team_policy)
        self.assertIn("Choose a merge commit", self.portable_team_policy)
        self.assertNotIn("Fast-forward merge is acceptable only", self.team_policy)

    def test_gwt_005_given_readme_history_update_when_classified_then_pr_review_and_linear_topology_are_preserved(self) -> None:
        self.assertIn(
            "Correct historical README wording with no normative, generated, release, security, or migration truth change",
            self.workflow_policy,
        )
        self.assertIn(
            "A historical README-only update normally uses direct mode, a pull request, and linear integration",
            normalized(self.team_policy),
        )
        self.assertIn(
            "The local fast-forward path is not permission to push unreviewed work directly",
            self.team_policy,
        )

    def test_gwt_006_given_skill_routing_when_loaded_then_topology_is_not_derived_from_mode(self) -> None:
        for spec in (self.orchestrator, self.governance, self.auditor):
            constraints = "\n".join(spec["constraints"])
            with self.subTest(skill=spec["asset_id"]):
                self.assertIn("select linear or merge-commit topology", constraints)
                self.assertNotIn("use --no-ff for merges unless", constraints)


if __name__ == "__main__":
    unittest.main()
