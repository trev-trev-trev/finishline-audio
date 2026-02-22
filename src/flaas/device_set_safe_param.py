from __future__ import annotations
import json
import sys
from pathlib import Path
from flaas.osc_rpc import OscTarget, request_once
from flaas.device_map import generate_device_map
from flaas.device_set_param import device_set_param
from pythonosc.udp_client import SimpleUDPClient


# Preference list for safe parameters (case-insensitive)
PREFERRED_PARAMS = [
    "wetdry", "wet", "dry", "mix", "depth", "rate", 
    "feedback", "gain", "level"
]

# Avoid these parameters
AVOID_PARAMS = [
    "device on", "on", "bypass", "enable", "mode", 
    "program", "preset"
]


def device_set_safe_param(
    track_id: int,
    device_id: int,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
) -> int:
    """
    Set a safe parameter on a plugin device, verify change, and revert.
    
    Returns:
        0 on success
        20 on read failure
        30 on write failure
    """
    # Ensure device map exists
    map_path = Path(f"data/registry/device_map_t{track_id}_d{device_id}.json")
    
    if not map_path.exists():
        print(f"Generating device map: {map_path}", file=sys.stderr)
        try:
            generate_device_map(track_id, device_id, target, timeout_sec)
        except Exception as e:
            print(f"ERROR: Failed to generate device map: {e}", file=sys.stderr)
            return 20
    
    # Load device map
    try:
        device_map = json.loads(map_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to read device map: {e}", file=sys.stderr)
        return 20
    
    params = device_map.get("params", [])
    
    # Find safe parameter by preference list
    selected_param = None
    
    for pref in PREFERRED_PARAMS:
        for param in params:
            name_lower = param["name"].lower()
            # Skip avoided params
            if any(avoid.lower() in name_lower for avoid in AVOID_PARAMS):
                continue
            
            # Check if matches preference
            if pref in name_lower:
                # Check constraints
                if param.get("is_quantized", True):
                    continue
                
                param_range = param.get("max", 1.0) - param.get("min", 0.0)
                if param_range < 0.1:
                    continue
                
                selected_param = param
                break
        
        if selected_param:
            break
    
    if not selected_param:
        print(f"ERROR: No safe parameter found for device {track_id}/{device_id}", file=sys.stderr)
        return 20
    
    param_id = selected_param["id"]
    param_name = selected_param["name"]
    param_min = selected_param["min"]
    param_max = selected_param["max"]
    param_range = param_max - param_min
    
    # Get current value
    try:
        values_before = request_once(
            target, 
            "/live/device/get/parameters/value", 
            [track_id, device_id], 
            timeout_sec=timeout_sec
        )
        idx = 2 + int(param_id)
        if idx >= len(values_before):
            print(f"ERROR: param_id {param_id} out of range", file=sys.stderr)
            return 20
        
        original_value = float(values_before[idx])
    except Exception as e:
        print(f"ERROR: Failed to read parameter value: {e}", file=sys.stderr)
        return 20
    
    # Calculate new value (2% delta, clamped)
    delta = param_range * 0.02
    new_value = original_value + delta
    new_value = max(param_min, min(param_max, new_value))
    
    # Set new value
    try:
        client = SimpleUDPClient(target.host, target.port)
        client.send_message(
            "/live/device/set/parameter/value", 
            [track_id, device_id, param_id, float(new_value)]
        )
    except Exception as e:
        print(f"ERROR: Failed to set parameter: {e}", file=sys.stderr)
        return 30
    
    # Verify change
    try:
        values_after = request_once(
            target, 
            "/live/device/get/parameters/value", 
            [track_id, device_id], 
            timeout_sec=timeout_sec
        )
        after_value = float(values_after[idx])
    except Exception as e:
        print(f"ERROR: Failed to verify parameter change: {e}", file=sys.stderr)
        return 20
    
    # Check if value actually changed
    if abs(after_value - new_value) > 0.001:
        print(f"ERROR: Value did not change as expected (expected {new_value:.6f}, got {after_value:.6f})", file=sys.stderr)
        return 30
    
    # Revert to original
    try:
        client.send_message(
            "/live/device/set/parameter/value", 
            [track_id, device_id, param_id, float(original_value)]
        )
    except Exception as e:
        print(f"ERROR: Failed to revert parameter: {e}", file=sys.stderr)
        return 30
    
    # Verify revert
    try:
        values_reverted = request_once(
            target, 
            "/live/device/get/parameters/value", 
            [track_id, device_id], 
            timeout_sec=timeout_sec
        )
        reverted_value = float(values_reverted[idx])
    except Exception as e:
        print(f"ERROR: Failed to verify revert: {e}", file=sys.stderr)
        return 20
    
    # Check if reverted correctly
    if abs(reverted_value - original_value) > 0.001:
        print(f"ERROR: Value did not revert as expected (expected {original_value:.6f}, got {reverted_value:.6f})", file=sys.stderr)
        return 30
    
    # Success - print result
    print(f"track_id={track_id} device_id={device_id} param_id={param_id} name={param_name} before={original_value:.6f} after={after_value:.6f} reverted_to={reverted_value:.6f}")
    
    return 0
