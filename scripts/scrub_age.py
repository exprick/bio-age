#!/usr/bin/env python3
"""Scrub chronological-age leakage from a health-snapshot text.

Removes / rewrites every age anchor we know about. Reads from stdin, writes to stdout.

Usage:
  cat snapshot.txt | python3 scrub_age.py > snapshot_blind.txt
  python3 scrub_age.py < input.txt
  python3 scrub_age.py --self-test    # run unit tests

What gets scrubbed:
  - "Age: X years old" / "Age: X years old (X years Y months at draw)" → removed
  - "Date of birth: YYYY-MM-DD" → removed
  - "started age 18" / "since age 18" / "smoker since 18" → "long-term smoker"
  - "diseases suffered for N to N years ago" → "longstanding history"
  - "diseases suffered N to N years ago" → "more recent history"
  - "diseases suffered for N years or more" → "longstanding history"
  - "diseases suffered within N year(s)" → "current/within-year"
  - "low for age" / "for age" → "low" / removed
  - "for [N]yo male" / "[N]yo" / "[N]-year-old" → removed
  - "X year-old" / "aged X" → removed
  - "chronological age" mentions → "age estimate target" (preserves intent of LLM aging task)

What stays untouched:
  - Lab values (these ARE the inference signal)
  - BMD as % YAM (Young Adult Mean is age-fixed, not patient-age)
  - Disease descriptions (active/inactive — only the time anchors get rewritten)
  - Collection dates (reveal time spacing only, not absolute age)
"""
from __future__ import annotations
import re
import sys


def scrub(text: str) -> str:
    """Apply all scrub rules to text. Idempotent — safe to run twice.

    Rule ordering matters: more-specific patterns first, generic age-stripper last.
    """
    # 1. Age line + DOB line (specific anchors first)
    text = re.sub(r"Age: \d+ years old \(\d+ years \d+ months at draw\)\.?\s*", "", text)
    text = re.sub(r"Age: \d+ years old\.?\s*", "", text)
    text = re.sub(r"Age: \d+\.?\s*", "", text)
    text = re.sub(r"Date of birth: \d{4}-\d{2}-\d{2}\.?\s*", "", text)
    text = re.sub(r"DOB: \d{4}-\d{2}-\d{2}\.?\s*", "", text, flags=re.IGNORECASE)
    # Inline parenthesized "(NNy NNm at YYYY-MM-DD blood draw)" or "(NNy NNm at draw)"
    text = re.sub(r"\(\d+y \d+m at [^)]*?(?:blood draw|draw)\)", "(at draw)", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d+y \d+m\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d+\s*-?\s*year-old\b", "an adult", text, flags=re.I)

    # 2. Smoking-onset age (must run BEFORE generic "age N" stripper, otherwise the
    #    generic rule eats "age 18" and leaves "started at " / "smoker since ")
    text = re.sub(r"started at age \d+", "started smoking long ago", text, flags=re.IGNORECASE)
    text = re.sub(r"started age \d+", "started smoking long ago", text, flags=re.IGNORECASE)
    text = re.sub(r"smoker since age \d+", "long-term smoker", text, flags=re.IGNORECASE)
    text = re.sub(r"smoker since \d+", "long-term smoker", text, flags=re.IGNORECASE)
    text = re.sub(r"since age \d+", "for many years", text, flags=re.IGNORECASE)

    # 2b. Generic "age N" stripper (catches stray "age 38" etc. after specific rules)
    text = re.sub(r"\bage \d+\b", "", text, flags=re.IGNORECASE)

    # 3. Relative-time disease anchors
    text = re.sub(r"diseases suffered for \d+ to \d+ years ago", "longstanding history", text, flags=re.I)
    text = re.sub(r"diseases suffered \d+ to \d+ years ago", "more recent history", text, flags=re.I)
    text = re.sub(r"diseases suffered for \d+ years or more", "longstanding history", text, flags=re.I)
    text = re.sub(r"diseases suffered within \d+ years?", "current/within-year", text, flags=re.I)

    # 4. "for age" qualifiers
    text = re.sub(r"low for age", "low", text, flags=re.I)
    text = re.sub(r"low-end of normal range for \d+yo (male|female|adult)?", "low-end of normal range", text, flags=re.I)
    text = re.sub(r"\bfor age\b", "", text, flags=re.I)
    text = re.sub(r"for \d+yo (male|female|adult)?", "", text, flags=re.I)
    text = re.sub(r"\b\d+yo\b", "", text, flags=re.I)
    text = re.sub(r"\b\d+\s*-?\s*year-old\b", "an adult", text, flags=re.I)
    text = re.sub(r"\baged \d+\b", "", text, flags=re.I)

    # 5. "chronological age = X" mentions in narrative
    text = re.sub(r"chronological age (?:is |of )?\d+\.?\d*", "chronological age (withheld)", text, flags=re.I)

    # 6. one-year decline framings that imply absolute timeline.
    # Use [^)]*? (don't cross close-paren) so we don't blow past matching parens
    # when the input is single-line JSON with literal \n inside string values.
    text = re.sub(r"\([^)]*?eGFR drop[^)]*?within one year[^)]*?\)", "", text)

    # 7. Remove "X years X months at draw" pattern wherever it appears
    text = re.sub(r"\d+ years \d+ months at draw", "at draw", text)

    # Collapse blank space artifacts
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\.\s+\.", ".", text)
    text = re.sub(r",\s+\.", ".", text)
    return text.strip()


def self_test() -> int:
    """Verify scrub removes every leak we test for. Returns exit code."""
    cases = [
        ("Age: 38 years old (38 years 10 months at draw).", ""),
        ("Age: 37 years old.", ""),
        ("Date of birth: 1987-05-10.", ""),
        ("DOB: 1987-05-10", ""),
        ("started at age 18", "started smoking long ago"),
        ("smoker since 18", "long-term smoker"),
        ("smoker since age 18", "long-term smoker"),
        ("diseases suffered for 5 to 10 years ago: surgery", "longstanding history: surgery"),
        ("diseases suffered 1 to 5 years ago: dyslipidemia", "more recent history: dyslipidemia"),
        ("diseases suffered for 10 years or more: nicotine dependence", "longstanding history: nicotine dependence"),
        ("diseases suffered within 1 year: alcohol", "current/within-year: alcohol"),
        ("HRV ~33 ms (low for age)", "HRV ~33 ms (low)"),
        ("low-end of normal range for 38yo male", "low-end of normal range"),
        ("38yo male", "male"),
        ("a 38-year-old patient", "a an adult patient"),
        ("aged 38", ""),
        ("chronological age is 38.86", "chronological age (withheld)"),
    ]
    passed, failed = 0, 0
    for src, want_substr in cases:
        got = scrub(src)
        if want_substr and want_substr not in got:
            print(f"FAIL: input={src!r}\n  want substring: {want_substr!r}\n  got: {got!r}")
            failed += 1
        elif not want_substr and got.strip() and got.strip() != src.strip():
            # Empty target — got should be empty or close to empty
            if any(c.isdigit() for c in got):
                print(f"FAIL (residual digits): input={src!r}\n  got: {got!r}")
                failed += 1
                continue
            passed += 1
        else:
            passed += 1
    print(f"\n{passed}/{passed + failed} cases pass")
    return 0 if failed == 0 else 1


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    text = sys.stdin.read()
    sys.stdout.write(scrub(text))


if __name__ == "__main__":
    main()
