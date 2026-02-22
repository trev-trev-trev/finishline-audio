from __future__ import annotations
from pythonosc.udp_client import SimpleUDPClient
from flaas.osc_rpc import OscTarget

UTILITY_GAIN_PARAM_ID = 9  # confirmed via /live/device/get/parameters/name (index in names[2:])

def set_utility_gain_db(track_id: int, device_id: int, gain_db: float, target: OscTarget = OscTarget()) -> None:
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, UTILITY_GAIN_PARAM_ID, float(gain_db)])
