#!/usr/bin/env python3
"""Render bio-age rich result → multi-page HTML (one organ per page) → PDF/JPG.

Input JSON schema (rich):
  {
    "organs": {
      "<organ key>": {
        "age": int,
        "inference": str,
        "plain": str,
        "stop": [str, ...],
        "improve": [str, ...],
        "explore": [str, ...]
      }, ...  (7 organs)
    },
    "estimated_chronological_age": int,
    "chronological_age_confidence": str,
    "generated_at": str,
    "model": str
  }

Output:
  PDF: 9 pages — cover + 7 organ pages + methodology
  HTML: same structure, screen view
"""
from __future__ import annotations
import argparse
import datetime as _dt
import html as html_mod
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSS = ROOT / "templates" / "styles" / "default.css"

ORGAN_ORDER = [
    ("overall biological age",   "整体",   "OVERALL"),
    ("cardiovascular age",        "心血管", "CARDIOVASCULAR"),
    ("hepatic age",               "肝",     "HEPATIC"),
    ("pulmonary age",             "肺",     "PULMONARY"),
    ("renal age",                 "肾",     "RENAL"),
    ("metabolic system age",      "代谢",   "METABOLIC"),
    ("musculoskeletal age",       "肌骨",   "MUSCULOSKELETAL"),
]

REPO_URL    = "github.com/exprick/bio-age"
PAPER_URL   = "nature.com/articles/s41591-025-03856-8"
PAPER_FULL  = "Sun et al. (2025). A large language model approach for biological age estimation and aging intervention. Nature Medicine."


def status_class(age: int, ref: int) -> str:
    """Return young / on-track / aging / elderly based on delta vs reference age."""
    if age is None or ref is None:
        return "neutral"
    delta = age - ref
    if delta <= -3:    return "young"
    if delta <= 1:     return "neutral"
    if delta <= 5:     return "aging"
    return "elderly"


def status_label(age: int, ref: int) -> str:
    if age is None or ref is None:
        return ""
    delta = age - ref
    if delta <= -3:    return "比同龄更年轻"
    if delta <= 1:     return "处于同龄水平"
    if delta <= 5:     return "略偏老"
    return "明显偏老"


def fmt_delta(age: int, ref: int) -> str:
    if age is None or ref is None:
        return "—"
    delta = age - ref
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:.0f}"


def page_footer(idx: int, total: int, generated_at: str) -> str:
    return f"""<div class="page-footer">
  <div class="left">
    <span>bio-age</span>
    <span>·</span>
    <a href="https://{REPO_URL}">{REPO_URL}</a>
    <span>·</span>
    <a href="https://{PAPER_URL}">Sun et al. Nat Med 2025</a>
  </div>
  <div class="right">
    <span>{idx:02d} / {total:02d}</span>
  </div>
</div>"""


def cover_page(data: dict, total: int) -> str:
    chron = data.get("estimated_chronological_age")
    conf  = data.get("chronological_age_confidence", "")
    organs = data.get("organs", {})
    overall = organs.get("overall biological age", {}).get("age")

    # Eyebrow line
    today = _dt.datetime.now().strftime("%Y-%m-%d")
    eyebrow = f"""<div class="eyebrow">
  <div class="left"><span class="index">01</span><span>封面</span></div>
  <div class="right"><span>bio-age · 生物标志物推断</span><span>{today}</span></div>
</div>"""

    # Hero
    hero_block = f"""<h1 class="cover-title">生理年龄报告</h1>
<p class="cover-lede">基于一份体检快照，由 LLM 在<strong>不知道实际年龄</strong>的前提下，纯靠生物标志物推断 7 个器官系统的生理年龄，并反推你的实际年龄。把反推结果对比你的真实年龄，即可判断模型估计的可信度。</p>

<div class="hero-age">
  <div class="num">{overall if overall is not None else '—'}</div>
  <div class="meta">
    <p class="label">整体生理年龄 · OVERALL</p>
    <p class="estimate">反推年龄 {chron if chron else '—'} 岁</p>
    <p class="conf">{html_mod.escape(conf)}</p>
  </div>
</div>"""

    # Summary grid (7 organs)
    cells = []
    for key, cn, en in ORGAN_ORDER:
        organ = organs.get(key, {})
        age = organ.get("age")
        cls = status_class(age, chron) if chron else "neutral"
        delta = fmt_delta(age, chron) if chron else ""
        cells.append(f"""<div class="summary-cell {cls}">
  <p class="organ">{cn}<span class="organ-en">{en}</span></p>
  <p class="age-num">{age if age is not None else '—'}</p>
  <p class="delta">{delta}</p>
</div>""")

    summary = f"""<div class="cover-summary">
<p class="summary-title">7 个器官系统 · ORGAN SYSTEMS</p>
<div class="summary-grid">{''.join(cells)}</div>
</div>"""

    return f"""<section class="page cover-page">
{eyebrow}
{hero_block}
{summary}
{page_footer(1, total, data.get('generated_at',''))}
</section>"""


