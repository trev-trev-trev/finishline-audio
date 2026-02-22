#!/usr/bin/env bash
set -e

# FLAAS Device Control Smoke Tests (3 Lanes)
# Usage: 
#   ./scripts/run_smoke_tests.sh             # Lane 1: READ-ONLY (fast)
#   ./scripts/run_smoke_tests.sh --write-fast # Lane 2: WRITE-FAST (dev loop gate)
#   ./scripts/run_smoke_tests.sh --write      # Lane 3: WRITE (pre-commit gate)
#
# Exit codes:
#   0  = pass
#   10 = soft-skip only
#   20 = read failure
#   30 = write failure

WRITE_MODE=false
FAST_MODE=false

if [[ "${1:-}" == "--write" ]]; then
    WRITE_MODE=true
elif [[ "${1:-}" == "--write-fast" ]]; then
    WRITE_MODE=true
    FAST_MODE=true
fi

REPORT_TXT="data/reports/smoke_latest.txt"
REPORT_JSON="data/reports/smoke_latest.json"
TARGET_CONFIG="data/targets/default.json"
CACHE_FILE="data/caches/model_cache.json"
CACHE_MAX_AGE_SEC=30

# Timeout settings (faster for iteration)
TIMEOUT_READ=1.5
TIMEOUT_WRITE=3.0
MAX_RETRIES=1

mkdir -p "$(dirname "$REPORT_TXT")" data/targets data/registry

MODE_STR="READ-ONLY"
if [ "$FAST_MODE" = true ]; then
    MODE_STR="WRITE-FAST"
elif [ "$WRITE_MODE" = true ]; then
    MODE_STR="READ+WRITE"
fi

echo "FLAAS Smoke Tests - $(date -u +"%Y-%m-%d %H:%M:%S UTC")" > "$REPORT_TXT"
echo "Mode: $MODE_STR" >> "$REPORT_TXT"
echo "" >> "$REPORT_TXT"

source .venv/bin/activate

# Load target configuration
if [ ! -f "$TARGET_CONFIG" ]; then
    echo "{\"track_id\":41,\"eq8_device_id\":0,\"other_device_ids\":[1,2]}" > "$TARGET_CONFIG"
fi

TRACK_ID=$(jq -r '.track_id' "$TARGET_CONFIG")
EQ8_DEV=$(jq -r '.eq8_device_id' "$TARGET_CONFIG")
OTHER_DEVS=($(jq -r '.other_device_ids[]' "$TARGET_CONFIG"))

PASSED=0
FAILED=0
SKIPPED=0
FIRST_FAILURE=""
declare -a TEST_RESULTS=()

# Helper function to log test results
log_test() {
    local state_id="$1"
    local status="$2"  # PASS, FAIL, SKIP
    local description="$3"
    local output="${4:-}"
    
    echo "TEST: $state_id" >> "$REPORT_TXT"
    echo "$description" >> "$REPORT_TXT"
    
    if [ "$status" = "PASS" ]; then
        echo "✅ PASS" >> "$REPORT_TXT"
        PASSED=$((PASSED + 1))
    elif [ "$status" = "FAIL" ]; then
        echo "❌ FAIL" >> "$REPORT_TXT"
        if [ -n "$output" ]; then
            echo "$output" >> "$REPORT_TXT"
        fi
        FAILED=$((FAILED + 1))
        if [ -z "$FIRST_FAILURE" ]; then
            FIRST_FAILURE="$state_id"
        fi
    elif [ "$status" = "SKIP" ]; then
        echo "⏭️  SKIP: $description" >> "$REPORT_TXT"
        SKIPPED=$((SKIPPED + 1))
    fi
    echo "" >> "$REPORT_TXT"
    
    # Store for JSON (escape quotes in description)
    DESC_ESCAPED=$(echo "$description" | sed 's/"/\\"/g')
    TEST_RESULTS+=("{\"state_id\":\"$state_id\",\"status\":\"$status\",\"description\":\"$DESC_ESCAPED\"}")
}

