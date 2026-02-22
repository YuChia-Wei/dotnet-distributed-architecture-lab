#!/bin/bash

# ====================================================================
# Repository Compliance Check
# 
# Generated from: repository-standards.md
# Purpose: Check compliance based on markdown documentation
# 
# THIS FILE IS AUTO-GENERATED FROM MARKDOWN - DO NOT EDIT MANUALLY
# Regenerate with: ./generate-check-scripts-from-md.sh
# ====================================================================

set -e

# Colors for output
RED='[0;31m'
GREEN='[0;32m'
YELLOW='[1;33m'
BLUE='[0;34m'
NC='[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SRC_DIR="$BASE_DIR/src"

TARGET_FILES=$(find "$SRC_DIR" -type f \( -path "*/Repositories/*.cs" -o -name "*Repository*.cs" \) -not -path "*/bin/*" -not -path "*/obj/*")
if [ -z "$TARGET_FILES" ]; then
    echo -e "${YELLOW}⚠ No target files found for this check${NC}"
    exit 0
fi

# Flags
HAS_VIOLATIONS=false

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Repository Compliance Check${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# ====================================================================
# Checks Generated from Markdown
# ====================================================================

# Rule 1: 禁止自定義 Repository 介面（interface）
echo -e "${YELLOW}Checking: Check: 禁止自定義 Repository 介面（interface）${NC}"

# Pattern that should exist: IRepository<
if [ true = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "IRepository<" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "IRepository<" {} 2>/dev/null | wc -l)
    fi
    if [ "$MATCHES" -gt 0 ]; then
        echo -e "${GREEN}✓ Found $MATCHES files with correct pattern${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Pattern not found in any files${NC}"
    fi
else
    MISSING=()
    for file in $TARGET_FILES; do
        if [ false = "true" ]; then
            match=$(grep -E "IRepository<" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "IRepository<" "$file" 2>/dev/null; then
                MISSING+=("$file")
            fi
        fi
    done
    if [ "${#MISSING[@]}" -eq 0 ]; then
        echo -e "${GREEN}✓ All files contain the required pattern${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Pattern missing in ${#MISSING[@]} files${NC}"
        for file in "${MISSING[@]}"; do
            echo -e "  ${YELLOW}→${NC} $file"
        done
    fi
fi
echo ""

# Rule 2: 禁止自定義 Repository 介面（interface）
echo -e "${YELLOW}Checking: Check: 禁止自定義 Repository 介面（interface）${NC}"

# Pattern that should NOT exist: interface\s+\w*Repository\s*:\s*IRepository
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "interface\s+\w*Repository\s*:\s*IRepository" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "interface\s+\w*Repository\s*:\s*IRepository" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "interface\s+\w*Repository\s*:\s*IRepository" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "interface\s+\w*Repository\s*:\s*IRepository" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 3: 查詢需求只能透過 Projection / Inquiry / Archive
echo -e "${YELLOW}Checking: Check: 查詢需求只能透過 Projection / Inquiry / Archive${NC}"

# Pattern that should NOT exist: FindBy|GetBy|QueryBy|SearchBy
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -Ei "FindBy|GetBy|QueryBy|SearchBy" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -Ei -l "FindBy|GetBy|QueryBy|SearchBy" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -Ei "FindBy|GetBy|QueryBy|SearchBy" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -Ei "FindBy|GetBy|QueryBy|SearchBy" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 4: No Custom Repository Interface
echo -e "${YELLOW}Checking: // ❌ Forbidden: custom query method in repository interface${NC}"

# Pattern that should NOT exist: interface\s+\w*Repository\s*:\s*IRepository
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "interface\s+\w*Repository\s*:\s*IRepository" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "interface\s+\w*Repository\s*:\s*IRepository" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "interface\s+\w*Repository\s*:\s*IRepository" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "interface\s+\w*Repository\s*:\s*IRepository" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# ====================================================================
# Summary
# ====================================================================

if [ "$HAS_VIOLATIONS" = true ]; then
    echo -e "${RED}✗ Violations found! Please fix the issues above.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
fi
