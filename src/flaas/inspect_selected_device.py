from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once


def inspect_selected_device(
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
    raw: bool = False,
) -> None:
    """
    Print full parameter table for the currently selected device in Ableton.
    
    Queries:
    - /live/view/get/selected_device → (track_id, device_id)
    - /live/device/get/parameters/{name,value,min,max,is_quantized}
    
    Outputs formatted table or raw tuples if raw=True.
    """
    # Get selected device
    sel = request_once(target, "/live/view/get/selected_device", [], timeout_sec=timeout_sec)
    track_id, device_id = int(sel[0]), int(sel[1])
    
    if raw:
        print(f"selected_device: {sel}")
    
    # Query all parameter info
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
    
    # Parse (skip first 2 items: track_id, device_id)
    param_names = names[2:]
    param_values = values[2:]
    param_mins = mins[2:]
    param_maxs = maxs[2:]
    param_quants = quants[2:]
    
    # Print formatted table
    print(f"track_id={track_id} device_id={device_id}")
    print()
    
    num_params = len(param_names)
    for i in range(num_params):
        name = param_names[i] if i < len(param_names) else "?"
        val = param_values[i] if i < len(param_values) else "?"
        pmin = param_mins[i] if i < len(param_mins) else "?"
        pmax = param_maxs[i] if i < len(param_maxs) else "?"
        quant = param_quants[i] if i < len(param_quants) else "?"
        
        print(f"{i:2d}  {str(name):30s}  val={val!s:8s}  min={pmin!s:8s}  max={pmax!s:8s}  quant={quant!s}")
