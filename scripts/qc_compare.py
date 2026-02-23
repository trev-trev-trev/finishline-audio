#!/usr/bin/env python3
"""
QC Compare - Comprehensive loudness verification

Validates audio against intended targets and answers:
- Does actual LUFS match intended target?
- If we gain-match to -14 or -9 LUFS, what does true peak become?
- Short-term/momentary variation (section dynamics)
- LRA, crest factor

Usage:
  python scripts/qc_compare.py output/stand_tall_premium_iter2.wav
  python scripts/qc_compare.py output/file.wav --target -14  # Explicit target
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flaas.analyze import analyze_wav


def load_stereo_interleaved(path: str | Path) -> tuple[np.ndarray, int]:
    """Load audio as float32 interleaved stereo for pyebur128."""
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    if data.shape[1] == 1:
        # Mono: duplicate to stereo
        data = np.column_stack([data[:, 0], data[:, 0]])
    # Interleave: [L0,R0,L1,R1,...]
    interleaved = data.flatten(order="F")
    return interleaved, int(sr)


def compute_ebur128_metrics(path: str | Path) -> dict:
    """Compute short-term, momentary via pyebur128. LRA via pyloudnorm (more reliable)."""
    result = {}

    # LRA from pyloudnorm (BS.1770 compliant, no mode flags needed)
    try:
        import pyloudnorm as pyln
        from flaas.audio_io import read_mono_float
        mono, sr = read_mono_float(path)
        meter = pyln.Meter(sr)
        result["lra"] = float(meter.loudness_range(mono))
    except Exception as e:
        result["lra_error"] = str(e)

    # Short-term, momentary from pyebur128 (requires MODE_S, MODE_M)
    try:
        import pyebur128
    except ImportError:
        return result

    interleaved, sr = load_stereo_interleaved(path)
    channels = 2
    # MODE_I=5, MODE_S=3, MODE_M=1 (from pyebur128) - avoid MODE_LRA which needs extra flag
    mode = 5 | 3 | 1  # I | S | M
    state = pyebur128.R128State(channels, sr, mode)

    chunk = 4096
    n_frames = len(interleaved) // channels
    n_chunks = (n_frames + chunk - 1) // chunk

    for i in range(n_chunks):
        start = i * chunk * channels
        end = min((i + 1) * chunk * channels, len(interleaved))
        frames = (end - start) // channels
        if frames <= 0:
            break
        state.add_frames(interleaved[start:end], frames)

    try:
        result["lufs_shortterm"] = float(pyebur128.get_loudness_shortterm(state))
    except ValueError:
        pass
    try:
        result["lufs_momentary"] = float(pyebur128.get_loudness_momentary(state))
    except ValueError:
        pass

    return result


def compute_crest_factor(mono: np.ndarray) -> float:
    """Crest factor = peak / RMS (higher = more dynamic)."""
    rms = np.sqrt(np.mean(mono**2))
    if rms == 0:
        return 0.0
    peak = np.max(np.abs(mono))
    return float(peak / rms)


def gain_match_simulation(
    lufs_i: float, true_peak_dbtp: float, targets: list[float]
) -> list[dict]:
    """Simulate: if we gain-match to target LUFS, what does true peak become?"""
    results = []
    for target in targets:
        gain_db = target - lufs_i
        projected_tp = true_peak_dbtp + gain_db
        safe = projected_tp <= -1.0
        results.append({
            "target_lufs": target,
            "gain_db": round(gain_db, 2),
            "projected_true_peak_dbtp": round(projected_tp, 2),
            "safe": safe,
        })
    return results


def find_jsonl_for_file(wav_path: Path) -> dict | None:
    """Try to find JSONL with iteration data for this file."""
    stem = wav_path.stem  # e.g. stand_tall_premium_iter2
    if "iter" not in stem:
        return None
    out_dir = wav_path.parent
    for j in out_dir.glob("*.jsonl"):
        if "streaming_safe" in j.name or "loud_preview" in j.name:
            for line in j.read_text().strip().split("\n"):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    iter_num = obj.get("iteration")
                    if iter_num is not None and f"iter{iter_num}" in stem:
                        return obj
                except json.JSONDecodeError:
                    continue
    return None


def main():
    parser = argparse.ArgumentParser(description="QC Compare - loudness verification")
    parser.add_argument("wav", help="Path to WAV file")
    parser.add_argument("--target", type=float, default=None, help="Explicit LUFS target (e.g. -14)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    path = Path(args.wav)
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Use flaas analyze for consistency
    analysis = analyze_wav(path)

    # Extended metrics
    ebur = compute_ebur128_metrics(path)
    if "error" in ebur:
        ebur = {}

    from flaas.audio_io import read_mono_float
    mono, _ = read_mono_float(path)
    crest = compute_crest_factor(mono)

    # Gain-match simulation
    targets = [-14.0, -9.0]
    sim = gain_match_simulation(
        analysis.lufs_i, analysis.true_peak_dbtp, targets
    )

    # Intended target from JSONL if available
    jsonl_meta = find_jsonl_for_file(path)
    intended_target = args.target
    intended_mode = None
    if jsonl_meta:
        intended_mode = jsonl_meta.get("mode")
        if intended_mode == "streaming_safe":
            intended_target = -14.0
        elif intended_mode == "loud_preview":
            intended_target = -9.0
        elif intended_mode == "headroom":
            intended_target = -10.0

    # Target alignment
    target_delta = None
    target_pass = None
    if intended_target is not None:
        target_delta = analysis.lufs_i - intended_target
        target_pass = abs(target_delta) <= 0.5

    # Build report
    report = {
        "file": str(path),
        "duration_sec": round(analysis.duration_sec, 1),
        "sample_rate": analysis.sr,
        "channels": analysis.channels,
        "lufs_i": round(analysis.lufs_i, 2),
        "true_peak_dbtp": round(analysis.true_peak_dbtp, 2),
        "peak_dbfs": round(analysis.peak_dbfs, 2),
        "lra": round(ebur.get("lra", 0), 2) if ebur else None,
        "lufs_shortterm": round(ebur.get("lufs_shortterm", 0), 2) if ebur else None,
        "lufs_momentary": round(ebur.get("lufs_momentary", 0), 2) if ebur else None,
        "crest_factor": round(crest, 2),
        "intended_mode": intended_mode,
        "intended_target_lufs": intended_target,
        "target_delta_lu": round(target_delta, 2) if target_delta is not None else None,
        "target_hit": target_pass,
        "gain_match_simulation": sim,
        "true_peak_safe": analysis.true_peak_dbtp <= -1.0,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return

    # Human-readable report
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║                    QC COMPARE - LOUDNESS VERIFICATION                   ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"File: {path.name}")
    print(f"Duration: {analysis.duration_sec:.1f}s")
    print()
    print("═" * 75)
    print("AUDIO SPECIFICATIONS")
    print("═" * 75)
    print(f"  LUFS (integrated):  {analysis.lufs_i:.2f}")
    print(f"  True Peak:          {analysis.true_peak_dbtp:.2f} dBTP")
    print(f"  Peak (sample):      {analysis.peak_dbfs:.2f} dBFS")
    if ebur:
        if ebur.get("lra") is not None:
            print(f"  LRA:                {ebur['lra']:.2f} LU")
        # Short-term/momentary are "last window" - may be silence at tail
        st = ebur.get("lufs_shortterm")
        mo = ebur.get("lufs_momentary")
        if st is not None and st > -80:
            print(f"  Short-term (3s):    {st:.2f} LUFS (last window)")
        if mo is not None and mo > -80:
            print(f"  Momentary (400ms): {mo:.2f} LUFS (last window)")
    print(f"  Crest factor:       {crest:.2f}")
    print()

    print("═" * 75)
    print("TARGET ALIGNMENT")
    print("═" * 75)
    if intended_mode:
        print(f"  Intended mode: {intended_mode}")
    if intended_target is not None:
        print(f"  Target LUFS:   {intended_target}")
        print(f"  Actual LUFS:   {analysis.lufs_i:.2f}")
        print(f"  Delta:         {target_delta:+.2f} LU")
        status = "✅ PASS" if target_pass else "❌ FAIL"
        print(f"  Status:        {status} (target ±0.5 LU)")
    else:
        print("  (No intended target from JSONL or --target)")
    print()

    print("═" * 75)
    print("GAIN-MATCH SIMULATION")
    print("═" * 75)
    print("  If we gain-match to target LUFS, what does true peak become?")
    print()
    print(f"  {'Target':>8} {'Gain':>8} {'Projected TP':>14} {'Safe?':>8}")
    print("  " + "-" * 45)
    for row in sim:
        safe_str = "✅" if row["safe"] else "❌"
        print(f"  {row['target_lufs']:>8.1f} {row['gain_db']:>+8.2f} {row['projected_true_peak_dbtp']:>14.2f} {safe_str:>8}")
    print()
    print("  ⚠️  'Safe' at delivery does NOT guarantee safe after platform normalization.")
    print("     Platforms apply gain; if they add +2.3 dB without limiting → clipping risk.")
    print()

    print("═" * 75)
    print("VERDICT")
    print("═" * 75)
    tp_ok = analysis.true_peak_dbtp <= -1.0
    print(f"  True peak at delivery: {'✅ Safe (≤ -1.0 dBTP)' if tp_ok else '❌ Exceeds -1.0 dBTP'}")
    if intended_target is not None and target_pass is not None:
        print(f"  Target alignment:      {'✅ Hit target' if target_pass else '❌ Missed target'}")
    print()

    # Exit code: 0 if all pass
    exit_code = 0 if (tp_ok and (target_pass is None or target_pass)) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
