#!/bin/bash

# ====================================================================
# Comprehensive Project Check Script (.NET)
# 
# Purpose: 執行所有專案檢查腳本，提供完整的專案健康報告
# Usage: ./check-all.sh [--quick | --full | --critical]
# ====================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Parse arguments strictly so a typo cannot silently select the full gate.
MODE="full"
if [ "$#" -gt 1 ]; then
    echo "Usage: $0 [--quick | --full | --critical]" >&2
    exit 2
elif [ "$#" -eq 1 ] && { [ "$1" == "--help" ] || [ "$1" == "-h" ]; }; then
    echo "Usage: $0 [--quick | --full | --critical]"
    echo ""
    echo "Modes:"
    echo "  --quick    : Only run fast, critical checks"
    echo "  --critical : Only run the most important checks"
    echo "  --full     : Run all available checks (default)"
    echo ""
    exit 0
elif [ "$#" -eq 1 ]; then
    case "$1" in
        --quick) MODE="quick" ;;
        --critical) MODE="critical" ;;
        --full) MODE="full" ;;
        *)
            echo "Unknown argument: $1" >&2
            echo "Usage: $0 [--quick | --full | --critical]" >&2
            exit 2
            ;;
    esac
fi

# Track results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0
WARNINGS=0
REQUIRED_SELECTED=0
REQUIRED_RUN=0
REQUIRED_FAILED=0
ADVISORY_SELECTED=0
DEFERRED_CHECKS=0
NOT_APPLICABLE=0

