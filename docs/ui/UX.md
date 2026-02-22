# UX: Read-Only Status Dashboard

**Last updated**: 2026-02-22  
**Purpose**: Running UX/spec document for a frontend that visualizes docs/status system.  
**Status**: Planning only - no implementation until requested.

---

## 1. Purpose

**This frontend is read-only.** It visualizes project status and progress only.

**What it does**:
- Renders docs/status markdown files in structured UI
- Shows task progress, receipts, and roadmap in navigable format
- Computes derived metrics (% complete, velocity, gate status)
- Provides fast search/filter over receipts and tasks

**What it does NOT do**:
- Control Ableton Live
- Trigger automation or execute commands
- Edit markdown files (docs/status remains canonical)
- Write actions or change backend state

**Design philosophy**: Terminal-first workflow remains primary. UI is an optional read-only visualization layer.

---

## 2. Non-Goals

**Explicitly out of scope**:
- ❌ No control of Ableton (read-only visualization)
- ❌ No "write" actions (button to trigger `flaas apply`, etc.)
- ❌ No automation triggers (UI cannot start loops)
- ❌ No editing receipts from UI (markdown files are source of truth)
- ❌ No git operations from UI (commit, push stay terminal-only)
- ❌ No file uploads or workspace editing

**Why**: Docs/status system is designed to be human-readable markdown that works without UI. UI is sugar, not essential.

---

## 3. Primary Data Source

**Canonical sources** (all read-only):
- `docs/status/CURRENT.md` - Entrypoint (where we are now)
- `docs/status/ROADMAP.md` - Future work (prioritized)
- `docs/status/RECEIPTS/*.md` - Audit trail (completed tasks)
- `docs/status/SNAPSHOTS/*` - Optional structured dumps
- `docs/status/TEMPLATES/*.md` - Metadata schema definitions

**Additional context** (linked, not mirrored):
- `docs/project/operating-manual-v1.md` - Unified reference
- `docs/workflow/execution-system.md` - FSM + gates
- `docs/reference/ENGINEERING_NOTEBOOK.md` - API catalog
- Git history (commits as task completions)

**Update mechanism**: UI watches filesystem or polls markdown files. No database. Markdown is truth.

---

## 4. Information Architecture (Menu)

**Left-nav menu** (driven by docs/status indexes):

```
📊 Overview         → CURRENT.md structured view
✅ Tasks            → Unified task list (DONE/NEXT/BACKLOG)
📋 Receipts         → Chronological receipt browser
🗺️  Roadmap          → ROADMAP.md + milestone view
📸 Snapshots        → SNAPSHOTS/ file browser
📚 Docs             → Links to full docs (external)
⚙️  Settings         → UI preferences (dark mode, etc.)
```

**Top bar** (always visible):
- Current milestone + % complete
- Last commit hash (clickable → GitHub)
- Gate status indicators (G1..G5 colored badges)
- "Refresh" button (re-read markdown files)

---

## 5. Core Views (Read-only)

### 5.1 Overview

**Purpose**: Dashboard showing CURRENT.md in structured, at-a-glance format.

**Layout**:
```
┌─────────────────────────────────────────┐
│ FLAAS v0.0.2                            │
│ main @ 175a358                          │
│ Updated: 2026-02-22 04:00 UTC           │
├─────────────────────────────────────────┤
│ Milestone: MVP (90%)  ████████░░        │
│ Next: Discover export endpoint          │
├─────────────────────────────────────────┤
│ Gates: G1✅ G2⚠️ G3⚠️ G4⚠️ G5🚧           │
├─────────────────────────────────────────┤
│ Fingerprint: d4d98c...                  │
│ Tracks: 1  Devices: 1                   │
│ Last scan: 2026-02-22 03:54 UTC         │
├─────────────────────────────────────────┤
│ Capabilities (13 verified)              │
│ ✅ OSC ping, scan, inspect              │
│ ✅ Analysis, check, plan, apply         │
│ ✅ Loop, verify, reset                  │
│ ⚠️  Gates G2-G4 pending rerun           │
└─────────────────────────────────────────┘
```

