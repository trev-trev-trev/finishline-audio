from __future__ import annotations
import sys
from dataclasses import dataclass

from flaas.osc_rpc import OscTarget, request_once

@dataclass(frozen=True)
class Targets:
    master_lufs: float = -10.5
    true_peak_ceiling_dbfs: float = -1.0  # placeholder until TP estimator exists
    stem_peak_ceiling_dbfs: float = -6.0

DEFAULT_TARGETS = Targets()

# Master track constants and helpers
MASTER_TRACK_ID = -1000


def resolve_utility_device_id(target: OscTarget = OscTarget()) -> int:
    """
    Resolve Utility device ID on the master track by querying device names.
    
    Returns device index if found.
    Raises SystemExit(20) if Utility device not found.
    """
    try:
        response = request_once(
            target,
            "/live/track/get/devices/name",
            [MASTER_TRACK_ID],
            timeout_sec=3.0
        )
        # Response format: (track_id, name0, name1, name2, ...)
        # Drop the first element (track_id), keep device names
        names = list(response)[1:]
        
        for idx, name in enumerate(names):
            if str(name).strip().lower() == "utility":
                return idx
        
        # Utility not found
        print(f"ERROR: Utility device not found on master track", file=sys.stderr)
        print(f"Available devices: {names}", file=sys.stderr)
        raise SystemExit(20)
        
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: Failed to query devices on master track: {e}", file=sys.stderr)
        raise SystemExit(20)