select_check() {
    local description=$1
    local is_critical=$2
    local is_quick=$3
    if [ "$MODE" == "critical" ] && [ "$is_critical" != "true" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping by mode: $description (non-critical)"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        return 1
    fi
    if [ "$MODE" == "quick" ] && [ "$is_quick" != "true" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping by mode: $description (not quick)"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        return 1
    fi
    return 0
}

record_selected() {
    local enforcement=$1
    if [ "$enforcement" != "required" ] && [ "$enforcement" != "advisory" ]; then
        echo "Internal error: unsupported enforcement class '$enforcement'" >&2
        exit 2
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ "$enforcement" == "required" ]; then
        REQUIRED_SELECTED=$((REQUIRED_SELECTED + 1))
    else
        ADVISORY_SELECTED=$((ADVISORY_SELECTED + 1))
    fi
}

record_unavailable_or_failed() {
    local enforcement=$1
    local description=$2
    if [ "$enforcement" == "required" ]; then
        echo -e "${RED}✗ FAILED${NC}: $description"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    else
        echo -e "${YELLOW}⚠ ADVISORY${NC}: $description"
        WARNINGS=$((WARNINGS + 1))
    fi
}

# Function to run a check script
run_check() {
    local script_name=$1
    local description=$2
    local enforcement=$3
    local is_critical=$4
    local is_quick=$5
    shift 5
    local args=("$@")
    select_check "$description" "$is_critical" "$is_quick" || return
    record_selected "$enforcement"
    
    echo ""
    echo -e "${CYAN}▶ Running:${NC} $description"
    echo "  Script: $script_name"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -f "$SCRIPT_DIR/$script_name" ]; then
        if [ -x "$SCRIPT_DIR/$script_name" ]; then
            [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
            if "$SCRIPT_DIR/$script_name" "${args[@]}" 2>&1; then
                echo -e "${GREEN}✓ PASSED${NC}: $description"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                record_unavailable_or_failed "$enforcement" "$description returned non-zero"
            fi
        else
            record_unavailable_or_failed "$enforcement" "$script_name is not executable"
        fi
    else
        record_unavailable_or_failed "$enforcement" "$script_name not found"
    fi
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

run_command_check() {
    local command_text=$1
    local description=$2
    local enforcement=$3
    local is_critical=$4
    local is_quick=$5
    select_check "$description" "$is_critical" "$is_quick" || return
    record_selected "$enforcement"
    [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))

    echo ""
    echo -e "${CYAN}▶ Running:${NC} $description"
    echo "  Command: $command_text"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if (cd "$PROJECT_ROOT" && eval "$command_text"); then
        echo -e "${GREEN}✓ PASSED${NC}: $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        record_unavailable_or_failed "$enforcement" "$description returned non-zero"
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to mark a check as pending dotnet-native replacement
run_deferred_check() {
    local script_name=$1
    local description=$2
    local is_critical=$3
    local is_quick=$4
    local reason=${5:-"dotnet-native replacement pending"}

    select_check "$description" "$is_critical" "$is_quick" || return
    echo -e "${YELLOW}⊖${NC} DEFERRED: $description ($reason)"
    DEFERRED_CHECKS=$((DEFERRED_CHECKS + 1))
}

run_spec_compliance_check() {
    local spec_file="${SPEC_FILE:-}"
    local task_name="${TASK_NAME:-}"

    if [ -z "$spec_file" ] && [ -z "$task_name" ]; then
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Spec Implementation Compliance (SPEC_FILE/TASK_NAME not set)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
        return
    fi
    if [ -z "$spec_file" ] || [ -z "$task_name" ]; then
        echo -e "${RED}✗ FAILED${NC}: Spec Implementation Compliance requires both SPEC_FILE and TASK_NAME"
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_SELECTED=$((REQUIRED_SELECTED + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
        return
    fi

    run_check "check-spec-compliance.sh" \
        "Spec Implementation Compliance (.NET)" \
        "required" "false" "true" "$spec_file" "$task_name"
}

# Header
echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║    Comprehensive Project Check         ║${NC}"
echo -e "${MAGENTA}║    Mode: ${YELLOW}$MODE${MAGENTA}                          ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Starting checks at $(date '+%Y-%m-%d %H:%M:%S')${NC}"

# ====================================================================
# Critical Checks (always run in quick and critical modes)
# ====================================================================

echo ""
echo -e "${MAGENTA}════ Critical Checks ════${NC}"

run_command_check "python .ai/scripts/validate-workflow-artifacts.py" \
    "Workflow Artifact Metadata" \
    "required" "true" "true"

run_command_check "python .ai/scripts/validate-ai-context.py" \
    "AI Context Navigation and Runtime Contracts" \
    "required" "true" "true"

run_command_check "python .ai/scripts/validate-shell-assets.py" \
    "Shell Asset Classification And Git Modes" \
    "required" "true" "true"

# Coding standards are fundamental for AI context and standards docs
run_check "check-coding-standards.sh" \
    "Coding Standards Compliance" \
    "required" "true" "true"

run_command_check "dotnet test tools/DotnetBackendAnalyzers.Tests/DotnetBackendAnalyzers.Tests.csproj" \
    "Dotnet Backend Analyzer Self Tests" \
    "required" "true" "true"

run_command_check "dotnet test tools/DotnetBackendValidation.Tests/DotnetBackendValidation.Tests.csproj" \
    "Dotnet Backend Runtime Validation Self Tests" \
    "required" "true" "true"

run_command_check "dotnet build MQArchLab.slnx --no-restore" \
    "Analyzer-Enabled Product Build" \
    "required" "true" "true"

# Analyzer self-tests verify rule behavior. The product build above proves the
# source-included analyzers execute against this repository's production code.

# ====================================================================
# Important Checks (run in full and quick modes)
# ====================================================================

if [ "$MODE" != "critical" ]; then
    echo ""
    echo -e "${MAGENTA}════ Important Checks ════${NC}"
    
    # Aggregate and UseCase source validation is covered by the analyzer-enabled product build.
    
    # Controller compliance is covered by the analyzer-enabled product build.

    # Projection source is covered by the analyzer-enabled product build. EF model
    # registration validation remains tool-only until this Dapper target has an EF projection model.
    
    # Spec compliance is important
    run_spec_compliance_check
    
    # Dependencies check (dotnet-native replacement not yet available)
    run_deferred_check "check-dependencies.sh" \
        "Dependencies and Versions" \
        "false" "true" "dotnet-native replacement not yet available"
fi

# ====================================================================
# Additional Checks (only in full mode)
# ====================================================================

if [ "$MODE" == "full" ]; then
    echo ""
    echo -e "${MAGENTA}════ Additional Checks ════${NC}"
    
    # Test compliance
    run_check "check-test-compliance.sh" \
        "Test Standards Compliance" \
        "advisory" "false" "false"
    
    # Test DI compliance helper remains transitional
    run_deferred_check "check-test-di-compliance.sh" \
        "Test DI Compliance" \
        "true" "false" "replace with analyzer or test architecture rules"
    
    # Template sync check (dotnet-native replacement not yet available)
    run_deferred_check "check-template-sync.sh" \
        "Template Synchronization" \
        "false" "false" "dotnet-native replacement not yet available"
    
    # ADR index update (dotnet-native replacement not yet available)
    run_deferred_check "update-adr-index.sh" \
        "ADR Index Update" \
        "false" "false" "dotnet-native replacement not yet available"
    
    # Add ADR script (if needed)
    if [ -f "$SCRIPT_DIR/add-adr.sh" ]; then
        echo -e "${CYAN}ℹ${NC} add-adr.sh is available for creating new ADRs"
    fi
fi

# ====================================================================
# Results Summary
# ====================================================================

echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║           Check Results Summary        ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo ""

# Calculate statistics
if [ $TOTAL_CHECKS -gt 0 ]; then
    PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
else
    PASS_RATE=0
fi

# Display results with colors
echo -e "Total Checks Run: ${CYAN}$TOTAL_CHECKS${NC}"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
echo -e "Skipped By Mode: ${YELLOW}$SKIPPED_CHECKS${NC}"
echo -e "Advisory Warnings: ${YELLOW}$WARNINGS${NC}"
echo -e "Deferred: ${YELLOW}$DEFERRED_CHECKS${NC}"
echo -e "Not Applicable: ${CYAN}$NOT_APPLICABLE${NC}"
echo -e "Required Selected: ${CYAN}$REQUIRED_SELECTED${NC}"
echo -e "Required Executed: ${CYAN}$REQUIRED_RUN${NC}"
echo -e "Required Failed: ${RED}$REQUIRED_FAILED${NC}"
echo -e "Advisory Selected: ${CYAN}$ADVISORY_SELECTED${NC}"
echo -e "Pass Rate: ${CYAN}${PASS_RATE}%${NC}"

echo ""
echo -e "${BLUE}Completed at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""

# Overall status
if [ $FAILED_CHECKS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║    ✓ All Checks Passed Successfully!   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    exit 0
elif [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠ Passed with $WARNINGS Advisory Warning(s) ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║    ✗ $FAILED_CHECKS Check(s) Failed!              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    
    # Provide helpful next steps
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Review the failed checks above"
    echo "2. Run individual scripts for detailed errors"
    echo "3. Fix the issues and run this check again"
    echo ""
    
    exit 1
fi
