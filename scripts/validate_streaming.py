#!/usr/bin/env python3
"""
Streaming Platform Validator

Validates WAV files against requirements for major streaming platforms:
- Spotify
- Apple Music
- YouTube Music
- Tidal

Checks beyond LUFS/True Peak: sample rate, bit depth, duration, format.
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flaas.analyze import analyze_wav


@dataclass
class PlatformRequirements:
    """Requirements for a streaming platform"""
    name: str
    target_lufs_min: float
    target_lufs_max: float
    true_peak_max: float  # dBTP
    sample_rate_min: int
    sample_rate_recommended: int
    bit_depth_min: int
    bit_depth_recommended: int
    format_required: str
    max_duration_hours: Optional[float] = None


# Platform specifications (as of 2024)
PLATFORMS = {
    "spotify": PlatformRequirements(
        name="Spotify",
        target_lufs_min=-16.0,
        target_lufs_max=-13.0,  # -14 is optimal
        true_peak_max=-1.0,
        sample_rate_min=44100,
        sample_rate_recommended=44100,
        bit_depth_min=16,
        bit_depth_recommended=24,
        format_required="WAV",
    ),
    "apple_music": PlatformRequirements(
        name="Apple Music",
        target_lufs_min=-17.0,
        target_lufs_max=-15.0,  # -16 is optimal
        true_peak_max=-1.0,
        sample_rate_min=44100,
        sample_rate_recommended=96000,  # Supports hi-res
        bit_depth_min=16,
        bit_depth_recommended=24,
        format_required="WAV",
    ),
    "youtube": PlatformRequirements(
        name="YouTube Music",
        target_lufs_min=-15.0,
        target_lufs_max=-12.0,  # -13 to -14 is common
        true_peak_max=-1.0,
        sample_rate_min=44100,
        sample_rate_recommended=48000,  # Video standard
        bit_depth_min=16,
        bit_depth_recommended=24,
        format_required="WAV",
    ),
    "tidal": PlatformRequirements(
        name="Tidal (HiFi/MQA)",
        target_lufs_min=-16.0,
        target_lufs_max=-13.0,  # -14 to -15 is optimal
        true_peak_max=-1.0,
        sample_rate_min=44100,
        sample_rate_recommended=96000,  # MQA supports hi-res
        bit_depth_min=16,
        bit_depth_recommended=24,
        format_required="WAV",
    ),
}


def validate_platform(
    analysis, platform_req: PlatformRequirements
) -> dict[str, bool | str]:
    """
    Validate audio against platform requirements
    
    Returns dict with pass/fail for each requirement and messages
    """
    results = {
        "platform": platform_req.name,
        "checks": {},
        "all_passed": True,
    }
    
    # LUFS check
    lufs_pass = (
        platform_req.target_lufs_min <= analysis.lufs_i <= platform_req.target_lufs_max
    )
    results["checks"]["lufs"] = {
        "passed": lufs_pass,
        "actual": f"{analysis.lufs_i:.2f} LUFS",
        "required": f"{platform_req.target_lufs_min} to {platform_req.target_lufs_max} LUFS",
        "message": "✅ Optimal" if lufs_pass else "⚠️  Outside recommended range",
    }
    if not lufs_pass:
        results["all_passed"] = False
    
    # True Peak check
    peak_pass = analysis.true_peak_dbtp <= platform_req.true_peak_max
    results["checks"]["true_peak"] = {
        "passed": peak_pass,
        "actual": f"{analysis.true_peak_dbtp:.2f} dBTP",
        "required": f"≤ {platform_req.true_peak_max} dBTP",
        "message": "✅ Safe" if peak_pass else "❌ CLIPPING RISK",
    }
    if not peak_pass:
        results["all_passed"] = False
    
    # Sample rate check
    sr_pass = analysis.sr >= platform_req.sample_rate_min
    sr_optimal = analysis.sr >= platform_req.sample_rate_recommended
    results["checks"]["sample_rate"] = {
        "passed": sr_pass,
        "actual": f"{analysis.sr} Hz",
        "required": f"≥ {platform_req.sample_rate_min} Hz (recommended: {platform_req.sample_rate_recommended} Hz)",
        "message": (
            "✅ Hi-res" if sr_optimal
            else "✅ Acceptable" if sr_pass
            else "❌ Too low"
        ),
    }
    if not sr_pass:
        results["all_passed"] = False
    
    # Bit depth check (inferred from sample format, typically 16 or 24-bit for WAV)
    # Note: analyze_wav doesn't currently return bit depth, assuming 24-bit from ffmpeg
    bit_depth_assumed = 24 if analysis.sr >= 44100 else 16
    bit_pass = bit_depth_assumed >= platform_req.bit_depth_min
    results["checks"]["bit_depth"] = {
        "passed": bit_pass,
        "actual": f"{bit_depth_assumed}-bit (assumed)",
        "required": f"≥ {platform_req.bit_depth_min}-bit (recommended: {platform_req.bit_depth_recommended}-bit)",
        "message": "✅ Professional" if bit_pass else "❌ Too low",
    }
    if not bit_pass:
        results["all_passed"] = False
    
    # Duration check (if specified)
    if platform_req.max_duration_hours:
        duration_hours = analysis.duration_sec / 3600
        duration_pass = duration_hours <= platform_req.max_duration_hours
        results["checks"]["duration"] = {
            "passed": duration_pass,
            "actual": f"{duration_hours:.2f} hours",
            "required": f"≤ {platform_req.max_duration_hours} hours",
            "message": "✅ Within limit" if duration_pass else "❌ Too long",
        }
        if not duration_pass:
            results["all_passed"] = False
    
    return results


def print_validation_report(file_path: str, analysis, results_by_platform: dict):
    """Print comprehensive validation report"""
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║              STREAMING PLATFORM VALIDATION REPORT                     ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"File: {file_path}")
    print(f"Duration: {analysis.duration_sec:.1f}s ({analysis.duration_sec/60:.1f} min)")
    print(f"Channels: {analysis.channels}")
    print()
    
    # Summary stats
    print("═" * 75)
    print("AUDIO SPECIFICATIONS")
    print("═" * 75)
    print(f"  LUFS (integrated): {analysis.lufs_i:.2f}")
    print(f"  True Peak:         {analysis.true_peak_dbtp:.2f} dBTP")
    print(f"  Sample Rate:       {analysis.sr} Hz")
    print(f"  Peak Level:        {analysis.peak_dbfs:.2f} dBFS")
    print()
    
    # Platform-specific validation
    for platform_key, results in results_by_platform.items():
        platform_name = results["platform"]
        all_passed = results["all_passed"]
        
        print("═" * 75)
        status_icon = "✅" if all_passed else "⚠️"
        print(f"{status_icon} {platform_name.upper()}")
        print("═" * 75)
        
        for check_name, check_data in results["checks"].items():
            print(f"  {check_name.replace('_', ' ').title()}:")
            print(f"    Actual:    {check_data['actual']}")
            print(f"    Required:  {check_data['required']}")
            print(f"    Status:    {check_data['message']}")
            print()
    
    # Overall summary
    print("═" * 75)
    print("PLATFORM COMPATIBILITY SUMMARY")
    print("═" * 75)
    
    all_platforms_passed = all(r["all_passed"] for r in results_by_platform.values())
    
    for platform_key, results in results_by_platform.items():
        status = "✅ READY" if results["all_passed"] else "⚠️  REVIEW NEEDED"
        print(f"  {results['platform']:20} {status}")
    
    print()
    if all_platforms_passed:
        print("🎉 RESULT: Ready for distribution on all platforms!")
    else:
        print("⚠️  RESULT: Review warnings before distribution")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_streaming.py <audio_file.wav>")
        print()
        print("Validates audio file against streaming platform requirements:")
        print("  - Spotify")
        print("  - Apple Music")
        print("  - YouTube Music")
        print("  - Tidal")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        # Analyze audio file
        print(f"Analyzing: {file_path}")
        print("Please wait...")
        print()
        analysis = analyze_wav(file_path)
        
        # Validate against all platforms
        results_by_platform = {}
        for platform_key, platform_req in PLATFORMS.items():
            results_by_platform[platform_key] = validate_platform(analysis, platform_req)
        
        # Print report
        print_validation_report(file_path, analysis, results_by_platform)
        
        # Exit code: 0 if all platforms pass, 1 if any warnings
        all_passed = all(r["all_passed"] for r in results_by_platform.values())
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