# Helper function for retrying RPC calls
retry_cmd() {
    local retries="$1"
    shift
    local attempt=0
    while [ $attempt -le $retries ]; do
        if "$@" > /tmp/smoke_out.txt 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        [ $attempt -le $retries ] && sleep 0.5
    done
    return 1
}

# FAST READ-ONLY TESTS (sequential, reduced timeout, retry)
if retry_cmd $MAX_RETRIES flaas remote-version --timeout $TIMEOUT_READ && grep -q "remote_version=" /tmp/smoke_out.txt; then
    VERSION=$(cat /tmp/smoke_out.txt | head -1)
    # Check for version mismatch warning
    if grep -q "WARNING: Version mismatch" /tmp/smoke_out.txt; then
        log_test "remote-version" "FAIL" "Version mismatch" "$(cat /tmp/smoke_out.txt 2>&1)"
        exit 20  # Read failure
    fi
    log_test "remote-version" "PASS" "$VERSION"
else
    log_test "remote-version" "FAIL" "Check AbletonOSC version" "$(cat /tmp/smoke_out.txt 2>&1)"
    exit 20  # Read failure
fi

if retry_cmd $MAX_RETRIES flaas ping --wait --timeout $TIMEOUT_READ && grep -q "ok:" /tmp/smoke_out.txt; then
    log_test "ping" "PASS" "OSC ping"
else
    log_test "ping" "FAIL" "OSC ping" "$(cat /tmp/smoke_out.txt 2>&1)"
    exit 20  # Read failure
fi

# Skip inspect in fast mode
if [ "$FAST_MODE" = false ]; then
    if retry_cmd $MAX_RETRIES flaas device-param-info $TRACK_ID $EQ8_DEV --param-id 0 --timeout $TIMEOUT_READ && grep -q "track_id=$TRACK_ID" /tmp/smoke_out.txt; then
        log_test "inspect-track-$TRACK_ID" "PASS" "Inspect track $TRACK_ID"
    else
        log_test "inspect-track-$TRACK_ID" "FAIL" "Inspect track $TRACK_ID" "$(cat /tmp/smoke_out.txt 2>&1)"
        exit 20  # Read failure
    fi
fi

# Skip full inspection suite in fast mode
if [ "$FAST_MODE" = false ]; then
    # SCAN (with cache reuse and targeted scan)
    SKIP_SCAN=false
    if [ -f "$CACHE_FILE" ]; then
        CACHE_AGE=$(($(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)))
        if [ "$CACHE_AGE" -lt "$CACHE_MAX_AGE_SEC" ]; then
            log_test "scan" "PASS" "Scan Live set (cached, ${CACHE_AGE}s old)"
            SKIP_SCAN=true
        fi
    fi

    if [ "$SKIP_SCAN" = false ]; then
        # Use targeted scan when config exists, full scan otherwise
        if [ -f "$TARGET_CONFIG" ]; then
            if retry_cmd $MAX_RETRIES flaas scan --tracks $TRACK_ID && grep -q "model_cache.json" /tmp/smoke_out.txt; then
                log_test "scan" "PASS" "Scan track $TRACK_ID"
            else
                log_test "scan" "FAIL" "Scan track $TRACK_ID" "$(cat /tmp/smoke_out.txt 2>&1)"
                exit 20  # Read failure
            fi
        else
            if retry_cmd $MAX_RETRIES flaas scan && grep -q "model_cache.json" /tmp/smoke_out.txt; then
                log_test "scan" "PASS" "Scan Live set (full)"
            else
                log_test "scan" "FAIL" "Scan Live set" "$(cat /tmp/smoke_out.txt 2>&1)"
                exit 20  # Read failure
            fi
        fi
    fi

    # Test EQ8 device
    if retry_cmd $MAX_RETRIES flaas device-param-info $TRACK_ID $EQ8_DEV --param-id 7 --timeout $TIMEOUT_READ && grep -q "track_id=$TRACK_ID" /tmp/smoke_out.txt; then
        log_test "inspect-device-$TRACK_ID-$EQ8_DEV" "PASS" "Inspect device $TRACK_ID/$EQ8_DEV (EQ Eight)"
    else
        log_test "inspect-device-$TRACK_ID-$EQ8_DEV" "FAIL" "Inspect device $TRACK_ID/$EQ8_DEV" "$(cat /tmp/smoke_out.txt 2>&1)"
        exit 20  # Read failure
    fi

    # Test other devices
    for DEV in "${OTHER_DEVS[@]}"; do
        if retry_cmd $MAX_RETRIES flaas device-param-info $TRACK_ID $DEV --param-id 0 --timeout $TIMEOUT_READ && grep -q "track_id=$TRACK_ID" /tmp/smoke_out.txt; then
            log_test "inspect-device-$TRACK_ID-$DEV" "PASS" "Inspect device $TRACK_ID/$DEV"
        else
            log_test "inspect-device-$TRACK_ID-$DEV" "FAIL" "Inspect device $TRACK_ID/$DEV" "$(cat /tmp/smoke_out.txt 2>&1)"
            exit 20  # Read failure
        fi
    done

    # Device map test
    if retry_cmd $MAX_RETRIES flaas device-map $TRACK_ID $EQ8_DEV && grep -q "WROTE" /tmp/smoke_out.txt; then
        log_test "device-map-$TRACK_ID-$EQ8_DEV" "PASS" "Generate device map (EQ Eight)"
    else
        log_test "device-map-$TRACK_ID-$EQ8_DEV" "FAIL" "Generate device map" "$(cat /tmp/smoke_out.txt 2>&1)"
        exit 20  # Read failure
    fi

    # SKIPPED: Selection-based tests (non-deterministic)
    log_test "inspect-selected-track" "SKIP" "requires UI selection"
    log_test "inspect-selected-device" "SKIP" "requires UI selection"
