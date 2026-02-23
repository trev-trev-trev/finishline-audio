#!/bin/bash
#
# Export VOCALS group for analysis
# Run this in YOUR terminal (not Cursor's background shell)
#

set -e

cd /Users/trev/Repos/finishline_audio_repo
source .venv/bin/activate

export FLAAS_UI_EXPORT_DEBUG=1

echo "========================================================================"
echo "STAND TALL - VOCAL EXPORT FOR ANALYSIS"
echo "========================================================================"
echo ""
echo "PRE-REQUISITES (DO THESE NOW):"
echo "  [ ] Ableton: Stand Tall project open"
echo "  [ ] Solo VOCALS group (click 'S' button on VOCALS track/group)"
echo "  [ ] Bypass all processing on VOCALS (we want raw vocal)"
echo "  [ ] Loop brace set over representative section (verse + chorus, 30-60 sec)"
echo ""
read -p "Press Enter after VOCALS is soloed and processing bypassed... " _

# Run export
python scripts/export_vocals_analysis.py

echo ""
echo "========================================================================"
echo "EXPORT COMPLETE"
echo "========================================================================"
echo ""
echo "File exported: output/stand_tall_vocal_raw.wav"
echo ""
echo "Paste this in Cursor chat:"
echo "  Analyze: output/stand_tall_vocal_raw.wav"
echo ""
echo "========================================================================"
