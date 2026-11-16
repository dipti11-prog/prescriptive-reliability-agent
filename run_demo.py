"""
run_demo.py - run the agent from the command line.

  python run_demo.py                         # all scenarios -> reports/
  python run_demo.py --fault bearing_wear_de # one scenario
  python run_demo.py --evaluate              # accuracy evaluation -> docs/evaluation.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pra import agent                      # noqa: E402
from pra.report import to_markdown         # noqa: E402
from pra.simulate import FAULTS, simulate  # noqa: E402

ROOT = Path(__file__).parent


def run_one(fault: str | None, seed: int = 1) -> None:
    name = fault or "healthy"
    df = simulate(fault, seed=seed)
    (ROOT / "data").mkdir(exist_ok=True)
    df.to_csv(ROOT / "data" / f"sensors_{name}.csv")
    p = agent.run(df)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / f"{name}.md").write_text(to_markdown(p), encoding="utf-8")
    (ROOT / "reports" / f"{name}.json").write_text(json.dumps(p.to_dict(), indent=2, default=str), encoding="utf-8")
    dx = p.diagnosis["name"] if p.diagnosis else "-"
    print(f"{name:22s} -> {p.status:7s} | diagnosis: {dx:45s} | "
          f"priority: {p.priority.get('label', '-')}")


def evaluate(seeds: int) -> None:
    from pra.evaluate import run_eval
    res, s = run_eval(seeds)
    f = res[res["fault"] != "healthy"]
    by = f.groupby("fault").agg(detected=("detected", "mean"), onset_to_alert_d=("days_onset_to_alert", "median"),
                                lead_vs_alarm_d=("lead_vs_alarm_days", "median"), top1_alert=("top1_at_alert", "mean"),
                                top1_3d=("top1_at_3d", "mean"), top3_3d=("top3_at_3d", "mean"))
    md = ["# Evaluation results", "",
          f"{s['fault_cases']} fault cases (9 failure modes x {seeds} random seeds) and "
          f"{s['healthy_cases']} healthy cases. Held-out seeds (1000+) never used while tuning the method.", "",
          "| Metric | Result |", "|---|---|",
          f"| Detection rate | {s['detection_rate']:.0%} |",
          f"| False alarm rate (healthy machines) | {s['false_alarm_rate']:.0%} |",
          f"| Median days from fault onset to alert | {s['median_days_onset_to_alert']} |",
          f"| Median days of warning before conventional alarm limit | {s['median_lead_vs_alarm_days']} |",
          f"| Diagnosis correct (top-1) at first alert | {s['top1_at_alert']:.0%} |",
          f"| Diagnosis in top-3 at first alert | {s['top3_at_alert']:.0%} |",
          f"| Diagnosis correct (top-1) at alert + 3 days | {s['top1_at_3d']:.0%} |",
          f"| Diagnosis in top-3 at alert + 3 days | {s['top3_at_3d']:.0%} |",
          f"| Wrong diagnoses the agent itself flagged as uncertain | {s['wrong_but_flagged_ambiguous']} |",
          "", "## By failure mode", "", by.round(2).to_markdown(), "",
          "*Lead vs alarm is blank where the fault had not reached the conventional alarm limit within the "
          "simulated window - i.e. the agent warned and the plant alarm had still not sounded.*", "",
          "## Honest limitations", "",
          "- Synthetic data: fault signatures are engineering-informed but simplified. Real plant data has "
          "instrument faults, operating-mode changes and overlapping failures.",
          "- Hardest case is early misalignment vs imbalance vs bearing wear: with only vibration visible, "
          "the agent correctly reports uncertainty and asks for a vibration spectrum.",
          "- Next step for real deployment: calibrate on historian + CMMS data from one asset, with "
          "engineer feedback on each recommendation."]
    out = ROOT / "docs" / "evaluation.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")
    res.to_csv(ROOT / "docs" / "evaluation_cases.csv", index=False)
    print("\n".join(md[:16]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fault", choices=list(FAULTS) + ["healthy"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--evaluate", action="store_true")
    ap.add_argument("--seeds", type=int, default=10)
    a = ap.parse_args()
    if a.evaluate:
        evaluate(a.seeds)
    elif a.fault:
        run_one(None if a.fault == "healthy" else a.fault, a.seed)
    else:
        for f in [None] + list(FAULTS):
            run_one(f, a.seed)
