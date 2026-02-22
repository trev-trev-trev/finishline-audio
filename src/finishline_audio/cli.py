from __future__ import annotations
import argparse
import sys

from finishline_audio.config import load_config
from finishline_audio.osc.rpc import OscRpc, OscConfig
from finishline_audio.ableton.api import AbletonApi

def _make_api():
    cfg = load_config().ableton
    rpc = OscRpc(OscConfig(
        host=cfg.host,
        port_in=cfg.port_in,
        port_out=cfg.port_out,
        timeout_s=cfg.timeout_s,
        retries=cfg.retries,
    ))
    rpc.start()
    return rpc, AbletonApi(rpc=rpc)

def cmd_ping(_args) -> int:
    rpc, api = _make_api()
    try:
        resp = api.test()
        print("OK", resp)
        return 0
    except Exception as e:
        print("PING_FAILED", repr(e))
        return 2
    finally:
        rpc.stop()

def cmd_tracks(_args) -> int:
    rpc, api = _make_api()
    try:
        names = api.track_names()
        for i, n in enumerate(names):
            print(f"{i}: {n}")
        return 0
    except Exception as e:
        print("TRACKS_FAILED", repr(e))
        return 2
    finally:
        rpc.stop()

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="finishline-audio")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping").set_defaults(fn=cmd_ping)
    sub.add_parser("tracks").set_defaults(fn=cmd_tracks)

    args = p.parse_args(argv)
    return int(args.fn(args))

if __name__ == "__main__":
    raise SystemExit(main())
