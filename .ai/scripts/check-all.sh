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

# Parse arguments
MODE="full"
if [ "$1" == "--quick" ]; then
    MODE="quick"
elif [ "$1" == "--critical" ]; then
    MODE="critical"
elif [ "$1" == "--full" ]; then
    MODE="full"
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [--quick | --full | --critical]"
    echo ""
    echo "Modes:"
    echo "  --quick    : Only run fast, critical checks"
    echo "  --critical : Only run the most important checks"
    echo "  --full     : Run all available checks (default)"
    echo ""
    exit 0
fi

# Track results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0
WARNINGS=0

# Function to run a check script
run_check() {
    local script_name=$1
    local description=$2
    local is_critical=$3
    local is_quick=$4
    shift 4
    local args=("$@")
    
    # Skip logic based on mode
    if [ "$MODE" == "critical" ] && [ "$is_critical" != "true" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping: $description (non-critical)"
        ((SKIPPED_CHECKS++))
        return
    fi
    
    if [ "$MODE" == "quick" ] && [ "$is_quick" != "true" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping: $description (not quick)"
        ((SKIPPED_CHECKS++))
        return
    fi
    
    ((TOTAL_CHECKS++))
    
    echo ""
    echo -e "${CYAN}▶ Running:${NC} $description"
    echo "  Script: $script_name"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -f "$SCRIPT_DIR/$script_name" ]; then
        if [ -x "$SCRIPT_DIR/$script_name" ]; then
            # Run the script and capture exit code
            if "$SCRIPT_DIR/$script_name" "${args[@]}" 2>&1; then
                echo -e "${GREEN}✓ PASSED${NC}: $description"
                ((PASSED_CHECKS++))
            else
                echo -e "${RED}✗ FAILED${NC}: $description"
                ((FAILED_CHECKS++))
            fi
        else
            echo -e "${YELLOW}⚠ WARNING${NC}: $script_name is not executable"
            echo "  Run: chmod +x $SCRIPT_DIR/$script_name"
            ((WARNINGS++))
        fi
    else
        echo -e "${RED}✗ ERROR${NC}: $script_name not found"
        ((FAILED_CHECKS++))
    fi
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to mark a check as pending .NET translation
run_check_pending() {
    local script_name=$1
    local description=$2
    local is_critical=$3
    local is_quick=$4
    local reason=${5:-".NET translation pending"}

    # Skip logic based on mode
    if [ "$MODE" == "critical" ] && [ "$is_critical" != "true" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping: $description (non-critical)"
        ((SKIPPED_CHECKS++))
        return
    fi

    if [ "$MODE" == "quick" ] && [ "$is_quick" != "true" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping: $description (not quick)"
        ((SKIPPED_CHECKS++))
        return
    fi

    echo -e "${YELLOW}⊖${NC} TODO: $description ($reason)"
    ((SKIPPED_CHECKS++))
}

run_spec_compliance_check() {
    local spec_file="${SPEC_FILE:-}"
    local task_name="${TASK_NAME:-}"

    if [ -z "$spec_file" ] || [ -z "$task_name" ]; then
        echo -e "${YELLOW}⊖${NC} Skipping: Spec Implementation Compliance (SPEC_FILE/TASK_NAME not set)"
        ((SKIPPED_CHECKS++))
        return
    fi

    run_check "check-spec-compliance.sh" \
        "Spec Implementation Compliance (.NET)" \
        "false" "true" "$spec_file" "$task_name"
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

# Coding standards are fundamental
run_check "check-coding-standards.sh" \
    "Coding Standards Compliance" \
    "true" "true"

# Repository pattern compliance is critical
run_check "check-repository-compliance.sh" \
    "Repository Pattern Compliance" \
    "true" "true"

# Mapper compliance is critical
run_check "check-mapper-compliance.sh" \
    "Mapper Design Compliance" \
    "true" "true"

# ====================================================================
# Important Checks (run in full and quick modes)
# ====================================================================

if [ "$MODE" != "critical" ]; then
    echo ""
    echo -e "${MAGENTA}════ Important Checks ════${NC}"
    
    # Aggregate compliance
    run_check "check-aggregate-compliance.sh" \
        "Aggregate Pattern Compliance" \
        "false" "true"
    
    # UseCase compliance
    run_check "check-usecase-compliance.sh" \
        "UseCase Pattern Compliance" \
        "false" "true"
    
    # Controller compliance
    run_check "check-controller-compliance.sh" \
        "Controller Pattern Compliance" \
        "false" "true"
    
    # JPA configuration (pending .NET translation)
    run_check_pending "check-jpa-projection-config.sh" \
        "JPA Projection Configuration" \
        "false" "true"
    
    # Spec compliance is important
    run_spec_compliance_check
    
    # Dependencies check (script not yet ported)
    run_check_pending "check-dependencies.sh" \
        "Dependencies and Versions" \
        "false" "true" "script not yet available in .NET"
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
        "false" "false"
    
    # Spring DI Test compliance (pending .NET translation)
    run_check_pending "check-test-spring-di.sh" \
        "Spring DI Test Compliance" \
        "true" "false"
    
    # Projection compliance
    run_check "check-projection-compliance.sh" \
        "Projection Pattern Compliance" \
        "false" "false"
    
    # Archive compliance
    run_check "check-archive-compliance.sh" \
        "Archive Pattern Compliance" \
        "false" "false"
    
    # Template sync check (script not yet ported)
    run_check_pending "check-template-sync.sh" \
        "Template Synchronization" \
        "false" "false" "script not yet available in .NET"
    
    # ADR index update (script not yet ported)
    run_check_pending "update-adr-index.sh" \
        "ADR Index Update" \
        "false" "false" "script not yet available in .NET"
    
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
echo -e "Skipped: ${YELLOW}$SKIPPED_CHECKS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
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
    echo -e "${YELLOW}║  ⚠ Passed with $WARNINGS Warning(s)          ║${NC}"
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
