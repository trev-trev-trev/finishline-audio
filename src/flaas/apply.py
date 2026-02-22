from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from pythonosc.udp_client import SimpleUDPClient

from flaas.osc_rpc import OscTarget
from flaas.param_map import get_param_range, linear_to_norm

@dataclass(frozen=True)
class LoadedAction:
    track_role: str
    device: str
    param: str
    delta_db: float  # currently used as "linear delta" for Utility Gain (-1..+1) until dB mapping exists

UTILITY_GAIN_PARAM_ID = 9

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
    for a in load_actions(path):
        print(f"DRY_RUN: {a.track_role} :: {a.device}.{a.param} += {a.delta_db:.2f}")

def apply_actions_osc(
    actions_path: str | Path = "data/actions/actions.json",
    target: OscTarget = OscTarget(),
) -> None:
    """
    MVP apply: supports MASTER Utility Gain by mapping delta into Utility Gain param on track 0 device 0.
    Assumes:
      - track 0 is PREMASTER/MASTER track role
      - device 0 is Utility
    """
    client = SimpleUDPClient(target.host, target.port)

    for a in load_actions(actions_path):
        if a.track_role == "MASTER" and a.device == "Utility" and a.param == "Gain":
            # interpret delta_db as "linear gain delta" for now.
            # get current normalized value
            # We can't reliably read current value without extra calls, so we set absolute based on desired delta from 0.0 baseline:
            # For now: set to midpoint + delta mapped into [-1,1] range.
            pr = get_param_range(0, 0, UTILITY_GAIN_PARAM_ID, target=target)
            # delta_db will be treated as linear value in [-1,1] then mapped.
            n = linear_to_norm(a.delta_db, pr)
            client.send_message("/live/device/set/parameter/value", [0, 0, UTILITY_GAIN_PARAM_ID, float(n)])
            print(f"APPLIED: track0 device0 Utility.Gain <= linear {a.delta_db:.2f} (norm {n:.3f})")
        else:
            print(f"SKIP: unsupported action {a}")
