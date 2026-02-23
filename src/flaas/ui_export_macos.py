"""
macOS UI automation for Ableton Live export.

Uses AppleScript to drive Ableton's Export dialog via System Events.
Requires: Accessibility + Automation permissions for Terminal.
"""

from __future__ import annotations
import subprocess
import time
import os
from pathlib import Path


def auto_export_wav(out_path: str | Path, timeout_s: int = 600) -> None:
    """
    Trigger Ableton Live export via macOS UI automation (AppleScript).
    
    Args:
        out_path: Path to output WAV file (will be resolved to absolute)
        timeout_s: Maximum time to wait for file to stabilize (default 600s)
    
    Raises:
        RuntimeError: If export fails or file doesn't appear
    
    Strategy:
    1. Resolve to absolute path (critical - relative paths fail)
    2. Delete existing file (avoid overwrite prompts)
    3. Run AppleScript to drive Ableton UI:
       - Bring Ableton frontmost
       - Close plugin windows (best-effort, they block dialogs)
       - File menu → Export Audio/Video (preferred over Cmd+Shift+R)
       - Click Export button in dialog
       - Navigate to exact folder via Cmd+Shift+G
       - Enter filename
       - Click Save button (preferred over Return)
       - Handle overwrite dialog (click Replace)
    4. Wait for file to appear + stabilize (size + mtime)
    5. If missing: Use mdfind to discover where it went
    """
    # CRITICAL: Resolve to absolute path immediately
    out_path = Path(out_path).expanduser().resolve()
    out_dir = out_path.parent
    
    # Remove .wav extension (Ableton adds it automatically)
    # If we type "_probe.wav", Ableton creates "_probe.wav.wav"
    out_filename_base = out_path.stem  # Without extension
    out_filename_full = out_path.name  # With extension (for wait loop)
    
    debug = os.environ.get("FLAAS_UI_EXPORT_DEBUG") == "1"
    
    if debug:
        print(f"[DEBUG] Auto-export target: {out_path}")
        print(f"[DEBUG] Directory: {out_dir}")
        print(f"[DEBUG] Filename (base, no ext): {out_filename_base}")
        print(f"[DEBUG] Filename (full): {out_filename_full}")
    
    # Delete existing file (avoids overwrite prompt)
    if out_path.exists():
        out_path.unlink()
        if debug:
            print(f"[DEBUG] Deleted existing: {out_path}")
    
    # AppleScript to drive Ableton export
    # Uses System Events to click UI elements by name
    script = f'''
on run
    log "Step 1: Bring Ableton Live frontmost"
    tell application "System Events"
        set abletonProcs to (processes whose bundle identifier starts with "com.ableton.live")
        if (count of abletonProcs) is 0 then
            error "Ableton Live not running"
        end if
        set abletonProc to item 1 of abletonProcs
        set frontmost of abletonProc to true
    end tell
    delay 0.5
    
    log "Step 2: Close plugin windows (best-effort)"
    tell application "System Events"
        tell (item 1 of (processes whose bundle identifier starts with "com.ableton.live"))
            try
                tell menu bar 1
                    tell menu bar item "View"
                        tell menu 1
                            set viewItems to menu items whose name contains "Plug"
                            repeat with viewItem in viewItems
                                if name of viewItem contains "Hide" or name of viewItem contains "Close" then
                                    click viewItem
                                    delay 0.2
                                    exit repeat
                                end if
                            end repeat
                        end tell
                    end tell
                end tell
            end try
        end tell
    end tell
    delay 0.3
    
    log "Step 3: Open File menu -> Export Audio/Video"
    tell application "System Events"
        tell (item 1 of (processes whose bundle identifier starts with "com.ableton.live"))
            tell menu bar 1
                tell menu bar item "File"
                    tell menu 1
                        set exportItems to menu items whose name contains "Export"
                        if (count of exportItems) > 0 then
                            click item 1 of exportItems
                        else
                            log "Step 3 fallback: Using Cmd+Shift+R"
                            keystroke "r" using {{command down, shift down}}
                        end if
                    end tell
                end tell
            end tell
        end tell
    end tell
    delay 1.5
    
    log "Step 4: Click Export button in dialog"
    tell application "System Events"
        tell (item 1 of (processes whose bundle identifier starts with "com.ableton.live"))
            try
                click button "Export" of window 1
                delay 1.5
            on error
                log "Step 4 fallback: Pressing Return"
                keystroke return
                delay 1.5
            end try
        end tell
    end tell
    
    log "Step 5: Navigate to folder (Cmd+Shift+G) - FORCE correct location"
    tell application "System Events"
        tell (item 1 of (processes whose bundle identifier starts with "com.ableton.live"))
            -- Clear any cached location by clicking in location dropdown (if visible)
            try
                -- Click the location bar to ensure we can navigate
                keystroke "l" using {{command down}}
                delay 0.3
            end try
            
            -- Now force absolute path navigation
            keystroke "g" using {{command down, shift down}}
            delay 0.8
            
            log "Step 6: Type absolute folder path (clearing first)"
            -- Clear any pre-filled path
            keystroke "a" using {{command down}}
            delay 0.2
            keystroke "{out_dir}"
            delay 0.5
            keystroke return
            delay 0.8
            
            log "Step 7: Clear filename field and type new name (WITHOUT extension)"
            keystroke "a" using {{command down}}
            delay 0.2
            keystroke "{out_filename_base}"
            delay 0.3
            
            log "Step 8: Click Save button"
            try
                click button "Save" of sheet 1 of window 1
                delay 0.5
            on error
                log "Step 8 fallback: Pressing Return"
                keystroke return
                delay 0.5
            end try
            
            log "Step 9: Handle overwrite prompt"
            try
                tell sheet 1 of window 1
                    set replaceButtons to buttons whose name contains "Replace"
                    if (count of replaceButtons) > 0 then
                        click item 1 of replaceButtons
                        log "Step 9: Clicked Replace button"
                    else
                        keystroke return
                        log "Step 9: Pressed Return for overwrite"
                    end if
                end tell
                delay 0.3
            on error
                log "Step 9: No overwrite prompt (file didn't exist)"
            end try
        end tell
    end tell
    
    log "Step 10: Export initiated successfully"
    return "Export triggered"
end run
'''
    
    # Run AppleScript
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        
        if debug:
            print(f"[DEBUG] AppleScript stdout: {result.stdout.strip()}")
            if result.stderr:
                print(f"[DEBUG] AppleScript logs:")
                for line in result.stderr.strip().split('\n'):
                    print(f"  {line}")
    
    except subprocess.CalledProcessError as e:
        error_msg = f"AppleScript failed (exit {e.returncode})"
        if e.stdout:
            error_msg += f"\nStdout: {e.stdout}"
        if e.stderr:
            error_msg += f"\nStderr: {e.stderr}"
        raise RuntimeError(error_msg)
    
    except subprocess.TimeoutExpired:
        raise RuntimeError("AppleScript timed out after 30s (UI hung?)")
    
    # Wait for file to appear and stabilize
    if debug:
        print(f"[DEBUG] Waiting for file to appear: {out_path}")
    
    start_time = time.time()
    size_prev = None
    mtime_prev = None
    stable_checks = 0
    
    while (time.time() - start_time) < timeout_s:
        if out_path.exists():
            size_now = out_path.stat().st_size
            mtime_now = out_path.stat().st_mtime
            
            if size_now == size_prev and mtime_now == mtime_prev:
                stable_checks += 1
                if stable_checks >= 2:
                    if debug:
                        print(f"[DEBUG] File stable: size={size_now}, mtime={mtime_now}")
                    return  # Success!
            else:
                stable_checks = 0
                if debug and size_prev is not None:
                    print(f"[DEBUG] File growing: {size_prev} → {size_now} bytes")
            
            size_prev = size_now
            mtime_prev = mtime_now
        
        time.sleep(2)
    
    # File never appeared or never stabilized - try to find it
    error_msg = f"Export file did not appear: {out_path}"
    
    # Use mdfind to search for the filename (may have been saved elsewhere)
    try:
        mdfind_result = subprocess.run(
            ["mdfind", f"kMDItemFSName == '{out_filename_full}'"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if mdfind_result.stdout.strip():
            found_paths = mdfind_result.stdout.strip().split('\n')[:5]  # First 5 hits
            error_msg += f"\n\nFile MAY have been saved to (mdfind results):"
            for path in found_paths:
                error_msg += f"\n  - {path}"
            error_msg += f"\n\nCheck Ableton's last export location (File → Export → check folder path)"
            
            if debug:
                error_msg += f"\n[DEBUG] Expected: {out_path}"
                error_msg += f"\n[DEBUG] mdfind found {len(found_paths)} matches"
    
    except Exception as e:
        if debug:
            error_msg += f"\n[DEBUG] mdfind search failed: {e}"
    
    if debug:
        error_msg += f"\n[DEBUG] Waited {timeout_s}s without file stabilizing"
    
    raise RuntimeError(error_msg)
