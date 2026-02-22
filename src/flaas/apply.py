from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LoadedAction:
    track_role: str
    device: str
    param: str
    delta_db: float

def load_actions(path: str | Path = "data/actions/actions.json") -> list[LoadedAction]:
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    out: list[LoadedAction] = []
    for a in obj.get("actions", []):
        out.append(
            LoadedAction(
                track_role=a["track_role"],
                device=a["device"],
                param=a["param"],
                delta_db=float(a["delta_db"]),
            )
        )
    return out

def apply_actions_dry_run(path: str | Path = "data/actions/actions.json") -> None:
    actions = load_actions(path)
    for a in actions:
        print(f"DRY_RUN: {a.track_role} :: {a.device}.{a.param} += {a.delta_db:.2f} dB")
