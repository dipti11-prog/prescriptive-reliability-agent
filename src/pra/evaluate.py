"""
evaluate.py - does the agent get it right?

Runs every injected fault x N random seeds, plus healthy machines, and scores:
  - detection rate and false alarms
  - detection lead time: days from first alert until the sensor would hit its ALARM limit
    (how much earlier than the plant's own alarm system we know)
  - diagnosis accuracy: top-1 and top-3, at first alert and at alert + 3 days
  - how often the agent correctly flags itself as unsure (ambiguous) when it is wrong
"""
from __future__ import annotations

import pandas as pd

from . import agent, detect, diagnose as dx
from .config import load_asset
from .simulate import FAULTS, simulate


def alarm_crossing(df: pd.DataFrame) -> pd.Timestamp | None:
    """When the plant's conventional alarm (fixed limit) would first go off."""
    sens = load_asset()["sensors"]
    first = None
    for tag, s in sens.items():
        if s.get("alarm") is None:
            continue
        x = df[tag].rolling("1h", min_periods=1).mean()
        hit = x >= s["alarm"] if s["direction"] == "high" else x <= s["alarm"]
        if hit.any():
            ts = hit.idxmax()
            first = ts if first is None or ts < first else first
    return first


def run_eval(seeds: int = 5) -> tuple[pd.DataFrame, dict]:
    rows = []
    for fault in [None] + list(FAULTS):
        for seed in range(seeds):
            df = simulate(fault, seed=1000 + seed)   # held-out seeds, never used while tuning
            z = detect.zscores(df)
            mf = detect.margin_fraction(df)
            alert = detect.first_alert(z, mf)
            row = {"fault": fault or "healthy", "seed": seed, "detected": alert is not None}
            if fault is None:
                rows.append(row)
                continue
            exp = FAULTS[fault]["expected_fm"]
            row["expected"] = exp
            if alert is not None:
                onset = df.index[0] + pd.Timedelta(days=38)
                row["days_onset_to_alert"] = round((alert.timestamp - onset).total_seconds() / 86400, 1)
                alarm = alarm_crossing(df)
                row["lead_vs_alarm_days"] = (round((alarm - alert.timestamp).total_seconds() / 86400, 1)
                                             if alarm is not None else None)
                h0 = dx.diagnose(z.loc[alert.timestamp].to_dict(), mf.loc[alert.timestamp].to_dict())
                row["top1_at_alert"] = h0[0].fm_id == exp
                row["top3_at_alert"] = exp in [h.fm_id for h in h0[:3]]
                p = agent.run(df)
                row["predicted"] = p.diagnosis["fm_id"]
                row["top1_at_3d"] = p.diagnosis["fm_id"] == exp
                row["top3_at_3d"] = exp in [h["fm_id"] for h in p.hypotheses[:3]]
                row["flagged_ambiguous"] = p.ambiguous
                row["priority"] = p.priority["level"]
            rows.append(row)
    res = pd.DataFrame(rows)
    f = res[res["fault"] != "healthy"]
    wrong = f[~f["top1_at_3d"].astype(bool)]
    summary = {
        "fault_cases": len(f),
        "healthy_cases": int((res["fault"] == "healthy").sum()),
        "detection_rate": round(f["detected"].mean(), 3),
        "false_alarm_rate": round(res[res["fault"] == "healthy"]["detected"].mean(), 3),
        "median_days_onset_to_alert": float(f["days_onset_to_alert"].median()),
        "median_lead_vs_alarm_days": float(f["lead_vs_alarm_days"].dropna().median()),
        "top1_at_alert": round(f["top1_at_alert"].mean(), 3),
        "top3_at_alert": round(f["top3_at_alert"].mean(), 3),
        "top1_at_3d": round(f["top1_at_3d"].mean(), 3),
        "top3_at_3d": round(f["top3_at_3d"].mean(), 3),
        "wrong_but_flagged_ambiguous": f"{int(wrong['flagged_ambiguous'].sum())}/{len(wrong)}",
    }
    return res, summary


if __name__ == "__main__":
    res, summary = run_eval()
    print(res.groupby("fault")[["top1_at_alert", "top1_at_3d"]].mean())
    print(summary)
