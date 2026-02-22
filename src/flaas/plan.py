from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from flaas.analyze import analyze_wav
from flaas.targets import Targets, DEFAULT_TARGETS
from flaas.actions import GainAction, write_actions

@dataclass(frozen=True)
class PlanGainResult:
    delta_linear: float
    lufs_i: float
    target_lufs: float
    clamped: bool

def plan_utility_gain_linear_for_master(path: str | Path, targets: Targets = DEFAULT_TARGETS, clamp_linear: float = 1.0) -> PlanGainResult:
    """
    Temporary MVP model:
      - compute LUFS error in dB
      - map dB error to a linear control in [-1, +1] by dividing by 12 (rough), then clamp
    """
    a = analyze_wav(path)
    err_db = targets.master_lufs - a.lufs_i
    raw = err_db / 12.0  # rough scale: 12 dB -> full-scale control move
    delta = raw
    if delta > clamp_linear:
        delta = clamp_linear
    if delta < -clamp_linear:
        delta = -clamp_linear
    clamped = (delta != raw)
    return PlanGainResult(delta_linear=float(delta), lufs_i=float(a.lufs_i), target_lufs=float(targets.master_lufs), clamped=clamped)

def write_plan_gain_actions(path: str | Path, out_actions: str | Path = "data/actions/actions.json") -> Path:
    r = plan_utility_gain_linear_for_master(path)
    actions = [
        GainAction(
            track_role="MASTER",
            device="Utility",
            param="Gain",
            delta_db=r.delta_linear,  # stored in delta_db field for now (legacy)
        )
    ]
    out = write_actions(actions, out_actions)
    if r.clamped:
        print(f"WARNING: gain plan clamped to {r.delta_linear:.3f} (raw would exceed clamp).")
    return out
