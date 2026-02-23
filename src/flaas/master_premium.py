"""
Premium master chain optimization (Waves C6/SSL/L3 + stock Utility/Saturator).

Target chain (device order):
  [0] Utility
  [1] EQ Eight
  [2] Waves C6 Stereo (multiband compression)
  [3] Waves F6 Stereo (static preset - not automated)
  [4] Waves SSLComp Stereo (glue compression)
  [5] Saturator (RMS boost)
  [6] Waves L3 UltraMaximizer Stereo (final limiting)

Strategy:
- Start aggressive, iterate to target LUFS/True Peak
- Use C6 for multiband leveling (tame bass buildup, presence boost)
- Use SSLComp for glue (2-4 dB GR)
- Use Saturator for harmonic RMS boost
- Use L3 for transparent limiting to -1.0 dBTP
- Diminishing returns detection (stop if LUFS improvement < 0.2 LU)
"""

from __future__ import annotations
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from flaas.osc_rpc import OscTarget, request_once
from flaas.analyze import analyze_wav
from flaas.targets import MASTER_TRACK_ID
from flaas.preflight import run_preflight_checks
from pythonosc.udp_client import SimpleUDPClient

if sys.platform == "darwin":
    from flaas.ui_export_macos import auto_export_wav


def resolve_device_id_by_name(track_id: int, device_name: str, target: OscTarget = OscTarget()) -> int:
    """Resolve device ID by name (case-insensitive, partial match)."""
    response = request_once(target, "/live/track/get/devices/name", [track_id], timeout_sec=3.0)
    names = list(response)[1:]
    
    search_lower = device_name.strip().lower()
    for idx, name in enumerate(names):
        if search_lower in str(name).strip().lower():
            return idx
    
    raise RuntimeError(f"Device '{device_name}' not found on track {track_id}. Available: {names}")


def resolve_device_params(track_id: int, device_id: int, target: OscTarget = OscTarget()) -> dict[str, dict]:
    """Resolve all parameter info for a device."""
    names_resp = request_once(target, "/live/device/get/parameters/name", [track_id, device_id], timeout_sec=3.0)
    mins_resp = request_once(target, "/live/device/get/parameters/min", [track_id, device_id], timeout_sec=3.0)
    maxs_resp = request_once(target, "/live/device/get/parameters/max", [track_id, device_id], timeout_sec=3.0)
    
    names = list(names_resp[2:])
    mins = list(mins_resp[2:])
    maxs = list(maxs_resp[2:])
    
    params = {}
    for i in range(len(names)):
        param_name = str(names[i])
        params[param_name] = {
            "id": i,
            "min": float(mins[i]) if i < len(mins) else 0.0,
            "max": float(maxs[i]) if i < len(maxs) else 1.0,
        }
    
    return params


def set_param_normalized(track_id: int, device_id: int, param_id: int, norm_value: float, target: OscTarget) -> None:
    """Set parameter with normalized value [0, 1]."""
    norm_value = max(0.0, min(1.0, norm_value))
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, param_id, norm_value])


def db_to_normalized(db_value: float, min_db: float, max_db: float) -> float:
    """Convert dB to normalized [0, 1]."""
    return (db_value - min_db) / (max_db - min_db)


