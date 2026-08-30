#!/bin/bash

# ====================================================================
# Comprehensive Project Check Script (.NET)
# 
# Purpose: Execute one declared validation profile and retain complete logs.
# Usage: ./check-all.sh [--profile <name> | --quick | --full | --critical] [--verbose]
# ====================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# The registry is intentionally shell-native: the runner must remain usable in
# a minimal downstream Git Bash environment before Python prerequisites can be
# established.  It owns membership; this runner only owns execution.
declare -ag PROFILE_IDS=()
declare -A PROFILE_PURPOSE=()
declare -A PROFILE_BUDGET=()
declare -A PROFILE_ENFORCEMENT=()
declare -ag CHECK_IDS=()
declare -A CHECK_ID_BY_DESCRIPTION=()
declare -A CHECK_DESCRIPTION=()
declare -A CHECK_OWNER=()
declare -A CHECK_ENFORCEMENT=()
declare -A CHECK_TAGS=()
declare -A CHECK_PROFILES=()
declare -A CHECK_INPUT_PATHS=()
declare -A CHECK_DEPENDS=()
declare -A CHECK_ENVIRONMENT=()
declare -A CHECK_TIMEOUT=()
declare -A CHECK_RESOURCE_CLASS=()
declare -A CHECK_CACHE_POLICY=()
declare -A CHECK_DISPOSITION=()
declare -A CHECK_COMMAND=()
declare -A CHECK_APPLICABILITY=()
declare -A DISCOVERED_CHECK_IDS=()
declare -A DEPENDENCY_VALIDATION_STATE=()
declare -ag DEPENDENCY_VALIDATION_STACK=()
declare -A SELECTED_CHECK_IDS=()
declare -ag SELECTED_CHECK_ORDER=()
declare -A SELECTION_REASON_BY_ID=()
declare -A CHANGED_PATHS=()
declare -A IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID=()
CHANGED_PATHS_DIGEST=unavailable
SELECTION_MODE=full
SELECTION_ESCALATION_REASON=
SELECTION_BASE_SHA=
SELECTION_HEAD_SHA=
IMMUTABLE_HISTORY_SOURCE_CONTEXT=false
IMMUTABLE_HISTORY_FORCE_FULL=false
IMMUTABLE_HISTORY_MODE=downstream-target-local
IMMUTABLE_HISTORY_REASON=not-source-repository
IMMUTABLE_HISTORY_FINGERPRINT=
IMMUTABLE_HISTORY_RECEIPT_SOURCE=
IMMUTABLE_HISTORY_PREPARATION_ACTIVE=false
IMMUTABLE_HISTORY_PREPARATION_LOG=
IMMUTABLE_HISTORY_PREPARATION_RESULT=

register_profile() {
    local id=$1 purpose=$2 budget=$3 enforcement=$4
    PROFILE_IDS+=("$id")
    PROFILE_PURPOSE["$id"]=$purpose
    PROFILE_BUDGET["$id"]=$budget
    PROFILE_ENFORCEMENT["$id"]=$enforcement
}

register_check() {
    local id=$1 description=$2 enforcement=$3 tags=$4 profiles=$5 input_paths=$6
    local depends_on=$7 environment_capabilities=$8 timeout_seconds=$9
    local resource_class=${10} cache_policy=${11} disposition=${12}
    local command_or_callable=${13} applicability=${14}
    CHECK_IDS+=("$id")
    CHECK_ID_BY_DESCRIPTION["$description"]=$id
    CHECK_DESCRIPTION["$id"]=$description
    CHECK_OWNER["$id"]=ai-context-governance
    CHECK_ENFORCEMENT["$id"]=$enforcement
    CHECK_TAGS["$id"]=$tags
    CHECK_PROFILES["$id"]=$profiles
    CHECK_INPUT_PATHS["$id"]=$input_paths
    CHECK_DEPENDS["$id"]=$depends_on
    CHECK_ENVIRONMENT["$id"]=$environment_capabilities
    CHECK_TIMEOUT["$id"]=$timeout_seconds
    CHECK_RESOURCE_CLASS["$id"]=$resource_class
    CHECK_CACHE_POLICY["$id"]=$cache_policy
    CHECK_DISPOSITION["$id"]=$disposition
    CHECK_COMMAND["$id"]=$command_or_callable
    CHECK_APPLICABILITY["$id"]=$applicability
}

REGISTRY_PATH="$SCRIPT_DIR/validation-profile-registry.sh"
if [ ! -r "$REGISTRY_PATH" ]; then
    echo "Validation profile registry is missing: $REGISTRY_PATH" >&2
    exit 2
fi
# shellcheck source=validation-profile-registry.sh
source "$REGISTRY_PATH"

registry_has_profile() {
    local expected=$1 profile
    for profile in "${PROFILE_IDS[@]}"; do
        [ "$profile" = "$expected" ] && return 0
    done
    return 1
}

profiles_include() {
    local profiles=$1 expected=$2 profile
    for profile in $profiles; do
        [ "$profile" = "$expected" ] && return 0
    done
    return 1
}

