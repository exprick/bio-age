# Design briefs for bio-age reports

Each `.md` file in this folder is a **standalone, self-contained brief** you can paste into Claude Design / Claude / any frontend designer. They will return a single replacement file:

```
templates/styles/default.css
```

Drop it in, re-render, you're done. No code or HTML changes needed.

## Available briefs

| File | Aesthetic | Vibe |
|---|---|---|
| [`01-cyberpunk-neon.md`](./01-cyberpunk-neon.md) | Cyberpunk / Neon biotech | Blade Runner ripperdoc, Cyberpunk 2077 ripperdoc UI, terminal aesthetic |
| [`02-bioluminescent.md`](./02-bioluminescent.md) | Bioluminescent / organic | Deep-sea jellyfish, mitochondrial glow, plasma flow |
| [`03-mission-control.md`](./03-mission-control.md) | Mission control / datacenter | NASA console, Bloomberg terminal, infosec SOC dashboard |
| [`04-holographic-hud.md`](./04-holographic-hud.md) | Holographic / AR HUD | Iron Man suit, Ghost in the Shell, tactical overlay |

All four briefs:
- Use the same HTML structure (no markup changes required)
- Cover both single-snapshot and multi-snapshot trend layouts
- Include print-friendly degradation for the PDF output
- Specify exact colors, fonts, effects, fallbacks

## How to use

1. Pick a brief (or mix: "do the report in cyberpunk style for screen, but keep print clean and readable")
2. Paste the entire `.md` content into your designer's chat
3. They return a CSS file
4. Save to `templates/styles/<theme>.css`
5. Re-render with `--css templates/styles/<theme>.css` flag, or replace `default.css`

## Want to add your own?

Each brief follows the same structure (the four headings, then concrete CSS guidance). Use them as templates and PR a new one.
