#!/usr/bin/env bash
set -euo pipefail

SPEC_FILE=${1:-}
TASK_NAME=${2:-}

if [[ -z "$SPEC_FILE" || -z "$TASK_NAME" ]]; then
  echo "Usage: .ai/scripts/check-spec-compliance.sh <spec-file> <task-name>"
  exit 1
fi

if [[ ! -f "$SPEC_FILE" ]]; then
  echo "Spec file not found: $SPEC_FILE"
  exit 1
fi

echo "Checking .NET spec compliance (best-effort): $TASK_NAME"
echo "Spec file: $SPEC_FILE"
echo ""

missing_items=0

extract_names() {
  local component="$1"
  grep -A 40 "\"$component\"" "$SPEC_FILE" \
    | grep -E '"name"' \
    | sed -E 's/.*"name"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/' \
    | sed '/^$/d' \
    | sort -u
}

check_component() {
  local component="$1"
  local suffix="$2"
  local preferred_dir="$3"
  local names

  names=$(extract_names "$component" || true)
  if [[ -z "$names" ]]; then
    echo "No $component defined in spec."
    return
  fi

  echo "$component required by spec:"
  while IFS= read -r name; do
    if [[ -z "$name" ]]; then
      continue
    fi

    local found
    found=""

    if [[ -n "$preferred_dir" && -d "$preferred_dir" ]]; then
      found=$(find "$preferred_dir" -type f -name "${name}${suffix}" 2>/dev/null | head -n 1 || true)
    fi

    if [[ -z "$found" ]]; then
      found=$(find src -type f -name "${name}${suffix}" 2>/dev/null | head -n 1 || true)
    fi

    if [[ -n "$found" ]]; then
      echo "  OK: $name ($found)"
    else
      echo "  MISSING: $name"
      missing_items=$((missing_items + 1))
    fi
  done <<< "$names"

  echo ""
}

echo "Required components from spec:"
check_component "mappers" ".cs" ""
check_component "projections" ".cs" ""
check_component "dataTransferObjects" ".cs" "src/Api/Contracts"

echo "Compliance summary:"
if [[ $missing_items -eq 0 ]]; then
  echo "All listed components appear to exist."
else
  echo "Missing components detected: $missing_items"
fi

exit 0