def organ_page(idx: int, total: int, data: dict, organ_key: str, organ_cn: str, organ_en: str) -> str:
    organ = data.get("organs", {}).get(organ_key, {})
    age = organ.get("age")
    chron = data.get("estimated_chronological_age")
    plain = organ.get("plain", "")
    stop_items = organ.get("stop", []) or []
    improve_items = organ.get("improve", []) or []
    explore_items = organ.get("explore", []) or []

    cls = status_class(age, chron) if chron else "neutral"
    label = status_label(age, chron) if chron else ""
    delta = fmt_delta(age, chron) if chron else "—"

    eyebrow = f"""<div class="eyebrow">
  <div class="left"><span class="index">{idx:02d}</span><span>器官 {idx-1} / 7</span></div>
  <div class="right"><span>{organ_en}</span></div>
</div>"""

    head = f"""<div class="head">
  <h2 class="organ-cn">{organ_cn}</h2>
  <p class="organ-en">{organ_en}</p>
</div>"""

    hero = f"""<div class="organ-hero">
  <div class="num">{age if age is not None else '—'}</div>
  <div class="meta">
    <p class="delta-line">反推年龄 {chron if chron else '—'} 岁 <span class="delta-num">·  {delta}</span></p>
    <p class="status">{label}</p>
  </div>
</div>"""

    plain_html = f'<p class="organ-plain">{html_mod.escape(plain)}</p>' if plain else ""

    def render_list(name: str, en_name: str, items: list) -> str:
        if not items:
            return ""
        lis = "".join(f'<li>{html_mod.escape(s)}</li>' for s in items)
        return f"""<div class="action-group">
  <div class="action-head">
    <span class="action-name">{name}</span>
    <span class="action-en">{en_name}</span>
    <span class="action-count">{len(items):02d}</span>
  </div>
  <ul class="action-list">{lis}</ul>
</div>"""

    actions = f"""<div class="actions">
{render_list("止损", "STOP", stop_items)}
{render_list("改善", "IMPROVE", improve_items)}
{render_list("探索", "EXPLORE", explore_items)}
</div>"""

    return f"""<section class="page organ-page {cls}">
{eyebrow}
{head}
{hero}
{plain_html}
{actions}
{page_footer(idx, total, data.get('generated_at',''))}
</section>"""


def methodology_page(idx: int, total: int, data: dict) -> str:
    today = _dt.datetime.now().strftime("%Y-%m-%d")
    eyebrow = f"""<div class="eyebrow">
  <div class="left"><span class="index">{idx:02d}</span><span>方法与出处</span></div>
  <div class="right"><span>{today}</span></div>
</div>"""

    body = f"""<h2 class="cover-title" style="margin-bottom:64px">方法与出处 · METHODOLOGY</h2>

<div class="method-block">
  <p class="label">论文方法 · METHOD</p>
  <p class="body">{PAPER_FULL} <a href="https://{PAPER_URL}">{PAPER_URL}</a></p>
  <p class="body">本工具完整复现论文 prompt（自带补充材料）。每个器官系统年龄由 LLM 在 zero-shot 模式下推断，不做任何 fine-tune、不做特征工程。论文在 NHANES 验证集上与既有衰老时钟相关性 r=0.84。</p>
</div>

<div class="method-block">
  <p class="label">Skill 仓库 · SKILL</p>
  <p class="body"><a href="https://{REPO_URL}">{REPO_URL}</a></p>
  <p class="body">Cross-vendor skill，Claude Code / Codex / OpenClaw 都可调用，谁调用谁出推理。默认 <strong>blind 模式</strong>：先把实际年龄从输入里抹掉，让模型纯靠生物标志物推断器官年龄并反推实际年龄；用户拿真实年龄一对比就能判断准确度。MIT 协议开源。</p>
</div>

<div class="method-block">
  <p class="label">运行元数据 · METADATA</p>
  <p class="meta">model = {html_mod.escape(data.get('model', '—'))}</p>
  <p class="meta">generated_at = {html_mod.escape(data.get('generated_at', ''))}</p>
  <p class="meta">est_chronological_age = {data.get('estimated_chronological_age', '—')}</p>
</div>

<div class="method-block">
  <p class="label">免责声明 · DISCLAIMER</p>
  <p class="body">仅供研究与个人参考。这是 LLM 推断结果，<strong>不是医疗诊断</strong>，不能用于临床决策。任何健康问题请咨询合格的医疗专业人员。</p>
</div>"""

    return f"""<section class="page method-page">
{eyebrow}
{body}
{page_footer(idx, total, data.get('generated_at',''))}
</section>"""


