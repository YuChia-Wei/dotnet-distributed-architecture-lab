#!/usr/bin/env bash
set -euo pipefail

# Domain Events Compliance Check Script (.NET)
# Ensures domain events follow .NET ezDDD conventions (metadata, event markers)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Domain Events Compliance Check (.NET)║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"

echo ""

ERROR_COUNT=0
WARNING_COUNT=0
TOTAL_FILES=0
PASSED_FILES=0

if [ ! -d "$SRC_DIR" ]; then
  echo -e "${YELLOW}⚠ No src directory found: $SRC_DIR${NC}"
  exit 0
fi

# Find all domain event files
EVENT_FILES=$(find "$SRC_DIR" -type f \( -name "*Event.cs" -o -name "*Events.cs" \) -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true)

if [ -z "$EVENT_FILES" ]; then
  echo -e "${YELLOW}No domain event files found${NC}"
  exit 0
fi

check_custom_interfaces() {
  local file=$1
  local errors=()

  if grep -q "interface ConstructionEvent" "$file" 2>/dev/null; then
    errors+=("❌ Custom ConstructionEvent interface found (use shared event marker instead)")
    ((ERROR_COUNT++))
  fi

  if grep -q "interface DestructionEvent" "$file" 2>/dev/null; then
    errors+=("❌ Custom DestructionEvent interface found (use shared event marker instead)")
    ((ERROR_COUNT++))
  fi

  if [ ${#errors[@]} -gt 0 ]; then
    echo -e "\n${RED}Issues found in: ${BOLD}$(basename "$file")${NC}"
    for error in "${errors[@]}"; do
      echo -e "  $error"
    done
    return 1
  fi

  return 0
}

check_domain_event_structure() {
  local file=$1
  local warnings=()

  if ! grep -Eq "(record|class)\s+[A-Za-z0-9_]+Event" "$file" 2>/dev/null; then
    warnings+=("⚠️  No Event record/class declaration detected")
    ((WARNING_COUNT++))
  fi

  if ! grep -Eq ":\s*(IDomainEvent|IEvent|DomainEvent)" "$file" 2>/dev/null; then
    warnings+=("⚠️  Event does not implement a known marker interface (IDomainEvent/IEvent)")
    ((WARNING_COUNT++))
  fi

  if ! grep -Eq "Metadata|MetaData" "$file" 2>/dev/null || ! grep -Eq "Dictionary<|IReadOnlyDictionary<" "$file" 2>/dev/null; then
    warnings+=("⚠️  Missing Metadata property (expected dictionary-like metadata)")
    ((WARNING_COUNT++))
  fi

  if ! grep -Eq "EventType|EventName|TypeMapper" "$file" 2>/dev/null; then
    warnings+=("⚠️  Missing event type mapping (EventType/EventName/TypeMapper)")
    ((WARNING_COUNT++))
  fi

  if [ ${#warnings[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}Warnings for: ${BOLD}$(basename "$file")${NC}"
    for warning in "${warnings[@]}"; do
      echo -e "  $warning"
    done
  fi
}

while IFS= read -r file; do
  [ -f "$file" ] || continue
  ((TOTAL_FILES++))

  echo -e "\n${CYAN}Checking: $(basename "$file")${NC}"
  all_passed=true

  if ! check_custom_interfaces "$file"; then
    all_passed=false
  fi

  check_domain_event_structure "$file"

  if [ "$all_passed" = true ]; then
    ((PASSED_FILES++))
    echo -e "  ${GREEN}✓ Base checks passed${NC}"
  fi

done <<< "$EVENT_FILES"

# Summary
echo -e "\n${CYAN}═══════════════════════════════════════${NC}"
echo -e "${BOLD}Summary:${NC}"
echo -e "  Total files checked: $TOTAL_FILES"
echo -e "  Files passed: ${GREEN}$PASSED_FILES${NC}"
echo -e "  Errors found: ${RED}$ERROR_COUNT${NC}"
echo -e "  Warnings found: ${YELLOW}$WARNING_COUNT${NC}"

if [ $ERROR_COUNT -gt 0 ]; then
  echo -e "\n${RED}${BOLD}❌ Domain Events Compliance Check Failed${NC}"
  exit 1
fi

if [ $WARNING_COUNT -gt 0 ]; then
  echo -e "\n${YELLOW}Note: Some warnings were found. Consider addressing them.${NC}"
fi

exit 0
