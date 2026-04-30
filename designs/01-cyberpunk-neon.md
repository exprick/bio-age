# Design Brief — Cyberpunk Neon Biotech

Paste this entire file to your designer (Claude / Claude Design / human). They return a single file: `templates/styles/default.css`. No HTML/code changes.

---

## Vibe

Blade Runner 2049 ripperdoc consultation room. Cyberpunk 2077 V's medical readout. *Ghost in the Shell* augmented anatomy. Hospital readout from a chrome-implant clinic in 2089. A health report someone got at a back-alley street doc with a neon sign — but it's clean, organized, almost luxurious in its dystopian fluency.

Reference imagery (search these terms for mood):
- "Cyberpunk 2077 ripperdoc UI"
- "Blade Runner 2049 hologram interface"
- "Ghost in the Shell medical scan"
- "Synthwave grid"
- "Detroit Become Human Connor HUD"

**Strict no-go**: medical clipboard aesthetic. Excel tables. Bootstrap defaults. Anything that says "PDF from a clinic in 2010".

---

## Color palette

```css
--bg-deep:       #0a0e1a;   /* near-black, slight blue cast */
--bg-surface:    #0f1420;   /* card bg, slightly lighter */
--bg-glass:      rgba(20, 30, 50, 0.55);

--neon-cyan:     #00ffff;   /* primary accent — "good", glow, focus */
--neon-magenta:  #ff0080;   /* alert / "bad" / threshold breach */
--neon-green:    #00ff66;   /* nominal / online / "young" */
--neon-amber:    #ffaa00;   /* "warn" — caution */
--neon-red:      #ff2244;   /* critical */

--text-primary:  #e8f4ff;   /* slight cyan-tinted white */
--text-mute:     #6a7a8a;   /* subdued labels */
--text-faint:    #3a4456;   /* disabled / placeholder */

--grid-line:     rgba(0, 255, 255, 0.08);
--scan-line:     rgba(0, 255, 255, 0.04);
```

Status mapping: `.good` → cyan or green, `.warn` → amber, `.bad` → magenta or red, `.pending` → faint gray.

---

## Typography

- **Numbers**: `"JetBrains Mono", "Fira Code", "SF Mono", monospace`. Weight 700-800. Tabular nums **mandatory**. Numbers should look engraved.
- **Headings (CN/EN)**: `"Orbitron", "Eurostile", "PingFang SC", sans-serif`. All-caps where it fits without crowding.
- **Body text**: `"Inter", "Roboto", "PingFang SC", sans-serif` — but kept slightly looser tracking (letter-spacing: 0.02em) for tech feel.
- **Section labels**: monospace, all-caps, with a leading prefix:
  - `> CARDIO_AGE.SYS [ NOMINAL ]`
  - `> RENAL_AGE.SYS [ ELEVATED ]`
  - Use `::before { content: "> "; color: var(--neon-cyan); }`

---

## Signature effects

### 1. Scan lines
Apply to the body or main container as a 2px repeating gradient:

```css
body::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 9999;
  background: repeating-linear-gradient(
    0deg, transparent 0, transparent 2px,
    var(--scan-line) 2px, var(--scan-line) 3px
  );
  mix-blend-mode: screen; opacity: 0.6;
}
```

### 2. Number glow + chromatic aberration on big numbers (organ-age, chron-num)
```css
.organ-age, .chron-num {
  color: var(--neon-cyan);
  text-shadow:
    0 0 10px rgba(0, 255, 255, 0.6),
    0 0 30px rgba(0, 255, 255, 0.3),
    -1px 0 0 rgba(255, 0, 128, 0.5),    /* magenta on left */
     1px 0 0 rgba(0, 255, 255, 0.5);    /* cyan on right */
}
```

Apply different glow color per status: `.good` → green glow, `.warn` → amber, `.bad` → magenta-red.