fi

if [ "$WRITE_MODE" = false ]; then
    # Write JSON report
    echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"mode\":\"$MODE_STR\",\"passed\":$PASSED,\"failed\":$FAILED,\"skipped\":$SKIPPED,\"tests\":[$(IFS=,; echo "${TEST_RESULTS[*]}")]}" > "$REPORT_JSON"
    
    # 5-line summary
    echo "Passed: $PASSED  Failed: $FAILED  Skipped: $SKIPPED"
    if [ -n "$FIRST_FAILURE" ]; then
        echo "First failure: $FIRST_FAILURE"
    fi
    echo "Report: $REPORT_TXT"
    echo ""
    echo "Run with --write or --write-fast flag to include write tests"
    
    # Exit code: 0 = pass, 10 = soft-skip only
    [ "$SKIPPED" -gt 0 ] && [ "$PASSED" -gt 0 ] && exit 0
    [ "$SKIPPED" -gt 0 ] && [ "$PASSED" -eq 0 ] && exit 10
    exit 0
fi

# === WRITE TESTS (with auto-map generation via direct RPC) ===
echo "" >> "$REPORT_TXT"
echo "=== WRITE TESTS (with revert) ===" >> "$REPORT_TXT"
echo "" >> "$REPORT_TXT"

# Auto-generate EQ8 map if missing (using direct RPC, no scan needed)
EQ8_MAP_FILE="data/registry/eq8_map_t${TRACK_ID}_d${EQ8_DEV}.json"
if [ ! -f "$EQ8_MAP_FILE" ]; then
    flaas eq8-map $TRACK_ID $EQ8_DEV > /dev/null 2>&1 || true
fi

# EQ Eight band 1 A gain test
ORIGINAL_GAIN=$(flaas device-param-info $TRACK_ID $EQ8_DEV --param-id 7 | grep -oE 'val=[^ ]+' | cut -d= -f2)

if flaas eq8-set $TRACK_ID $EQ8_DEV --band 1 --side A --param gain --value -3.0 > /tmp/smoke_out.txt 2>&1 && grep -q "after=-3.000000" /tmp/smoke_out.txt; then
    log_test "eq8-set-gain" "PASS" "EQ8 set gain -3.0"
