#!/usr/bin/env bash
set -euo pipefail

# Projection Configuration Checker (.NET)
# Validates that projection/read models are registered in DbContext

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

TOTAL_ISSUES=0
PROJECTIONS_FOUND=0
MISSING_CONFIGS=0

if [ ! -d "$SRC_DIR" ]; then
  echo -e "${YELLOW}⚠ No src directory found: $SRC_DIR${NC}"
  exit 0
fi

echo "================================================"
echo "Projection Configuration Checker (.NET)"
echo "================================================"

echo "Searching for DbContext files..."
DBCONTEXT_FILES=$(find "$SRC_DIR" -name "*DbContext.cs" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true)

if [ -z "$DBCONTEXT_FILES" ]; then
  echo -e "${YELLOW}⚠ No DbContext files found${NC}"
  exit 0
fi

echo -e "${GREEN}✓ Found DbContext files${NC}"

echo "Extracting DbSet registrations..."
DBSET_TYPES=$(grep -R "DbSet<" $DBCONTEXT_FILES 2>/dev/null | sed -E 's/.*DbSet<\s*([^>]+)\s*>.*/\1/' | cut -d" " -f1 | sort -u)

echo "Extracting Entity configuration registrations..."
ENTITY_TYPES=$(grep -R "Entity<" $DBCONTEXT_FILES 2>/dev/null | sed -E 's/.*Entity<\s*([^>]+)\s*>.*/\1/' | cut -d" " -f1 | sort -u)
CONFIG_TYPES=$(grep -R "IEntityTypeConfiguration<" "$SRC_DIR" --include="*.cs" 2>/dev/null | sed -E 's/.*IEntityTypeConfiguration<\s*([^>]+)\s*>.*/\1/' | cut -d" " -f1 | sort -u)
CONFIGURED_TYPES=$(printf "%s\n%s\n%s\n" "$DBSET_TYPES" "$ENTITY_TYPES" "$CONFIG_TYPES" | sort -u)

if [ -z "$DBSET_TYPES" ]; then
  echo -e "${YELLOW}⚠ No DbSet registrations found in DbContext files${NC}"
fi

echo "Searching for projection/read model files..."
PROJECTION_FILES=$(find "$SRC_DIR" -type f \( -name "*Projection.cs" -o -name "*ReadModel.cs" \) -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true)

if [ -z "$PROJECTION_FILES" ]; then
  echo -e "${YELLOW}⚠ No projection/read model files found${NC}"
  exit 0
fi

echo ""
while IFS= read -r projection_file; do
  [ -f "$projection_file" ] || continue
  PROJECTIONS_FOUND=$((PROJECTIONS_FOUND + 1))

  CLASS_NAME=$(basename "$projection_file" .cs)
  echo "Found: $CLASS_NAME"
  echo "  File: $projection_file"

  if echo "$CONFIGURED_TYPES" | grep -q "^$CLASS_NAME$"; then
    echo -e "  ${GREEN}✓ $CLASS_NAME is configured in DbContext/model builder${NC}"
  else
    echo -e "  ${RED}✗ Missing DbSet/model configuration for $CLASS_NAME!${NC}"
    MISSING_CONFIGS=$((MISSING_CONFIGS + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
  fi
  echo ""
done <<< "$PROJECTION_FILES"

echo "Checking DbContext registration in DI..."
if grep -R "AddDbContext" "$SRC_DIR" --include="*.cs" 2>/dev/null | grep -q .; then
  echo -e "${GREEN}✓ Found AddDbContext registration${NC}"
else
  echo -e "${YELLOW}⚠ No AddDbContext registration found${NC}"
fi

echo "================================================"
echo "Summary"
echo "================================================"
echo "Projections found: $PROJECTIONS_FOUND"
echo "Missing DbSet registrations: $MISSING_CONFIGS"

echo ""
if [ $TOTAL_ISSUES -eq 0 ]; then
  echo -e "${GREEN}✓ All projections are configured in DbContext${NC}"
  exit 0
else
  echo -e "${RED}✗ Found $TOTAL_ISSUES configuration issues${NC}"
  echo "Fix: register missing DbSet<T> in the read DbContext."
  exit 1
fi
