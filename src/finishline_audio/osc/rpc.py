from __future__ import annotations
import threading
import time
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Any, Tuple

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

@dataclass(frozen=True)
class OscConfig:
    host: str
    port_in: int
    port_out: int
    timeout_s: float = 1.0
    retries: int = 2

class OscRpc:
    """Minimal request/response OSC helper for AbletonOSC.

    AbletonOSC listens on port_in and replies to port_out.
    """
    def __init__(self, cfg: OscConfig):
        self.cfg = cfg
        self.client = udp_client.SimpleUDPClient(cfg.host, cfg.port_in)
        self._q: "Queue[Tuple[str, Tuple[Any, ...]]]" = Queue()
        self._server: ThreadingOSCUDPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        disp = Dispatcher()
        disp.set_default_handler(self._on_msg)
        self._server = ThreadingOSCUDPServer(("0.0.0.0", self.cfg.port_out), disp)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()

    def _on_msg(self, address: str, *args: Any) -> None:
        self._q.put((address, args))

    def call(self, address: str, *args: Any, expect: str | None = None) -> Tuple[Any, ...]:
        expect_addr = expect or address
        last_err: Exception | None = None

        for _ in range(self.cfg.retries + 1):
            self.client.send_message(address, list(args))
            t0 = time.time()

            while (time.time() - t0) < self.cfg.timeout_s:
                try:
                    addr, a = self._q.get(timeout=0.05)
                except Empty:
                    continue
                if addr == expect_addr:
                    return a

            last_err = TimeoutError(f"OSC timeout waiting for {expect_addr}")

        raise last_err  # type: ignore[misc]
