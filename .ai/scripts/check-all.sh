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
declare -A SELECTED_CHECK_IDS=()
declare -A SELECTION_REASON_BY_ID=()
declare -A CHANGED_PATHS=()
declare -A IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID=()
CHANGED_PATHS_DIGEST=unavailable
SELECTION_MODE=profile-full
SELECTION_ESCALATION_REASON=
IMMUTABLE_HISTORY_SOURCE_CONTEXT=false
IMMUTABLE_HISTORY_FORCE_FULL=false
IMMUTABLE_HISTORY_MODE=downstream-target-local
IMMUTABLE_HISTORY_REASON=not-source-repository
IMMUTABLE_HISTORY_FINGERPRINT=
IMMUTABLE_HISTORY_RECEIPT_SOURCE=

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
}

select_with_dependencies() {
    local id=$1 dependency
    [ -n "${CHECK_DESCRIPTION[$id]:-}" ] || return 1
    [ -n "${SELECTED_CHECK_IDS[$id]:-}" ] && return 0
    SELECTED_CHECK_IDS["$id"]=selected
    for dependency in ${CHECK_DEPENDS[$id]}; do
        select_with_dependencies "$dependency" || return 1
    done
}

prepare_full_profile_selection() {
    local reason=$1 id
    SELECTED_CHECK_IDS=()
    for id in "${CHECK_IDS[@]}"; do
        if profiles_include "${CHECK_PROFILES[$id]}" "$PROFILE"; then
            select_with_dependencies "$id" || return 1
        fi
    done
    for id in "${!SELECTED_CHECK_IDS[@]}"; do
        SELECTION_REASON_BY_ID["$id"]="full-profile-escalation:$reason"
    done
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
    local base=$1 head=$2 path id owned active_owned
    if ! collect_changed_paths "$base" "$head"; then
        SELECTION_ESCALATION_REASON=changed-path-diff-unavailable
        prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        return
    fi
    for path in "${!CHANGED_PATHS[@]}"; do
        if is_global_invalidator "$path"; then
            SELECTION_ESCALATION_REASON=global-invalidator
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
            return
        fi
        owned=false
        active_owned=false
        for id in "${CHECK_IDS[@]}"; do
            if input_owns_path "$path" "${CHECK_INPUT_PATHS[$id]}"; then
                owned=true
                if profiles_include "${CHECK_PROFILES[$id]}" "$PROFILE"; then
                    active_owned=true
                    SELECTED_CHECK_IDS["$id"]=selected
                    SELECTION_REASON_BY_ID["$id"]=changed-path-match
                fi
            fi
        done
        if [ "$owned" = false ]; then
            SELECTION_ESCALATION_REASON=unknown-impact-path
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
            return
        fi
    done
    for id in "${!SELECTED_CHECK_IDS[@]}"; do
        select_with_dependencies "$id" || {
            SELECTION_ESCALATION_REASON=dependency-resolution-failed
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
            return
        }
    done
    for id in "${!SELECTED_CHECK_IDS[@]}"; do
        [ -n "${SELECTION_REASON_BY_ID[$id]:-}" ] || SELECTION_REASON_BY_ID["$id"]=dependency-expansion
    done
    SELECTION_MODE=changed-path
}

