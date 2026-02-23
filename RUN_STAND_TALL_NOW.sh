#!/bin/bash
#
# Stand Tall Premium Master Generation
# Run this in YOUR terminal (not Cursor's background shell)
#

set -e

cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

# Enable debug output for auto-export
export FLAAS_UI_EXPORT_DEBUG=1

echo "========================================================================"
echo "STAND TALL - PREMIUM MASTER GENERATION"
echo "========================================================================"
echo ""
echo "This will:"
echo "  - Optimize Waves C6/SSL/L3 + Saturator chain"
echo "  - Target: -9.0 LUFS, -1.0 dBTP (loud_preview mode)"
echo "  - Up to 15 iterations (adaptive convergence)"
echo "  - Auto-export each iteration via macOS UI automation"
echo ""
echo "Expected runtime: 30-60 minutes"
echo ""
echo "Pre-requisites (CONFIRM NOW):"
echo "  [ ] Ableton Live running with Stand Tall project open"
echo "  [ ] Loop brace set over section to master (8-16 bars)"
echo "  [ ] Master chain: Utility → EQ → C6 → F6 → SSL → Saturator → L3"
echo "  [ ] Master fader = 0.0 dB"
echo "  [ ] All plugin windows closed"
echo "  [ ] F6 preset set (gentle 2-5 kHz cut, or flat)"
echo ""
read -p "Press Enter to start optimization... " _

# Run optimization
flaas master-premium --mode loud_preview

# Show results
echo ""
echo "========================================================================"
echo "OPTIMIZATION COMPLETE"
echo "========================================================================"
echo ""
echo "Results:"
ls -lh output/stand_tall_premium_loud_preview_iter*.wav 2>/dev/null || echo "  (no exports found)"
echo ""
echo "Final master:"
FINAL_ITER=$(ls -t output/stand_tall_premium_loud_preview_iter*.wav 2>/dev/null | head -n 1)
if [ -n "$FINAL_ITER" ]; then
    echo "  $FINAL_ITER"
    echo ""
    flaas verify-audio "$FINAL_ITER"
else
    echo "  (no final master found)"
fi

echo ""
echo "========================================================================"
