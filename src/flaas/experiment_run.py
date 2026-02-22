from __future__ import annotations
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from flaas.osc_rpc import OscTarget, request_once
from flaas.analyze import analyze_wav
from flaas.check import check_wav
from flaas.targets import DEFAULT_TARGETS


@dataclass
class ExperimentConfig:
    """Single experiment configuration."""
    id: str
    export_file: str
    glue: dict[str, float]
    limiter: dict[str, float]


@dataclass
class DeviceInfo:
    """Resolved device information."""
    device_id: int
    params: dict[str, dict]  # param_name -> {id, min, max, is_quantized}


def resolve_device_id_by_name(
    track_id: int,
    device_name: str,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 3.0,
) -> int:
    """
    Resolve device ID by name on a track.
    
    Returns device index if found.
    Raises SystemExit(20) if device not found.
    """
    try:
        response = request_once(
            target,
            "/live/track/get/devices/name",
            [track_id],
            timeout_sec=timeout_sec
        )
        names = list(response)[1:]  # Drop track_id
        
        for idx, name in enumerate(names):
            if str(name).strip().lower() == device_name.strip().lower():
                return idx
        
        print(f"ERROR: Device '{device_name}' not found on track {track_id}")
        print(f"Available devices: {names}")
        raise SystemExit(20)
        
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: Failed to query devices on track {track_id}: {e}")
        raise SystemExit(20)


def resolve_device_params(
    track_id: int,
    device_id: int,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 3.0,
) -> dict[str, dict]:
    """
    Resolve all parameter info for a device.
    
    Returns dict: param_name -> {id, min, max, is_quantized}
    """
    try:
        names_resp = request_once(target, "/live/device/get/parameters/name", [track_id, device_id], timeout_sec=timeout_sec)
        mins_resp = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=timeout_sec)
        maxs_resp = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=timeout_sec)
        quants_resp = request_once(target, "/live/device/get/parameters/is_quantized", [track_id, device_id], timeout_sec=timeout_sec)
        
        names = list(names_resp[2:])
        mins = list(mins_resp[2:])
        maxs = list(maxs_resp[2:])
        quants = list(quants_resp[2:])
        
        params = {}
        for i in range(len(names)):
            param_name = str(names[i])
            params[param_name] = {
                "id": i,
                "min": float(mins[i]) if i < len(mins) else 0.0,
                "max": float(maxs[i]) if i < len(maxs) else 1.0,
                "is_quantized": bool(quants[i]) if i < len(quants) else False,
            }
        
        return params
        
    except Exception as e:
        print(f"ERROR: Failed to query device params (track={track_id}, device={device_id}): {e}")
        raise SystemExit(20)


def set_device_param_by_name(
    track_id: int,
    device_id: int,
    param_name: str,
    value: float,
    param_info: dict,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 3.0,
) -> None:
    """
    Set device parameter by name.
    
    Converts value to normalized [0,1] and sends via OSC.
    """
    param_id = param_info["id"]
    min_val = param_info["min"]
    max_val = param_info["max"]
    
    # Convert to normalized [0,1]
    norm_value = (value - min_val) / (max_val - min_val)
    norm_value = max(0.0, min(1.0, norm_value))  # Clamp
    
    try:
        request_once(
            target,
            "/live/device/set/parameter/value",
            [track_id, device_id, param_id, norm_value],
            timeout_sec=timeout_sec
        )
    except Exception as e:
        print(f"ERROR: Failed to set param {param_name} (track={track_id}, device={device_id}, param_id={param_id}, value={value}): {e}")
        raise SystemExit(30)


def set_master_fader(
    track_id: int,
    linear_value: float,
    target: OscTarget = OscTarget(),
    timeout_sec: float = 3.0,
) -> None:
    """
    Set track volume (master fader).
    
    Value is linear (0.0-1.0, where 0.85 ≈ 0.0 dB).
    """
    try:
        request_once(
            target,
            "/live/track/set/volume",
            [track_id, linear_value],
            timeout_sec=timeout_sec
        )
    except Exception as e:
        print(f"ERROR: Failed to set master fader: {e}")
        print(f"FALLBACK: Manually set Master fader to 0.0 dB in Ableton")


