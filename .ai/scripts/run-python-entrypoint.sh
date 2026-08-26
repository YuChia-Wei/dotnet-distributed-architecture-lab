#!/usr/bin/env sh
# Thin POSIX adapter: Python owns dependency checks and validator semantics.
set -eu
LC_ALL=C
export LC_ALL
entrypoint=${1:?usage: run-python-entrypoint.sh <entrypoint> [args...]}
shift
diagnostic_format=human
if [ "${1:-}" = "--diagnostic-format=json" ]; then diagnostic_format=json; shift; fi
case "$0" in */*) launcher_dir=${0%/*} ;; *) launcher_dir=. ;; esac
script_dir=$(CDPATH= cd -- "$launcher_dir" && pwd)
requirements_path=$(CDPATH= cd -- "$script_dir/../.." && pwd)/requirements.txt
exit_code=1
case "$entrypoint" in .ai/scripts/plan-ai-context-package-apply.py) exit_code=2 ;; esac
supported_python() { "$1" -B -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; }
candidate=${AI_CONTEXT_PYTHON:-}
if [ -n "$candidate" ] && ! supported_python "$candidate"; then candidate=; fi
if [ -z "${candidate:-}" ] && [ -n "${VIRTUAL_ENV:-}" ]; then
  if [ -x "$VIRTUAL_ENV/Scripts/python.exe" ]; then candidate=$VIRTUAL_ENV/Scripts/python.exe; else candidate=$VIRTUAL_ENV/bin/python; fi
  if [ ! -x "$candidate" ] || ! supported_python "$candidate"; then candidate=; fi
fi
if [ -z "${candidate:-}" ] && command -v python >/dev/null 2>&1; then candidate=$(command -v python); if ! supported_python "$candidate"; then candidate=; fi; fi
if [ -z "${candidate:-}" ] && command -v python3 >/dev/null 2>&1; then candidate=$(command -v python3); if ! supported_python "$candidate"; then candidate=; fi; fi
if [ -z "${candidate:-}" ]; then
  old_ifs=$IFS; IFS=:
  for directory in $PATH; do
    [ -n "$directory" ] || directory=.
    for possible in "$directory"/python*; do
      [ -x "$possible" ] || continue
      name=${possible##*/}
      case "$name" in python3.[0-9]*|python3[0-9]*|python[0-9][0-9]*)
        if supported_python "$possible"; then candidate=$possible; break 2; fi ;;
      esac
    done
  done
  IFS=$old_ifs
fi
if [ -z "${candidate:-}" ] && command -v uv >/dev/null 2>&1; then
  candidate=$(uv python find --managed-python --no-python-downloads --offline --no-config --no-project ">=3.11" 2>/dev/null || true)
fi
if [ -n "${candidate:-}" ] && ! supported_python "$candidate"; then candidate=; fi
if [ -z "${candidate:-}" ]; then
  if [ "$diagnostic_format" = json ]; then
    case "$entrypoint" in *'"'*|*'\\'*) safe_entrypoint=invalid-entrypoint ;; *) safe_entrypoint=$entrypoint ;; esac
    printf '{"candidates":[],"entrypoint":"%s","missing_requirements":[],"mutation_started":false,"outcome":"blocked-by-environment","reason_code":"no-ready-python","recovery_command":null,"required_python":">=3.11","requirements_path":"%s","schema_version":"1.0","selected_executable":null,"selected_version":null}\n' "$safe_entrypoint" "$requirements_path"
  else
    printf '%s\n' "Python prerequisite blocked for $entrypoint: no-ready-python. Python >=3.11 is required; see requirements.txt." >&2
  fi
  exit "$exit_code"
fi
AI_CONTEXT_PYTHON=$candidate exec "$candidate" "$script_dir/python_prerequisites.py" --entrypoint "$entrypoint" --diagnostic-format "$diagnostic_format" --delegate -- "$@"
