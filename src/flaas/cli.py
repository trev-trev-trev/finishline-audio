import argparse
from flaas.osc import OscTarget, send_ping
from flaas.scan import write_model_cache
from flaas.analyze import write_analysis

def main() -> None:
    p = argparse.ArgumentParser(prog="flaas")
    sub = p.add_subparsers(dest="cmd")

    p.add_argument("--version", action="store_true")

    ping = sub.add_parser("ping", help="Send /live/test ping to AbletonOSC")
    ping.add_argument("--host", default="127.0.0.1")
    ping.add_argument("--port", type=int, default=11000)

    scan = sub.add_parser("scan", help="Write model_cache.json (stub for now)")
    scan.add_argument("--out", default="data/caches/model_cache.json")

    analyze = sub.add_parser("analyze", help="Analyze a WAV and write analysis.json")
    analyze.add_argument("wav")
    analyze.add_argument("--out", default="data/reports/analysis.json")

    args = p.parse_args()

    if args.version:
        print("0.0.1")
        return

    if args.cmd == "ping":
        send_ping(OscTarget(host=args.host, port=args.port))
        print("sent")
        return

    if args.cmd == "scan":
        path = write_model_cache(args.out)
        print(str(path))
        return

    if args.cmd == "analyze":
        out = write_analysis(args.wav, args.out)
        print(str(out))
        return

    p.print_help()

if __name__ == "__main__":
    main()