prepare_profile_selection() {
    local implicit_base
    if [ -n "$BASE_SHA" ] || [ -n "$HEAD_SHA" ]; then
        if [ -z "$BASE_SHA" ] || [ -z "$HEAD_SHA" ] ||
            ! git rev-parse --verify "${BASE_SHA}^{commit}" >/dev/null 2>&1 ||
            ! git rev-parse --verify "${HEAD_SHA}^{commit}" >/dev/null 2>&1; then
            SELECTION_ESCALATION_REASON=comparison-base-unavailable
            prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
        else
            prepare_changed_path_selection "$BASE_SHA" "$HEAD_SHA"
        fi
    elif implicit_base=$(git merge-base HEAD '@{upstream}' 2>/dev/null); then
        prepare_changed_path_selection "$implicit_base" HEAD
    else
        SELECTION_ESCALATION_REASON=comparison-base-unavailable
        prepare_full_profile_selection "$SELECTION_ESCALATION_REASON"
    fi
    for id in "${CHECK_IDS[@]}"; do
        [ -n "${SELECTION_REASON_BY_ID[$id]:-}" ] || SELECTION_REASON_BY_ID["$id"]=not-selected-unmatched-input-contract
    done
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
    select_with_dependencies "$id" || return 1
    SELECTION_REASON_BY_ID["$id"]=$reason
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
    local output rc outcome reason source_revision source_tree receipt_commit reusable_ids id
    if ! immutable_history_source_context_available; then
        return 0
    fi
    IMMUTABLE_HISTORY_SOURCE_CONTEXT=true

    case "$PROFILE" in
        release)
            select_immutable_history_full_checks release-candidate
            return
            ;;
        nightly-full)
            select_immutable_history_full_checks scheduled-governance
            return
            ;;
        fast|pr)
            select_immutable_history_check workflow-artifacts immutable-history-routine-proof || return 1
            select_immutable_history_check assessment-artifacts immutable-history-routine-proof || return 1
            select_immutable_history_check source-ai-context-version immutable-history-routine-proof || return 1
            ;;
        *)
            return 0
            ;;
    esac

    if [ ! -f "$IMMUTABLE_HISTORY_HELPER" ] ||
        [ ! -f "$IMMUTABLE_HISTORY_CONTRACT" ] ||
        [ ! -f "$IMMUTABLE_HISTORY_RECEIPT" ]; then
        select_immutable_history_full_checks missing-receipt-contract
        return
    fi

    set +e
    output=$(python .ai/scripts/validate-immutable-history.py verify \
        --repo "$PROJECT_ROOT" \
        --contract "$IMMUTABLE_HISTORY_CONTRACT" \
        --receipt "$IMMUTABLE_HISTORY_RECEIPT" \
        --head HEAD \
        --profile "$PROFILE" \
        --output-format tsv)
    rc=$?
    set -e
    IFS=$'\t' read -r outcome reason source_revision source_tree receipt_commit reusable_ids <<< "$output"

    if [ "$rc" -eq 10 ] && [ "$outcome" = full-required ] && [ -n "$reason" ]; then
        select_immutable_history_full_checks "$reason"
        return
    fi
    if [ "$rc" -ne 0 ] || [ "$outcome" != routine-reusable ] ||
        [ -z "$source_revision" ] || [ -z "$source_tree" ] || [ -z "$receipt_commit" ]; then
        echo "Immutable history receipt verification failed closed: ${output:-no-output}" >&2
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
        IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID["$id"]=true
    done
    for id in workflow-artifacts assessment-artifacts source-ai-context-version; do
        [ -n "${IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID[$id]:-}" ] || {
            echo "Immutable history receipt omitted required reusable check id: $id" >&2
            return 1
        }
        SELECTION_REASON_BY_ID["$id"]="immutable-history-receipt:$source_revision"
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
NOT_APPLICABLE=0
BLOCKED_CHECKS=0
REQUIRED_BLOCKED=0
CHECK_TIMINGS=()
BLOCKED_LIST=()
TOTAL_ELAPSED_START=$SECONDS
LOG_BASE="${AI_CONTEXT_VALIDATION_LOG_DIR:-$PROJECT_ROOT/artifacts/validation}"
INVOCATION_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"
LOG_DIR="$LOG_BASE/$INVOCATION_ID"
mkdir -p "$LOG_DIR"
# Child contract tests must distinguish the aggregate runner's retained
# diagnostics from mutations made by the entrypoint being tested.
export AI_CONTEXT_VALIDATION_RUN_LOG_DIR="$LOG_DIR"
# Child contract tests must distinguish the aggregate runner's retained
# diagnostics from mutations made by the entrypoint being tested.
export AI_CONTEXT_VALIDATION_RUN_LOG_DIR="$LOG_DIR"

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

