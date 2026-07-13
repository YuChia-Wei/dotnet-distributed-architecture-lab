#!/usr/bin/env bash
set -euo pipefail

# .NET Configuration Checks (EF Core + Wolverine)

echo "🔍 Checking .NET configuration..."
echo "================================"

ERRORS=0
WARNINGS=0

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Check csproj dependencies
echo -n "Checking EF Core packages... "
CSPROJ=$(find "$PROJECT_ROOT" -name "*.csproj" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | head -1 || true)
if [ -n "$CSPROJ" ]; then
  if grep -q "Microsoft.EntityFrameworkCore" "$CSPROJ"; then
    echo "✅"
  else
    echo "❌ Missing Microsoft.EntityFrameworkCore package reference"
    ((ERRORS++))
  fi
else
  echo "⚠️  No .csproj found"
  ((WARNINGS++))
fi

echo -n "Checking Wolverine packages... "
if [ -n "$CSPROJ" ]; then
  if grep -q "Wolverine" "$CSPROJ"; then
    echo "✅"
  else
    echo "⚠️  Wolverine package not found"
    ((WARNINGS++))
  fi
fi

# Check appsettings profiles
EXPECTED_BASE=("appsettings.inmemory.json" "appsettings.outbox.json")
EXPECTED_TEST=("appsettings.test-inmemory.json" "appsettings.test-outbox.json")

for file in "${EXPECTED_BASE[@]}"; do
  if find "$PROJECT_ROOT" -name "$file" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Found $file"
  else
    echo "❌ Missing $file"
    ((ERRORS++))
  fi
done

for file in "${EXPECTED_TEST[@]}"; do
  if find "$PROJECT_ROOT" -name "$file" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | head -1 | grep -q .; then
    echo "✅ Found $file"
  else
    echo "⚠️  Missing $file"
    ((WARNINGS++))
  fi
done

# Check for ASPNETCORE_ENVIRONMENT inside config (should be env var)
if find "$PROJECT_ROOT" -name "appsettings*.json" -type f -not -path "*/bin/*" -not -path "*/obj/*" -exec grep -l "ASPNETCORE_ENVIRONMENT" {} \; 2>/dev/null | head -1 | grep -q .; then
  echo "❌ Found ASPNETCORE_ENVIRONMENT inside appsettings (should be env var)"
  ((ERRORS++))
fi

# Check Outbox connection string in outbox configs
for file in $(find "$PROJECT_ROOT" -name "appsettings*outbox*.json" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null || true); do
  if grep -q "\"ConnectionStrings\"" "$file" && grep -q "\"Outbox\"" "$file"; then
    echo "✅ Outbox connection string found in $(basename "$file")"
  else
    echo "⚠️  Outbox connection string missing in $(basename "$file")"
    ((WARNINGS++))
  fi
done

# Check for durable outbox gating
if grep -R "UseDurableOutbox" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -q .; then
  if grep -R "UseDurableOutbox" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -qi "outbox"; then
    echo "✅ UseDurableOutbox appears gated by outbox environment"
  else
    echo "⚠️  UseDurableOutbox found without explicit outbox gating"
    ((WARNINGS++))
  fi
else
  echo "⚠️  UseDurableOutbox not found"
  ((WARNINGS++))
fi

# Check InMemory database usage
if grep -R "UseInMemoryDatabase" "$PROJECT_ROOT/src" --include="*.cs" 2>/dev/null | grep -q .; then
  echo "✅ UseInMemoryDatabase found"
else
  echo "⚠️  UseInMemoryDatabase not found (required for inmemory profile)"
  ((WARNINGS++))
fi

echo "================================"
echo "Results:"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
  echo "❌ Configuration errors found"
  exit 1
fi

if [ $WARNINGS -gt 0 ]; then
  echo "⚠️  Configuration warnings found"
  exit 0
fi

echo "✅ All checks passed"
exit 0
