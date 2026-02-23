#!/bin/bash
#
# STAND TALL - FULL AUTONOMOUS MASTER GENERATION
# Everything configured autonomously, just run this
#

set -e

cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

export FLAAS_UI_EXPORT_DEBUG=1

echo "========================================================================"
echo "STAND TALL - FULL AUTONOMOUS MASTER"
echo "========================================================================"
echo ""
echo "Vocals configured autonomously:"
echo "  ✓ Utility PRE: -1 dB (clipping protection)"
echo "  ✓ Vocal Rider: ±4 dB range, high sensitivity"
echo "  ✓ Sibilance: -40 dB threshold, 5 dB range"
echo "  ✓ RVox: 55% compression (4-6 dB GR)"
echo ""
echo "Master chain:"
echo "  Utility → EQ → C6 → F6 → SSL → Saturator → L3"
echo ""
echo "Target:"
echo "  -9.0 LUFS, -1.0 dBTP (loud_preview mode)"
echo ""
echo "Runtime: 30-60 minutes (up to 15 iterations)"
echo ""
echo "Pre-requisites:"
echo "  [ ] Ableton: Stand Tall project open"
echo "  [ ] VOCALS track: All processing ON"
echo "  [ ] Loop brace: Set over representative section (verse + chorus)"
echo "  [ ] Master fader: 0.0 dB"
echo "  [ ] All plugin windows closed"
echo ""
read -p "Press Enter to start autonomous optimization... " _

# Run optimization
flaas master-premium --mode loud_preview

# Show results
echo ""
echo "========================================================================"
echo "OPTIMIZATION COMPLETE"
echo "========================================================================" 
echo ""
echo "Final master:"
FINAL_ITER=$(ls -t output/stand_tall_premium_loud_preview_iter*.wav 2>/dev/null | head -n 1)
if [ -n "$FINAL_ITER" ]; then
    echo "  $FINAL_ITER"
    echo ""
    flaas verify-audio "$FINAL_ITER"
    echo ""
    echo "Compare to Life You Chose:"
    echo "  output/life_you_chose/master_loud_preview_iter1.wav"
else
    echo "  (no final master found)"
fi

echo ""
echo "========================================================================"
