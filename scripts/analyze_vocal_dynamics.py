#!/usr/bin/env python3
"""
Analyze vocal waveform dynamics to find loud/quiet sections.
"""
import sys
from pathlib import Path
import numpy as np
import soundfile as sf

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flaas.audio_io import read_audio_info

def analyze_dynamics(wav_path: Path):
    """Analyze waveform dynamics and identify problem areas."""
    
    # Read audio
    data, sr = sf.read(wav_path)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        mono = np.mean(data, axis=1)
    else:
        mono = data
    
    # Calculate RMS over 1-second windows
    window_size = sr  # 1 second
    hop_size = sr // 2  # 0.5 second hop
    
    num_windows = (len(mono) - window_size) // hop_size + 1
    
    rms_values = []
    peak_values = []
    timestamps = []
    
    for i in range(num_windows):
        start = i * hop_size
        end = start + window_size
        window = mono[start:end]
        
        rms = np.sqrt(np.mean(window ** 2))
        peak = np.max(np.abs(window))
        
        rms_db = 20 * np.log10(rms) if rms > 0 else -np.inf
        peak_db = 20 * np.log10(peak) if peak > 0 else -np.inf
        
        rms_values.append(rms_db)
        peak_values.append(peak_db)
        timestamps.append(start / sr)
    
    rms_values = np.array(rms_values)
    peak_values = np.array(peak_values)
    
    # Calculate statistics
    rms_mean = np.mean(rms_values[np.isfinite(rms_values)])
    rms_std = np.std(rms_values[np.isfinite(rms_values)])
    rms_min = np.min(rms_values[np.isfinite(rms_values)])
    rms_max = np.max(rms_values[np.isfinite(rms_values)])
    
    peak_mean = np.mean(peak_values[np.isfinite(peak_values)])
    peak_max = np.max(peak_values[np.isfinite(peak_values)])
    
    # Find problem areas
    # Sections significantly above/below mean
    loud_threshold = rms_mean + rms_std
    quiet_threshold = rms_mean - rms_std
    
    loud_sections = []
    quiet_sections = []
    
    for i, (timestamp, rms) in enumerate(zip(timestamps, rms_values)):
        if np.isfinite(rms):
            if rms > loud_threshold:
                loud_sections.append((timestamp, rms, rms - rms_mean))
            elif rms < quiet_threshold:
                quiet_sections.append((timestamp, rms, rms - rms_mean))
    
    return {
        "rms_mean": rms_mean,
        "rms_std": rms_std,
        "rms_range": rms_max - rms_min,
        "peak_max": peak_max,
        "loud_sections": loud_sections[:10],  # Top 10
        "quiet_sections": quiet_sections[:10],  # Bottom 10
        "duration": len(mono) / sr,
    }

def main():
    wav_path = Path("output/stand_tall_vocal_raw.wav")
    
    if not wav_path.exists():
        print(f"Error: {wav_path} not found")
        return 1
    
    print("=" * 70)
    print("VOCAL DYNAMICS ANALYSIS")
    print("=" * 70)
    print()
    print(f"Analyzing: {wav_path.name}")
    print("(This may take 10-20 seconds for long files...)")
    print()
    
    try:
        result = analyze_dynamics(wav_path)
        
        print("=" * 70)
        print("STATISTICS")
        print("=" * 70)
        print(f"Duration: {result['duration']:.1f} seconds")
        print(f"RMS Mean: {result['rms_mean']:.2f} dBFS")
        print(f"RMS Std Dev: {result['rms_std']:.2f} dB (consistency)")
        print(f"RMS Range: {result['rms_range']:.2f} dB (quietest to loudest)")
        print(f"Peak Max: {result['peak_max']:.2f} dBFS")
        print()
        
        print("=" * 70)
        print("INTERPRETATION")
        print("=" * 70)
        
        if result['rms_std'] > 3.0:
            print(f"⚠️  HIGH INCONSISTENCY: {result['rms_std']:.2f} dB std dev")
            print("    → Clip gain (Layer A) is CRITICAL")
            print("    → Expect to make 10-20 adjustments")
        elif result['rms_std'] > 2.0:
            print(f"⚠️  MODERATE INCONSISTENCY: {result['rms_std']:.2f} dB std dev")
            print("    → Clip gain (Layer A) is important")
            print("    → Expect to make 5-10 adjustments")
        else:
            print(f"✓ GOOD CONSISTENCY: {result['rms_std']:.2f} dB std dev")
            print("    → Clip gain (Layer A) can be minimal")
        
        print()
        
        if result['rms_range'] > 15.0:
            print(f"⚠️  WIDE DYNAMIC RANGE: {result['rms_range']:.2f} dB")
            print("    → Extreme loud/quiet variation")
            print("    → Compression alone won't fix this")
        elif result['rms_range'] > 10.0:
            print(f"⚠️  MODERATE DYNAMIC RANGE: {result['rms_range']:.2f} dB")
            print("    → Normal for vocals")
        else:
            print(f"✓ NARROW DYNAMIC RANGE: {result['rms_range']:.2f} dB")
        
        print()
        print("=" * 70)
        print("LOUD SECTIONS (Need clip gain reduction)")
        print("=" * 70)
        
        if len(result['loud_sections']) > 0:
            print(f"Found {len(result['loud_sections'])} sections louder than average:")
            print()
            for i, (timestamp, rms, diff) in enumerate(result['loud_sections'][:5], 1):
                mins = int(timestamp // 60)
                secs = int(timestamp % 60)
                print(f"{i}. {mins:02d}:{secs:02d} - {rms:.2f} dBFS (+{diff:.2f} dB)")
                print(f"   → Reduce by ~{min(diff, 4.0):.1f} dB with clip gain")
        else:
            print("None found (all sections within 1 std dev)")
        
        print()
        print("=" * 70)
        print("QUIET SECTIONS (Need clip gain boost)")
        print("=" * 70)
        
        if len(result['quiet_sections']) > 0:
            print(f"Found {len(result['quiet_sections'])} sections quieter than average:")
            print()
            for i, (timestamp, rms, diff) in enumerate(result['quiet_sections'][:5], 1):
                mins = int(timestamp // 60)
                secs = int(timestamp % 60)
                print(f"{i}. {mins:02d}:{secs:02d} - {rms:.2f} dBFS ({diff:.2f} dB)")
                print(f"   → Boost by ~{min(abs(diff), 4.0):.1f} dB with clip gain")
        else:
            print("None found (all sections within 1 std dev)")
        
        print()
        print("=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print()
        print("1. CRITICAL: Reduce Utility PRE gain by 2-3 dB")
        print("   (Peak at -1.5 dBFS + True Peak +0.46 dBTP = clipping!)")
        print()
        print("2. Layer A: Fix loud/quiet sections listed above")
        print("   (Use Clip Gain slider or automate Utility PRE)")
        print()
        print("3. Add compression chain (R-Vox 4-6 dB GR)")
        print()
        print("4. Re-export and verify True Peak < 0 dBTP")
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"Error analyzing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
