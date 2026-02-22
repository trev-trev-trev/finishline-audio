from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import soundfile as sf
import numpy as np

@dataclass(frozen=True)
class AudioData:
    path: str
    sr: int
    channels: int
    samples: int

def read_audio_info(path: str | Path) -> AudioData:
    p = Path(path)
    info = sf.info(str(p))
    return AudioData(
        path=str(p),
        sr=int(info.samplerate),
        channels=int(info.channels),
        samples=int(info.frames),
    )

def read_mono_float(path: str | Path) -> tuple[np.ndarray, int]:
    x, sr = sf.read(str(path), always_2d=True)
    x = x.astype(np.float32)
    mono = x.mean(axis=1)
    return mono, int(sr)
