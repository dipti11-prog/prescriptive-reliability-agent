"""
history.py - maintenance work-order history: generate (synthetic) and search.

Real CMMS data is messy: free text, inconsistent codes, some records not coded at
all. We mimic that, then use text search (TF-IDF) so the agent can find similar
past jobs even when the failure code is missing - a common real-world problem.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import ROOT, fmea_by_id

WO_PATH = ROOT / "data" / "work_orders.csv"

# Free-text phrasing variants per failure mode (how technicians actually write).
TEXT = {
    "FM01": [("DE brg high vib + temp", "DE journal bearing vibration trending up, bearing temp high. Bearing replaced, babbitt wiped, oil sample showed high particle count."),
             ("K brg DE replaced", "Radial bearing DE found worn on inspection, clearance above OEM limit. New pads fitted. Lube oil changed."),
             ("High vibration drive end", "Vibration alarm DE probes. Shaft centreline shift. Bearing pads scored - replaced. Recommend oil cleanliness review.")],
    "FM02": [("LO temp high", "Lube oil supply temperature high in afternoon. Cooler tubes fouled, cleaned. All bearing temps returned to normal."),
             ("LO cooler cleaning", "Fin fan lube oil cooler dirty, approach temp high. Cleaned and TCV checked.")],
    "FM03": [("Coupling misalignment", "High 2x vibration and axial vib. Hot alignment found out of tolerance, corrected. Coupling shims replaced."),
             ("Realign motor-compressor", "Alignment correction after baseplate settlement. Soft foot found at NDE motor foot.")],
    "FM04": [("Rotor 1x vib high", "1x vibration high both ends after scrubber upset. Rotor removed, deposits found on impellers, cleaned and balanced."),
             ("Imbalance - online wash", "Vibration rose both bearings, liquid carry-over suspected. Online wash performed, vibration reduced.")],
    "FM05": [("Compressor efficiency low", "Polytropic efficiency down 5%, discharge temp high. Offline wash of impellers, salt deposits."),
             ("Performance degradation", "Head and efficiency loss trend. Fouling confirmed at inspection. Improve inlet separator.")],
    "FM06": [("DGS primary vent high", "Primary vent flow increasing, seal gas DP dropping. DGS cartridge replaced. Seal gas filter found bypassed."),
             ("Seal gas leak NDE", "Dry gas seal leakage NDE, faces damaged by liquids in seal gas. Seal replaced, heater repaired.")],
    "FM07": [("Thrust brg temp high", "Thrust pad temperature high and axial position shift after surge event. Thrust bearing replaced, balance piston seal worn."),
             ("Axial displacement alarm", "Axial position trending towards alarm. Thrust bearing wear found, pads replaced.")],
    "FM08": [("ASV passing", "Recycle valve passing - downstream pipe hot with valve shut. Trim overhauled, positioner recalibrated."),
             ("Recycle valve leak-by", "Anti-surge valve leak by, power high for throughput. Seat lapped.")],
    "FM09": [("Suction strainer DP high", "Suction pressure low, strainer blocked with scale. Element cleaned."),
             ("Strainer cleaning", "Debris in suction strainer after pipeline pigging. Cleaned and DP gauge replaced.")],
    None: [("PM - lube oil sample", "Routine 3-monthly oil sample. Results normal."),
           ("PM - vibration route", "Monthly vibration and thermography route. No issues."),
           ("Instrument calibration", "Calibrated PT/TT loops on compressor skid."),
           ("PM - DGS filter change", "Seal gas filter elements changed per schedule.")],
}

# Plant shorthand -> plain words, so text search understands technician notes.
ABBREV = {
    r"\bbrg\b": "bearing", r"\bvib\b": "vibration", r"\blo\b": "lube oil",
    r"\bdgs\b": "dry gas seal", r"\basv\b": "anti-surge recycle valve",
    r"\bde\b": "drive end", r"\bnde\b": "non drive end", r"\btcv\b": "temperature control valve",
    r"\bdp\b": "differential pressure", r"\bpm\b": "preventive maintenance",
    r"\b1x\b": "1x imbalance", r"\b2x\b": "2x misalignment", r"\btemp\b": "temperature",
    r"\bk\b": "compressor",
}


def normalise(text: str) -> str:
    import re
    t = text.lower()
    for pat, rep in ABBREV.items():
        t = re.sub(pat, rep, t)
    return t


COST = {"FM01": (40e3, 36), "FM02": (8e3, 6), "FM03": (25e3, 24), "FM04": (60e3, 48),
        "FM05": (30e3, 24), "FM06": (120e3, 60), "FM07": (90e3, 48), "FM08": (15e3, 8),
        "FM09": (5e3, 4), None: (1.5e3, 0)}


def generate_work_orders(seed: int = 7) -> pd.DataFrame:
    """~5 years of history for three sister compressors."""
    rng = np.random.default_rng(seed)
    fm = fmea_by_id()
    rows = []
    # Hand-placed failures so the demo has a story: K-101 is a DE-bearing bad actor.
    planned = [("K-101", "2022-03-14", "FM06"), ("K-101", "2024-02-02", "FM01"),
               ("K-101", "2025-06-19", "FM01"), ("K-101", "2023-08-30", "FM02"),
               ("K-102", "2023-05-11", "FM03"), ("K-102", "2025-01-09", "FM04"),
               ("K-102", "2024-09-22", "FM07"), ("K-201", "2022-11-03", "FM05"),
               ("K-201", "2024-04-17", "FM09"), ("K-201", "2025-10-05", "FM08"),
               ("K-201", "2023-12-12", "FM01"), ("K-102", "2026-03-03", "FM06")]
    for eq, date, f in planned:
        rows.append((eq, pd.Timestamp(date), f))
    # Routine PMs
    for eq in ("K-101", "K-102", "K-201"):
        for d in pd.date_range("2021-11-01", "2026-08-31", freq="45D"):
            rows.append((eq, d + pd.Timedelta(days=int(rng.integers(0, 10))), None))

    out = []
    for i, (eq, date, f) in enumerate(sorted(rows, key=lambda r: r[1])):
        short, long = TEXT[f][int(rng.integers(0, len(TEXT[f])))]
        cost, down = COST[f]
        coded = f is not None and rng.random() > 0.3        # ~30 % of failures left uncoded
        out.append({
            "wo_id": f"WO{400100 + i}",
            "date": date.date().isoformat(),
            "equipment": eq,
            "notif_type": "M2" if f else "M1",
            "short_text": short,
            "long_text": long,
            "damage_code": fm[f]["sap_damage_code"] if coded else "",
            "cause_code": fm[f]["sap_cause_code"] if coded else "",
            "fm_id_coded": f if coded else "",
            "fm_id_true": f or "",                           # hidden truth, for evaluation only
            "downtime_h": round(down * rng.uniform(0.7, 1.3), 1) if f else 0.0,
            "cost_usd": round(cost * rng.uniform(0.7, 1.4), -2),
        })
    return pd.DataFrame(out)


def load_work_orders() -> pd.DataFrame:
    if not WO_PATH.exists():
        WO_PATH.parent.mkdir(parents=True, exist_ok=True)
        generate_work_orders().to_csv(WO_PATH, index=False)
    return pd.read_csv(WO_PATH, keep_default_na=False)


def similar_work_orders(fm_id: str, k: int = 5, min_sim: float = 0.10) -> pd.DataFrame:
    """Text-search the history for jobs that look like this failure mode."""
    wo = load_work_orders()
    fm = fmea_by_id()[fm_id]
    query = " ".join([fm["name"], fm["component"], fm.get("keywords", ""), fm.get("keywords", ""), " ".join(fm["causes"]),
                      " ".join(s.replace("_", " ") for s in fm["symptoms"])])
    docs = [normalise(d) for d in (wo["short_text"] + ". " + wo["long_text"])]
    query = normalise(query)
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    m = vec.fit_transform(docs + [query])
    sim = cosine_similarity(m[-1], m[:-1]).ravel()
    wo = wo.assign(similarity=sim.round(3))
    hits = wo[(wo["similarity"] >= min_sim) & (wo["notif_type"] == "M2")]
    return hits.sort_values("similarity", ascending=False).head(k)


def recurrence(fm_id: str, equipment: str, months: int = 36,
               as_of: str | pd.Timestamp = "2026-11-01") -> dict:
    """How often has this failure mode hit this machine? Combines coded records
    with uncoded records found by text search (a 'bad actor' check)."""
    wo = load_work_orders()
    as_of = pd.Timestamp(as_of)
    window = wo[(pd.to_datetime(wo["date"]) >= as_of - pd.DateOffset(months=months)) &
                (wo["equipment"] == equipment)]
    coded = window[window["fm_id_coded"] == fm_id]
    text_hits = similar_work_orders(fm_id, k=50, min_sim=0.18)
    text_hits = text_hits[text_hits["wo_id"].isin(window["wo_id"]) &
                          (text_hits["fm_id_coded"] == "")]
    events = pd.concat([coded, text_hits]).drop_duplicates("wo_id")
    return {
        "count": int(len(events)),
        "coded": int(len(coded)),
        "found_by_text_only": int(len(text_hits)),
        "total_cost_usd": float(events["cost_usd"].sum()),
        "total_downtime_h": float(events["downtime_h"].sum()),
        "wo_ids": events["wo_id"].tolist(),
        "dates": events["date"].tolist(),
        "bad_actor": len(events) >= 2,
    }
