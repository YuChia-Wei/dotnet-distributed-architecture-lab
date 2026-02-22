#!/usr/bin/env bash
set -euo pipefail

# Test DI Compliance Checker (.NET)
# Purpose: Ensure tests follow xUnit + BDDfy + DI + NSubstitute rules

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_ROOT="$PROJECT_ROOT/src"

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}        .NET Test DI Compliance Checker          ${NC}"
echo -e "${BLUE}=================================================${NC}"

echo ""

ERRORS=0
WARNINGS=0

TEST_FILES=$(find "$SRC_ROOT" -type f -name "*Test*.cs" -o -path "*/Tests/*.cs" -o -path "*/tests/*.cs" 2>/dev/null | grep -v "bin/" | grep -v "obj/" || true)

if [ -z "$TEST_FILES" ]; then
  echo -e "${YELLOW}⚠ No .NET test files found${NC}"
  exit 0
fi

# Check base test class usage
if echo "$TEST_FILES" | xargs -I {} grep -n "BaseTestClass\|BaseUseCaseTest" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${RED}❌ Found BaseTestClass/BaseUseCaseTest usage (forbidden)${NC}"
  echo "$TEST_FILES" | xargs -I {} grep -n "BaseTestClass\|BaseUseCaseTest" {} 2>/dev/null | head -3
  ((ERRORS++))
else
  echo -e "${GREEN}✅ No BaseTestClass usage detected${NC}"
fi

# Check for MSTest/NUnit attributes
if echo "$TEST_FILES" | xargs -I {} grep -n "\[TestMethod\]|\[Test\]" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${YELLOW}⚠ Found MSTest/NUnit attributes; xUnit is required${NC}"
  ((WARNINGS++))
fi

# Check for MSTest TestClass attribute
if echo "$TEST_FILES" | xargs -I {} grep -n "\[TestClass\]" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${YELLOW}⚠ Found [TestClass] (MSTest). Use xUnit instead.${NC}"
  ((WARNINGS++))
fi

# Check for xUnit attributes
if echo "$TEST_FILES" | xargs -I {} grep -n "\[Fact\]|\[Theory\]" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${GREEN}✅ xUnit attributes detected${NC}"
else
  echo -e "${YELLOW}⚠ No xUnit attributes detected${NC}"
  ((WARNINGS++))
fi

# Check for NSubstitute usage (preferred)
if echo "$TEST_FILES" | xargs -I {} grep -n "Substitute\.For" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${GREEN}✅ NSubstitute usage detected${NC}"
else
  echo -e "${YELLOW}⚠ No NSubstitute usage detected (ok if no mocks)${NC}"
fi

# Check for other mocking frameworks
if echo "$TEST_FILES" | xargs -I {} grep -n "Moq\.|FakeItEasy" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${YELLOW}⚠ Found Moq/FakeItEasy usage (prefer NSubstitute)${NC}"
  ((WARNINGS++))
fi

# Check for profile strings in tests/config
if grep -R "test-inmemory\|test-outbox" "$SRC_ROOT" --include="*.cs" --include="*.json" 2>/dev/null | head -1 | grep -q .; then
  echo -e "${GREEN}✅ Profile strings detected (test-inmemory/outbox)${NC}"
else
  echo -e "${YELLOW}⚠ No profile strings found in tests/config${NC}"
  ((WARNINGS++))
fi

# Check for BDDfy usage
if echo "$TEST_FILES" | xargs -I {} grep -n "BDDfy" {} 2>/dev/null | head -1 | grep -q .; then
  echo -e "${GREEN}✅ BDDfy usage detected${NC}"
else
  CSPROJ_FILES=$(find "$SRC_ROOT" -type f -name "*.csproj" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true)
  if echo "$CSPROJ_FILES" | xargs -I {} grep -q "TestStack.BDDfy" {} 2>/dev/null; then
    echo -e "${GREEN}✅ BDDfy package reference detected${NC}"
  else
    echo -e "${YELLOW}⚠ No BDDfy usage detected (ok if no BDD tests yet)${NC}"
    ((WARNINGS++))
  fi
fi

echo ""
echo "================================================="
echo "                    SUMMARY                     "
echo "================================================="

if [ $ERRORS -gt 0 ]; then
  echo -e "${RED}❌ Found $ERRORS critical issues that must be fixed${NC}"
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo -e "${YELLOW}⚠ Found $WARNINGS warnings to review${NC}"
  exit 0
else
  echo -e "${GREEN}✅ Test DI compliance checks passed${NC}"
  exit 0
fi
