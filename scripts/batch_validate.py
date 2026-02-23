#!/usr/bin/env python3
"""
Batch Streaming Validator

Scans output/ directory for all WAV files and validates them against
streaming platform requirements. Generates a summary report showing
which masters are ready for distribution and which need attention.
"""

import sys
from pathlib import Path
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flaas.analyze import analyze_wav


@dataclass
class ValidationResult:
    """Result of validating a single file"""
    file_path: str
    file_name: str
    lufs_i: float
    true_peak_dbtp: float
    sample_rate: int
    duration_sec: float
    streaming_safe: bool  # True if meets -1.0 dBTP requirement
    spotify_ready: bool  # -16 to -13 LUFS
    apple_ready: bool  # -17 to -15 LUFS
    youtube_ready: bool  # -15 to -12 LUFS
    issues: list[str]


def validate_file(file_path: Path) -> ValidationResult:
    """Validate a single WAV file"""
    try:
        analysis = analyze_wav(str(file_path))
        
        # Check streaming safety (true peak)
        streaming_safe = analysis.true_peak_dbtp <= -1.0
        
        # Check platform-specific LUFS targets
        spotify_ready = -16.0 <= analysis.lufs_i <= -13.0 and streaming_safe
        apple_ready = -17.0 <= analysis.lufs_i <= -15.0 and streaming_safe
        youtube_ready = -15.0 <= analysis.lufs_i <= -12.0 and streaming_safe
        
        # Collect issues
        issues = []
        if not streaming_safe:
            issues.append(f"True Peak {analysis.true_peak_dbtp:.2f} dBTP > -1.0 (CLIPPING RISK)")
        if not (spotify_ready or apple_ready or youtube_ready):
            issues.append(f"LUFS {analysis.lufs_i:.2f} outside all platform ranges")
        
        return ValidationResult(
            file_path=str(file_path),
            file_name=file_path.name,
            lufs_i=analysis.lufs_i,
            true_peak_dbtp=analysis.true_peak_dbtp,
            sample_rate=analysis.sr,
            duration_sec=analysis.duration_sec,
            streaming_safe=streaming_safe,
            spotify_ready=spotify_ready,
            apple_ready=apple_ready,
            youtube_ready=youtube_ready,
            issues=issues,
        )
    except Exception as e:
        return ValidationResult(
            file_path=str(file_path),
            file_name=file_path.name,
            lufs_i=0.0,
            true_peak_dbtp=0.0,
            sample_rate=0,
            duration_sec=0.0,
            streaming_safe=False,
            spotify_ready=False,
            apple_ready=False,
            youtube_ready=False,
            issues=[f"Analysis failed: {str(e)}"],
        )


def find_wav_files(output_dir: Path) -> list[Path]:
    """Recursively find all WAV files in output directory"""
    return sorted(output_dir.rglob("*.wav"))


