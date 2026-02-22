from __future__ import annotations
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from flaas.osc_rpc import OscTarget, request_once
from flaas.analyze import analyze_wav
from flaas.check import check_wav
from flaas.targets import DEFAULT_TARGETS
from pythonosc.udp_client import SimpleUDPClient

if sys.platform == "darwin":
    from flaas.ui_export_macos import auto_export_wav


def resolve_device_id_by_name(track_id: int, device_name: str, target: OscTarget = OscTarget()) -> int:
    """Resolve device ID by name (case-insensitive)."""
    response = request_once(target, "/live/track/get/devices/name", [track_id], timeout_sec=3.0)
    names = list(response)[1:]
    
    for idx, name in enumerate(names):
        if str(name).strip().lower() == device_name.strip().lower():
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


def set_param(track_id: int, device_id: int, param_name: str, value: float, params: dict, target: OscTarget) -> None:
    """Set device parameter (dB → normalized conversion)."""
    if param_name not in params:
        raise RuntimeError(f"Parameter '{param_name}' not found in device")
    
    info = params[param_name]
    param_id = info["id"]
    min_val = info["min"]
    max_val = info["max"]
    
    # Normalize
    norm_value = (value - min_val) / (max_val - min_val)
    norm_value = max(0.0, min(1.0, norm_value))
    
    # Fire-and-forget write
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, param_id, norm_value])