def compute_sha256(path: Path) -> str:
    """Compute SHA256 hash."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def master_premium(
    target: OscTarget = OscTarget(),
    auto_export_enabled: bool = True,
    mode: str = "loud_preview",  # streaming_safe | loud_preview | headroom
    skip_prompts: bool = False,
) -> int:
    """
    Generate premium master using Waves C6/SSL/L3 + stock Utility/Saturator.
    
    Modes:
    - streaming_safe: -14 LUFS, -1 dBTP (official streaming spec)
    - loud_preview: -9 LUFS, -1 dBTP (competitive commercial)
    - headroom: -6 dBFS sample peak (internal safety)
    
    Expected chain order:
      [0] Utility
      [1] EQ Eight
      [2] Waves C6 Stereo
      [3] Waves F6 Stereo (static preset, not automated)
      [4] Waves SSLComp Stereo
      [5] Saturator
      [6] Waves L3 UltraMaximizer Stereo
    """
    
    # Mode configs
    mode_configs = {
        "streaming_safe": {"target_lufs": -14.0, "true_peak_limit": -1.0},
        "loud_preview": {"target_lufs": -9.0, "true_peak_limit": -1.0},
        "headroom": {"target_lufs": -10.0, "true_peak_limit": -2.0},
    }
    
    if mode not in mode_configs:
        print(f"❌ Invalid mode: {mode}. Choose: streaming_safe, loud_preview, headroom")
        return 1
    
    cfg = mode_configs[mode]
    target_lufs = cfg["target_lufs"]
    true_peak_limit = cfg["true_peak_limit"]
    
    print("=" * 70)
    print("PREMIUM MASTER OPTIMIZATION (Stand Tall)")
    print("=" * 70)
    print(f"\nMode: {mode}")
    print(f"Target: {target_lufs:.1f} LUFS, {true_peak_limit:.1f} dBTP")
    print(f"\nExpected chain: Utility → EQ → C6 → F6 → SSL → Saturator → L3\n")
    
    # Pre-flight checks
    print("=" * 70)
    print("PRE-FLIGHT CHECKS")
    print("=" * 70)
    print()
    
    # Check 1: Master fader (will prompt user if OSC fails)
    expected_order = ["Utility", "EQ Eight", "C6", "F6", "SSL", "Saturator", "L3"]
    if not run_preflight_checks(MASTER_TRACK_ID, target, expected_chain=expected_order, skip_prompts=skip_prompts):
        print("\n❌ Pre-flight checks failed. Fix issues and re-run.")
        return 1
    
    print("\n✅ Pre-flight checks passed - starting optimization...\n")
    
    # Resolve devices
    tid = MASTER_TRACK_ID
    try:
        utility_id = resolve_device_id_by_name(tid, "Utility", target)
        c6_id = resolve_device_id_by_name(tid, "C6", target)
        ssl_id = resolve_device_id_by_name(tid, "SSL", target)
        saturator_id = resolve_device_id_by_name(tid, "Saturator", target)
        l3_id = resolve_device_id_by_name(tid, "L3", target)
        
        print(f"✓ Resolved devices: Utility={utility_id}, C6={c6_id}, SSL={ssl_id}, Saturator={saturator_id}, L3={l3_id}\n")
    except Exception as e:
        print(f"❌ Device resolution failed: {e}")
        return 1
    
    # Get parameter info
    utility_params = resolve_device_params(tid, utility_id, target)
    c6_params = resolve_device_params(tid, c6_id, target)
    ssl_params = resolve_device_params(tid, ssl_id, target)
    saturator_params = resolve_device_params(tid, saturator_id, target)
    l3_params = resolve_device_params(tid, l3_id, target)
    
    # Check macOS export
    if auto_export_enabled and sys.platform != "darwin":
        print("❌ Auto-export requires macOS")
        return 1
    
    # Starting parameters (aggressive for loud_preview)
    if mode == "loud_preview":
        c6_low_thresh = -20.0  # dB (tame bass buildup)
        c6_mid_thresh = -15.0  # dB (control vocal presence)
        c6_high_thresh = -10.0  # dB (control highs)
        ssl_thresh = -18.0     # dB (glue)
        ssl_makeup = 15.0      # dB
        ssl_ratio = 4.0        # ratio (0.0=2:1, 0.5=4:1, 1.0=10:1 - need to map)
        saturator_drive = 5.0  # dB
        l3_threshold = -8.0    # dB
    elif mode == "streaming_safe":
        c6_low_thresh = -25.0
        c6_mid_thresh = -20.0
        c6_high_thresh = -15.0
        ssl_thresh = -25.0
        ssl_makeup = 10.0
        ssl_ratio = 3.0
        saturator_drive = 3.0
        l3_threshold = -12.0
    else:  # headroom
        c6_low_thresh = -30.0
        c6_mid_thresh = -25.0
        c6_high_thresh = -20.0
        ssl_thresh = -30.0
        ssl_makeup = 8.0
        ssl_ratio = 2.5
        saturator_drive = 2.0
        l3_threshold = -15.0
    
    print("Starting parameters:")
    print(f"  C6: Low={c6_low_thresh:.1f} dB, Mid={c6_mid_thresh:.1f} dB, High={c6_high_thresh:.1f} dB")
    print(f"  SSL: Thresh={ssl_thresh:.1f} dB, Makeup={ssl_makeup:.1f} dB, Ratio={ssl_ratio:.1f}:1")
    print(f"  Saturator: Drive={saturator_drive:.1f} dB")
    print(f"  L3: Threshold={l3_threshold:.1f} dB")
    print()
    
    # Iteration log
    output_dir = Path("output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = output_dir / f"stand_tall_premium_{mode}.jsonl"
    
    max_iterations = 15
    prev_lufs = None
    stop_reason = None
    
    for iteration in range(1, max_iterations + 1):
        print("─" * 70)
        print(f"ITERATION {iteration}/{max_iterations}")
        print("─" * 70)
        
        # Set C6 parameters (simplified - just low/mid/high bands)
        print("Setting C6 multiband compression...")
        # Band 1 (low): params 11, 12
        set_param_normalized(tid, c6_id, c6_params["Band 1 Threshold"]["id"], 
                            db_to_normalized(c6_low_thresh, -60, 0), target)
        # Band 3 (mid): params around 23, 24
        set_param_normalized(tid, c6_id, c6_params["Band 3 Threshold"]["id"] if "Band 3 Threshold" in c6_params else 23,
                            db_to_normalized(c6_mid_thresh, -60, 0), target)
        # Band 5 (high): params around 35, 36
        set_param_normalized(tid, c6_id, c6_params["Band 5 Threshold"]["id"] if "Band 5 Threshold" in c6_params else 35,
                            db_to_normalized(c6_high_thresh, -60, 0), target)
        print(f"  ✓ C6: Low={c6_low_thresh:.1f} dB, Mid={c6_mid_thresh:.1f} dB, High={c6_high_thresh:.1f} dB")
        
        # Set SSL parameters
        print("Setting SSL compression...")
        set_param_normalized(tid, ssl_id, ssl_params["Thresh"]["id"], 
                            db_to_normalized(ssl_thresh, -60, 0), target)
        set_param_normalized(tid, ssl_id, ssl_params["Makeup"]["id"],
                            db_to_normalized(ssl_makeup, -20, 20), target)
        # Ratio: 0.0=2:1, 0.5=4:1, 1.0=10:1 (approximate)
        ssl_ratio_norm = (ssl_ratio - 2.0) / 8.0
        set_param_normalized(tid, ssl_id, ssl_params["Ratio"]["id"], ssl_ratio_norm, target)
        print(f"  ✓ SSL: Thresh={ssl_thresh:.1f} dB, Makeup={ssl_makeup:.1f} dB, Ratio={ssl_ratio:.1f}:1")
        
        # Set Saturator
        print("Setting Saturator...")
        # Drive: normalized directly (0-1 maps to reasonable range)
        saturator_drive_norm = saturator_drive / 20.0  # Assume 0-20 dB range
        set_param_normalized(tid, saturator_id, saturator_params["Drive"]["id"], saturator_drive_norm, target)
        print(f"  ✓ Saturator: Drive={saturator_drive:.1f} dB")
        
        # Set L3
        print("Setting L3 limiter...")
        # Threshold: typically -30 to 0 dB
        set_param_normalized(tid, l3_id, l3_params["Threshold"]["id"],
                            db_to_normalized(l3_threshold, -30, 0), target)
        # Out Ceiling: typically -20 to 0 dB (set to -1.0 dBTP equivalent)
        set_param_normalized(tid, l3_id, l3_params["Out Ceiling"]["id"],
                            db_to_normalized(-1.0, -20, 0), target)
        print(f"  ✓ L3: Threshold={l3_threshold:.1f} dB, Ceiling=-1.0 dB")
        
        print()
        
        # Export
        export_file = output_dir / f"stand_tall_premium_iter{iteration}.wav"
        export_file_abs = export_file.resolve()
        
        print(f"Exporting: {export_file.name}")
        
        if not auto_export_enabled:
            print("  ⚠️  Auto-export disabled - manual export required")
            input("  Press Enter after exporting...")
        else:
            # Delete old file
            if export_file_abs.exists():
                export_file_abs.unlink()
            
            try:
                auto_export_wav(export_file_abs, timeout_s=600)
                print(f"  ✓ Exported: {export_file.name}")
            except Exception as e:
                print(f"  ✗ Export failed: {e}")
                return 1
        
        # Verify
        print("Analyzing...")
        analysis = analyze_wav(export_file_abs)
        lufs_i = analysis.lufs_i
        peak_dbfs = analysis.peak_dbfs
        true_peak_dbtp = analysis.true_peak_dbtp
        
        lufs_distance = abs(lufs_i - target_lufs)
        true_peak_safe = true_peak_dbtp <= true_peak_limit
        
        print(f"  LUFS-I: {lufs_i:.2f} (target {target_lufs:.1f}, gap {lufs_distance:.2f} LU)")
        print(f"  Peak: {peak_dbfs:.2f} dBFS")
        print(f"  True Peak: {true_peak_dbtp:.2f} dBTP (limit {true_peak_limit:.1f}, {'✓ safe' if true_peak_safe else '✗ OVER'})")
        print()
        
        # Log iteration
        iter_log = {
            "iteration": iteration,
            "mode": mode,
            "c6_low_thresh": c6_low_thresh,
            "c6_mid_thresh": c6_mid_thresh,
            "c6_high_thresh": c6_high_thresh,
            "ssl_thresh": ssl_thresh,
            "ssl_makeup": ssl_makeup,
            "ssl_ratio": ssl_ratio,
            "saturator_drive": saturator_drive,
            "l3_threshold": l3_threshold,
            "lufs_i": lufs_i,
            "peak_dbfs": peak_dbfs,
            "true_peak_dbtp": true_peak_dbtp,
            "lufs_distance": lufs_distance,
            "true_peak_safe": true_peak_safe,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": compute_sha256(export_file_abs),
        }
        
        with log_path.open("a") as f:
            f.write(json.dumps(iter_log) + "\n")
        
        # Check convergence
        if true_peak_safe and lufs_distance <= 0.5:
            print(f"🎯 CONVERGED: LUFS within 0.5 LU of target, True Peak safe")
            stop_reason = "hit_target"
            break
        
        # Check true peak violation
        if true_peak_dbtp > true_peak_limit:
            print(f"⚠️  True Peak OVER limit ({true_peak_dbtp:.2f} > {true_peak_limit:.1f})")
            # Back off L3 threshold
            l3_threshold += 2.0
            print(f"   → Reducing L3 intensity (Threshold: {l3_threshold:.1f} dB)")
            continue
        
        # Detect diminishing returns
        if prev_lufs is not None:
            lufs_improvement = lufs_i - prev_lufs
            if lufs_improvement < 0.2 and lufs_i < target_lufs:
                print(f"⚠️  Diminishing returns detected (improvement: {lufs_improvement:.2f} LU)")
                print(f"   → Prioritizing C6/SSL compression over L3 gain")
                c6_low_thresh -= 2.0
                c6_mid_thresh -= 2.0
                ssl_thresh -= 2.0
                ssl_makeup += 2.0
                saturator_drive += 1.0
                # Don't increase L3 threshold
            else:
                # Normal adaptive adjustment
                if lufs_i < target_lufs - 3.0:
                    # Far from target - large adjustments
                    l3_threshold -= 3.0
                    ssl_makeup += 2.0
                    saturator_drive += 1.0
                elif lufs_i < target_lufs - 1.0:
                    # Medium gap - moderate adjustments
                    l3_threshold -= 2.0
                    ssl_makeup += 1.0
                    saturator_drive += 0.5
                else:
                    # Close to target - fine-tune
                    l3_threshold -= 1.0
                    ssl_makeup += 0.5
        else:
            # First iteration - adjust based on gap
            if lufs_i < target_lufs - 3.0:
                l3_threshold -= 3.0
                ssl_makeup += 2.0
                saturator_drive += 1.0
            else:
                l3_threshold -= 2.0
                ssl_makeup += 1.0
        
        prev_lufs = lufs_i
        
        # Clamp parameters to reasonable ranges
        c6_low_thresh = max(-60.0, min(-5.0, c6_low_thresh))
        c6_mid_thresh = max(-60.0, min(-5.0, c6_mid_thresh))
        c6_high_thresh = max(-60.0, min(-5.0, c6_high_thresh))
        ssl_thresh = max(-60.0, min(-5.0, ssl_thresh))
        ssl_makeup = max(0.0, min(30.0, ssl_makeup))
        ssl_ratio = max(2.0, min(10.0, ssl_ratio))
        saturator_drive = max(0.0, min(20.0, saturator_drive))
        l3_threshold = max(-30.0, min(0.0, l3_threshold))
        
        if iteration == max_iterations:
            stop_reason = "max_iterations"
    
    # Final summary
    print()
    print("=" * 70)
    print("OPTIMIZATION COMPLETE")
    print("=" * 70)
    print(f"\nFinal master: {export_file.name}")
    print(f"  LUFS-I: {lufs_i:.2f} (target {target_lufs:.1f})")
    print(f"  True Peak: {true_peak_dbtp:.2f} dBTP (limit {true_peak_limit:.1f})")
    print(f"  Iterations: {iteration}")
    print(f"  Stop reason: {stop_reason or 'max_iterations'}")
    print()
    print(f"✓ Log: {log_path}")
    print("=" * 70)
    
    return 0
