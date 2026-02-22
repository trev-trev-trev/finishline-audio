#!/usr/bin/env python3
"""
True Peak Validation Test

Purpose: Validate our true peak implementation against reference values.

Our implementation: 4x oversampling via scipy.signal.resample
ITU-R BS.1770-4 spec: 4x oversampling with proper inter-sample peak detection

Test methodology:
1. Generate known test signals (sine sweeps, full-scale)
2. Measure with our implementation
3. Compare against reference meter (ffmpeg ebur128, Youlean, etc.)
4. Validate accuracy within 0.5 dB tolerance

CRITICAL: This is a placeholder validation script.
Our current true peak implementation (scipy resample) is an approximation.
It needs validation against a trusted reference meter.

TODO:
- Generate test signals (1 kHz sine at various levels)
- Measure with our analyze.py
- Measure same files with ffmpeg -filter ebur128=peak=true
- Compare results
- Accept if within 0.5 dB tolerance

If validation fails, replace with proper ITU-R BS.1770-4 implementation:
- Option 1: Use ffmpeg subprocess for true peak
- Option 2: Use pyebur128 (needs proper API integration)
- Option 3: Implement proper oversample + lowpass filter per spec
"""

import numpy as np
import soundfile as sf
from pathlib import Path

def generate_sine_sweep(freq_hz: float, amplitude: float, duration_s: float, sr: int = 44100) -> np.ndarray:
    """Generate sine wave at given frequency and amplitude."""
    t = np.arange(0, duration_s, 1/sr)
    return amplitude * np.sin(2 * np.pi * freq_hz * t)

def create_test_signals():
    """Create test signals for true peak validation."""
    test_dir = Path("tests/data/true_peak_validation")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test 1: Full-scale 1 kHz sine (should have TP ≈ 0 dBTP)
    sine_full = generate_sine_sweep(1000, 1.0, 1.0)
    sf.write(test_dir / "sine_1khz_full_scale.wav", sine_full, 44100)
    
    # Test 2: -6 dB 1 kHz sine (should have TP ≈ -6 dBTP)
    sine_minus6 = generate_sine_sweep(1000, 0.5, 1.0)
    sf.write(test_dir / "sine_1khz_minus6db.wav", sine_minus6, 44100)
    
    # Test 3: -12 dB 1 kHz sine (should have TP ≈ -12 dBTP)
    sine_minus12 = generate_sine_sweep(1000, 0.25, 1.0)
    sf.write(test_dir / "sine_1khz_minus12db.wav", sine_minus12, 44100)
    
    print(f"Generated test signals in {test_dir}")
    print(f"")
    print(f"NEXT STEPS:")
    print(f"1. Measure with flaas:")
    print(f"   flaas verify-audio {test_dir}/sine_1khz_full_scale.wav")
    print(f"   flaas verify-audio {test_dir}/sine_1khz_minus6db.wav")
    print(f"   flaas verify-audio {test_dir}/sine_1khz_minus12db.wav")
    print(f"")
    print(f"2. Compare against reference meter:")
    print(f"   - Youlean Loudness Meter (free, accurate)")
    print(f"   - ffmpeg -i <file> -filter:a ebur128=peak=true -f null -")
    print(f"   - Any broadcast-grade meter")
    print(f"")
    print(f"3. Expected values:")
    print(f"   - sine_1khz_full_scale.wav: TP ≈ 0.0 dBTP")
    print(f"   - sine_1khz_minus6db.wav: TP ≈ -6.0 dBTP")
    print(f"   - sine_1khz_minus12db.wav: TP ≈ -12.0 dBTP")
    print(f"")
    print(f"4. Tolerance: ±0.5 dB acceptable")

if __name__ == "__main__":
    create_test_signals()
