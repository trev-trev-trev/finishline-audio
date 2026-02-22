from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pythonosc.udp_client import SimpleUDPClient
from flaas.osc_rpc import OscTarget

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
    for a in load_actions(path):
        print(f"DRY_RUN: {a.track_role} :: {a.device}.{a.param} += {a.delta_db:.2f} dB")

def _send(client: SimpleUDPClient, address: str, *args: Any) -> None:
    client.send_message(address, list(args) if len(args) != 1 else args[0])

def apply_actions_osc(
    actions_path: str | Path = "data/actions/actions.json",
    target: OscTarget = OscTarget(),
) -> None:
    """
    MVP apply: supports ONLY MASTER Utility Gain via AbletonOSC direct endpoint.
    Requires AbletonOSC loaded and listening on target.port (default 11000).
    """
    client = SimpleUDPClient(target.host, target.port)

    for a in load_actions(actions_path):
        if a.track_role == "MASTER" and a.device == "Utility" and a.param == "Gain":
            # AbletonOSC: /live/master/track/gain <float_db>
            _send(client, "/live/master/track/gain", a.delta_db)
            print(f"APPLIED: MASTER Utility Gain += {a.delta_db:.2f} dB")
        else:
            print(f"SKIP: unsupported action {a}")
