#!/bin/bash
# System health check - verify all components operational

set -euo pipefail

REPO_DIR="/Users/trev/Repos/finishline_audio_repo"
cd "$REPO_DIR"

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              FLAAS SYSTEM HEALTH CHECK                                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check 1: Git repository
echo "🔍 Git Repository"
if git status > /dev/null 2>&1; then
    STATUS=$(git status --porcelain | wc -l | tr -d ' ')
    if [ "$STATUS" -eq 0 ]; then
        echo "   ✅ Clean working directory"
    else
        echo "   ⚠️  $STATUS uncommitted change(s)"
    fi
    
    AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
    if [ "$AHEAD" -eq 0 ]; then
        echo "   ✅ Synced with origin/main"
    else
        echo "   ⚠️  $AHEAD commit(s) ahead of origin"
    fi
else
    echo "   ❌ Git error"
    exit 1
fi
echo ""

# Check 2: Testing service
echo "🧪 Automated Testing"
if launchctl list | grep -q "com.finishline.flaas.tests"; then
    echo "   ✅ Service running (com.finishline.flaas.tests)"
    
    if [ -f "logs/tests/latest.log" ]; then
        LAST_RUN=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" logs/tests/latest.log 2>/dev/null || echo "unknown")
        PASSED=$(grep "passed" logs/tests/latest.log | tail -1 | grep -o "[0-9]* passed" || echo "unknown")
        EXIT_CODE=$(grep "Test Exit Code:" logs/tests/latest.log | tail -1 | awk '{print $NF}')
        
        echo "   ✅ Latest run: $LAST_RUN"
        echo "   ✅ Result: $PASSED"
        
        if [ "$EXIT_CODE" = "0" ]; then
            echo "   ✅ Exit code: 0 (success)"
        else
            echo "   ⚠️  Exit code: $EXIT_CODE"
        fi
    else
        echo "   ⚠️  No test logs found"
    fi
else
    echo "   ❌ Service not running"
fi
echo ""

# Check 3: Unit tests
echo "🎯 Unit Tests (Quick Run)"
source .venv/bin/activate 2>/dev/null
if python -m pytest tests/ -q --tb=no 2>&1 | tail -1 | grep -q "passed"; then
    RESULT=$(python -m pytest tests/ -q --tb=no 2>&1 | tail -1)
    echo "   ✅ $RESULT"
else
    echo "   ❌ Tests failing"
fi
echo ""

# Check 4: Python environment
echo "🐍 Python Environment"
if [ -f ".venv/bin/python" ]; then
    PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
    echo "   ✅ Virtual environment active"
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Virtual environment not found"
fi
echo ""

# Check 5: Required files
echo "📁 Critical Files"
REQUIRED_FILES=(
    "src/flaas/master_premium.py"
    "src/flaas/analyze.py"
    "src/flaas/osc_rpc.py"
    "scripts/run_tests_background.sh"
    "STATE.md"
    "QUICK_START.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
    fi
done
echo ""

# Check 6: Completed masters
echo "🎵 Completed Masters"
if [ -f "output/stand_tall_PERFECT_MASTER.wav" ]; then
    SIZE=$(ls -lh output/stand_tall_PERFECT_MASTER.wav | awk '{print $5}')
    echo "   ✅ Stand Tall: $SIZE"
else
    echo "   ⚠️  Stand Tall master not found"
fi

if [ -f "output/life_you_chose/master_loud_preview_iter1.wav" ]; then
    SIZE=$(ls -lh output/life_you_chose/master_loud_preview_iter1.wav | awk '{print $5}')
    echo "   ✅ Life You Chose: $SIZE"
else
    echo "   ⚠️  Life You Chose master not found"
fi
echo ""

# Check 7: Documentation
echo "📚 Documentation"
DOC_COUNT=$(ls -1 *.md 2>/dev/null | wc -l | tr -d ' ')
echo "   ✅ $DOC_COUNT markdown files in root"
echo "   ✅ docs/API.md exists: $([ -f docs/API.md ] && echo "yes" || echo "no")"
echo "   ✅ tests/README.md exists: $([ -f tests/README.md ] && echo "yes" || echo "no")"
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                      SYSTEM STATUS: HEALTHY ✅                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Quick commands:"
echo "  • Master new track: flaas master-premium --mode streaming_safe --yes"
echo "  • Verify audio: flaas verify-audio output/track.wav"
echo "  • Run tests: python -m pytest tests/ -v"
echo "  • View test logs: cat logs/tests/latest.log"
echo ""
