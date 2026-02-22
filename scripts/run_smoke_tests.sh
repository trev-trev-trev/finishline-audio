#!/usr/bin/env bash
set -e

# FLAAS Device Control Smoke Tests
# Usage: ./scripts/run_smoke_tests.sh [--write]

WRITE_MODE=false
if [[ "${1:-}" == "--write" ]]; then
    WRITE_MODE=true
fi

REPORT="data/reports/smoke_latest.txt"
mkdir -p "$(dirname "$REPORT")"
echo "FLAAS Smoke Tests - $(date -u +"%Y-%m-%d %H:%M:%S UTC")" > "$REPORT"
echo "Mode: $([ "$WRITE_MODE" = true ] && echo "READ+WRITE" || echo "READ-ONLY")" >> "$REPORT"
echo "" >> "$REPORT"

echo "========================================="
echo "FLAAS Smoke Tests"
echo "Mode: $([ "$WRITE_MODE" = true ] && echo "READ+WRITE (reverts changes)" || echo "READ-ONLY (safe)")"
echo "Report: $REPORT"
echo "========================================="
echo ""

source .venv/bin/activate

PASSED=0
FAILED=0

echo "=== READ-ONLY TESTS ==="
echo ""

# Test 1: OSC ping
echo "→ OSC ping"
echo "TEST: OSC ping" >> "$REPORT"
if flaas ping --wait > /tmp/smoke_out.txt 2>&1 && grep -q "ok:" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    echo "" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    echo "" >> "$REPORT"
    FAILED=$((FAILED + 1))
    exit 1
fi
sleep 1

# Test 2: Scan
echo "→ Scan Live set"
echo "TEST: Scan" >> "$REPORT"
if flaas scan > /tmp/smoke_out.txt 2>&1 && grep -q "model_cache.json" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    echo "" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# Test 3: Inspect track
echo "→ Inspect selected track"
echo "TEST: Inspect selected track" >> "$REPORT"
if flaas inspect-selected-track > /tmp/smoke_out.txt 2>&1 && grep -q "track_id=" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    echo "" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# Test 4: Inspect device
echo "→ Inspect selected device"
echo "TEST: Inspect selected device" >> "$REPORT"
if flaas inspect-selected-device > /tmp/smoke_out.txt 2>&1 && grep -q "track_id=" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    echo "" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# Test 5: Device param info
echo "→ Device param info (Utility Gain)"
echo "TEST: Device param info" >> "$REPORT"
if flaas device-param-info 0 0 --param-id 9 > /tmp/smoke_out.txt 2>&1 && grep -q 'name="Gain"' /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    echo "" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# Test 6: Device map
echo "→ Generate device map (Limiter)"
echo "TEST: Device map" >> "$REPORT"
if flaas device-map 0 2 > /tmp/smoke_out.txt 2>&1 && grep -q "WROTE" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    echo "" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi

if [ "$WRITE_MODE" = false ]; then
    echo ""
    echo "========================================="
    echo "READ-ONLY TESTS COMPLETE"
    echo "Passed: $PASSED"
    echo "Failed: $FAILED"
    echo "========================================="
    echo ""
    echo "Run with --write flag to include write tests (with auto-revert)"
    echo "SUMMARY: $PASSED passed, $FAILED failed" >> "$REPORT"
    exit 0
fi

echo ""
echo "=== WRITE TESTS (with revert) ==="
echo ""

# EQ Eight band 1 A gain test
echo "→ EQ Eight: Read band 1 A gain original"
ORIGINAL_GAIN=$(flaas device-param-info 0 1 --param-id 7 | grep -oE 'val=[^ ]+' | cut -d= -f2)
echo "  Original: $ORIGINAL_GAIN dB"
echo "EQ8 Band 1 A Gain original: $ORIGINAL_GAIN" >> "$REPORT"
sleep 1

echo "→ EQ Eight: Set band 1 A gain to -3.0 dB"
echo "TEST: EQ8 set gain -3.0" >> "$REPORT"
if flaas eq8-set 0 1 --band 1 --side A --param gain --value -3.0 > /tmp/smoke_out.txt 2>&1 && grep -q "after=-3.000000" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