report_dependency_cycle() {
    local repeated=$1 index start=-1 cycle=
    for index in "${!DEPENDENCY_VALIDATION_STACK[@]}"; do
        if [ "${DEPENDENCY_VALIDATION_STACK[$index]}" = "$repeated" ]; then
            start=$index
            break
        fi
    done
    if [ "$start" -lt 0 ]; then
        echo "Dependency cycle detected: $repeated -> $repeated" >&2
        return 1
    fi
    for ((index = start; index < ${#DEPENDENCY_VALIDATION_STACK[@]}; index++)); do
        [ -z "$cycle" ] || cycle="$cycle -> "
        cycle="$cycle${DEPENDENCY_VALIDATION_STACK[$index]}"
    done
    echo "Dependency cycle detected: $cycle -> $repeated" >&2
    return 1
}

validate_dependency_graph_node() {
    local id=$1 dependency last_index
    case "${DEPENDENCY_VALIDATION_STATE[$id]:-unvisited}" in
        visited) return 0 ;;
        visiting) report_dependency_cycle "$id"; return 1 ;;
    esac
    DEPENDENCY_VALIDATION_STATE["$id"]=visiting
    DEPENDENCY_VALIDATION_STACK+=("$id")
    for dependency in ${CHECK_DEPENDS[$id]}; do
        validate_dependency_graph_node "$dependency" || return 1
    done
    last_index=$((${#DEPENDENCY_VALIDATION_STACK[@]} - 1))
    unset "DEPENDENCY_VALIDATION_STACK[$last_index]"
    DEPENDENCY_VALIDATION_STATE["$id"]=visited
}

validate_profile_registry() {
    local profile id dependency
    for profile in fast pr release closeout nightly-full; do
        if ! registry_has_profile "$profile" || [ -z "${PROFILE_PURPOSE[$profile]:-}" ] ||
            { [ "${PROFILE_ENFORCEMENT[$profile]:-}" != report-and-warn ] &&
              [ "${PROFILE_ENFORCEMENT[$profile]:-}" != measure-first ]; }; then
            echo "Invalid validation profile registry entry: $profile" >&2
            return 1
        fi
    done
    for id in "${CHECK_IDS[@]}"; do
        if [ -z "$id" ] || [ -z "${CHECK_DESCRIPTION[$id]:-}" ] ||
            [ -z "${CHECK_OWNER[$id]:-}" ] || [ -z "${CHECK_PROFILES[$id]:-}" ] ||
            [ -z "${CHECK_INPUT_PATHS[$id]:-}" ] || [ -z "${CHECK_ENVIRONMENT[$id]:-}" ] ||
            [ -z "${CHECK_RESOURCE_CLASS[$id]:-}" ] || [ -z "${CHECK_CACHE_POLICY[$id]:-}" ] ||
            [ -z "${CHECK_DISPOSITION[$id]:-}" ] || [ -z "${CHECK_COMMAND[$id]:-}" ] ||
            [ -z "${CHECK_APPLICABILITY[$id]:-}" ]; then
            echo "Incomplete validation check registry entry: $id" >&2
            return 1
        fi
        for profile in ${CHECK_PROFILES[$id]}; do
            registry_has_profile "$profile" || {
                echo "Unknown profile '$profile' in validation check '$id'" >&2
                return 1
            }
        done
        for dependency in ${CHECK_DEPENDS[$id]}; do
            [ -n "${CHECK_DESCRIPTION[$dependency]:-}" ] || {
                echo "Unknown dependency '$dependency' in validation check '$id'" >&2
                return 1
            }
        done
    done
    DEPENDENCY_VALIDATION_STATE=()
    DEPENDENCY_VALIDATION_STACK=()
    for id in "${CHECK_IDS[@]}"; do
        validate_dependency_graph_node "$id" || return 1
    done
}

reset_selection_state() {
    DISCOVERED_CHECK_IDS=()
    SELECTED_CHECK_IDS=()
    SELECTED_CHECK_ORDER=()
    SELECTION_REASON_BY_ID=()
}

discover_selection_root() {
    local id=$1 reason=$2
    DISCOVERED_CHECK_IDS["$id"]=discovered
    [ -n "${SELECTION_REASON_BY_ID[$id]:-}" ] || SELECTION_REASON_BY_ID["$id"]=$reason
}

select_with_dependencies() {
    local id=$1 chain=${2:-$1} dependency
    [ -n "${CHECK_DESCRIPTION[$id]:-}" ] || return 1
    [ -n "${SELECTED_CHECK_IDS[$id]:-}" ] && return 0
    for dependency in ${CHECK_DEPENDS[$id]}; do
        select_with_dependencies "$dependency" "$chain -> $dependency" || return 1
    done
    SELECTED_CHECK_IDS["$id"]=selected
    SELECTED_CHECK_ORDER+=("$id")
    [ -n "${SELECTION_REASON_BY_ID[$id]:-}" ] || SELECTION_REASON_BY_ID["$id"]="dependency-chain:$chain"
}

expand_discovered_roots() {
    local id
    for id in "${CHECK_IDS[@]}"; do
        [ -n "${DISCOVERED_CHECK_IDS[$id]:-}" ] || continue
        select_with_dependencies "$id" "$id" || return 1
    done
}

prepare_full_profile_selection() {
    local reason=$1 id
    SELECTION_ESCALATION_REASON=${reason:-profile-full}
    if [ -n "$reason" ]; then
        SELECTION_MODE=escalated
    else
        SELECTION_MODE=full
    fi
    reset_selection_state
    for id in "${CHECK_IDS[@]}"; do
        if profiles_include "${CHECK_PROFILES[$id]}" "$PROFILE"; then
            discover_selection_root "$id" "profile-inclusion:$PROFILE${reason:+;escalation:$reason}"
        fi
    done
    expand_discovered_roots
}

path_is_safe() {
    local path=$1 segment old_ifs
    case "$path" in
        ''|/*|*\\*|*'//'*) return 1 ;;
    esac
    [[ "$path" =~ ^[A-Za-z]: ]] && return 1
    old_ifs=$IFS
    IFS=/
    for segment in $path; do
        [ -n "$segment" ] && [ "$segment" != . ] && [ "$segment" != .. ] || { IFS=$old_ifs; return 1; }
    done
    IFS=$old_ifs
    return 0
}

sha256_regular_file() {
    local output digest
    output=$(sha256sum -- "$1") || return 1
    digest=${output%%[[:space:]]*}
    digest=${digest#\\}
    [[ "$digest" =~ ^[0-9a-f]{64}$ ]] || return 1
    printf '%s\n' "$digest"
}

repo_relative_artifact() {
    local input_path normalized_root normalized_path relative
    input_path=$1
    normalized_root=$PROJECT_ROOT
    normalized_path=$input_path
    if command -v cygpath >/dev/null 2>&1; then
        normalized_root=$(cygpath -u "$PROJECT_ROOT") || return 1
        normalized_path=$(cygpath -u "$input_path") || return 1
    fi
    relative=$(realpath -m --relative-to="$normalized_root" "$normalized_path") || return 1
    path_is_safe "$relative" || return 1
    printf '%s\n' "$relative"
}

add_changed_path() {
    local path=$1
    path_is_safe "$path" || return 1
    CHANGED_PATHS["$path"]=changed
}

input_owns_path() {
    local path=$1 token
    for token in $2; do
        case "$token" in
            *'**'|*'?'|*'['*) [[ "$path" == $token ]] && return 0 ;;
            *) [[ "$path" == "$token" || "$path" == "$token/"* ]] && return 0 ;;
        esac
    done
    return 1
}

is_global_invalidator() {
    case "$1" in
        .ai/scripts/validation-profile-registry.sh|.ai/scripts/check-all.sh|.ai/scripts/validation-evidence.py|\
        .ai/scripts/validation_process_supervisor.py|\
        .ai/scripts/validate-immutable-history.py|.ai/distribution/validation/immutable-history-validation.yaml|\
        .ai/scripts/validate-workflow-artifacts.py|.ai/scripts/validate-assessment-artifacts.py|\
        .ai/scripts/validate-ai-context-versions.py|.dev/standards/WORKFLOW-ARTIFACT-POLICY.md|\
        .dev/standards/ASSESSMENT-ARTIFACT-POLICY.md|.dev/standards/AI-CONTEXT-VERSION-POLICY.md|\
        .github/workflows/*)
            return 0 ;;
    esac
    return 1
}

collect_changed_paths() {
    local base=$1 head=$2 temporary status first second
    temporary=$(mktemp) || return 1
    if ! git diff --name-status --find-renames --find-copies -z "$base" "$head" > "$temporary"; then
        rm -f "$temporary"
        return 1
    fi
    while IFS= read -r -d '' status; do
        case "$status" in
            R*|C*)
                IFS= read -r -d '' first && IFS= read -r -d '' second || { rm -f "$temporary"; return 1; }
                add_changed_path "$first" && add_changed_path "$second" || { rm -f "$temporary"; return 1; }
                ;;
            *)
                IFS= read -r -d '' first || { rm -f "$temporary"; return 1; }
                add_changed_path "$first" || { rm -f "$temporary"; return 1; }
                ;;
        esac
    done < "$temporary"
    rm -f "$temporary"
    CHANGED_PATHS_DIGEST=$(printf '%s\n' "${!CHANGED_PATHS[@]}" | LC_ALL=C sort | sha256sum | awk '{print $1}')
    CHANGED_PATHS_DIGEST=${CHANGED_PATHS_DIGEST:-unavailable}
}

prepare_changed_path_selection() {
    local base=$1 head=$2 path id owned
    reset_selection_state
    if ! collect_changed_paths "$base" "$head"; then
        SELECTION_ESCALATION_REASON=changed-path-diff-unavailable
        prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        return
    fi
    while IFS= read -r path; do
        [ -n "$path" ] || continue
        if is_global_invalidator "$path"; then
            SELECTION_ESCALATION_REASON=global-invalidator
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
            return
        fi
        owned=false
        for id in "${CHECK_IDS[@]}"; do
            if input_owns_path "$path" "${CHECK_INPUT_PATHS[$id]}"; then
                owned=true
                if profiles_include "${CHECK_PROFILES[$id]}" "$PROFILE"; then
                    discover_selection_root "$id" "direct-path-match:$path"
                fi
            fi
        done
        if [ "$owned" = false ]; then
            SELECTION_ESCALATION_REASON=unknown-impact-path
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
            return
        fi
    done < <(printf '%s\n' "${!CHANGED_PATHS[@]}" | LC_ALL=C sort)
    expand_discovered_roots || return 1
    SELECTION_MODE=changed-path
}

prepare_profile_selection() {
    local current_head explicit_base explicit_head implicit_base repository_status
    current_head=$(git rev-parse --verify 'HEAD^{commit}' 2>/dev/null) || return 1
    SELECTION_BASE_SHA=$current_head
    SELECTION_HEAD_SHA=$current_head
    if [ -n "$BASE_SHA" ] || [ -n "$HEAD_SHA" ]; then
        if [ -z "$BASE_SHA" ] || [ -z "$HEAD_SHA" ] ||
            ! explicit_base=$(git rev-parse --verify "${BASE_SHA}^{commit}" 2>/dev/null) ||
            ! explicit_head=$(git rev-parse --verify "${HEAD_SHA}^{commit}" 2>/dev/null); then
            SELECTION_ESCALATION_REASON=comparison-base-unavailable
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        elif [ "$explicit_head" != "$current_head" ]; then
            SELECTION_BASE_SHA=$explicit_base
            SELECTION_ESCALATION_REASON=comparison-head-mismatch
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        elif ! git merge-base --is-ancestor "$explicit_base" "$current_head" >/dev/null 2>&1; then
            SELECTION_BASE_SHA=$explicit_base
            SELECTION_ESCALATION_REASON=comparison-base-not-ancestor
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        elif ! repository_status=$(git status --porcelain --untracked-files=normal 2>/dev/null); then
            SELECTION_BASE_SHA=$explicit_base
            SELECTION_ESCALATION_REASON=selection-status-unavailable
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        elif [ -n "$repository_status" ]; then
            SELECTION_BASE_SHA=$explicit_base
            SELECTION_ESCALATION_REASON=dirty-repository-selection
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        else
            SELECTION_BASE_SHA=$explicit_base
            prepare_changed_path_selection "$explicit_base" "$current_head"
        fi
    elif implicit_base=$(git merge-base HEAD '@{upstream}' 2>/dev/null); then
        SELECTION_BASE_SHA=$implicit_base
        if ! repository_status=$(git status --porcelain --untracked-files=normal 2>/dev/null); then
            SELECTION_ESCALATION_REASON=selection-status-unavailable
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        elif [ -n "$repository_status" ]; then
            SELECTION_ESCALATION_REASON=dirty-repository-selection
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        else
            prepare_changed_path_selection "$implicit_base" "$current_head"
        fi
    else
        SELECTION_ESCALATION_REASON=comparison-base-unavailable
        prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
    fi
    for id in "${CHECK_IDS[@]}"; do
        [ -n "${SELECTION_REASON_BY_ID[$id]:-}" ] || SELECTION_REASON_BY_ID["$id"]=not-selected-unmatched-input-contract
    done
}

verify_selection_admission() {
    local observed_head repository_status
    observed_head=$(git rev-parse --verify 'HEAD^{commit}' 2>/dev/null) || return 1
    [ "$observed_head" = "$SELECTION_HEAD_SHA" ] || return 1
    if [ "$SELECTION_MODE" = changed-path ]; then
        repository_status=$(git status --porcelain --untracked-files=normal 2>/dev/null) || return 1
        [ -z "$repository_status" ] || return 1
    fi
}

check_is_selected() {
    local description=$1
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    [ -n "$id" ] && [ -n "${SELECTED_CHECK_IDS[$id]:-}" ]
}

show_usage() {
    cat <<'EOF'
Usage: ./check-all.sh [--profile <fast|pr|release|closeout|nightly-full>] [--base <sha> --head <sha>] [--verbose]

Profiles:
  fast          Local development feedback (30 seconds, report-and-warn)
  pr            Pull-request integration (90 seconds, report-and-warn)
  release       Immutable candidate validation (measure-first)
  closeout      Post-publication administrative verification (120 seconds)
  nightly-full  Full history and compatibility regression (measure-first)

Compatibility aliases (deprecated):
  --quick       --profile pr
  --critical    --profile release
  --full        --profile nightly-full (the default)
EOF
}

# Parse arguments strictly so an unknown flag cannot silently select a gate.
PROFILE=nightly-full
VERBOSE=false
PROFILE_EXPLICIT=false
BASE_SHA=
HEAD_SHA=
while [ "$#" -gt 0 ]; do
    case "$1" in
        --profile)
            [ "$#" -ge 2 ] && [ "$PROFILE_EXPLICIT" = false ] || { show_usage >&2; exit 2; }
            PROFILE=$2
            PROFILE_EXPLICIT=true
            shift 2
            ;;
        --quick)
            [ "$PROFILE_EXPLICIT" = false ] || { show_usage >&2; exit 2; }
            PROFILE=pr
            PROFILE_EXPLICIT=true
            shift
            ;;
        --critical)
            [ "$PROFILE_EXPLICIT" = false ] || { show_usage >&2; exit 2; }
            PROFILE=release
            PROFILE_EXPLICIT=true
            shift
            ;;
        --full)
            [ "$PROFILE_EXPLICIT" = false ] || { show_usage >&2; exit 2; }
            PROFILE=nightly-full
            PROFILE_EXPLICIT=true
            shift
            ;;
        --verbose)
            [ "$VERBOSE" = false ] || { show_usage >&2; exit 2; }
            VERBOSE=true
            shift
            ;;
        --base)
            [ "$#" -ge 2 ] && [ -z "$BASE_SHA" ] || { show_usage >&2; exit 2; }
            BASE_SHA=$2
            shift 2
            ;;
        --head)
            [ "$#" -ge 2 ] && [ -z "$HEAD_SHA" ] || { show_usage >&2; exit 2; }
            HEAD_SHA=$2
            shift 2
            ;;
        --help|-h)
            [ "$#" -eq 1 ] || { show_usage >&2; exit 2; }
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            show_usage >&2
            exit 2
            ;;
    esac
done

if ! registry_has_profile "$PROFILE" || ! validate_profile_registry || ! prepare_profile_selection; then
    exit 2
fi

# Resolve the existing Python contract across Windows Git Bash and POSIX hosts.
# Keep literal `python ...` command declarations below for shell-manifest parity.
resolve_python() {
    local candidate directory possible name old_ifs
    if [ -n "${AI_CONTEXT_PYTHON:-}" ]; then
        if command -v "$AI_CONTEXT_PYTHON" >/dev/null 2>&1 &&
            "$AI_CONTEXT_PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
            command -v "$AI_CONTEXT_PYTHON"
            return 0
        fi
        return 1
    fi

    if [ -n "${VIRTUAL_ENV:-}" ]; then
        if [ -x "$VIRTUAL_ENV/Scripts/python.exe" ]; then
            candidate=$VIRTUAL_ENV/Scripts/python.exe
        else
            candidate=$VIRTUAL_ENV/bin/python
        fi
        if [ -x "$candidate" ] &&
            "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
            printf '%s\n' "$candidate"
            return 0
        fi
    fi

    for candidate in python python3; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
            command -v "$candidate"
            return 0
        fi
    done

    old_ifs=$IFS
    IFS=:
    for directory in $PATH; do
        [ -n "$directory" ] || directory=.
        for possible in "$directory"/python*; do
            [ -x "$possible" ] || continue
            name=${possible##*/}
            case "$name" in
                python3.[0-9]*|python3[0-9]*|python[0-9][0-9]*)
                    if "$possible" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
                        IFS=$old_ifs
                        printf '%s\n' "$possible"
                        return 0
                    fi
                    ;;
            esac
        done
    done
    IFS=$old_ifs

    if command -v uv >/dev/null 2>&1; then
        candidate=$(uv python find --managed-python --no-python-downloads --offline --no-config --no-project ">=3.11" 2>/dev/null || true)
        if [ -n "$candidate" ] &&
            "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
            printf '%s\n' "$candidate"
            return 0
        fi
    fi
    return 1
}

if ! PYTHON_EXECUTABLE="$(resolve_python)"; then
    echo -e "${YELLOW}⊘ BLOCKED-BY-ENVIRONMENT${NC}: Python 3.11 or newer is required. Install source dependencies from requirements.txt or set AI_CONTEXT_PYTHON to a usable interpreter." >&2
    exit 3
fi
export AI_CONTEXT_PYTHON="$PYTHON_EXECUTABLE"
export PYTHON_EXECUTABLE

python() {
    "$PYTHON_EXECUTABLE" "$@"
}

# Establish one retained invocation root and immutable source snapshot before
# any validation child can launch. Fast/PR remain usable on a stable dirty
# tree; release/nightly-full require a clean, operation-free commit.
TOTAL_ELAPSED_START=$SECONDS
EVIDENCE_HELPER="$SCRIPT_DIR/validation-evidence.py"
LOG_BASE="${AI_CONTEXT_VALIDATION_LOG_DIR:-$PROJECT_ROOT/artifacts/validation}"
INVOCATION_ID="${AI_CONTEXT_VALIDATION_INVOCATION_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
case "$INVOCATION_ID" in
    ''|*[!A-Za-z0-9._-]*)
        echo "Invalid validation invocation id: $INVOCATION_ID" >&2
        exit 2
        ;;
esac
LOG_DIR="$LOG_BASE/$INVOCATION_ID"
if ! mkdir -p "$LOG_BASE" 2>/dev/null || ! mkdir "$LOG_DIR" 2>/dev/null; then
    echo "Validation invocation evidence directory is not uniquely creatable: $INVOCATION_ID" >&2
    exit 2
fi
export AI_CONTEXT_VALIDATION_RUN_LOG_DIR="$LOG_DIR"
EVIDENCE_SNAPSHOT="$LOG_DIR/repository-snapshot-pre.json"
VALIDATION_ABORTED=false
VALIDATION_ABORT_REASON=
RUNNER_CANCELLED_BY_SIGNAL=false
ACTIVE_SUPERVISOR_PID=
export AI_CONTEXT_VALIDATION_RUNNER_PID=$$

request_validation_cancellation() {
    local signal_name=$1
    VALIDATION_ABORTED=true
    RUNNER_CANCELLED_BY_SIGNAL=true
    VALIDATION_ABORT_REASON="runner-signal-$signal_name"
    if [ -n "$ACTIVE_SUPERVISOR_PID" ]; then
        kill -TERM "$ACTIVE_SUPERVISOR_PID" 2>/dev/null || true
    fi
}

cleanup_active_supervisor() {
    if [ -n "$ACTIVE_SUPERVISOR_PID" ]; then
        kill -TERM "$ACTIVE_SUPERVISOR_PID" 2>/dev/null || true
        wait "$ACTIVE_SUPERVISOR_PID" 2>/dev/null || true
    fi
}

remove_owned_terminal_publication() {
    local owns_final=false
    if [ -n "${EVIDENCE_STAGED_MANIFEST:-}" ] &&
        [ -n "${EVIDENCE_SEALED_MANIFEST:-}" ] &&
        [ -e "$EVIDENCE_STAGED_MANIFEST" ] &&
        [ -e "$EVIDENCE_SEALED_MANIFEST" ] &&
        [ "$EVIDENCE_STAGED_MANIFEST" -ef "$EVIDENCE_SEALED_MANIFEST" ]; then
        owns_final=true
    elif [ "${EVIDENCE_SEAL_PUBLISHED:-false}" = true ]; then
        owns_final=true
    fi
    if [ "$owns_final" = true ]; then
        rm -f -- "$EVIDENCE_SEALED_MANIFEST"
    fi
    [ -z "${EVIDENCE_STAGED_MANIFEST:-}" ] || rm -f -- "$EVIDENCE_STAGED_MANIFEST"
    EVIDENCE_SEAL_PUBLISHED=false
}

cleanup_validation_runner() {
    cleanup_active_supervisor
    if [ "${RUNNER_CANCELLED_BY_SIGNAL:-false}" = true ]; then
        remove_owned_terminal_publication
    fi
}

trap 'request_validation_cancellation INT' INT
trap 'request_validation_cancellation TERM' TERM
trap 'request_validation_cancellation HUP' HUP
trap cleanup_validation_runner EXIT

run_managed_evidence_cli() {
    local launch_mode=$1 supervisor_pid supervisor_rc
    shift
    case "$launch_mode" in
        validator) [ "$VALIDATION_ABORTED" != true ] || return 130 ;;
        control) [ "$RUNNER_CANCELLED_BY_SIGNAL" != true ] || return 130 ;;
        *) return 2 ;;
    esac
    python .ai/scripts/validation-evidence.py "$@" &
    supervisor_pid=$!
    ACTIVE_SUPERVISOR_PID=$supervisor_pid
    if [ "$RUNNER_CANCELLED_BY_SIGNAL" = true ]; then
        kill -TERM "$supervisor_pid" 2>/dev/null || true
    fi
    while true; do
        wait "$supervisor_pid"
        supervisor_rc=$?
        if kill -0 "$supervisor_pid" 2>/dev/null; then
            [ "$RUNNER_CANCELLED_BY_SIGNAL" != true ] || kill -TERM "$supervisor_pid" 2>/dev/null || true
            continue
        fi
        break
    done
    ACTIVE_SUPERVISOR_PID=
    return "$supervisor_rc"
}

run_supervisor_cli() {
    run_managed_evidence_cli validator "$@"
}

run_control_supervisor_cli() {
    run_managed_evidence_cli control "$@"
}

declare -A EVIDENCE_CONTROL_RESULT_BY_ROLE=()
EVIDENCE_BOOTSTRAP_SNAPSHOT_LOG="$LOG_DIR/control-bootstrap-snapshot.log"
EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT="$LOG_DIR/control-bootstrap-snapshot.result.json"
if ! EVIDENCE_SNAPSHOT_REF=$(repo_relative_artifact "$EVIDENCE_SNAPSHOT"); then
    echo "Validation snapshot path is outside the repository evidence boundary." >&2
    exit 2
