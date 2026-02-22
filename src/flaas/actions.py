from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

@dataclass
class GainAction:
    track_role: str
    device: str
    param: str
    delta_db: float

@dataclass
class ActionsFile:
    schema_version: str
    created_at_utc: str
    live_fingerprint: Optional[str]
    actions: list[GainAction]

def write_actions(
    actions: list[GainAction],
    path_out: str | Path = "data/actions/actions.json",
    live_fingerprint: str | None = None,
    schema_version: str = "1.0",
) -> Path:
    out = Path(path_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = ActionsFile(
        schema_version=schema_version,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        live_fingerprint=live_fingerprint,
        actions=actions,
    )
    out.write_text(json.dumps(asdict(payload), indent=2) + "\n", encoding="utf-8")
    return out
