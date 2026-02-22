#!/usr/bin/env bash
# Test macOS UI automation export (proof-of-concept)
# Requires: Ableton Live running, macOS Accessibility permissions

set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate

OUT="$PWD/output/proof_auto_export.wav"

echo "Testing macOS UI automation export..."
echo "Output: $OUT"
echo ""

# Remove existing file
rm -f "$OUT"

# Run UI export via Python module
python3 - <<'PY'
import sys
from pathlib import Path
from flaas.ui_export_macos import auto_export_wav

out_path = Path("output/proof_auto_export.wav")
print(f"Triggering export to {out_path.name}...")

try:
    auto_export_wav(out_path, timeout_s=180)
    print(f"✓ Export complete, file ready")
except RuntimeError as e:
    print(f"✗ Export failed: {e}")
    sys.exit(1)
PY

# Verify
echo ""
echo "Verifying audio..."
flaas verify-audio "$OUT"