EVIDENCE_HELPER="$SCRIPT_DIR/validation-evidence.py"
EVIDENCE_PATH="$LOG_DIR/evidence.jsonl"
EVIDENCE_SUMMARY="$LOG_DIR/evidence-summary.json"
EVIDENCE_CACHE="$LOG_BASE/evidence-cache.json"
EVIDENCE_SELECTION="$LOG_DIR/evidence-selection.tsv"
EVIDENCE_EVENTS="$LOG_DIR/evidence-events.tsv"
EVIDENCE_CHANGED_PATHS="$LOG_DIR/changed-paths.txt"
declare -A EVIDENCE_FINGERPRINT_BY_ID=()
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
EVIDENCE_POLICY_FINGERPRINT=$(sha256sum "$REGISTRY_PATH" "$SCRIPT_DIR/check-all.sh" "$EVIDENCE_HELPER" 2>/dev/null | sha256sum 2>/dev/null | awk '{print $1}')
EVIDENCE_POLICY_FINGERPRINT=${EVIDENCE_POLICY_FINGERPRINT:-unavailable}
EVIDENCE_INPUT_FINGERPRINT=
EVIDENCE_CACHE_HIT=false
EVIDENCE_RECEIPT_HIT=false
EVIDENCE_PRIOR_LOG=

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
    local id version prepared record fingerprint cache_hit prior_log
    [ -f "$EVIDENCE_HELPER" ] || {
        echo "Validation evidence helper is missing: $EVIDENCE_HELPER" >&2
        return 1
    }
    : > "$EVIDENCE_SELECTION"
    for id in "${CHECK_IDS[@]}"; do
        version=$(validator_version "$id")
        VALIDATOR_VERSION_BY_ID["$id"]=$version
        if [ -n "${IMMUTABLE_HISTORY_RECEIPT_REUSE_BY_ID[$id]:-}" ]; then
            EVIDENCE_FINGERPRINT_BY_ID["$id"]=$IMMUTABLE_HISTORY_FINGERPRINT
            EVIDENCE_CACHE_HIT_BY_ID["$id"]=false
            EVIDENCE_RECEIPT_HIT_BY_ID["$id"]=true
            EVIDENCE_PRIOR_LOG_BY_ID["$id"]=$IMMUTABLE_HISTORY_RECEIPT
            continue
        fi
        printf '%s\t%s\t%s\t%s\n' \
            "$id" "$version" "${CHECK_INPUT_PATHS[$id]}" "${CHECK_CACHE_POLICY[$id]}" \
            >> "$EVIDENCE_SELECTION"
    done
    prepared=$(python .ai/scripts/validation-evidence.py prepare \
        --repo "$PROJECT_ROOT" \
        --cache "$EVIDENCE_CACHE" \
        --profile "$PROFILE" \
        --environment-class "$EVIDENCE_ENVIRONMENT_CLASS" \
        --selection "$EVIDENCE_SELECTION") || return 1
    while IFS=$'\t' read -r record fingerprint cache_hit prior_log; do
        [ -n "$record" ] || continue
        EVIDENCE_FINGERPRINT_BY_ID["$record"]=$fingerprint
        EVIDENCE_CACHE_HIT_BY_ID["$record"]=$cache_hit
        EVIDENCE_RECEIPT_HIT_BY_ID["$record"]=false
        EVIDENCE_PRIOR_LOG_BY_ID["$record"]=$prior_log
    done <<< "$prepared"
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