def build_html(data: dict, css: str) -> str:
    pages = []
    total = 1 + len(ORGAN_ORDER) + 1   # cover + 7 organs + methodology
    pages.append(cover_page(data, total))
    for i, (key, cn, en) in enumerate(ORGAN_ORDER, start=2):
        pages.append(organ_page(i, total, data, key, cn, en))
    pages.append(methodology_page(total, total, data))

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>bio-age report</title>
<style>
{css}
</style>
</head>
<body>
{''.join(pages)}
</body>
</html>
"""


def html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    chrome_candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/usr/bin/google-chrome",
        "google-chrome",
        "chromium",
    ]
    chrome = next((c for c in chrome_candidates if Path(c).exists() or shutil.which(c)), None)
    if not chrome:
        print("[render_report] no Chrome found; skipping PDF", file=sys.stderr)
        return False
    # Use a temp profile dir to avoid contention with the user's running Chrome instance
    import tempfile
    with tempfile.TemporaryDirectory(prefix="bio-age-chrome-") as profile_dir:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--no-sandbox",
            "--single-process",      # avoid zombie GPU/renderer subprocesses
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={pdf_path}",
            f"file://{html_path.resolve()}",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print("[render_report] Chrome timed out (120s) — try again or check Chrome install", file=sys.stderr)
            return False
    if proc.returncode != 0 and not pdf_path.exists():
        print(f"[render_report] PDF render failed: {proc.stderr}", file=sys.stderr)
        return False
    return True


def build_social_html(data: dict, css: str) -> str:
    """Compact 1080-wide single-page social card — all 7 organs in one tall image."""
    chron   = data.get("estimated_chronological_age")
    conf    = data.get("chronological_age_confidence", "")
    organs  = data.get("organs", {})
    overall = organs.get("overall biological age", {}).get("age")
    today   = _dt.datetime.now().strftime("%Y-%m-%d")

    rows = []
    for i, (key, cn, en) in enumerate(ORGAN_ORDER, start=1):
        organ = organs.get(key, {})
        age = organ.get("age")
        plain = organ.get("plain", "") or ""
        cls = status_class(age, chron) if chron else "neutral"
        label = status_label(age, chron) if chron else ""
        delta = fmt_delta(age, chron) if chron else "—"
        rows.append(f"""<div class="organ-row {cls}">
  <div class="organ-num">0{i} / 07</div>
  <div class="body">
    <div class="organ-name">
      <span class="organ-cn">{html_mod.escape(cn)}</span>
      <span class="organ-en">{html_mod.escape(en)}</span>
      <span class="status">{label}</span>
    </div>
    <p class="plain">{html_mod.escape(plain)}</p>
  </div>
  <div class="age-block">
    <div class="age-num">{age if age is not None else '—'}</div>
    <div class="age-delta">{delta}</div>
  </div>
