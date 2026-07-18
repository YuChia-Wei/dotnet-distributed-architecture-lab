#!/bin/bash

# ====================================================================
# Coding Standards Structural Integrity Checker (.NET)
#
# Purpose: 檢查 required files、headings、catalog routes 與 shell syntax。
# This script does not claim C# semantic or architecture compliance.
# Usage: ./check-coding-standards.sh
# ====================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base directories - use relative path or detect from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
STANDARDS_DIR="$BASE_DIR/.dev/standards/coding-standards"
MAIN_FILE="$BASE_DIR/.dev/standards/coding-standards.md"
INDEX_FILE="$STANDARDS_DIR/INDEX.MD"
SHARED_CONTEXT_DIR="$BASE_DIR/.ai/assets/shared"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Coding Standards Structural Integrity Check (.NET)${NC}"
echo -e "${BLUE}========================================${NC}"

# ====================================================================
# Self-Check: Verify this script is consistent with project structure
# ====================================================================
echo ""
echo -e "${YELLOW}0. Self-Check: Script Consistency${NC}"
echo "----------------------------------------"

SELF_CHECK_ERRORS=0

# Check if base directories exist
echo -e "${BLUE}Checking configured paths:${NC}"
if [ -d "$BASE_DIR" ]; then
    echo -e "  ${GREEN}✓${NC} BASE_DIR exists: $BASE_DIR"
else
    echo -e "  ${RED}✗${NC} BASE_DIR not found: $BASE_DIR"
    SELF_CHECK_ERRORS=$((SELF_CHECK_ERRORS + 1))
fi

if [ -d "$STANDARDS_DIR" ]; then
    echo -e "  ${GREEN}✓${NC} STANDARDS_DIR exists"
else
    echo -e "  ${RED}✗${NC} STANDARDS_DIR not found: $STANDARDS_DIR"
    SELF_CHECK_ERRORS=$((SELF_CHECK_ERRORS + 1))
fi

if [ -f "$INDEX_FILE" ]; then
    echo -e "  ${GREEN}✓${NC} INDEX_FILE exists"
else
    echo -e "  ${RED}✗${NC} INDEX_FILE not found: $INDEX_FILE"
    SELF_CHECK_ERRORS=$((SELF_CHECK_ERRORS + 1))
fi

if [ -d "$SHARED_CONTEXT_DIR" ]; then
    echo -e "  ${GREEN}✓${NC} SHARED_CONTEXT_DIR exists"
else
    echo -e "  ${RED}✗${NC} SHARED_CONTEXT_DIR not found: $SHARED_CONTEXT_DIR"
    SELF_CHECK_ERRORS=$((SELF_CHECK_ERRORS + 1))
fi

echo ""
echo -e "${BLUE}Checking for unchecked supporting files:${NC}"
echo -e "  ${BLUE}ℹ${NC} Supporting assets are validated selectively by canonical workflow usage."

