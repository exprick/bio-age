# Design Brief — Mission Control / Datacenter

Paste this entire file to your designer. They return a single file: `templates/styles/default.css`. No HTML/code changes.

---

## Vibe

The Apollo Mission Control consoles where engineers tracked a man going to the moon. Bloomberg Terminal where traders watch markets. A SOC (Security Operations Center) dashboard where defenders watch packets. SpaceX's launch readout. NASA TV's flight data display.

This is **information density done right** — every pixel earns its place, every color signals state, the whole thing breathes professionalism: "the people reading this know what they're doing." It's the opposite of consumer health-app friendliness.

Reference imagery:
- "NASA Mission Control 1969"
- "Bloomberg Terminal screenshot"
- "SpaceX Falcon 9 launch readout"
- "Apollo CRT display"
- "Modern SOC dashboard"
- "NORAD command center"

**Strict no-go**: rounded corners. Pastel colors. Wellness-app vibes. Marketing-friendly typography. Excessive whitespace. Anything that wouldn't fit on a launch console.

---

## Color palette

```css
--bg-base:       #0c0c0e;      /* near-black */
--bg-panel:      #14161a;      /* slightly lighter for panels */
--bg-deeper:     #08080a;      /* deepest recess */
--bg-row-alt:    #0e1014;

--phosphor:      #5be37c;      /* CRT phosphor green — primary text */
--phosphor-dim:  #2a6638;      /* dimmed phosphor — grid lines */
--amber:         #ffb800;      /* alert / warn — old terminal amber */
--scarlet:       #ff3344;      /* critical */
--ice-blue:      #58a8ff;      /* secondary data */
--white:         #f0f4f8;      /* highlights / current values */
--gray-mid:      #5a5e66;      /* labels, axes */
--gray-dim:      #2c2e34;      /* borders, separators */

--glow-soft:     0 0 4px;
--glow-hot:      0 0 12px;
```

Status mapping (PRINT-FRIENDLY too):
- `.good` → phosphor green text + dim green left-stripe
- `.warn` → amber text + amber stripe
- `.bad` → scarlet text + scarlet stripe
- `.pending` → gray dim

---

## Typography

**EVERYTHING is monospace**. No exceptions. This is a terminal aesthetic.

- **Numbers + labels**: `"IBM Plex Mono", "JetBrains Mono", "SF Mono", monospace`
- **Headings**: same, but UPPERCASE with letter-spacing 0.08em
- **Section dividers**: ASCII / Unicode box-drawing characters (`═`, `─`, `│`, `┌`, `┘`)

Type sizes are aggressively compact:
- h1: 22px (don't go bigger; this isn't a hero)
- h2: 14px UPPERCASE, monospace
- h3: 12px UPPERCASE, monospace, dimmed
- Body / data: 12-13px
- Big numbers (organ-age): 28-36px (LARGE for the number, but contained)

---

## Signature effects

### 1. CRT phosphor glow on text
```css
body {
  font-family: "IBM Plex Mono", "SF Mono", monospace;
  background: var(--bg-base);
  color: var(--phosphor);
  text-shadow: 0 0 2px currentColor;   /* subtle glow on EVERY character */
}
```

Big numbers get heavier glow. Headers get amber glow if amber-status, scarlet if critical.

### 2. Section frames as ASCII boxes
Headers wrap themselves in Unicode box drawing:

```
╔═══════════════════════════════════════════════════════════╗
║  CARDIOVASCULAR_AGE_ASSESSMENT                  [NOMINAL] ║
╚═══════════════════════════════════════════════════════════╝
```

Use CSS pseudo-elements + monospace `content` strings. The brackets close on the right edge regardless of content length (use `display: flex; justify-content: space-between`).

### 3. Status indicators as bracketed flags
Every section title has a status indicator on the right:

```
[ NOMINAL ]   green
[ ELEVATED ]  amber
[ CRITICAL ]  scarlet
[ NO DATA ]   gray
```

These are mandatory — they make the report scannable in 2 seconds.