**Data mapped from**:
- CURRENT.md Section 1 (identity)
- CURRENT.md Section 2 (milestone + progress)
- CURRENT.md Section 4 (gate status)
- CURRENT.md Section 5 (fingerprint)
- CURRENT.md Section 6 (capabilities)
- CURRENT.md Section 7 (next action)

**Interactions**:
- Click "Next action" → Shows full command block (read-only, copyable)
- Click gate badge → Links to execution-system.md gate definition
- Click fingerprint → Shows full model_cache.json (read-only viewer)

---

### 5.2 Tasks (Main Feature)

**Purpose**: Linear list of ALL tasks (completed + future) with status tracking.

**Task sources**:
1. **DONE tasks**: Derived from `RECEIPTS/*.md` (one task per receipt)
2. **NEXT task**: From CURRENT.md Section 7 "next single action"
3. **BACKLOG tasks**: From ROADMAP.md expansions (not yet receipted)

**Layout** (list view):
```
Status  | Task Title                          | When         | Commit
--------|-------------------------------------|--------------|--------
✅ DONE | Gate G1 verified                   | Feb 22 03:54 | -
✅ DONE | Export endpoint discovery          | Feb 22 03:30 | -
✅ DONE | inspect-selected-device command    | Feb 22 04:00 | 175a358
🟦 NEXT | Discover export endpoint           | -            | -
⬜ TODO | EQ Eight parameter discovery       | -            | -
⬜ TODO | Limiter parameter discovery        | -            | -
⬜ TODO | True-peak estimation algorithm     | -            | -
```

**Filters**:
- Status: DONE / NEXT / BACKLOG
- Milestone: MVP / v0.2 / v1.0
- Priority: P0 / P1 / P2 / P3
- Category: Discovery / Algorithm / Integration / Hardening

**Sorting**:
- Default: Chronological (completed tasks) + priority (backlog)
- Options: By commit, by milestone, by priority

**Click task** → Opens detail view (Receipt Detail or Roadmap Entry).

---

### 5.3 Receipt Detail View

**Purpose**: Show completed task with full validation evidence.

**Layout**:
```
┌─────────────────────────────────────────────────┐
│ inspect-selected-device Command                 │
│ 2026-02-22 04:00 UTC                            │
│ Commit: 175a358                                 │
│ Status: ✅ Validated                            │
├─────────────────────────────────────────────────┤
│ Why                                             │
│ • Accelerate device parameter discovery         │
│ • Instantly map any device's parameter struct   │
│ • Validate parameter semantics                  │
├─────────────────────────────────────────────────┤
│ Files Touched (4)                               │
│ + src/flaas/inspect_selected_device.py          │
│ ~ src/flaas/cli.py                              │
│ ~ docs/workflow/terminal-cheatsheet.md          │
│ ~ docs/reference/ENGINEERING_NOTEBOOK.md        │
├─────────────────────────────────────────────────┤
│ Terminal Validation                             │
│ ▶ python3 -m compileall src/flaas/             │
│ ▶ flaas inspect-selected-device                 │
│   [show output in collapsible block]            │
├─────────────────────────────────────────────────┤
│ Pass Criteria                                   │
│ ✅ Module compiles without errors               │
│ ✅ Table printed with 12 Utility parameters     │
│ ✅ No prefix in param names (sliced correctly)  │
│ ✅ Gain param (ID 9) shows current value        │
├─────────────────────────────────────────────────┤
│ Artifacts                                       │
│ • src/flaas/inspect_selected_device.py          │
│ • OSC endpoints: /live/view/get/selected_device │
├─────────────────────────────────────────────────┤
│ TL;DR (Explain Like I'm 8)                      │
│ We made a command that lets you pick any device │
│ in Ableton and instantly see all its knobs and  │
│ numbers. Before this, we had to guess which     │
│ numbers meant what. Now we just ask Ableton.    │
├─────────────────────────────────────────────────┤
│ Related                                         │
│ • Receipt: Gate G1 verified (OSC working)       │
│ • Roadmap: Expansion 2 (EQ Eight - uses this)   │
│ • Code: inspect_selected_device.py              │
│ • Docs: ENGINEERING_NOTEBOOK.md (OSC endpoints) │
└─────────────────────────────────────────────────┘
```

