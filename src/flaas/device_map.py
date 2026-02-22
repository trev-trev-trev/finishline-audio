from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from flaas.osc_rpc import OscTarget, request_once


def generate_device_map(
    track_id: int,
    device_id: int,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
) -> str:
    """
    Generate generic device parameter map as JSON.
    
    Queries device metadata and all parameter info, writes flat structure.
    Works for any device type (Limiter, Compressor, Utility, etc.).
    
    Returns path to written JSON file.
    """
    name_resp = request_once(target, "/live/device/get/name", [track_id, device_id], timeout_sec=timeout_sec)
    class_resp = request_once(target, "/live/device/get/class_name", [track_id, device_id], timeout_sec=timeout_sec)
    num_resp = request_once(target, "/live/device/get/num_parameters", [track_id, device_id], timeout_sec=timeout_sec)
    
    device_name = str(name_resp[2])
    device_class_name = str(class_resp[2])
    num_parameters = int(num_resp[2])
    
    names_resp = request_once(target, "/live/device/get/parameters/name", [track_id, device_id], timeout_sec=timeout_sec)
    values_resp = request_once(target, "/live/device/get/parameters/value", [track_id, device_id], timeout_sec=timeout_sec)
    mins_resp = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=timeout_sec)
    maxs_resp = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=timeout_sec)
    quants_resp = request_once(target, "/live/device/get/parameters/is_quantized", [track_id, device_id], timeout_sec=timeout_sec)
    
    names = list(names_resp[2:])
    values = list(values_resp[2:])
    mins = list(mins_resp[2:])
    maxs = list(maxs_resp[2:])
    quants = list(quants_resp[2:])
    
    params = []
    for i in range(len(names)):
        params.append({
            "id": i,
            "name": str(names[i]),
            "value": float(values[i]) if i < len(values) else 0.0,
            "min": float(mins[i]) if i < len(mins) else 0.0,
            "max": float(maxs[i]) if i < len(maxs) else 1.0,
            "is_quantized": bool(quants[i]) if i < len(quants) else False,
        })
    
    payload = {
        "track_id": track_id,
        "device_id": device_id,
        "device_name": device_name,
        "device_class_name": device_class_name,
        "num_parameters": num_parameters,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "params": params,
    }
    
    out_dir = Path("data/registry")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"device_map_t{track_id}_d{device_id}.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    
    return str(out_path)
