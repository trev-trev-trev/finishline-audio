# UX Implementation: Read-Only Status Dashboard (UI MVP)

**Last updated**: 2026-02-22  
**Upstream**: [UX.md](UX.md) (philosophy + design)  
**Status**: Planning - do not implement until requested

---

## 1. UI MVP Definition (v0)

**What UI v0 IS**:
- Read-only web app (local static site or dev server)
- Left-nav menu: Overview, Tasks, Receipts, Roadmap, Snapshots, Docs
- Markdown renderer for CURRENT, ROADMAP, RECEIPTS
- Derived task list (DONE/NEXT/BACKLOG)
- Copy-paste terminal commands (code blocks)

**What UI v0 is NOT**:
- ❌ No Ableton control, no write actions, no git operations
- ❌ No search/filter (post-MVP)
- ❌ No velocity stats (post-MVP)
- ❌ No real-time filesystem watch (post-MVP)

**MVP acceptance**: "Render docs/status as navigable UI, faster than reading raw markdown."

---

## 2. Tech Stack (Decision + Constraints)

**Constraints**: Render markdown, read files, build menu from folder structure.

### Option A: "Fastest Local" (Recommended)
**Stack**: Astro + Tailwind CSS  
**Repo placement**: `/ui/dashboard/`  
**Build/run**:
```bash
cd ui/dashboard
npm install && npm run dev  # http://localhost:4321
npm run build  # dist/ (static HTML)
```
**Artifacts**: Static HTML (deploy to GitHub Pages or local)  
**Why**: Markdown-first, zero backend, fast prototype.

### Option B: "Future Web" (Optional)
**Stack**: FastAPI + Jinja2 + HTMX  
**Repo placement**: `/ui/server/`  
**Build/run**:
```bash
cd ui/server
pip install -e . && python -m dashboard.app  # http://localhost:8000
```
**Artifacts**: Python web server (requires runtime)  
**Why**: Python-native, live filesystem watch, can add write actions later.

**Recommendation**: **Option A (Astro)** for MVP. Simpler, faster, no server dependency.

---

## 3. Data Inputs (Canonical)

**UI reads** (relative paths from `/ui/dashboard/`):
- `../../docs/status/CURRENT.md` (262 lines)
- `../../docs/status/ROADMAP.md` (275 lines)
- `../../docs/status/RECEIPTS/*.md` (3 files, ~150 lines each)
- `../../docs/status/SNAPSHOTS/*` (optional, currently empty)

**Required metadata per doc**:

**CURRENT.md**:
```yaml
version, branch, last_commit          # Section 1
milestone, progress, completed, blocked  # Section 2
gate_status: {G1: "PASS", G2: "NOT RUN", ...}  # Section 4
fingerprint, timestamp  # Section 5
capabilities: ["OSC ping", "scan", ...]  # Section 6
next_action_title, next_action_cmd  # Section 7
```

**ROADMAP.md**:
```yaml
expansions: [{id, title, status, priority, what_it_unlocks, validation_cmd}]
```

