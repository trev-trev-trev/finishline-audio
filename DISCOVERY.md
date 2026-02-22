# ABLETON CONTROL DISCOVERY

**Goal**: Systematically expose all available Ableton controls via OSC → Python

**Philosophy**: Mirror Ableton's entire control surface in Python through exhaustive OSC endpoint mapping

---

## AVAILABLE OSC MODULES (AbletonOSC)

From `/Users/trev/Music/Ableton/User Library/Remote Scripts/AbletonOSC/abletonosc/`:

1. **application.py** - Application-level controls
2. **song.py** - Song/project controls
3. **track.py** - Track controls (regular, return, master)
4. **device.py** - Device/plugin controls
5. **clip.py** - Clip controls
6. **clip_slot.py** - Clip slot controls
7. **scene.py** - Scene controls
8. **view.py** - View/selection controls
9. **midimap.py** - MIDI mapping
10. **introspection.py** - Live API introspection

---

## HIERARCHICAL CONTROL STRUCTURE

```
Song (Global)
├── Tempo
├── Time signature
├── Loop
├── Arrangement position
├── Session record
└── MIDI recording quantization

Tracks (Regular, Return, Master)
├── Volume
├── Pan
├── Mute
├── Solo
├── Arm
├── Monitor state
├── Input/output routing
├── Send levels (to returns)
├── Track name
├── Track color
└── Devices (on track)

Devices (Audio/MIDI effects, Instruments)
├── Device on/off
├── Parameters (N per device)
│   ├── Name
│   ├── Value (normalized 0-1)
│   ├── Min/max
│   ├── Is quantized
│   └── Display string
├── Device name
├── Preset
└── Device chain

Clips
├── Name
├── Color
├── Length
├── Loop start/end
├── Warp mode
├── Pitch
├── Gain
├── Launch quantization
├── Clip slot state (has_clip, is_playing, is_triggered)
└── MIDI notes (for MIDI clips)

Scenes
├── Name
├── Color
├── Launch
└── Tempo

View/Selection
├── Selected track
├── Selected device
├── Selected scene
├── Selected clip slot
└── Highlighted clip slot

Application
├── Version
├── Tempo
├── Loop
├── Metronome
└── Global quantization
```

---

## DISCOVERY METHODOLOGY

### Phase 1: Enumerate All Endpoints (DONE)

**Approach**: Read each AbletonOSC `.py` module, extract all registered OSC addresses

**Executed**:
```bash
grep -r '/live/' "/Users/trev/Music/Ableton/User Library/Remote Scripts/AbletonOSC/abletonosc/" | grep -oE '/live/[a-z_/]+' | sort -u > data/discovery/all_osc_endpoints.txt
```

**Output**: 108 endpoint patterns discovered

**CRITICAL GAP IDENTIFIED**: Patterns are not specifications. Need full endpoint registry with:
- Exact address
- Arg types, ranges, examples
- Response shape and types
- Safety classification (read-only, write-safe, revertable)
- Critical quirks (indexing rules, selection requirements)

**See**: `docs/ENDPOINT_REGISTRY.json` for proper specification structure

### Phase 2: Categorize by Control Type

**Categories**:
1. **Get** (read-only query) - e.g., `/live/track/get/volume`
2. **Set** (write) - e.g., `/live/track/set/volume`
3. **Action** (trigger) - e.g., `/live/track/stop_all_clips`
4. **Observer** (callback/listener) - e.g., `/live/track/observe/name`

### Phase 3: Map to Python Commands

**For each endpoint**:
```python
# Example mapping
OSC: /live/track/get/volume [track_id]
Python: flaas track-get-volume <track_id>
File: src/flaas/track_volume.py
```

### Phase 4: Generate Bulk Commands

**Template**:
```bash
# Generate 100 track control commands
for endpoint in $(list_track_endpoints); do
  generate_python_command "$endpoint"
  generate_cli_parser "$endpoint"
  generate_test "$endpoint"
done
```

---

## PRIORITIZATION: SOLID WINS

### Tier 1: Universal Controls (Guaranteed Useful)

**Track Level** (per track, ~100 controls for 10 tracks):
- ✅ Volume (get/set) - DONE (via Utility device)
- Pan (get/set)
- Mute (get/set/toggle)
- Solo (get/set/toggle)
- Arm (get/set/toggle)
- Name (get/set)
- Color (get/set)
- Send levels (get/set, 1 per return track)

**Device Level** (per device, ~10-1000 params per device):
- ✅ Parameter value (get/set) - DONE (generic)
- ✅ Parameter info (name/min/max/quantized) - DONE
- Device on/off (get/set/toggle)
- Device preset (get/set/list)
- Device chain reorder

**Clip Level** (per clip slot):
- Clip name (get/set)
- Clip launch
- Clip stop
- Clip loop (get/set)
- Clip position (get/set)
- Has clip (get)
- Is playing (get)

**Song Level** (global, ~20 controls):
- ✅ Tempo (get/set) - Partial (application.py has it)
- Time signature (get/set)
- Loop (get/set/toggle)
- Arrangement position (get/set)
- Session record (get/set)
- Play/stop/continue
- Metronome (get/set/toggle)

