# Unique Lines: Imports

**Total unique lines**: 41

---

## Line: `from __future__ import annotations`

**Occurrences**: 15

- `src/flaas/actions.py:1`
- `src/flaas/analyze.py:1`
- `src/flaas/apply.py:1`
- `src/flaas/audio_io.py:1`
- `src/flaas/check.py:1`
- `src/flaas/loop.py:1`
- `src/flaas/osc.py:1`
- `src/flaas/osc_rpc.py:1`
- `src/flaas/param_map.py:1`
- `src/flaas/plan.py:1`
- `src/flaas/scan.py:1`
- `src/flaas/targets.py:1`
- `src/flaas/util.py:1`
- `src/flaas/verify.py:1`
- `src/flaas/verify_audio.py:1`

## Line: `from dataclasses import dataclass`

**Occurrences**: 7

- `src/flaas/apply.py:3`
- `src/flaas/audio_io.py:2`
- `src/flaas/osc.py:2`
- `src/flaas/osc_rpc.py:4`
- `src/flaas/param_map.py:2`
- `src/flaas/plan.py:2`
- `src/flaas/targets.py:2`

## Line: `from dataclasses import dataclass, asdict`

**Occurrences**: 4

- `src/flaas/actions.py:3`
- `src/flaas/analyze.py:3`
- `src/flaas/check.py:3`
- `src/flaas/scan.py:4`

## Line: `from datetime import datetime, timezone`

**Occurrences**: 3

- `src/flaas/actions.py:5`
- `src/flaas/analyze.py:5`
- `src/flaas/scan.py:6`

## Line: `from flaas.actions import GainAction, write_actions`

**Occurrences**: 1

- `src/flaas/plan.py:7`

## Line: `from flaas.analyze import analyze_wav`

**Occurrences**: 4

- `src/flaas/check.py:5`
- `src/flaas/loop.py:4`
- `src/flaas/plan.py:5`
- `src/flaas/verify_audio.py:3`

## Line: `from flaas.analyze import write_analysis`

**Occurrences**: 1

- `src/flaas/cli.py:6`

## Line: `from flaas.apply import apply_actions_dry_run, apply_actions_osc`

**Occurrences**: 1

- `src/flaas/cli.py:9`

## Line: `from flaas.apply import apply_actions_osc, apply_actions_dry_run`

**Occurrences**: 1

- `src/flaas/loop.py:6`

## Line: `from flaas.audio_io import read_audio_info, read_mono_float`

**Occurrences**: 1

- `src/flaas/analyze.py:9`

## Line: `from flaas.check import check_wav`

**Occurrences**: 1

- `src/flaas/verify_audio.py:4`

## Line: `from flaas.check import write_check`

**Occurrences**: 1

- `src/flaas/cli.py:7`

## Line: `from flaas.export_guide import print_export_guide`

**Occurrences**: 1

- `src/flaas/cli.py:13`

## Line: `from flaas.loop import run_loop`

**Occurrences**: 1

- `src/flaas/cli.py:11`

## Line: `from flaas.osc import OscTarget as FireAndForgetTarget, send_ping`

**Occurrences**: 1

- `src/flaas/cli.py:3`

## Line: `from flaas.osc_rpc import OscTarget`

**Occurrences**: 1

- `src/flaas/util.py:3`

## Line: `from flaas.osc_rpc import OscTarget as RpcTarget, request_once`

**Occurrences**: 1

- `src/flaas/cli.py:4`

## Line: `from flaas.osc_rpc import OscTarget, request_once`

**Occurrences**: 5

- `src/flaas/apply.py:7`
- `src/flaas/param_map.py:3`
- `src/flaas/plan.py:9`
- `src/flaas/scan.py:8`
- `src/flaas/verify.py:2`

## Line: `from flaas.param_map import get_param_range`

**Occurrences**: 1

- `src/flaas/plan.py:10`

## Line: `from flaas.param_map import get_param_range, linear_to_norm`

**Occurrences**: 2

- `src/flaas/apply.py:8`
- `src/flaas/util.py:4`

## Line: `from flaas.plan import write_plan_gain_actions`

**Occurrences**: 2

- `src/flaas/cli.py:8`
- `src/flaas/loop.py:5`

## Line: `from flaas.scan import scan_live`

**Occurrences**: 2

- `src/flaas/apply.py:9`
- `src/flaas/plan.py:8`

## Line: `from flaas.scan import write_model_cache`

**Occurrences**: 1

- `src/flaas/cli.py:5`

## Line: `from flaas.targets import Targets, DEFAULT_TARGETS`

**Occurrences**: 2

- `src/flaas/check.py:6`
- `src/flaas/plan.py:6`

## Line: `from flaas.util import set_utility_gain_norm, set_utility_gain_linear`

**Occurrences**: 1

- `src/flaas/cli.py:10`

## Line: `from flaas.verify import verify_master_utility_gain`

**Occurrences**: 2

- `src/flaas/cli.py:12`
- `src/flaas/loop.py:7`

## Line: `from flaas.verify_audio import verify_audio`

**Occurrences**: 1

- `src/flaas/cli.py:14`

## Line: `from pathlib import Path`

**Occurrences**: 9

- `src/flaas/actions.py:4`
- `src/flaas/analyze.py:4`
- `src/flaas/apply.py:4`
- `src/flaas/audio_io.py:3`
- `src/flaas/check.py:4`
- `src/flaas/loop.py:2`
- `src/flaas/plan.py:3`
- `src/flaas/scan.py:5`
- `src/flaas/verify_audio.py:2`

## Line: `from pythonosc.dispatcher import Dispatcher`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:7`

## Line: `from pythonosc.osc_server import ThreadingOSCUDPServer`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:8`

## Line: `from pythonosc.udp_client import SimpleUDPClient`

**Occurrences**: 4

- `src/flaas/apply.py:5`
- `src/flaas/osc.py:4`
- `src/flaas/osc_rpc.py:9`
- `src/flaas/util.py:2`

## Line: `from typing import Any`

**Occurrences**: 2

- `src/flaas/osc.py:3`
- `src/flaas/osc_rpc.py:5`

## Line: `from typing import Optional`

**Occurrences**: 1

- `src/flaas/actions.py:6`

## Line: `import argparse`

**Occurrences**: 1

- `src/flaas/cli.py:1`

## Line: `import hashlib`

**Occurrences**: 1

- `src/flaas/scan.py:3`

## Line: `import json`

**Occurrences**: 5

- `src/flaas/actions.py:2`
- `src/flaas/analyze.py:2`
- `src/flaas/apply.py:2`
- `src/flaas/check.py:2`
- `src/flaas/scan.py:2`

## Line: `import numpy as np`

**Occurrences**: 2

- `src/flaas/analyze.py:6`
- `src/flaas/audio_io.py:5`

## Line: `import pyloudnorm as pyln`

**Occurrences**: 1

- `src/flaas/analyze.py:7`

## Line: `import queue`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:2`

## Line: `import soundfile as sf`

**Occurrences**: 1

- `src/flaas/audio_io.py:4`

## Line: `import threading`

**Occurrences**: 1

- `src/flaas/osc_rpc.py:3`

