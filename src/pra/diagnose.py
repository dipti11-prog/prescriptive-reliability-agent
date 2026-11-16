"""
diagnose.py - match the observed symptom pattern to FMEA failure modes.

Think of it like a reliability engineer reading trends:
  "DE vibration up AND DE bearing temp up, NDE barely moved, axial normal
   -> looks like DE bearing wear, not misalignment."

For every failure mode we score:
  SUPPORT    - do the expected symptoms appear, in the expected direction?
               (weighted: primary symptoms count more than secondary ones)
  CONTRADICT - does an expected symptom move the OPPOSITE way? (penalty)
  EXPLAINED  - how much of the total abnormality does this failure mode explain?
               A failure mode that leaves big deviations unexplained is less likely.

match_score = support x (0.2 + 0.8 x explained)   ->  0 ... 1
Every number is traceable to sensor evidence: no black box.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import load_asset, load_fmea

Z_NOTICE = 2.5     # a sensor counts as "moved" beyond this many robust std devs
Z_FULL = 6.0       # at or beyond this, evidence counts fully
Z_CAP = 25.0       # cap so one huge deviation can't swamp everything
M_NOTICE = 0.02    # engineering significance: share of alarm margin used ...
M_FULL = 0.15      # ... from which evidence counts fully


@dataclass
class Evidence:
    sensor: str
    label: str
    expected: str          # "up" / "down"
    weight: float
    z: float
    verdict: str           # "supports" / "contradicts" / "not seen"


@dataclass
class Hypothesis:
    fm_id: str
    name: str
    match_score: float
    likelihood: float = 0.0               # share among all hypotheses (sums to 1)
    support: float = 0.0
    explained: float = 0.0
    evidence: list[Evidence] = field(default_factory=list)
    unexplained: list[str] = field(default_factory=list)


def _strength(z_signed: float, m_signed: float | None = None) -> float:
    """Evidence strength 0..1 = the WEAKER of:
       statistical  - how unusual (z from Z_NOTICE to Z_FULL), and
       engineering  - how much of the alarm margin is used (M_NOTICE to M_FULL).
    A change must be both real and meaningful to count - as an engineer would judge."""
    stat = float(np.clip((z_signed - Z_NOTICE) / (Z_FULL - Z_NOTICE), 0, 1))
    if m_signed is None:
        return stat
    eng = float(np.clip((m_signed - M_NOTICE) / (M_FULL - M_NOTICE), 0, 1))
    return min(stat, eng)


def diagnose(z_row: dict[str, float], m_row: dict[str, float] | None = None,
             top_n: int = 9) -> list[Hypothesis]:
    """Rank failure modes for one snapshot.

    z_row: signed z-scores per sensor;  m_row: signed margin fractions per sensor.
    """
    labels = {k: v["label"] for k, v in load_asset()["sensors"].items()}
    z = {k: float(np.clip(v, -Z_CAP, Z_CAP)) for k, v in z_row.items() if k in labels}
    m = {k: float(v) for k, v in (m_row or {}).items() if k in labels}

    def strength(tag: str, sign: int) -> float:
        return _strength(z.get(tag, 0.0) * sign, m[tag] * sign if tag in m else None)

    # how abnormal is each sensor (in either direction)?
    abnormal = {k: max(strength(k, 1), strength(k, -1)) for k in z}
    abnormal = {k: v for k, v in abnormal.items() if v > 0}
    total_abnormal = sum(abnormal.values()) or 1e-9

    hyps: list[Hypothesis] = []
    for fm in load_fmea():
        sym = fm["symptoms"]
        wsum = sum(s["weight"] for s in sym.values())
        support = 0.0
        explained_mag = 0.0
        ev: list[Evidence] = []
        for tag, s in sym.items():
            d = 1 if s["direction"] == "up" else -1
            pos, neg = strength(tag, d), strength(tag, -d)
            if pos > 0:
                support += s["weight"] * pos
                explained_mag += abnormal.get(tag, 0.0)
                verdict = "supports"
            elif neg > 0:
                support -= s["weight"] * neg
                verdict = "contradicts"
            else:
                verdict = "not seen"
            ev.append(Evidence(tag, labels[tag], s["direction"], s["weight"],
                               round(z.get(tag, 0.0), 1), verdict))
        support = max(support / wsum, 0.0)
        explained = explained_mag / total_abnormal
        unexplained = sorted([k for k in abnormal if k not in sym], key=lambda k: -abnormal[k])
        score = support * (0.2 + 0.8 * explained)
        hyps.append(Hypothesis(fm["id"], fm["name"], round(score, 3), 0.0,
                               round(support, 3), round(explained, 3), ev, unexplained))

    # Likelihood: share among hypotheses, sharpened (power 4) so a clearly better match
    # stands out instead of being diluted by look-alike failure modes.
    tot = sum(h.match_score ** 4 for h in hyps) or 1e-9
    for h in hyps:
        h.likelihood = round(h.match_score ** 4 / tot, 3)
    hyps.sort(key=lambda h: -h.match_score)
    return hyps[:top_n]
