#!/bin/bash
# shellcheck shell=bash
#
# Canonical validation-profile registry for the source repository.  The
# aggregate runner owns execution; this file owns profile membership and the
# stable metadata that explains every selected check.

register_profile fast \
    local-development-feedback 30 report-and-warn
register_profile pr \
    pull-request-integration 90 report-and-warn
register_profile release \
    immutable-candidate-validation '' measure-first
register_profile closeout \
    post-publication-administrative-verification 120 report-and-warn
register_profile nightly-full \
    full-history-and-compatibility-regression '' measure-first

# id | owner | tags | profiles | input paths | dependencies |
# environment capabilities | timeout | resource class | cache policy |
# source/downstream disposition | command/callable | applicability
register_check assessment-artifacts \
    "Assessment Artifact Metadata" required \
    "governance,metadata" "fast pr release nightly-full" \
    ".dev/assessments" '' "python>=3.11" 30 cpu reuse-by-input \
    source "python .ai/scripts/validate-assessment-artifacts.py" always
register_check assessment-artifacts-tests \
    "Assessment Artifact Fail-Closed Tests" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/scripts/tests/test_assessment_artifacts.py .dev/assessments" assessment-artifacts \
    "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_assessment_artifacts.py -v" always
register_check workflow-artifacts \
    "Workflow Artifact Metadata" required \
    "governance,metadata" "fast pr release nightly-full" \
    ".dev/workflows" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/validate-workflow-artifacts.py" always
register_check workflow-implementation-contract \
    "Workflow Implementation Contract Fail-Closed Tests" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/assets/skills/software-development-orchestrator .dev/workflows" workflow-artifacts \
    "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/assets/skills/software-development-orchestrator/scripts/tests/test_workflow_implementation_contract.py -v" always
register_check workflow-lifecycle-contract \
    "Workflow Lifecycle Contract Fail-Closed Tests" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/scripts/tests/test_workflow_lifecycle_contract.py .dev/workflows" workflow-artifacts \
    "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_workflow_lifecycle_contract.py -v" always
register_check git-commit-policy \
    "Git Commit Policy Fail-Closed Tests" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/scripts/tests/test_git_commit_policy.py .dev/standards/GIT-COMMIT-POLICY.md" '' \
    "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_git_commit_policy.py -v" always
register_check workflow-handoff \
    "Workflow Handoff Fail-Closed Tests" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/scripts/tests/test_workflow_handoff.py .dev/workflows" workflow-artifacts \
    "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_workflow_handoff.py -v" always
register_check workflow-handoff-checkpoints \
    "Registered Workflow Handoff Checkpoints" required \
    "governance,metadata" "fast pr release nightly-full" \
    ".dev/workflows" workflow-artifacts "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/validate-workflow-handoff.py --all" always
register_check orchestrator-capability-contract \
    "Development Workflow Capability Contract" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/assets/skills/software-development-orchestrator" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/assets/skills/software-development-orchestrator/scripts/tests/test_software_development_orchestrator_capability_contract.py -v" always
register_check orchestrator-acceptance \
    "Development Workflow Deterministic Acceptance" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/assets/skills/software-development-orchestrator" orchestrator-capability-contract "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/assets/skills/software-development-orchestrator/scripts/tests/test_software_development_orchestrator_acceptance.py -v" always
register_check skill-script-colocation \
    "Canonical Skill Script Colocation Contract" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/assets/skills .ai/scripts" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_skill_script_colocation.py -v" always
register_check semantic-customization-lifecycle \
    "Semantic Customization Lifecycle" required \
    "governance,tests" "fast pr release nightly-full" \
    ".dev/ai-context .ai/assets/skills/ai-context-governance" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_semantic_customization_lifecycle.py -v" always
register_check semantic-customization-skill-contract \
    "Semantic Customization Skill Contract" required \
    "governance,tests" "fast pr release nightly-full" \
    ".ai/assets/skills/ai-context-governance .agents/skills" semantic-customization-lifecycle "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_semantic_customization_skill_contract.py -v" always
register_check selected-git-commits \
    "Selected Git Commit Messages" required \
    "governance,git" "pr release nightly-full" \
    ".git" workflow-artifacts "python>=3.11 git" 30 cpu no-reuse source \
    "python .ai/scripts/validate-git-commits.py --range COMMIT_RANGE" commit-range
