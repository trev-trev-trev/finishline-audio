#!/bin/bash
# Background test runner - logs to timestamped file

set -euo pipefail

REPO_DIR="/Users/trev/Repos/finishline_audio_repo"
LOG_DIR="$REPO_DIR/logs/tests"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/test_run_$TIMESTAMP.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Run tests and capture output
cd "$REPO_DIR"
source .venv/bin/activate

echo "========================================" > "$LOG_FILE"
echo "FLAAS Automated Test Run" >> "$LOG_FILE"
echo "Started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run pytest with coverage
python -m pytest tests/ -v --cov=src/flaas --cov-report=term >> "$LOG_FILE" 2>&1
TEST_EXIT_CODE=$?

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "Test Exit Code: $TEST_EXIT_CODE" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Keep only last 100 logs (cleanup old ones)
cd "$LOG_DIR"
ls -t test_run_*.log | tail -n +101 | xargs rm -f 2>/dev/null || true

# Create "latest" symlink
rm -f "$LOG_DIR/latest.log"
ln -s "$LOG_FILE" "$LOG_DIR/latest.log"

# Exit with test result
exit $TEST_EXIT_CODE
