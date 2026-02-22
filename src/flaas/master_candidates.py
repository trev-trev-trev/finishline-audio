from __future__ import annotations
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from flaas.osc_rpc import OscTarget, request_once
from flaas.analyze import analyze_wav
from flaas.check import check_wav
from flaas.targets import DEFAULT_TARGETS
from pythonosc.udp_client import SimpleUDPClient

if sys.platform == "darwin":
    from flaas.ui_export_macos import auto_export_wav


@dataclass
class CandidatePreset:
    """Mastering candidate preset."""
    id: str
    name: str
    export_file: str
    glue_threshold_start: float  # Starting threshold (dB)
    glue_makeup: float  # Makeup gain (dB)
    glue_ratio: float  # Ratio (1.0-10.0)
    glue_attack: float  # Attack (ms)
    limiter_ceiling: float  # Ceiling (dB)
    limiter_gain: float  # Gain (dB)
    target_gr_db: tuple[float, float]  # Target GR range (min, max)


# Curated presets (starting points)
CANDIDATES = [
    CandidatePreset(
        id="consensus",
        name="CONSENSUS (balanced, safest)",
        export_file="output/master_consensus.wav",
        glue_threshold_start=-30.0,
        glue_makeup=18.0,
        glue_ratio=4.0,
        glue_attack=10.0,
        limiter_ceiling=-6.3,
        limiter_gain=30.0,
        target_gr_db=(12.0, 15.0),
    ),
    CandidatePreset(
        id="variant_a",
        name="VARIANT A (controlled, clean)",
        export_file="output/master_variant_a.wav",
        glue_threshold_start=-25.0,
        glue_makeup=15.0,
        glue_ratio=3.0,
        glue_attack=10.0,
        limiter_ceiling=-6.3,
        limiter_gain=32.0,
        target_gr_db=(8.0, 12.0),
    ),
    CandidatePreset(
        id="variant_b",
        name="VARIANT B (loud, forward)",
        export_file="output/master_variant_b.wav",
        glue_threshold_start=-35.0,
        glue_makeup=20.0,
        glue_ratio=6.0,
        glue_attack=10.0,
        limiter_ceiling=-6.5,
        limiter_gain=34.0,
        target_gr_db=(15.0, 18.0),
    ),
]