# Self-check summary
echo ""
if [ $SELF_CHECK_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Self-check passed: Script is consistent with project structure${NC}"
else
    echo -e "${RED}✗ Self-check failed: Script needs updating (found $SELF_CHECK_ERRORS issues)${NC}"
    echo -e "${YELLOW}The script may not accurately check the project. Please fix these issues first.${NC}"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to check if file exists
check_file_exists() {
    local file=$1
    local name=$2
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $name exists"
        return 0
    else
        echo -e "${RED}✗${NC} $name is missing!"
        return 1
    fi
}

# Function to check section in file
check_section() {
    local file=$1
    local pattern=$2
    local section=$3

    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $section"
        return 0
    else
        echo -e "  ${RED}✗${NC} $section missing"
        return 1
    fi
}

# Function to count lines
count_lines() {
    local file=$1
    if [ -f "$file" ]; then
        wc -l "$file" | awk '{print $1}'
    else
        echo "0"
    fi
}

# Initialize error counter
ERRORS=0
WARNINGS=0

echo ""
echo -e "${YELLOW}1. Checking Main File${NC}"
echo "----------------------------------------"

# Check main coding-standards.md
if check_file_exists "$MAIN_FILE" "coding-standards.md"; then
    lines=$(count_lines "$MAIN_FILE")
    echo -e "  Lines: $lines"

    # Check required sections in main file
    echo -e "  ${BLUE}Required sections:${NC}"
    check_section "$MAIN_FILE" "## Overview" "Overview" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "## Specialized Coding Standards" "Specialized Coding Standards" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Aggregate Standards" "Aggregate Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "UseCase Standards" "UseCase Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Controller Standards" "Controller Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Repository Standards" "Repository Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Test Standards" "Test Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Projection Standards" "Projection Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Mapper Standards" "Mapper Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Archive Standards" "Archive Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Reactor Standards" "Reactor Standards link" || ERRORS=$((ERRORS + 1))
    check_section "$MAIN_FILE" "Profile / Environment Configuration Standards" "Profile Configuration Standards link" || ERRORS=$((ERRORS + 1))
else
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo -e "${YELLOW}2. Checking Specialized Standards Files${NC}"
echo "----------------------------------------"

# Define required specialized files
declare -a SPECIALIZED_FILES=(
    "aggregate-standards.md"
    "usecase-standards.md"
    "controller-standards.md"
    "repository-standards.md"
    "test-standards.md"
    "projection-standards.md"
    "mapper-standards.md"
    "archive-standards.md"
    "reactor-standards.md"
    "profile-configuration-standards.md"
)

# Check each specialized file
for file in "${SPECIALIZED_FILES[@]}"; do
    full_path="$STANDARDS_DIR/$file"
    if check_file_exists "$full_path" "$file"; then
        lines=$(count_lines "$full_path")
        echo -e "  Lines: $lines"

        # Check for minimum content
        if [ "$lines" -lt 20 ]; then
            echo -e "  ${YELLOW}⚠${NC} Warning: File seems too short (< 20 lines)"
            WARNINGS=$((WARNINGS + 1))
        fi

        # Check for required sections
        if ! grep -Eq "^## (🔴 )?(Mandatory Rules|MUST Rules|Core Rules|Core Boundaries)|^## (🔍 )?(Checklist|Review Checklist)" "$full_path"; then
            echo -e "  ${YELLOW}⚠${NC} Warning: Missing standard sections"
            WARNINGS=$((WARNINGS + 1))
        fi

        # Check for related documents section
        if ! grep -q "## Related Documents" "$full_path"; then
            echo -e "  ${YELLOW}⚠${NC} Warning: Missing Related Documents section"
            WARNINGS=$((WARNINGS + 1))
        fi

        if ! grep -Fq "\`$file\`" "$INDEX_FILE"; then
            echo -e "  ${RED}✗${NC} Missing exact catalog route in INDEX.MD"
            ERRORS=$((ERRORS + 1))
        fi
    else
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
# Navigation ownership is intentionally one-way: coding-standards.md catalogs
# the specialized standards. Leaf standards do not duplicate parent backlinks.
# coding-standards.md also contains compact overview contracts and links to the
# canonical detailed standards. Shared method names are intentional and are not
# sufficient evidence of duplicated normative ownership.
echo -e "${YELLOW}3. File Statistics${NC}"
echo "----------------------------------------"

# Calculate total lines
total_lines=0
echo -e "${BLUE}File sizes:${NC}"
for file in "${SPECIALIZED_FILES[@]}"; do
    full_path="$STANDARDS_DIR/$file"
    if [ -f "$full_path" ]; then
        lines=$(count_lines "$full_path")
        total_lines=$((total_lines + lines))
        printf "  %-30s: %5d lines\n" "$file" "$lines"
    fi
done

main_lines=$(count_lines "$MAIN_FILE")
printf "  %-30s: %5d lines\n" "coding-standards.md (main)" "$main_lines"
echo "  ----------------------------------------"
printf "  %-30s: %5d lines\n" "Total specialized files" "$total_lines"
printf "  %-30s: %5d lines\n" "Grand total" "$((total_lines + main_lines))"

echo ""
echo -e "${YELLOW}4. Script Health Check${NC}"
echo "----------------------------------------"

# Check health of scripts in .ai/scripts directory
SCRIPTS_DIR="$BASE_DIR/.ai/scripts"
echo -e "${BLUE}Checking scripts in .ai/scripts/:${NC}"

SCRIPT_ISSUES=0

# Check for hardcoded paths (excluding this check itself)
echo ""
echo -e "${BLUE}Checking for hardcoded paths:${NC}"
HARDCODED_SCRIPTS=$(grep -l "^[^#]*=[\"']*\/Users\/\|^[^#]*=[\"']*\/home\/\|^[^#]*=[\"']*C:\\\\" "$SCRIPTS_DIR"/*.sh 2>/dev/null || true)
if [ -z "$HARDCODED_SCRIPTS" ]; then
    echo -e "  ${GREEN}✓${NC} No hardcoded paths found in scripts"
else
    echo -e "  ${RED}✗${NC} Found hardcoded paths in:"
    echo "$HARDCODED_SCRIPTS" | while read script; do
        echo -e "    ${YELLOW}→${NC} $(basename "$script")"
        SCRIPT_ISSUES=$((SCRIPT_ISSUES + 1))
    done
    WARNINGS=$((WARNINGS + 1))
fi

# Check for executable permissions
echo ""
echo -e "${BLUE}Checking script permissions:${NC}"
NON_EXEC_SCRIPTS=0
for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ] && [ ! -x "$script" ]; then
        if [ $NON_EXEC_SCRIPTS -eq 0 ]; then
            echo -e "  ${YELLOW}⚠${NC} Scripts without execute permission:"
        fi
        echo -e "    ${YELLOW}→${NC} $(basename "$script")"
        NON_EXEC_SCRIPTS=$((NON_EXEC_SCRIPTS + 1))
    fi
done

if [ $NON_EXEC_SCRIPTS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} All scripts have execute permission"
else
    echo -e "  ${YELLOW}Tip: Run 'chmod +x $SCRIPTS_DIR/*.sh' to fix${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for bash syntax errors
echo ""
echo -e "${BLUE}Checking script syntax:${NC}"
SYNTAX_ERRORS=0
for script in "$SCRIPTS_DIR"/*.sh; do
    if [ -f "$script" ]; then
        if ! bash -n "$script" 2>/dev/null; then
            if [ $SYNTAX_ERRORS -eq 0 ]; then
                echo -e "  ${RED}✗${NC} Scripts with syntax errors:"
            fi
            echo -e "    ${RED}→${NC} $(basename "$script")"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} All scripts have valid syntax"
fi

# Count total scripts
TOTAL_SCRIPTS=$(ls -1 "$SCRIPTS_DIR"/*.sh 2>/dev/null | wc -l)
echo ""
echo -e "${BLUE}Script statistics:${NC}"
echo -e "  Total scripts: $TOTAL_SCRIPTS"
echo -e "  Scripts with issues: $((SCRIPT_ISSUES + NON_EXEC_SCRIPTS + SYNTAX_ERRORS))"

echo ""
echo "========================================"
echo -e "${BLUE}Summary${NC}"
echo "========================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed successfully!${NC}"
    echo "Structural integrity passed for required files, headings, catalog routes, executable modes, and shell syntax."
    echo "This result does not assert C# semantic compliance, architecture completeness, example correctness, or target technology adoption."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Checks passed with $WARNINGS warning(s)${NC}"
    echo "Consider reviewing the warnings above."
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo "Please fix the errors before proceeding."
    exit 1
fi
