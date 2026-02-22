#!/bin/bash

# ====================================================================
# Coding Standards Compliance Checker (.NET)
#
# Purpose: 檢查 dotnet coding-standards 相關檔案的完整性和一致性
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
PROMPTS_DIR="$BASE_DIR/.ai/prompts"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Coding Standards Integrity Check (.NET)${NC}"
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
    ((SELF_CHECK_ERRORS++))
fi

if [ -d "$STANDARDS_DIR" ]; then
    echo -e "  ${GREEN}✓${NC} STANDARDS_DIR exists"
else
    echo -e "  ${RED}✗${NC} STANDARDS_DIR not found: $STANDARDS_DIR"
    ((SELF_CHECK_ERRORS++))
fi

if [ -d "$PROMPTS_DIR" ]; then
    echo -e "  ${GREEN}✓${NC} PROMPTS_DIR exists"
else
    echo -e "  ${RED}✗${NC} PROMPTS_DIR not found: $PROMPTS_DIR"
    ((SELF_CHECK_ERRORS++))
fi

# Check if files referenced in script actually exist
echo ""
echo -e "${BLUE}Checking files referenced in this script:${NC}"

# Extract all .md files mentioned in check_prompt_references calls
REFERENCED_PROMPTS=$(grep "check_prompt_references.*\.md\"" "$0" | sed 's/.*"\$PROMPTS_DIR\/\([^"]*\)".*/\1/' | sort -u)

MISSING_PROMPTS=0
for prompt in $REFERENCED_PROMPTS; do
    if [ -f "$PROMPTS_DIR/$prompt" ]; then
        echo -e "  ${GREEN}✓${NC} $prompt"
    else
        echo -e "  ${RED}✗${NC} $prompt - NOT FOUND (script references non-existent file)"
        ((MISSING_PROMPTS++))
        ((SELF_CHECK_ERRORS++))
    fi
done

if [ $MISSING_PROMPTS -eq 0 ]; then
    echo -e "  ${GREEN}All referenced prompt files exist${NC}"
fi