record_validation_evidence() {
    local id=$1 outcome=$2 disposition=$3 started_ms=$4 completed_ms=$5 log_path=$6
    local suppressed_bytes=0 version selection_reason
    [ "$VERBOSE" = true ] || suppressed_bytes=-1
    version=${VALIDATOR_VERSION_BY_ID[$id]:-}
    [ -n "$version" ] || return 1
    selection_reason=${SELECTION_REASON_BY_ID[$id]:-selection-reason-unavailable}
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$id" "$version" "$EVIDENCE_INPUT_FINGERPRINT" "$outcome" "$disposition" \
        "$started_ms" "$completed_ms" "$EVIDENCE_CACHE_HIT" "$(basename "$log_path")" "$suppressed_bytes" \
        "$selection_reason" "$CHANGED_PATHS_DIGEST" \
        >> "$EVIDENCE_EVENTS"
}

if ! prepare_all_validation_evidence; then
    echo "Validation evidence preparation failed; no checks were launched." >&2
    exit 2
fi
: > "$EVIDENCE_EVENTS"
printf '%s\n' "${!CHANGED_PATHS[@]}" | LC_ALL=C sort > "$EVIDENCE_CHANGED_PATHS"

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

if ! record_not_selected_evidence; then
    echo "Validation not-selected evidence could not be recorded." >&2
    exit 2
fi

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

wait_for_check_with_timeout() {
    local child_pid=$1 timeout_seconds=$2 started_seconds=$SECONDS
    local child_rc
    while kill -0 "$child_pid" 2>/dev/null; do
        if [ $((SECONDS - started_seconds)) -ge "$timeout_seconds" ]; then
            kill -TERM "$child_pid" 2>/dev/null || true
            sleep 0.1
            kill -KILL "$child_pid" 2>/dev/null || true
            wait "$child_pid" 2>/dev/null || true
            return 124
        fi
        sleep 0.1
    done
    wait "$child_pid"
    child_rc=$?
    return "$child_rc"
}

run_script_with_timeout() {
    local timeout_seconds=$1 log_path=$2
    shift 2
    if command -v timeout >/dev/null 2>&1; then
        timeout --foreground "${timeout_seconds}s" "$@" >"$log_path" 2>&1
        return $?
    fi
    "$@" >"$log_path" 2>&1 &
    wait_for_check_with_timeout "$!" "$timeout_seconds"
}

run_text_command_with_timeout() {
    local timeout_seconds=$1 log_path=$2 command_text=$3
    if command -v timeout >/dev/null 2>&1; then
        export -f python
        timeout --foreground "${timeout_seconds}s" bash -c \
            'cd "$1" && eval "$2"' bash "$PROJECT_ROOT" "$command_text" >"$log_path" 2>&1
        return $?
    fi
    (cd "$PROJECT_ROOT" && eval "$command_text") >"$log_path" 2>&1 &
    wait_for_check_with_timeout "$!" "$timeout_seconds"
}

