from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once
from pythonosc.udp_client import SimpleUDPClient


def device_set_param(
    track_id: int,
    device_id: int,
    param_id: int,
    value: float,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
    dry: bool = False,
) -> None:
    """
    Set any parameter on any device (generic version).
    
    Uses:
    - /live/device/get/parameters/value → (track_id, device_id, val0, val1, ...)
    - /live/device/set/parameter/value → sends [track_id, device_id, param_id, value]
    
    Prints: track_id=<t> device_id=<d> param_id=<id> before=<b> after=<a>
    """
    values_before = request_once(target, "/live/device/get/parameters/value", [track_id, device_id], timeout_sec=timeout_sec)
    
    idx = 2 + int(param_id)
    if idx >= len(values_before):
        raise IndexError(f"param_id {param_id} out of range (device has {len(values_before)-2} params)")
    
    before = float(values_before[idx])
    
    if dry:
        print(f"DRY_RUN: track_id={track_id} device_id={device_id} param_id={param_id} before={before:.6f} -> would_set={value:.6f}")
        return
    
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, param_id, float(value)])
    
    values_after = request_once(target, "/live/device/get/parameters/value", [track_id, device_id], timeout_sec=timeout_sec)
    after = float(values_after[idx])
    
    print(f"track_id={track_id} device_id={device_id} param_id={param_id} before={before:.6f} after={after:.6f}")
