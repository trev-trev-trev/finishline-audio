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
    lufs_i: float
    created_at_utc: str

def analyze_wav(path: str | Path) -> AnalysisResult:
    info = read_audio_info(path)
    mono, sr = read_mono_float(path)
    if mono.size == 0:
        raise ValueError("empty audio")

    peak = float(np.max(np.abs(mono)))
    peak_dbfs = -float("inf") if peak == 0.0 else float(20.0 * np.log10(peak))

    meter = pyln.Meter(sr)  # BS.1770
    lufs_i = float(meter.integrated_loudness(mono))

    dur = info.samples / info.sr
    return AnalysisResult(
        file=info.path,
        sr=info.sr,
        channels=info.channels,
        samples=info.samples,
        duration_sec=float(dur),
        peak_dbfs=peak_dbfs,
        lufs_i=lufs_i,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )

def write_analysis(path_in: str | Path, path_out: str | Path = "data/reports/analysis.json") -> Path:
    out = Path(path_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res = analyze_wav(path_in)
    out.write_text(json.dumps(asdict(res), indent=2) + "\n", encoding="utf-8")
    return out
