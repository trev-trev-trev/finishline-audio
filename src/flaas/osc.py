from __future__ import annotations
from dataclasses import dataclass
from pythonosc.udp_client import SimpleUDPClient

@dataclass(frozen=True)
class OscTarget:
    host: str = "127.0.0.1"
    port: int = 11000

def send_ping(target: OscTarget, address: str = "/live/test") -> None:
    """
    Fire-and-forget ping for AbletonOSC.
    Some AbletonOSC builds reply, some don't; MVP just sends.
    """
    client = SimpleUDPClient(target.host, target.port)
    client.send_message(address, 1)
