# Design Brief — Holographic / AR HUD

Paste this entire file to your designer. They return a single file: `templates/styles/default.css`. No HTML/code changes.

---

## Vibe

Tony Stark looking at his suit's medical readout. The Major's neural diagnostic in *Ghost in the Shell*. A soldier's tactical overlay in *Halo* / *Cyberpunk Edgerunners*. The Iron Man HUD interface — translucent, layered, geometric, scanning. Information **floats** over reality.

Not glowing organic (that's brief 02), not dystopian gritty (that's brief 01). This is **clean, precise, military-tech translucency**. Engineered to be glanceable.

Reference imagery:
- "Iron Man HUD UI"
- "Ghost in the Shell tactical overlay"
- "Halo MJOLNIR HUD"
- "Edgerunners netrunner scan"
- "Apple Vision Pro app interface"
- "Microsoft HoloLens demos"

**Strict no-go**: gritty cyberpunk decay. Heavy ornamentation. Anything that doesn't feel like it's projected from a beam onto your retina.

---

## Color palette

```css
--void:           #000814;       /* deepest bg — true black with blue hint */
--mist:           rgba(8, 16, 32, 0.4);  /* translucent panel bg */
--mist-deep:      rgba(8, 16, 32, 0.7);

--hud-cyan:       #00e5ff;       /* primary HUD color — bright cyan */
--hud-blue:       #4d8fff;       /* secondary blue */
--hud-white:      #ffffff;       /* highlights */
--hud-amber:      #ffb000;       /* alert */
--hud-red:        #ff3344;       /* critical */
--hud-green:      #66ff99;       /* nominal */

--line-bright:    rgba(0, 229, 255, 0.85);
--line-soft:      rgba(0, 229, 255, 0.3);
--line-faint:     rgba(0, 229, 255, 0.12);

--text-primary:   #e8f4ff;
--text-secondary: rgba(232, 244, 255, 0.7);
--text-muted:     rgba(232, 244, 255, 0.4);
```

Status: `.good` → hud-green or hud-cyan, `.warn` → hud-amber, `.bad` → hud-red. **Always paired with shape/icon** (not color alone).

---

## Typography

- **Numbers + readouts**: `"Aldrich", "Eurostile", "Bank Gothic", "Orbitron", "Inter Tight", sans-serif`. Wide condensed letterforms. Weight 400-500 (not heavy — HUD text is thin).
- **Headings**: same family, often condensed-extended versions. Letter-spacing 0.15-0.25em on caps.
- **Body**: `"Inter", "Roboto", "PingFang SC", sans-serif`, weight 300-400 (lightweight)
- **Labels**: All-caps, monospace `"JetBrains Mono"`, very small (10-11px), tracked out wide

Type philosophy: **thin lines, wide tracking, minimal weight contrast**. Like text projected at low brightness.

---

## Signature effects

### 1. Translucent layered panels (the core HUD effect)
```css
.card, .organ-card, .matrix-card {
  background: var(--mist);
  backdrop-filter: blur(20px) saturate(1.2);
  -webkit-backdrop-filter: blur(20px) saturate(1.2);
  border: 1px solid var(--line-soft);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.05),
    0 0 60px rgba(0, 229, 255, 0.04);
}
```

In print, fall back to opaque white with cyan border.

### 2. Geometric corner accents (HUD framing)
Each panel has small geometric brackets at corners — NOT decorative, but functional-looking. Use SVG inline or pseudo-elements:

```
┌─                         ─┐
│                            │
│      [content]             │
│                            │
└─                         ─┘
```

The brackets are 12-16px lines, 1.5px thick, hud-cyan color, slight glow.

### 3. Targeting reticles around big numbers
The `chron-num` and main `organ-age` numbers are **inside a target reticle**:
- Two crosshair lines (top + bottom) extending from the number
- Small tick marks at the corners
- Number sits centered in this implied target

```
        ┊
   ─────┼─────
        ┊
       [42]
        ┊
   ─────┼─────
        ┊
```

Use pseudo-elements + absolutely positioned thin lines.

