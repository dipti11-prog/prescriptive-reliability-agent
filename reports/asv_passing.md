# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-17 14:00:00 | First alert: 2026-10-14 14:00:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Anti-surge (recycle) valve passing** (match 20%, likelihood 100% among 9 failure modes). Evidence: Suction temperature up (+10 sigma); Discharge temperature up (+3 sigma). Diagnosis not yet conclusive - Impeller / aerodynamic fouling is close behind. Run the discriminating checks first. At the current trend the machine reaches a trip limit in about 30 days. Priority **P3 Planned** (schedule within 30 days (confirm diagnosis first - low confidence)). Planned intervention avoids roughly USD 253,000 versus run-to-failure (illustrative). First action: [FM08 Anti-surge (recycle) valve passing] Valve position feedback vs demand - should be 0% at normal load.

## 1. Diagnosis

**Anti-surge (recycle) valve passing** - Anti-surge control valve  
ISO 14224 failure mode: ILP/LOO - Internal leakage / low output | Mechanism: 1.1 Leakage | Severity 5/10 | Typical P-F interval 120 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM08 Anti-surge (recycle) valve passing | 20% | 100% | - |
| 2 | FM05 Impeller / aerodynamic fouling | 1% | 0% | suction_temp |
| 3 | FM09 Suction strainer / filter blockage | 1% | 0% | suction_temp |
| 4 | FM01 Journal bearing wear (DE) | 0% | 0% | suction_temp, discharge_temp |
| 5 | FM02 Lube oil cooler fouling / high oil temperature | 0% | 0% | suction_temp, discharge_temp |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Suction temperature | up | +9.9 | 1.0 | supports |
| Motor power | up | +1.7 | 1.0 | not seen |
| Export gas flow | down | +0.8 | 0.8 | not seen |
| Discharge temperature | up | +3.0 | 0.5 | supports |

**Likely causes:** Seat or trim damage on recycle valve; Valve not fully closing (positioner calibration, actuator issue)

> **Diagnosis not conclusive.** Run these checks to separate the look-alikes:

> - [FM08 Anti-surge (recycle) valve passing] Valve position feedback vs demand - should be 0% at normal load
> - [FM08 Anti-surge (recycle) valve passing] Acoustic or temperature check downstream of valve (hot pipe when shut)

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Suction temperature (degC) | 40.0 | 42.51 | 55.0 | 60.0 | 24.7 | 29.8 |
| Discharge temperature (degC) | 135.0 | 138.33 | 150.0 | 160.0 | 32.8 | 47.0 |

**Priority P3 - Planned: schedule within 30 days (confirm diagnosis first - low confidence).**  
Rule inputs: {'severity': 5, 'days_to_trip': 29.8, 'criticality': 'A', 'confidence': 0.2}

## 3. Recommended actions

**Confirm the diagnosis**
- [FM08 Anti-surge (recycle) valve passing] Valve position feedback vs demand - should be 0% at normal load
- [FM08 Anti-surge (recycle) valve passing] Acoustic or temperature check downstream of valve (hot pipe when shut)

**Immediate (protect the machine)**
- Check positioner, stroke the valve if safe to do so
- Quantify recycled energy loss (kW and USD/day)

**Corrective (fix the defect)**
- Overhaul valve trim at next opportunity

**Defect elimination (stop it coming back)**
- Add valve signature / partial stroke diagnostics

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400206 | 2025-10-05 | K-201 | Recycle valve leak-by - Anti-surge valve leak by, power high for throughput. Seat lapped.... | 0.40 |
| WO400148 | 2023-08-30 | K-101 | LO cooler cleaning - Fin fan lube oil cooler dirty, approach temp high. Cleaned and TCV checked.... | 0.10 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 337,000
- Planned intervention: ~USD 83,000
- **Avoided cost: ~USD 253,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 3 - Planned |
| Short Text | K-101 suspected Anti-surge (recycle) val |
| Damage Code | LEAK |
| Cause Code | WEAR |
| Iso14224 Failure Mode | ILP/LOO - Internal leakage / low output |
| Long Text | Condition-monitoring alert 14-Oct-2026 14:00. Suspected Anti-surge (recycle) valve passing (match 20%). Evidence: Suction temperature 42.51 degC (normal 40.0), Discharge temperature 138.33 degC (normal 135.0). Predicted trip in 29.8 days. Recommended: Check positioner, stroke the valve if safe to do so; Overhaul valve trim at next opportunity. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 14-Oct 14:00 on suction_temp. |
| 2 Diagnose | `diagnose.diagnose` | FM08 Anti-surge (recycle) valve passing: 100% | FM05 Impeller / aerodynamic fouling: 0% | FM09 Suction strainer / filter blockage: 0% |
| 3 Doubt | `ambiguity check` | Top hypotheses only 100% apart - recommending discriminating checks before committing. |
| 4 Recall | `history.similar_work_orders + recurrence` | 2 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 29.8 days. |
| 6 Decide | `priority rules` | P3 Planned - schedule within 30 days (confirm diagnosis first - low confidence). |
| 7 Value | `economics` | Acting now avoids ~USD 253,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 6 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*