register_check ai-context-navigation \
    "AI Context Navigation and Runtime Contracts" required \
    "context,navigation" "fast pr release nightly-full" \
    ".ai AGENTS.md CLAUDE.md" '' "python>=3.11" 600 cpu reuse-by-input portable \
    "python .ai/scripts/validate-ai-context.py" always
register_check ai-context-wrapper-metadata \
    "AI Context Wrapper Semantic Contract Fail-Closed Tests" required \
    "context,tests" "fast pr release nightly-full" \
    ".ai .agents .claude" ai-context-navigation "python>=3.11" 30 cpu reuse-by-input portable \
    "python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v" always
register_check ai-context-language-policy \
    "AI Context Language And Bilingual Parity Fail-Closed Tests" required \
    "context,tests" "fast pr release nightly-full" \
    ".ai AGENTS.md AGENTS.zh-TW.md" ai-context-navigation "python>=3.11" 30 cpu reuse-by-input portable \
    "python .ai/scripts/tests/test_ai_context_language_policy.py -v" always
register_check ai-context-source-include-evidence \
    "Source-Include Evidence Contract" required \
    "context,tests" "fast pr release nightly-full" \
    ".ai/distribution .ai/scripts/tests/test_ai_context_source_include_evidence.py" ai-context-navigation "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_ai_context_source_include_evidence.py -v" always
register_check governance-term-routing \
    "Governance Term Routing And Release Projection Contract" required \
    "governance,context,tests" "fast pr release nightly-full" \
    ".dev/standards/AI-CONTEXT-OWNERSHIP.yaml .dev/standards/AI-CONTEXT-SOURCE-RELEASE-POLICY.md .ai/assets/shared/governance/AI-CONTEXT-VERSION-POLICY.md .ai/distribution .ai/scripts/tests/test_governance_term_routing_contract.py" ai-context-navigation "python>=3.11 git" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_governance_term_routing_contract.py -v" source-release
register_check target-ai-context-version \
    "AI Context Target Apply, Provenance And Customization Contracts" required \
    "context,target" "fast pr release nightly-full" \
    ".dev/ai-context .dev/AI-CONTEXT-APPLY-PENDING.yaml" ai-context-navigation "python>=3.11" 30 cpu reuse-by-input portable \
    "python .ai/scripts/validate-ai-context-target.py" target-provenance
register_check source-ai-context-version \
    "AI Context Release And Version Contracts" required \
    "release,source" "release nightly-full" \
    ".dev/releases .ai/distribution" ai-context-navigation "python>=3.11 git" 60 cpu reuse-by-input source \
    "python .ai/scripts/validate-ai-context-versions.py" source-release
register_check package-apply \
    "AI Context Safe Apply GWT Tests" required \
    "package,tests" "pr release nightly-full" \
    ".ai/scripts/ai_context_package_apply.py .ai/scripts/tests/test_ai_context_package_apply.py" '' "python>=3.11 git" 90 io reuse-by-input portable \
    "python .ai/scripts/tests/test_ai_context_package_apply.py -v" always
register_check payload-user-view \
    "Selected Payload User-View Fail-Closed Contract" required \
    "package,navigation,components" "fast pr release nightly-full" \
    ".ai/scripts/ai_context_package.py .ai/scripts/tests/test_payload_user_view_contract.py .ai/distribution/profiles/dotnet-backend.yaml" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_payload_user_view_contract.py -v" source-release
register_check package-smoke \
    "AI Context Package Smoke Tests" required \
    "package,smoke" "pr release nightly-full" \
    ".ai/scripts/ai_context_package.py .ai/scripts/tests/test_ai_context_package_smoke.py .ai/distribution" package-apply "python>=3.11 git" 120 io reuse-by-fingerprint source \
    "python .ai/scripts/tests/test_ai_context_package_smoke.py -v" source-release
register_check dependency-versions \
    "Offline Dependency And Version Consistency" required \
    "dependency,metadata" "fast pr release nightly-full" \
    "requirements.txt .ai/distribution" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/validate-dependency-versions.py" always
