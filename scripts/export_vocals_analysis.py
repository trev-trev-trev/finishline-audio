#!/usr/bin/env python3
"""
Export VOCALS group and analyze for processing recommendations.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flaas.ui_export_macos import auto_export_wav
from flaas.analyze import analyze_wav
import json

def main():
    output_dir = Path("output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = output_dir / "stand_tall_vocal_raw.wav"
    
    print("=" * 70)
    print("STAND TALL - VOCAL ANALYSIS EXPORT")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Solo VOCALS group in Ableton")
    print("  2. Export to: stand_tall_vocal_raw.wav")
    print("  3. Analyze levels, peaks, LUFS")
    print("  4. Generate targeted action plan")
    print()
    print("PRE-REQUISITES:")
    print("  [ ] Ableton: Stand Tall project open")
    print("  [ ] VOCALS group exists (all vocal tracks routed to it)")
    print("  [ ] Loop brace set over representative section (verse + chorus)")
    print("  [ ] All processing on VOCALS group BYPASSED (we want raw)")
    print()
    input("Press Enter to start export...")
    print()
    
    # Delete old file
    if export_file.exists():
        export_file.unlink()
    
    # Export
    print(f"Exporting VOCALS group to: {export_file.name}")
    print("NOTE: You must MANUALLY solo VOCALS group before export!")
    print("      (I can't control track solo via OSC)")
    print()
    input("Press Enter after you've soloed VOCALS group...")
    print()
    
    try:
        auto_export_wav(export_file, timeout_s=600)
        print(f"✓ Exported: {export_file.name}")
    except Exception as e:
        print(f"✗ Export failed: {e}")
        return 1
    
    # Analyze
    print()
    print("=" * 70)
    print("ANALYZING VOCAL")
    print("=" * 70)
    print()
    
    analysis = analyze_wav(export_file)
    
    print(f"FILE: {export_file.name}")
    print(f"LUFS-I: {analysis.lufs_i:.2f}")
    print(f"Peak: {analysis.peak_dbfs:.2f} dBFS")
    print(f"True Peak: {analysis.true_peak_dbtp:.2f} dBTP")
    print(f"Duration: {analysis.duration_sec:.1f} seconds")
    print()
    
    # Save analysis
    analysis_file = output_dir / "stand_tall_vocal_analysis.json"
    with analysis_file.open("w") as f:
        json.dump({
            "file": str(export_file),
            "lufs_i": analysis.lufs_i,
            "peak_dbfs": analysis.peak_dbfs,
            "true_peak_dbtp": analysis.true_peak_dbtp,
            "duration_sec": analysis.duration_sec,
        }, f, indent=2)
    
    print(f"✓ Analysis saved: {analysis_file.name}")
    print()
    print("=" * 70)
    print("NEXT STEP")
    print("=" * 70)
    print()
    print("Paste this in Cursor:")
    print(f"  output/stand_tall_vocal_raw.wav")
    print()
    print("I'll analyze the waveform and generate targeted action plan.")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