**Data mapped from** receipt file:
- Title, date, commit from filename + frontmatter
- Why, change summary, validation commands from markdown sections
- Pass criteria checkboxes from markdown
- Artifacts list from markdown
- TL;DR: **Generated by UI** (simple summarization of "Why" section)

**Interactions**:
- Click commit hash → GitHub commit page
- Click file path → Opens file in GitHub (or local editor if available)
- Click related receipt → Navigate to that receipt
- Copy button for terminal commands

---

### 5.4 Roadmap View

**Purpose**: Show prioritized future work grouped by milestone.

**Layout**:
```
┌─────────────────────────────────────────────────┐
│ Roadmap: Next 20 Expansions                     │
├─────────────────────────────────────────────────┤
│ MVP (v0.1.0) - 1 remaining                      │
│                                                 │
│ 🔍 Expansion 1: /live/song/export/*             │
│    Priority: P0 (MVP blocker)                   │
│    Unlocks: Automated export, full closed-loop  │
│    Validation: python3 -c "from flaas.osc_rpc…  │
│                                                 │
├─────────────────────────────────────────────────┤
│ Post-MVP (v0.2.0) - 6 expansions                │
│                                                 │
│ 🔍 Expansion 2: EQ Eight band parameters        │
│    Priority: P1                                 │
│    Unlocks: Mud cuts, harshness cuts, rumble    │
│    Validation: flaas inspect-selected-device    │
│    Status: Discovery needed                     │
│                                                 │
│ 🔍 Expansion 3: Limiter parameters              │
│    Priority: P1                                 │
│    Unlocks: True-peak ceiling enforcement       │
│    Validation: flaas inspect-selected-device    │
│    Status: Discovery needed                     │
│                                                 │
│ [... more expansions ...]                       │
└─────────────────────────────────────────────────┘
```

**Data mapped from**:
- ROADMAP.md milestone sections
- Each expansion entry (status, priority, what it unlocks, validation)

**Filters**:
- Milestone: MVP / v0.2 / v1.0
- Priority: P0 / P1 / P2 / P3
- Status: Discovery / Algorithm / Blocked / Ready

**Interactions**:
- Click expansion → Show full details (expected params, endpoints, notes)
- Click validation command → Copy to clipboard
- Click related receipt (if expansion completed) → Navigate to receipt

---

### 5.5 Snapshots View

**Purpose**: Browse structured dumps from docs/status/SNAPSHOTS.

**Layout** (file browser):
```
┌─────────────────────────────────────────────────┐
│ Snapshots (3 files)                             │
├─────────────────────────────────────────────────┤
│ 📄 model_cache_2026-02-22.json                  │
│    Type: Cache                                  │
│    Size: 1.2 KB                                 │
│    Created: 2026-02-22 03:54 UTC                │
│                                                 │
│ 📄 endpoint_registry_2026-02-22.json            │
│    Type: Registry                               │
│    Size: 3.4 KB                                 │
│    Created: 2026-02-22 04:15 UTC                │
│                                                 │
│ 📄 device_params_utility_2026-02-22.json        │
│    Type: Device Map                             │
│    Size: 890 B                                  │
│    Created: 2026-02-22 04:00 UTC                │
└─────────────────────────────────────────────────┘
```

**Data mapped from**:
- SNAPSHOTS/ directory listing (filesystem)
- Filename parsing for type inference
- File metadata (size, mtime)

