#!/bin/bash
# Test macOS auto-export probe
# Acceptance: File appears at output/_probe.wav and is measurable

set -e

cd "$(dirname "$0")/.."
source .venv/bin/activate

echo "========================================"
echo "EXPORT PROBE TEST"
echo "========================================"
echo ""
echo "Target: output/_probe.wav"
echo "Timeout: 180s"
echo ""
echo "Pre-requisites:"
echo "  [ ] Ableton Live running with project open"
echo "  [ ] Loop/selection set (any duration)"
echo "  [ ] Master fader = 0.0 dB"
echo ""
read -p "Press Enter to start export probe..."
echo ""

# Enable debug mode
export FLAAS_UI_EXPORT_DEBUG=1

# Run probe
python -c "
from pathlib import Path
from flaas.ui_export_macos import auto_export_wav

probe_path = Path('output/_probe.wav').resolve()
print(f'Probe path: {probe_path}')
print('')

try:
    auto_export_wav(probe_path, timeout_s=180)
    print('')
    print('✅ Export probe SUCCESS')
except Exception as e:
    print('')
    print(f'❌ Export probe FAILED: {e}')
    exit(1)
"

echo ""
echo "========================================"
echo "Verifying exported file..."
echo "========================================"
echo ""

if [ -f "output/_probe.wav" ]; then
    ls -lh output/_probe.wav
    echo ""
    flaas verify-audio output/_probe.wav
    echo ""
    echo "✅ PROBE TEST PASSED"
    echo ""
    echo "Cleanup:"
    rm -f output/_probe.wav
    echo "  Deleted output/_probe.wav"
else
    echo "❌ PROBE TEST FAILED: File not found at output/_probe.wav"
    exit 1
fi
