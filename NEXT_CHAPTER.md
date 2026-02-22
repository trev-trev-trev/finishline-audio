# NEXT CHAPTER: SYSTEMATIC CONTROL DISCOVERY

**Commit**: 7e401ff - Documentation consolidation complete

---

## WHAT WE HAVE NOW

✅ Master track control (plan-gain, apply, verify)  
✅ Generic device control (device-set-param, device-set-safe-param)  
✅ EQ Eight control (8 bands, all params)  
✅ Limiter control (6 params)  
✅ Three lanes smoke tests  
✅ Version checking  
✅ Consolidated documentation

**Current exposure**: ~15 commands, ~60 control points

---

## WHAT'S AVAILABLE (AbletonOSC)

**Discovered**: 108 unique OSC endpoint patterns  
**File**: `data/discovery/all_osc_endpoints.txt`

**Categories**:
- Application (version, CPU usage, etc.)
- Song (tempo, loop, transport, etc.)
- Track (volume, pan, mute, solo, arm, sends, etc.)
- Device (all params, presets, on/off, etc.)
- Clip (launch, stop, notes, properties, etc.)
- Clip slot (state, duplicate, etc.)
- Scene (launch, properties, etc.)
- View (selection, highlighted, etc.)

---

## THE GOAL

**Mirror Ableton's entire control surface in Python.**

Systematically expose ALL 108 endpoint patterns → 500-1000 individual commands

---

## THE STRATEGY

### 10 → 100 → 1000 Breakdown

**10 Major Goals**:
1. Track controls (volume, pan, mute, solo, arm, sends)
2. Song controls (tempo, transport, loop, arrangement)
3. Clip controls (launch, stop, properties, notes)
4. Device controls (presets, routing, chain)
5. Scene controls (launch, create, delete)
6. View controls (selection, highlight)
7. Automation controls (write, delete, re-enable)
8. MIDI controls (learn, map, input)
9. Audio routing (input, output, monitor)
10. Advanced (sync, grooves, browser)

**100 Sub-Goals**: Each major goal → 10 specific control groups

**1000 Tasks**: Each sub-goal → 10 actionable implementations

---

## EXECUTION APPROACH

### Terminal-Driven Discovery

```bash
# 1. Extract endpoint patterns
grep -r '/live/' AbletonOSC/ > all_endpoints.txt

# 2. Categorize by type
grep '/track/' all_endpoints.txt > track_endpoints.txt
grep '/device/' all_endpoints.txt > device_endpoints.txt
grep '/clip/' all_endpoints.txt > clip_endpoints.txt

# 3. Generate Python stubs
for endpoint in $(cat track_endpoints.txt); do
  generate_python_stub "$endpoint"
done

# 4. Wire CLI
for endpoint in $(cat track_endpoints.txt); do
  add_cli_parser "$endpoint"
done

# 5. Generate tests
for endpoint in $(cat track_endpoints.txt); do
  add_smoke_test "$endpoint"
done
```

### Budget-Conscious: Maximum Terminal Use

**Why**: Terminal feedback confirms success instantly (no guessing)  
**How**: Small batches, validate each, iterate  
**Result**: Reliable progress, zero wasted compute

---

## SOLID WINS (Priority Order)

### Batch 1: Track Controls (~50 commands)

**Per-track operations** (multiply by track count for full coverage):
```
track-get-volume <t>
track-set-volume <t> <val>
track-get-pan <t>
track-set-pan <t> <val>
track-get-mute <t>
track-set-mute <t> <bool>
track-toggle-mute <t>
track-get-solo <t>
track-set-solo <t> <bool>
track-toggle-solo <t>
track-get-arm <t>
track-set-arm <t> <bool>
track-toggle-arm <t>
track-get-name <t>
track-set-name <t> <str>
track-get-color <t>
track-set-color <t> <r> <g> <b>
track-get-send <t> <return_id>
track-set-send <t> <return_id> <val>
```

### Batch 2: Song Controls (~30 commands)

```
song-get-tempo
song-set-tempo <bpm>
song-play
song-stop
song-continue
song-get-loop
song-set-loop <bool>
song-get-loop-start
song-set-loop-start <bar>
song-get-loop-end
song-set-loop-end <bar>
song-get-metronome
song-set-metronome <bool>
song-get-time-signature
song-set-time-signature <num> <denom>
song-get-arrangement-position
song-set-arrangement-position <beats>
song-create-scene
song-delete-scene <idx>
song-duplicate-scene <idx>
```

