#!/bin/bash
#
# STAND TALL - FULLY AUTONOMOUS MASTER
# Vocals configured, master chain optimized, all automated
#

set -e

cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

export FLAAS_UI_EXPORT_DEBUG=1

echo "========================================================================"
echo "STAND TALL - FULLY AUTONOMOUS MASTER GENERATION"
echo "========================================================================"
echo ""
echo "✅ Vocals configured autonomously (already done):"
echo "   - Utility PRE: -1 dB"
echo "   - Vocal Rider: ±4 dB range, high sensitivity"  
echo "   - Sibilance: -40 dB threshold, 5 dB range"
echo "   - RVox: 55% compression (4-6 dB GR)"
echo ""
echo "✅ Master chain ready:"
echo "   Utility → EQ → C6 → F6 → SSL → Saturator → L3"
echo ""
echo "🎯 Target: -9.0 LUFS, -1.0 dBTP (loud_preview)"
echo ""
echo "⏱️  Runtime: 30-60 minutes (up to 15 iterations)"
echo ""
echo "Pre-check:"
echo "  [ ] Ableton: Stand Tall open, loop brace set"
echo "  [ ] Master fader: 0.0 dB"
echo "  [ ] All plugin windows: CLOSED"
echo ""
read -p "Press Enter to START... " _

echo ""
echo "🚀 STARTING AUTONOMOUS OPTIMIZATION..."
echo ""

# Run master optimization
flaas master-premium --mode loud_preview

EXIT_CODE=$?

echo ""
echo "========================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ OPTIMIZATION COMPLETE"
else
    echo "⚠️  OPTIMIZATION EXITED WITH CODE: $EXIT_CODE"
fi
echo "========================================================================"
echo ""

# Show final master
FINAL=$(ls -t output/stand_tall_premium_loud_preview_iter*.wav 2>/dev/null | head -n 1)

if [ -n "$FINAL" ]; then
    echo "📊 FINAL MASTER:"
    echo ""
    ls -lh "$FINAL"
    echo ""
    
    echo "📈 METRICS:"
    echo ""
    flaas verify-audio "$FINAL"
    echo ""
    
    echo "📋 LOG:"
    echo ""
    tail -n 5 output/stand_tall_premium_loud_preview.jsonl
    echo ""
    
    echo "🎵 COMPARE TO LIFE YOU CHOSE:"
    echo ""
    echo "Stand Tall: $FINAL"
    echo "Life You Chose: output/life_you_chose/master_loud_preview_iter1.wav"
    echo ""
else
    echo "⚠️  No output files found"
    echo ""
    echo "Check:"
    echo "  - output/ directory"
    echo "  - Export errors in log above"
fi

echo "========================================================================"
