#!/bin/bash

# ====================================================================
# Usecase Compliance Check
# 
# Generated from: usecase-standards.md
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

TARGET_FILES=$(find "$SRC_DIR" -type f \( -path "*/UseCases/*.cs" -o -path "*/Handlers/*.cs" -o -name "*UseCase*.cs" -o -name "*Handler*.cs" \) -not -path "*/bin/*" -not -path "*/obj/*")
if [ -z "$TARGET_FILES" ]; then
    echo -e "${YELLOW}⚠ No target files found for this check${NC}"
    exit 0
fi

# Flags
HAS_VIOLATIONS=false

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Usecase Compliance Check${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# ====================================================================
# Checks Generated from Markdown
# ====================================================================

# Rule 1: Command 與 Query 必須分離
echo -e "${YELLOW}Checking: Check: Command 與 Query 必須分離${NC}"

# Pattern that should exist: Handle\(
if [ false = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "Handle\(" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "Handle\(" {} 2>/dev/null | wc -l)
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
            match=$(grep -E "Handle\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "Handle\(" "$file" 2>/dev/null; then
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

# Rule 2: 依賴注入必須透過 constructor
echo -e "${YELLOW}Checking: Check: 依賴注入必須透過 constructor${NC}"

# Pattern that should NOT exist: IServiceProvider|ServiceLocator
if [ true = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -Ei "IServiceProvider|ServiceLocator" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -Ei -l "IServiceProvider|ServiceLocator" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ true = "true" ]; then
            match=$(grep -Ei "IServiceProvider|ServiceLocator" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -Ei "IServiceProvider|ServiceLocator" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 3: 依賴注入必須透過 constructor
echo -e "${YELLOW}Checking: Check: 依賴注入必須透過 constructor${NC}"

# Pattern that should exist: private readonly
if [ false = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "private readonly" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "private readonly" {} 2>/dev/null | wc -l)
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
            match=$(grep -E "private readonly" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "private readonly" "$file" 2>/dev/null; then
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

# Rule 4: 依賴注入必須透過 constructor
echo -e "${YELLOW}Checking: Check: 依賴注入必須透過 constructor${NC}"

# Pattern that should NOT exist: \[Inject\]|IServiceProvider
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "\[Inject\]|IServiceProvider" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "\[Inject\]|IServiceProvider" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "\[Inject\]|IServiceProvider" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "\[Inject\]|IServiceProvider" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 5: 依賴注入必須透過 constructor
echo -e "${YELLOW}Checking: Check: 依賴注入必須透過 constructor${NC}"

# Pattern that should exist: public\s+\w+\(
if [ false = "true" ]; then
    if [ false = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "public\s+\w+\(" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "public\s+\w+\(" {} 2>/dev/null | wc -l)
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
            match=$(grep -E "public\s+\w+\(" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! grep -E -q "public\s+\w+\(" "$file" 2>/dev/null; then
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
