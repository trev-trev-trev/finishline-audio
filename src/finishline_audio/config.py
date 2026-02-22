from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class AbletonConfig:
    host: str = "127.0.0.1"
    port_in: int = 11000   # AbletonOSC listens here
    port_out: int = 11001  # AbletonOSC replies here
    timeout_s: float = 1.0
    retries: int = 2

@dataclass(frozen=True)
class AppConfig:
    ableton: AbletonConfig

def load_config(path: str | Path = "config.yaml") -> AppConfig:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    a = (data.get("ableton") or {})
    ableton = AbletonConfig(
        host=str(a.get("host", "127.0.0.1")),
        port_in=int(a.get("port_in", 11000)),
        port_out=int(a.get("port_out", 11001)),
        timeout_s=float(a.get("timeout_s", 1.0)),
        retries=int(a.get("retries", 2)),
    )
    return AppConfig(ableton=ableton)
