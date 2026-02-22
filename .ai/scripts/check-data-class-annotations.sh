#!/usr/bin/env bash
set -euo pipefail

echo "=================================="
echo "Data Class Annotation Check (.NET)"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SEARCH_ROOT="${SEARCH_ROOT:-$PROJECT_ROOT/src}"

ERROR_COUNT=0
WARNING_COUNT=0

if [ ! -d "$SEARCH_ROOT" ]; then
  echo -e "${YELLOW}⚠ No src directory found: $SEARCH_ROOT${NC}"
  exit 0
fi

echo -e "${YELLOW}Scanning for Data classes...${NC}"
DATA_FILES=$(find "$SEARCH_ROOT" -type f -name "*Data.cs" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true)

if [ -z "$DATA_FILES" ]; then
  echo -e "${YELLOW}⚠ No *Data.cs files found${NC}"
  exit 0
fi

while IFS= read -r file; do
  [ -f "$file" ] || continue
  local_errors=0
  local_warnings=0

  echo -n "Checking $(basename "$file")... "

  if grep -q "\[EnumDataType" "$file" 2>/dev/null; then
    echo -e "${RED}ERROR${NC}"
    echo -e "  ${RED}❌ Found [EnumDataType] attribute in:${NC}"
    echo "     $file"
    ((ERROR_COUNT++))
    ((local_errors++))
  fi

  if grep -q "\benum\b" "$file" 2>/dev/null; then
    if [ $local_errors -eq 0 ]; then
      echo -e "${YELLOW}WARNING${NC}"
    fi
    echo -e "  ${YELLOW}⚠ Enum declaration found in Data class file${NC}"
    ((WARNING_COUNT++))
    ((local_warnings++))
  fi

  # Heuristic: property types ending with State/Status/Type/Kind/Category in Data classes
  if grep -E "public\s+[A-Z][A-Za-z0-9_]*(State|Status|Type|Kind|Category)\s+[A-Za-z0-9_]+\s*\{\s*get;\s*set;" "$file" 2>/dev/null | head -1 | grep -q .; then
    if [ $local_errors -eq 0 ] && [ $local_warnings -eq 0 ]; then
      echo -e "${YELLOW}WARNING${NC}"
    fi
    echo -e "  ${YELLOW}⚠ Possible enum-like property detected (consider persisting as string)${NC}"
    grep -E "public\s+[A-Z][A-Za-z0-9_]*(State|Status|Type|Kind|Category)\s+[A-Za-z0-9_]+\s*\{\s*get;\s*set;" "$file" | head -1 | sed 's/^/     /'
    ((WARNING_COUNT++))
    ((local_warnings++))
  fi

  if [ $local_errors -eq 0 ] && [ $local_warnings -eq 0 ]; then
    echo -e "${GREEN}OK${NC}"
  fi

done <<< "$DATA_FILES"

# Summary
echo -e "\n=================================="
echo "Summary"
echo "=================================="

echo -e "Errors: $ERROR_COUNT"
echo -e "Warnings: $WARNING_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
  echo -e "${RED}❌ Data class annotation issues found${NC}"
  echo "Recommendations:"
  echo "1. Do not apply [EnumDataType] to persistence Data classes"
  echo "2. Persist enum-like values as string (or dedicated value object)"
  exit 1
fi

echo -e "${GREEN}✅ Data class checks complete${NC}"
exit 0
