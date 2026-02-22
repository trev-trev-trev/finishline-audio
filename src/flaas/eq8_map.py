from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from flaas.osc_rpc import OscTarget, request_once


def generate_eq8_map(
    track_id: int,
    device_id: int,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
) -> str:
    """
    Generate structured EQ Eight parameter map as JSON.
    
    Queries all parameter metadata and builds hierarchical map:
    - Flat params list (id, name, min, max, is_quantized)
    - Grouped structure (global params + 8 bands × 2 sides × 5 controls)
    
    Returns path to written JSON file.
    """
    names_resp = request_once(target, "/live/device/get/parameters/name", [track_id, device_id], timeout_sec=timeout_sec)
    mins_resp = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=timeout_sec)
    maxs_resp = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=timeout_sec)
    quants_resp = request_once(target, "/live/device/get/parameters/is_quantized", [track_id, device_id], timeout_sec=timeout_sec)
    
    names = list(names_resp[2:])
    mins = list(mins_resp[2:])
    maxs = list(maxs_resp[2:])
    quants = list(quants_resp[2:])
    
    params = []
    for i in range(len(names)):
        params.append({
            "id": i,
            "name": str(names[i]),
            "min": float(mins[i]) if i < len(mins) else 0.0,
            "max": float(maxs[i]) if i < len(maxs) else 1.0,
            "is_quantized": bool(quants[i]) if i < len(quants) else False,
        })
    
    groups = _build_groups(params)
    
    payload = {
        "track_id": track_id,
        "device_id": device_id,
        "device_class_expected": "Eq8",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "params": params,
        "groups": groups,
    }
    
    out_dir = Path("data/registry")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"eq8_map_t{track_id}_d{device_id}.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    
    return str(out_path)


def _build_groups(params: list[dict]) -> dict:
    """
    Parse EQ Eight parameter names and build hierarchical groups.
    
    Expected names:
    - Global: "Device On", "Output Gain", "Scale", "Adaptive Q"
    - Bands: "<N> Filter On <A|B>", "<N> Filter Type <A|B>", "<N> Frequency <A|B>",
             "<N> Gain <A|B>", "<N> Resonance <A|B>" where N in 1..8
    """
    name_to_id = {p["name"]: p["id"] for p in params}
    
    global_params = {}
    if "Device On" in name_to_id:
        global_params["device_on"] = name_to_id["Device On"]
    if "Output Gain" in name_to_id:
        global_params["output_gain"] = name_to_id["Output Gain"]
    if "Scale" in name_to_id:
        global_params["scale"] = name_to_id["Scale"]
    if "Adaptive Q" in name_to_id:
        global_params["adaptive_q"] = name_to_id["Adaptive Q"]
    
    bands = {}
    for band_num in range(1, 9):
        band_data = {}
        for side in ["A", "B"]:
            side_data = {}
            
            on_key = f"{band_num} Filter On {side}"
            type_key = f"{band_num} Filter Type {side}"
            freq_key = f"{band_num} Frequency {side}"
            gain_key = f"{band_num} Gain {side}"
            res_key = f"{band_num} Resonance {side}"
            
            if on_key in name_to_id:
                side_data["on"] = name_to_id[on_key]
            if type_key in name_to_id:
                side_data["type"] = name_to_id[type_key]
            if freq_key in name_to_id:
                side_data["freq"] = name_to_id[freq_key]
            if gain_key in name_to_id:
                side_data["gain"] = name_to_id[gain_key]
            if res_key in name_to_id:
                side_data["res"] = name_to_id[res_key]
            
            band_data[side] = side_data
        
        bands[str(band_num)] = band_data
    
    expected_count = 4 + (8 * 2 * 5)
    missing = []
    if len(name_to_id) < expected_count:
        all_expected = set()
        all_expected.add("Device On")
        all_expected.add("Output Gain")
        all_expected.add("Scale")
        all_expected.add("Adaptive Q")
        for band_num in range(1, 9):
            for side in ["A", "B"]:
                all_expected.add(f"{band_num} Filter On {side}")
                all_expected.add(f"{band_num} Filter Type {side}")
                all_expected.add(f"{band_num} Frequency {side}")
                all_expected.add(f"{band_num} Gain {side}")
                all_expected.add(f"{band_num} Resonance {side}")
        missing = sorted(list(all_expected - set(name_to_id.keys())))
    
    return {
        "global": global_params,
        "bands": bands,
        "missing": missing,
    }
