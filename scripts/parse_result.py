#!/usr/bin/env python3
"""Parse the LLM's raw output into a normalized JSON for rendering.

Mode-specific normalization:
  - standard / blind  → {"organs": {...7 keys...}, "inference": str, "blind": bool, "estimated_chronological_age": ?}
  - trend             → {"snapshots": [{"label","date","organs","inference"}], "estimated_chronological_age": ?, "chronological_age_confidence": str}

Adds metadata: generated_at (ISO timestamp), model (best-effort detection from raw).
"""
from __future__ import annotations
import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

ORGAN_KEYS = [
    "overall biological age",
    "cardiovascular age",
    "hepatic age",
    "pulmonary age",
    "renal age",
    "metabolic system age",
    "musculoskeletal age",
]


def extract_json(text: str) -> dict | None:
    text = re.sub(r"\x1b\[[\d;]*[A-Za-z]", "", text)  # strip ANSI
    # Try fenced ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Try first balanced {...}
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                blob = text[start : i + 1]
                try:
                    return json.loads(blob)
                except json.JSONDecodeError:
                    start = -1
    return None


def normalize_keys(d: dict) -> dict:
    return {(k.lower() if isinstance(k, str) else k): v for k, v in d.items()}


def collect_organs(d: dict) -> dict:
    """Pull the 7 organ ages out of a dict (handle paper-style 'inference process N' too)."""
    nd = normalize_keys(d)
    organs = {k: nd.get(k) for k in ORGAN_KEYS}
    # Stitch all "inference process N" into one inference string if present
    inferences = [nd.get(f"inference process {n}", "") for n in range(1, 8)]
    inf_clean = [s for s in inferences if s]
    inference = nd.get("inference") or " ".join(inf_clean)
    return {"organs": organs, "inference": inference}


def parse_standard(raw: str) -> dict:
    obj = extract_json(raw)
    if not obj:
        raise SystemExit(f"[parse_result] no JSON found in raw output")
    res = collect_organs(obj)
    res["blind"] = False
    return res


def parse_blind_single(raw: str) -> dict:
    obj = extract_json(raw)
    if not obj:
        raise SystemExit(f"[parse_result] no JSON found in raw output")
    nd = normalize_keys(obj)

    # Rich schema: organs[X] = {age, inference, plain, stop, improve, explore}
    organs = nd.get("organs")
    if isinstance(organs, dict) and any(
        isinstance(v, dict) and "age" in v for v in organs.values()
    ):
        return {
            "blind": True,
            "organs": organs,
            "estimated_chronological_age":
                nd.get("estimated_chronological_age") or nd.get("estimated chronological age"),
            "chronological_age_confidence":
                nd.get("chronological_age_confidence") or nd.get("chronological age confidence"),
        }

    # Legacy flat schema (paper prompt — organs are bare ints)
    res = collect_organs(obj)
    res["blind"] = True
    res["estimated_chronological_age"] = (
        nd.get("estimated chronological age") or nd.get("estimated_chronological_age")
    )
    res["chronological_age_confidence"] = (
        nd.get("chronological age confidence") or nd.get("chronological_age_confidence")
    )
    return res


def parse_trend(raw: str) -> dict:
    obj = extract_json(raw)
    if not obj:
        raise SystemExit(f"[parse_result] no JSON found in raw output")
    nd = normalize_keys(obj)
    snapshots = []
    for k, v in nd.items():
        if isinstance(v, dict) and k.startswith("snapshot "):
            sub = collect_organs(v)
            label = k.replace("snapshot ", "snapshot ").upper().replace("SNAPSHOT", "snapshot")  # keep label
            label_clean = k.title().replace("Snapshot ", "snapshot ")
            snapshots.append({
                "label": label_clean,
                "date": "",  # no longer in JSON; could be passed in
                "organs": sub["organs"],
                "inference": sub["inference"],
            })
    snapshots.sort(key=lambda s: s["label"])
    return {
        "blind": True,
        "snapshots": snapshots,
        "estimated_chronological_age": nd.get("estimated chronological age"),
        "chronological_age_confidence": nd.get("chronological age confidence", ""),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["standard", "blind", "trend"])
    ap.add_argument("--raw", required=True, help="path to raw model output")
    ap.add_argument("--out", required=True, help="path to write normalized JSON")
    args = ap.parse_args()

    raw = Path(args.raw).read_text()
    if args.mode == "standard":
        result = parse_standard(raw)
    elif args.mode == "blind":
        result = parse_blind_single(raw)
    else:
        result = parse_trend(raw)

    result["generated_at"] = _dt.datetime.now().isoformat(timespec="seconds")
    # Best-effort model detection
    if "gpt-5" in raw.lower() or "codex" in raw.lower():
        result["model"] = "GPT-5.5pro / codex"
    elif "claude" in raw.lower():
        result["model"] = "Claude"
    elif "gemma" in raw.lower():
        result["model"] = "Gemma"
    elif "llama" in raw.lower():
        result["model"] = "Llama"
    else:
        result.setdefault("model", "—")

    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"[parse_result] wrote {args.out}")


if __name__ == "__main__":
    main()
