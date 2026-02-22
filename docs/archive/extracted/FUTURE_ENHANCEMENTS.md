# Future Enhancements

This document sequences features **beyond MVP** in logical order, maintaining consistency with the core philosophy.

**Core Philosophy Reminder:** Every enhancement must:
* Enforce consistency, not replace taste
* Produce explainable, logged outputs
* Keep creative parameters off-limits
* Make the album addressable at scale

---

## Phase 2: Enhanced Audio Automation

**When:** After MVP proves single-song automation works reliably.

### 2.1 Album-Level Consistency

**Problem:** MVP optimizes each song independently, can still yield inconsistency across album.

**Solution:** Compute album-level medians per stem role:

```python
# After analyzing all songs
album_stats = {
    "VOCAL_LEAD": {
        "median_lufs": -18.5,
        "median_brightness_ratio": 0.15,  # harsh-band/mid-band energy
        "median_mud_ratio": 0.12
    },
    "BASS": {
        "median_low_end_energy": 0.35
    }
}
```

Rules then apply **minimal correction toward album median**:
* If song's vocal brightness is 2 dB brighter than album median → apply small cut
* If bass low-end is 3 dB quieter than album median → apply small boost (exception to "no boosts" rule, gated by album context)

**Guardrails:**
* Max deviation correction: ±2 dB per song
* Only apply if deviation exceeds threshold (e.g., >1.5 dB)
* User reviews album stats before applying

**Deliverables:**
* `src/jobs/analyze_album_consistency.py`
* `data/profiles/album_median_profile.json`
* Report showing per-song deviation from median

---

### 2.2 Reference Profile System (Full)

**Problem:** MVP uses fixed thresholds. Real-world references might have different tonal balance.

**Solution:** Analyze 3-5 reference tracks, compute p25/p50/p75 band energy distributions.

```python
profile = {
    "name": "REFERENCE_SET_A",
    "tracks": ["ref1.wav", "ref2.wav", "ref3.wav"],
    "lufs": {"p25": -11.0, "median": -10.5, "p75": -9.8},
    "mud_ratio": {"p25": 0.10, "median": 0.12, "p75": 0.15},
    "harsh_burst_rate": {"p25": 0.05, "median": 0.08, "p75": 0.12}
}
```

Rules then use: "if song mud_ratio > ref_p75 + margin → cut"

**Guardrails:**
* Reference tracks must be mastered (not raw stems)
* Minimum 3 references required
* User confirms references match target aesthetic

**Deliverables:**
* `src/rules/profile.py` (full implementation)
* CLI: `python -m src.cli build-profile --refs refs/*.wav --name MY_REFS`

---

### 2.3 Programmatic Export from Live

**Problem:** MVP requires manual stem export, prone to human error.

**Solution:** Use AbletonOSC to:
1. Set export settings programmatically (normalization off, etc.)
2. Trigger render for each stem track
3. Verify exported file metadata (sample rate, bit depth)

