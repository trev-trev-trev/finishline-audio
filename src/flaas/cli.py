import argparse
import sys

from flaas.version import FLAAS_VERSION, ABLETONOSC_VERSION_EXPECTED
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
from flaas.device_param_info import device_param_info
from flaas.eq8_map import generate_eq8_map
from flaas.eq8_set import eq8_set
from flaas.eq8_reset_gains import eq8_reset_gains
from flaas.device_map import generate_device_map
from flaas.limiter_set import limiter_set
from flaas.device_set_safe_param import device_set_safe_param

def main() -> None:
    p = argparse.ArgumentParser(prog="flaas")
    sub = p.add_subparsers(dest="cmd")

    p.add_argument("--version", action="store_true", help=f"Show version ({FLAAS_VERSION})")

    ping = sub.add_parser("ping", help="Ping AbletonOSC via /live/test")
    ping.add_argument("--host", default="127.0.0.1")
    ping.add_argument("--port", type=int, default=11000)
    ping.add_argument("--wait", action="store_true", help="Wait for /live/test reply on 11001")
    ping.add_argument("--listen-port", type=int, default=11001)
    ping.add_argument("--timeout", type=float, default=2.0)
    ping.add_argument("--arg", default="ok", help="Argument sent to /live/test (default: ok)")

    scan = sub.add_parser("scan", help="Scan Live set and write model cache")
    scan.add_argument("--out", default="data/caches/model_cache.json")
    scan.add_argument("--tracks", type=int, nargs='+', help="Scan only specific track IDs (e.g., --tracks 41)")
    scan.add_argument("--devices", action="store_true", help="Include device information (default: true)")


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
    vf.add_argument("--track-id", type=int, default=None, help="Track ID (defaults to master track -1000)")
    vf.add_argument("--device-id", type=int, default=None, help="Device ID (defaults to dynamically resolved Utility)")
    vf.add_argument("--host", default="127.0.0.1")
    vf.add_argument("--port", type=int, default=11000)

    rs = sub.add_parser("reset", help="Reset master Utility gain to center")
    rs.add_argument("--host", default="127.0.0.1")
    rs.add_argument("--port", type=int, default=11000)

    eg = sub.add_parser("export-guide", help="Print Ableton export settings (manual MVP)")
    
    rv = sub.add_parser("remote-version", help="Get AbletonOSC remote script version")
    rv.add_argument("--host", default="127.0.0.1")
    rv.add_argument("--port", type=int, default=11000)
    rv.add_argument("--timeout", type=float, default=2.0)

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

    dpi = sub.add_parser("device-param-info", help="Show single parameter metadata")
    dpi.add_argument("track_id", type=int, help="Track index")
    dpi.add_argument("device_id", type=int, help="Device index")
    dpi.add_argument("--param-id", type=int, required=True, help="Parameter index")
    dpi.add_argument("--timeout", type=float, default=5.0)
    dpi.add_argument("--raw", action="store_true", help="Print raw OSC tuples")
    dpi.add_argument("--host", default="127.0.0.1")
    dpi.add_argument("--port", type=int, default=11000)

    eq8m = sub.add_parser("eq8-map", help="Generate EQ Eight parameter map as JSON")
    eq8m.add_argument("track_id", type=int, help="Track index")
    eq8m.add_argument("device_id", type=int, help="Device index")
    eq8m.add_argument("--timeout", type=float, default=5.0)
    eq8m.add_argument("--host", default="127.0.0.1")
    eq8m.add_argument("--port", type=int, default=11000)

    eq8s = sub.add_parser("eq8-set", help="Set EQ Eight param by semantic name (requires eq8-map)")
    eq8s.add_argument("track_id", type=int, help="Track index")
    eq8s.add_argument("device_id", type=int, help="Device index")
    eq8s.add_argument("--band", type=int, required=True, help="Band number (1-8)")
    eq8s.add_argument("--side", choices=["A", "B"], required=True, help="Side A or B")
    eq8s.add_argument("--param", choices=["on", "type", "freq", "gain", "res"], required=True, help="Parameter name")
    eq8s.add_argument("--value", type=float, required=True, help="Parameter value")
    eq8s.add_argument("--timeout", type=float, default=5.0)
    eq8s.add_argument("--dry", action="store_true", help="Preview only, no write")
    eq8s.add_argument("--host", default="127.0.0.1")
    eq8s.add_argument("--port", type=int, default=11000)

    eq8r = sub.add_parser("eq8-reset-gains", help="Reset all EQ Eight band gains to 0 dB (requires eq8-map)")
    eq8r.add_argument("track_id", type=int, help="Track index")
    eq8r.add_argument("device_id", type=int, help="Device index")
    eq8r.add_argument("--timeout", type=float, default=5.0)
    eq8r.add_argument("--dry", action="store_true", help="Preview only, no write")
    eq8r.add_argument("--host", default="127.0.0.1")
    eq8r.add_argument("--port", type=int, default=11000)

    dm = sub.add_parser("device-map", help="Generate generic device parameter map as JSON")
    dm.add_argument("track_id", type=int, help="Track index")
    dm.add_argument("device_id", type=int, help="Device index")
    dm.add_argument("--timeout", type=float, default=5.0)
    dm.add_argument("--host", default="127.0.0.1")
    dm.add_argument("--port", type=int, default=11000)

    lim = sub.add_parser("limiter-set", help="Set Limiter param by semantic name (requires device-map)")
    lim.add_argument("track_id", type=int, help="Track index")
    lim.add_argument("device_id", type=int, help="Device index")
    lim.add_argument("--param", choices=["gain", "ceiling", "release", "auto", "link", "lookahead"], required=True, help="Parameter name")
    lim.add_argument("--value", type=float, required=True, help="Parameter value")
    lim.add_argument("--timeout", type=float, default=5.0)
    lim.add_argument("--dry", action="store_true", help="Preview only, no write")
    lim.add_argument("--host", default="127.0.0.1")
    lim.add_argument("--port", type=int, default=11000)

    dsp = sub.add_parser("device-set-safe-param", help="Set safe parameter on plugin device, verify, and revert (smoke test)")
    dsp.add_argument("track_id", type=int, help="Track index")
    dsp.add_argument("device_id", type=int, help="Device index")
    dsp.add_argument("--timeout", type=float, default=5.0)
    dsp.add_argument("--host", default="127.0.0.1")
    dsp.add_argument("--port", type=int, default=11000)

    args = p.parse_args()

    if args.version:
        print(f"flaas {FLAAS_VERSION}")
        print(f"Expected AbletonOSC version: {ABLETONOSC_VERSION_EXPECTED}")
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
        track_ids = args.tracks if hasattr(args, 'tracks') and args.tracks else None
        path = write_model_cache(args.out, track_ids=track_ids)
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
        val = verify_master_utility_gain(
            track_id=args.track_id,
            device_id=args.device_id,
            target=RpcTarget(host=args.host, port=args.port)
        )
        print(f"{val:.6f}")
        return

    if args.cmd == "reset":
        set_utility_gain_norm(0, 0, 0.5, target=RpcTarget(host=args.host, port=args.port))
        print("sent")
        return

    if args.cmd == "export-guide":
        print_export_guide()
        return
    
    if args.cmd == "remote-version":
        target = RpcTarget(host=args.host, port=args.port)
        version = None
        # Try /live namespace first, then fallback
        for addr in ("/live/flaas/version", "/flaas/version"):
            try:
                version = request_once(target, addr, [], timeout_sec=args.timeout)
                break
            except TimeoutError:
                continue
        
        if version is None:
            print("ERROR: Could not get remote version (tried /live/flaas/version and /flaas/version)", file=sys.stderr)
            raise SystemExit(1)
        
        remote_ver = version[0]
        print(f"remote_version={remote_ver}")
        
        # Check version match
        if remote_ver != ABLETONOSC_VERSION_EXPECTED:
            print(f"WARNING: Version mismatch!", file=sys.stderr)
            print(f"  Remote: {remote_ver}", file=sys.stderr)
            print(f"  Expected: {ABLETONOSC_VERSION_EXPECTED}", file=sys.stderr)
            raise SystemExit(1)
        
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

    if args.cmd == "device-param-info":
        device_param_info(track_id=args.track_id, device_id=args.device_id, param_id=args.param_id, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, raw=args.raw)
        return

    if args.cmd == "eq8-map":
        path = generate_eq8_map(track_id=args.track_id, device_id=args.device_id, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout)
        import json
        data = json.load(open(path))
        missing_count = len(data["groups"].get("missing", []))
        print(f"WROTE {path} (params={len(data['params'])} missing={missing_count})")
        return

    if args.cmd == "eq8-set":
        eq8_set(track_id=args.track_id, device_id=args.device_id, band=args.band, side=args.side, param=args.param, value=args.value, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, dry=args.dry)
        return

    if args.cmd == "eq8-reset-gains":
        eq8_reset_gains(track_id=args.track_id, device_id=args.device_id, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, dry=args.dry)
        return

    if args.cmd == "device-map":
        path = generate_device_map(track_id=args.track_id, device_id=args.device_id, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout)
        import json
        data = json.load(open(path))
        print(f"WROTE {path} (class={data['device_class_name']} params={len(data['params'])})")
        return

    if args.cmd == "device-set-safe-param":
        target = RpcTarget(host=args.host, port=args.port)
        exit_code = device_set_safe_param(
            args.track_id,
            args.device_id,
            target,
            timeout_sec=args.timeout,
        )
        raise SystemExit(exit_code)

    if args.cmd == "limiter-set":
        limiter_set(track_id=args.track_id, device_id=args.device_id, param=args.param, value=args.value, target=RpcTarget(host=args.host, port=args.port), timeout_sec=args.timeout, dry=args.dry)
        return

    p.print_help()

if __name__ == "__main__":
    main()