### 4. Mini sparklines / data bars (CSS only)
For delta indicators and multi-snapshot rows, render bars using `background: linear-gradient(...)` rather than icons:

```
DELTA   [████████░░░░░░░░░░░]  +4
RANGE   [▁▂▄▆▇▆▅▃▂▁]
```

Use Unicode block chars or pseudo-element widths.

### 5. Grid background (very subtle)
A 12-column grid suggested by 1px vertical lines at low opacity. Like a graph-paper underlay.

```css
body::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    repeating-linear-gradient(90deg, var(--phosphor-dim) 0 1px, transparent 1px 80px),
    repeating-linear-gradient(0deg, var(--phosphor-dim) 0 1px, transparent 1px 24px);
  opacity: 0.05;
}
```

### 6. Time-of-day badge
The footer has a fake "system uptime" / "last refresh" indicator:

```
T+00:00:42  |  REFRESH RATE: 1.0 Hz  |  STATUS: NOMINAL
```

This is just a styling flourish — pull from `data.generated_at`.

### 7. Matrix table as console output
The trend matrix becomes a **densely packed data grid**:
- No padding extravagance — 6-8px max
- Alternating row backgrounds
- Column headers: `T-1` / `T-2` / `T-3` (like time series indices)
- Cells right-aligned for numbers
- Status conveyed by text color (not background)
- Sortable column header style (^ or ▼ indicators), even if static

---

## Layout requirements

- **Full-bleed background** (no max-width on body — info dense fills the screen)
- Inside, a 2-column main grid: left = primary readouts, right = supplementary panels
- **chron-callout** is a single-line readout, NOT a hero card:
  ```
  ESTIMATED_CHRONO_AGE: 38 ± 2  | CONFIDENCE: MODERATE | ANCHOR_BIOMARKERS: cv_apoB, t_low, bmd_low
  ```
- **organ-grid**: 4-column tight grid on desktop. Each "card" is a simple bordered region with 4-5 lines of data:
  ```
  ┌── CARDIO ────────────[NOMINAL]──┐
  │ AGE        42                   │
  │ DELTA      +4                   │
  │ STATUS     ↑ ELEVATED           │
  │ ANCHOR     ApoB 89, HRV 23      │
  └─────────────────────────────────┘
  ```
- **matrix**: a single dense console table; no card wrapping it, just a section header + table
- **inference**: show as a transcript log:
  ```
  > 2026-04-30 19:22 [SNAPSHOT_A] ANALYSIS:
  > Biomarkers suggest a relatively young adult ...
  ```

Mobile: stack panels but keep the dense feel — don't suddenly become friendly.

---

## Print / PDF rules

In `@media print`:
- Background → white
- Phosphor green → black
- Status colors stay (amber, scarlet) but desaturate slightly
- Glow disabled (text-shadow: none)
- Box-drawing characters render as actual lines (already unicode → no change needed)
- Grid background → invisible

Print version should look like **a flight data printout** — clean, dense, monochrome with status accents. Think NASA flight log.

---

## Specific HTML targets

```
.report-single, .report-multi, .report-header
.chron-callout, .chron-num, .chron-label, .chron-conf
.organ-grid, .organ-card, .organ-name, .organ-age, .delta
.organ-card.good, .organ-card.warn, .organ-card.bad
table.matrix, .organ-row, .m-cell, .m-cell.good, .m-cell.warn, .m-cell.bad
.inference, .inf-block (a <details>)
.report-footer, .disclaimer
```

`--organ-color` set inline → use as left-stripe accent for that organ's panels.

---

## Constraints

- 100% monospace, system mono fallback
- No external font CDN
- No JS, no canvas
- Animations: optionally a subtle "scan refresh" pass (top-to-bottom 0.3 opacity wipe every 60s) on screen — disable in print + reduced-motion
- A4 PDF: must fit on 1 page (this layout is dense by design)
- Total CSS < 350 lines (this is the most disciplined brief)

---

## Deliverable

A single `default.css` file. The bar: someone glances at it and says "that's a serious tool, not a wellness app". Density, hierarchy, status visibility = top priorities.
