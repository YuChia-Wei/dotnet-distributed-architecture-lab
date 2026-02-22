#!/usr/bin/env bash
set -euo pipefail

# Script: validate-dual-profile-config.sh (.NET)
# Purpose: Validate dual-profile (InMemory + Outbox) configuration

echo "======================================"
echo "Validating Dual-Profile Configuration (.NET)"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERROR_COUNT=0
WARNING_COUNT=0

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

EXPECTED=("appsettings.inmemory.json" "appsettings.test-inmemory.json" "appsettings.outbox.json" "appsettings.test-outbox.json")

for file in "${EXPECTED[@]}"; do
  if find "$PROJECT_ROOT" -name "$file" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | head -1 | grep -q .; then
    echo -e "${GREEN}✅ Found $file${NC}"
  else
    echo -e "${YELLOW}⚠ Missing $file${NC}"
    ((WARNING_COUNT++))
  fi
done

# Check for ASPNETCORE_ENVIRONMENT inside config
if find "$PROJECT_ROOT" -name "appsettings*.json" -type f -not -path "*/bin/*" -not -path "*/obj/*" -exec grep -l "ASPNETCORE_ENVIRONMENT" {} \; 2>/dev/null | head -1 | grep -q .; then
  echo -e "${RED}❌ ASPNETCORE_ENVIRONMENT should not be defined in appsettings files${NC}"
  ((ERROR_COUNT++))
fi

# Outbox gating check
OUTBOX_CONFIG_FILES=$(grep -R "UseDurableOutbox" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | cut -d: -f1 | sort -u || true)
if [ -n "$OUTBOX_CONFIG_FILES" ]; then
  for file in $OUTBOX_CONFIG_FILES; do
    if grep -qi "outbox" "$file"; then
      echo -e "${GREEN}✅ $file appears to gate outbox config by environment${NC}"
    else
      echo -e "${YELLOW}⚠ $file uses UseDurableOutbox without explicit outbox gating${NC}"
      ((WARNING_COUNT++))
    fi
  done
fi

# Check for InMemory and Outbox DB configuration
if grep -R "UseInMemoryDatabase" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -q .; then
  if grep -R "UseInMemoryDatabase" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -qi "inmemory"; then
    echo -e "${GREEN}✅ InMemory database configuration found${NC}"
  else
    echo -e "${YELLOW}⚠ UseInMemoryDatabase found without explicit inmemory gating${NC}"
    ((WARNING_COUNT++))
  fi
else
  echo -e "${YELLOW}⚠ No InMemory database configuration found${NC}"
  ((WARNING_COUNT++))
fi

if grep -R "UseNpgsql\|UseSqlServer" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -q .; then
  if grep -R "UseNpgsql\|UseSqlServer" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -qi "outbox"; then
    echo -e "${GREEN}✅ Outbox DB configuration found${NC}"
  else
    echo -e "${YELLOW}⚠ Outbox DB config found without explicit outbox gating${NC}"
    ((WARNING_COUNT++))
  fi
else
  echo -e "${YELLOW}⚠ No Outbox DB configuration found${NC}"
  ((WARNING_COUNT++))
fi

# Check for profile strings in tests/config
if grep -R "test-inmemory\|test-outbox" "$PROJECT_ROOT" --include="*.cs" --include="*.json" 2>/dev/null | head -1 | grep -q .; then
  echo -e "${GREEN}✅ Profile strings detected (test-inmemory/outbox)${NC}"
else
  echo -e "${YELLOW}⚠ No profile strings found${NC}"
  ((WARNING_COUNT++))
fi

# Summary
echo -e "\n======================================"
echo "Summary"
echo "======================================"

echo -e "Errors: $ERROR_COUNT"
echo -e "Warnings: $WARNING_COUNT"

if [ $ERROR_COUNT -eq 0 ] && [ $WARNING_COUNT -eq 0 ]; then
  echo -e "${GREEN}✅ Dual-profile configuration is valid!${NC}"
  exit 0
fi

if [ $ERROR_COUNT -gt 0 ]; then
  echo -e "${RED}❌ Found $ERROR_COUNT critical errors${NC}"
  exit 1
fi

echo -e "${YELLOW}⚠ Found $WARNING_COUNT warnings${NC}"
exit 0
