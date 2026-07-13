#!/usr/bin/env bash
set -euo pipefail

# Framework API Compliance Checker (.NET)
# Purpose: Detect common Wolverine/EF Core outbox integration issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

ERRORS=0
WARNINGS=0
CHECKS=0

if [ ! -d "$SRC_DIR" ]; then
  echo -e "${YELLOW}⚠ No src directory found: $SRC_DIR${NC}"
  exit 0
fi

echo "================================================="
echo "    .NET Framework API Compliance Checker      "
echo "================================================="

check_pattern() {
  local pattern="$1"
  local message="$2"
  local severity="$3"

  ((CHECKS++))

  if grep -R "$pattern" "$SRC_DIR" --include="*.cs" 2>/dev/null | grep -v "^Binary file" > /dev/null; then
    if [ "$severity" = "ERROR" ]; then
      echo -e "${RED}❌ $message${NC}"
      grep -R "$pattern" "$SRC_DIR" --include="*.cs" 2>/dev/null | head -3 | sed 's/^/     /'
      ((ERRORS++))
    else
      echo -e "${YELLOW}⚠️  $message${NC}"
      ((WARNINGS++))
    fi
    return 1
  else
    echo -e "${GREEN}✅ $message${NC}"
    return 0
  fi
}

check_correct_pattern() {
  local pattern="$1"
  local message="$2"

  ((CHECKS++))

  if grep -R "$pattern" "$SRC_DIR" --include="*.cs" 2>/dev/null | grep -v "^Binary file" > /dev/null; then
    echo -e "${GREEN}✅ $message${NC}"
    return 0
  else
    echo -e "${YELLOW}⚠️  $message not found (may be needed)${NC}"
    ((WARNINGS++))
    return 1
  fi
}

echo ""
echo "1. Message Store Client Creation Check"
echo "--------------------------------------"

check_pattern "new .*MessageStore" \
  "Found direct MessageStore instantiation (must use DI + Wolverine outbox)" \
  "ERROR"

check_correct_pattern "UseDurableOutbox" \
  "Found UseDurableOutbox configuration"

check_correct_pattern "PersistMessagesWithPostgresql" \
  "Found Wolverine PostgreSQL persistence configuration"

echo ""
echo "2. Outbox Mapper Structure Check"
echo "--------------------------------"

OUTBOX_MAPPER_FILES=$(find "$SRC_DIR" -type f -name "*OutboxMapper.cs" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true)
if [ -n "$OUTBOX_MAPPER_FILES" ]; then
  for file in $OUTBOX_MAPPER_FILES; do
    echo -e "${RED}❌ Found standalone OutboxMapper: $file${NC}"
    echo "   OutboxMapper must be nested inside the aggregate mapper class."
    ((ERRORS++))
  done
else
  echo -e "${GREEN}✅ No standalone OutboxMapper classes found${NC}"
fi

echo ""
echo "3. EF Core Mapping Checks"
echo "--------------------------"

check_pattern "@Entity|@Transient|jakarta\.|javax\." \
  "Found Java/Jakarta annotations in .NET code (remove them)" \
  "ERROR"

echo -e "${BLUE}Checking [NotMapped] for outbox-only fields...${NC}"
FILES_WITH_EVENTS=$(grep -R "DomainEventDatas" "$SRC_DIR" --include="*.cs" 2>/dev/null | cut -d: -f1 | sort -u || true)

if [ -n "$FILES_WITH_EVENTS" ]; then
  for file in $FILES_WITH_EVENTS; do
    if grep -B2 "DomainEventDatas" "$file" | grep -q "\[NotMapped\]"; then
      echo -e "${GREEN}✅ $file has [NotMapped] for DomainEventDatas${NC}"
    else
      echo -e "${RED}❌ $file missing [NotMapped] for DomainEventDatas${NC}"
      ((ERRORS++))
    fi
  done
else
  echo -e "${BLUE}ℹ️  No DomainEventDatas fields found${NC}"
fi

FILES_WITH_STREAM=$(grep -R "StreamName" "$SRC_DIR" --include="*.cs" 2>/dev/null | cut -d: -f1 | sort -u || true)
if [ -n "$FILES_WITH_STREAM" ]; then
  for file in $FILES_WITH_STREAM; do
    if grep -B2 "StreamName" "$file" | grep -q "\[NotMapped\]"; then
      echo -e "${GREEN}✅ $file has [NotMapped] for StreamName${NC}"
    else
      echo -e "${YELLOW}⚠️  $file might need [NotMapped] for StreamName${NC}"
      ((WARNINGS++))
    fi
  done
fi

echo ""
echo "4. OutboxData Implementation Check"
echo "-----------------------------------"

OUTBOX_DATA_FILES=$(grep -R "OutboxData" "$SRC_DIR" --include="*.cs" 2>/dev/null | cut -d: -f1 | sort -u || true)
if [ -n "$OUTBOX_DATA_FILES" ]; then
  for file in $OUTBOX_DATA_FILES; do
    echo -e "${BLUE}  Checking $file:${NC}"
    if grep -q "\[Key\]" "$file"; then
      echo -e "${GREEN}    ✓ Has [Key]${NC}"
    else
      echo -e "${YELLOW}    ⚠ Missing [Key]${NC}"
      ((WARNINGS++))
    fi
    if grep -q "\[ConcurrencyCheck\]" "$file"; then
      echo -e "${GREEN}    ✓ Has [ConcurrencyCheck]${NC}"
    else
      echo -e "${YELLOW}    ⚠ Missing [ConcurrencyCheck]${NC}"
      ((WARNINGS++))
    fi
  done
else
  echo -e "${BLUE}ℹ️  No OutboxData implementations found${NC}"
fi

echo ""
echo "5. Environment Gating Check"
echo "----------------------------"

OUTBOX_CONFIG_FILES=$(grep -R "UseDurableOutbox" "$SRC_DIR" --include="*.cs" 2>/dev/null | cut -d: -f1 | sort -u || true)
if [ -n "$OUTBOX_CONFIG_FILES" ]; then
  for file in $OUTBOX_CONFIG_FILES; do
    if grep -qi "outbox" "$file"; then
      echo -e "${GREEN}✅ $file references outbox environment gating${NC}"
    else
      echo -e "${YELLOW}⚠️  $file uses UseDurableOutbox but lacks outbox environment gating${NC}"
      ((WARNINGS++))
    fi
  done
fi

echo ""
echo "================================================="
echo "                    SUMMARY                     "
echo "================================================="

echo "Checks performed: $CHECKS"

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
  echo -e "${GREEN}✅ All framework API checks passed!${NC}"
elif [ "$ERRORS" -eq 0 ]; then
  echo -e "${YELLOW}⚠️  Found $WARNINGS warning(s)${NC}"
else
  echo -e "${RED}❌ Found $ERRORS error(s) and $WARNINGS warning(s)${NC}"
  echo "See: .dev/guides/design-guides/FRAMEWORK-API-INTEGRATION-GUIDE.md for details"
fi

exit $ERRORS