fi
bootstrap_supervise_arguments=(
    supervise
    --repo "$PROJECT_ROOT"
    --bootstrap-snapshot-output "$EVIDENCE_SNAPSHOT_REF"
    --bootstrap-profile "$PROFILE"
    --bootstrap-python "$PYTHON_EXECUTABLE"
    --log-path "$EVIDENCE_BOOTSTRAP_SNAPSHOT_LOG"
    --result-path "$EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT"
    --timeout-seconds 60
    --cwd-ref .
)
if [ "$PROFILE" = release ] || [ "$PROFILE" = nightly-full ]; then
    bootstrap_supervise_arguments+=(--bootstrap-require-clean)
fi
bootstrap_supervise_arguments+=(
    --
    "$PYTHON_EXECUTABLE"
    .ai/scripts/validation-evidence.py
    verify-snapshot
    --repo .
    --snapshot "$EVIDENCE_SNAPSHOT_REF"
)
set +e
run_control_supervisor_cli "${bootstrap_supervise_arguments[@]}"
bootstrap_rc=$?
set -e
bootstrap_verified=
if [ -f "$EVIDENCE_SNAPSHOT" ] && [ -f "$EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT" ]; then
    bootstrap_verified=$(python .ai/scripts/validation-evidence.py verify-supervision-result \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --result-path "$EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT" 2>/dev/null) || bootstrap_verified=
fi
IFS=$'\t' read -r bootstrap_status bootstrap_launched bootstrap_exit bootstrap_extra \
    <<< "$bootstrap_verified"
if [ "$bootstrap_rc" -ne 0 ] || [ "$bootstrap_status" != completed ] ||
    [ "$bootstrap_launched" != true ] || [ "$bootstrap_exit" != 0 ] ||
    [ -n "$bootstrap_extra" ]; then
    echo "Validation repository snapshot admission failed under process-tree supervision; no checks were launched." >&2
    echo "admission-evidence: $EVIDENCE_SNAPSHOT" >&2
    echo "admission-supervision: $EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT" >&2
    exit 2
fi
EVIDENCE_CONTROL_RESULT_BY_ROLE["bootstrap-snapshot"]=$EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT
if ! verify_selection_admission; then
    echo "Validation selection changed before repository snapshot admission; no checks were launched." >&2
    echo "admission-evidence: $EVIDENCE_SNAPSHOT" >&2
    echo "admission-supervision: $EVIDENCE_BOOTSTRAP_SNAPSHOT_RESULT" >&2
    exit 2
fi

IMMUTABLE_HISTORY_HELPER="$SCRIPT_DIR/validate-immutable-history.py"
IMMUTABLE_HISTORY_CONTRACT="$PROJECT_ROOT/.ai/distribution/validation/immutable-history-validation.yaml"
IMMUTABLE_HISTORY_RECEIPT="$PROJECT_ROOT/.ai/distribution/validation/immutable-history-receipt.yaml"

immutable_history_source_context_available() {
    [ -d "$PROJECT_ROOT/.dev/workflows" ] &&
        [ -d "$PROJECT_ROOT/.dev/assessments" ] &&
        [ -d "$PROJECT_ROOT/.dev/releases" ] &&
        [ -d "$PROJECT_ROOT/.ai/distribution" ]
}

immutable_history_check_is_protected() {
    case "$1" in
        workflow-artifacts|assessment-artifacts|source-ai-context-version) return 0 ;;
    esac
    return 1
}

select_immutable_history_check() {
    local id=$1 reason=$2
    SELECTION_REASON_BY_ID["$id"]="explicit-request:$reason"
    select_with_dependencies "$id" "$id" || return 1
}

select_immutable_history_full_checks() {
    local reason="immutable-history-full-required:$1" id
    IMMUTABLE_HISTORY_FORCE_FULL=true
    IMMUTABLE_HISTORY_MODE=full-required
    IMMUTABLE_HISTORY_REASON=$1
    for id in workflow-artifacts assessment-artifacts source-ai-context-version; do
        select_immutable_history_check "$id" "$reason" || return 1
    done
}

prepare_immutable_history_layer() {
    local rc outcome reason source_revision source_tree receipt_commit reusable_ids extra id preparation_line
    local -a preparation_lines=()
    if ! immutable_history_source_context_available; then
        return 0
    fi
    IMMUTABLE_HISTORY_SOURCE_CONTEXT=true

    case "$PROFILE" in
        fast|pr|release|nightly-full)
            select_immutable_history_check workflow-artifacts immutable-history-routine-proof || return 1
            select_immutable_history_check assessment-artifacts immutable-history-routine-proof || return 1
            select_immutable_history_check source-ai-context-version immutable-history-routine-proof || return 1
            ;;
        *)
            return 0
            ;;
    esac

    if [ ! -f "$IMMUTABLE_HISTORY_HELPER" ] || [ ! -f "$IMMUTABLE_HISTORY_CONTRACT" ]; then
        echo "Immutable history verifier or contract is missing; supervised preparation cannot run." >&2
        return 1
    fi

    IMMUTABLE_HISTORY_PREPARATION_LOG="$LOG_DIR/immutable-history-preparation.log"
    IMMUTABLE_HISTORY_PREPARATION_RESULT="$LOG_DIR/immutable-history-preparation.result.json"
    set +e
    run_supervisor_cli supervise \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --log-path "$IMMUTABLE_HISTORY_PREPARATION_LOG" \
        --result-path "$IMMUTABLE_HISTORY_PREPARATION_RESULT" \
        --timeout-seconds 30 \
        --accepted-child-exit-code 10 \
        --cwd-ref . \
        -- "$PYTHON_EXECUTABLE" .ai/scripts/validate-immutable-history.py verify \
        --repo . \
        --profile "$PROFILE" \
        --output-format tsv
    rc=$?
    set -e
    IMMUTABLE_HISTORY_PREPARATION_ACTIVE=true
    if [ ! -f "$IMMUTABLE_HISTORY_PREPARATION_LOG" ] ||
        [ ! -f "$IMMUTABLE_HISTORY_PREPARATION_RESULT" ]; then
        echo "Immutable history supervised preparation omitted retained evidence." >&2
        return 1
    fi
    mapfile -t preparation_lines < "$IMMUTABLE_HISTORY_PREPARATION_LOG"
    if [ "${#preparation_lines[@]}" -ne 1 ]; then
        echo "Immutable history supervised preparation did not emit exactly one TSV decision." >&2
        return 1
    fi
    preparation_line="${preparation_lines[0]%$'\r'}"
    IFS=$'\t' read -r outcome reason source_revision source_tree receipt_commit reusable_ids extra \
        <<< "$preparation_line"
    if [ -n "$extra" ]; then
        echo "Immutable history supervised preparation emitted an invalid TSV decision." >&2
        return 1
    fi

    # This preparation alone accepts child exit 10 as a successful decision;
    # the authenticated wrapper/raw receipts still retain the exact child exit.
    if [ "$rc" -eq 0 ] && [ "$outcome" = full-required ] && [ -n "$reason" ] &&
        [ -z "$reusable_ids" ] &&
        { [ -z "$source_revision" ] || [[ "$source_revision" =~ ^[0-9a-f]{40}$ ]]; } &&
        { [ -z "$source_tree" ] || [[ "$source_tree" =~ ^[0-9a-f]{40}$ ]]; } &&
        { [ -z "$receipt_commit" ] || [[ "$receipt_commit" =~ ^[0-9a-f]{40}$ ]]; }; then
        select_immutable_history_full_checks "$reason"
        return
    fi
    if [ "$rc" -ne 0 ] || [ "$outcome" != routine-reusable ] ||
        [ "$reason" != receipt-valid ] || [ -z "$reusable_ids" ] ||
        [ -z "$source_revision" ] || [ -z "$source_tree" ] || [ -z "$receipt_commit" ]; then
        echo "Immutable history receipt verification failed closed: ${preparation_lines[0]:-no-output}" >&2
        return 1
    fi
    if ! [[ "$source_revision" =~ ^[0-9a-f]{40}$ ]] ||
        ! [[ "$source_tree" =~ ^[0-9a-f]{40}$ ]] ||
        ! [[ "$receipt_commit" =~ ^[0-9a-f]{40}$ ]]; then
        echo "Immutable history receipt verification identity is invalid." >&2
        return 1
    fi
    if [ "$PROFILE" = release ] || [ "$PROFILE" = nightly-full ]; then
        echo "Immutable history preparation unexpectedly authorized reuse for terminal profile: $PROFILE" >&2
        return 1
    fi

    IMMUTABLE_HISTORY_MODE=routine-reusable
    IMMUTABLE_HISTORY_REASON=${reason:-receipt-verified}
    IMMUTABLE_HISTORY_RECEIPT_SOURCE=$source_revision
    IMMUTABLE_HISTORY_FINGERPRINT=$(printf '%s\n' "$source_revision" "$source_tree" "$receipt_commit" | sha256sum | awk '{print $1}')
    reusable_ids=${reusable_ids//,/ }
    for id in $reusable_ids; do
        immutable_history_check_is_protected "$id" || {
            echo "Immutable history receipt returned an unsupported check id: $id" >&2
            return 1
        }
        [ -z "${IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID[$id]:-}" ] || {
            echo "Immutable history receipt returned a duplicate reusable check id: $id" >&2
            return 1
        }
        IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID["$id"]=true
    done
    for id in workflow-artifacts assessment-artifacts source-ai-context-version; do
        [ -n "${IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID[$id]:-}" ] || {
            echo "Immutable history receipt omitted required reusable check id: $id" >&2
            return 1
        }
        SELECTION_REASON_BY_ID["$id"]="explicit-request:immutable-history-receipt:$source_revision"
    done
}

if ! prepare_immutable_history_layer; then
    echo "Immutable history validation preparation failed; no checks were launched." >&2
    exit 2
fi

# Track results
TOTAL_CHECKS=0
PASSED_CHECKS=0
EXECUTED_CHECKS=0
REUSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0
WARNINGS=0
REQUIRED_SELECTED=0
REQUIRED_RUN=0
REQUIRED_FAILED=0
ADVISORY_SELECTED=0
DEFERRED_CHECKS=0
REQUIRED_DEFERRED=0
NOT_APPLICABLE=0
BLOCKED_CHECKS=0
REQUIRED_BLOCKED=0
RUNNER_ABORT_FAILURE_RECORDED=false
CHECK_TIMINGS=()
BLOCKED_LIST=()
EVIDENCE_SELECTED_CHECKS="$LOG_DIR/selected-checks.tsv"
: > "$EVIDENCE_SELECTED_CHECKS"
for id in "${SELECTED_CHECK_ORDER[@]}"; do
    printf '%s\t%s\n' "$id" "${SELECTION_REASON_BY_ID[$id]}" >> "$EVIDENCE_SELECTED_CHECKS"
done

now_millis() {
    local value seconds fraction
    if [ -n "${EPOCHREALTIME:-}" ]; then
        seconds=${EPOCHREALTIME%.*}
        fraction=${EPOCHREALTIME#*.}
        printf '%s%03d\n' "$seconds" "$((10#${fraction:0:3}))"
        return 0
    fi
    value=$(date +%s%3N 2>/dev/null || true)
    case "$value" in
        ''|*[!0-9]*) printf '%s\n' "$((SECONDS * 1000))" ;;
        *) printf '%s\n' "$value" ;;
    esac
}

EVIDENCE_PATH="$LOG_DIR/evidence.jsonl"
EVIDENCE_SUMMARY="$LOG_DIR/evidence-summary.json"
EVIDENCE_WORKFLOW_SUMMARY="$LOG_DIR/workflow-summary.json"
EVIDENCE_POST_SNAPSHOT="$LOG_DIR/repository-snapshot-post.json"
EVIDENCE_SEALED_MANIFEST="$LOG_DIR/sealed-manifest.json"
EVIDENCE_STAGED_MANIFEST="$LOG_DIR/sealed-manifest.staged.json"
EVIDENCE_SEAL_SUPERVISION_LOG="$LOG_DIR/control-seal.log"
EVIDENCE_SEAL_SUPERVISION_RESULT="$LOG_DIR/control-seal.result.json"
EVIDENCE_SEAL_PUBLISHED=false
EVIDENCE_CACHE="$LOG_BASE/evidence-cache.json"
EVIDENCE_SELECTION="$LOG_DIR/evidence-selection.tsv"
EVIDENCE_PREPARATION_SELECTION="$LOG_DIR/evidence-preparation-selection.tsv"
EVIDENCE_EVENTS="$LOG_DIR/evidence-events.tsv"
EVIDENCE_CHANGED_PATHS="$LOG_DIR/changed-paths.txt"
EVIDENCE_SELECTION_COMPARISON="$LOG_DIR/selection-comparison.tsv"
declare -A EVIDENCE_FINGERPRINT_BY_ID=()
declare -A EVIDENCE_STANDARD_FINGERPRINT_BY_ID=()
declare -A EVIDENCE_CACHE_HIT_BY_ID=()
declare -A EVIDENCE_RECEIPT_HIT_BY_ID=()
declare -A EVIDENCE_PRIOR_LOG_BY_ID=()
declare -A VALIDATOR_VERSION_BY_ID=()
EVIDENCE_ENVIRONMENT_CLASS=linux-local
if [ "${GITHUB_ACTIONS:-}" = true ]; then
    EVIDENCE_ENVIRONMENT_CLASS=ubuntu-hosted
elif [ -n "${MSYSTEM:-}" ]; then
    EVIDENCE_ENVIRONMENT_CLASS=windows-native
elif [ -r /proc/version ] && grep -qi microsoft /proc/version 2>/dev/null; then
    EVIDENCE_ENVIRONMENT_CLASS=wsl-linux
fi
EVIDENCE_POLICY_FINGERPRINT=$(sha256sum \
    "$REGISTRY_PATH" \
    "$SCRIPT_DIR/check-all.sh" \
    "$EVIDENCE_HELPER" \
    "$SCRIPT_DIR/validation_process_supervisor.py" \
    2>/dev/null | sha256sum 2>/dev/null | awk '{print $1}')
EVIDENCE_POLICY_FINGERPRINT=${EVIDENCE_POLICY_FINGERPRINT:-unavailable}
EVIDENCE_INPUT_FINGERPRINT=
EVIDENCE_CACHE_HIT=false
EVIDENCE_RECEIPT_HIT=false
EVIDENCE_PRIOR_LOG=

