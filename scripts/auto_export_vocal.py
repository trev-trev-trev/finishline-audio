#!/usr/bin/env python3
"""
Automatically export VOCALS group and analyze.
No manual steps required.
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
    print("EXPORTING VOCALS GROUP (AUTOMATED)")
    print("=" * 70)
    print()
    print(f"Target: {export_file.name}")
    print()
    
    # Delete old file
    if export_file.exists():
        print(f"Removing old file: {export_file.name}")
        export_file.unlink()
    
    # Export (UI automation will handle everything)
    print("Starting export via UI automation...")
    print("(This will open Export dialog, type filename, click Save)")
    print()
    
    try:
        auto_export_wav(export_file, timeout_s=600)
        print()
        print(f"✓ Export complete: {export_file.name}")
    except Exception as e:
        print()
        print(f"✗ Export failed: {e}")
        print()
        print("Troubleshooting:")
        print("  - Is Ableton Live running?")
        print("  - Is Stand Tall project open?")
        print("  - Is loop brace set?")
        print("  - Try running: ./scripts/test_export_probe.sh")
        return 1
    
    # Analyze
    print()
    print("=" * 70)
    print("ANALYZING VOCAL")
    print("=" * 70)
    print()
    
    analysis = analyze_wav(export_file)
    
    print(f"FILE: {export_file.name}")
    print(f"LUFS-I: {analysis.lufs_i:.2f} dB")
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
    print("EXPORT COMPLETE")
    print("=" * 70)
    print()
    print(f"File: output/{export_file.name}")
    print(f"Analysis: output/{analysis_file.name}")
    print()
    print("I'll now analyze the waveform and generate targeted action plan.")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
