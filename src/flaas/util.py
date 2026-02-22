from __future__ import annotations
from pythonosc.udp_client import SimpleUDPClient
from flaas.osc_rpc import OscTarget

def set_utility_gain_db(track_id: int, device_id: int, gain_db: float, target: OscTarget = OscTarget()) -> None:
    """
    AbletonOSC: /live/device/set/parameter/value <track_id> <device_id> <param_id> <value>
    For Utility (class StereoGain), Gain is typically parameter 0.
    """
    client = SimpleUDPClient(target.host, target.port)
    client.send_message("/live/device/set/parameter/value", [track_id, device_id, 0, float(gain_db)])