record_runner_abort_failure() {
    if [ "$RUNNER_CANCELLED_BY_SIGNAL" = true ] && [ "$RUNNER_ABORT_FAILURE_RECORDED" = false ]; then
        echo -e "${RED}✗ FAILED${NC}: validation runner was cancelled (${VALIDATION_ABORT_REASON:-signal})"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
        RUNNER_ABORT_FAILURE_RECORDED=true
    fi
}

validator_version() {
    local id=$1
    printf '%s:%s\n' "$EVIDENCE_POLICY_FINGERPRINT" "$id"
}

prepare_validation_evidence() {
    local id=$1
    EVIDENCE_INPUT_FINGERPRINT=${EVIDENCE_FINGERPRINT_BY_ID[$id]:-}
    EVIDENCE_CACHE_HIT=${EVIDENCE_CACHE_HIT_BY_ID[$id]:-false}
    EVIDENCE_RECEIPT_HIT=${EVIDENCE_RECEIPT_HIT_BY_ID[$id]:-false}
    EVIDENCE_PRIOR_LOG=${EVIDENCE_PRIOR_LOG_BY_ID[$id]:-}
    [ -n "$EVIDENCE_INPUT_FINGERPRINT" ] || return 1
    return 0
}

prepare_all_validation_evidence() {
    local id version prepared line parse_line record fingerprint cache_hit prior_log rest tab_count row_count=0
    local -A expected_ids=() seen_ids=()
    [ -f "$EVIDENCE_HELPER" ] || {
        echo "Validation evidence helper is missing: $EVIDENCE_HELPER" >&2
        return 1
    }
    : > "$EVIDENCE_PREPARATION_SELECTION"
    for id in "${CHECK_IDS[@]}"; do
        expected_ids["$id"]=true
        version=$(validator_version "$id")
        VALIDATOR_VERSION_BY_ID["$id"]=$version
        printf '%s\t%s\t%s\t%s\n' \
            "$id" "$version" "${CHECK_INPUT_PATHS[$id]}" "${CHECK_CACHE_POLICY[$id]}" \
            >> "$EVIDENCE_PREPARATION_SELECTION"
    done
    EVIDENCE_PREPARATION_SELECTION_REF=$(repo_relative_artifact "$EVIDENCE_PREPARATION_SELECTION") || return 1
    EVIDENCE_CACHE_REF=$(repo_relative_artifact "$EVIDENCE_CACHE") || return 1
    if ! run_supervised_control prepare 60 \
        "$PYTHON_EXECUTABLE" .ai/scripts/validation-evidence.py prepare \
        --repo . \
        --cache "$EVIDENCE_CACHE_REF" \
        --profile "$PROFILE" \
        --environment-class "$EVIDENCE_ENVIRONMENT_CLASS" \
        --selection "$EVIDENCE_PREPARATION_SELECTION_REF"; then
        return 1
    fi
    prepared=$(< "$LOG_DIR/control-prepare.log")
    while IFS= read -r line; do
        parse_line="${line%$'\r'}"
        [ -n "$parse_line" ] || {
            echo "Validation evidence preparation contains a blank or empty row" >&2
            return 1
        }
        rest=$parse_line
        tab_count=0
        while [[ "$rest" == *$'\t'* ]]; do
            rest=${rest#*$'\t'}
            tab_count=$((tab_count + 1))
        done
        [ "$tab_count" -eq 3 ] || {
            echo "Validation evidence preparation row must contain exactly four columns" >&2
            return 1
        }
        IFS=$'\t' read -r record fingerprint cache_hit prior_log <<< "$parse_line"
        [[ "$record" =~ ^[a-z0-9][a-z0-9-]*$ ]] || {
            echo "Validation evidence preparation contains an invalid check id" >&2
            return 1
        }
        [ -n "${expected_ids[$record]:-}" ] || {
            echo "Validation evidence preparation contains an unknown check id: $record" >&2
            return 1
        }
        [ -z "${seen_ids[$record]:-}" ] || {
            echo "Validation evidence preparation contains a duplicate check id: $record" >&2
            return 1
        }
        [[ "$fingerprint" =~ ^[0-9a-f]{64}$ ]] || {
            echo "Validation evidence preparation contains an invalid fingerprint for: $record" >&2
            return 1
        }
        { [ "$cache_hit" = true ] || [ "$cache_hit" = false ]; } || {
            echo "Validation evidence preparation contains an invalid cache flag for: $record" >&2
            return 1
        }
        if [ "$cache_hit" = true ]; then
            path_is_safe "$prior_log" || {
                echo "Validation evidence preparation contains an invalid cache log for: $record" >&2
                return 1
            }
        elif [ -n "$prior_log" ]; then
            echo "Validation evidence preparation contains a log without a cache hit for: $record" >&2
            return 1
        fi
        seen_ids["$record"]=true
        row_count=$((row_count + 1))
        EVIDENCE_FINGERPRINT_BY_ID["$record"]=$fingerprint
        EVIDENCE_STANDARD_FINGERPRINT_BY_ID["$record"]=$fingerprint
        EVIDENCE_CACHE_HIT_BY_ID["$record"]=$cache_hit
        EVIDENCE_RECEIPT_HIT_BY_ID["$record"]=false
        EVIDENCE_PRIOR_LOG_BY_ID["$record"]=$prior_log
    done <<< "$prepared"
    [ "$row_count" -eq "${#CHECK_IDS[@]}" ] || {
        echo "Validation evidence preparation row count does not match the canonical registry" >&2
        return 1
    }
    for id in "${CHECK_IDS[@]}"; do
        if [ -n "${IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID[$id]:-}" ]; then
            EVIDENCE_FINGERPRINT_BY_ID["$id"]=$IMMUTABLE_HISTORY_FINGERPRINT
            EVIDENCE_CACHE_HIT_BY_ID["$id"]=false
            EVIDENCE_RECEIPT_HIT_BY_ID["$id"]=true
            EVIDENCE_PRIOR_LOG_BY_ID["$id"]=.ai/distribution/validation/immutable-history-receipt.yaml
        fi
    done
    if [ "$IMMUTABLE_HISTORY_SOURCE_CONTEXT" = true ] && [ "$IMMUTABLE_HISTORY_FORCE_FULL" = true ]; then
        for id in workflow-artifacts assessment-artifacts source-ai-context-version; do
            EVIDENCE_CACHE_HIT_BY_ID["$id"]=false
            EVIDENCE_RECEIPT_HIT_BY_ID["$id"]=false
            EVIDENCE_PRIOR_LOG_BY_ID["$id"]=
        done
    fi
    for id in "${CHECK_IDS[@]}"; do
        [ -n "${EVIDENCE_FINGERPRINT_BY_ID[$id]:-}" ] || {
            echo "Validation evidence preparation omitted selected check: $id" >&2
            return 1
        }
    done
}

prepare_nonreuse_validation_evidence() {
    local id=$1
    EVIDENCE_INPUT_FINGERPRINT=${EVIDENCE_STANDARD_FINGERPRINT_BY_ID[$id]:-}
    EVIDENCE_CACHE_HIT=false
    EVIDENCE_RECEIPT_HIT=false
    EVIDENCE_PRIOR_LOG=
    [ -n "$EVIDENCE_INPUT_FINGERPRINT" ]
}

write_final_fingerprint_selection() {
    local id event_id _version _fingerprint _outcome disposition _started _completed cache_hit
    local _log _suppressed _reason _changed result_ref _enforcement
    declare -A omit_immutable_reuse=()
    while IFS=$'\t' read -r event_id _version _fingerprint _outcome disposition \
        _started _completed cache_hit _log _suppressed _reason _changed result_ref _enforcement; do
        if [ "$IMMUTABLE_HISTORY_PREPARATION_ACTIVE" = true ] &&
            [ "$disposition" = reused ] && [ "$cache_hit" = false ] &&
            [ "$result_ref" = "$(basename "$IMMUTABLE_HISTORY_PREPARATION_RESULT")" ]; then
            omit_immutable_reuse["$event_id"]=true
        fi
    done < "$EVIDENCE_EVENTS"
    : > "$EVIDENCE_SELECTION"
    for id in "${CHECK_IDS[@]}"; do
        [ -z "${omit_immutable_reuse[$id]:-}" ] || continue
        printf '%s\t%s\t%s\t%s\n' \
            "$id" "${VALIDATOR_VERSION_BY_ID[$id]}" \
            "${CHECK_INPUT_PATHS[$id]}" "${CHECK_CACHE_POLICY[$id]}" \
            >> "$EVIDENCE_SELECTION"
    done
}

record_validation_evidence() {
    local id=$1 outcome=$2 disposition=$3 started_ms=$4 completed_ms=$5 log_path=$6
    local include_result=${7:-true}
    local suppressed_bytes=0 version selection_reason enforcement result_path result_ref=
    [ "$VERBOSE" = true ] || suppressed_bytes=-1
    version=${VALIDATOR_VERSION_BY_ID[$id]:-}
    [ -n "$version" ] || return 1
    selection_reason=${SELECTION_REASON_BY_ID[$id]:-selection-reason-unavailable}
    enforcement=${CHECK_ENFORCEMENT[$id]:-}
    [ "$enforcement" = required ] || [ "$enforcement" = advisory ] || return 1
    if [ "$include_result" != true ]; then
        result_path=
    elif [ "$disposition" = reused ] && [ "$EVIDENCE_RECEIPT_HIT" = true ]; then
        result_path=$IMMUTABLE_HISTORY_PREPARATION_RESULT
    else
        result_path="${log_path%.log}.result.json"
    fi
    [ -z "$result_path" ] || [ ! -f "$result_path" ] || result_ref=$(basename "$result_path")
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$id" "$version" "$EVIDENCE_INPUT_FINGERPRINT" "$outcome" "$disposition" \
        "$started_ms" "$completed_ms" "$EVIDENCE_CACHE_HIT" "$(basename "$log_path")" "$suppressed_bytes" \
        "$selection_reason" "$CHANGED_PATHS_DIGEST" "$result_ref" "$enforcement" \
        >> "$EVIDENCE_EVENTS"
}

: > "$EVIDENCE_EVENTS"
: > "$EVIDENCE_CHANGED_PATHS"
if [ "${#CHANGED_PATHS[@]}" -gt 0 ]; then
    printf '%s\n' "${!CHANGED_PATHS[@]}" | LC_ALL=C sort > "$EVIDENCE_CHANGED_PATHS"
fi
CHANGED_PATHS_DIGEST=$(sha256_regular_file "$EVIDENCE_CHANGED_PATHS")
CHANGED_PATHS_DIGEST=${CHANGED_PATHS_DIGEST:-unavailable}
printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    validation-selection-comparison/v1 "$SELECTION_MODE" "$SELECTION_BASE_SHA" \
    "$SELECTION_HEAD_SHA" "$CHANGED_PATHS_DIGEST" "$SELECTION_ESCALATION_REASON" \
    > "$EVIDENCE_SELECTION_COMPARISON"

record_not_selected_evidence() {
    local id log_path started_ms completed_ms
    for id in "${CHECK_IDS[@]}"; do
        [ -n "${SELECTED_CHECK_IDS[$id]:-}" ] && continue
        log_path="$LOG_DIR/$id.not-selected.log"
        printf 'NOT-SELECTED: %s\n' "${SELECTION_REASON_BY_ID[$id]}" > "$log_path"
        EVIDENCE_INPUT_FINGERPRINT=${EVIDENCE_FINGERPRINT_BY_ID[$id]:-}
        EVIDENCE_CACHE_HIT=false
        EVIDENCE_RECEIPT_HIT=false
        started_ms=$(now_millis)
        completed_ms=$started_ms
        record_validation_evidence "$id" "not-applicable" "not-selected" "$started_ms" "$completed_ms" "$log_path" || return 1
    done
}

emit_retained_output() {
    local log_path=$1 outcome=$2
    if [ "$VERBOSE" = true ]; then
        cat "$log_path"
    elif [ "$outcome" != passed ]; then
        sed -n '1,20p' "$log_path"
    fi
}

select_check() {
    local description=$1
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    if [ -z "$id" ]; then
        echo "Validation check is missing from the profile registry: $description" >&2
        exit 2
    fi
    if [ -z "${SELECTED_CHECK_IDS[$id]:-}" ]; then
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        return 1
    fi
    return 0
}

record_selected() {
    local enforcement=$1
    if [ "$enforcement" != "required" ] && [ "$enforcement" != "advisory" ]; then
        echo "Internal error: unsupported enforcement class '$enforcement'" >&2
        exit 2
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ "$enforcement" == "required" ]; then
        REQUIRED_SELECTED=$((REQUIRED_SELECTED + 1))
    else
        ADVISORY_SELECTED=$((ADVISORY_SELECTED + 1))
    fi
}

record_unavailable_or_failed() {
    local enforcement=$1
    local description=$2
    if [ "$enforcement" == "required" ]; then
        echo -e "${RED}✗ FAILED${NC}: $description"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    else
        echo -e "${YELLOW}⚠ ADVISORY${NC}: $description"
        WARNINGS=$((WARNINGS + 1))
    fi
}

record_timing() {
    local id=$1 elapsed=$2 description=$3 outcome=$4 disposition=$5 log_ref=$6
    CHECK_TIMINGS+=("${elapsed}|${outcome}|${disposition}|${id}|${description}|${log_ref}")
}

# Return a reason only for unambiguous host/runtime failures. Keep this list
# deliberately narrow: repository defects must continue to fail normally.
classify_environment_block() {
    local output=$1
    case "$output" in
        *'"outcome":"blocked-by-environment"'*|*"Python prerequisite blocked"*)
            printf '%s\n' "python-prerequisite"
            return 0
            ;;
        *"python: command not found"*|*"python3: command not found"*)
            printf '%s\n' "missing-python"
            return 0
            ;;
        *"dotnet: command not found"*|*"No .NET SDKs were found"*)
            printf '%s\n' "missing-dotnet-sdk"
            return 0
            ;;
        *"Could not resolve host"*|*"Name or service not known"*|*"Network is unreachable"*|*"No connection could be made"*)
            printf '%s\n' "network-unavailable"
            return 0
            ;;
        *"Read-only file system"*)
            printf '%s\n' "read-only-filesystem"
            return 0
            ;;
    esac
    return 1
}

record_environment_block() {
    local enforcement=$1
    local description=$2
    local reason=$3
    echo -e "${YELLOW}⊘ BLOCKED-BY-ENVIRONMENT${NC}: $description ($reason)"
    BLOCKED_CHECKS=$((BLOCKED_CHECKS + 1))
    BLOCKED_LIST+=("${reason}|${description}")
    if [ "$enforcement" == "required" ]; then
        REQUIRED_BLOCKED=$((REQUIRED_BLOCKED + 1))
    fi
}

