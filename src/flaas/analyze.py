from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pyloudnorm as pyln

from flaas.audio_io import read_audio_info, read_mono_float

@dataclass
class AnalysisResult:
    file: str
    sr: int
    channels: int
    samples: int
    duration_sec: float
    peak_dbfs: float
    true_peak_dbtp: float
    lufs_i: float
    created_at_utc: str

def analyze_wav(path: str | Path) -> AnalysisResult:
    info = read_audio_info(path)
    mono, sr = read_mono_float(path)
    if mono.size == 0:
        raise ValueError("empty audio")

    # Sample peak
    peak = float(np.max(np.abs(mono)))
    peak_dbfs = -float("inf") if peak == 0.0 else float(20.0 * np.log10(peak))

    # True peak (4x oversampling approximation for dBTP)
    # For true dBTP we'd need proper ITU-R BS.1770 true peak, but 4x oversample is close
    from scipy import signal
    oversampled = signal.resample(mono, len(mono) * 4)
    true_peak = float(np.max(np.abs(oversampled)))
    true_peak_dbtp = -float("inf") if true_peak == 0.0 else float(20.0 * np.log10(true_peak))

    # LUFS-I (BS.1770)
    meter = pyln.Meter(sr)
    lufs_i = float(meter.integrated_loudness(mono))

    dur = info.samples / info.sr
    return AnalysisResult(
        file=info.path,
        sr=info.sr,
        channels=info.channels,
        samples=info.samples,
        duration_sec=float(dur),
        peak_dbfs=peak_dbfs,
        true_peak_dbtp=true_peak_dbtp,
        lufs_i=lufs_i,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )

def write_analysis(path_in: str | Path, path_out: str | Path = "data/reports/analysis.json") -> Path:
    out = Path(path_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res = analyze_wav(path_in)
    out.write_text(json.dumps(asdict(res), indent=2) + "\n", encoding="utf-8")
    return out
