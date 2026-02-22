#!/bin/bash
# FINAL MASTER GENERATION
# Run this in YOUR terminal (not Cursor) so you can respond to prompts

set -e

cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

echo "========================================"
echo "FINAL MASTER: Maximum Loudness (-9 LUFS)"
echo "========================================"
echo ""
echo "This will:"
echo "  - Run pre-flight checks (you'll confirm master fader = 0.0 dB)"
echo "  - Run up to 15 iterations (set params → export → verify → adjust)"
echo "  - Target: -9 LUFS, -2 dBTP (commercial competitive loudness)"
echo "  - Output: output/master_loud_preview.wav"
echo ""
echo "PRE-REQUISITES:"
echo "  [ ] Ableton Live running with project open"
echo "  [ ] Master fader = 0.0 dB (you'll confirm this in pre-flight)"
echo "  [ ] Master chain: Utility → EQ → Glue → Saturator → Limiter"
echo "  [ ] Loop/selection = 8 bars"
echo "  [ ] Export defaults: Rendered Track=Master, Normalize=OFF, File Type=WAV"
echo ""
read -p "Press Enter to start..."
echo ""

# Run with debug mode (shows export progress)
export FLAAS_UI_EXPORT_DEBUG=1

flaas master-consensus --mode loud_preview

echo ""
echo "========================================"
echo "RESULTS:"
echo "========================================"
echo ""

if [ -f "output/master_loud_preview.wav" ]; then
    ls -lh output/master_loud_preview.wav
    echo ""
    echo "JSONL (last 20 lines):"
    tail -n 20 output/master_loud_preview.jsonl | jq -r '.'
    echo ""
    echo "✅ MASTER GENERATION COMPLETE"
    echo ""
    echo "Next: Listen to output/master_loud_preview.wav"
    echo "If LOUD + sounds good → ship it to Spotify"
else
    echo "❌ MASTER FILE NOT FOUND"
    echo ""
    echo "Check for files with wrong extensions:"
    ls -lh output/master_loud_preview* 2>/dev/null || echo "  None found"
fi