def compute_sha256(path: Path) -> str:
    """Compute SHA256 hash."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def master_consensus(
    target: OscTarget = OscTarget(),
    auto_export_enabled: bool = True,
    target_lufs: float = -9.0,  # Louder target (competitive streaming)
    peak_limit: float = -6.0,
) -> int:
    """
    Generate ONE high-quality consensus master with iterative optimization.
    
    Strategy:
    - Start aggressive: High compression (GR 15-18 dB), high makeup (20 dB), high limiter gain (35 dB)
    - Iterate up to 10 times to hit LUFS target (-9.0) while maintaining peak safety
    - Adjust threshold, makeup, and limiter gain dynamically based on results
    
    Output: output/master_consensus.wav
    Log: output/master_consensus.jsonl
    
    Returns 0 on success, 20 on failure.
    """
    master_track_id = -1000
    final_output = Path("output/master_consensus.wav")
    log_path = Path("output/master_consensus.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("MASTER CONSENSUS: Single High-Quality Master Generation")
    print("="*70)
    print(f"\nTarget: LUFS {target_lufs:.1f} (competitive streaming loudness)")
    print(f"Peak limit: {peak_limit:.1f} dBFS")
    print(f"")
    
    # Resolve devices
    print(f"Resolving devices on track {master_track_id}...")
    try:
        glue_device_id = resolve_device_id_by_name(master_track_id, "Glue Compressor", target)
        limiter_device_id = resolve_device_id_by_name(master_track_id, "Limiter", target)
        print(f"  ✓ Glue Compressor: device {glue_device_id}")
        print(f"  ✓ Limiter: device {limiter_device_id}")
    except RuntimeError as e:
        print(f"ERROR: {e}")
        return 20
    
    # Resolve parameters
    print(f"\nResolving parameters...")
    try:
        glue_params = resolve_device_params(master_track_id, glue_device_id, target)
        limiter_params = resolve_device_params(master_track_id, limiter_device_id, target)
        print(f"  ✓ Glue Compressor: {len(glue_params)} params")
        print(f"  ✓ Limiter: {len(limiter_params)} params")
    except Exception as e:
        print(f"ERROR: Failed to resolve params: {e}")
        return 20
    
    # Pre-run check
    print(f"\n{'─'*70}")
    print(f"PRE-RUN CHECKLIST:")
    print(f"  [ ] Ableton Live running with project open")
    print(f"  [ ] Export defaults: Rendered Track=Master, Normalize=OFF")
    print(f"  [ ] Export folder = /Users/trev/Repos/finishline_audio_repo/output")
    print(f"  [ ] Loop/selection set to 8-bar section")
    print(f"  [ ] Master fader = 0.0 dB (verify visually)")
    print(f"  [ ] Device chain: Utility → EQ → Glue Compressor → Limiter (all ON)")
    print(f"{'─'*70}")
    input("Press Enter to start optimization...")
    
    # Starting parameters (aggressive for loudness)
    threshold = -35.0  # Start with strong compression
    makeup = 22.0      # High makeup for loudness
    ratio = 5.0        # Moderate-high ratio
    attack = 8.0       # Fast attack for control
    limiter_ceiling = -6.2  # Slight margin
    limiter_gain = 36.0     # Aggressive gain
    
    print(f"\nStarting parameters (aggressive for loudness):")
    print(f"  Glue: Threshold {threshold:.1f} dB, Makeup {makeup:.1f} dB, Ratio {ratio:.1f}:1, Attack {attack:.1f} ms")
    print(f"  Limiter: Ceiling {limiter_ceiling:.1f} dB, Gain {limiter_gain:.1f} dB")
    print(f"")
    
    best_result = None
    best_distance = float('inf')
    
    for iteration in range(1, 11):  # Up to 10 iterations
        print(f"\n{'─'*70}")
        print(f"ITERATION {iteration}/10")
        print(f"{'─'*70}")
        
        # Set all parameters
        print(f"Setting parameters...")
        try:
            set_param(master_track_id, glue_device_id, "Threshold", threshold, glue_params, target)
            print(f"  ✓ Glue Threshold = {threshold:.1f} dB")
            
            set_param(master_track_id, glue_device_id, "Makeup", makeup, glue_params, target)
            print(f"  ✓ Glue Makeup = {makeup:.1f} dB")
            
            set_param(master_track_id, glue_device_id, "Ratio", ratio, glue_params, target)
            print(f"  ✓ Glue Ratio = {ratio:.1f}:1")
            
            set_param(master_track_id, glue_device_id, "Attack", attack, glue_params, target)
            print(f"  ✓ Glue Attack = {attack:.1f} ms")
            
            set_param(master_track_id, limiter_device_id, "Ceiling", limiter_ceiling, limiter_params, target)
            print(f"  ✓ Limiter Ceiling = {limiter_ceiling:.1f} dB")
            
            set_param(master_track_id, limiter_device_id, "Gain", limiter_gain, limiter_params, target)
            print(f"  ✓ Limiter Gain = {limiter_gain:.1f} dB")
            
        except Exception as e:
            print(f"ERROR: Failed to set params: {e}")
            return 20
        
        # Export
        temp_export = final_output.parent / f"{final_output.stem}_iter{iteration}{final_output.suffix}"
        if temp_export.exists():
            temp_export.unlink()
        
        print(f"\nExporting: {temp_export.name}")
        
        if auto_export_enabled and sys.platform == "darwin":
            try:
                auto_export_wav(temp_export, timeout_s=180)
                print(f"  ✓ Export complete")
            except RuntimeError as e:
                print(f"  ✗ Export failed: {e}")
                return 20
        else:
            print(f"  Manual export to: {temp_export}")
            input("  Press Enter after export completes...")
        
        # Verify
        print(f"\nVerifying...")
        try:
            analysis = analyze_wav(temp_export)
            
            lufs_distance = abs(analysis.lufs_i - target_lufs)
            peak_safe = analysis.peak_dbfs <= peak_limit
            
            print(f"  LUFS: {analysis.lufs_i:.2f} dBFS (target {target_lufs:.1f}, distance {lufs_distance:.2f})")
            print(f"  Peak: {analysis.peak_dbfs:.2f} dBFS (limit {peak_limit:.1f}, safe={peak_safe})")
            
            # Log iteration
            iter_log = {
                "iteration": iteration,
                "threshold_db": threshold,
                "makeup_db": makeup,
                "ratio": ratio,
                "limiter_ceiling_db": limiter_ceiling,
                "limiter_gain_db": limiter_gain,
                "lufs_i": analysis.lufs_i,
                "peak_dbfs": analysis.peak_dbfs,
                "lufs_distance": lufs_distance,
                "peak_safe": peak_safe,
            }
            
            # Check if this is best so far (closest to target with safe peak)
            if peak_safe and lufs_distance < best_distance:
                best_distance = lufs_distance
                best_result = iter_log
                print(f"  ✅ BEST SO FAR (distance {lufs_distance:.2f})")
            
            # Check convergence (LUFS within 0.3 LU of target, peak safe)
            if peak_safe and lufs_distance <= 0.3:
                print(f"\n{'='*70}")
                print(f"✅ CONVERGENCE ACHIEVED")
                print(f"  LUFS: {analysis.lufs_i:.2f} (target {target_lufs:.1f})")
                print(f"  Peak: {analysis.peak_dbfs:.2f} (limit {peak_limit:.1f})")
                print(f"{'='*70}")
                # Rename to final
                if temp_export != final_output:
                    if final_output.exists():
                        final_output.unlink()
                    temp_export.rename(final_output)
                best_result["export_file"] = str(final_output)
                best_result["final"] = True
                break
            
            # Adjust for next iteration
            print(f"\n  Adjusting for next iteration...")
            
            if not peak_safe:
                # Peak too high - CRITICAL: reduce gain immediately
                print(f"    ⚠️  Peak too high ({analysis.peak_dbfs:.2f} > {peak_limit:.1f})")
                limiter_gain -= 2.0
                print(f"    → Reducing limiter gain to {limiter_gain:.1f} dB")
            
            elif analysis.lufs_i < target_lufs:
                # Too quiet - need more loudness
                lufs_gap = target_lufs - analysis.lufs_i
                print(f"    Too quiet (gap {lufs_gap:.2f} LU)")
                
                if lufs_gap > 2.0:
                    # Large gap: aggressive adjustment
                    print(f"    → Large gap: lowering threshold by 4 dB, adding 2 dB makeup, adding 3 dB limiter gain")
                    threshold -= 4.0  # More compression
                    makeup += 2.0     # More output
                    limiter_gain += 3.0  # More final gain
                elif lufs_gap > 1.0:
                    # Medium gap: moderate adjustment
                    print(f"    → Medium gap: lowering threshold by 2.5 dB, adding 1.5 dB makeup, adding 2 dB limiter gain")
                    threshold -= 2.5
                    makeup += 1.5
                    limiter_gain += 2.0
                else:
                    # Small gap: gentle adjustment
                    print(f"    → Small gap: lowering threshold by 1.5 dB, adding 1 dB makeup, adding 1 dB limiter gain")
                    threshold -= 1.5
                    makeup += 1.0
                    limiter_gain += 1.0
            
            elif analysis.lufs_i > target_lufs:
                # Too loud (rare, but possible)
                lufs_excess = analysis.lufs_i - target_lufs
                print(f"    Too loud (excess {lufs_excess:.2f} LU)")
                print(f"    → Raising threshold by 2 dB, reducing makeup by 1 dB")
                threshold += 2.0
                makeup -= 1.0
            
        except Exception as e:
            print(f"  ✗ Verification failed: {e}")
            return 20
    
    # Final result
    if not best_result:
        print(f"\nERROR: No valid result after {iteration} iterations")
        return 20
    
    # If we didn't hit exact convergence, use best result
    if not best_result.get("final"):
        print(f"\n{'='*70}")
        print(f"USING BEST RESULT (closest to target)")
        print(f"  LUFS: {best_result['lufs_i']:.2f} (target {target_lufs:.1f}, distance {best_result['lufs_distance']:.2f})")
        print(f"  Peak: {best_result['peak_dbfs']:.2f} (limit {peak_limit:.1f})")
        print(f"  Iteration: {best_result['iteration']}")
        print(f"{'='*70}")
        
        # Find the best iteration file and rename to final
        best_iter = best_result['iteration']
        best_file = final_output.parent / f"{final_output.stem}_iter{best_iter}{final_output.suffix}"
        if best_file.exists():
            if final_output.exists():
                final_output.unlink()
            best_file.rename(final_output)
            best_result["export_file"] = str(final_output)
    
    # Compute final SHA256
    if final_output.exists():
        best_result["sha256"] = compute_sha256(final_output)
    
    # Write final log
    final_log = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": "CONSENSUS (high-quality, competitive loudness)",
        "export_file": str(final_output),
        "sha256": best_result.get("sha256", ""),
        "params": {
            "master_fader_db": 0.0,
            "glue": {
                "threshold_db": best_result["threshold_db"],
                "makeup_db": best_result["makeup_db"],
                "ratio": best_result["ratio"],
                "attack_ms": attack,
            },
            "limiter": {
                "ceiling_db": best_result["limiter_ceiling_db"],
                "gain_db": best_result["limiter_gain_db"],
            },
        },
        "results": {
            "lufs_i": best_result["lufs_i"],
            "peak_dbfs": best_result["peak_dbfs"],
            "lufs_distance": best_result["lufs_distance"],
            "peak_safe": best_result["peak_safe"],
        },
        "iterations_total": best_result["iteration"],
        "converged": best_result.get("final", False),
    }
    
    with log_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(final_log, indent=2) + "\n")
    
    # Print final summary
    print(f"\n{'='*70}")
    print(f"✅ CONSENSUS MASTER COMPLETE")
    print(f"{'='*70}")
    print(f"")
    print(f"File: {final_output}")
    print(f"")
    print(f"Results:")
    print(f"  LUFS: {best_result['lufs_i']:.2f} dBFS (target {target_lufs:.1f})")
    print(f"  Peak: {best_result['peak_dbfs']:.2f} dBFS (limit {peak_limit:.1f})")
    print(f"  Distance from target: {best_result['lufs_distance']:.2f} LU")
    print(f"  Peak safe: {best_result['peak_safe']}")
    print(f"")
    print(f"Final settings:")
    print(f"  Glue Threshold: {best_result['threshold_db']:.1f} dB")
    print(f"  Glue Makeup: {best_result['makeup_db']:.1f} dB")
    print(f"  Glue Ratio: {best_result['ratio']:.1f}:1")
    print(f"  Limiter Ceiling: {best_result['limiter_ceiling_db']:.1f} dB")
    print(f"  Limiter Gain: {best_result['limiter_gain_db']:.1f} dB")
    print(f"")
    print(f"Iterations: {best_result['iteration']}")
    print(f"Log: {log_path}")
    print(f"")
    
    # Update EXPORT_FINDINGS.md
    update_export_findings(final_log)
    
    return 0


def update_export_findings(result: dict) -> None:
    """Append consensus result to EXPORT_FINDINGS.md."""
    findings_path = Path("docs/reference/EXPORT_FINDINGS.md")
    
    if not findings_path.exists():
        print(f"Warning: {findings_path} not found, skipping doc update")
        return
    
    entry = f"\n\n---\n\n## Consensus Master (Automated Generation)\n\n"
    entry += f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
    entry += f"**Command**: `flaas master-consensus`\n"
    entry += f"**File**: `{result['export_file']}`\n\n"
    
    entry += "**Results**:\n"
    entry += f"- LUFS: {result['results']['lufs_i']:.2f} dBFS (target {-9.0:.1f})\n"
    entry += f"- Peak: {result['results']['peak_dbfs']:.2f} dBFS (limit -6.0)\n"
    entry += f"- Distance from target: {result['results']['lufs_distance']:.2f} LU\n"
    entry += f"- Converged: {result['converged']}\n"
    entry += f"- Iterations: {result['iterations_total']}\n\n"
    
    entry += "**Final settings**:\n"
    glue = result['params']['glue']
    limiter = result['params']['limiter']
    entry += f"- Glue: Threshold {glue['threshold_db']:.1f} dB, Makeup {glue['makeup_db']:.1f} dB, Ratio {glue['ratio']:.1f}:1\n"
    entry += f"- Limiter: Ceiling {limiter['ceiling_db']:.1f} dB, Gain {limiter['gain_db']:.1f} dB\n"
    
    with findings_path.open("a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"✓ Updated {findings_path}")