**Filters**:
- Type: Cache / Registry / Device Map / Custom
- Date range

**Interactions**:
- Click snapshot → JSON/text viewer (read-only)
- Download button (save locally)
- Search within snapshot (if JSON)

---

## 6. Status Math (Calculated Fields)

**These are computed fields, NOT stored in markdown:**

### Progress Calculation
```python
# MVP % complete
mvp_done = count(receipts matching milestone=MVP)
mvp_total = count(ROADMAP MVP items) + mvp_done
mvp_percent = (mvp_done / mvp_total) * 100

# Similar for v0.2, v1.0
```

**Displayed as**:
- Progress bar (90% → 90px of 100px width)
- Fraction (9/10 outcomes)
- ETA (simple velocity projection, see below)

---

### Velocity Stats
```python
# Parse timestamps from receipt filenames or commit dates
receipts_last_7d = receipts where (now - created_at) <= 7 days
tasks_per_day = len(receipts_last_7d) / 7

# Time between commits
commits = git log --since=7days --format=%at
avg_commit_interval_hours = average delta between commits

# Estimated remaining
remaining_tasks = count(ROADMAP backlog items)
eta_days = remaining_tasks / tasks_per_day (if tasks_per_day > 0)
```

**Displayed as**:
- "3.2 tasks/day (last 7d)"
- "Avg commit interval: 4.2h"
- "Est. remaining: 6 days (based on recent velocity)"

**Caveats** (shown in UI):
- Velocity assumes uniform task complexity (not true)
- ETA is projection only, not commitment
- Blockers (unknown endpoint existence) can invalidate projection

---

### Gate Health Score
```python
# Gate status from CURRENT.md Section 4
g1_pass = (gate_g1 == "PASS")
g2_pass = (gate_g2 == "PASS")
# ... etc

gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass])
gates_total = 5  # G1-G5
gate_health = (gates_passed / gates_total) * 100
```

**Displayed as**:
- Badge colors: ✅ green (PASS), ⚠️ yellow (NOT RUN), ❌ red (FAIL), 🚧 gray (not implemented)
- Overall score: "Gate health: 3/5 (60%)"

---

### Fingerprint Freshness
```python
# Parse CURRENT.md Section 5
fingerprint_timestamp = parse(CURRENT.md "Timestamp")
age_minutes = (now - fingerprint_timestamp).total_seconds() / 60

if age_minutes < 5:
    freshness = "🟢 Fresh"
elif age_minutes < 30:
    freshness = "🟡 Recent"
else:
    freshness = "🔴 Stale"
```

**Displayed as**:
- Color indicator + age ("🟢 Fresh - 2 min ago")
- Warning if stale: "Run `flaas scan` to refresh"

---

## 7. Data Model (Minimal Schema)

**Not code, just conceptual schema for UI parsing.**

### Task
```typescript
interface Task {
  id: string;                    // Derived from receipt filename or roadmap slug
  title: string;                 // From receipt title or roadmap expansion name
  status: "DONE" | "NEXT" | "IN_PROGRESS" | "BACKLOG";
  milestone: "MVP" | "v0.2" | "v1.0";
  priority: "P0" | "P1" | "P2" | "P3";
  receipt_path?: string;         // If DONE: path to receipt file
  commit_hash?: string;          // If DONE: git commit
  created_at?: Date;             // From receipt filename or commit date
  completed_at?: Date;           // From receipt date or commit date
  tags: string[];                // e.g., ["discovery", "osc", "device"]
  validation_cmd?: string;       // Command to validate (from receipt or roadmap)
}
```

---

### ReceiptSummary
```typescript
interface ReceiptSummary {
  slug: string;                  // From filename (e.g., "inspect_selected_device")
  datetime: Date;                // From filename (e.g., 2026-02-22 04:00)
  commit_hash: string | null;    // From receipt "Commit" field
  title: string;                 // From receipt title (first h1)
  status: "✅ Validated" | "⚠️ Partial" | "❌ Failed";
  artifacts: string[];           // List of produced files/docs
  tldr: string;                  // Auto-generated or from receipt section
  files_touched: number;         // Count from "Files touched" section
  lines_changed: string;         // e.g., "+150 -1"
}
```