**RECEIPTS/*.md**:
```yaml
datetime, slug  # From filename
title, commit, files_touched, validation_cmds, pass_criteria, artifacts, status  # From sections
```

---

## 4. Parsing Strategy (No Fragility)

**Approach**: Heading-based regex parsing (no YAML front-matter in MVP).

**Example parser** (TypeScript):
```typescript
function parseCurrent(md: string) {
  const sections = md.split(/^## /gm);
  const identity = sections.find(s => s.startsWith('1. Project Identity'));
  const version = identity?.match(/\*\*Current version\*\*:\s*(.+)/)?.[1];
  const milestone = sections.find(s => s.startsWith('2. Current Milestone'));
  const progress = milestone?.match(/\*\*Progress\*\*:\s*(.+)/)?.[1];
  return { version, progress, /* ... */ };
}
```

**Detect task status** (purely from docs):
```typescript
function getTaskStatus(slug: string): TaskStatus {
  const receiptExists = fs.existsSync(`../../docs/status/RECEIPTS/${slug}.md`);
  if (receiptExists) return "DONE";
  
  const current = fs.readFileSync('../../docs/status/CURRENT.md', 'utf-8');
  if (current.includes(slug)) return "NEXT";
  
  return "BACKLOG";
}
```

**YAML front-matter** (optional future):
- Add to `docs/status/TEMPLATES/receipt_template.md`
- Migrate incrementally (parser tries YAML first, falls back to headings)
- Schema: `{id, date, commit, status, milestone, tags}`

**Recommendation**: Start without YAML. Add only if parse reliability issues.

---

## 5. UI Information Architecture (Routes/Views)

**Routes**:
- `/` → Overview (CURRENT.md structured)
- `/tasks` → Task list (aggregated)
- `/receipts` → Receipt list
- `/receipts/[slug]` → Receipt detail
- `/roadmap` → Roadmap (milestone-grouped)
- `/snapshots` → Snapshots browser
- `/docs` → External doc links

**Astro pages**:
```
ui/dashboard/src/pages/
├── index.astro              # Overview
├── tasks.astro              # Task list
├── receipts/
│   ├── index.astro          # Receipt list
│   └── [slug].astro         # Receipt detail
├── roadmap.astro            # Roadmap
├── snapshots.astro          # Snapshots
└── docs.astro               # Doc links
```

---

## 6. Implementation Tasks (Running List)

**First 10 tasks = MVP-critical.** Tasks 11-20 = Post-MVP enhancements.

---

### Task 1: Scaffold Astro app ⭐
**Goal**: Create empty Astro project.  
**Files**: `ui/dashboard/*` (scaffold)  
**Commands**:
```bash
mkdir -p ui/dashboard && cd ui/dashboard
npm create astro@latest . -- --template minimal --no-install && npm install
npm run dev && curl -s http://localhost:4321 | grep Astro
```
**Pass**: ✅ Dev server runs, welcome page loads  
**Rollback**: `rm -rf ui/dashboard`

---

### Task 2: Read CURRENT.md ⭐
**Goal**: Load markdown file in index.astro.  
**Files**: `ui/dashboard/src/pages/index.astro`  
**Commands**: `npm run dev && curl http://localhost:4321 | grep "Project Identity"`  
**Pass**: ✅ CURRENT.md content appears  
**Rollback**: `git checkout ui/dashboard/src/pages/index.astro`

---

### Task 3: Add markdown renderer ⭐
**Goal**: Render markdown with syntax highlighting.  
**Files**: `ui/dashboard/src/components/MarkdownContent.astro`  
**Commands**: `npm install remark remark-html shiki && npm run dev`  
**Pass**: ✅ Code blocks styled, tables render, links work  
**Rollback**: `rm ui/dashboard/src/components/MarkdownContent.astro`

---

### Task 4: Create parsers module ⭐
**Goal**: Extract structured data from markdown.  
**Files**: `ui/dashboard/src/lib/parsers.ts`, `ui/dashboard/src/lib/types.ts`  
**Commands**: Browser console test `parseCurrent(md)`  
**Pass**: ✅ Returns `{version, milestone, gates, fingerprint, next_action}`  
**Rollback**: `rm ui/dashboard/src/lib/{parsers,types}.ts`

---

### Task 5: Left-nav menu ⭐
**Goal**: Fixed sidebar with 6 menu items.  
**Files**: `ui/dashboard/src/components/Layout.astro`, `ui/dashboard/src/components/LeftNav.astro`  
**Commands**: `npm run dev && curl http://localhost:4321 | grep "Overview"`  
**Pass**: ✅ Menu visible, 6 items, active route highlighted  
**Rollback**: `rm ui/dashboard/src/components/{Layout,LeftNav}.astro`

---

### Task 6: Overview cards ⭐
**Goal**: Render CURRENT.md as structured cards.  
**Files**: `ui/dashboard/src/pages/index.astro`, `ui/dashboard/src/components/OverviewCard.astro`  
**Commands**: Visual check in browser  
**Pass**: ✅ 5 cards (Identity, Milestone, Gates, Fingerprint, Capabilities), gate badges colored  
**Rollback**: `git checkout ui/dashboard/src/pages/index.astro`

---

### Task 7: Receipts list ⭐
**Goal**: `/receipts` lists all receipts.  
**Files**: `ui/dashboard/src/pages/receipts/index.astro`  
**Commands**: `curl http://localhost:4321/receipts | grep "inspect-selected-device"`  
**Pass**: ✅ 3 receipts, sorted by date, status badges  
**Rollback**: `rm ui/dashboard/src/pages/receipts/index.astro`

---

### Task 8: Receipt detail ⭐
**Goal**: `/receipts/[slug]` renders full receipt.  
**Files**: `ui/dashboard/src/pages/receipts/[slug].astro`  
**Commands**: `curl http://localhost:4321/receipts/2026-02-22_0400_inspect_selected_device`  
**Pass**: ✅ Sections render (Why, Commands, Pass Criteria), commit hash links to GitHub  
**Rollback**: `rm ui/dashboard/src/pages/receipts/[slug].astro`

---

### Task 9: Tasks list ⭐
**Goal**: `/tasks` aggregates DONE+NEXT+BACKLOG.  
**Files**: `ui/dashboard/src/pages/tasks.astro`, `ui/dashboard/src/lib/taskAggregator.ts`  
**Commands**: `curl http://localhost:4321/tasks | grep DONE`  
**Pass**: ✅ ~23 tasks (3 DONE, 1 NEXT, 20 BACKLOG), status badges  
**Rollback**: `rm ui/dashboard/src/pages/tasks.astro ui/dashboard/src/lib/taskAggregator.ts`

---

### Task 10: Roadmap page ⭐
**Goal**: `/roadmap` renders ROADMAP.md grouped.  
**Files**: `ui/dashboard/src/pages/roadmap.astro`  
**Commands**: `curl http://localhost:4321/roadmap | grep "Expansion 1"`  
**Pass**: ✅ Milestones (MVP, v0.2, v1.0), expansions with priority/validation  
**Rollback**: `rm ui/dashboard/src/pages/roadmap.astro`

---

### Task 11: Top bar component
**Goal**: Persistent top bar with version, gates, refresh.  
**Files**: `ui/dashboard/src/components/TopBar.astro`  
**Pass**: ✅ Shows version, commit, gate badges, refresh button  
**Rollback**: `rm ui/dashboard/src/components/TopBar.astro`

---

### Task 12: Copy-to-clipboard
**Goal**: Copy button for code blocks.  
**Files**: `ui/dashboard/src/components/CodeBlock.astro`  
**Pass**: ✅ Copy button, clipboard API works, "Copied!" toast  
**Rollback**: `rm ui/dashboard/src/components/CodeBlock.astro`

---

### Task 13: Tailwind styling
**Goal**: Add typography, colors, spacing.  
**Files**: `ui/dashboard/tailwind.config.mjs`  
**Commands**: `npm install -D tailwindcss && npm run dev`  
**Pass**: ✅ Clean typography, colored badges, responsive layout  
**Rollback**: `npm uninstall tailwindcss`

---

### Task 14: Static build
**Goal**: Generate deployable HTML.  
**Commands**: `npm run build && ls dist/ && python3 -m http.server 8000 -d dist`  
**Pass**: ✅ dist/ folder, all routes, site loads from static files  
**Rollback**: `rm -rf dist`

---

### Task 15: UI .gitignore
**Goal**: Ignore node_modules, dist.  
**Files**: `ui/dashboard/.gitignore`  
**Pass**: ✅ Build artifacts not tracked  
**Rollback**: `rm ui/dashboard/.gitignore`

---

### Task 16: UI README
**Goal**: Document build/run.  
**Files**: `ui/dashboard/README.md`  
**Pass**: ✅ Shows npm commands, links to UX.md  
**Rollback**: `rm ui/dashboard/README.md`

---

### Task 17: Commit UI v0
**Goal**: Commit working MVP.  
**Commands**: `git add ui/ && git commit -m "feat: status dashboard UI v0" && git push`  
**Pass**: ✅ Pushed to main  
**Rollback**: `git revert HEAD`

---

### Task 18: Snapshots browser (post-MVP)
**Goal**: `/snapshots` lists files with metadata.  
**Files**: `ui/dashboard/src/pages/snapshots.astro`  
**Pass**: ✅ Lists SNAPSHOTS/ files or shows "empty"  
**Rollback**: `rm ui/dashboard/src/pages/snapshots.astro`

---

### Task 19: Search receipts (post-MVP)
**Goal**: Filter receipts by keyword.  
**Files**: Edit `receipts/index.astro`  
**Pass**: ✅ Search box, filters list client-side  
**Rollback**: `git checkout receipts/index.astro`

---

### Task 20: Filter tasks (post-MVP)
**Goal**: Filter by status/milestone/priority.  
**Files**: Edit `tasks.astro`  
**Pass**: ✅ 3 dropdowns, filters work  
**Rollback**: `git checkout tasks.astro`

---

**Tasks 1-10**: MVP-critical (must ship together).  
**Tasks 11-17**: Finishing touches (include in v0).  
**Tasks 18-20**: Post-MVP enhancements.

---

## 7. Acceptance Tests (UI)

**Run after Task 17 (UI committed):**

```bash
cd ui/dashboard

# Test 1: App runs
npm run dev && sleep 2 && curl -s http://localhost:4321 | grep FLAAS
# ✅ Expected: Page loads

# Test 2: Menu renders
curl -s http://localhost:4321 | grep -E "(Overview|Tasks|Receipts)"
# ✅ Expected: Menu items found

# Test 3: CURRENT renders
curl -s http://localhost:4321 | grep "Project Identity"
# ✅ Expected: Section heading found

# Test 4: Receipts list
curl -s http://localhost:4321/receipts | grep "inspect-selected-device"
# ✅ Expected: Receipt title found

# Test 5: Receipt detail
curl -s http://localhost:4321/receipts/2026-02-22_0400_inspect_selected_device | grep "Terminal Validation"
# ✅ Expected: Section found

# Test 6: Tasks list
curl -s http://localhost:4321/tasks | grep -E "(DONE|NEXT)"
# ✅ Expected: Task statuses found

# Test 7: Static build
npm run build && ls dist/index.html
# ✅ Expected: dist/ created
```

**All 7 tests pass** → UI v0 ready to ship.

---

## 8. Repo Integration Plan

### File Structure
```
/ui/dashboard/              # Astro app
├── src/
│   ├── pages/             # Routes (index, tasks, receipts, etc.)
│   ├── components/        # UI components (LeftNav, TopBar, MarkdownContent)
│   ├── layouts/           # Page layout wrapper
│   └── lib/               # Parsers, utils (parseCurrent, parseReceipts, taskAggregator)
├── public/                # Static assets (favicon, etc.)
├── package.json
├── astro.config.mjs
├── tsconfig.json
├── .gitignore
└── README.md
```

### Reading docs/status
**All file reads use relative path from UI root**:
```typescript
// ui/dashboard/src/lib/dataLoader.ts
import { readFile } from 'fs/promises';
import { resolve } from 'path';

const repoRoot = resolve(import.meta.dir, '../../');
export async function loadCurrent() {
  const path = resolve(repoRoot, 'docs/status/CURRENT.md');
  return await readFile(path, 'utf-8');
}
```

### Exclude from Python package
**Add to `pyproject.toml`**:
```toml
[tool.setuptools.packages.find]
where = ["src"]
exclude = ["ui*"]
```

**Validate**: `pip install -e . && python -c "import pkgutil; print('ui' in [m.name for m in pkgutil.iter_modules()])"`  
**Expected**: `False`

### CI hooks (optional, later)
```yaml
# .github/workflows/ui-build.yml
name: UI Build
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd ui/dashboard && npm ci && npm run build
      - run: ls ui/dashboard/dist/index.html  # Smoke test
```

**Add after**: Task 17 (UI committed).

---

## 9. Future Extensions (Non-MVP)

**After Task 17, consider**:

- **Search/Filter**: Full-text search across receipts, filter tasks by tags/date
- **Velocity Stats**: Tasks/day, time-between-commits, ETA projection
- **Timeline View**: Horizontal commit timeline with receipts positioned by timestamp
- **Export**: Receipt list as CSV, status report as PDF
- **Real-Time Updates**: Filesystem watcher (chokidar) + WebSocket for live updates
- **Advanced Parsing**: Parse git log to infer missing tasks, detect dependencies
- **JSON Viewer**: Collapsible tree for SNAPSHOTS/*.json
- **Dark Mode**: Theme toggle with localStorage persistence
- **Mobile Responsive**: Optimize for tablet/phone (currently desktop-first)

**Decision rule**: Ship UI v0 (Tasks 1-17) first. Add extensions only if users request them.

---

## Task Backlog Summary

**MVP-critical (Tasks 1-10)**: Core navigation + rendering (must ship together)  
**Finishing touches (Tasks 11-17)**: Polish + deployment (include in v0)  
**Post-MVP (Tasks 18-20)**: Enhancements (ship incrementally)

**Estimated effort**: 
- Tasks 1-10: ~2-3 days (experienced Astro dev)
- Tasks 11-17: ~1 day
- Tasks 18-20: ~1 day each

**Prerequisites**: Node.js ≥18, npm, User approval to start.

---

**Last updated**: 2026-02-22  
**Next update**: After UI v0 ships or tech stack decision changes.
