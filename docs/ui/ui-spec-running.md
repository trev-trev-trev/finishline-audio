# UI Specification (Running Document)

**Status**: Placeholder - No UI work until MVP gates pass

**→ [UX.md](UX.md) is the canonical UI planning doc** (read-only status dashboard).

---

**This document** (`ui-spec-running.md`) covers general UI exploration. **[UX.md](UX.md)** is the focused spec for the Status Dashboard frontend

---

## MVP Gates (UI Work Blocked Until Complete)

### Gate 1: Automated Export/Re-render
- **Status**: ❌ Not implemented
- **What's needed**: Automated Ableton export via OSC or deterministic manual loop
- **Blocker**: Manual export currently required for iteration

### Gate 2: Multi-Stem Support
- **Status**: ❌ Not implemented
- **What's needed**: Stem naming contracts, per-stem analysis, per-stem actions
- **Blocker**: Only single-file master analysis supported

### Gate 3: True-Peak Estimation
- **Status**: ❌ Not implemented
- **What's needed**: Oversampling true-peak meter
- **Blocker**: Using peak dBFS approximation

### Gate 4: Expanded Device Mapping
- **Status**: ❌ Partial (Utility only)
- **What's needed**: EQ Eight, limiters, other devices
- **Blocker**: Only Utility Gain control implemented

### Gate 5: Verification + Iteration Cap
- **Status**: ✅ Basic implementation exists
- **What's improved**: Max iteration enforcement, better stop conditions
- **Blocker**: None (foundational, can improve)

**→ UI work should NOT begin until Gates 1-4 are complete.**

---

## Possible UI Surfaces (Future Exploration)

### Option A: Enhanced CLI (TUI)
**Tech**: `rich`, `textual`, or similar Python TUI library  
**Scope**: Interactive terminal UI with panels, live updates, progress bars

**Advantages**:
- No new tech stack (Python-based)
- Runs in terminal (fits current workflow)
- Fast to prototype

**Disadvantages**:
- Limited visual richness
- Terminal-only (no web/mobile)

**Use cases**:
- Real-time monitoring during loop iteration
- Visual feedback for LUFS/peak vs. targets
- Interactive parameter tweaking

**Questions for later**:
- How to show waveform/spectrum visualization in terminal?
- Live tail of OSC messages?
- Split-pane layout (logs, status, controls)?

---

### Option B: Web UI (Local Server)
**Tech**: FastAPI + React/Svelte/HTMX + WebSockets  
**Scope**: Browser-based UI served from local Python backend

**Advantages**:
- Rich visual feedback (graphs, waveforms)
- Can run on different machine (network access)
- Modern UI patterns

**Disadvantages**:
- New tech stack (frontend + backend coordination)
- More complex to maintain
- Requires browser

**Use cases**:
- Visual waveform display with LUFS overlay
- Drag-and-drop file uploads
- Real-time status dashboard during automated iteration
- Parameter adjustment with visual feedback

**Questions for later**:
- WebSocket latency for real-time OSC feedback?
- Authentication needed for network access?
- How to show Ableton state (track/device tree)?

---

### Option C: Ableton Device UI (Max for Live)
**Tech**: Max for Live (visual programming + JavaScript)  
**Scope**: Custom M4L device in Ableton with controls and feedback

**Advantages**:
- Native integration with Ableton
- No separate window/process
- Direct access to Live API (no OSC)

**Disadvantages**:
- Requires Max for Live (not all Ableton editions)
- Learning curve for Max/JavaScript
- Less flexibility than standalone app

**Use cases**:
- In-DAW controls for triggering analysis
- Live feedback on compliance targets
- One-click "fix LUFS" button

**Questions for later**:
- Can M4L drive Python subprocess?
- How to display rich feedback in M4L UI?
- Latency of M4L ↔ Python bridge?

---

### Option D: Hybrid (CLI + Web Dashboard)
**Tech**: CLI for automation, web UI for monitoring/reporting  
**Scope**: Core logic stays CLI-driven, web UI for visualization only

