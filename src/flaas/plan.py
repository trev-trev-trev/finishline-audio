from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from flaas.analyze import analyze_wav
from flaas.targets import Targets, DEFAULT_TARGETS
from flaas.actions import GainAction, write_actions

@dataclass(frozen=True)
class PlanGainResult:
    delta_db: float
    lufs_i: float
    target_lufs: float

def plan_utility_gain_for_master(path: str | Path, targets: Targets = DEFAULT_TARGETS, clamp_db: float = 6.0) -> PlanGainResult:
    """
    Compute Utility gain adjustment to hit target LUFS (rough first-order model).
    delta_db ~= target - measured
    """
    a = analyze_wav(path)
    delta = targets.master_lufs - a.lufs_i
    if delta > clamp_db:
        delta = clamp_db
    if delta < -clamp_db:
        delta = -clamp_db
    return PlanGainResult(delta_db=float(delta), lufs_i=float(a.lufs_i), target_lufs=float(targets.master_lufs))

def write_plan_gain_actions(path: str | Path, out_actions: str | Path = "data/actions/actions.json") -> Path:
    r = plan_utility_gain_for_master(path)
    actions = [
        GainAction(
            track_role="MASTER",
            device="Utility",
            param="Gain",
            delta_db=r.delta_db,
        )
    ]
    return write_actions(actions, out_actions)