def wait_for_file(path: Path, timeout_sec: float = 30.0) -> bool:
    """
    Wait for file to appear and size to stabilize.
    
    Returns True if file is ready, False if timeout.
    """
    start = time.time()
    last_size = -1
    stable_count = 0
    
    while time.time() - start < timeout_sec:
        if not path.exists():
            time.sleep(0.5)
            continue
        
        current_size = path.stat().st_size
        if current_size == last_size and current_size > 0:
            stable_count += 1
            if stable_count >= 3:  # 3 consecutive stable checks
                return True
        else:
            stable_count = 0
            last_size = current_size
        
        time.sleep(0.5)
    
    return False


def compute_sha256(path: Path) -> str:
    """Compute SHA256 hash of file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def experiment_run(
    config_path: str | Path,
    target: OscTarget = OscTarget(),
) -> int:
    """
    Run batch experiment from config file.
    
    For each experiment:
    1. Set parameters via OSC
    2. Pause for manual export
    3. Verify audio
    4. Log results to JSONL
    
    Returns 0 on success, 20 on read failure, 30 on write failure.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return 20
    
    try:
        config_data = json.loads(config_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: Failed to parse config: {e}")
        return 20
    
    # Extract config
    master_track_id = config_data.get("master_track_id", -1000)
    device_names = config_data.get("device_names", {})
    glue_name = device_names.get("glue", "Glue Compressor")
    limiter_name = device_names.get("limiter", "Limiter")
    runs = config_data.get("runs", [])
    
    if not runs:
        print("ERROR: No runs defined in config")
        return 20
    
    # Resolve device IDs
    print(f"Resolving devices on track {master_track_id}...")
    glue_device_id = resolve_device_id_by_name(master_track_id, glue_name, target)
    limiter_device_id = resolve_device_id_by_name(master_track_id, limiter_name, target)
    print(f"  Glue Compressor: device {glue_device_id}")
    print(f"  Limiter: device {limiter_device_id}")
    
    # Resolve parameters
    print(f"Resolving Glue Compressor parameters...")
    glue_params = resolve_device_params(master_track_id, glue_device_id, target)
    print(f"  Found {len(glue_params)} params")
    
    print(f"Resolving Limiter parameters...")
    limiter_params = resolve_device_params(master_track_id, limiter_device_id, target)
    print(f"  Found {len(limiter_params)} params")
    
    # Set master fader to 0.0 dB (0.85 linear)
    print(f"Setting master fader to 0.0 dB...")
    try:
        set_master_fader(master_track_id, 0.85, target)
        print(f"  ✓ Master fader set to 0.0 dB")
    except SystemExit:
        print(f"  ⚠ OSC failed - Manually set Master fader to 0.0 dB")
        input("Press Enter when ready...")
    
    # Prepare output log
    log_path = Path("output/experiments.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run experiments
    success_count = 0
    for idx, run in enumerate(runs, 1):
        exp_id = run.get("id", f"exp{idx}")
        export_file = run.get("export_file", f"output/exp_{exp_id}.wav")
        glue_settings = run.get("glue", {})
        limiter_settings = run.get("limiter", {})
        
        print(f"\n{'='*70}")
        print(f"EXPERIMENT {idx}/{len(runs)}: {exp_id}")
        print(f"{'='*70}")
        
        # Set Glue Compressor params
        print(f"\nSetting Glue Compressor...")
        for param_name, value in glue_settings.items():
            key = param_name
            if key not in glue_params:
                # Try variations (threshold_db -> Threshold, etc.)
                key_lower = key.replace("_db", "").replace("_", " ").lower()
                found = None
                for pname in glue_params.keys():
                    if pname.lower().replace(" ", "") == key_lower.replace(" ", ""):
                        found = pname
                        break
                if not found:
                    print(f"  ⚠ Param '{param_name}' not found, skipping")
                    continue
                key = found
            
            print(f"  Setting {key} = {value}")
            set_device_param_by_name(
                master_track_id,
                glue_device_id,
                key,
                value,
                glue_params[key],
                target
            )
            print(f"    ✓ {key} set")
        
        # Set Limiter params
        print(f"\nSetting Limiter...")
        for param_name, value in limiter_settings.items():
            key = param_name
            if key not in limiter_params:
                # Try variations (ceiling_db -> Ceiling, gain_db -> Gain)
                key_lower = key.replace("_db", "").replace("_", " ").lower()
                found = None
                for pname in limiter_params.keys():
                    if pname.lower().replace(" ", "") == key_lower.replace(" ", ""):
                        found = pname
                        break
                if not found:
                    print(f"  ⚠ Param '{param_name}' not found, skipping")
                    continue
                key = found
            
            print(f"  Setting {key} = {value}")
            set_device_param_by_name(
                master_track_id,
                limiter_device_id,
                key,
                value,
                limiter_params[key],
                target
            )
            print(f"    ✓ {key} set")
        
        # Pause for manual export
        print(f"\n{'─'*70}")
        print(f"📤 EXPORT NOW:")
        print(f"   File → Export Audio/Video")
        print(f"   Rendered Track = Master")
        print(f"   Normalize = OFF")
        print(f"   Filename: {export_file}")
        print(f"{'─'*70}")
        input("Press Enter after export completes...")
        
        # Wait for file to stabilize
        export_path = Path(export_file)
        print(f"\nWaiting for {export_path.name} to stabilize...")
        if not wait_for_file(export_path, timeout_sec=30.0):
            print(f"  ✗ File did not appear or stabilize within 30s")
            print(f"  Skipping verification for {exp_id}")
            continue
        print(f"  ✓ File ready")
        
        # Verify audio
        print(f"\nVerifying {export_path.name}...")
        try:
            analysis = analyze_wav(export_path)
            check = check_wav(export_path, DEFAULT_TARGETS)
            
            print(f"  LUFS: {analysis.lufs_i:.2f} (target {check.target_lufs:.2f}) pass={check.pass_lufs}")
            print(f"  PEAK: {analysis.peak_dbfs:.2f} dBFS (limit {check.target_peak_dbfs:.2f}) pass={check.pass_peak}")
            
            # Compute SHA256
            sha256 = compute_sha256(export_path)
            
            # Log to JSONL
            log_entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "id": exp_id,
                "export_file": export_file,
                "sha256": sha256,
                "params": {
                    "master_fader_db": 0.0,
                    "glue": glue_settings,
                    "limiter": limiter_settings,
                },
                "results": {
                    "lufs_i": analysis.lufs_i,
                    "peak_dbfs": analysis.peak_dbfs,
                    "pass_lufs": check.pass_lufs,
                    "pass_peak": check.pass_peak,
                }
            }
            
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            print(f"  ✓ Logged to {log_path}")
            
            # Check success
            if check.pass_lufs and check.pass_peak:
                print(f"\n{'='*70}")
                print(f"✅ SUCCESS: Targets hit!")
                print(f"   LUFS: {analysis.lufs_i:.2f} (target {check.target_lufs:.2f})")
                print(f"   PEAK: {analysis.peak_dbfs:.2f} (limit {check.target_peak_dbfs:.2f})")
                print(f"{'='*70}")
                success_count += 1
                return 0  # Early exit on success
            
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Verification failed: {e}")
            continue
    
    # All experiments complete
    print(f"\n{'='*70}")
    print(f"BATCH COMPLETE: {success_count}/{len(runs)} experiments verified")
    if success_count > 0:
        print(f"Results logged to: {log_path}")
    print(f"{'='*70}")
    
    return 0