### 4. Scanning line animation
A horizontal cyan line slowly sweeps top-to-bottom across the viewport (very subtle, low opacity). Disable in print + reduced-motion.

```css
body::before {
  content: ""; position: fixed; left: 0; right: 0; height: 1px;
  background: var(--line-bright); opacity: 0.4;
  pointer-events: none; z-index: 9998;
  animation: scan 12s linear infinite;
}
@keyframes scan {
  0% { top: -10px; opacity: 0; }
  10% { opacity: 0.5; }
  90% { opacity: 0.5; }
  100% { top: calc(100% + 10px); opacity: 0; }
}
```

### 5. Hexagonal / geometric accents
Sparingly — small hex icons next to status labels. Each organ's section header has a small geometric "node" icon. Inline SVG, 16px.

### 6. Data callouts with trailing arrows
For deltas and important values, draw thin arrowed callouts pointing from the number to a label nearby — like a HUD highlighting threats:

```
      42 ←──── ELEVATED
              +4 vs baseline
```

Use CSS borders + pseudo-elements for the arrow.

### 7. Numbers as luminous overlays
```css
.organ-age, .chron-num {
  font-weight: 300;     /* thin — let the glow do the work */
  color: var(--hud-cyan);
  text-shadow:
    0 0 8px rgba(0, 229, 255, 0.6),
    0 0 24px rgba(0, 229, 255, 0.3);
}
```

Different organ → different glow tint. Status overrides apply on `.warn` / `.bad`.

### 8. Matrix table as scanning grid
The matrix becomes a **tactical display**:
- Cells separated by thin cyan grid lines (1px)
- Active cells have a small corner reticle on focus/hover
- Column headers floated above slightly with a thin connector line
- Status in cells: thin colored bars + number, not solid backgrounds

### 9. Inference text with type-on effect (screen only)
Inference paragraphs reveal letter-by-letter on first paint (CSS `@keyframes` + `letter-spacing` trick or `clip-path` reveal). 1-2 second total animation, then static. **Disabled in print and reduced-motion.**

---

## Layout requirements

- **chron-callout**: A wide HUD readout panel at top. Number large in center with reticle around it. Confidence text floats to the right with a connector line. Subtle scan effect when first loaded.
- **organ-grid**: 7 panels in **hex-tiled or staggered grid** layout (think tactical map). On desktop, asymmetric — "Overall" panel large center, others orbit. Mobile: stack but keep HUD framing.
- **matrix**: Tactical grid with column scan-line on hover, row highlight on focus
- **inference**: Each inference is in its own translucent panel with a connector line to the timepoint above

Footer: minimal, single line of monospace metadata at the bottom, very small.

---

## Print / PDF rules

This is the trickiest brief — translucent HUD does not print. Strategy in `@media print`:

- White background
- Translucent panels → solid white with 1pt cyan border
- Backdrop-blur disabled (no fallback needed if we set background to white directly)
- Glow effects disabled
- Scan animation disabled
- Numbers stay thin sans-serif but in saturated cyan-blue (#0066cc) on white
- Reticles and corner brackets stay (they're vector shapes, print fine)
- Connector lines stay (1pt solid)
- Footer becomes a clean monospace line at page bottom

Print version: looks like **architectural drawing** or **engineering schematic** — precise, technical, but printable on white paper without losing identity.

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

`--organ-color` inline → use as accent for the organ's reticle / glow tint.

---

## Constraints

- No external CDN fonts (system + base64 if needed)
- No JS — all effects pure CSS / SVG
- Animations only on screen; respect `prefers-reduced-motion`
- Backdrop-blur with opaque fallback for browsers without support
- Status NEVER conveyed by color alone (also shape: ▲ warn, ⬢ critical, ◇ nominal)
- A4 PDF must fit on 1-2 pages
- Total CSS < 500 lines

---

## Deliverable

A single `default.css` file. Iterate until **someone seeing the screen says "is that an Iron Man movie prop?"** — that's the bar. Print version should be its own object: clean, technical, but recognizable as the same product.