else
    log_test "eq8-set-gain" "FAIL" "EQ8 set gain" "$(cat /tmp/smoke_out.txt 2>&1)"
    exit 1
fi

if flaas eq8-set $TRACK_ID $EQ8_DEV --band 1 --side A --param gain --value "$ORIGINAL_GAIN" > /tmp/smoke_out.txt 2>&1; then
    log_test "eq8-reset-gain" "PASS" "EQ8 reset gain to $ORIGINAL_GAIN"
else
    log_test "eq8-reset-gain" "FAIL" "EQ8 reset gain" "$(cat /tmp/smoke_out.txt 2>&1)"
    exit 1
fi

# Additional tests only in full write mode
if [ "$FAST_MODE" = false ]; then
    # EQ Eight band 1 A freq test
    ORIGINAL_FREQ=$(flaas device-param-info $TRACK_ID $EQ8_DEV --param-id 6 | grep -oE 'val=[^ ]+' | cut -d= -f2)

    if flaas eq8-set $TRACK_ID $EQ8_DEV --band 1 --side A --param freq --value 0.20 > /tmp/smoke_out.txt 2>&1 && grep -q "after=0.2" /tmp/smoke_out.txt; then
        log_test "eq8-set-freq" "PASS" "EQ8 set freq 0.20"
    else
        log_test "eq8-set-freq" "FAIL" "EQ8 set freq" "$(cat /tmp/smoke_out.txt 2>&1)"
        exit 1
    fi

    if flaas eq8-set $TRACK_ID $EQ8_DEV --band 1 --side A --param freq --value "$ORIGINAL_FREQ" > /tmp/smoke_out.txt 2>&1; then
        log_test "eq8-reset-freq" "PASS" "EQ8 reset freq to $ORIGINAL_FREQ"
    else
        log_test "eq8-reset-freq" "FAIL" "EQ8 reset freq" "$(cat /tmp/smoke_out.txt 2>&1)"
        exit 1
    fi
    
    # Plugin device safe param test
    # Get plugin device ID from config (default to device 1 if other_device_ids exists)
    if [ -f "$TARGET_CONFIG" ]; then
        PLUGIN_DEV=$(jq -r '.other_device_ids[0] // 1' "$TARGET_CONFIG")
    else
        PLUGIN_DEV=1
    fi
    
    if retry_cmd $MAX_RETRIES flaas device-set-safe-param $TRACK_ID $PLUGIN_DEV --timeout $TIMEOUT_WRITE && grep -q "reverted_to=" /tmp/smoke_out.txt; then
        log_test "plugin-set-safe-param" "PASS" "Plugin device safe param (track $TRACK_ID, device $PLUGIN_DEV)"
    else
        # Capture exit code from retry_cmd
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 20 ]; then
            log_test "plugin-set-safe-param" "FAIL" "Plugin device safe param (read)" "$(cat /tmp/smoke_out.txt 2>&1)"
            exit 20
        else
            log_test "plugin-set-safe-param" "FAIL" "Plugin device safe param (write)" "$(cat /tmp/smoke_out.txt 2>&1)"
            exit 30
        fi
    fi
else
    log_test "eq8-set-freq" "SKIP" "skipped in fast mode"
    log_test "eq8-reset-freq" "SKIP" "skipped in fast mode"
    log_test "plugin-set-safe-param" "SKIP" "skipped in fast mode"
fi

# Write JSON report
echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"mode\":\"$MODE_STR\",\"passed\":$PASSED,\"failed\":$FAILED,\"skipped\":$SKIPPED,\"tests\":[$(IFS=,; echo "${TEST_RESULTS[*]}")]}" > "$REPORT_JSON"

# 5-line summary
echo ""
echo "Passed: $PASSED  Failed: $FAILED  Skipped: $SKIPPED"
if [ -n "$FIRST_FAILURE" ]; then
    echo "First failure: $FIRST_FAILURE"
fi
echo "Report: $REPORT_TXT"
echo "JSON: $REPORT_JSON"

exit 0
