from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone

@dataclass
class ScanResult:
    ok: bool
    note: str
    created_at_utc: str

def write_model_cache(path: str | Path = "data/caches/model_cache.json") -> Path:
    """
    MVP stub: writes a placeholder cache file.
    Real implementation will query AbletonOSC for tracks/devices/params.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = ScanResult(
        ok=True,
        note="stub scan (no Ableton query yet)",
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    out.write_text(json.dumps(asdict(payload), indent=2) + "\n", encoding="utf-8")
    return out