# Check for prompts that exist but are not checked
echo ""
echo -e "${BLUE}Checking for unchecked prompt files:${NC}"
ACTUAL_PROMPTS=$(ls "$PROMPTS_DIR"/*-prompt.md 2>/dev/null | xargs -n1 basename | sort)
UNCHECKED_PROMPTS=0

for actual_prompt in $ACTUAL_PROMPTS; do
    if ! echo "$REFERENCED_PROMPTS" | grep -q "^$actual_prompt$"; then
        # Skip some prompts that don't need checking
        if [[ "$actual_prompt" == "frontend-"* ]] || [[ "$actual_prompt" == "mutation-"* ]] || [[ "$actual_prompt" == "outbox-"* ]] || [[ "$actual_prompt" == "profile-"* ]] || [[ "$actual_prompt" == "spec-"* ]]; then
            continue
        fi
        echo -e "  ${YELLOW}⚠${NC} $actual_prompt exists but is not checked by this script"
        ((UNCHECKED_PROMPTS++))
    fi
done

if [ $UNCHECKED_PROMPTS -eq 0 ]; then
    echo -e "  ${GREEN}All relevant prompts are being checked${NC}"
fi

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
    check_section "$MAIN_FILE" "## 概述" "概述" || ((ERRORS++))
    check_section "$MAIN_FILE" "## 專門領域編碼標準" "專門領域編碼標準" || ((ERRORS++))
    check_section "$MAIN_FILE" "Aggregate Standards" "Aggregate Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "UseCase Standards" "UseCase Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "Controller Standards" "Controller Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "Repository Standards" "Repository Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "Test Standards" "Test Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "Projection Standards" "Projection Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "Mapper Standards" "Mapper Standards link" || ((ERRORS++))
    check_section "$MAIN_FILE" "Archive Standards" "Archive Standards link" || ((ERRORS++))
else
    ((ERRORS++))
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
            ((WARNINGS++))
        fi

        # Check for required sections
        if ! grep -q "## 🔴 必須遵守的規則\|## ✅ 建議\|## 🔍 檢查清單" "$full_path"; then
            echo -e "  ${YELLOW}⚠${NC} Warning: Missing standard sections"
            ((WARNINGS++))
        fi

        # Check for related documents section
        if ! grep -q "## 相關文件" "$full_path"; then
            echo -e "  ${YELLOW}⚠${NC} Warning: Missing 相關文件 section"
            ((WARNINGS++))
        fi
    else
        ((ERRORS++))
    fi
done

echo ""
echo -e "${YELLOW}3. Checking Sub-agent Prompts References${NC}"
echo "----------------------------------------"

# Check individual prompt files for references
check_prompt_references() {
    local prompt_file=$1
    local expected_refs=$2
    local prompt_name=$(basename "$prompt_file")

    echo -e "${BLUE}$prompt_name:${NC}"
    if [ -f "$prompt_file" ]; then
        # Check if references main coding-standards.md
        local has_main_ref=false
        if grep -q "coding-standards\.md" "$prompt_file" 2>/dev/null; then
            has_main_ref=true
            echo -e "  ${GREEN}✓${NC} References main coding-standards.md"
        fi

        # Split expected refs by comma
        IFS=',' read -ra REFS <<< "$expected_refs"
        for ref in "${REFS[@]}"; do
            if grep -q "$ref" "$prompt_file" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} References $ref"
            elif [ "$has_main_ref" = true ]; then
                # If references main file, it's acceptable (modular design)
                echo -e "  ${BLUE}ℹ${NC} $ref covered by main coding-standards.md reference"
            else
                echo -e "  ${RED}✗${NC} Missing reference to $ref"
                ((WARNINGS++))
            fi
        done
    else
        echo -e "  ${YELLOW}⚠${NC} File not found"
        ((WARNINGS++))
    fi
}

# Check each prompt file
check_prompt_references "$PROMPTS_DIR/command-sub-agent-prompt.md" "aggregate-standards.md,usecase-standards.md,repository-standards.md"
check_prompt_references "$PROMPTS_DIR/query-sub-agent-prompt.md" "usecase-standards.md,repository-standards.md,projection-standards.md"

check_prompt_references "$PROMPTS_DIR/aggregate-sub-agent-prompt.md" "aggregate-standards.md"
check_prompt_references "$PROMPTS_DIR/aggregate-test-generation-prompt.md" "test-standards.md,aggregate-standards.md"
check_prompt_references "$PROMPTS_DIR/aggregate-code-review-prompt.md" "aggregate-standards.md,coding-standards.md"

check_prompt_references "$PROMPTS_DIR/controller-code-generation-prompt.md" "controller-standards.md"
check_prompt_references "$PROMPTS_DIR/controller-test-generation-prompt.md" "test-standards.md,controller-standards.md"
check_prompt_references "$PROMPTS_DIR/controller-code-review-prompt.md" "controller-standards.md,test-standards.md"

check_prompt_references "$PROMPTS_DIR/reactor-sub-agent-prompt.md" "aggregate-standards.md,usecase-standards.md"
check_prompt_references "$PROMPTS_DIR/reactor-test-generation-prompt.md" "test-standards.md"
check_prompt_references "$PROMPTS_DIR/reactor-code-review-prompt.md" "coding-standards.md"

check_prompt_references "$PROMPTS_DIR/usecase-test-generation-prompt.md" "test-standards.md,usecase-standards.md"
check_prompt_references "$PROMPTS_DIR/code-review-prompt.md" "coding-standards.md,aggregate-standards.md"

# General/testing prompts
check_prompt_references "$PROMPTS_DIR/testing-standards-prompt.md" "test-standards.md"


echo ""
echo -e "${YELLOW}4. Checking Cross-References${NC}"
echo "----------------------------------------"

# Check if specialized files reference back to main file
echo -e "${BLUE}Back references to main file:${NC}"
for file in "${SPECIALIZED_FILES[@]}"; do
    full_path="$STANDARDS_DIR/$file"
    if [ -f "$full_path" ]; then
        if grep -q "../coding-standards.md" "$full_path" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $file → coding-standards.md"
        else
            echo -e "  ${YELLOW}⚠${NC} $file missing back reference"
            ((WARNINGS++))
        fi
    fi
done

echo ""
echo -e "${YELLOW}5. Content Consistency Check${NC}"
echo "----------------------------------------"

# Check for duplicate content between main and specialized files
echo -e "${BLUE}Checking for unnecessary duplication:${NC}"

if grep -q "Repository 只能有三個方法" "$MAIN_FILE" 2>/dev/null && \
   grep -q "Repository 只能有三個方法" "$STANDARDS_DIR/repository-standards.md" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} Repository rules might be duplicated"
    ((WARNINGS++))
else
    echo -e "  ${GREEN}✓${NC} No major duplication detected"
fi

echo ""
echo -e "${YELLOW}6. File Statistics${NC}"
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
echo -e "${YELLOW}7. Script Health Check${NC}"
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
        ((SCRIPT_ISSUES++))
    done
    ((WARNINGS++))
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
        ((NON_EXEC_SCRIPTS++))
    fi
done

if [ $NON_EXEC_SCRIPTS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} All scripts have execute permission"
else
    echo -e "  ${YELLOW}Tip: Run 'chmod +x $SCRIPTS_DIR/*.sh' to fix${NC}"
    ((WARNINGS++))
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
            ((SYNTAX_ERRORS++))
            ((ERRORS++))
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
    echo "Coding standards files are complete and well-organized."
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