---

### CurrentStatus
```typescript
interface CurrentStatus {
  version: string;               // From Section 1
  branch: string;                // From Section 1
  last_commit: string;           // From Section 1
  milestone: string;             // From Section 2
  milestone_percent: number;     // From Section 2 (parsed or computed)
  completed_count: number;       // Count of ✅ items in Section 2
  blocked_count: number;         // Count of ⬜ items in Section 2
  next_action_title: string;     // From Section 7
  next_action_cmd: string;       // From Section 7 code block
  fallback_probe_cmd: string;    // From Section 8
  fingerprint: string;           // From Section 5 (64 hex chars)
  fingerprint_timestamp: Date;   // From Section 5
  gate_status: {                 // From Section 4
    [gate: string]: "PASS" | "NOT RUN" | "FAIL" | "Not implemented";
  };
  capabilities: string[];        // From Section 6 (✅ items)
}
```

---

### RoadmapEntry
```typescript
interface RoadmapEntry {
  expansion_id: number;          // e.g., 1, 2, 3
  title: string;                 // e.g., "EQ Eight band parameters"
  status: string;                // e.g., "🔍 Discovery needed"
  priority: "P0" | "P1" | "P2" | "P3";
  milestone: "MVP" | "v0.2" | "v1.0";
  what_it_unlocks: string;       // From "What it unlocks" field
  validation_cmd: string;        // From "Validation" field
  notes?: string;                // From "Discovery", "Expected", "Note" fields
}
```

---

## 8. Mapping Rules (Docs → UI)

**Deterministic rules for parsing markdown into UI data model:**

### Rule 1: Task ID Assignment
```python
# DONE tasks (from receipts)
task_id = f"receipt:{receipt_filename_without_ext}"
# Example: "receipt:2026-02-22_0400_inspect_selected_device"

# NEXT task (from CURRENT.md)
task_id = "current:next_action"

# BACKLOG tasks (from ROADMAP.md)
task_id = f"roadmap:expansion_{N}"
# Example: "roadmap:expansion_2"
```

---

### Rule 2: Task Status Assignment
```python
if receipt_exists(task_id):
    status = "DONE"
elif task_id in CURRENT.md Section 7:
    status = "NEXT"
elif task_id in CURRENT.md Section 2 and marked "IN_PROGRESS":
    status = "IN_PROGRESS"
else:
    status = "BACKLOG"
```

---

### Rule 3: Receipt Parsing
```python
# Filename format: YYYY-MM-DD_HHMM_<slug>.md
filename = "2026-02-22_0400_inspect_selected_device.md"
date_str, time_str, slug = parse_filename(filename)
datetime = parse(f"{date_str} {time_str}", format="%Y-%m-%d %H%M")

# Sections (parse markdown)
title = first_h1_text  # "Receipt: inspect-selected-device Command"
commit = extract_field("Commit")  # "175a358"
files_touched = parse_list_under_heading("## Change Summary / Files touched")
validation_cmds = extract_code_blocks_under_heading("## Terminal Validation / Commands run")
pass_criteria = extract_checklist_under_heading("## Terminal Validation / Pass criteria")
artifacts = parse_list_under_heading("## Artifacts Produced")
status_badge = extract_field("Status")  # "✅ Validated"
```

---

