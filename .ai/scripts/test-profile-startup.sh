#!/usr/bin/env bash
set -euo pipefail

# Profile Startup Test Script (.NET)
# Tests that both InMemory and Outbox profiles can start successfully

echo "========================================="
echo "Profile Startup Test (.NET)"
echo "========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOTNET_PROJECT=${DOTNET_PROJECT:-$(find "$PROJECT_ROOT" -name "*.csproj" -type f -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | head -1 || true)}

HEALTH_ENDPOINT=${HEALTH_ENDPOINT:-/health}
INMEMORY_PORT=${INMEMORY_PORT:-8080}
OUTBOX_PORT=${OUTBOX_PORT:-9090}
STARTUP_WAIT=${STARTUP_WAIT:-15}
LOG_DIR="$PROJECT_ROOT/.tmp/profile-startup"

if [ -z "$DOTNET_PROJECT" ]; then
  echo -e "${YELLOW}⚠ No .csproj found to run${NC}"
  exit 0
fi

if ! command -v dotnet >/dev/null 2>&1; then
  echo -e "${RED}❌ dotnet CLI not found${NC}"
  exit 1
fi

# Function to test profile startup
test_profile() {
  local profile=$1
  local port=$2

  echo -e "\n${YELLOW}Testing $profile profile on port $port...${NC}"

  mkdir -p "$LOG_DIR"
  DOTNET_ENVIRONMENT=$profile ASPNETCORE_ENVIRONMENT=$profile ASPNETCORE_URLS="http://localhost:$port" \
    dotnet run --project "$DOTNET_PROJECT" --no-launch-profile --no-build > "$LOG_DIR/dotnet-${profile}.log" 2>&1 &
  local PID=$!

  echo "Waiting for application to start (PID: $PID)..."
  sleep "$STARTUP_WAIT"

  if ps -p $PID > /dev/null 2>&1; then
    if command -v curl >/dev/null 2>&1; then
      if curl -s -f "http://localhost:$port$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $profile profile started and endpoint is responsive${NC}"
        kill $PID 2>/dev/null || true
        sleep 2
        return 0
      else
        echo -e "${RED}❌ $profile profile started but endpoint not responsive${NC}"
        kill $PID 2>/dev/null || true
        sleep 2
        return 1
      fi
    else
      echo -e "${YELLOW}⚠ curl not available; cannot verify endpoint${NC}"
      kill $PID 2>/dev/null || true
      sleep 2
      return 0
    fi
  else
    echo -e "${RED}❌ $profile profile failed to start${NC}"
    return 1
  fi
}

FAILED=0

if ! test_profile "test-inmemory" "$INMEMORY_PORT"; then
  FAILED=1
fi

if ! test_profile "test-outbox" "$OUTBOX_PORT"; then
  FAILED=1
fi

echo -e "\n========================================="
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ All profiles started successfully!${NC}"
  exit 0
else
  echo -e "${RED}❌ Some profiles failed to start${NC}"
  exit 1
fi
