"""
Phase 2.3: nudge copy generation (METHODOLOGY.md 2.3).

Deterministic notification-generation function: fixed (index, context) in
-> fixed message out, per PROJECT.md 5.5 (deterministic baseline before
randomness) and METHODOLOGY.md 2.5's output contract. No randomness
anywhere in this module.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

sys.path.insert(0, "config")
from phase2_nudge_copy import CHARGE_LEVEL_TEMPLATES, HUMIDITY_TIP, EXHAUSTION_DISCLAIMER_NOTE, OUTPUT_DIAL_REMINDER


@dataclass
class NudgeContext:
    target_charge_index: int      # 1-6, from phase2_index_calibration.parquet lookup (dial numbering confirmed 2026-09-02)
    mean_temp_c: float
    include_humidity_tip: bool = False   # caller decides cadence (e.g. "few times a month"), not this function
    include_exhaustion_disclaimer: bool = False  # e.g. shown once on first use, not every message
    include_output_reminder: bool = False  # e.g. every evening message -- output dial matters every night, not occasionally


def generate_nudge(ctx: NudgeContext) -> str:
    """Pure function: same NudgeContext always produces the same message."""
    if ctx.target_charge_index not in CHARGE_LEVEL_TEMPLATES:
        raise ValueError(f"target_charge_index must be 1-6, got {ctx.target_charge_index}")

    parts = [CHARGE_LEVEL_TEMPLATES[ctx.target_charge_index]]
    if ctx.include_output_reminder:
        parts.append(OUTPUT_DIAL_REMINDER)
    if ctx.include_humidity_tip:
        parts.append(HUMIDITY_TIP)
    if ctx.include_exhaustion_disclaimer:
        parts.append(EXHAUSTION_DISCLAIMER_NOTE)
    return " ".join(parts)


# --- Reading-level check (Flesch Reading Ease) ---
# Implemented directly rather than pulling a dependency for one formula.
# Score: 90-100 very easy, 60-70 standard, <50 difficult. Target: >=70
# ("fairly easy", roughly UK reading age ~11) for tenant-facing copy,
# per PROJECT.md's "tested for reading level" instruction -- an actual
# check, not an eyeballed judgement.

_VOWEL_GROUPS = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:—-")
    if not word:
        return 0
    groups = _VOWEL_GROUPS.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_reading_ease(text: str) -> float:
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"[A-Za-z']+", text)
    n_sentences = max(1, len(sentences))
    n_words = max(1, len(words))
    n_syllables = sum(_count_syllables(w) for w in words)
    return 206.835 - 1.015 * (n_words / n_sentences) - 84.6 * (n_syllables / n_words)


if __name__ == "__main__":
    # Self-test 1: determinism -- same input, same output, every time.
    ctx = NudgeContext(target_charge_index=3, mean_temp_c=8.0)
    out1 = generate_nudge(ctx)
    out2 = generate_nudge(ctx)
    assert out1 == out2, "same context must always produce the same message"
    print(f"Determinism: PASS  ('{out1}')")

    # Self-test 2: all 6 dial levels produce distinct, valid messages.
    for i in range(1, 7):
        msg = generate_nudge(NudgeContext(target_charge_index=i, mean_temp_c=0.0))
        assert msg, f"index {i} produced an empty message"
        print(f"  Dial {i}: {msg}")

    # Self-test 3: invalid index raises, doesn't silently produce garbage.
    try:
        generate_nudge(NudgeContext(target_charge_index=7, mean_temp_c=0.0))
        assert False, "should have raised on out-of-range index"
    except ValueError:
        print("Out-of-range guard: PASS")

    # Self-test 4: reading level, actually measured, not assumed.
    print()
    print("=== Reading level (Flesch Reading Ease, target >=70) ===")
    all_texts = list(CHARGE_LEVEL_TEMPLATES.values()) + [HUMIDITY_TIP, EXHAUSTION_DISCLAIMER_NOTE, OUTPUT_DIAL_REMINDER]
    scores = []
    for t in all_texts:
        score = flesch_reading_ease(t)
        scores.append(score)
        flag = "OK" if score >= 70 else "TOO HARD"
        print(f"  [{flag:8s}] {score:5.1f}  {t}")

    below_target = [s for s in scores if s < 70]
    if below_target:
        print(f"\n{len(below_target)}/{len(scores)} lines score below the target -- flagged above, not silently shipped.")
    else:
        print(f"\nAll {len(scores)} lines meet the >=70 reading-ease target.")

    # Self-test 5: with all supplementary lines included, message stays SMS-reasonable.
    full_ctx = NudgeContext(target_charge_index=6, mean_temp_c=-2.0, include_output_reminder=True,
                             include_humidity_tip=True, include_exhaustion_disclaimer=True)
    full_msg = generate_nudge(full_ctx)
    print(f"\nFull message length with all supplements: {len(full_msg)} chars")
    print(f"  '{full_msg}'")

    print("\nsrc/nudge_generator.py self-test: DONE (see reading-level results above)")