</div>""")

    body = f"""<div class="social">
  <div class="top">
    <span class="brand">bio-age · 生理年龄报告</span>
    <span>{today}</span>
  </div>

  <div class="hero">
    <div class="num">{overall if overall is not None else '—'}</div>
    <div class="meta">
      <p class="label">整体生理年龄 · OVERALL</p>
      <p class="estimate">反推年龄 {chron if chron else '—'} 岁</p>
      <p class="conf">{html_mod.escape(conf)}</p>
    </div>
  </div>

  {''.join(rows)}

  <div class="footer">
    <div class="left">
      <p><strong>方法</strong> · Sun et al. (2025) <em>A large language model approach for biological age estimation and aging intervention.</em> Nature Medicine</p>
      <p><strong>Skill</strong> · <a href="https://{REPO_URL}">{REPO_URL}</a> · MIT</p>
      <p>Blind 模式：模型不知道实际年龄，纯靠生物标志物推断 7 器官年龄 + 反猜年龄。</p>
    </div>
    <div class="right">
      仅供研究参考<br>非医疗诊断
    </div>
  </div>
</div>"""

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080,initial-scale=1">
<title>bio-age · social card</title>
<style>
{css}
</style>
</head>
<body class="social-card">
{body}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", default="-")
    ap.add_argument("--html", default="./bio-age-report.html")
    ap.add_argument("--pdf", default=None)
    ap.add_argument("--social-html", default=None, help="optional: write single-page social card HTML to this path")
    ap.add_argument("--social-pdf", default=None, help="optional: render social card to a single-page tall PDF")
    ap.add_argument("--css", default=str(DEFAULT_CSS))
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input).read_text())

    # Ensure metadata exists
    data.setdefault("generated_at", _dt.datetime.now().isoformat(timespec="seconds"))
    data.setdefault("model", "Claude (current session)")

    css = Path(args.css).read_text() if Path(args.css).exists() else ""

    # 1) Multi-page report (PDF source)
    html = build_html(data, css)
    html_path = Path(args.html).resolve()
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html)
    print(f"[render_report] HTML → {html_path} ({len(html)} chars)")

    if not args.no_pdf:
        pdf_path = Path(args.pdf) if args.pdf else html_path.with_suffix(".pdf")
        ok = html_to_pdf(html_path, pdf_path)
        if ok:
            print(f"[render_report] PDF → {pdf_path}")

    # 2) Social card (single tall page → PDF → JPG)
    if args.social_html or args.social_pdf:
        sh = build_social_html(data, css)
        social_html_path = Path(args.social_html) if args.social_html else html_path.with_name("social.html")
        social_html_path.write_text(sh)
        print(f"[render_report] social HTML → {social_html_path} ({len(sh)} chars)")
        if args.social_pdf:
            social_pdf_path = Path(args.social_pdf)
            ok = html_to_pdf_custom(social_html_path, social_pdf_path, page_size="1080px 2400px")
            if ok:
                print(f"[render_report] social PDF → {social_pdf_path}")


def html_to_pdf_custom(html_path: Path, pdf_path: Path, page_size: str = "1080px 2400px") -> bool:
    """Render HTML to a single-page PDF with custom page size (for social card)."""
    chrome_candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/usr/bin/google-chrome",
        "google-chrome",
        "chromium",
    ]
    chrome = next((c for c in chrome_candidates if Path(c).exists() or shutil.which(c)), None)
    if not chrome:
        print("[render_report] no Chrome found; skipping social PDF", file=sys.stderr)
        return False

    # Inject @page rule with the custom size into the HTML's existing <style>
    import tempfile
    html_text = html_path.read_text()
    width_str, height_str = page_size.split()
    width_px = int(width_str.rstrip("px"))
    height_px = int(height_str.rstrip("px"))
    width_in = width_px / 96.0    # CSS px → inches @ 96 dpi
    height_in = height_px / 96.0

    with tempfile.TemporaryDirectory(prefix="bio-age-chrome-") as profile_dir:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--no-sandbox",
            "--single-process",      # avoid zombie GPU/renderer subprocesses
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={pdf_path}",
            f"--virtual-time-budget=2000",
            f"--window-size={width_px},{height_px}",
            f"file://{html_path.resolve()}",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            print("[render_report] Chrome timed out (social card)", file=sys.stderr)
            return False
    if proc.returncode != 0 and not pdf_path.exists():
        print(f"[render_report] social PDF failed: {proc.stderr}", file=sys.stderr)
        return False
    return True


if __name__ == "__main__":
    main()
