from __future__ import annotations
import os
import time
import subprocess
from pathlib import Path


def auto_export_wav(out_path: Path, timeout_s: int = 600) -> None:
    """
    Automatically export WAV from Ableton Live using macOS UI automation.
    
    Requires:
    - Ableton Live running with project open
    - macOS Accessibility permissions for Terminal (System Settings → Privacy & Security)
    - Ableton export defaults already configured (Rendered Track, Normalize, Loop/Selection)
    
    Raises:
    - RuntimeError: On AppleScript errors or file timeout
    """
    # Remove existing file if present
    if out_path.exists():
        out_path.unlink()
    
    out_dir = str(out_path.parent.absolute())
    out_name = out_path.name
    
    # AppleScript to drive Ableton's Export dialog
    applescript = f"""
on run argv
  set outDir to "{out_dir}"
  set outName to "{out_name}"

  tell application "System Events"
    -- Find Ableton Live process (any version)
    set abletonProcs to (name of processes whose bundle identifier starts with "com.ableton.live")
    if (count of abletonProcs) is 0 then
      error "Ableton Live not running"
    end if
    set abletonName to item 1 of abletonProcs

    tell process abletonName
      set frontmost to true
      delay 0.2

      -- Open Export Audio/Video (Cmd+Shift+R)
      keystroke "r" using {{command down, shift down}}
      delay 0.5

      -- Confirm Export (Return) -> opens Save dialog
      key code 36
      delay 0.7

      -- Go to folder (Cmd+Shift+G)
      keystroke "g" using {{command down, shift down}}
      delay 0.3
      
      -- Type directory path
      keystroke outDir
      delay 0.2
      
      -- Confirm folder (Return)
      key code 36
      delay 0.4

      -- Select filename field and replace (Cmd+A then type)
      keystroke "a" using {{command down}}
      delay 0.1
      keystroke outName
      delay 0.2
      
      -- Save (Return)
      key code 36
      delay 0.3

      -- Confirm overwrite if prompted (Return again)
      key code 36
    end tell
  end tell
end run
"""
    
    # Run AppleScript
    result = subprocess.run(
        ["osascript", "-"],
        input=applescript,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    if result.returncode != 0:
        error_msg = result.stderr.strip() if result.stderr else "Unknown AppleScript error"
        raise RuntimeError(f"AppleScript export trigger failed: {error_msg}")
    
    # Wait for file to appear and stabilize
    start_time = time.time()
    last_size = -1
    last_mtime = -1
    stable_checks = 0
    
    while time.time() - start_time < timeout_s:
        if not out_path.exists():
            time.sleep(0.5)
            continue
        
        try:
            stat = out_path.stat()
            current_size = stat.st_size
            current_mtime = stat.st_mtime
            
            # Check if size and mtime are stable
            if current_size == last_size and current_mtime == last_mtime and current_size > 0:
                stable_checks += 1
                if stable_checks >= 2:  # 2 consecutive stable checks (1s apart)
                    # File is ready
                    return
            else:
                stable_checks = 0
                last_size = current_size
                last_mtime = current_mtime
            
            time.sleep(0.5)
            
        except OSError:
            # File appeared but not readable yet
            time.sleep(0.5)
            continue
    
    # Timeout
    if out_path.exists():
        raise RuntimeError(f"File appeared but did not stabilize within {timeout_s}s: {out_path}")
    else:
        raise RuntimeError(f"File did not appear within {timeout_s}s: {out_path}")
