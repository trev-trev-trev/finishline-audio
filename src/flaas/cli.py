import argparse
from flaas.osc import OscTarget, send_ping

def main() -> None:
    p = argparse.ArgumentParser(prog="flaas")
    sub = p.add_subparsers(dest="cmd")

    p.add_argument("--version", action="store_true")

    ping = sub.add_parser("ping", help="Send /live/test ping to AbletonOSC")
    ping.add_argument("--host", default="127.0.0.1")
    ping.add_argument("--port", type=int, default=11000)

    args = p.parse_args()

    if args.version:
        print("0.0.1")
        return

    if args.cmd == "ping":
        send_ping(OscTarget(host=args.host, port=args.port))
        print("sent")
        return

    p.print_help()

if __name__ == "__main__":
    main()
