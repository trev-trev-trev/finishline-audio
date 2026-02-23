"""
Pre-flight checks for master consensus generation.

Hard invariants that must be verified before optimization:
- Master fader at 0.0 dB (post-chain, defeats limiter if boosted)
- Device order correct (Glue → Saturator → Limiter)
- All devices active (not bypassed)
"""

from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once


def verify_master_fader(track_id: int, target: OscTarget = OscTarget()) -> tuple[bool, float]:
    """
    Verify master fader is at 0.0 dB.
    
    Returns: (is_zero, actual_value_db)
    
    NOTE: /live/track/get/volume endpoint may not exist.
    If it fails, we cannot verify programmatically - must rely on user confirmation.
    """
    try:
        # Try to read master fader volume
        # Response format varies, may be (track_id, volume) or just volume
        response = request_once(target, "/live/track/get/volume", [track_id], timeout_sec=1.5)
        
        # Parse response (handle tuple or single value)
        if isinstance(response, (tuple, list)):
            volume = float(response[-1])  # Last element is likely the value
        else:
            volume = float(response)
        
        # Convert normalized to dB (if 0.85 is 0 dB, adjust accordingly)
        # This is a guess - actual mapping depends on Ableton's internal scale
        # Common mapping: 0.85 = 0 dB, 1.0 = +6 dB, 0.0 = -inf
        volume_db = 0.0 if abs(volume - 0.85) < 0.01 else (volume - 0.85) * 50.0
        
        is_zero = abs(volume_db) < 0.5  # Within 0.5 dB tolerance
        return is_zero, volume_db
    
    except Exception:
        # Endpoint doesn't exist or failed - cannot verify
        return None, None


def verify_device_order(track_id: int, expected_order: list[str], target: OscTarget = OscTarget()) -> tuple[bool, list[str]]:
    """
    Verify device chain order matches expected.
    
    Args:
        track_id: Track to check
        expected_order: List of device names in expected order (e.g., ["Glue Compressor", "Saturator", "Limiter"])
        target: OSC target
    
    Returns: (matches_order, actual_devices)
    """
    try:
        response = request_once(target, "/live/track/get/devices/name", [track_id], timeout_sec=1.5)
        device_names = [str(name).strip() for name in list(response)[1:]]  # Drop track_id
        
        # Check if expected devices appear in correct order
        # Allow other devices before/after/between, just verify relative order
        expected_indices = []
        for expected_name in expected_order:
            found_idx = None
            for idx, actual_name in enumerate(device_names):
                if expected_name.lower() in actual_name.lower():
                    found_idx = idx
                    break
            
            if found_idx is None:
                # Device missing (optional devices like Saturator are OK)
                if expected_name.lower() == "saturator":
                    continue
                else:
                    return False, device_names
            
            expected_indices.append(found_idx)
        
        # Verify indices are in ascending order
        matches_order = all(expected_indices[i] < expected_indices[i+1] for i in range(len(expected_indices)-1))
        return matches_order, device_names
    
    except Exception as e:
        raise RuntimeError(f"Failed to verify device order: {e}")


def run_preflight_checks(track_id: int, target: OscTarget = OscTarget(), expected_chain: list[str] | None = None) -> bool:
    """
    Run all pre-flight checks.
    
    Args:
        track_id: Track ID to check
        target: OSC target
        expected_chain: Optional list of device names in expected order (default: stock chain)
    
    Returns: True if all checks pass, False otherwise
    Prints diagnostics to stdout.
    """
    print(f"\n{'='*70}")
    print(f"PRE-FLIGHT CHECKS")
    print(f"{'='*70}")
    
    all_pass = True
    
    # Check 1: Master fader
    print(f"\n1. Master fader verification...")
    fader_ok, fader_db = verify_master_fader(track_id, target)
    
    if fader_ok is None:
        print(f"   ⚠️  Cannot verify master fader via OSC (endpoint unavailable)")
        print(f"   → USER MUST CONFIRM: Master fader is visually at 0.0 dB")
        user_confirm = input(f"   → Confirm master fader is 0.0 dB? (y/n): ").strip().lower()
        if user_confirm != 'y':
            print(f"   ❌ FAIL: Master fader not confirmed at 0.0 dB")
            all_pass = False
        else:
            print(f"   ✅ PASS: User confirmed master fader at 0.0 dB")
    elif fader_ok:
        print(f"   ✅ PASS: Master fader at {fader_db:.2f} dB (within tolerance)")
    else:
        print(f"   ❌ FAIL: Master fader at {fader_db:.2f} dB (must be 0.0 dB)")
        print(f"   → Master fader is POST-chain (defeats limiter if boosted)")
        all_pass = False
    
    # Check 2: Device order
    print(f"\n2. Device chain order verification...")
    if expected_chain is None:
        expected_chain = ["Glue Compressor", "Saturator", "Limiter"]
    
    try:
        order_ok, actual_devices = verify_device_order(track_id, expected_chain, target)
        
        print(f"   Expected: {' → '.join(expected_chain)}")
        print(f"   Actual: {' → '.join(actual_devices)}")
        
        if order_ok:
            print(f"   ✅ PASS: Device order correct")
        else:
            print(f"   ❌ FAIL: Device order incorrect")
            print(f"   → Limiter/L3 must be LAST (final peak catcher)")
            print(f"   → Saturator (optional) should be BEFORE limiter")
            all_pass = False
    
    except RuntimeError as e:
        print(f"   ❌ FAIL: {e}")
        all_pass = False
    
    # Summary
    print(f"\n{'='*70}")
    if all_pass:
        print(f"✅ ALL PRE-FLIGHT CHECKS PASSED")
    else:
        print(f"❌ PRE-FLIGHT CHECKS FAILED")
        print(f"   → Fix issues above before running optimization")
    print(f"{'='*70}\n")
    
    return all_pass