### 3. Border-glow on cards
```css
.organ-card, .card {
  background: var(--bg-glass);
  border: 1px solid rgba(0, 255, 255, 0.2);
  box-shadow:
    inset 0 0 20px rgba(0, 255, 255, 0.05),
    0 0 24px rgba(0, 255, 255, 0.08);
  position: relative;
}
.organ-card::after {
  /* corner brackets — like targeting reticles */
  content: "";
  position: absolute; inset: -1px;
  background:
    linear-gradient(45deg, var(--neon-cyan) 0 12px, transparent 12px) top left / 12px 12px no-repeat,
    linear-gradient(-45deg, var(--neon-cyan) 0 12px, transparent 12px) top right / 12px 12px no-repeat,
    linear-gradient(-45deg, var(--neon-cyan) 0 12px, transparent 12px) bottom left / 12px 12px no-repeat,
    linear-gradient(45deg, var(--neon-cyan) 0 12px, transparent 12px) bottom right / 12px 12px no-repeat;
  pointer-events: none; opacity: 0.6;
}
```

### 4. Header glitch effect (h1)
Use a CSS-only RGB-split keyframe with `clip-path` snippets — but **only animate on `:hover`** (and disable for print + `prefers-reduced-motion`). Three layers (cyan / magenta / white), slight x-offset.

### 5. Delta badges as "loading bars"
Instead of a pill, render delta as a horizontal segmented bar (4-6 segments lit / unlit based on magnitude), with the number on the right.

```
DELTA  ▮▮▮▯▯▯  +3
```

### 6. Matrix table — terminal output style
- All-monospace cells
- Each cell has a subtle background grid (1px dots)
- "Header" rows look like CLI output: `┌─────────────────┐` Unicode box drawing as the table border
- Status colors fill cells with low-alpha gradients

### 7. Inference text
Style the reasoning paragraph as if it's streaming from a terminal — monospace, with a leading `█` cursor. No blink animation in print.

---

## Layout requirements

- **chron-callout**: A wide horizontal bar at top, full-width. Big monospace number on left (60-80px), label + confidence text right. Cyan glow border around the number "card-within-card".
- **organ-grid**: 7 cards in a 4-3 layout on desktop (≥960px). The "整体 / Overall" card is **double width** (spans 2 columns of the 4) and has a brighter border. Mobile collapses to single column.
- **matrix table**: For trend mode. Each row gets a left border in the organ's accent color (cyan / red / amber / etc). Cells use the status background color.
- **inference blocks**: Collapsible `<details>` styled as terminal logs.

---

## Print / PDF rules

When `@media print`:

- Background switches to **white** (cyberpunk on screen, clean engineering schematic in print)
- Glow / shadow effects → solid colored borders (1.5pt)
- Scan line overlay disabled
- Animations disabled (`animation: none !important`)
- Numbers stay monospace, but in solid black
- Status colors as left-border accents only (printer-friendly)
- Cards have visible 1pt borders (no glow)

Crucially: the print version should look like **a precision-machined engineering datasheet**, not a degraded screenshot of the screen view. Treat them as two separate looks that share structure.

---

## Specific HTML targets

The HTML you will be styling has these classes (don't change them, just style them):

```
.report-single, .report-multi, .report-header
.chron-callout, .chron-num, .chron-label, .chron-conf
.organ-grid, .organ-card, .organ-name, .organ-age, .delta
.organ-card.good, .organ-card.warn, .organ-card.bad
table.matrix, .organ-row, .m-cell, .m-cell.good, .m-cell.warn, .m-cell.bad
.inference, .inf-block (a <details>)
.report-footer, .disclaimer
```

Each `.organ-card` and `.organ-row` has a `--organ-color` CSS variable set inline — you can use it for the accent stripe per organ.

---

## Constraints

- No external font imports (use only system fallbacks + base64 if needed)
- No JS
- Animations only on screen, never in print
- Must be readable in greyscale (status NEVER conveyed by color alone — also use icons / shape / position)
- Total CSS < 400 lines
- A4 PDF must fit on 1-2 pages

---

## Deliverable

A single `default.css` file. Test it directly via the renderer (no LLM call needed):

```bash
mkdir -p test && cp examples/sample-result.json test/result.json
python3 scripts/render_report.py test/result.json --html test/report.html --pdf test/report.pdf
open test/report.html
open test/report.pdf
```

`examples/sample-result.json` is a fictional mock that exercises all severity classes (`.good / .warn / .bad`). Iterate until both screen and print look like they came from the same product.