run_script_with_timeout() {
    local timeout_seconds=$1 log_path=$2 result_path=$3 script_path=$4
    shift 4
    run_supervisor_cli supervise \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --log-path "$log_path" \
        --result-path "$result_path" \
        --timeout-seconds "$timeout_seconds" \
        --cwd-ref . \
        -- bash "$script_path" "$@"
}

PARSED_COMMAND_ARGV=()

parse_declared_command_argv() {
    local command_text=$1 token reconstructed
    PARSED_COMMAND_ARGV=()
    case "$command_text" in
        ''|*$'\t'*|*$'\r'*|*$'\n'*) return 1 ;;
    esac
    read -r -a PARSED_COMMAND_ARGV <<< "$command_text"
    [ "${#PARSED_COMMAND_ARGV[@]}" -gt 0 ] || return 1
    printf -v reconstructed '%s ' "${PARSED_COMMAND_ARGV[@]}"
    reconstructed=${reconstructed% }
    [ "$reconstructed" = "$command_text" ] || return 1
    for token in "${PARSED_COMMAND_ARGV[@]}"; do
        [[ "$token" =~ ^[-A-Za-z0-9_./:=+@,%~]+$ ]] || return 1
    done
    if [ "${PARSED_COMMAND_ARGV[0]}" = python ]; then
        PARSED_COMMAND_ARGV[0]=$PYTHON_EXECUTABLE
    fi
}

declared_command_target_is_available() {
    local executable=${1:-} target=${2:-}
    [ "$executable" = "$PYTHON_EXECUTABLE" ] || return 1
    [[ "$target" == *.py ]] || return 1
    path_is_safe "$target" || return 1
    [ -f "$PROJECT_ROOT/$target" ]
}

run_argv_with_timeout() {
    local timeout_seconds=$1 log_path=$2 result_path=$3
    shift 3
    run_supervisor_cli supervise \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --log-path "$log_path" \
        --result-path "$result_path" \
        --timeout-seconds "$timeout_seconds" \
        --cwd-ref . \
        -- "$@"
}

VERIFIED_SUPERVISION_STATUS=
VERIFIED_SUPERVISION_LAUNCHED=false
VERIFIED_SUPERVISION_EXIT=

verify_supervision_return_contract() {
    local supervisor_rc=$1 result_path=$2 verified extra
    VERIFIED_SUPERVISION_STATUS=
    VERIFIED_SUPERVISION_LAUNCHED=false
    VERIFIED_SUPERVISION_EXIT=
    if [ "$supervisor_rc" -eq 130 ] && [ ! -f "$result_path" ] &&
        [ "$RUNNER_CANCELLED_BY_SIGNAL" = true ]; then
        VERIFIED_SUPERVISION_STATUS=cancelled-before-adapter-launch
        return 0
    fi
    case "$supervisor_rc" in
        0|1|124|125|126|127|128|130) ;;
        *) return 1 ;;
    esac
    verified=$(python .ai/scripts/validation-evidence.py verify-supervision-result \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --result-path "$result_path") || return 1
    IFS=$'\t' read -r VERIFIED_SUPERVISION_STATUS VERIFIED_SUPERVISION_LAUNCHED \
        VERIFIED_SUPERVISION_EXIT extra <<< "$verified"
    [ -z "$extra" ] || return 1
    [ "$VERIFIED_SUPERVISION_LAUNCHED" = true ] ||
        [ "$VERIFIED_SUPERVISION_LAUNCHED" = false ] || return 1
    case "$supervisor_rc:$VERIFIED_SUPERVISION_STATUS:$VERIFIED_SUPERVISION_LAUNCHED" in
        0:completed:true) ;;
        1:completed:true) ;;
        124:timed-out:true) ;;
        125:snapshot-drift:true) ;;
        126:cleanup-failed:true) ;;
        127:launch-failed:false) ;;
        128:snapshot-drift:false) ;;
        130:cancelled:true) ;;
        *) return 1 ;;
    esac
    case "$VERIFIED_SUPERVISION_EXIT" in
        ''|*[!0-9-]*) [ -z "$VERIFIED_SUPERVISION_EXIT" ] || return 1 ;;
    esac
}

run_supervised_control() {
    local role=$1 timeout_seconds=$2 log_path result_path rc
    shift 2
    log_path="$LOG_DIR/control-$role.log"
    result_path="$LOG_DIR/control-$role.result.json"
    set +e
    run_control_supervisor_cli supervise \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --log-path "$log_path" \
        --result-path "$result_path" \
        --timeout-seconds "$timeout_seconds" \
        --cwd-ref . \
        -- "$@"
    rc=$?
    set -e
    if ! verify_supervision_return_contract "$rc" "$result_path" ||
        [ "$rc" -ne 0 ] || [ "$VERIFIED_SUPERVISION_STATUS" != completed ] ||
        [ "$VERIFIED_SUPERVISION_LAUNCHED" != true ] ||
        [ "$VERIFIED_SUPERVISION_EXIT" != 0 ]; then
        return 1
    fi
    EVIDENCE_CONTROL_RESULT_BY_ROLE["$role"]=$result_path
}

if ! prepare_all_validation_evidence; then
    echo "Validation evidence preparation failed under process-tree supervision; no checks were launched." >&2
    exit 2
fi
if ! record_not_selected_evidence; then
    echo "Validation not-selected evidence could not be recorded." >&2
    exit 2
fi

record_aborted_selected_check() {
    local id=$1 description=$2 enforcement=$3
    local started_ms completed_ms duration_ms log_path outcome=failed
    local disposition=not-executed
    log_path="$LOG_DIR/$id.log"
    started_ms=$(now_millis)
    printf 'Validation check was not launched: %s.\n' "${VALIDATION_ABORT_REASON:-validation-chain-aborted}" >"$log_path"
    if ! prepare_nonreuse_validation_evidence "$id"; then
        printf '%s\n' "validation evidence lookup failed for $id" >&2
        EVIDENCE_INPUT_FINGERPRINT=unavailable
        EVIDENCE_CACHE_HIT=false
    fi
    record_unavailable_or_failed "$enforcement" "$description was not launched after ${VALIDATION_ABORT_REASON:-validation-chain-abort}"
    completed_ms=$(now_millis)
    duration_ms=$((completed_ms - started_ms))
    if ! record_validation_evidence "$id" "$outcome" "$disposition" "$started_ms" "$completed_ms" "$log_path"; then
        echo "Validation evidence record failed for aborted check: $id" >&2
    fi
    record_timing "$id" "$duration_ms" "$description" "$outcome" "$disposition" "$log_path"
    printf '%-36s %-24s %6sms %s\n' "$id" "$outcome" "$duration_ms" "$disposition"
    emit_retained_output "$log_path" "$outcome"
}

admit_selected_check() {
    local id=$1 description=$2 enforcement=$3
    if [ "$VALIDATION_ABORTED" = true ]; then
        record_aborted_selected_check "$id" "$description" "$enforcement"
        return 1
    fi
    return 0
}

record_selected_without_execution() {
    local description=$1 requested_outcome=$2 reason=$3
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    local enforcement=${CHECK_ENFORCEMENT[$id]:-}
    local started_ms completed_ms duration_ms log_path outcome=$requested_outcome
    select_check "$description" || return 0
    record_selected "$enforcement"
    admit_selected_check "$id" "$description" "$enforcement" || return 0
    log_path="$LOG_DIR/$id.log"
    started_ms=$(now_millis)
    if ! prepare_nonreuse_validation_evidence "$id"; then
        outcome=failed
        reason="validation evidence lookup failed before the selected check could be classified"
        EVIDENCE_INPUT_FINGERPRINT=unavailable
        EVIDENCE_CACHE_HIT=false
        record_unavailable_or_failed "$enforcement" "validation evidence lookup for $description"
    else
        case "$outcome" in
            not-applicable)
                NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
                echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: $description ($reason)"
                ;;
            deferred-with-owner)
                DEFERRED_CHECKS=$((DEFERRED_CHECKS + 1))
                [ "$enforcement" != required ] || REQUIRED_DEFERRED=$((REQUIRED_DEFERRED + 1))
                echo -e "${YELLOW}⊖${NC} DEFERRED: $description ($reason)"
                ;;
            failed)
                record_unavailable_or_failed "$enforcement" "$description ($reason)"
                ;;
            *)
                echo "Internal error: unsupported non-execution outcome '$outcome'" >&2
                exit 2
                ;;
        esac
    fi
    printf 'Selected check was not launched; outcome=%s; reason=%s\n' "$outcome" "$reason" >"$log_path"
    completed_ms=$(now_millis)
    duration_ms=$((completed_ms - started_ms))
    if ! record_validation_evidence "$id" "$outcome" "not-executed" "$started_ms" "$completed_ms" "$log_path"; then
        echo "Validation evidence record failed for non-executed check: $id" >&2
        if [ "$outcome" != failed ]; then
            [ "$outcome" = not-applicable ] && NOT_APPLICABLE=$((NOT_APPLICABLE - 1))
            if [ "$outcome" = deferred-with-owner ]; then
                DEFERRED_CHECKS=$((DEFERRED_CHECKS - 1))
                [ "$enforcement" != required ] || REQUIRED_DEFERRED=$((REQUIRED_DEFERRED - 1))
            fi
            record_unavailable_or_failed "$enforcement" "validation evidence record for $description"
            outcome=failed
        fi
    fi
    record_timing "$id" "$duration_ms" "$description" "$outcome" "not-executed" "$log_path"
    printf '%-36s %-24s %6sms %s\n' "$id" "$outcome" "$duration_ms" "not-executed"
    emit_retained_output "$log_path" "$outcome"
}