### Rule 4: CURRENT.md Parsing
```python
# Parse structured sections (headings are anchors)
identity = parse_section("## 1. Project Identity")
milestone = parse_section("## 2. Current Milestone")
environment = parse_section("## 3. Last Known-Good Environment")
gates = parse_section("## 4. Current Known-Good Gates")
fingerprint = parse_section("## 5. Latest Fingerprint")
capabilities = parse_section("## 6. Latest Verified Capabilities")
next_action = parse_section("## 7. Next Single Action")
fallback_probe = parse_section("## 8. If It Fails")

# Extract key fields
version = extract_field(identity, "Current version")
last_commit = extract_field(identity, "Last commit")
milestone_name = extract_field(milestone, "Milestone")
milestone_progress = extract_field(milestone, "Progress")  # "90% complete (9/10)"
next_cmd = extract_code_block(next_action, "Command to run")
```

---

### Rule 5: Single Source of Truth
**Markdown files remain canonical.**

**UI does NOT**:
- Store state in database
- Cache parsed data across sessions (ephemeral only)
- Modify markdown files

**UI DOES**:
- Re-parse markdown on every page load (or on "Refresh" click)
- Use filesystem watch (inotify/FSEvents) for live updates (optional)
- Show warning if markdown parse fails

**Conflict resolution**: If UI and markdown disagree, markdown wins. Show error in UI: "Parse failed, see docs/status/CURRENT.md directly."

---

## 9. Acceptance Criteria (for First UI Build Later)

**UI v0 must do** (when implementation starts):

### Must Have
- ✅ Render CURRENT.md cleanly (all 9 sections)
- ✅ List receipts with search/filter (by date, status, keyword)
- ✅ Show tasks list with statuses (DONE/NEXT/BACKLOG)
- ✅ Link out to markdown files (open in editor or GitHub)
- ✅ Compute % progress for milestones (from task counts)
- ✅ Display gate status badges (colored indicators)
- ✅ Copy-paste terminal commands (one-click copy)
- ✅ Refresh button (re-parse all markdown)

### Should Have
- ✅ Search across all receipts (full-text)
- ✅ Filter tasks by milestone, priority, status
- ✅ Show TL;DR for receipts (auto-generated summary)
- ✅ Display commit links (clickable to GitHub)
- ✅ Show velocity stats (tasks/day, ETA)

### Could Have
- ⬜ Dark mode toggle
- ⬜ Markdown preview side-by-side with structured view
- ⬜ Export receipt list as CSV
- ⬜ Timeline visualization (commits over time)

### Won't Have (v0)
- ❌ No editing receipts from UI
- ❌ No running commands from UI (read-only)
- ❌ No git operations from UI
- ❌ No Ableton control from UI

---

## 10. Open Questions (for Future)

### Data Format
**Q1**: Should we add structured front-matter to receipts for easier parsing?
```yaml
---
id: 2026-02-22_0400_inspect_selected_device
title: inspect-selected-device Command
commit: 175a358
date: 2026-02-22T04:00:00Z
status: validated
tags: [discovery, osc, device, surface-expansion]
---
```
**Trade-off**: Easier parsing vs. more verbose receipts.  
**Decision**: TBD (test with markdown-only first, add YAML only if parse reliability becomes issue).

---

**Q2**: Should we create `docs/status/tasks/index.json` for structured task registry?
```json
{
  "tasks": [
    {
      "id": "receipt:2026-02-22_0400_inspect_selected_device",
      "status": "DONE",
      "milestone": "MVP",
      "receipt": "RECEIPTS/2026-02-22_0400_inspect_selected_device.md"
    },
    {
      "id": "roadmap:expansion_2",
      "status": "BACKLOG",
      "milestone": "v0.2",
      "priority": "P1"
    }
  ]
}
```
**Trade-off**: Single structured source vs. maintaining parallel index.  
**Decision**: TBD (prefer markdown-only; add JSON index only if UI performance requires it).

---

**Q3**: Should receipts include "TL;DR" section or should UI generate it?
**Options**:
- A) Manual: Author writes TL;DR in receipt template (more work, higher quality)
- B) Auto: UI generates TL;DR from "Why" section (less work, lower quality)
- C) Hybrid: Optional TL;DR in receipt, fallback to auto-generation

