"""
agent.py - the Prescriptive Reliability Agent.

It works like a reliability engineer handed an alert:

  1. CHECK    - is there a real, persistent anomaly?          (detect.py)
  2. DIAGNOSE - which failure mode fits the symptoms?         (diagnose.py + FMEA)
  3. DOUBT    - is the diagnosis clear, or do we need a test to tell look-alikes apart?
  4. RECALL   - has this happened before on this machine?     (history.py)
  5. FORECAST - how long until alarm / trip at current trend? (detect.time_to_limit)
  6. DECIDE   - priority from severity x confidence x time-to-trip x criticality
  7. VALUE    - what does acting now save vs waiting for failure?
  8. PRESCRIBE- actions: confirm -> immediate -> corrective -> defect elimination (+RCA)
  9. DRAFT    - CMMS notification ready for the planner
 10. HAND OVER- nothing is executed: a human engineer approves.

Every step is logged in `trace`, so the reasoning can be audited - essential for
industrial use, where an unexplained recommendation will (rightly) be ignored.
The core is deterministic; an LLM is optional and only writes the summary text.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import pandas as pd

from . import detect, diagnose as dx, history
from .config import fmea_by_id, load_asset

AMBIGUITY_GAP = 0.15     # if top-2 likelihoods are this close, ask for a discriminating test
MIN_CONFIDENT = 0.35     # match score below this = weak diagnosis


@dataclass
class Prescription:
    status: str                                   # healthy / alert
    asset: dict
    analysis_time: str
    alert_time: str | None = None
    triggered_sensors: list[str] = field(default_factory=list)
    hypotheses: list[dict] = field(default_factory=list)
    diagnosis: dict | None = None
    ambiguous: bool = False
    discriminating_checks: list[str] = field(default_factory=list)
    history: dict = field(default_factory=dict)
    similar_work_orders: list[dict] = field(default_factory=list)
    forecast: list[dict] = field(default_factory=list)
    days_to_trip: float | None = None
    priority: dict = field(default_factory=dict)
    economics: dict = field(default_factory=dict)
    actions: dict = field(default_factory=dict)
    notification: dict = field(default_factory=dict)
    summary: str = ""
    approval: str = "PENDING ENGINEER REVIEW"
    trace: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _log(trace: list, step: str, tool: str, result: str) -> None:
    trace.append({"step": step, "tool": tool, "result": result})


def _priority(severity: int, days_to_trip: float | None, criticality: str, confidence: float) -> dict:
    """SAP PM-style priority. Rules written so an engineer can read and challenge them."""
    d = 999 if days_to_trip is None else days_to_trip
    crit_a = criticality == "A"
    if d <= 3 or (severity >= 9 and d <= 7 and crit_a):
        p, label, window = 1, "Emergency", "act within 24 h"
    elif d <= 14 or (severity >= 8 and crit_a):
        p, label, window = 2, "Urgent", "act within 7 days"
    elif d <= 45:
        p, label, window = 3, "Planned", "schedule within 30 days"
    else:
        p, label, window = 4, "Opportunity", "next planned shutdown"
    if confidence < MIN_CONFIDENT and p > 1:
        window += " (confirm diagnosis first - low confidence)"
    return {"level": p, "label": label, "window": window,
            "rule_inputs": {"severity": severity, "days_to_trip": None if d == 999 else round(d, 1),
                            "criticality": criticality, "confidence": round(confidence, 2)}}


def _economics(fm_id: str, asset: dict, hist_similar: pd.DataFrame) -> dict:
    """Illustrative value of planned intervention vs run-to-failure."""
    base_cost, base_down = history.COST[fm_id]
    # only past jobs that really are this failure mode (coded, or a strong text match)
    hist_similar = hist_similar[(hist_similar["fm_id_coded"] == fm_id) | (hist_similar["similarity"] >= 0.25)]
    if len(hist_similar):
        repair = float(hist_similar["cost_usd"].mean())
        down = float(hist_similar["downtime_h"].mean())
    else:
        repair, down = base_cost, base_down
    per_hour = asset["asset"]["production_impact_per_day_usd"] / 24
    # Unplanned failure: secondary damage (x2 repair), longer outage (x1.8), full production loss.
    unplanned = repair * 2.0 + down * 1.8 * per_hour
    # Planned: repair in a planned window; production loss only if no spare/opportunity (~40 %).
    planned = repair + down * 0.4 * per_hour
    return {"repair_cost_usd": round(repair, -2), "outage_h": round(down, 1),
            "unplanned_cost_usd": round(unplanned, -3), "planned_cost_usd": round(planned, -3),
            "value_of_acting_now_usd": round(unplanned - planned, -3),
            "basis": "Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; "
                     "planned = 1x repair + 40% of outage production loss."}


def run(df: pd.DataFrame, at: str | pd.Timestamp | None = "alert+3d") -> Prescription:
    """Run the agent on a sensor history.

    at: analysis time. 'alert+3d' (default) = 3 days after first alert, as if an engineer
        is reviewing it; None = latest data point; or any timestamp.
    """
    asset = load_asset()
    sensors = asset["sensors"]
    fmea = fmea_by_id()
    trace: list[dict] = []
    tag = asset["asset"]["tag"]

    # 1. CHECK -----------------------------------------------------------------
    z = detect.zscores(df)
    mfrac = detect.margin_fraction(df)
    alert = detect.first_alert(z, mfrac)
    if alert is None:
        t = df.index[-1]
        _log(trace, "1 Check", "detect.first_alert", "No persistent anomaly. Machine healthy.")
        return Prescription("healthy", asset["asset"], str(t), summary=f"{tag}: no abnormal behaviour detected. No action required.",
                            approval="N/A", trace=trace)
    if isinstance(at, str) and at.startswith("alert+"):          # e.g. "alert+3d"
        t = min(alert.timestamp + pd.Timedelta(days=float(at[6:].rstrip("d"))), df.index[-1])
    elif at is None:
        t = df.index[-1]
    else:
        t = df.index[df.index.get_indexer([pd.Timestamp(at)], method="nearest")[0]]
    _log(trace, "1 Check", "detect.first_alert",
         f"Persistent anomaly since {alert.timestamp:%d-%b %H:%M} on {', '.join(alert.triggered_sensors)}.")

    # 2. DIAGNOSE --------------------------------------------------------------
    hyps = dx.diagnose(z.loc[t].to_dict(), mfrac.loc[t].to_dict())
    top = hyps[0]
    fm = fmea[top.fm_id]
    _log(trace, "2 Diagnose", "diagnose.diagnose",
         " | ".join(f"{h.fm_id} {h.name}: {h.likelihood:.0%}" for h in hyps[:3]))

    # 3. DOUBT -----------------------------------------------------------------
    gap = top.likelihood - hyps[1].likelihood
    ambiguous = gap < AMBIGUITY_GAP or top.match_score < MIN_CONFIDENT
    checks: list[str] = []
    if ambiguous:
        for h in hyps[:3]:
            if h.likelihood > 0.08:
                checks += [f"[{h.fm_id} {h.name}] {c}" for c in fmea[h.fm_id]["confirm_checks"][:2]]
        _log(trace, "3 Doubt", "ambiguity check",
             f"Top hypotheses only {gap:.0%} apart - recommending discriminating checks before committing.")
    else:
        _log(trace, "3 Doubt", "ambiguity check", f"Clear leader ({gap:.0%} ahead of next hypothesis).")

    # 4. RECALL ----------------------------------------------------------------
    sim = history.similar_work_orders(top.fm_id, k=5)
    rec = history.recurrence(top.fm_id, tag, as_of=t)
    _log(trace, "4 Recall", "history.similar_work_orders + recurrence",
         f"{len(sim)} similar past jobs across fleet; {rec['count']} on {tag} in 36 months"
         + (" -> BAD ACTOR" if rec["bad_actor"] else "") + ".")

    # 5. FORECAST --------------------------------------------------------------
    forecast = []
    for e in top.evidence:
        s = sensors[e.sensor]
        if e.verdict != "supports" or s.get("trip") is None:
            continue
        now_val = float(df[e.sensor].rolling(detect.SMOOTH_WINDOW, min_periods=1).mean().loc[t])
        tta = detect.time_to_limit(df, e.sensor, t, s["alarm"], s["direction"]) if s.get("alarm") is not None else None
        ttt = detect.time_to_limit(df, e.sensor, t, s["trip"], s["direction"])
        forecast.append({"sensor": e.sensor, "label": s["label"], "unit": s["unit"],
                         "normal": s["normal"], "now": round(now_val, 2), "alarm": s["alarm"], "trip": s["trip"],
                         "days_to_alarm": None if tta is None else round(tta, 1),
                         "days_to_trip": None if ttt is None else round(ttt, 1)})
    trips = [f["days_to_trip"] for f in forecast if f["days_to_trip"] is not None]
    days_to_trip = min(trips) if trips else None
    _log(trace, "5 Forecast", "detect.time_to_limit",
         f"Earliest predicted trip in {days_to_trip:.1f} days." if days_to_trip is not None
         else "No trip predicted within 90 days at current trend.")

    # 6. DECIDE ----------------------------------------------------------------
    prio = _priority(fm["severity"], days_to_trip, asset["asset"]["criticality"], top.match_score)
    _log(trace, "6 Decide", "priority rules", f"P{prio['level']} {prio['label']} - {prio['window']}.")

    # 7. VALUE -----------------------------------------------------------------
    econ = _economics(top.fm_id, asset, sim)
    _log(trace, "7 Value", "economics", f"Acting now avoids ~USD {econ['value_of_acting_now_usd']:,.0f} (illustrative).")

    # 8. PRESCRIBE -------------------------------------------------------------
    actions = {
        "confirm": checks if ambiguous else fm["confirm_checks"][:3],
        "immediate": fm["immediate_actions"],
        "corrective": fm["corrective_actions"],
        "defect_elimination": list(fm["defect_elimination"]),
    }
    if rec["bad_actor"]:
        actions["defect_elimination"].insert(
            0, f"Initiate formal RCA: {rec['count']} '{fm['name']}' events on {tag} in 36 months "
               f"(USD {rec['total_cost_usd']:,.0f}, {rec['total_downtime_h']:.0f} h downtime). Fix the cause, not the part.")
    _log(trace, "8 Prescribe", "FMEA actions", f"{sum(len(v) for v in actions.values())} actions across 4 horizons.")

    # 9. DRAFT -----------------------------------------------------------------
    worst = ", ".join(f"{f['label']} {f['now']} {f['unit']} (normal {f['normal']})" for f in forecast[:3])
    notif = {
        "notification_type": "M2 - Malfunction report",
        "functional_location": asset["asset"]["functional_location"],
        "equipment": tag,
        "priority": f"{prio['level']} - {prio['label']}",
        "short_text": f"{tag} suspected {fm['name']}"[:40],
        "damage_code": fm["sap_damage_code"],
        "cause_code": fm["sap_cause_code"],
        "iso14224_failure_mode": fm["iso14224_failure_mode"],
        "long_text": (f"Condition-monitoring alert {alert.timestamp:%d-%b-%Y %H:%M}. Suspected {fm['name']} "
                      f"(match {top.match_score:.0%}). Evidence: {worst}. "
                      f"Predicted trip in {days_to_trip if days_to_trip is not None else '>90'} days. "
                      f"Recommended: {actions['immediate'][0]}; {actions['corrective'][0]}."),
        "status": "DRAFT - requires engineer approval",
    }
    _log(trace, "9 Draft", "CMMS notification", "Draft M2 notification prepared (not submitted).")

    p = Prescription(
        status="alert", asset=asset["asset"], analysis_time=str(t), alert_time=str(alert.timestamp),
        triggered_sensors=alert.triggered_sensors,
        hypotheses=[{"fm_id": h.fm_id, "name": h.name, "match_score": h.match_score,
                     "likelihood": h.likelihood, "support": h.support, "explained": h.explained,
                     "unexplained": h.unexplained} for h in hyps],
        diagnosis={"fm_id": top.fm_id, "name": fm["name"], "component": fm["component"],
                   "match_score": top.match_score, "likelihood": top.likelihood,
                   "severity": fm["severity"], "pf_interval_days": fm["pf_interval_days"],
                   "iso14224_failure_mode": fm["iso14224_failure_mode"], "mechanism": fm["mechanism"],
                   "likely_causes": fm["causes"],
                   "evidence": [asdict(e) for e in top.evidence], "unexplained": top.unexplained},
        ambiguous=ambiguous, discriminating_checks=checks, history=rec,
        similar_work_orders=sim[["wo_id", "date", "equipment", "short_text", "long_text",
                                 "cost_usd", "downtime_h", "similarity"]].to_dict("records"),
        forecast=forecast, days_to_trip=days_to_trip, priority=prio, economics=econ,
        actions=actions, notification=notif, trace=trace,
    )

    # 10. HAND OVER ------------------------------------------------------------
    from .narrative import summarise
    p.summary = summarise(p)
    _log(trace, "10 Hand over", "narrative", "Summary written. Awaiting engineer approval - nothing executed.")
    return p
