from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone

@dataclass
class GainAction:
    track_role: str
    device: str
    param: str
    delta_db: float

@dataclass
class ActionsFile:
    created_at_utc: str
    actions: list[GainAction]

def write_actions(actions: list[GainAction], path_out: str | Path = "data/actions/actions.json") -> Path:
    out = Path(path_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = ActionsFile(
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        actions=actions,
    )
    out.write_text(json.dumps(asdict(payload), indent=2) + "\n", encoding="utf-8")
    return out
