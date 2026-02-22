from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once


def device_param_info(
    track_id: int,
    device_id: int,
    param_id: int,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
    raw: bool = False,
) -> None:
    """
    Print full metadata for a single parameter on a device.
    
    Queries:
    - /live/device/get/parameters/name → (track_id, device_id, name0, name1, ...)
    - /live/device/get/parameters/value → (track_id, device_id, val0, val1, ...)
    - /live/device/get/parameters/min → (track_id, device_id, min0, min1, ...)
    - /live/device/get/parameters/max → (track_id, device_id, max0, max1, ...)
    - /live/device/get/parameters/is_quantized → (track_id, device_id, q0, q1, ...)
    
    Outputs single line with all metadata or raw tuples if raw=True.
    """
    names = request_once(target, "/live/device/get/parameters/name", [track_id, device_id], timeout_sec=timeout_sec)
    values = request_once(target, "/live/device/get/parameters/value", [track_id, device_id], timeout_sec=timeout_sec)
    mins = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=timeout_sec)
    maxs = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=timeout_sec)
    quants = request_once(target, "/live/device/get/parameters/is_quantized", [track_id, device_id], timeout_sec=timeout_sec)
    
    if raw:
        print(f"names: {names}")
        print(f"values: {values}")
        print(f"mins: {mins}")
        print(f"maxs: {maxs}")
        print(f"is_quantized: {quants}")
        return
    
    param_names = list(names[2:])
    param_values = list(values[2:])
    param_mins = list(mins[2:])
    param_maxs = list(maxs[2:])
    param_quants = list(quants[2:])
    
    if param_id >= len(param_names):
        raise IndexError(f"param_id {param_id} out of range (device has {len(param_names)} params)")
    
    name = param_names[param_id]
    val = param_values[param_id]
    pmin = param_mins[param_id]
    pmax = param_maxs[param_id]
    quant = param_quants[param_id]
    
    print(f'track_id={track_id} device_id={device_id} param_id={param_id} name="{name}" val={val} min={pmin} max={pmax} quant={quant}')
