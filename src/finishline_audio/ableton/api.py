from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Any

from finishline_audio.osc.rpc import OscRpc

@dataclass(frozen=True)
class AbletonApi:
    rpc: OscRpc

    def test(self) -> Tuple[Any, ...]:
        # AbletonOSC supports /live/test -> replies with "ok" when configured correctly
        return self.rpc.call("/live/test")

    def track_names(self) -> List[str]:
        # /live/song/get/track_names -> list of track name strings
        resp = self.rpc.call("/live/song/get/track_names")
        # Some OSC libs wrap strings; keep it defensive
        return [str(x) for x in resp]
