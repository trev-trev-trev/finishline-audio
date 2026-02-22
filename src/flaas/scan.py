from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone

from flaas.osc_rpc import OscTarget, request_once

@dataclass
class DeviceInfo:
    index: int
    name: str
    class_name: str

@dataclass
class TrackInfo:
    track_id: int
    name: str
    num_devices: int
    devices: list[DeviceInfo]

@dataclass
class ScanResult:
    ok: bool
    note: str
    created_at_utc: str
    num_tracks: int
    tracks: list[TrackInfo]
    fingerprint: str

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def scan_live(target: OscTarget = OscTarget(), timeout_sec: float = 2.0, track_ids: list[int] | None = None) -> ScanResult:
    """
    Scan Live set for track/device information.
    
    Args:
        target: OSC target
        timeout_sec: RPC timeout
        track_ids: Optional list of specific track IDs to scan. If None, scans all tracks.
    """
    num_tracks = int(request_once(target, "/live/song/get/num_tracks", None, timeout_sec=timeout_sec)[0])
    
    if track_ids is None:
        # Full scan
        names = request_once(target, "/live/song/get/track_names", [], timeout_sec=timeout_sec)
        track_names = list(names)[:num_tracks]
        tracks_to_scan = list(enumerate(track_names))
    else:
        # Targeted scan - get names only for requested tracks
        tracks_to_scan = []
        for tid in track_ids:
            if tid >= num_tracks:
                continue
            # Get individual track name
            name_resp = request_once(target, "/live/track/get/name", [tid], timeout_sec=timeout_sec)
            tname = name_resp[1] if len(name_resp) > 1 else f"Track {tid}"
            tracks_to_scan.append((tid, tname))

    tracks: list[TrackInfo] = []
    fp_parts: list[str] = []

    for tid, tname in tracks_to_scan:
        nd = request_once(target, "/live/track/get/num_devices", [tid], timeout_sec=timeout_sec)
        # response: (track_id, num_devices)
        num_devices = int(nd[1]) if len(nd) > 1 else 0

        dn = request_once(target, "/live/track/get/devices/name", [tid], timeout_sec=timeout_sec)
        dc = request_once(target, "/live/track/get/devices/class_name", [tid], timeout_sec=timeout_sec)

        # responses include track_id first
        dev_names = list(dn[1:]) if len(dn) > 1 else []
        dev_class = list(dc[1:]) if len(dc) > 1 else []

        devices: list[DeviceInfo] = []
        for i in range(min(len(dev_names), len(dev_class))):
            devices.append(DeviceInfo(index=i, name=str(dev_names[i]), class_name=str(dev_class[i])))

        tracks.append(TrackInfo(track_id=tid, name=str(tname), num_devices=num_devices, devices=devices))
        fp_parts.append(f"{tid}:{tname}:{num_devices}:" + "|".join([d.class_name for d in devices]))

    fingerprint = _sha256(";".join(fp_parts))
    note = f"targeted scan ({len(tracks)} tracks)" if track_ids else "full scan"

    return ScanResult(
        ok=True,
        note=note,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        num_tracks=num_tracks if track_ids is None else len(tracks),
        tracks=tracks,
        fingerprint=fingerprint,
    )

def write_model_cache(path: str | Path = "data/caches/model_cache.json", track_ids: list[int] | None = None) -> Path:
    """
    Write model cache from Live scan.
    
    Args:
        path: Output file path
        track_ids: Optional list of specific track IDs to scan. If None, scans all tracks.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        payload = scan_live(track_ids=track_ids)
    except Exception as e:
        payload = ScanResult(
            ok=False,
            note=f"scan failed: {type(e).__name__}: {e}",
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            num_tracks=0,
            tracks=[],
            fingerprint="",
        )

    out.write_text(json.dumps(asdict(payload), indent=2) + "\n", encoding="utf-8")
    return out
