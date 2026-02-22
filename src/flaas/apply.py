from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from pythonosc.udp_client import SimpleUDPClient

from flaas.osc_rpc import OscTarget, request_once
from flaas.param_map import get_param_range, linear_to_norm
from flaas.scan import scan_live

@dataclass(frozen=True)
class LoadedAction:
    track_role: str
    device: str
    param: str
    delta_db: float  # "linear delta" for Utility Gain (-1..+1)

UTILITY_GAIN_PARAM_ID = 9

def _read_actions_file(path: str | Path) -> tuple[str | None, list[LoadedAction]]:
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    fp = obj.get("live_fingerprint")
    actions: list[LoadedAction] = []
    for a in obj.get("actions", []):
        actions.append(
            LoadedAction(
                track_role=a["track_role"],
                device=a["device"],
                param=a["param"],
                delta_db=float(a["delta_db"]),
            )
        )
    return fp, actions

def apply_actions_dry_run(path: str | Path = "data/actions/actions.json") -> None:
    _, actions = _read_actions_file(path)
    for a in actions:
        print(f"DRY_RUN: {a.track_role} :: {a.device}.{a.param} += {a.delta_db:.2f}")

def apply_actions_osc(
    actions_path: str | Path = "data/actions/actions.json",
    target: OscTarget = OscTarget(),
    enforce_fingerprint: bool = True,
) -> None:
    """
    MVP apply: supports MASTER Utility Gain as a RELATIVE delta.
    Assumes track 0 device 0 is Utility.
    """
    expected_fp, actions = _read_actions_file(actions_path)

    if enforce_fingerprint and expected_fp:
        current_fp = scan_live(target=target).fingerprint
        if current_fp != expected_fp:
            raise RuntimeError(f"Live fingerprint mismatch: expected {expected_fp}, got {current_fp}")

    client = SimpleUDPClient(target.host, target.port)
    pr = get_param_range(0, 0, UTILITY_GAIN_PARAM_ID, target=target)

    for a in actions:
        if a.track_role == "MASTER" and a.device == "Utility" and a.param == "Gain":
            cur = request_once(target, "/live/device/get/parameter/value", [0,0,UTILITY_GAIN_PARAM_ID], timeout_sec=3.0)
            cur_norm = float(cur[3])
            cur_linear = pr.min + cur_norm * (pr.max - pr.min)

            new_linear = cur_linear + float(a.delta_db)
            new_norm = linear_to_norm(new_linear, pr)

            client.send_message("/live/device/set/parameter/value", [0, 0, UTILITY_GAIN_PARAM_ID, float(new_norm)])
            print(f"APPLIED: Utility.Gain {cur_linear:.3f} -> {new_linear:.3f} (norm {cur_norm:.3f}->{new_norm:.3f})")
        else:
            print(f"SKIP: unsupported action {a}")
