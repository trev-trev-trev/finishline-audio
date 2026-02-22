from __future__ import annotations
import queue
import threading
from dataclasses import dataclass
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

@dataclass(frozen=True)
class OscTarget:
    host: str = "127.0.0.1"
    port: int = 11000  # AbletonOSC listen port

def request_once(
    target: OscTarget,
    address: str,
    value: Any = 1,
    listen_port: int = 11001,  # AbletonOSC reply port
    timeout_sec: float = 2.0,
) -> tuple[Any, ...]:
    """
    Send one OSC message, wait for one reply on `listen_port`, then return reply args.
    """
    q: "queue.Queue[tuple[Any, ...]]" = queue.Queue()

    disp = Dispatcher()

    def _handler(_addr: str, *args: Any) -> None:
        q.put(tuple(args))

    disp.map(address, _handler)

    server = ThreadingOSCUDPServer(("0.0.0.0", listen_port), disp)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    client = SimpleUDPClient(target.host, target.port)
    client.send_message(address, value)

    try:
        args = q.get(timeout=timeout_sec)
    except queue.Empty as e:
        server.shutdown()
        server.server_close()
        raise TimeoutError(f"Timed out waiting for reply on :{listen_port} for {address}") from e

    server.shutdown()
    server.server_close()
    return args