# Function to run a check script
run_check() {
    local script_name=$1
    local description=$2
    local enforcement=$3
    local is_critical=$4
    local is_quick=$5
    local command_contract=$6
    shift 6
    local args=("$@")
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    local started_ms completed_ms duration_ms output rc reason outcome log_path result_path disposition timeout_seconds
    local supervision_contract_valid=true record_result=true
    select_check "$description" "$is_critical" "$is_quick" || return 0
    record_selected "$enforcement"
    admit_selected_check "$id" "$description" "$enforcement" || return 0
    log_path="$LOG_DIR/$id.log"
    result_path="$LOG_DIR/$id.result.json"
    started_ms=$(now_millis)
    timeout_seconds=${CHECK_TIMEOUT[$id]:-}

    if ! prepare_validation_evidence "$id"; then
        printf '%s\n' "validation evidence lookup failed for $id" >"$log_path"
        EVIDENCE_INPUT_FINGERPRINT=unavailable
        EVIDENCE_CACHE_HIT=false
        record_unavailable_or_failed "$enforcement" "validation evidence lookup for $description"
        outcome="failed"
        disposition="not-executed"
    elif [ "${CHECK_COMMAND[$id]:-}" != "$command_contract" ]; then
        printf '%s\n' "runner command does not match the canonical registry contract" >"$log_path"
        record_unavailable_or_failed "$enforcement" "runner command contract for $description"
        outcome="failed"
        disposition="not-executed"
    elif [ ! -f "$SCRIPT_DIR/$script_name" ]; then
        printf '%s\n' "$script_name not found" >"$log_path"
        record_unavailable_or_failed "$enforcement" "$script_name not found"
        outcome="failed"
        disposition="not-executed"
    elif [ ! -x "$SCRIPT_DIR/$script_name" ]; then
        printf '%s\n' "$script_name is not executable" >"$log_path"
        record_unavailable_or_failed "$enforcement" "$script_name is not executable"
        outcome="failed"
        disposition="not-executed"
    elif [ "$EVIDENCE_CACHE_HIT" = true ] || [ "$EVIDENCE_RECEIPT_HIT" = true ]; then
        printf 'Reused eligible validation evidence; source=%s; prior_log=%s\n' \
            "$([ "$EVIDENCE_RECEIPT_HIT" = true ] && printf receipt || printf cache)" \
            "$EVIDENCE_PRIOR_LOG" >"$log_path"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        REUSED_CHECKS=$((REUSED_CHECKS + 1))
        outcome="passed"
        disposition="reused"
    else
        set +e
        run_script_with_timeout "$timeout_seconds" "$log_path" "$result_path" ".ai/scripts/$script_name" "${args[@]}"
        rc=$?
        set -e
        output=$(cat "$log_path" 2>/dev/null || true)
        if ! verify_supervision_return_contract "$rc" "$result_path"; then
            supervision_contract_valid=false
            record_result=false
        fi
        if [ "$supervision_contract_valid" = true ] &&
            [ "$VERIFIED_SUPERVISION_LAUNCHED" = true ]; then
            [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
            EXECUTED_CHECKS=$((EXECUTED_CHECKS + 1))
        fi
        if [ "$supervision_contract_valid" != true ]; then
            printf '\nValidation supervision result was missing or could not be authenticated.\n' >> "$log_path"
            record_unavailable_or_failed "$enforcement" "$description supervision evidence was invalid"
            outcome="failed"
            disposition="not-executed"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=validation-supervision-evidence-invalid
        elif [ "$rc" -eq 124 ]; then
            record_unavailable_or_failed "$enforcement" "$description timed out after ${timeout_seconds}s"
            outcome="failed"
            disposition="timed-out"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=validation-timeout
        elif [ "$rc" -eq 125 ]; then
            record_unavailable_or_failed "$enforcement" "$description observed repository snapshot drift"
            outcome="failed"
            disposition="snapshot-drift"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=repository-snapshot-drift
        elif [ "$rc" -eq 128 ]; then
            record_unavailable_or_failed "$enforcement" "$description was blocked by repository snapshot drift before launch"
            outcome="failed"
            disposition="snapshot-drift"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=repository-snapshot-drift
        elif [ "$rc" -eq 126 ]; then
            record_unavailable_or_failed "$enforcement" "$description could not prove complete process-tree cleanup"
            outcome="failed"
            disposition="executed"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=process-tree-cleanup-failed
        elif [ "$rc" -eq 130 ]; then
            record_unavailable_or_failed "$enforcement" "$description was cancelled"
            outcome="failed"
            if [ "$VERIFIED_SUPERVISION_LAUNCHED" = true ]; then
                disposition="cancelled"
            else
                disposition="not-executed"
            fi
            VALIDATION_ABORTED=true
            [ -n "$VALIDATION_ABORT_REASON" ] || VALIDATION_ABORT_REASON=validation-cancelled
        elif [ "$rc" -eq 127 ]; then
            record_unavailable_or_failed "$enforcement" "$description could not be launched by the process supervisor"
            outcome="failed"
            disposition="not-executed"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=validation-launch-failed
        elif [ "$rc" -eq 0 ]; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            outcome="passed"
        elif reason=$(classify_environment_block "$output"); then
            record_environment_block "$enforcement" "$description" "$reason"
            outcome="blocked-by-environment"
        else
            record_unavailable_or_failed "$enforcement" "$description returned non-zero"
            outcome="failed"
        fi
        disposition=${disposition:-executed}
    fi
    completed_ms=$(now_millis)
    duration_ms=$((completed_ms - started_ms))
    if [ "$disposition" != reused ] &&
        { [ "$EVIDENCE_CACHE_HIT" = true ] || [ "$EVIDENCE_RECEIPT_HIT" = true ]; }; then
        prepare_nonreuse_validation_evidence "$id" || EVIDENCE_INPUT_FINGERPRINT=unavailable
    fi
    if ! record_validation_evidence "$id" "$outcome" "$disposition" "$started_ms" "$completed_ms" "$log_path" "$record_result"; then
        printf '%s\n' "validation evidence record failed for $id" >&2
        if [ "$outcome" = passed ]; then
            PASSED_CHECKS=$((PASSED_CHECKS - 1))
            [ "$disposition" = reused ] && REUSED_CHECKS=$((REUSED_CHECKS - 1))
            record_unavailable_or_failed "$enforcement" "validation evidence record for $description"
            outcome="failed"
        fi
    fi
    record_timing "$id" "$duration_ms" "$description" "$outcome" "$disposition" "$log_path"
    printf '%-36s %-24s %6sms %s\n' "$id" "$outcome" "$duration_ms" "$disposition"
    emit_retained_output "$log_path" "$outcome"
}

run_command_check() {
    local command_text=$1
    local description=$2
    local enforcement=$3
    local is_critical=$4
    local is_quick=$5
    shift 5
    local supplied_argv=("$@")
    local command_argv=() command_ready=true
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    local started_ms completed_ms duration_ms output rc reason outcome log_path result_path disposition timeout_seconds
    local supervision_contract_valid=true record_result=true
    select_check "$description" "$is_critical" "$is_quick" || return 0
    record_selected "$enforcement"
    admit_selected_check "$id" "$description" "$enforcement" || return 0
    log_path="$LOG_DIR/$id.log"
    result_path="$LOG_DIR/$id.result.json"
    started_ms=$(now_millis)
    timeout_seconds=${CHECK_TIMEOUT[$id]:-}

    if [ "${#supplied_argv[@]}" -gt 0 ]; then
        command_argv=("${supplied_argv[@]}")
    elif parse_declared_command_argv "$command_text"; then
        command_argv=("${PARSED_COMMAND_ARGV[@]}")
    else
        command_ready=false
    fi

    if ! prepare_validation_evidence "$id"; then
        printf '%s\n' "validation evidence lookup failed for $id" >"$log_path"
        EVIDENCE_INPUT_FINGERPRINT=unavailable
        EVIDENCE_CACHE_HIT=false
        record_unavailable_or_failed "$enforcement" "validation evidence lookup for $description"
        outcome="failed"
        disposition="not-executed"
    elif [ "${CHECK_COMMAND[$id]:-}" != "$command_text" ]; then
        printf '%s\n' "runner command does not match the canonical registry contract" >"$log_path"
        record_unavailable_or_failed "$enforcement" "runner command contract for $description"
        outcome="failed"
        disposition="not-executed"
    elif [ "$command_ready" != true ]; then
        printf '%s\n' "canonical command cannot be represented as a direct argument vector" >"$log_path"
        record_unavailable_or_failed "$enforcement" "direct argument vector for $description"
        outcome="failed"
        disposition="not-executed"
    elif ! declared_command_target_is_available "${command_argv[@]}"; then
        printf 'canonical command target is missing or unsafe: %s\n' \
            "${command_argv[1]:-unavailable}" >"$log_path"
        record_unavailable_or_failed "$enforcement" "canonical command target for $description"
        outcome="failed"
        disposition="not-executed"
    elif [ "$EVIDENCE_CACHE_HIT" = true ] || [ "$EVIDENCE_RECEIPT_HIT" = true ]; then
        printf 'Reused eligible validation evidence; source=%s; prior_log=%s\n' \
            "$([ "$EVIDENCE_RECEIPT_HIT" = true ] && printf receipt || printf cache)" \
            "$EVIDENCE_PRIOR_LOG" >"$log_path"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        outcome="passed"
        REUSED_CHECKS=$((REUSED_CHECKS + 1))
        disposition="reused"
    else
        set +e
        run_argv_with_timeout "$timeout_seconds" "$log_path" "$result_path" "${command_argv[@]}"
        rc=$?
        set -e
        output=$(cat "$log_path" 2>/dev/null || true)
        if ! verify_supervision_return_contract "$rc" "$result_path"; then
            supervision_contract_valid=false
            record_result=false
        fi
        if [ "$supervision_contract_valid" = true ] &&
            [ "$VERIFIED_SUPERVISION_LAUNCHED" = true ]; then
            [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
            EXECUTED_CHECKS=$((EXECUTED_CHECKS + 1))
        fi
        if [ "$supervision_contract_valid" != true ]; then
            printf '\nValidation supervision result was missing or could not be authenticated.\n' >> "$log_path"
            record_unavailable_or_failed "$enforcement" "$description supervision evidence was invalid"
            outcome="failed"
            disposition="not-executed"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=validation-supervision-evidence-invalid
        elif [ "$rc" -eq 124 ]; then
            record_unavailable_or_failed "$enforcement" "$description timed out after ${timeout_seconds}s"
            outcome="failed"
            disposition="timed-out"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=validation-timeout
        elif [ "$rc" -eq 125 ]; then
            record_unavailable_or_failed "$enforcement" "$description observed repository snapshot drift"
            outcome="failed"
            disposition="snapshot-drift"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=repository-snapshot-drift
        elif [ "$rc" -eq 128 ]; then
            record_unavailable_or_failed "$enforcement" "$description was blocked by repository snapshot drift before launch"
            outcome="failed"
            disposition="snapshot-drift"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=repository-snapshot-drift
        elif [ "$rc" -eq 126 ]; then
            record_unavailable_or_failed "$enforcement" "$description could not prove complete process-tree cleanup"
            outcome="failed"
            disposition="executed"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=process-tree-cleanup-failed
        elif [ "$rc" -eq 130 ]; then
            record_unavailable_or_failed "$enforcement" "$description was cancelled"
            outcome="failed"
            if [ "$VERIFIED_SUPERVISION_LAUNCHED" = true ]; then
                disposition="cancelled"
            else
                disposition="not-executed"
            fi
            VALIDATION_ABORTED=true
            [ -n "$VALIDATION_ABORT_REASON" ] || VALIDATION_ABORT_REASON=validation-cancelled
        elif [ "$rc" -eq 127 ]; then
            record_unavailable_or_failed "$enforcement" "$description could not be launched by the process supervisor"
            outcome="failed"
            disposition="not-executed"
            VALIDATION_ABORTED=true
            VALIDATION_ABORT_REASON=validation-launch-failed
        elif [ "$rc" -eq 0 ]; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            outcome="passed"
        elif reason=$(classify_environment_block "$output"); then
            record_environment_block "$enforcement" "$description" "$reason"
            outcome="blocked-by-environment"
        else
            record_unavailable_or_failed "$enforcement" "$description returned non-zero"
            outcome="failed"
        fi
        disposition=${disposition:-executed}
    fi
    completed_ms=$(now_millis)
    duration_ms=$((completed_ms - started_ms))
    if [ "$disposition" != reused ] &&
        { [ "$EVIDENCE_CACHE_HIT" = true ] || [ "$EVIDENCE_RECEIPT_HIT" = true ]; }; then
        prepare_nonreuse_validation_evidence "$id" || EVIDENCE_INPUT_FINGERPRINT=unavailable
    fi
    if ! record_validation_evidence "$id" "$outcome" "$disposition" "$started_ms" "$completed_ms" "$log_path" "$record_result"; then
        printf '%s\n' "validation evidence record failed for $id" >&2
        if [ "$outcome" = passed ]; then
            PASSED_CHECKS=$((PASSED_CHECKS - 1))
            [ "$disposition" = reused ] && REUSED_CHECKS=$((REUSED_CHECKS - 1))
            record_unavailable_or_failed "$enforcement" "validation evidence record for $description"
            outcome="failed"
        fi
    fi
    record_timing "$id" "$duration_ms" "$description" "$outcome" "$disposition" "$log_path"
    printf '%-36s %-24s %6sms %s\n' "$id" "$outcome" "$duration_ms" "$disposition"
    emit_retained_output "$log_path" "$outcome"
}

# Function to mark a check as pending dotnet-native replacement
run_deferred_check() {
    local script_name=$1
    local description=$2
    local is_critical=$3
    local is_quick=$4
    local reason=${5:-"dotnet-native replacement pending"}

    record_selected_without_execution "$description" "deferred-with-owner" "$reason"
}

run_spec_compliance_check() {
    local spec_file="${SPEC_FILE:-}"
    local task_name="${TASK_NAME:-}"

    if [ -z "$spec_file" ] && [ -z "$task_name" ]; then
        record_selected_without_execution \
            "Spec Implementation Compliance (.NET)" \
            "not-applicable" \
            "SPEC_FILE/TASK_NAME not set"
        return
    fi
    if [ -z "$spec_file" ] || [ -z "$task_name" ]; then
        record_selected_without_execution \
            "Spec Implementation Compliance (.NET)" \
            "failed" \
            "requires both SPEC_FILE and TASK_NAME"
        return
    fi

    run_check "check-spec-compliance.sh" \
        "Spec Implementation Compliance (.NET)" \
        "required" "false" "true" \
        "check-spec-compliance.sh SPEC_FILE TASK_NAME" "$spec_file" "$task_name"
}

source_release_context_available() {
    [ -d "$PROJECT_ROOT/.dev/releases" ] &&
        [ -d "$PROJECT_ROOT/.ai/distribution" ] &&
        [ -f "$PROJECT_ROOT/.ai/scripts/ai_context_package.py" ]
}

run_source_repository_sdk_free_contract() {
    if ! check_is_selected "SDK-Free Framework Contract"; then
        return
    fi
    if ! source_release_context_available; then
        record_selected_without_execution \
            "SDK-Free Framework Contract" \
            "not-applicable" \
            "source framework test not packaged"
        return
    fi

    run_command_check "python .ai/scripts/tests/test_sdk_free_framework_contract.py -v" \
        "SDK-Free Framework Contract" \
        "required" "true" "true"
}

run_source_repository_engineering_guardrails_provider_contract() {
    if ! check_is_selected "Engineering Guardrails Provider Contract"; then
        return
    fi
    if ! source_release_context_available; then
        record_selected_without_execution \
            "Engineering Guardrails Provider Contract" \
            "not-applicable" \
            "source framework test not packaged"
        return
    fi

    run_command_check "python .ai/scripts/tests/test_engineering_guardrails_provider_contract.py -v" \
        "Engineering Guardrails Provider Contract" \
        "required" "true" "true"
}

run_source_repository_release_checks() {
    local description
    if ! source_release_context_available; then
        for description in \
            "Governance Term Routing And Release Projection Contract" \
            "AI Context Version Governance Fail-Closed Tests" \
            "AI Context Packaging GWT Tests" \
            "AI Context Release State Fail-Closed Tests" \
            "AI Context Release Preparation Fail-Closed Tests" \
            "AI Context Release Renderer Fail-Closed Tests" \
            "AI Behavior Deterministic Evaluation" \
            "AI Context Load Measurement Contract" \
            "Repository Configuration Ownership Contract" \
            "Repository Configuration Ownership Fail-Closed Tests" \
            "Skill Transition Compatibility Contract" \
            "Skill Transition Compatibility Fail-Closed Tests" \
            "Effective Rule Packet Resolution and Consumer Parity Tests" \
            "Effective Rule Action Skill Consumption Contract"; do
            record_selected_without_execution \
                "$description" \
                "not-applicable" \
                "source release context not packaged"
        done
        return
    fi

    run_command_check "python .ai/scripts/tests/test_governance_term_routing_contract.py -v" \
        "Governance Term Routing And Release Projection Contract" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_ai_context_version_governance.py -v" \
        "AI Context Version Governance Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_ai_context_packaging.py -v" \
        "AI Context Packaging GWT Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_ai_context_release_state.py -v" \
        "AI Context Release State Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_prepare_ai_context_release.py -v" \
        "AI Context Release Preparation Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_release_notes_renderer.py -v" \
        "AI Context Release Renderer Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_ai_behavior_evaluation.py -v" \
        "AI Behavior Deterministic Evaluation" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_ai_context_load_measurement.py -v" \
        "AI Context Load Measurement Contract" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/validate-repository-config-contract.py" \
        "Repository Configuration Ownership Contract" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_repository_config_contract.py -v" \
        "Repository Configuration Ownership Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/validate-skill-transition.py" \
        "Skill Transition Compatibility Contract" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_skill_transition_contract.py -v" \
        "Skill Transition Compatibility Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_ai_context_effective_rules.py -v" \
        "Effective Rule Packet Resolution and Consumer Parity Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_effective_rule_action_skill_contract.py -v" \
        "Effective Rule Action Skill Consumption Contract" \
        "required" "true" "true"
}

run_ai_context_version_check() {
    if source_release_context_available; then
        record_selected_without_execution \
            "AI Context Target Apply, Provenance And Customization Contracts" \
            "not-applicable" \
            "source release context owns version validation"
        run_command_check "python .ai/scripts/validate-ai-context-versions.py" \
            "AI Context Release And Version Contracts" \
            "required" "true" "true"
    elif [ -f "$PROJECT_ROOT/.dev/ai-context/provenance.yaml" ] || \
         [ -f "$PROJECT_ROOT/.dev/AI-CONTEXT-APPLY-PENDING.yaml" ]; then
        run_command_check "python .ai/scripts/validate-ai-context-target.py" \
            "AI Context Target Apply, Provenance And Customization Contracts" \
            "required" "true" "true"
        record_selected_without_execution \
            "AI Context Release And Version Contracts" \
            "not-applicable" \
            "source release context not packaged"
    else
        record_selected_without_execution \
            "AI Context Target Apply, Provenance And Customization Contracts" \
            "not-applicable" \
            "target provenance not initialized"
        record_selected_without_execution \
            "AI Context Release And Version Contracts" \
            "not-applicable" \
            "source release context not packaged"
    fi
}

source_governance_context_available() {
    source_release_context_available &&
        [ -f "$PROJECT_ROOT/.github/workflows/governance.yml" ] &&
        [ -f "$PROJECT_ROOT/.ai/distribution/governance-checks.yaml" ] &&
        [ -f "$PROJECT_ROOT/.ai/scripts/validate-source-governance.py" ]
}

run_source_repository_governance_checks() {
    local description
    if ! source_governance_context_available; then
        for description in \
            "Source Governance Manifest Registry" \
            "Terminal Issue Closure Contract" \
            "Terminal Issue Closure Fail-Closed Tests" \
            "Repository Identity Drift Fail-Closed Tests"; do
            record_selected_without_execution \
                "$description" \
                "not-applicable" \
                "source governance registry not packaged"
        done
        for description in \
            "Governance Pull-Request Workflow Contract" \
            "GitHub Workflow Lifecycle Contract"; do
            record_selected_without_execution \
                "$description" \
                "not-applicable" \
                "source CI workflow not packaged"
        done
        return
    fi

    run_command_check "python .ai/scripts/validate-source-governance.py" \
        "Source Governance Manifest Registry" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/validate-terminal-issue-closure.py" \
        "Terminal Issue Closure Contract" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_terminal_issue_closure.py -v" \
        "Terminal Issue Closure Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_repository_identity.py -v" \
        "Repository Identity Drift Fail-Closed Tests" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_governance_workflow_contract.py -v" \
        "Governance Pull-Request Workflow Contract" \
        "required" "true" "true"

    run_command_check "python .ai/scripts/tests/test_github_workflow_contract.py -v" \
        "GitHub Workflow Lifecycle Contract" \
        "required" "true" "true"
}

run_source_package_smoke() {
    if ! check_is_selected "AI Context Package Smoke Tests"; then
        return
    fi
    if ! source_release_context_available; then
        record_selected_without_execution \
            "AI Context Package Smoke Tests" \
            "not-applicable" \
            "source package builder not packaged"
        return
    fi
    run_command_check "python .ai/scripts/tests/test_ai_context_package_smoke.py -v" \
        "AI Context Package Smoke Tests" \
        "required" "true" "true"
}

# Header
echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║    Profile-driven Project Check        ║${NC}"
echo -e "${MAGENTA}║    Profile: ${YELLOW}$PROFILE${MAGENTA}                     ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Starting checks at $(date '+%Y-%m-%d %H:%M:%S')${NC}"

# ====================================================================
# Critical Checks (always run in quick and critical modes)
# ====================================================================

echo ""
echo -e "${MAGENTA}════ Critical Checks ════${NC}"

run_command_check "python .ai/scripts/validate-assessment-artifacts.py" \
    "Assessment Artifact Metadata" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_assessment_artifacts.py -v" \
    "Assessment Artifact Fail-Closed Tests" \
    "required" "true" "true"

  run_command_check "python .ai/scripts/validate-workflow-artifacts.py" \
      "Workflow Artifact Metadata" \
      "required" "true" "true"

run_command_check "python .ai/assets/skills/software-development-orchestrator/scripts/tests/test_workflow_implementation_contract.py -v" \
      "Workflow Implementation Contract Fail-Closed Tests" \
      "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_workflow_lifecycle_contract.py -v" \
    "Workflow Lifecycle Contract Fail-Closed Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_git_commit_policy.py -v" \
    "Git Commit Policy Fail-Closed Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_workflow_handoff.py -v" \
    "Workflow Handoff Fail-Closed Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/validate-workflow-handoff.py --all" \
    "Registered Workflow Handoff Checkpoints" \
    "required" "true" "true"

run_command_check "python .ai/assets/skills/software-development-orchestrator/scripts/tests/test_software_development_orchestrator_capability_contract.py -v" \
    "Development Workflow Capability Contract" \
    "required" "true" "true"

run_command_check "python .ai/assets/skills/software-development-orchestrator/scripts/tests/test_software_development_orchestrator_acceptance.py -v" \
    "Development Workflow Deterministic Acceptance" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_skill_script_colocation.py -v" \
    "Canonical Skill Script Colocation Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_semantic_customization_lifecycle.py -v" \
    "Semantic Customization Lifecycle" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_semantic_customization_skill_contract.py -v" \
    "Semantic Customization Skill Contract" \
    "required" "true" "true"

if [ -n "${COMMIT_RANGE:-}" ]; then
    COMMIT_VALIDATION_ARGV=(
        "$PYTHON_EXECUTABLE"
        ".ai/scripts/validate-git-commits.py"
        "--range"
        "$COMMIT_RANGE"
    )
    if [ -n "${WORKFLOW_ID:-}" ]; then
        COMMIT_VALIDATION_ARGV+=("--workflow-id" "$WORKFLOW_ID")
    fi
    run_command_check \
        "python .ai/scripts/validate-git-commits.py --range COMMIT_RANGE [--workflow-id WORKFLOW_ID]" \
        "Selected Git Commit Messages" \
        "required" "true" "true" \
        "${COMMIT_VALIDATION_ARGV[@]}"
else
    record_selected_without_execution \
        "Selected Git Commit Messages" \
        "not-applicable" \
        "COMMIT_RANGE not set"
fi

run_command_check "python .ai/scripts/validate-ai-context.py" \
    "AI Context Navigation and Runtime Contracts" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_ai_context_wrapper_metadata.py -v" \
    "AI Context Wrapper Semantic Contract Fail-Closed Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_ai_context_language_policy.py -v" \
    "AI Context Language And Bilingual Parity Fail-Closed Tests" \
    "required" "true" "true"

run_ai_context_version_check

run_source_repository_release_checks

run_command_check "python .ai/scripts/tests/test_ai_context_package_apply.py -v" \
    "AI Context Safe Apply GWT Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_payload_user_view_contract.py -v" \
    "Selected Payload User-View Fail-Closed Contract" \
    "required" "true" "true"

run_source_package_smoke

run_command_check "python .ai/scripts/tests/test_ai_context_packaging.py UpgradeRoutePackageProjectionGwtTests -v" \
    "AI Context Upgrade Route Package Projection" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_ai_context_packaging.py ProviderRolePackageProjectionGwtTests -v" \
    "Provider-Neutral Role Package Projection" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_ai_context_multi_hop_upgrade.py -v" \
    "AI Context Multi-Hop Upgrade Transaction GWT Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/validate-dependency-versions.py" \
    "Offline Dependency And Version Consistency" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_dependency_version_consistency.py -v" \
    "Dependency And Version Consistency Fail-Closed Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_python_source_entrypoints.py -v" \
    "Source-Only Python Entrypoint Prerequisite Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/validate-shell-assets.py" \
    "Shell Asset Classification And Git Modes" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_file_disposition_manifest.py -v" \
    "File Disposition Manifest Fail-Closed Tests" \
    "required" "true" "true"

run_source_repository_governance_checks

run_command_check "python .ai/scripts/tests/test_ai_context_release_closeout.py -v" \
    "Source-Only Release Closeout Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_fail_closed_validation.py -v" \
    "Aggregate Runner And Shell Registry Fail-Closed Tests" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_validation_profile_registry.py -v" \
    "Validation Profile Registry Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_validation_process_supervisor.py -v" \
    "Validation Process Supervisor Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_validation_evidence.py ValidationEvidenceRoutineContractGwtTests -v" \
    "Validation Execution Evidence Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_validation_evidence.py -v" \
    "Validation Execution Evidence Exhaustive Contract" \
    "required" "true" "true"

if immutable_history_source_context_available; then
    run_command_check "python .ai/scripts/tests/test_immutable_history_validation.py -v" \
        "Immutable History Validation Contract" \
        "required" "true" "true"
elif check_is_selected "Immutable History Validation Contract"; then
    record_selected_without_execution \
        "Immutable History Validation Contract" \
        "not-applicable" \
        "source history not packaged"
fi

run_command_check "python .ai/scripts/tests/test_coding_standards_integrity_contract.py -v" \
    "Coding Standards Integrity Claim Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_code_reviewer_routing_contract.py -v" \
    "Code Reviewer Routing Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_profile_projection_contract.py -v" \
    "Profile Projection Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_document_projection_contract.py -v" \
    "Documentation Projection Contract" \
    "required" "true" "true"

run_command_check "python .ai/scripts/tests/test_ai_context_source_include_evidence.py -v" \
    "Source-Include Evidence Contract" \
    "required" "true" "true"

# Coding standards are fundamental for AI context and standards docs
run_check "check-coding-standards.sh" \
    "Coding Standards Structural Integrity" \
    "required" "true" "true" \
    "check-coding-standards.sh"

run_source_repository_sdk_free_contract
run_source_repository_engineering_guardrails_provider_contract

# Optional target analyzers and configuration tests are target-selected and are
# never framework-owned required checks.

# ====================================================================
# Important Checks (run in full and quick modes)
# ====================================================================

if check_is_selected "Spec Implementation Compliance (.NET)"; then
    echo ""
    echo -e "${MAGENTA}════ Important Checks ════${NC}"
    
    # Aggregate and UseCase source validation is covered by DBA1002-DBA1003 and DBA1009-DBA1012.
    
    # Controller compliance is covered by DBA1004-DBA1006 in analyzer tests.

    # Projection source and EF model registration are covered by DBA1013 and configuration validation tests.
    
    # Spec compliance is important
    run_spec_compliance_check
    
fi

# ====================================================================
# Additional Checks (only in full mode)
# ====================================================================

if [ "$PROFILE" == "nightly-full" ] ||
    check_is_selected "Test DI Compliance" ||
    check_is_selected "Template Synchronization" ||
    check_is_selected "ADR Index Update"; then
    echo ""
    echo -e "${MAGENTA}════ Additional Checks ════${NC}"

    # Test DI compliance helper remains transitional
    run_deferred_check "check-test-di-compliance.sh" \
        "Test DI Compliance" \
        "true" "false" "replace with analyzer or test architecture rules"
    
    # Template sync check (dotnet-native replacement not yet available)
    run_deferred_check "check-template-sync.sh" \
        "Template Synchronization" \
        "false" "false" "dotnet-native replacement not yet available"
    
    # ADR index update (dotnet-native replacement not yet available)
    run_deferred_check "update-adr-index.sh" \
        "ADR Index Update" \
        "false" "false" "dotnet-native replacement not yet available"
    
    # Add ADR script (if needed)
    if [ -f "$SCRIPT_DIR/add-adr.sh" ]; then
        echo -e "${CYAN}ℹ${NC} add-adr.sh is available for creating new ADRs"
    fi
fi

# ====================================================================
# Results Summary
# ====================================================================

if ! write_final_fingerprint_selection; then
    echo -e "${RED}✗ FAILED${NC}: final fingerprint selection could not be bound to evidence events"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
fi
record_runner_abort_failure

echo ""
echo -e "${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║           Check Results Summary        ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo ""

# Calculate statistics
if [ $TOTAL_CHECKS -gt 0 ]; then
    PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
else
    PASS_RATE=0
fi

FINALIZATION_FAILED=false
if ! EVIDENCE_SNAPSHOT_REF=$(repo_relative_artifact "$EVIDENCE_SNAPSHOT") ||
    ! EVIDENCE_POST_SNAPSHOT_REF=$(repo_relative_artifact "$EVIDENCE_POST_SNAPSHOT") ||
    ! EVIDENCE_CACHE_REF=$(repo_relative_artifact "$EVIDENCE_CACHE") ||
    ! EVIDENCE_PATH_REF=$(repo_relative_artifact "$EVIDENCE_PATH") ||
    ! EVIDENCE_EVENTS_REF=$(repo_relative_artifact "$EVIDENCE_EVENTS") ||
    ! EVIDENCE_SUMMARY_REF=$(repo_relative_artifact "$EVIDENCE_SUMMARY") ||
    ! EVIDENCE_WORKFLOW_SUMMARY_REF=$(repo_relative_artifact "$EVIDENCE_WORKFLOW_SUMMARY") ||
    ! EVIDENCE_SELECTED_CHECKS_REF=$(repo_relative_artifact "$EVIDENCE_SELECTED_CHECKS") ||
    ! EVIDENCE_SELECTION_REF=$(repo_relative_artifact "$EVIDENCE_SELECTION") ||
    ! EVIDENCE_PREPARATION_SELECTION_REF=$(repo_relative_artifact "$EVIDENCE_PREPARATION_SELECTION") ||
    ! EVIDENCE_CHANGED_PATHS_REF=$(repo_relative_artifact "$EVIDENCE_CHANGED_PATHS") ||
    ! EVIDENCE_SELECTION_COMPARISON_REF=$(repo_relative_artifact "$EVIDENCE_SELECTION_COMPARISON") ||
    ! EVIDENCE_STAGED_MANIFEST_REF=$(repo_relative_artifact "$EVIDENCE_STAGED_MANIFEST") ||
    ! EVIDENCE_SEALED_MANIFEST_REF=$(repo_relative_artifact "$EVIDENCE_SEALED_MANIFEST") ||
    ! EVIDENCE_SEAL_SUPERVISION_LOG_REF=$(repo_relative_artifact "$EVIDENCE_SEAL_SUPERVISION_LOG") ||
    ! EVIDENCE_SEAL_SUPERVISION_RESULT_REF=$(repo_relative_artifact "$EVIDENCE_SEAL_SUPERVISION_RESULT"); then
    echo -e "${RED}✗ FAILED${NC}: validation artifacts could not be represented as repository-relative paths"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    FINALIZATION_FAILED=true
fi

if [ "$FINALIZATION_FAILED" = false ] && ! run_supervised_control post-snapshot 60 \
    "$PYTHON_EXECUTABLE" .ai/scripts/validation-evidence.py verify-snapshot \
    --repo . \
    --snapshot "$EVIDENCE_SNAPSHOT_REF" \
    --output "$EVIDENCE_POST_SNAPSHOT_REF"; then
    echo -e "${RED}✗ FAILED${NC}: repository identity could not be supervised through final snapshot verification"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    FINALIZATION_FAILED=true
fi
record_runner_abort_failure

finalize_control_argv=(
    "$PYTHON_EXECUTABLE"
    .ai/scripts/validation-evidence.py
    finalize
    --repo .
    --cache "$EVIDENCE_CACHE_REF"
    --evidence "$EVIDENCE_PATH_REF"
    --events "$EVIDENCE_EVENTS_REF"
    --invocation-id "$INVOCATION_ID"
    --profile "$PROFILE"
    --environment-class "$EVIDENCE_ENVIRONMENT_CLASS"
    --snapshot "$EVIDENCE_SNAPSHOT_REF"
)
if [ "$IMMUTABLE_HISTORY_PREPARATION_ACTIVE" = true ]; then
    finalize_control_argv+=(--preparation-python "$PYTHON_EXECUTABLE")
fi
if [ "$FINALIZATION_FAILED" = false ] &&
    ! run_supervised_control finalize 60 "${finalize_control_argv[@]}"; then
    echo -e "${RED}✗ FAILED${NC}: validation evidence records could not be supervised through finalization"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    FINALIZATION_FAILED=true
fi
record_runner_abort_failure

if [ "$FINALIZATION_FAILED" = false ] && ! run_supervised_control summarize 60 \
    "$PYTHON_EXECUTABLE" .ai/scripts/validation-evidence.py summarize \
    --evidence "$EVIDENCE_PATH_REF" \
    --output "$EVIDENCE_SUMMARY_REF" \
    --invocation-id "$INVOCATION_ID" \
    --profile "$PROFILE"; then
    echo -e "${RED}✗ FAILED${NC}: validation evidence summary could not be supervised"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    FINALIZATION_FAILED=true
fi
record_runner_abort_failure

TOTAL_ELAPSED=$((SECONDS - TOTAL_ELAPSED_START))
workflow_summary_control_argv=(
    "$PYTHON_EXECUTABLE"
    .ai/scripts/validation-evidence.py
    workflow-summary
    --evidence "$EVIDENCE_PATH_REF"
    --output "$EVIDENCE_WORKFLOW_SUMMARY_REF"
    --invocation-id "$INVOCATION_ID"
    --profile "$PROFILE"
    --wall-span-ms "$((TOTAL_ELAPSED * 1000))"
)
if [ -n "${WORKFLOW_ID:-}" ]; then
    workflow_summary_control_argv+=(--workflow-id "$WORKFLOW_ID")
fi
if [ "$FINALIZATION_FAILED" = false ] &&
    ! run_supervised_control workflow-summary 60 "${workflow_summary_control_argv[@]}"; then
    echo -e "${RED}✗ FAILED${NC}: workflow evidence summary could not be supervised"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    FINALIZATION_FAILED=true
fi
record_runner_abort_failure

INVOCATION_OUTCOME=passed
record_runner_abort_failure
if [ "$VALIDATION_ABORTED" = true ] || [ "$FAILED_CHECKS" -gt 0 ] ||
    [ "$REQUIRED_DEFERRED" -gt 0 ]; then
    INVOCATION_OUTCOME=failed
elif [ "$BLOCKED_CHECKS" -gt 0 ]; then
    INVOCATION_OUTCOME=blocked
fi
seal_child_argv=(
    "$PYTHON_EXECUTABLE"
    .ai/scripts/validation-evidence.py
    seal-invocation
    --repo .
    --snapshot "$EVIDENCE_SNAPSHOT_REF"
    --post-snapshot "$EVIDENCE_POST_SNAPSHOT_REF"
    --evidence "$EVIDENCE_PATH_REF"
    --summary "$EVIDENCE_SUMMARY_REF"
    --workflow-summary "$EVIDENCE_WORKFLOW_SUMMARY_REF"
    --selection "$EVIDENCE_SELECTED_CHECKS_REF"
    --preparation-selection "$EVIDENCE_PREPARATION_SELECTION_REF"
    --fingerprint-selection "$EVIDENCE_SELECTION_REF"
    --events "$EVIDENCE_EVENTS_REF"
    --changed-paths "$EVIDENCE_CHANGED_PATHS_REF"
    --selection-comparison "$EVIDENCE_SELECTION_COMPARISON_REF"
    --output "$EVIDENCE_STAGED_MANIFEST_REF"
    --publication-output "$EVIDENCE_SEALED_MANIFEST_REF"
    --cache "$EVIDENCE_CACHE_REF"
    --invocation-id "$INVOCATION_ID"
    --control-python "$PYTHON_EXECUTABLE"
)
for control_role in bootstrap-snapshot prepare post-snapshot finalize summarize workflow-summary; do
    if [ -z "${EVIDENCE_CONTROL_RESULT_BY_ROLE[$control_role]:-}" ] ||
        ! control_result_ref=$(repo_relative_artifact "${EVIDENCE_CONTROL_RESULT_BY_ROLE[$control_role]}"); then
        FINALIZATION_FAILED=true
        break
    fi
    seal_child_argv+=(--control-result "$control_role" "$control_result_ref")
done
seal_child_argv+=(
    --terminal-result "$EVIDENCE_SEAL_SUPERVISION_RESULT_REF"
    --terminal-log "$EVIDENCE_SEAL_SUPERVISION_LOG_REF"
)
if [ "$IMMUTABLE_HISTORY_PREPARATION_ACTIVE" = true ]; then
    if ! IMMUTABLE_HISTORY_PREPARATION_RESULT_REF=$(repo_relative_artifact "$IMMUTABLE_HISTORY_PREPARATION_RESULT"); then
        FINALIZATION_FAILED=true
    fi
    seal_child_argv+=(
        --preparation-python "$PYTHON_EXECUTABLE"
        --preparation-result "$IMMUTABLE_HISTORY_PREPARATION_RESULT_REF"
    )
fi
record_runner_abort_failure
if [ "$RUNNER_ABORT_FAILURE_RECORDED" = true ]; then
    INVOCATION_OUTCOME=failed
fi
seal_child_argv+=(--outcome "$INVOCATION_OUTCOME")
seal_rc=1
if [ "$FINALIZATION_FAILED" = false ]; then
    set +e
    run_control_supervisor_cli supervise \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT" \
        --log-path "$EVIDENCE_SEAL_SUPERVISION_LOG" \
        --result-path "$EVIDENCE_SEAL_SUPERVISION_RESULT" \
        --timeout-seconds 90 \
        --cwd-ref . \
        -- "${seal_child_argv[@]}"
    seal_rc=$?
    set -e
fi
terminal_supervision_valid=false
authenticated_staged_manifest_digest=
if [ "$FINALIZATION_FAILED" = false ] && [ "$RUNNER_CANCELLED_BY_SIGNAL" != true ] &&
    verify_supervision_return_contract "$seal_rc" "$EVIDENCE_SEAL_SUPERVISION_RESULT" &&
    [ "$seal_rc" -eq 0 ] && [ "$VERIFIED_SUPERVISION_STATUS" = completed ] &&
    [ "$VERIFIED_SUPERVISION_LAUNCHED" = true ] && [ "$VERIFIED_SUPERVISION_EXIT" = 0 ] &&
    [ -f "$EVIDENCE_STAGED_MANIFEST" ] && [ ! -e "$EVIDENCE_SEALED_MANIFEST" ]; then
    terminal_supervision_valid=true
fi
if [ "$terminal_supervision_valid" = true ]; then
    authenticated_staged_manifest_digest=$(python .ai/scripts/validation-evidence.py \
        verify-terminal-invocation \
        --repo "$PROJECT_ROOT" \
        --snapshot "$EVIDENCE_SNAPSHOT_REF" \
        --manifest "$EVIDENCE_STAGED_MANIFEST_REF" \
        --result-path "$EVIDENCE_SEAL_SUPERVISION_RESULT_REF" \
        -- "${seal_child_argv[@]}") || authenticated_staged_manifest_digest=
    if [[ ! "$authenticated_staged_manifest_digest" =~ ^[0-9a-f]{64}$ ]]; then
        terminal_supervision_valid=false
    fi
fi
if [ "$terminal_supervision_valid" != true ] ||
    [ "$RUNNER_CANCELLED_BY_SIGNAL" = true ]; then
    rm -f -- "$EVIDENCE_STAGED_MANIFEST"
    echo -e "${RED}✗ FAILED${NC}: validation invocation artifacts could not be sealed"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
else
    if ! ln -- "$EVIDENCE_STAGED_MANIFEST" "$EVIDENCE_SEALED_MANIFEST" ||
        [ ! -f "$EVIDENCE_SEALED_MANIFEST" ]; then
        rm -f -- "$EVIDENCE_STAGED_MANIFEST"
        echo -e "${RED}✗ FAILED${NC}: sealed invocation manifest could not be published without overwrite"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    else
        published_manifest_digest=$(sha256_regular_file "$EVIDENCE_SEALED_MANIFEST")
        if [ "$published_manifest_digest" != "$authenticated_staged_manifest_digest" ]; then
            remove_owned_terminal_publication
            echo -e "${RED}✗ FAILED${NC}: published invocation manifest changed during atomic read-back"
            printf 'authenticated-manifest-digest: %s\npublished-manifest-digest: %s\n' \
                "$authenticated_staged_manifest_digest" "$published_manifest_digest"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
        else
            EVIDENCE_SEAL_PUBLISHED=true
            rm -f -- "$EVIDENCE_STAGED_MANIFEST"
        fi
    fi
fi
record_runner_abort_failure
if [ "$RUNNER_CANCELLED_BY_SIGNAL" = true ]; then
    remove_owned_terminal_publication
fi
TOTAL_ELAPSED=$((SECONDS - TOTAL_ELAPSED_START))
PROFILE_BUDGET_SECONDS=${PROFILE_BUDGET[$PROFILE]:-}
if [ -n "$PROFILE_BUDGET_SECONDS" ] && [ "$TOTAL_ELAPSED" -gt "$PROFILE_BUDGET_SECONDS" ]; then
    if [ "${PROFILE_ENFORCEMENT[$PROFILE]}" = report-and-warn ]; then
        WARNINGS=$((WARNINGS + 1))
        echo -e "${YELLOW}⚠ ADVISORY${NC}: profile=$PROFILE exceeded its ${PROFILE_BUDGET_SECONDS}s budget (${TOTAL_ELAPSED}s measured)"
    else
        echo -e "${CYAN}ℹ${NC} MEASURED: profile=$PROFILE exceeded its ${PROFILE_BUDGET_SECONDS}s budget (${TOTAL_ELAPSED}s measured)"
    fi
fi

# The concise summary deliberately separates outcome from execution disposition.
record_runner_abort_failure
echo "summary: profile=$PROFILE selected=$TOTAL_CHECKS executed=$EXECUTED_CHECKS reused=$REUSED_CHECKS failed=$FAILED_CHECKS blocked=$BLOCKED_CHECKS warnings=$WARNINGS deferred=$DEFERRED_CHECKS not-applicable=$NOT_APPLICABLE"
echo "full-log: $LOG_DIR"
echo "evidence: $EVIDENCE_PATH"
if [ "$EVIDENCE_SEAL_PUBLISHED" = true ]; then
    echo "sealed-manifest: $EVIDENCE_SEALED_MANIFEST"
    echo "seal-supervision-result: $EVIDENCE_SEAL_SUPERVISION_RESULT"
else
    echo "sealed-manifest: unavailable"
    echo "seal-supervision-result: unavailable"
fi
echo -e "Required Selected: ${CYAN}$REQUIRED_SELECTED${NC}"
echo -e "Required Executed: ${CYAN}$REQUIRED_RUN${NC}"
echo -e "Required Failed: ${RED}$REQUIRED_FAILED${NC}"
echo -e "Required Blocked: ${YELLOW}$REQUIRED_BLOCKED${NC}"
echo -e "Required Deferred: ${YELLOW}$REQUIRED_DEFERRED${NC}"

echo ""
if [ "$VERBOSE" = true ] && [ ${#CHECK_TIMINGS[@]} -gt 0 ]; then
    echo -e "${MAGENTA}──── Elapsed By Check (slowest first) ────${NC}"
    printf '%s\n' "${CHECK_TIMINGS[@]}" \
        | sort -t'|' -k1,1nr \
        | head -15 \
        | while IFS='|' read -r millis outcome disposition id description log_ref; do
            printf "  %6sms  %-24s %-10s %s\n" "$millis" "$id" "$outcome" "$log_ref"
        done
fi
echo -e "  ${CYAN}Total wall time: ${TOTAL_ELAPSED}s across $TOTAL_CHECKS selected checks${NC}"
echo "AI_CONTEXT_CHECK_TIMING total_seconds=${TOTAL_ELAPSED} profile=${PROFILE} checks=${TOTAL_CHECKS} executed=${EXECUTED_CHECKS} reused=${REUSED_CHECKS} failed=${FAILED_CHECKS} blocked=${BLOCKED_CHECKS}"

if [ ${#BLOCKED_LIST[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}──── Blocked By Environment (do NOT remediate code) ────${NC}"
    printf '%s\n' "${BLOCKED_LIST[@]}" | while IFS='|' read -r reason description; do
        printf "  %-24s %s\n" "$reason" "$description"
    done
    echo -e "  ${CYAN}These are host/runtime conditions. Prepare the environment, then re-run.${NC}"
fi

echo ""
echo -e "${BLUE}Completed at $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""

# Overall status
record_runner_abort_failure
finish_validation_successfully() {
    trap 'request_validation_cancellation INT; exit 1' INT
    trap 'request_validation_cancellation TERM; exit 1' TERM
    trap 'request_validation_cancellation HUP; exit 1' HUP
    [ "$VALIDATION_ABORTED" != true ] || exit 1
    exit 0
}
if [ "$VALIDATION_ABORTED" != true ] && [ $FAILED_CHECKS -eq 0 ] && [ $BLOCKED_CHECKS -eq 0 ] && [ $WARNINGS -eq 0 ] && [ $REQUIRED_DEFERRED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║    ✓ All Checks Passed Successfully!   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    finish_validation_successfully
elif [ "$VALIDATION_ABORTED" != true ] && [ $FAILED_CHECKS -eq 0 ] && [ $BLOCKED_CHECKS -eq 0 ] && [ $REQUIRED_DEFERRED -eq 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠ Passed with $WARNINGS Advisory Warning(s) ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    finish_validation_successfully
elif [ "$VALIDATION_ABORTED" != true ] && [ $FAILED_CHECKS -eq 0 ] && [ $REQUIRED_DEFERRED -eq 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⊘ $BLOCKED_CHECKS check(s) blocked by environment  ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Do NOT modify repository code for these."
    echo "2. Prepare the host prerequisite listed above."
    echo "3. Re-run. Exit code 3 means unverified, never passed."
    exit 3
elif [ "$VALIDATION_ABORTED" != true ] && [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${RED}╔═══════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⊖ $REQUIRED_DEFERRED required check(s) remain deferred   ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════╝${NC}"
    echo "Required deferred validation is retained evidence, not a passing result."
    exit 1
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║    ✗ $FAILED_CHECKS Check(s) Failed!              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    
    # Provide helpful next steps
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Review the failed checks above"
    echo "2. Run individual scripts for detailed errors"
    echo "3. Fix the issues and run this check again"
    echo ""
    
    exit 1
fi