register_check dependency-versions-tests \
    "Dependency And Version Consistency Fail-Closed Tests" required \
    "dependency,tests" "fast pr release nightly-full" \
    ".ai/scripts/tests/test_dependency_version_consistency.py requirements.txt" dependency-versions "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_dependency_version_consistency.py -v" always
register_check python-source-entrypoints \
    "Source-Only Python Entrypoint Prerequisite Contract" required \
    "runtime,tests" "pr release nightly-full" \
    ".ai/scripts requirements.txt" '' "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_python_source_entrypoints.py -v" always
register_check shell-assets \
    "Shell Asset Classification And Git Modes" required \
    "shell,metadata" "fast pr release nightly-full" \
    ".ai/scripts .ai/distribution/profiles" '' "python>=3.11 git" 30 cpu reuse-by-input portable \
    "python .ai/scripts/validate-shell-assets.py" always
register_check file-disposition-manifest \
    "File Disposition Manifest Fail-Closed Tests" required \
    "package,tests" "fast pr release nightly-full" \
    ".ai/distribution .ai/scripts/tests/test_file_disposition_manifest.py" shell-assets "python>=3.11 git" 60 io reuse-by-input source \
    "python .ai/scripts/tests/test_file_disposition_manifest.py -v" always
register_check aggregate-runner-contract \
    "Aggregate Runner And Shell Registry Fail-Closed Tests" required \
    "runner,tests" "release nightly-full" \
    ".ai/scripts/check-all.sh .ai/scripts/validation-profile-registry.sh .ai/scripts/tests/test_fail_closed_validation.py" shell-assets "python>=3.11 bash" 300 cpu no-reuse portable \
    "python .ai/scripts/tests/test_fail_closed_validation.py -v" always
register_check profile-registry-contract \
    "Validation Profile Registry Contract" required \
    "runner,registry,tests" "fast pr release nightly-full" \
    ".ai/scripts/validation-profile-registry.sh .ai/scripts/check-all.sh .ai/scripts/tests/test_validation_profile_registry.py" '' "python>=3.11 bash" 30 cpu reuse-by-input portable \
    "python .ai/scripts/tests/test_validation_profile_registry.py -v" always
register_check validation-evidence-contract \
    "Validation Execution Evidence Contract" required \
    "runner,evidence,tests" "fast pr release nightly-full" \
    ".ai/scripts/validation-evidence.py .ai/scripts/tests/test_validation_evidence.py .ai/scripts/check-all.sh" profile-registry-contract "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_validation_evidence.py -v" always
register_check immutable-history-validation-contract \
    "Immutable History Validation Contract" required \
    "governance,history,tests" "pr release nightly-full" \
    ".ai/scripts/validate-immutable-history.py .ai/scripts/tests/test_immutable_history_validation.py .ai/distribution/validation/immutable-history-validation.yaml .ai/distribution/IMMUTABLE-HISTORY-VALIDATION-CONTRACT.md" validation-evidence-contract "python>=3.11 git" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_immutable_history_validation.py -v" source-release
register_check coding-standards-integrity \
    "Coding Standards Integrity Claim Contract" required \
    "standards,tests" "fast pr release nightly-full" \
    ".dev/standards .ai/scripts/tests/test_coding_standards_integrity_contract.py" '' "python>=3.11" 30 cpu reuse-by-input portable \
    "python .ai/scripts/tests/test_coding_standards_integrity_contract.py -v" always
register_check code-review-routing-contract \
    "Code Reviewer Routing Contract" required \
    "context,review,tests" "fast pr release nightly-full" \
    ".ai/assets/skills/code-reviewer .ai/assets/sub-agent-role-prompts .ai/assets/tech-stacks/dotnet-backend .ai/scripts/tests/test_code_reviewer_routing_contract.py" coding-standards-integrity "python>=3.11" 60 cpu reuse-by-input portable \
    "python .ai/scripts/tests/test_code_reviewer_routing_contract.py -v" always
register_check profile-projection \
    "Profile Projection Contract" required \
    "package,tests" "fast pr release nightly-full" \
    ".ai/distribution/profiles .ai/scripts/tests/test_profile_projection_contract.py" '' "python>=3.11 git" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_profile_projection_contract.py -v" always
