from __future__ import annotations
from pathlib import Path
from flaas.analyze import analyze_wav
from flaas.check import check_wav

def verify_audio(path: str | Path) -> int:
    a = analyze_wav(path)
    c = check_wav(path)
    print(f"FILE: {a.file}")
    print(f"LUFS: {a.lufs_i:.2f} (target {c.target_lufs:.2f})  pass={c.pass_lufs}")
    print(f"PEAK: {a.peak_dbfs:.2f} dBFS (limit {c.target_peak_dbfs:.2f}) pass={c.pass_peak}")
    ok = c.pass_lufs and c.pass_peak
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1