### Tier 2: Workflow Accelerators

**Scene Level**:
- Scene launch
- Scene name/color
- Scene create/delete

**View Level**:
- ✅ Selected track (get/set) - DONE
- ✅ Selected device (get/set) - DONE
- Selected scene (get/set)
- Selected clip slot (get/set)

**Automation**:
- Write automation
- Delete automation
- Re-enable automation

### Tier 3: Advanced/Specialized

**MIDI**:
- MIDI map create/delete
- MIDI learn
- MIDI note input

**Audio routing**:
- Input routing (get/set)
- Output routing (get/set)
- Monitor state (get/set)

**Session/arrangement**:
- Arrangement overdub
- Session record fixed length
- Capture MIDI

---

## GENERATION STRATEGY

### Batch 1: Track Controls (100 commands)

**Per track control** × **N tracks** = comprehensive coverage

Example generation:
```python
# Generate for all track properties
TRACK_PROPS = ["volume", "pan", "mute", "solo", "arm", "name", "color"]
OPERATIONS = ["get", "set", "toggle"]  # where applicable

for prop in TRACK_PROPS:
    for op in applicable_ops(prop):
        generate_command(f"track-{op}-{prop}")
```

**Output**: `flaas track-get-volume`, `flaas track-set-mute`, etc.

### Batch 2: Device Controls (1000+ commands)

**Per device type**:
- Generic device controls (works for all)
- ✅ EQ Eight - DONE (8 bands × 5 params = 40 params)
- ✅ Limiter - DONE (6 params)
- Compressor (12 params)
- Reverb (20 params)
- Delay (15 params)
- etc.

**Approach**: Generate device-specific helpers for common devices

### Batch 3: Clip Controls (500 commands)

**Per clip property** × **Operations**:
```
clip-get-name
clip-set-name
clip-launch
clip-stop
clip-get-length
clip-set-length
clip-get-loop
clip-set-loop
...
```

### Batch 4: Song/Global Controls (50 commands)

```
song-get-tempo
song-set-tempo
song-play
song-stop
song-get-loop
song-set-loop
song-create-scene
song-delete-scene
...
```

---

## IMPLEMENTATION ROADMAP

### Step 1: Enumerate (1 hour)
Extract all OSC endpoints from AbletonOSC source

### Step 2: Generate Stubs (2 hours)
Create Python function stubs for all endpoints

### Step 3: Wire CLI (2 hours)
Add argparse entries for all commands

### Step 4: Test Matrix (4 hours)
Generate smoke tests for all commands

### Step 5: Document (1 hour)
Generate reference docs from code

**Total**: ~10 hours for 500-1000 commands

---

## AUTOMATION APPROACH

### Code Generation Template

```python
# generate_commands.py

OSC_ENDPOINTS = load_from_abletonosc_source()

for endpoint in OSC_ENDPOINTS:
    module_code = generate_python_module(endpoint)
    cli_code = generate_cli_parser(endpoint)
    test_code = generate_smoke_test(endpoint)
    
    write_file(f"src/flaas/{endpoint.name}.py", module_code)
    append_cli(f"src/flaas/cli.py", cli_code)
    append_test(f"scripts/run_smoke_tests.sh", test_code)
```

### Endpoint Extraction

```bash
# Extract all /live/* endpoints from AbletonOSC
rg '/live/\w+' "/Users/trev/Music/Ableton/User Library/Remote Scripts/AbletonOSC/" \
  -o -N | sort -u > data/discovery/all_osc_endpoints.txt
```

---

## NEXT ACTIONS (BLOCKED UNTIL EXPORT LOOP WORKS)

**BLOCKER**: Export crash prevents closed-loop audio iteration (`plan-gain → apply → export → verify-audio`)

**Must complete first**:
1. Fix export crash in Ableton (disable third-party plugins)
2. Validate gain adjustment via `flaas verify-audio output/master_iter1.wav`
3. Confirm export loop is stable and repeatable

**After export loop works**:
1. Populate `docs/ENDPOINT_REGISTRY.json` (top 50 endpoints with full specs)
2. Generate Python stubs from registry
3. Wire CLI parsers
4. Generate smoke tests
5. Scale to 500-1000 commands

**See**: `PRIORITY.md` for execution order correction

---

## SOLID WINS PRIORITY

**Tier 1** (do first, ~100 commands):
- All track controls (volume, pan, mute, solo, arm, name, color, sends)
- All song controls (tempo, time sig, loop, play/stop, transport)
- All clip controls (launch, stop, name, length, loop)

**Tier 2** (do second, ~200 commands):
- All scene controls (launch, name, color, create, delete)
- All view controls (selection get/set)
- Common device controls (on/off, preset)

**Tier 3** (do third, ~200+ commands):
- Advanced automation controls
- MIDI controls
- Audio routing controls

---

**Philosophy**: Copy Ableton shamelessly. If Ableton exposes it via OSC, we expose it via Python. Complete control surface mirror.

**End result**: `flaas` becomes comprehensive Ableton automation toolkit with 500-1000 commands covering every accessible control point.
