import argparse

from flaas.osc import OscTarget as FireAndForgetTarget, send_ping
from flaas.osc_rpc import OscTarget as RpcTarget, request_once
from flaas.scan import write_model_cache
from flaas.analyze import write_analysis
from flaas.check import write_check
from flaas.plan import write_plan_gain_actions
from flaas.apply import apply_actions_dry_run, apply_actions_osc
from flaas.util import set_utility_gain_norm, set_utility_gain_linear
from flaas.loop import run_loop
from flaas.verify import verify_master_utility_gain
from flaas.export_guide import print_export_guide
from flaas.verify_audio import verify_audio
from flaas.inspect_selected_device import inspect_selected_device
from flaas.eq8_set_param import eq8_set_param
from flaas.inspect_selected_track import inspect_selected_track
from flaas.device_set_param import device_set_param

def main() -> None:
    p = argparse.ArgumentParser(prog="flaas")
    sub = p.add_subparsers(dest="cmd")

    p.add_argument("--version", action="store_true")

    ping = sub.add_parser("ping", help="Ping AbletonOSC via /live/test")
    ping.add_argument("--host", default="127.0.0.1")
    ping.add_argument("--port", type=int, default=11000)
    ping.add_argument("--wait", action="store_true", help="Wait for /live/test reply on 11001")
    ping.add_argument("--listen-port", type=int, default=11001)
    ping.add_argument("--timeout", type=float, default=2.0)
    ping.add_argument("--arg", default="ok", help="Argument sent to /live/test (default: ok)")

    scan = sub.add_parser("scan", help="Write model_cache.json (stub for now)")
    scan.add_argument("--out", default="data/caches/model_cache.json")

    analyze = sub.add_parser("analyze", help="Analyze a WAV and write analysis.json")
    analyze.add_argument("wav")
    analyze.add_argument("--out", default="data/reports/analysis.json")

    check = sub.add_parser("check", help="Check WAV against compliance targets")
    check.add_argument("wav")
    check.add_argument("--out", default="data/reports/check.json")

    pg = sub.add_parser("plan-gain", help="Plan Utility gain action to hit LUFS target (writes actions.json)")
    pg.add_argument("wav")
    pg.add_argument("--out", default="data/actions/actions.json")

    ap = sub.add_parser("apply", help="Apply actions")
    ap.add_argument("--actions", default="data/actions/actions.json")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=11000)

    ugn = sub.add_parser("util-gain-norm", help="Set Utility Gain normalized 0..1")
    ugn.add_argument("track_id", type=int)
    ugn.add_argument("device_id", type=int)
    ugn.add_argument("gain_norm", type=float)
    ugn.add_argument("--host", default="127.0.0.1")
    ugn.add_argument("--port", type=int, default=11000)

    ugl = sub.add_parser("util-gain-linear", help="Set Utility Gain in exposed linear range (ex: -1..+1)")
    ugl.add_argument("track_id", type=int)
    ugl.add_argument("device_id", type=int)
    ugl.add_argument("gain_linear", type=float)
    ugl.add_argument("--host", default="127.0.0.1")
    ugl.add_argument("--port", type=int, default=11000)

    lp = sub.add_parser("loop", help="analyze -> plan-gain -> apply (manual export/verify)")
    lp.add_argument("wav")
    lp.add_argument("--dry", action="store_true")

    vf = sub.add_parser("verify", help="Read back master Utility gain normalized")
    vf.add_argument("--track-id", type=int, default=0)
    vf.add_argument("--device-id", type=int, default=0)
    vf.add_argument("--host", default="127.0.0.1")
    vf.add_argument("--port", type=int, default=11000)

    rs = sub.add_parser("reset", help="Reset master Utility gain to center")
    rs.add_argument("--host", default="127.0.0.1")
    rs.add_argument("--port", type=int, default=11000)

    eg = sub.add_parser("export-guide", help="Print Ableton export settings (manual MVP)")

    va = sub.add_parser("verify-audio", help="Analyze+check a WAV and print PASS/FAIL")
    va.add_argument("wav")

    isd = sub.add_parser("inspect-selected-device", help="Print full parameter table for selected device")
    isd.add_argument("--timeout", type=float, default=5.0)
    isd.add_argument("--raw", action="store_true", help="Print raw OSC tuples")
    isd.add_argument("--host", default="127.0.0.1")
    isd.add_argument("--port", type=int, default=11000)

    eq8 = sub.add_parser("eq8-set-param", help="Set any parameter on selected device (intended for EQ Eight)")
    eq8.add_argument("--param-id", type=int, required=True, help="Parameter index")
    eq8.add_argument("--value", type=float, required=True, help="Parameter value to set")
    eq8.add_argument("--timeout", type=float, default=5.0)
    eq8.add_argument("--dry", action="store_true", help="Preview only, no write")
    eq8.add_argument("--host", default="127.0.0.1")
    eq8.add_argument("--port", type=int, default=11000)

    ist = sub.add_parser("inspect-selected-track", help="Print device list for selected track")
    ist.add_argument("--timeout", type=float, default=5.0)
    ist.add_argument("--raw", action="store_true", help="Print raw OSC tuples")
    ist.add_argument("--host", default="127.0.0.1")
    ist.add_argument("--port", type=int, default=11000)

    dsp = sub.add_parser("device-set-param", help="Set any parameter on any device (generic)")
    dsp.add_argument("track_id", type=int, help="Track index")
    dsp.add_argument("device_id", type=int, help="Device index")
    dsp.add_argument("--param-id", type=int, required=True, help="Parameter index")
    dsp.add_argument("--value", type=float, required=True, help="Parameter value to set")
    dsp.add_argument("--timeout", type=float, default=5.0)
    dsp.add_argument("--dry", action="store_true", help="Preview only, no write")
    dsp.add_argument("--host", default="127.0.0.1")
    dsp.add_argument("--port", type=int, default=11000)

    args = p.parse_args()

    if args.version:
        print("0.0.2")
        return

    if args.cmd == "ping":
        if args.wait:
            resp = request_once(
                RpcTarget(host=args.host, port=args.port),
                "/live/test",
                args.arg,
                listen_port=args.listen_port,
                timeout_sec=args.timeout,
            )
            print(f"ok: {resp}")
        else:
            send_ping(FireAndForgetTarget(host=args.host, port=args.port), value=args.arg)
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

    if args.cmd == "check":
        out = write_check(args.wav, args.out)
        print(str(out))
        return

    if args.cmd == "plan-gain":
        out = write_plan_gain_actions(args.wav, args.out)
        print(str(out))
        return

    if args.cmd == "apply":
        if args.dry:
            apply_actions_dry_run(args.actions)
        else:
            apply_actions_osc(args.actions, target=RpcTarget(host=args.host, port=args.port))
        return

    if args.cmd == "util-gain-norm":
        set_utility_gain_norm(args.track_id, args.device_id, args.gain_norm, target=RpcTarget(host=args.host, port=args.port))
        print("sent")
        return

    if args.cmd == "util-gain-linear":
        set_utility_gain_linear(args.track_id, args.device_id, args.gain_linear, target=RpcTarget(host=args.host, port=args.port))
        print("sent")
        return

    if args.cmd == "loop":
        run_loop(args.wav, dry=args.dry)
        return

    if args.cmd == "verify":
        v = verify_master_utility_gain(args.track_id, args.device_id, target=RpcTarget(host=args.host, port=args.port))
        print(v)
        return

    if args.cmd == "reset":
        set_utility_gain_norm(0, 0, 0.5, target=RpcTarget(host=args.host, port=args.port))
        print("sent")
        return

    if args.cmd == "export-guide":
        print_export_guide()
        return

    if args.cmd == "verify-audio":
        raise SystemExit(verify_audio(args.wav))

    if args.cmd == "inspect-selected-device":
        inspect_selected_device(target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, raw=args.raw)
        return

    if args.cmd == "eq8-set-param":
        eq8_set_param(param_id=args.param_id, value=args.value, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, dry=args.dry)
        return

    if args.cmd == "inspect-selected-track":
        inspect_selected_track(target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, raw=args.raw)
        return

    if args.cmd == "device-set-param":
        device_set_param(track_id=args.track_id, device_id=args.device_id, param_id=args.param_id, value=args.value, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, dry=args.dry)
        return

    p.print_help()

if __name__ == "__main__":
    main()