**Challenges:**
* AbletonOSC export API is limited (may require Live's "Export Audio/Video" command trigger)
* Long-running export process (need to poll for completion)

**Deliverables:**
* `src/ableton/export.py`
* CLI: `python -m src.cli export --song SongName`
* Automatic verification of export settings via WAV header inspection

---

### 2.4 Section-Aware Analysis

**Problem:** MVP analyzes entire song as one block. Intro/verse/chorus have different density/energy.

**Solution:** Use Ableton locators/markers to segment song:

```json
{
  "sections": [
    {"name": "Intro", "start_sec": 0.0, "end_sec": 16.0},
    {"name": "Verse", "start_sec": 16.0, "end_sec": 48.0},
    {"name": "Chorus", "start_sec": 48.0, "end_sec": 80.0}
  ]
}
```

Analyze per-section:
* Different mud/harsh thresholds for sparse verse vs dense chorus
* Reverb tail detection only at section boundaries (prevent masking transitions)

**Guardrails:**
* Markers optional (fall back to full-song analysis)
* Max sections: 16 (prevent over-segmentation)

**Deliverables:**
* Extract markers via AbletonOSC: `/live/song/get/cue_points`
* `src/analysis/sections.py`
* Per-section reporting in `report.json`

---

### 2.5 Undo Mechanism

**Problem:** No way to reverse applied corrections without reloading Live set backup.

**Solution:** Store "pre-correction snapshot" of all modified parameters:

```json
{
  "song": "SongName",
  "snapshot_id": "pre_polish_2026_02_22_001",
  "params": [
    {"track": "VOCAL_LEAD", "device": "Utility", "param": "Gain", "original_value": 0.85}
  ]
}
```

**Deliverables:**
* `src/ableton/snapshot.py`
* CLI: `python -m src.cli undo --song SongName --snapshot <id>`
* Automatic snapshot before every apply

---

## Phase 3: Show Control & Visual Integration

**When:** After audio automation is production-stable (6+ songs processed successfully).

### 3.1 Beat-Synced Event Detection

**Problem:** Need to know **when** things happen in the song (impacts, drops, transitions) for visual sync.

**Solution:** Detect musical events from audio + timeline data:

* **Onset detection:** Transient spikes (kick hits, snare hits, impacts)
* **Energy drops:** Sudden RMS decrease (breakdown, filter sweep)
* **Build detection:** Sustained energy increase over bars
* **Reverb tail events:** Long decay at section end

Output:

```json
{
  "events": [
    {"type": "impact", "time_sec": 48.2, "bar": 49, "energy": 0.85},
    {"type": "drop", "time_sec": 64.0, "bar": 65, "energy_change": -0.6},
    {"type": "tail_start", "time_sec": 112.0, "bar": 113, "duration_sec": 2.5}
  ]
}
```

**Use Cases:**
* Lighting cue triggers
* Visual scene changes
* Screen animation sync points

**Deliverables:**
* `src/analysis/events.py`
* `data/events/<song>_events.json`
* Timeline integration (events reference beat grid)

---

### 3.2 Lighting / Visual Control Interface

**Problem:** Need to send event data to external systems (DMX lighting, video players, LED controllers).

**Solution:** Build adapters for common protocols:

* **OSC output:** Send events to QLab, Resolume, TouchDesigner
* **MIDI output:** Send notes/CCs to lighting consoles
* **DMX (via OLA):** Direct fixture control for small setups
* **Websocket:** Browser-based visualizers

**Deliverables:**
* `src/output/osc_sender.py`
* `src/output/midi_sender.py`
* Example QLab workspace template (cue list synced to timeline)

---

### 3.3 Show Choreography Scripting

**Problem:** Need to coordinate what happens on stage during specific moments.

**Solution:** Declarative show script format:

```yaml
show:
  - song: "Song1"
    sections:
      - name: "Intro"
        time_range: [0, 16]
        stage:
          position: "center_back"
          lighting: "dim_blue"
          screen: "abstract_slow"
      - name: "Chorus"
        time_range: [48, 80]
        stage:
          position: "front_center"
          lighting: "bright_white_strobes"
          screen: "lyric_video_fragment"
        events:
          - bar: 49
            trigger: "impact_bass_drop"
            lighting: "blackout_then_flash"
```

**Deliverables:**
* `show_script.yaml` format spec
* `src/show/parser.py` (load + validate script)
* `src/show/executor.py` (playback engine that sends cues at correct times)

---

## Phase 4: Narrative & Release Engineering

**When:** After show control is proven in rehearsal/test performance.

### 4.1 Lyric Timestamp Integration

**Problem:** Need to know **what words** are being sung **when** for narrative-aware visuals.

**Solution:** Import timestamped lyrics (LRC format or manual JSON):

```json
{
  "lyrics": [
    {"time_sec": 16.5, "text": "Verse line 1", "section": "Verse 1"},
    {"time_sec": 19.2, "text": "Verse line 2", "section": "Verse 1"}
  ]
}
```

**Use Cases:**
* Screen shows specific lyric lines at correct time
* Lighting changes on thematic keywords ("fire" → red lights)
* Camera direction cues ("I" → closeup, "we" → wide shot)

**Deliverables:**
* `data/lyrics/<song>_lyrics.json`
* `src/narrative/lyrics_parser.py`

---

### 4.2 Narrative Structure Map

**Problem:** Need to track recurring themes, motifs, callbacks across album.

**Solution:** Album-level narrative graph:

```json
{
  "album": "AlbumName",
  "themes": [
    {"id": "isolation", "songs": ["Song1", "Song4", "Song7"]},
    {"id": "rebirth", "songs": ["Song3", "Song8"]}
  ],
  "callbacks": [
    {
      "motif": "piano_melody_A",
      "appearances": [
        {"song": "Song1", "section": "Intro"},
        {"song": "Song7", "section": "Outro"}
      ]
    }
  ]
}
```

**Use Cases:**
* Show script ensures consistent visual treatment of recurring themes
* Setlist optimizer groups thematically linked songs
* Marketing materials highlight narrative arc

**Deliverables:**
* `data/narrative/album_structure.json`
* Manual creation initially (later: AI-assisted extraction from lyrics)

---

### 4.3 Multi-Format Export Pipeline

**Problem:** Need stems, masters, clips, teasers for different platforms.

**Solution:** Automated export profiles:

```yaml
export_profiles:
  - name: "Spotify_Master"
    format: "WAV"
    lufs_target: -14.0
    true_peak_max: -1.0
    sample_rate: 44100
    bit_depth: 16
  
  - name: "YouTube_Teaser"
    format: "MP3"
    duration: 30
    start_time: "Chorus"
    fade_in: 2.0
    fade_out: 3.0
  
  - name: "Stem_Pack"
    format: "WAV"
    include: ["VOCAL_LEAD", "BASS", "DRUMS", "MUSIC"]
    normalize_stems: false
```

**Deliverables:**
* `src/export/profiles.py`
* CLI: `python -m src.cli export-all --profile Spotify_Master`

---

### 4.4 Metadata Management

**Problem:** Need consistent metadata across formats (ISRC, credits, artwork).

**Solution:** Central metadata registry:

```json
{
  "song": "SongName",
  "isrc": "USXX12345678",
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "year": 2026,
  "credits": {
    "producer": "Name",
    "engineer": "Name",
    "mastering": "FinishLine Auto + Name"
  },
  "artwork": "assets/album_cover.jpg"
}
```

Embed into all exports automatically.

**Deliverables:**
* `data/metadata/<song>_metadata.json`
* Auto-embedding via `mutagen` library

---

### 4.5 Release Strategy Tracker

**Problem:** Need to coordinate release schedule, promotional assets, analytics.

**Solution:** Release operations dashboard:

```yaml
release_plan:
  - date: "2026-03-01"
    action: "Single 1 Release"
    platforms: ["Spotify", "Apple Music", "YouTube"]
    assets_needed:
      - "Master WAV"
      - "Cover 3000x3000"
      - "Teaser 30sec video"
    status: "ready"
  
  - date: "2026-03-15"
    action: "Lyric Video"
    status: "in_progress"
```

**Deliverables:**
* `release_schedule.yaml`
* CLI: `python -m src.cli release status`
* Analytics integration (track performance, update strategy)

---

## Phase 5: Intelligence Layer (Optional, Long-Term)

**When:** After all manual workflows are proven and stable.

### 5.1 Anomaly Detection

**Problem:** Catch outliers that rule-based system might miss.

**Solution:** Train model on "approved" songs, flag new songs that deviate:

* "This vocal is 5 dB quieter than album average"
* "This chorus has unusual frequency content"
* "This transition has phase correlation issue"

**Deliverables:**
* `src/intelligence/anomaly_detector.py`
* Lightweight model (no LLMs, just statistical baselines)

---

### 5.2 Adaptive Thresholds

**Problem:** Fixed thresholds might not suit all genres/styles.

**Solution:** Learn thresholds from reference set:

* Analyze 10 approved songs
* Compute confidence intervals for all metrics
* Use as dynamic thresholds instead of hardcoded values

**Deliverables:**
* `src/intelligence/threshold_learner.py`

---

### 5.3 Setlist Optimizer (Live Performance)

**Problem:** Need to order songs for live show based on energy, narrative, dynamics.

**Solution:** Constraint-based optimizer:

```python
constraints = [
    "no more than 2 slow songs in a row",
    "high-energy song every 15 minutes",
    "thematically linked songs close together",
    "key transitions <3 semitones preferred"
]
```

**Deliverables:**
* `src/show/setlist_optimizer.py`

---

## Implementation Priority Summary

### Must Do After MVP (Phase 2)
1. ✅ Album-level consistency
2. ✅ Programmatic export
3. ✅ Undo mechanism

### Should Do for Live Shows (Phase 3)
4. ✅ Event detection (onsets, drops)
5. ✅ Lighting/visual output adapters
6. ✅ Show choreography scripting

### Can Do for Release (Phase 4)
7. ✅ Multi-format export
8. ✅ Metadata management
9. ⏸️ Lyric integration (if narrative visuals needed)
10. ⏸️ Release tracker

### Optional Enhancements (Phase 5)
11. ⏸️ Anomaly detection
12. ⏸️ Adaptive thresholds
13. ⏸️ Setlist optimizer

---

## Consistency Check: Does This Align with Philosophy?

**Every enhancement passes the philosophy test:**

### "You define intent, system enforces consistency"
- ✅ Album consistency: enforces YOUR median across songs
- ✅ Show script: YOU write cues, system executes timing
- ✅ Reference profiles: YOU choose references, system matches them

### "Outputs are explainable and logged"
- ✅ Event detection: timestamps + energy values logged
- ✅ Metadata: central registry, version-controlled
- ✅ Release tracker: audit trail of what was done when

### "No creative changes"
- ✅ Visual sync: READS musical data, doesn't CHANGE it
- ✅ Narrative map: organizational tool, not generative
- ✅ Anomaly detection: FLAGS issues, doesn't auto-fix

### "Addressable at scale"
- ✅ Album operations: batch 12 songs with one command
- ✅ Show automation: coordinate lights + video + audio from single timeline
- ✅ Release pipeline: generate all export formats from one source

**Philosophy remains intact through all phases.**

---

## When to Build What

**Don't build Phase N until:**
- Phase N-1 is production-stable (used on 3+ real songs)
- User workflow is documented and repeatable
- No major bugs remain
- You actually need the next feature (don't build speculatively)

**The MVP alone could be enough** if it solves your immediate album-finishing problem. Everything else is optional enhancement.