def resolve_device_id_by_name(
    track_id: int,
    device_name: str,
    target: OscTarget = OscTarget(),
) -> int:
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
    """Compute SHA256 hash of file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def master_candidates(target: OscTarget = OscTarget(), auto_export_enabled: bool = True) -> int:
    """
    Generate 3 master candidates with iterative threshold search.
    
    For each candidate:
    - Set fixed params (makeup, ratio, attack, limiter)
    - Iterate on threshold (up to 6 tries) to hit LUFS target
    - Export final WAV
    - Log results to output/master_candidates.jsonl
    
    Returns 0 on success, 20 on failure.
    """
    master_track_id = -1000
    
    print("="*70)
    print("MASTER CANDIDATES: Generating 3 Spotify-ready masters")
    print("="*70)
    
    # Resolve devices
    print(f"\nResolving devices on track {master_track_id}...")
    try:
        glue_device_id = resolve_device_id_by_name(master_track_id, "Glue Compressor", target)
        limiter_device_id = resolve_device_id_by_name(master_track_id, "Limiter", target)
        print(f"  Glue Compressor: device {glue_device_id}")
        print(f"  Limiter: device {limiter_device_id}")
    except RuntimeError as e:
        print(f"ERROR: {e}")
        return 20
    
    # Resolve parameters
    print(f"\nResolving parameters...")
    try:
        glue_params = resolve_device_params(master_track_id, glue_device_id, target)
        limiter_params = resolve_device_params(master_track_id, limiter_device_id, target)
        print(f"  Glue: {len(glue_params)} params")
        print(f"  Limiter: {len(limiter_params)} params")
    except Exception as e:
        print(f"ERROR: Failed to resolve params: {e}")
        return 20
    
    # Pre-run check
    print(f"\n{'─'*70}")
    print(f"🎛️  PRE-RUN CHECK:")
    print(f"   Ableton Live running with project open? ✓")
    print(f"   Export defaults: Rendered Track=Master, Normalize=OFF? ✓")
    print(f"   Loop/selection set to desired range (4-8 bars)? ✓")
    print(f"   Master fader = 0.0 dB? (confirm visually)")
    print(f"{'─'*70}")
    input("Press Enter to start candidate generation...")
    
    # Prepare log
    log_path = Path("output/master_candidates.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run candidates
    results = []
    
    for candidate in CANDIDATES:
        print(f"\n{'='*70}")
        print(f"CANDIDATE: {candidate.name}")
        print(f"{'='*70}")
        
        # Set fixed params
        print(f"\nSetting fixed parameters...")
        try:
            # Glue fixed params
            set_param(master_track_id, glue_device_id, "Makeup", candidate.glue_makeup, glue_params, target)
            print(f"  ✓ Glue Makeup = {candidate.glue_makeup} dB")
            
            set_param(master_track_id, glue_device_id, "Ratio", candidate.glue_ratio, glue_params, target)
            print(f"  ✓ Glue Ratio = {candidate.glue_ratio}:1")
            
            set_param(master_track_id, glue_device_id, "Attack", candidate.glue_attack, glue_params, target)
            print(f"  ✓ Glue Attack = {candidate.glue_attack} ms")
            
            # Limiter params
            set_param(master_track_id, limiter_device_id, "Ceiling", candidate.limiter_ceiling, limiter_params, target)
            print(f"  ✓ Limiter Ceiling = {candidate.limiter_ceiling} dB")
            
            set_param(master_track_id, limiter_device_id, "Gain", candidate.limiter_gain, limiter_params, target)
            print(f"  ✓ Limiter Gain = {candidate.limiter_gain} dB")
            
        except Exception as e:
            print(f"ERROR: Failed to set fixed params: {e}")
            continue
        
        # Iterative threshold search (up to 6 iterations)
        print(f"\nIterative threshold search (target LUFS -10.50, peak <= -6.00)...")
        threshold = candidate.glue_threshold_start
        best_result = None
        
        for iteration in range(1, 7):
            print(f"\n  Iteration {iteration}/6: Threshold = {threshold:.1f} dB")
            
            # Set threshold
            try:
                set_param(master_track_id, glue_device_id, "Threshold", threshold, glue_params, target)
                print(f"    ✓ Threshold set")
            except Exception as e:
                print(f"    ✗ Failed to set threshold: {e}")
                break
            
            # Export (auto or manual)
            # CRITICAL: Resolve to absolute path, delete existing
            export_path = Path(candidate.export_file).expanduser().resolve()
            temp_export = (export_path.parent / f"{export_path.stem}_iter{iteration}{export_path.suffix}").resolve()
            
            # Remove existing file
            if temp_export.exists():
                temp_export.unlink()
            
            if auto_export_enabled and sys.platform == "darwin":
                print(f"    📤 Auto-exporting: {temp_export.name}")
                try:
                    auto_export_wav(temp_export, timeout_s=600)
                    print(f"    ✓ Export complete")
                except RuntimeError as e:
                    print(f"    ✗ Export failed: {e}")
                    break
            else:
                print(f"    📤 Export manually to: {temp_export}")
                input("    Press Enter after export completes...")
            
            # Verify
            try:
                analysis = analyze_wav(temp_export)
                check = check_wav(temp_export, DEFAULT_TARGETS)
                
                print(f"    LUFS: {analysis.lufs_i:.2f} (target -10.50) pass={check.pass_lufs}")
                print(f"    PEAK: {analysis.peak_dbfs:.2f} (limit -6.00) pass={check.pass_peak}")
                
                # Log iteration
                iter_log = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "candidate": candidate.id,
                    "iteration": iteration,
                    "export_file": str(temp_export),
                    "threshold_db": threshold,
                    "lufs_i": analysis.lufs_i,
                    "peak_dbfs": analysis.peak_dbfs,
                    "pass_lufs": check.pass_lufs,
                    "pass_peak": check.pass_peak,
                }
                
                # Check success
                if check.pass_lufs and check.pass_peak:
                    print(f"    ✅ TARGETS HIT!")
                    best_result = iter_log
                    # Rename to final filename
                    if temp_export != export_path:
                        if export_path.exists():
                            export_path.unlink()
                        temp_export.rename(export_path)
                        best_result["export_file"] = str(export_path)
                    break
                
                # Adjust for next iteration
                if not check.pass_peak:
                    # Peak too high - reduce limiter gain slightly
                    print(f"    → Peak too high, reducing limiter gain")
                    candidate.limiter_gain -= 1.0
                    set_param(master_track_id, limiter_device_id, "Gain", candidate.limiter_gain, limiter_params, target)
                elif not check.pass_lufs:
                    # LUFS too low - more compression
                    print(f"    → LUFS too low, increasing compression")
                    threshold -= 2.5  # Lower threshold = more GR
                
                best_result = iter_log
                
            except Exception as e:
                print(f"    ✗ Verification failed: {e}")
                break
        
        # Log final result
        if best_result:
            # Add full preset info
            final_log = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "candidate": candidate.id,
                "name": candidate.name,
                "export_file": best_result["export_file"],
                "sha256": compute_sha256(Path(best_result["export_file"])),
                "params": {
                    "master_fader_db": 0.0,
                    "glue": {
                        "threshold_db": best_result["threshold_db"],
                        "makeup_db": candidate.glue_makeup,
                        "ratio": candidate.glue_ratio,
                        "attack_ms": candidate.glue_attack,
                    },
                    "limiter": {
                        "ceiling_db": candidate.limiter_ceiling,
                        "gain_db": candidate.limiter_gain,
                    },
                },
                "results": {
                    "lufs_i": best_result["lufs_i"],
                    "peak_dbfs": best_result["peak_dbfs"],
                    "pass_lufs": best_result["pass_lufs"],
                    "pass_peak": best_result["pass_peak"],
                },
                "iterations": best_result["iteration"],
            }
            
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(final_log) + "\n")
            
            results.append(final_log)
            print(f"\n  ✓ Logged to {log_path}")
        else:
            print(f"\n  ✗ No valid result for {candidate.name}")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"MASTER CANDIDATES COMPLETE")
    print(f"{'='*70}")
    print(f"\nGenerated {len(results)}/3 candidates:")
    print(f"")
    
    for r in results:
        status = "✅ PASS" if (r["results"]["pass_lufs"] and r["results"]["pass_peak"]) else "⚠️  NEAR"
        print(f"{status} {r['name']}")
        print(f"     File: {r['export_file']}")
        print(f"     LUFS: {r['results']['lufs_i']:.2f} (target -10.50)")
        print(f"     PEAK: {r['results']['peak_dbfs']:.2f} (limit -6.00)")
        print(f"     Iterations: {r['iterations']}")
        print(f"")
    
    print(f"Logs: {log_path}")
    print(f"")
    
    # Update EXPORT_FINDINGS.md
    update_export_findings(results)
    
    return 0


def update_export_findings(results: list[dict]) -> None:
    """Append candidate results table to EXPORT_FINDINGS.md."""
    findings_path = Path("docs/reference/EXPORT_FINDINGS.md")
    
    if not findings_path.exists():
        print(f"Warning: {findings_path} not found, skipping update")
        return
    
    # Build table
    table = "\n\n---\n\n## Master Candidates (Automated Generation)\n\n"
    table += "**Date**: " + datetime.now(timezone.utc).strftime("%Y-%m-%d") + "\n"
    table += "**Command**: `flaas master-candidates`\n\n"
    table += "| Candidate | LUFS | Peak | Pass | Iterations | Settings |\n"
    table += "|-----------|-----:|-----:|:----:|-----------:|----------|\n"
    
    for r in results:
        candidate = r["candidate"]
        lufs = r["results"]["lufs_i"]
        peak = r["results"]["peak_dbfs"]
        pass_both = r["results"]["pass_lufs"] and r["results"]["pass_peak"]
        pass_str = "✅" if pass_both else "⚠️"
        iters = r["iterations"]
        
        glue = r["params"]["glue"]
        limiter = r["params"]["limiter"]
        settings = f"Glue T={glue['threshold_db']:.1f} M={glue['makeup_db']:.1f} R={glue['ratio']:.1f}, Lim C={limiter['ceiling_db']:.1f} G={limiter['gain_db']:.1f}"
        
        table += f"| {candidate} | {lufs:.2f} | {peak:.2f} | {pass_str} | {iters} | {settings} |\n"
    
    table += "\n**File paths**:\n"
    for r in results:
        table += f"- `{r['export_file']}`\n"
    
    # Append to file
    with findings_path.open("a", encoding="utf-8") as f:
        f.write(table)
    
    print(f"✓ Updated {findings_path}")


def compute_sha256(path: Path) -> str:
    """Compute SHA256 hash."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
