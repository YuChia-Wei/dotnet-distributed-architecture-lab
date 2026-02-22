#!/bin/bash

# ====================================================================
# Mapper Compliance Check
# 
# Generated from: mapper-standards.md
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

TARGET_FILES=$(find "$SRC_DIR" -type f \( -path "*/Mappers/*.cs" -o -name "*Mapper*.cs" -o -name "*Mapping*.cs" \) -not -path "*/bin/*" -not -path "*/obj/*")
if [ -z "$TARGET_FILES" ]; then
    echo -e "${YELLOW}⚠ No target files found for this check${NC}"
    exit 0
fi

# Flags
HAS_VIOLATIONS=false

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Mapper Compliance Check${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# ====================================================================
# Checks Generated from Markdown
# ====================================================================

# Rule 1: Mapper 必須是 static 或純轉換服務
echo -e "${YELLOW}Checking: Check: Mapper 必須是 static 或純轉換服務${NC}"

# Pattern that should exist: static class|sealed class
if [ true = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "static class|sealed class" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "static class|sealed class" {} 2>/dev/null | wc -l)
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
            match=$(grep -E "static class|sealed class" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "static class|sealed class" "$file" 2>/dev/null; then
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

# Rule 2: Mapper 必須是 static 或純轉換服務
echo -e "${YELLOW}Checking: Check: Mapper 必須是 static 或純轉換服務${NC}"

# Pattern that should NOT exist: I[A-Za-z0-9]*Repository|UseCase|Handler
if [ true = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "I[A-Za-z0-9]*Repository|UseCase|Handler" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "I[A-Za-z0-9]*Repository|UseCase|Handler" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ true = "true" ]; then
            match=$(grep -E "I[A-Za-z0-9]*Repository|UseCase|Handler" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "I[A-Za-z0-9]*Repository|UseCase|Handler" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 3: Mapper 必須是 static 或純轉換服務
echo -e "${YELLOW}Checking: Check: Mapper 必須是 static 或純轉換服務${NC}"

# Pattern that should exist: static
if [ false = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "static" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "static" {} 2>/dev/null | wc -l)
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
            match=$(grep -E "static" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "static" "$file" 2>/dev/null; then
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
