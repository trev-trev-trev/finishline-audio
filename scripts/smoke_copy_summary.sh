#!/usr/bin/env bash

# Copy smoke test summary to macOS clipboard
# Usage: ./scripts/smoke_copy_summary.sh

REPORT_TXT="data/reports/smoke_latest.txt"
REPORT_JSON="data/reports/smoke_latest.json"

if [ ! -f "$REPORT_JSON" ]; then
    echo "Error: No smoke test report found at $REPORT_JSON"
    echo "Run ./scripts/run_smoke_tests.sh first"
    exit 1
fi

# Extract summary from JSON
PASSED=$(jq -r '.passed' "$REPORT_JSON")
FAILED=$(jq -r '.failed' "$REPORT_JSON")
SKIPPED=$(jq -r '.skipped' "$REPORT_JSON")
TIMESTAMP=$(jq -r '.timestamp' "$REPORT_JSON")

# Find first failure if any
FIRST_FAILURE=""
if [ "$FAILED" -gt 0 ]; then
    FIRST_FAILURE=$(jq -r '.tests[] | select(.status=="FAIL") | .state_id' "$REPORT_JSON" | head -n1)
fi

# Build summary
SUMMARY="FLAAS Smoke Test Summary ($TIMESTAMP)
Passed: $PASSED  Failed: $FAILED  Skipped: $SKIPPED"

if [ -n "$FIRST_FAILURE" ]; then
    SUMMARY="$SUMMARY
First failure: $FIRST_FAILURE"
fi

SUMMARY="$SUMMARY
Report: $REPORT_TXT"

# Copy to clipboard
echo "$SUMMARY" | pbcopy

echo "Copied to clipboard:"
echo "$SUMMARY"
