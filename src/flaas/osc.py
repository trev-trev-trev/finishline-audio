from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from pythonosc.udp_client import SimpleUDPClient

@dataclass(frozen=True)
class OscTarget:
    host: str = "127.0.0.1"
    port: int = 11000

def send_ping(target: OscTarget, address: str = "/live/test", value: Any = "ok") -> None:
    client = SimpleUDPClient(target.host, target.port)
    client.send_message(address, value)
