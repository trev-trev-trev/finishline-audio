from __future__ import annotations
from pathlib import Path
from flaas.analyze import analyze_wav
from flaas.plan import write_plan_gain_actions
from flaas.apply import apply_actions_osc

def run_loop(wav: str | Path) -> None:
    a = analyze_wav(wav)
    print(f"MEASURE: LUFS={a.lufs_i:.2f} peak_dBFS={a.peak_dbfs:.2f}")
    write_plan_gain_actions(wav)
    apply_actions_osc()
    print("DONE: planned+applied (export/verify still manual)")