**Decision**: TBD (start with auto-generation, upgrade to manual if quality insufficient).

---

**Q4**: How to handle git log as task source?
**Current approach**: Receipts are explicit (one receipt = one completed task).  
**Alternative**: Parse git log commits as implicit tasks (commit message = task title).

**Trade-off**:
- Pro (git log): Automatic, no manual receipt creation
- Con (git log): Less structured, missing validation commands/outputs

**Decision**: TBD (prefer explicit receipts for now; git log is fallback for velocity stats).

---

**Q5**: Should UI display "suggested next action" (not just from CURRENT.md)?
**Example**: UI suggests "Run Gate G2" if last G2 run was >7 days ago or after code change.

**Decision**: TBD (start with CURRENT.md only; add suggestions later if useful).

---

## Implementation Notes (When UI Work Starts)

### Tech Stack Recommendations (Not Decided)
**Option 1: Static Site Generator** (e.g., Astro, Hugo)
- Pro: No backend, fast, deploy to GitHub Pages
- Con: No live updates (manual refresh)

**Option 2: Python Web Server** (e.g., FastAPI + HTMX)
- Pro: Python-native, server-side rendering, easy filesystem watch
- Con: Requires server running

**Option 3: Electron/Tauri App**
- Pro: Desktop app, full filesystem access, native feel
- Con: Heavy, new tech stack, packaging complexity

**Recommendation**: Start with static site (Astro + filesystem watch for hot reload). Upgrade to server if real-time updates needed.

---

### Parsing Strategy
**Approach**: Treat markdown as structured data, parse via regex/AST.

**Libraries** (Python):
- `markdown-it-py` (AST parser)
- `frontmatter` (YAML front-matter)
- `python-dateutil` (timestamp parsing)

**Libraries** (JavaScript, if static site):
- `remark` (markdown AST)
- `gray-matter` (front-matter)
- `date-fns` (timestamp parsing)

**Fallback**: If parsing fails, show raw markdown (graceful degradation).

---

### Filesystem Watch (Optional)
**If UI is local server or Electron**:
- Watch `docs/status/**/*.md` for changes
- On change: Re-parse affected files → Push update to UI (WebSocket or SSE)
- Use debounce (500ms) to avoid thrashing on rapid edits

**Libraries**:
- Python: `watchdog`
- JavaScript: `chokidar`

---

### Responsive Design
**Breakpoints**:
- Desktop (≥1024px): Left nav + main content + right sidebar (optional)
- Tablet (768-1023px): Collapsible left nav + main content
- Mobile (≤767px): Hamburger menu + single-column layout

**Priority**: Desktop-first (terminal users have large screens). Mobile is nice-to-have.

---

## Validation Checklist (Before UI Implementation Starts)

**Backend prerequisites**:
- ✅ docs/status system exists and stable
- ✅ CURRENT.md, ROADMAP.md, receipts format stable
- ✅ Templates define required metadata
- ✅ At least 5 receipts exist (enough data to test UI)

**Design prerequisites**:
- ⬜ Wireframes for Overview, Tasks, Receipt Detail views
- ⬜ Color scheme + typography decisions
- ⬜ Responsive breakpoints defined

**Tech stack decision**:
- ⬜ Static site vs. server vs. desktop app chosen
- ⬜ Framework selected (Astro/Next/Svelte/etc.)
- ⬜ Parsing library tested on real receipts

---

## Future Evolution

**As backend matures, UI should visualize**:
- Audio waveforms with LUFS overlay (when verify-audio supports JSON export)
- Parameter change timeline (when actions.json includes history)
- Device graph (when scan includes device chains)
- OSC message inspector (when OSC logging implemented)
- A/B comparison player (when before/after audio stored)

**These are NOT in scope for UI v0.** Markdown-only dashboard first.

---

**Last updated**: 2026-02-22  
**Next update trigger**: After MVP completion, or after 10+ receipts created, or when UI implementation requested.