# Function to run a check script
run_check() {
    local script_name=$1
    local description=$2
    local enforcement=$3
    local is_critical=$4
    local is_quick=$5
    shift 5
    local args=("$@")
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    local started_ms completed_ms duration_ms output rc reason outcome log_path disposition timeout_seconds
    select_check "$description" "$is_critical" "$is_quick" || return 0
    record_selected "$enforcement"
    log_path="$LOG_DIR/$id.log"
    started_ms=$(now_millis)
    timeout_seconds=${CHECK_TIMEOUT[$id]:-}

    if ! prepare_validation_evidence "$id"; then
        printf '%s\n' "validation evidence lookup failed for $id" >"$log_path"
        record_unavailable_or_failed "$enforcement" "validation evidence lookup for $description"
        outcome="failed"
        disposition="executed"
    elif [ "$EVIDENCE_CACHE_HIT" = true ] || [ "$EVIDENCE_RECEIPT_HIT" = true ]; then
        printf 'Reused eligible validation evidence; source=%s; prior_log=%s\n' \
            "$([ "$EVIDENCE_RECEIPT_HIT" = true ] && printf receipt || printf cache)" \
            "$EVIDENCE_PRIOR_LOG" >"$log_path"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        REUSED_CHECKS=$((REUSED_CHECKS + 1))
        outcome="passed"
        disposition="reused"
    elif [ -f "$SCRIPT_DIR/$script_name" ]; then
        if [ -x "$SCRIPT_DIR/$script_name" ]; then
            [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
            EXECUTED_CHECKS=$((EXECUTED_CHECKS + 1))
            set +e
            run_script_with_timeout "$timeout_seconds" "$log_path" "$SCRIPT_DIR/$script_name" "${args[@]}"
            rc=$?
            set -e
            output=$(<"$log_path")
            if [ "$rc" -eq 124 ]; then
                printf 'Validation timed out after %ss.\n' "$timeout_seconds" >>"$log_path"
                record_unavailable_or_failed "$enforcement" "$description timed out after ${timeout_seconds}s"
                outcome="failed"
                disposition="timed-out"
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
        else
            printf '%s\n' "$script_name is not executable" >"$log_path"
            record_unavailable_or_failed "$enforcement" "$script_name is not executable"
            outcome="failed"
            disposition="executed"
        fi
    else
        printf '%s\n' "$script_name not found" >"$log_path"
        record_unavailable_or_failed "$enforcement" "$script_name not found"
        outcome="failed"
        disposition="executed"
    fi
    completed_ms=$(now_millis)
    duration_ms=$((completed_ms - started_ms))
    if ! record_validation_evidence "$id" "$outcome" "$disposition" "$started_ms" "$completed_ms" "$log_path"; then
        printf '%s\n' "validation evidence record failed" >>"$log_path"
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
    local id=${CHECK_ID_BY_DESCRIPTION[$description]:-}
    local started_ms completed_ms duration_ms output rc reason outcome log_path disposition timeout_seconds
    select_check "$description" "$is_critical" "$is_quick" || return 0
    record_selected "$enforcement"
    log_path="$LOG_DIR/$id.log"
    started_ms=$(now_millis)
    timeout_seconds=${CHECK_TIMEOUT[$id]:-}

    if ! prepare_validation_evidence "$id"; then
        printf '%s\n' "validation evidence lookup failed for $id" >"$log_path"
        record_unavailable_or_failed "$enforcement" "validation evidence lookup for $description"
        outcome="failed"
        disposition="executed"
    elif [ "$EVIDENCE_CACHE_HIT" = true ] || [ "$EVIDENCE_RECEIPT_HIT" = true ]; then
        printf 'Reused eligible validation evidence; source=%s; prior_log=%s\n' \
            "$([ "$EVIDENCE_RECEIPT_HIT" = true ] && printf receipt || printf cache)" \
            "$EVIDENCE_PRIOR_LOG" >"$log_path"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        outcome="passed"
        REUSED_CHECKS=$((REUSED_CHECKS + 1))
        disposition="reused"
    else
        [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
        EXECUTED_CHECKS=$((EXECUTED_CHECKS + 1))
        set +e
        run_text_command_with_timeout "$timeout_seconds" "$log_path" "$command_text"
        rc=$?
        set -e
        output=$(<"$log_path")
        if [ "$rc" -eq 124 ]; then
            printf 'Validation timed out after %ss.\n' "$timeout_seconds" >>"$log_path"
            record_unavailable_or_failed "$enforcement" "$description timed out after ${timeout_seconds}s"
            outcome="failed"
            disposition="timed-out"
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
    if ! record_validation_evidence "$id" "$outcome" "$disposition" "$started_ms" "$completed_ms" "$log_path"; then
        printf '%s\n' "validation evidence record failed" >>"$log_path"
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

    select_check "$description" "$is_critical" "$is_quick" || return 0
    echo -e "${YELLOW}⊖${NC} DEFERRED: $description ($reason)"
    DEFERRED_CHECKS=$((DEFERRED_CHECKS + 1))
}

run_spec_compliance_check() {
    local spec_file="${SPEC_FILE:-}"
    local task_name="${TASK_NAME:-}"

    if [ -z "$spec_file" ] && [ -z "$task_name" ]; then
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Spec Implementation Compliance (SPEC_FILE/TASK_NAME not set)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
        return
    fi
    if [ -z "$spec_file" ] || [ -z "$task_name" ]; then
        echo -e "${RED}✗ FAILED${NC}: Spec Implementation Compliance requires both SPEC_FILE and TASK_NAME"
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_SELECTED=$((REQUIRED_SELECTED + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
        return
    fi

    run_check "check-spec-compliance.sh" \
        "Spec Implementation Compliance (.NET)" \
        "required" "false" "true" "$spec_file" "$task_name"
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
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: SDK-Free Framework Contract (source framework test not packaged)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
        return
    fi

    run_command_check "python .ai/scripts/tests/test_sdk_free_framework_contract.py -v" \
        "SDK-Free Framework Contract" \
        "required" "true" "true"
}

run_source_repository_release_checks() {
    if ! check_is_selected "Governance Term Routing And Release Projection Contract" &&
        ! check_is_selected "AI Context Version Governance Fail-Closed Tests" &&
        ! check_is_selected "AI Context Packaging GWT Tests"; then
        return
    fi
    if ! source_release_context_available; then
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Governance Term Routing And Release Projection Contract (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Version Governance Fail-Closed Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Packaging GWT Tests (source package builder not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Release State Fail-Closed Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Release Preparation Fail-Closed Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Release Renderer Fail-Closed Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Behavior Deterministic Evaluation (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Load Measurement Contract (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Repository Configuration Ownership Contract (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Repository Configuration Ownership Fail-Closed Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Skill Transition Compatibility Contract (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Skill Transition Compatibility Fail-Closed Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Effective Rule Packet Resolution and Consumer Parity Tests (source release context not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Effective Rule Action Skill Consumption Contract (source release context not packaged)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 14))
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
        run_command_check "python .ai/scripts/validate-ai-context-versions.py" \
            "AI Context Release And Version Contracts" \
            "required" "true" "true"
    elif [ -f "$PROJECT_ROOT/.dev/ai-context/provenance.yaml" ] || \
         [ -f "$PROJECT_ROOT/.dev/AI-CONTEXT-APPLY-PENDING.yaml" ]; then
        run_command_check "python .ai/scripts/validate-ai-context-target.py" \
            "AI Context Target Apply, Provenance And Customization Contracts" \
            "required" "true" "true"
    else
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Target Provenance And Customization Contracts (target provenance not initialized)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
    fi
}

source_governance_context_available() {
    source_release_context_available &&
        [ -f "$PROJECT_ROOT/.github/workflows/governance.yml" ] &&
        [ -f "$PROJECT_ROOT/.ai/distribution/governance-checks.yaml" ] &&
        [ -f "$PROJECT_ROOT/.ai/scripts/validate-source-governance.py" ]
}

run_source_repository_governance_checks() {
    if ! check_is_selected "Source Governance Manifest Registry"; then
        return
    fi
    if ! source_governance_context_available; then
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Source Governance Manifest Registry (source governance registry not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Repository Identity Drift Fail-Closed Tests (source governance registry not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Governance Pull-Request Workflow Contract (source CI workflow not packaged)"
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: GitHub Workflow Lifecycle Contract (source CI workflows not packaged)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 4))
        return
    fi

    run_command_check "python .ai/scripts/validate-source-governance.py" \
        "Source Governance Manifest Registry" \
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
        echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: AI Context Package Smoke Tests (source package builder not packaged)"
        NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
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
    COMMIT_VALIDATION_COMMAND="python .ai/scripts/validate-git-commits.py --range '$COMMIT_RANGE'"
    if [ -n "${WORKFLOW_ID:-}" ]; then
        COMMIT_VALIDATION_COMMAND="$COMMIT_VALIDATION_COMMAND --workflow-id '$WORKFLOW_ID'"
    fi
    run_command_check "$COMMIT_VALIDATION_COMMAND" \
        "Selected Git Commit Messages" \
        "required" "true" "true"
else
    echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Selected Git Commit Messages (COMMIT_RANGE not set)"
    NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
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

run_command_check "python .ai/scripts/tests/test_validation_evidence.py -v" \
    "Validation Execution Evidence Contract" \
    "required" "true" "true"

if immutable_history_source_context_available; then
    run_command_check "python .ai/scripts/tests/test_immutable_history_validation.py -v" \
        "Immutable History Validation Contract" \
        "required" "true" "true"
elif check_is_selected "Immutable History Validation Contract"; then
    echo -e "${CYAN}ℹ${NC} NOT APPLICABLE: Immutable History Validation Contract (source history not packaged)"
    NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
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
    "required" "true" "true"

run_source_repository_sdk_free_contract

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

if [ "$PROFILE" == "nightly-full" ]; then
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

if ! python .ai/scripts/validation-evidence.py finalize \
    --repo "$PROJECT_ROOT" \
    --cache "$EVIDENCE_CACHE" \
    --evidence "$EVIDENCE_PATH" \
    --events "$EVIDENCE_EVENTS" \
    --invocation-id "$INVOCATION_ID" \
    --profile "$PROFILE" \
    --environment-class "$EVIDENCE_ENVIRONMENT_CLASS"; then
    echo -e "${RED}✗ FAILED${NC}: validation evidence records could not be finalized"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
fi

if ! python .ai/scripts/validation-evidence.py summarize \
    --evidence "$EVIDENCE_PATH" \
    --output "$EVIDENCE_SUMMARY" \
    --invocation-id "$INVOCATION_ID" \
    --profile "$PROFILE"; then
    echo -e "${RED}✗ FAILED${NC}: validation evidence summary could not be written"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
fi

TOTAL_ELAPSED=$((SECONDS - TOTAL_ELAPSED_START))
if ! python .ai/scripts/validation-evidence.py workflow-summary \
    --evidence "$EVIDENCE_PATH" \
    --output "$LOG_DIR/workflow-summary.json" \
    --profile "$PROFILE" \
    --wall-span-ms "$((TOTAL_ELAPSED * 1000))" \
    --workflow-id "${WORKFLOW_ID:-}"; then
    echo -e "${RED}✗ FAILED${NC}: workflow evidence summary could not be written"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
fi
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
echo "summary: profile=$PROFILE selected=$TOTAL_CHECKS executed=$EXECUTED_CHECKS reused=$REUSED_CHECKS failed=$FAILED_CHECKS blocked=$BLOCKED_CHECKS warnings=$WARNINGS deferred=$DEFERRED_CHECKS not-applicable=$NOT_APPLICABLE"
echo "full-log: $LOG_DIR"
echo "evidence: $EVIDENCE_PATH"
echo -e "Required Selected: ${CYAN}$REQUIRED_SELECTED${NC}"
echo -e "Required Executed: ${CYAN}$REQUIRED_RUN${NC}"
echo -e "Required Failed: ${RED}$REQUIRED_FAILED${NC}"
echo -e "Required Blocked: ${YELLOW}$REQUIRED_BLOCKED${NC}"

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
if [ $FAILED_CHECKS -eq 0 ] && [ $BLOCKED_CHECKS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║    ✓ All Checks Passed Successfully!   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    exit 0
elif [ $FAILED_CHECKS -eq 0 ] && [ $BLOCKED_CHECKS -eq 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠ Passed with $WARNINGS Advisory Warning(s) ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    exit 0
elif [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⊘ $BLOCKED_CHECKS check(s) blocked by environment  ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Do NOT modify repository code for these."
    echo "2. Prepare the host prerequisite listed above."
    echo "3. Re-run. Exit code 3 means unverified, never passed."
    exit 3
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
