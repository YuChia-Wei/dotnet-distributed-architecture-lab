#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROMPTS_DIR="$BASE_DIR/.ai/assets/shared"

if [ ! -d "$PROMPTS_DIR" ]; then
  echo -e "${RED}✗ shared asset directory not found: $PROMPTS_DIR${NC}"
  exit 1
fi

# Comma-separated extra forbidden terms can be passed by environment variable.
# Example:
# PORTABILITY_EXTRA_TERMS="CompanyX,DomainY" ./.ai/scripts/check-prompt-portability.sh
EXTRA_TERMS_RAW="${PORTABILITY_EXTRA_TERMS:-}"

FORBIDDEN_TERMS=(
  "AiScrum"
  "MQArchLab"
  "ProductBacklogItem"
  "SaleOrders"
  "SaleProducts"
  "InventoryControl"
)

if [ -n "$EXTRA_TERMS_RAW" ]; then
  IFS=',' read -r -a EXTRA_TERMS <<< "$EXTRA_TERMS_RAW"
  for t in "${EXTRA_TERMS[@]}"; do
    term="$(echo "$t" | xargs)"
    if [ -n "$term" ]; then
      FORBIDDEN_TERMS+=("$term")
    fi
  done
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Shared Asset Portability Check${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Target: $PROMPTS_DIR"
echo ""

ERRORS=0

run_check() {
  local title="$1"
  local pattern="$2"
  local path="$3"
  local output

  echo -e "${YELLOW}${title}${NC}"
  set +e
  output="$(rg -n "$pattern" "$path" 2>/dev/null)"
  local code=$?
  set -e

  if [ $code -eq 1 ]; then
    echo -e "  ${GREEN}✓ No matches${NC}"
    echo ""
    return 0
  fi

  if [ $code -gt 1 ]; then
    echo -e "  ${RED}✗ Search failed (rg exit code: $code)${NC}"
    echo ""
    ERRORS=$((ERRORS + 1))
    return 1
  fi

  echo -e "  ${RED}✗ Found non-portable content:${NC}"
  echo "$output" | sed 's/^/    /'
  echo ""
  ERRORS=$((ERRORS + 1))
  return 1
}

run_check "1) Numeric ADR references are forbidden" "ADR-[0-9]{3}" "$PROMPTS_DIR"
run_check "2) Direct .dev ADR path references are forbidden" "\\.dev/adr" "$PROMPTS_DIR"

if [ ${#FORBIDDEN_TERMS[@]} -gt 0 ]; then
  # Build regex like: term1|term2|term3
  TERM_PATTERN="$(printf "%s|" "${FORBIDDEN_TERMS[@]}")"
  TERM_PATTERN="${TERM_PATTERN%|}"
  run_check "3) Repository-specific terms are forbidden" "$TERM_PATTERN" "$PROMPTS_DIR"
fi

echo -e "${BLUE}Summary${NC}"
if [ "$ERRORS" -eq 0 ]; then
  echo -e "${GREEN}✓ Prompt portability check passed${NC}"
  exit 0
fi

echo -e "${RED}✗ Prompt portability check failed (${ERRORS} group(s) failed)${NC}"
echo -e "${YELLOW}Tip:${NC} Update prompts or expand placeholders in .ai/assets/shared/PROMPT-PORTABILITY-RULES.md"
exit 1


