from __future__ import annotations
from flaas.osc_rpc import OscTarget, request_once


def inspect_selected_track(
    target: OscTarget = OscTarget(),
    timeout_sec: float = 5.0,
    raw: bool = False,
) -> None:
    """
    Print device list for the currently selected track in Ableton.
    
    Queries:
    - /live/view/get/selected_track → (track_id,)
    - /live/track/get/num_devices → (track_id, num_devices)
    - /live/track/get/devices/name → (track_id, name0, name1, ...)
    - /live/track/get/devices/class_name → (track_id, class0, class1, ...)
    
    Outputs formatted table or raw tuples if raw=True.
    """
    sel = request_once(target, "/live/view/get/selected_track", [], timeout_sec=timeout_sec)
    track_id = int(sel[0])
    
    if raw:
        print(f"selected_track: {sel}")
    
    nd = request_once(target, "/live/track/get/num_devices", [track_id], timeout_sec=timeout_sec)
    num_devices = int(nd[1])
    
    names = request_once(target, "/live/track/get/devices/name", [track_id], timeout_sec=timeout_sec)
    classes = request_once(target, "/live/track/get/devices/class_name", [track_id], timeout_sec=timeout_sec)
    
    if raw:
        print(f"num_devices: {nd}")
        print(f"device_names: {names}")
        print(f"device_classes: {classes}")
        return
    
    device_names = list(names[1:]) if len(names) > 1 else []
    device_classes = list(classes[1:]) if len(classes) > 1 else []
    
    print(f"track_id={track_id} num_devices={num_devices}")
    print()
    
    for i in range(num_devices):
        name = device_names[i] if i < len(device_names) else "?"
        cls = device_classes[i] if i < len(device_classes) else "?"
        print(f"{i:2d}  name={str(name):30s}  class={cls}")