**Advantages**:
- Preserves terminal-first workflow
- Web UI is optional (doesn't break CLI)
- Best of both worlds

**Disadvantages**:
- Two codebases to maintain
- Complexity of keeping them in sync

**Use cases**:
- Run `flaas loop` from terminal
- Monitor progress in web dashboard
- View historical iteration timeline
- Export/share compliance reports

**Questions for later**:
- How to push updates from CLI to web UI (WebSocket? Polling? Event stream?)
- Where to store timeline data for web UI?

---

## UI Feature Wishlist (Unordered)

### Visualization
- [ ] Waveform display with LUFS overlay
- [ ] Spectrum analyzer (before/after)
- [ ] LUFS meter (real-time target comparison)
- [ ] Peak meter with true-peak indicator
- [ ] Parameter value history (gain over iterations)
- [ ] Iteration timeline (LUFS convergence graph)

### Controls
- [ ] Drag-and-drop audio file upload
- [ ] One-click "analyze and plan" button
- [ ] Manual parameter override sliders
- [ ] Target adjustment (LUFS, peak ceiling)
- [ ] Iteration mode selector (auto/manual/dry-run)
- [ ] Emergency stop button

### Monitoring
- [ ] Live OSC message log (filtered)
- [ ] Ableton state display (track/device tree)
- [ ] Current Utility Gain readout (live)
- [ ] Fingerprint match status (visual indicator)
- [ ] Error/warning panel

### Reporting
- [ ] Compliance report export (PDF/HTML)
- [ ] Iteration history export (JSON/CSV)
- [ ] Before/after audio comparison player
- [ ] Shareable compliance badge/certificate

---

## Open Questions (To Answer Later)

### Architecture
1. Should UI be a separate process or embedded in Python package?
2. How to handle UI when running headless (CI/automation)?
3. Should UI have its own config file or reuse existing?
4. How to version UI separately from CLI/core logic?

### Data Flow
1. How does UI subscribe to real-time updates?
2. Where to store UI state (session, persistence)?
3. How to replay past iterations in UI?
4. Should UI have read-only mode?

### User Experience
1. What's the primary workflow (file-centric vs. project-centric)?
2. How to handle multi-stem workflows in UI?
3. Should UI guide user through Ableton setup?
4. How to surface advanced features without clutter?

### Integration
1. Can UI trigger Ableton export automatically?
2. Should UI show Ableton's current playback position?
3. How to display device parameters not exposed via OSC?
4. Should UI support multiple Live sets?

### Testing
1. How to test UI without manual clicking?
2. Should UI have a demo/mock mode (no Ableton)?
3. How to snapshot UI state for regression testing?

---

## Non-Goals (Explicit Out-of-Scope for UI)

- ❌ **Audio editing**: FLAAS analyzes, not edits. Use Ableton for editing.
- ❌ **Full DAW integration**: Not replacing Ableton, complementing it.
- ❌ **Real-time audio processing**: Analysis is offline, not live.
- ❌ **Plugin hosting**: Not a VST/AU host.
- ❌ **Cloud/collaboration features**: Local-first tool.
- ❌ **Mobile apps**: Desktop/terminal-first (web UI might work on tablets, but not optimized).

---

## Strict Rule

**No UI implementation work begins until**:
1. MVP gates 1-4 are complete (documented in `docs/project/mvp_remaining.md`)
2. User explicitly requests UI development
3. Core CLI workflow is stable and tested

**Why**: UI is high-effort, high-maintenance. Core logic must be solid first.

---

## Future Considerations (Post-MVP)

### Advanced Features (If UI is Built)
- Session management (save/load iteration history)
- Presets (target profiles: streaming, CD, vinyl)
- Multi-file batch processing UI
- Export templates (naming conventions, path patterns)
- Integration with other tools (ffmpeg, SoX, etc.)

### Accessibility
- Keyboard shortcuts for all actions
- Screen reader support (if web UI)
- High-contrast themes
- Adjustable font sizes

### Performance
- Lazy-load large waveforms
- Virtualized lists for long iteration histories
- Caching of analysis results
- Efficient OSC message filtering (don't spam UI)

---

**This document should be updated**:
- When MVP gates complete
- When UI surface is chosen
- When prototyping begins
- When design decisions are made

**Do not speculate on UI implementation details until MVP is complete.**
