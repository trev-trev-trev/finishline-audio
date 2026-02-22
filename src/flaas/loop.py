from __future__ import annotations
from pathlib import Path

from flaas.analyze import analyze_wav
from flaas.plan import write_plan_gain_actions
from flaas.apply import apply_actions_osc, apply_actions_dry_run
from flaas.verify import verify_master_utility_gain

def run_loop(wav: str | Path, dry: bool = False) -> None:
    cur_norm = verify_master_utility_gain()
    if cur_norm >= 0.99:
        print(f"STOP: utility gain already near max (norm={cur_norm:.3f})")
        return

    a = analyze_wav(wav)
    print(f"MEASURE: LUFS={a.lufs_i:.2f} peak_dBFS={a.peak_dbfs:.2f}")
    write_plan_gain_actions(wav)

    if dry:
        apply_actions_dry_run()
        print("DONE: planned (dry-run, no OSC)")
        return

    apply_actions_osc()
    new_norm = verify_master_utility_gain()
    print(f"DONE: planned+applied (norm={new_norm:.3f})")
