# Design Brief — Bioluminescent / Organic

Paste this entire file to your designer. They return a single file: `templates/styles/default.css`. No HTML/code changes.

---

## Vibe

You're inside a cell. Mitochondria glow. Jellyfish drift in the dark. Plasma flows through veins of light. The report is **alive** — not a printout, not a dashboard, but a translucent organism showing you what it sees.

This is the "biotech meets fine art" lane. Think:
- Iris van Herpen runway show projection visuals
- Refik Anadol AI data sculptures
- Deep-sea bioluminescence documentaries (anglerfish, comb jellies)
- Mitochondrial / DNA imaging from CRISPR papers
- Apple's "Liquid Retina" marketing renders
- Luma AI / Octane volumetric clouds

Reference search terms:
- "bioluminescent jellyfish closeup"
- "mitochondria fluorescence microscopy"
- "Iris van Herpen runway"
- "Refik Anadol data painting"
- "Apple Vision Pro UI rendering"

**Strict no-go**: hospital chart aesthetic. Sharp corners. Box shadows on white. Bootstrap. Anything that looks "designed in 2015".

---

## Color palette

```css
--abyss:         #050816;     /* deepest bg */
--abyss-mid:     #0a0a1f;     /* mid bg */
--abyss-warm:    #150a2e;     /* surface, hint of purple */

--bio-cyan:      #00d4ff;     /* primary accent */
--bio-magenta:   #ff3df3;     /* secondary glow */
--bio-lime:      #b3ff42;     /* "young" / "good" */
--bio-coral:     #ff6b9d;     /* warm accent */
--bio-uv:        #8a4dff;     /* ultraviolet purple */

--text-bright:   #f0f8ff;     /* main text */
--text-soft:     #a8b8d4;     /* secondary */
--text-faint:    #4a5478;

--glow-soft:     0 0 40px;
--glow-strong:   0 0 80px;
```

**Color philosophy**: every color element is a "bioluminescence" — glowing from within against a dark plasma backdrop. Status mapping: `.good` → bio-lime (alive, vibrant), `.warn` → bio-coral (drifting toward warm), `.bad` → bio-magenta (cellular distress signal).

---

## Typography

- **Numbers**: A serif display face for the big numbers — `"Fraunces", "Source Serif Pro", "Noto Serif CJK SC"`. Weight 600-700. Numbers should feel **organic, hand-drawn** — not engineered. Tabular nums on.
- **Headings**: `"Manrope", "Inter", "PingFang SC"` — geometric sans, slightly humanist
- **Body**: same as headings, tracking 0.01em
- **No monospace anywhere** — this is the opposite of the cyberpunk brief

Typography should feel like calligraphy through a lens. Slight letter-spacing on headings. No all-caps shouting.

---

## Signature effects

### 1. Living gradient background
The body has a slow-shifting radial gradient that suggests cells drifting:

```css
body {
  background:
    radial-gradient(circle at 20% 30%, rgba(0, 212, 255, 0.15), transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(255, 61, 243, 0.12), transparent 40%),
    radial-gradient(circle at 50% 90%, rgba(179, 255, 66, 0.08), transparent 50%),
    var(--abyss);
}
```

For motion: SVG filter `<feTurbulence>` + slow `animation` on a fixed-position ::before layer (disable in print + reduced-motion).

### 2. Numbers glow from within
```css
.organ-age, .chron-num {
  color: var(--bio-cyan);
  text-shadow:
    0 0 20px currentColor,
    0 0 60px currentColor,
    0 0 120px rgba(0, 212, 255, 0.3);
  filter: drop-shadow(0 0 8px currentColor);
}
```

Each organ uses its own glow color (think anglerfish lure):
- Cardiovascular: bio-coral
- Hepatic: bio-uv
- Pulmonary: bio-cyan
- Renal: bio-magenta
- Metabolic: bio-lime
- Musculoskeletal: cyan-lime mix

### 3. Cards as "cellular membranes"
- No sharp corners — `border-radius: 24px` minimum
- Backdrop-blur for glass effect (`backdrop-filter: blur(40px) saturate(1.4)`)
- Border is a subtle gradient: `border: 1px solid; border-image: linear-gradient(135deg, rgba(0,212,255,0.4), rgba(255,61,243,0.2)) 1;`
- Inner radial gradient: brighter at center, fades to edges (mimics cell with bright nucleus)
- On hover (screen only): subtle scale + brighten

### 4. Connecting filaments
For the multi-snapshot trend matrix: between cells of the same row, draw thin glowing lines (1px) connecting them — like axons. Use `box-shadow` or pseudo-elements + `transform`.

For connecting "snapshot A → B → C" timeline at top: a horizontal flowing gradient line with pulsing dots at each timepoint.

### 5. Inference text as "neural transcript"
The inference paragraph gets:
- Italic serif body
- Hanging quotation marks at start (large, glowing)
- Subtle gradient text fill (text bleeds from cyan to lime over the paragraph)
- Background: slight inner glow rather than a solid fill

### 6. Delta badges as "pulse waves"
Don't use pills. Render delta as a small inline waveform — 5-7 bars varying height based on magnitude — with the number floating above. Like an EKG snippet but stylized.

### 7. Section transitions
Between sections, instead of borders, use a slowly fading gradient strip (50% opacity, blur, color drift). Sections feel like they melt into each other rather than being boxed.

---

## Layout requirements

- **chron-callout**: A circular "nucleus" (200px diameter) with the number floating in the middle, glowing. Surrounding text orbits the right side. The whole thing has a soft halo glow.
- **organ-grid**: Asymmetric grid — "Overall" card is largest and centered, others are slightly smaller and arranged around it like organelles. Use CSS Grid with mixed sizing. Mobile = single column.
- **matrix table**: Reimagine as a **tracery diagram**. Rows are organs, columns are timepoints, cells are glowing nodes connected by faint lines. The "matrix" structure is preserved semantically (it's still a `<table>`) but visually it's a constellation.
- **inference blocks**: Translucent cards that overlap slightly when expanded, with backdrop-blur

---

## Print / PDF rules

This is the hardest part — bioluminescence **does not print well**. Strategy: in print mode, retain the *organic feel* through layout but switch to a high-contrast version.

In `@media print`:
- Bg: pure white
- Glow effects → flat colors (saturated but solid)
- Filter / blur disabled
- Numbers stay serif but switch to deep saturated jewel-tones (deep teal, plum, forest green) on white
- Cards keep rounded corners but lose translucency — solid pale tinted backgrounds
- Connecting lines stay (1pt solid)
- The print version should look like **a cellular biology lab's hand-illustrated report** — still organic, but flat

**No dark-mode-on-paper attempts** — they always look bad.

---

## Specific HTML targets

```
.report-single, .report-multi, .report-header
.chron-callout, .chron-num, .chron-label, .chron-conf
.organ-grid, .organ-card, .organ-name, .organ-age, .delta
.organ-card.good, .organ-card.warn, .organ-card.bad
table.matrix, .organ-row, .m-cell
.inference, .inf-block
.report-footer, .disclaimer
```

`--organ-color` is set inline on each card / row — use it as the glow tint for that organ.

---

## Constraints

- No external CDN fonts (system fallbacks)
- No JS, no canvas
- Animations only on screen + respect `prefers-reduced-motion`
- Status NEVER conveyed by color alone (also size / shape / icon)
- A4 PDF must fit on 1-2 pages
- Total CSS < 600 lines (this brief is more elaborate, so a bit more is allowed)

---

## Deliverable

A single `default.css` file. Iterate on screen first, then verify the print version is gorgeous in its own right. Both views should feel like the same organism, just observed at different wavelengths.
