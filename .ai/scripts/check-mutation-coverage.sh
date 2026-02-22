#!/usr/bin/env bash

# ============================================
# Mutation Testing Coverage Check Script (.NET)
# ============================================
# Purpose: Automate mutation testing with Stryker.NET and validate thresholds
# Usage: .ai/scripts/check-mutation-coverage.sh [entity-name]
# Example: .ai/scripts/check-mutation-coverage.sh ProductBacklogItem
# ============================================

set -euo pipefail

# Colors for output
RED='[0;31m'
GREEN='[0;32m'
YELLOW='[1;33m'
BLUE='[0;34m'
NC='[0m'

TARGET_MUTATION_COVERAGE=80
TARGET_TEST_STRENGTH=85

print_message() {
  local color=$1
  local message=$2
  echo -e "${color}${message}${NC}"
}

entity_name=${1:-}

PROJECT_ROOT="$(pwd)"
LOG_DIR="$PROJECT_ROOT/.tmp/stryker"

if ! command -v dotnet >/dev/null 2>&1; then
  print_message "$RED" "dotnet CLI not found. Install .NET SDK first."
  exit 1
fi

if [ ! -f "stryker-config.json" ]; then
  print_message "$YELLOW" "stryker-config.json not found."
  echo "Create a config file at repo root. Example:"
  cat << 'EOF'
{
  "stryker-config": {
    "project": "src/Domain/YourDomain.csproj",
    "reporters": ["progress", "cleartext", "html"],
    "thresholds": { "high": 80, "low": 60, "break": 80 },
    "mutate": ["src/Domain/**/*.cs"],
    "exclude": [
      "**/*Generated*.cs",
      "**/*Migrations/*.cs",
      "**/*Dto.cs",
      "**/Contracts/**",
      "**/Events/**"
    ],
    "ignore-methods": [
      "*Contract*",
      "*Ensure*",
      "*Require*",
      "*Invariant*"
    ]
  }
}
EOF
  echo ""
  print_message "$YELLOW" "TODO: refine exclusions for uContract/Contract namespaces."
  exit 1
fi

print_message "$GREEN" "========================================="
print_message "$GREEN" "Mutation Testing Coverage Check (.NET)"
print_message "$GREEN" "Entity: ${entity_name:-ALL}"
print_message "$GREEN" "========================================="

echo ""
print_message "$BLUE" "Verifying tests pass..."
if ! dotnet test; then
  print_message "$RED" "Tests failed. Fix tests before mutation analysis."
  exit 1
fi

# Build mutate argument if entity provided
mutate_arg=""
if [ -n "$entity_name" ]; then
  mutate_arg="--mutate src/Domain/**/${entity_name}.cs"
  print_message "$YELLOW" "Using mutate filter: $mutate_arg"
  echo "TODO: adjust mutate path if domain structure differs."
fi

echo ""
print_message "$BLUE" "Running Stryker.NET baseline..."
mkdir -p "$LOG_DIR"
# Baseline run
if ! dotnet stryker --config-file stryker-config.json $mutate_arg | tee "$LOG_DIR/stryker_baseline.log"; then
  print_message "$RED" "Baseline mutation testing failed."
  exit 1
fi

baseline_score=$(grep -i "Mutation score" "$LOG_DIR/stryker_baseline.log" | grep -o '[0-9]*%' | head -1 | tr -d '%')
baseline_strength=$(grep -i "Test strength" "$LOG_DIR/stryker_baseline.log" | grep -o '[0-9]*%' | head -1 | tr -d '%')

print_message "$YELLOW" "Baseline Metrics:"
echo "  Mutation Score: ${baseline_score:-0}%"
echo "  Test Strength: ${baseline_strength:-0}%"

echo ""
print_message "$BLUE" "Running Stryker.NET final..."
if ! dotnet stryker --config-file stryker-config.json $mutate_arg | tee "$LOG_DIR/stryker_final.log"; then
  print_message "$RED" "Final mutation testing failed."
  exit 1
fi

final_score=$(grep -i "Mutation score" "$LOG_DIR/stryker_final.log" | grep -o '[0-9]*%' | head -1 | tr -d '%')
final_strength=$(grep -i "Test strength" "$LOG_DIR/stryker_final.log" | grep -o '[0-9]*%' | head -1 | tr -d '%')

print_message "$BLUE" "Final Metrics:"
echo "  Mutation Score: ${final_score:-0}% (baseline: ${baseline_score:-0}%)"
echo "  Test Strength: ${final_strength:-0}% (baseline: ${baseline_strength:-0}%)"

echo ""
if [ "${final_score:-0}" -ge "$TARGET_MUTATION_COVERAGE" ]; then
  print_message "$GREEN" "Mutation coverage target met (>=${TARGET_MUTATION_COVERAGE}%)."
else
  print_message "$YELLOW" "Below target mutation coverage (target: ${TARGET_MUTATION_COVERAGE}%)."
fi

if [ "${final_strength:-0}" -ge "$TARGET_TEST_STRENGTH" ]; then
  print_message "$GREEN" "Test strength target met (>=${TARGET_TEST_STRENGTH}%)."
else
  print_message "$YELLOW" "Below target test strength (target: ${TARGET_TEST_STRENGTH}%)."
fi

print_message "$GREEN" "========================================="
print_message "$GREEN" "Mutation testing analysis complete"
print_message "$GREEN" "========================================="