register_check document-projection \
    "Documentation Projection Contract" required \
    "context,tests" "fast pr release nightly-full" \
    ".ai/distribution .dev .ai/scripts/tests/test_document_projection_contract.py" '' "python>=3.11" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_document_projection_contract.py -v" always
register_check coding-standards-structural \
    "Coding Standards Structural Integrity" required \
    "standards,shell" "fast pr release nightly-full" \
    ".dev/standards .ai/scripts/check-coding-standards.sh" coding-standards-integrity "bash" 30 cpu reuse-by-input portable \
    "check-coding-standards.sh" always
register_check spec-implementation \
    "Spec Implementation Compliance (.NET)" required \
    "spec,optional" "pr release nightly-full" \
    ".dev/specs .ai/scripts/check-spec-compliance.sh" '' "python>=3.11 bash" 60 cpu no-reuse portable \
    "check-spec-compliance.sh SPEC_FILE TASK_NAME" spec-inputs
register_check sdk-free-framework-contract \
    "SDK-Free Framework Contract" required \
    "portability,release" "fast pr release nightly-full" \
    ".ai/scripts/tests/test_sdk_free_framework_contract.py .ai/assets/tech-stacks/dotnet-backend/tooling/on-demand-mechanical-validation .github/workflows/portable-gates.yml" '' "python>=3.11 git" 30 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_sdk_free_framework_contract.py -v" source-release
register_check source-version-governance-tests \
    "AI Context Version Governance Fail-Closed Tests" required \
    "release,tests" "release nightly-full" \
    ".ai/scripts/tests/test_ai_context_version_governance.py .dev/releases" source-ai-context-version "python>=3.11 git" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_ai_context_version_governance.py -v" source-release
register_check package-full-matrix \
    "AI Context Packaging GWT Tests" required \
    "package,full-matrix" "release nightly-full" \
    ".ai/scripts/ai_context_package.py .ai/scripts/tests/test_ai_context_packaging.py .ai/distribution" source-ai-context-version "python>=3.11 git" 900 io reuse-by-fingerprint source \
    "python .ai/scripts/tests/test_ai_context_packaging.py -v" source-release
register_check release-state-tests \
    "AI Context Release State Fail-Closed Tests" required \
    "release,tests" "release nightly-full" \
    ".ai/scripts/tests/test_ai_context_release_state.py .dev/releases" source-ai-context-version "python>=3.11 git" 90 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_ai_context_release_state.py -v" source-release
register_check release-preparation-tests \
    "AI Context Release Preparation Fail-Closed Tests" required \
    "release,tests" "release nightly-full" \
    ".ai/scripts/tests/test_prepare_ai_context_release.py .dev/releases" source-ai-context-version "python>=3.11 git" 90 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_prepare_ai_context_release.py -v" source-release
register_check release-notes-renderer \
    "AI Context Release Renderer Fail-Closed Tests" required \
    "release,tests" "release nightly-full" \
    ".ai/scripts/tests/test_release_notes_renderer.py .dev/releases" source-ai-context-version "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_release_notes_renderer.py -v" source-release
register_check ai-behavior-evaluation \
    "AI Behavior Deterministic Evaluation" required \
    "evaluation,release" "release nightly-full" \
    ".ai/scripts/tests/test_ai_behavior_evaluation.py .ai" source-ai-context-version "python>=3.11" 90 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_ai_behavior_evaluation.py -v" source-release
register_check ai-context-load-measurement \
    "AI Context Load Measurement Contract" required \
    "evaluation,release" "release nightly-full" \
    ".ai/scripts/tests/test_ai_context_load_measurement.py .ai" source-ai-context-version "python>=3.11" 90 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_ai_context_load_measurement.py -v" source-release
register_check repository-config-contract \
    "Repository Configuration Ownership Contract" required \
    "configuration,release" "release nightly-full" \
    ".dev/project-config.yaml .ai/scripts/validate-repository-config-contract.py" source-ai-context-version "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/validate-repository-config-contract.py" source-release
register_check repository-config-contract-tests \
    "Repository Configuration Ownership Fail-Closed Tests" required \
    "configuration,release" "release nightly-full" \
    ".ai/scripts/tests/test_repository_config_contract.py .dev/project-config.yaml" repository-config-contract "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_repository_config_contract.py -v" source-release