def print_summary_report(results: list[ValidationResult]):
    """Print comprehensive batch validation report"""
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║            BATCH STREAMING VALIDATION REPORT                          ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    
    if not results:
        print("❌ No WAV files found in output/ directory")
        return
    
    # Summary statistics
    total_files = len(results)
    streaming_safe_count = sum(1 for r in results if r.streaming_safe)
    spotify_ready_count = sum(1 for r in results if r.spotify_ready)
    apple_ready_count = sum(1 for r in results if r.apple_ready)
    youtube_ready_count = sum(1 for r in results if r.youtube_ready)
    files_with_issues = sum(1 for r in results if r.issues)
    
    print("═" * 75)
    print("SUMMARY STATISTICS")
    print("═" * 75)
    print(f"  Total files scanned:       {total_files}")
    print(f"  Streaming safe (-1.0 dBTP): {streaming_safe_count}/{total_files}")
    print(f"  Spotify ready:             {spotify_ready_count}/{total_files}")
    print(f"  Apple Music ready:         {apple_ready_count}/{total_files}")
    print(f"  YouTube ready:             {youtube_ready_count}/{total_files}")
    print(f"  Files with issues:         {files_with_issues}/{total_files}")
    print()
    
    # Files ready for distribution
    ready_files = [r for r in results if not r.issues]
    if ready_files:
        print("═" * 75)
        print("✅ READY FOR DISTRIBUTION")
        print("═" * 75)
        for result in ready_files:
            platforms = []
            if result.spotify_ready:
                platforms.append("Spotify")
            if result.apple_ready:
                platforms.append("Apple")
            if result.youtube_ready:
                platforms.append("YouTube")
            
            platform_str = ", ".join(platforms) if platforms else "No optimal platform"
            print(f"  {result.file_name}")
            print(f"    LUFS: {result.lufs_i:.2f}  |  True Peak: {result.true_peak_dbtp:.2f} dBTP")
            print(f"    Platforms: {platform_str}")
            print()
    
    # Files needing attention
    issues_files = [r for r in results if r.issues]
    if issues_files:
        print("═" * 75)
        print("⚠️  NEEDS ATTENTION")
        print("═" * 75)
        for result in issues_files:
            print(f"  {result.file_name}")
            print(f"    LUFS: {result.lufs_i:.2f}  |  True Peak: {result.true_peak_dbtp:.2f} dBTP")
            for issue in result.issues:
                print(f"    ❌ {issue}")
            
            # Suggest fix
            if not result.streaming_safe:
                print(f"    💡 Fix: Re-master with L3 'Out Ceiling' set to -1.5 dB or lower")
            print()
    
    # Overall verdict
    print("═" * 75)
    print("VERDICT")
    print("═" * 75)
    
    if files_with_issues == 0:
        print("🎉 All masters are ready for streaming distribution!")
    elif files_with_issues == total_files:
        print("⚠️  All masters need attention before distribution")
        print("    Recommendation: Re-run mastering with correct limiter settings")
    else:
        print(f"⚠️  {files_with_issues}/{total_files} master(s) need attention")
        print(f"✅ {total_files - files_with_issues}/{total_files} master(s) ready for distribution")
    print()
    
    # Detailed file list
    print("═" * 75)
    print("DETAILED FILE LIST")
    print("═" * 75)
    print(f"{'File':<40} {'LUFS':>8} {'Peak':>8} {'Safe':>6} {'Status':>12}")
    print("-" * 75)
    
    for result in results:
        status = "✅ READY" if not result.issues else "⚠️  REVIEW"
        safe_icon = "✅" if result.streaming_safe else "❌"
        
        # Truncate filename if too long
        display_name = result.file_name
        if len(display_name) > 40:
            display_name = display_name[:37] + "..."
        
        print(
            f"{display_name:<40} "
            f"{result.lufs_i:>8.2f} "
            f"{result.true_peak_dbtp:>8.2f} "
            f"{safe_icon:>6} "
            f"{status:>12}"
        )
    
    print()


def main():
    # Get output directory
    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / "output"
    
    if not output_dir.exists():
        print(f"❌ Error: Output directory not found: {output_dir}")
        sys.exit(1)
    
    print(f"Scanning: {output_dir}")
    print("Finding WAV files...")
    print()
    
    # Find all WAV files
    wav_files = find_wav_files(output_dir)
    
    if not wav_files:
        print("❌ No WAV files found")
        sys.exit(0)
    
    print(f"Found {len(wav_files)} WAV file(s)")
    print("Analyzing files (this may take a moment)...")
    print()
    
    # Validate each file
    results = []
    for i, wav_file in enumerate(wav_files, 1):
        print(f"  [{i}/{len(wav_files)}] {wav_file.name}...", end=" ")
        result = validate_file(wav_file)
        results.append(result)
        status = "✅" if not result.issues else "⚠️"
        print(status)
    
    print()
    
    # Print summary report
    print_summary_report(results)
    
    # Exit code: 0 if all pass, 1 if any issues
    any_issues = any(r.issues for r in results)
    sys.exit(1 if any_issues else 0)


if __name__ == "__main__":
    main()