### Batch 3: Clip Controls (~40 commands)

```
clip-launch <t> <c>
clip-stop <t> <c>
clip-get-name <t> <c>
clip-set-name <t> <c> <str>
clip-get-length <t> <c>
clip-set-length <t> <c> <beats>
clip-get-loop <t> <c>
clip-set-loop <t> <c> <bool>
clip-get-loop-start <t> <c>
clip-set-loop-start <t> <c> <beats>
clip-get-loop-end <t> <c>
clip-set-loop-end <t> <c> <beats>
clip-get-color <t> <c>
clip-set-color <t> <c> <idx>
clip-get-notes <t> <c>
clip-add-notes <t> <c> <notes_json>
clip-remove-notes <t> <c> <notes_json>
```

### Batch 4: Scene Controls (~15 commands)

```
scene-launch <idx>
scene-get-name <idx>
scene-set-name <idx> <str>
scene-get-color <idx>
scene-set-color <idx> <idx>
scene-create
scene-delete <idx>
scene-duplicate <idx>
```

### Batch 5: Device Expansion (~100 commands)

**Common devices** (generate specific helpers):
- Compressor (12 params)
- Gate (8 params)
- EQ Eight (40 params) ✅ DONE
- Limiter (6 params) ✅ DONE
- Reverb (20 params)
- Delay (15 params)
- Chorus (12 params)
- Phaser (10 params)
- Flanger (10 params)
- Auto Filter (15 params)
- Auto Pan (8 params)
- Saturator (10 params)

**Approach**: Generate `<device>-set` commands similar to existing `eq8-set` and `limiter-set`

---

## IMPLEMENTATION PHASES

### Phase 1: Enumerate (DONE)
- ✅ Extract 108 OSC endpoints from AbletonOSC
- ✅ Save to `data/discovery/all_osc_endpoints.txt`

### Phase 2: Generate Track Controls (Next)
- Create Python modules for all track operations
- Wire CLI parsers
- Generate smoke tests
- **Output**: ~50 commands, 100% track control coverage

### Phase 3: Generate Song Controls
- Song/transport operations
- **Output**: ~30 commands, global control

### Phase 4: Generate Clip Controls
- Clip launch, properties, MIDI notes
- **Output**: ~40 commands, session control

### Phase 5: Generate Scene Controls
- Scene operations
- **Output**: ~15 commands

### Phase 6: Expand Device Library
- Common device helpers (Compressor, Reverb, Delay, etc.)
- **Output**: ~100 commands, 10-20 devices

### Phase 7: Advanced Controls
- Automation, MIDI, routing
- **Output**: ~50 commands

**Total estimate**: 300-500 commands, comprehensive Ableton mirror

---

## TERMINAL-FIRST WORKFLOW

### Small Batches, Validate Each

```bash
# Generate 5 commands
./scripts/generate_commands.sh track-controls 5

# Test immediately
make write-fast

# If pass, generate 5 more
./scripts/generate_commands.sh track-controls 5

# Repeat until batch complete
```

### Why This Works

1. **Terminal feedback** confirms each batch works
2. **Small iterations** prevent compound failures
3. **Budget-friendly** - no wasted regeneration
4. **Reliable progress** - always have working state

---

## SUCCESS CRITERIA

**Comprehensive Ableton mirror achieved when**:
- ✅ 300+ commands generated
- ✅ 95%+ OSC endpoint coverage
- ✅ All smoke tests passing
- ✅ Documentation auto-generated
- ✅ Can control virtually any Ableton parameter from Python

**At that point**: Python layer == complete Ableton control surface

---

## NEXT IMMEDIATE ACTION

**Start Phase 2**: Generate track control commands

```bash
# Create generator script
./scripts/create_command_generator.sh

# Generate first batch: track volume controls
./scripts/generate_commands.sh track-volume

# Test
make write-fast

# Iterate
```

---

**This chapter**: Systematic discovery and exposure of ALL Ableton controls  
**End state**: Complete Python mirror of Ableton Live  
**Approach**: Terminal-driven, batch-validated, budget-conscious

Let's build.
