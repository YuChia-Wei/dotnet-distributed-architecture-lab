#!/usr/bin/env bash
set -euo pipefail

"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/check-jpa-projection-config.sh" "$@"