echo "→ EQ Eight: Reset band 1 A gain to $ORIGINAL_GAIN dB"
echo "TEST: EQ8 reset gain" >> "$REPORT"
if flaas eq8-set 0 1 --band 1 --side A --param gain --value "$ORIGINAL_GAIN" > /tmp/smoke_out.txt 2>&1; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# EQ Eight band 1 A freq test
echo "→ EQ Eight: Read band 1 A freq original"
ORIGINAL_FREQ=$(flaas device-param-info 0 1 --param-id 6 | grep -oE 'val=[^ ]+' | cut -d= -f2)
echo "  Original: $ORIGINAL_FREQ"
echo "EQ8 Band 1 A Freq original: $ORIGINAL_FREQ" >> "$REPORT"
sleep 1

echo "→ EQ Eight: Set band 1 A freq to 0.20"
echo "TEST: EQ8 set freq 0.20" >> "$REPORT"
if flaas eq8-set 0 1 --band 1 --side A --param freq --value 0.20 > /tmp/smoke_out.txt 2>&1 && grep -q "after=0.2" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

echo "→ EQ Eight: Reset band 1 A freq to $ORIGINAL_FREQ"
echo "TEST: EQ8 reset freq" >> "$REPORT"
if flaas eq8-set 0 1 --band 1 --side A --param freq --value "$ORIGINAL_FREQ" > /tmp/smoke_out.txt 2>&1; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# Limiter ceiling test
echo "→ Limiter: Read ceiling original"
ORIGINAL_CEILING=$(flaas device-param-info 0 2 --param-id 2 | grep -oE 'val=[^ ]+' | cut -d= -f2)
echo "  Original: $ORIGINAL_CEILING dB"
echo "Limiter Ceiling original: $ORIGINAL_CEILING" >> "$REPORT"
sleep 1

echo "→ Limiter: Set ceiling to -1.0 dB"
echo "TEST: Limiter set ceiling -1.0" >> "$REPORT"
if flaas limiter-set 0 2 --param ceiling --value -1.0 > /tmp/smoke_out.txt 2>&1 && grep -q "after=-1.000000" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

echo "→ Limiter: Reset ceiling to $ORIGINAL_CEILING dB"
echo "TEST: Limiter reset ceiling" >> "$REPORT"
if flaas limiter-set 0 2 --param ceiling --value "$ORIGINAL_CEILING" > /tmp/smoke_out.txt 2>&1; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

# Limiter lookahead test
echo "→ Limiter: Read lookahead original"
ORIGINAL_LOOKAHEAD=$(flaas device-param-info 0 2 --param-id 6 | grep -oE 'val=[^ ]+' | cut -d= -f2)
echo "  Original: $ORIGINAL_LOOKAHEAD"
echo "Limiter Lookahead original: $ORIGINAL_LOOKAHEAD" >> "$REPORT"
sleep 1

echo "→ Limiter: Set lookahead to 0"
echo "TEST: Limiter set lookahead 0" >> "$REPORT"
if flaas limiter-set 0 2 --param lookahead --value 0 > /tmp/smoke_out.txt 2>&1 && grep -q "after=0.000000" /tmp/smoke_out.txt; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi
sleep 1

echo "→ Limiter: Reset lookahead to $ORIGINAL_LOOKAHEAD"
echo "TEST: Limiter reset lookahead" >> "$REPORT"
if flaas limiter-set 0 2 --param lookahead --value "$ORIGINAL_LOOKAHEAD" > /tmp/smoke_out.txt 2>&1; then
    echo "  ✅ PASS"
    echo "✅ PASS" >> "$REPORT"
    PASSED=$((PASSED + 1))
else
    echo "  ❌ FAIL"
    cat /tmp/smoke_out.txt >> "$REPORT"
    echo "❌ FAIL" >> "$REPORT"
    exit 1
fi

echo ""
echo "========================================="
echo "ALL TESTS COMPLETE"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "========================================="
echo ""
echo "SUMMARY: $PASSED passed, $FAILED failed" >> "$REPORT"
echo "Report saved: $REPORT"

exit 0