register_check skill-transition \
    "Skill Transition Compatibility Contract" required \
    "skill,release" "release nightly-full" \
    ".ai/scripts/validate-skill-transition.py .ai/assets/skills" source-ai-context-version "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/validate-skill-transition.py" source-release
register_check skill-transition-tests \
    "Skill Transition Compatibility Fail-Closed Tests" required \
    "skill,release" "release nightly-full" \
    ".ai/scripts/tests/test_skill_transition_contract.py .ai/assets/skills" skill-transition "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_skill_transition_contract.py -v" source-release
register_check effective-rules \
    "Effective Rule Packet Resolution and Consumer Parity Tests" required \
    "rules,release" "release nightly-full" \
    ".ai/scripts/tests/test_ai_context_effective_rules.py .ai" source-ai-context-version "python>=3.11" 90 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_ai_context_effective_rules.py -v" source-release
register_check effective-rule-action-skill \
    "Effective Rule Action Skill Consumption Contract" required \
    "rules,release" "release nightly-full" \
    ".ai/scripts/tests/test_effective_rule_action_skill_contract.py .ai" effective-rules "python>=3.11" 90 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_effective_rule_action_skill_contract.py -v" source-release
register_check source-governance-manifest \
    "Source Governance Manifest Registry" required \
    "governance,source" "fast pr release nightly-full" \
    ".ai/distribution/governance-checks.yaml .ai/distribution/repository-identity-policy.yaml .ai/scripts/validate-source-governance.py .ai/scripts/validate-repository-identity.py" '' "python>=3.11 git" 60 cpu reuse-by-input source \
    "python .ai/scripts/validate-source-governance.py" source-governance
register_check repository-identity-tests \
    "Repository Identity Drift Fail-Closed Tests" required \
    "governance,source,tests" "fast pr release nightly-full" \
    ".ai/distribution/repository-identity-policy.yaml .ai/scripts/validate-repository-identity.py .ai/scripts/tests/test_repository_identity.py" source-governance-manifest "python>=3.11 git" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_repository_identity.py -v" source-governance
register_check governance-workflow-contract \
    "Governance Pull-Request Workflow Contract" required \
    "governance,source" "pr release nightly-full" \
    ".github/workflows/governance.yml .ai/scripts/tests/test_governance_workflow_contract.py" repository-identity-tests "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_governance_workflow_contract.py -v" source-governance
register_check github-workflow-contract \
    "GitHub Workflow Lifecycle Contract" required \
    "governance,source" "pr release nightly-full" \
    ".github/workflows .ai/scripts/tests/test_github_workflow_contract.py" source-governance-manifest "python>=3.11" 60 cpu reuse-by-input source \
    "python .ai/scripts/tests/test_github_workflow_contract.py -v" source-governance
register_check source-release-closeout-contract \
    "Source-Only Release Closeout Contract" required \
    "release,closeout" "closeout" \
    ".ai/assets/skills/ai-context-release-closeout .agents/skills/ai-context-release-closeout .claude/skills/ai-context-release-closeout .ai/scripts/ai_context_release_closeout.py .ai/scripts/tests/test_ai_context_release_closeout.py" '' "python>=3.11 git" 120 io no-reuse source \
    "python .ai/scripts/tests/test_ai_context_release_closeout.py -v" always
register_check test-di-compliance \
    "Test DI Compliance" advisory \
    "deferred,nightly" "nightly-full" \
    ".ai/scripts/check-test-di-compliance.sh" '' "bash" 0 cpu no-reuse portable \
    "check-test-di-compliance.sh" deferred
register_check template-synchronization \
    "Template Synchronization" advisory \
    "deferred,nightly" "nightly-full" \
    ".ai/scripts/check-template-sync.sh" '' "bash" 0 cpu no-reuse portable \
    "check-template-sync.sh" deferred
register_check adr-index-update \
    "ADR Index Update" advisory \
    "deferred,nightly" "nightly-full" \
    ".ai/scripts/update-adr-index.sh" '' "bash" 0 cpu no-reuse portable \
    "update-adr-index.sh" deferred
