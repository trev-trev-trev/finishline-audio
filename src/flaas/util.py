from __future__ import annotations
from pythonosc.udp_client import SimpleUDPClient
from flaas.osc_rpc import OscTarget

UTILITY_GAIN_PARAM_ID = 9  # Utility "Gain" parameter id (index in names[2:])

def set_utility_gain_norm(track_id: int, device_id: int, gain_norm_0_1: float, target: OscTarget = OscTarget()) -> None:
    v = float(max(0.0, min(1.0, gain_norm_0_1)))
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID, v])
