# bio-age

> Estimate biological age across 7 organ systems by feeding a health snapshot to any LLM. Replicates the Nature Medicine 2025 paper, with optional **age-blinding** + **multi-timepoint trend** modes. Cross-vendor skill — works with Claude Code, Codex CLI, and OpenClaw.

## What it does

You give it a health snapshot (lab panel + lifestyle + history, in plain text). It produces:

1. **Standard mode** — replicates the paper: 7 organ ages (overall, cardiovascular, hepatic, pulmonary, renal, metabolic, musculoskeletal) plus reasoning, while the LLM sees your actual age.
2. **Blind mode** — strips every age anchor (DOB, "started smoking at 18", "diseases 5-10 years ago", "low for age", etc.) so the LLM has to estimate organ ages purely from biomarkers. Bonus: it also reverse-guesses the chronological age.
3. **Trend mode** — feeds 2+ snapshots in one prompt, automatically blinds them, and produces a side-by-side comparison.

All three modes output JSON + a polished HTML report + a print-quality PDF (rendered via headless Chrome).

Backed by a finding from the original experiment: **giving the LLM the actual age softens estimates by 5-7 years on bad snapshots** — anchoring effect. Blind mode removes this bias.

## Why this exists

Sun et al. 2025 ([Nature Medicine](https://www.nature.com/articles/s41591-025-03856-8)) showed that an off-the-shelf LLM with a one-page prompt produces biological-age estimates that correlate r=0.84 with established clocks. No fine-tuning, no feature engineering, no model-specific tricks. The prompt is reproduced here verbatim.

This skill packages the method so you can:
- Run it locally with any model (Claude / Codex / Ollama)
- Audit the exact prompt and scrubbed input
- Get a shareable HTML/PDF report instead of raw JSON
- Test the anchoring effect by toggling blind mode

## Install

The skill is self-contained — clone anywhere and symlink into your agent's skill directory.

```bash
git clone https://github.com/YOUR-ORG/bio-age.git ~/dev/bio-age
chmod +x ~/dev/bio-age/bin/bio-age
```

Then register it with each agent you use:

```bash
# Claude Code
ln -s ~/dev/bio-age ~/.claude/skills/bio-age

# Codex CLI
ln -s ~/dev/bio-age ~/.codex/skills/bio-age

# Optional: add to PATH for direct shell use
echo 'export PATH="$HOME/dev/bio-age/bin:$PATH"' >> ~/.zshrc
```

## How to invoke from your agent

Once installed, just **talk to your agent in natural language**. You don't need to remember any commands — the trigger words are part of the skill description, so the agent picks it up automatically.

### Examples of what to say

**English (any agent):**
- "Run bio-age on my health report — it's at `~/health/2026-annual.txt`"
- "Estimate my biological age from these lab numbers" *[paste your panel]*
- "I want a biological age report I can share — feed in `report.txt`"
- "Use the bio-age skill to evaluate this annual physical"

**中文（任何 agent）：**
- "用 bio-age 评估一下我的生理年龄，体检报告在 `~/Downloads/2026体检.txt`"
- "把这份化验单丢给 bio-age 跑一下，做成可以发朋友圈的图" *[贴化验单]*
- "盲测一下我的生理年龄，看模型反推出来准不准"
- "出一份生理年龄报告，要 PDF 加单张分享图"

### What happens

The agent will:
1. Detect the bio-age trigger and invoke the skill
2. Run `bio-age <your-report> --runner claude --output ./out` (constructs the prompt with age scrubbed)
3. **Read the prompt itself**, reason through your biomarkers, write the JSON answer back to `./out/raw.txt`
4. Run `bio-age <your-report> --runner skip-llm --output ./out` (parses + renders)
5. **Deliver to you**:
   - `~/Downloads/bio-age-<timestamp>/social.jpg` (1 single tall image, all 7 organs)
   - `~/Downloads/bio-age-<timestamp>/report.pdf` (9-page A4 detailed report)
   - On Telegram / Discord (via OpenClaw): both files appear directly in chat

You don't need to know about `--runner`, `--output`, file flags, or any of it. Just hand over the report and ask.

### If you want to drive it manually from a shell

```bash
bio-age path/to/your-exam.txt              # default = blind mode, outputs to ./bio-age-out/
bio-age trend t1.txt t2.txt t3.txt         # multi-timepoint comparison
bio-age standard exam.txt --runner codex   # explicit standard mode + GPT-5.5pro
```

## Quickstart

```bash
# Single snapshot, blind, render full report
bio-age blind path/to/your-exam.txt --output ./out --runner codex
open ./out/report.html
open ./out/report.pdf

# Multi-timepoint trend (auto-blind)
bio-age trend exam-2024.txt exam-2025.txt exam-2026.txt --output ./trend --runner codex

# Use the agent's own LLM (no external API call)
bio-age blind exam.txt --runner claude   # produces prompt.txt
# Claude / Codex reads prompt.txt, writes answer to raw.txt manually
bio-age blind exam.txt --runner skip-llm # parse + render
```

### Runners

| `--runner` | What it does |
|---|---|
| `claude` (default) | Two-step: emits prompt for the agent in this session to answer, then `--runner skip-llm` parses |
| `skip-llm` | Skip LLM step (assumes raw.txt already exists), only parse + render |
| `codex` | Calls `codex exec` with reasoning=high (needs OpenAI account auth) |
| `ollama:MODEL` | Calls `ollama run MODEL` (needs local Ollama install) |
| `dryrun` | Build the prompt only, don't call any model |

## Input format

A plain text file with at minimum:

```
[Basic information]
Gender: male
Age: 38                        # omit in blind mode
Ethnicity: ...

[Lifestyle]
Smoking: ...
Alcohol: ...
Diet: ...
Physical activity: ...

[Blood biochemistry]
Lipid: LDL 108, HDL 42, TG 72, ApoB 89
Liver: ALT 19, AST 20, GGT 10
Kidney: Cr 0.88, eGFR 78, uric acid 6.2
Metabolic: glucose 89, HbA1c 5.5, CRP 0.04, insulin 1.5

[Medical history]
...
```

Most users will paste their own annual physical PDF / OCR'd scan / lab portal export — the format is loose, the LLM tolerates messy structure. Just dump everything you have.

**Minimum data** (≥ 8 metrics → ±5 year accuracy): gender + lifestyle (smoke/drink/exercise) + lipid + liver + kidney + glucose.
**Recommended** (≥ 25 metrics → ±2 year accuracy): add ApoB, Lp(a), CRP, insulin, ferritin, vitamin D, testosterone, BP, HRV, VO2max, BMI, family history.
**Specialty bonuses** (organ-level precision): ECG / FibroScan / spirometry / Cystatin C / DEXA BMD / OGTT.

## Output

```
out/
├── prompt.txt        # actual prompt sent to the model (blind-redacted; audit trail)
├── raw.txt           # model's raw stdout
├── result.json       # normalized JSON: 7 organs + inference + estimated age
├── report.html       # polished web report
└── report.pdf        # A4 print-ready PDF (via headless Chrome)
```

## Design

The default theme is an original modern-editorial design built specifically for bio-age — clean off-white canvas, type-driven hierarchy via Inter Display, status conveyed by left-edge color stripe, generous whitespace. One organ = one PDF page = one JPG card.

To swap in an alternative aesthetic, the repo includes pre-written design briefs in `designs/` you can hand to any LLM/designer:

- `designs/01-cyberpunk-neon.md`
- `designs/02-bioluminescent.md`
- `designs/03-mission-control.md`
- `designs/04-holographic-hud.md`

They each return a single replacement `templates/styles/default.css` — no other file changes needed.

## How blind-mode works

`scripts/scrub_age.py` runs 7 categories of regex substitution:

1. `Age: X years old` / `Date of birth: YYYY-MM-DD` → removed
2. `started age 18` / `smoker since age 18` → `long-term smoker`
3. `diseases suffered for X-Y years ago` → `longstanding history`
4. `low for age` / `for [N]yo male` / `[N]-year-old` → age portion removed
5. `chronological age = X` → `chronological age (withheld)`
6. `(eGFR drop ... within one year)` → removed (relative timeline leak)
7. Generic `\bage \d+\b` final pass

What's intentionally **not** scrubbed:
- Lab values themselves (these are the inference signal)
- Disease descriptions (only the time anchors get rewritten)
- Collection dates (reveal time spacing only, not absolute age)
- BMD `% YAM` (Young Adult Mean is a fixed reference, not patient age)

Verify with the unit test suite:
```bash
python3 scripts/scrub_age.py --self-test   # 17 cases, all pass
```

## Limitations

- **Anchoring effect**: when given the chronological age, the model softens organ-age estimates by ~5 years on high-burden cases. Always cross-check with blind mode.
- **Cross-model variance**: same input → different LLMs gives ±5 year spread. For stable numbers, run 3 models and take the median.
- **Single-case statistics meaningless**: r=0.84 was on the NHANES validation set. Your individual report has higher uncertainty.
- **Not a medical diagnostic**. This is for healthspan optimization research, not clinical decisions.

## Reference

Sun et al. (2025). *A large language model approach for biological age estimation and aging intervention.* Nature Medicine. https://www.nature.com/articles/s41591-025-03856-8

## Acknowledgements

The biological-age method is the work of Sun et al. (Nature Medicine 2025). The paper-prompt template here is reproduced verbatim from the supplementary materials.

## License

MIT — see `LICENSE`.
