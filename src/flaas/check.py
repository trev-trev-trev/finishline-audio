from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from flaas.analyze import analyze_wav
from flaas.targets import Targets, DEFAULT_TARGETS

@dataclass
class CheckResult:
    file: str
    pass_lufs: bool
    pass_peak: bool
    lufs_i: float
    peak_dbfs: float
    target_lufs: float
    target_peak_dbfs: float

def check_wav(path: str | Path, targets: Targets = DEFAULT_TARGETS) -> CheckResult:
    a = analyze_wav(path)
    pass_lufs = abs(a.lufs_i - targets.master_lufs) <= 0.5
    pass_peak = a.peak_dbfs <= targets.stem_peak_ceiling_dbfs
    return CheckResult(
        file=a.file,
        pass_lufs=pass_lufs,
        pass_peak=pass_peak,
        lufs_i=a.lufs_i,
        peak_dbfs=a.peak_dbfs,
        target_lufs=targets.master_lufs,
        target_peak_dbfs=targets.stem_peak_ceiling_dbfs,
    )

def write_check(path_in: str | Path, path_out: str | Path = "data/reports/check.json") -> Path:
    out = Path(path_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res = check_wav(path_in)
    out.write_text(json.dumps(asdict(res), indent=2) + "\n", encoding="utf-8")
    return out
