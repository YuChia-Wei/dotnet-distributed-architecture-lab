#!/bin/bash

# ====================================================================
# Projection Compliance Check
# 
# Generated from: projection-standards.md
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

TARGET_FILES=$(find "$SRC_DIR" -type f \( -path "*/Projections/*.cs" -o -path "*/ReadModels/*.cs" -o -name "*Projection*.cs" -o -name "*ReadModel*.cs" \) -not -path "*/bin/*" -not -path "*/obj/*")
if [ -z "$TARGET_FILES" ]; then
    echo -e "${YELLOW}⚠ No target files found for this check${NC}"
    exit 0
fi

# Flags
HAS_VIOLATIONS=false

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Projection Compliance Check${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# ====================================================================
# Checks Generated from Markdown
# ====================================================================

# Rule 1: Projection 不得包含 Domain 變更行為
echo -e "${YELLOW}Checking: Check: Projection 不得包含 Domain 變更行為${NC}"

# Pattern that should NOT exist: SaveChanges
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "SaveChanges" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "SaveChanges" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "SaveChanges" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "SaveChanges" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 2: Projection 不得包含 Domain 變更行為
echo -e "${YELLOW}Checking: Check: Projection 不得包含 Domain 變更行為${NC}"

# Pattern that should NOT exist: Update\(
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "Update\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "Update\(" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "Update\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "Update\(" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 3: Projection 不得包含 Domain 變更行為
echo -e "${YELLOW}Checking: Check: Projection 不得包含 Domain 變更行為${NC}"

# Pattern that should NOT exist: Add\(
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "Add\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "Add\(" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "Add\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "Add\(" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 4: Projection 不得包含 Domain 變更行為
echo -e "${YELLOW}Checking: Check: Projection 不得包含 Domain 變更行為${NC}"

# Pattern that should NOT exist: Remove\(
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "Remove\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "Remove\(" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "Remove\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "Remove\(" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 5: Projection 使用 EF Core Query/Projection
echo -e "${YELLOW}Checking: Check: Projection 使用 EF Core Query/Projection${NC}"

# Pattern that should exist: AsNoTracking|Select|ProjectTo
if [ true = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "AsNoTracking|Select|ProjectTo" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "AsNoTracking|Select|ProjectTo" {} 2>/dev/null | wc -l)
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
            match=$(grep -E "AsNoTracking|Select|ProjectTo" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "AsNoTracking|Select|ProjectTo" "$file" 2>/dev/null; then
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

# Rule 6: Projection 使用 EF Core Query/Projection
echo -e "${YELLOW}Checking: Check: Projection 使用 EF Core Query/Projection${NC}"

# Pattern that should NOT exist: \b(FindBy|DeleteBy|GetBy|QueryBy)
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "\b(FindBy|DeleteBy|GetBy|QueryBy)" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "\b(FindBy|DeleteBy|GetBy|QueryBy)" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "\b(FindBy|DeleteBy|GetBy|QueryBy)" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "\b(FindBy|DeleteBy|GetBy|QueryBy)" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
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
