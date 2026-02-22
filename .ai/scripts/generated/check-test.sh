#!/bin/bash

# ====================================================================
# Test Compliance Check
# 
# Generated from: test-standards.md
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

TARGET_FILES=$(find "$SRC_DIR" -type f \( -path "*/Tests/*.cs" -o -name "*Test*.cs" \) -not -path "*/bin/*" -not -path "*/obj/*")
if [ -z "$TARGET_FILES" ]; then
    echo -e "${YELLOW}⚠ No target files found for this check${NC}"
    exit 0
fi

# Flags
HAS_VIOLATIONS=false

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}Test Compliance Check${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# ====================================================================
# Checks Generated from Markdown
# ====================================================================

# Rule 1: 測試框架為 xUnit + BDDfy
echo -e "${YELLOW}Checking: Check: 測試框架為 xUnit + BDDfy${NC}"

# Pattern that should NOT exist: NUnit|MSTest|Moq|FakeItEasy|\\[TestClass\\]|\\[TestMethod\\]
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -Ei "NUnit|MSTest|Moq|FakeItEasy|\\[TestClass\\]|\\[TestMethod\\]" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -Ei -l "NUnit|MSTest|Moq|FakeItEasy|\\[TestClass\\]|\\[TestMethod\\]" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -Ei "NUnit|MSTest|Moq|FakeItEasy|\\[TestClass\\]|\\[TestMethod\\]" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -Ei "NUnit|MSTest|Moq|FakeItEasy|\\[TestClass\\]|\\[TestMethod\\]" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 2: 測試框架為 xUnit + BDDfy (optional)
echo -e "${YELLOW}Checking (optional): Check: 測試框架為 xUnit + BDDfy${NC}"

# Optional pattern: BDDfy|TestStack\\.BDDfy|Gherkin-style
if [ false = "true" ]; then
    MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "BDDfy|TestStack\\.BDDfy|Gherkin-style" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
else
    MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "BDDfy|TestStack\\.BDDfy|Gherkin-style" {} 2>/dev/null | wc -l)
fi

if [ "$MATCHES" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $MATCHES files with optional pattern${NC}"
else
    echo -e "${CYAN}ℹ Optional pattern not found${NC}"
fi
echo ""

# Rule 3: 禁止使用 BaseTestClass / BaseUseCaseTest
echo -e "${YELLOW}Checking: Check: 禁止使用 BaseTestClass / BaseUseCaseTest${NC}"

# Pattern that should NOT exist: BaseTestClass|BaseUseCaseTest
if [ true = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "BaseTestClass|BaseUseCaseTest" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "BaseTestClass|BaseUseCaseTest" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ true = "true" ]; then
            match=$(grep -E "BaseTestClass|BaseUseCaseTest" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "BaseTestClass|BaseUseCaseTest" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 4: 禁止使用 BaseTestClass / BaseUseCaseTest
echo -e "${YELLOW}Checking: Check: 禁止使用 BaseTestClass / BaseUseCaseTest${NC}"

# Pattern that should NOT exist: BaseTestClass|BaseUseCaseTest
if [ false = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$(grep -E "BaseTestClass|BaseUseCaseTest" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "BaseTestClass|BaseUseCaseTest" {} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}✗ Found violations:${NC}"
    for file in $VIOLATIONS; do
        if [ false = "true" ]; then
            match=$(grep -E "BaseTestClass|BaseUseCaseTest" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${RED}→${NC} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${RED}→${NC} $file"
            grep -E "BaseTestClass|BaseUseCaseTest" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${GREEN}✓ No violations found${NC}"
fi
echo ""

# Rule 5: Mock 使用 NSubstitute (optional)
echo -e "${YELLOW}Checking (optional): Check: Mock 使用 NSubstitute${NC}"

# Optional pattern: Substitute\\.For
if [ false = "true" ]; then
    MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E "Substitute\\.For" {} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
else
    MATCHES=$(echo "$TARGET_FILES" | xargs -I {} grep -E -l "Substitute\\.For" {} 2>/dev/null | wc -l)
fi

if [ "$MATCHES" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $MATCHES files with optional pattern${NC}"
else
    echo -e "${CYAN}ℹ Optional pattern not found${NC}"
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
