# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-17 03:10:00 | First alert: 2026-10-14 03:10:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Impeller / aerodynamic fouling** (match 37%, likelihood 99% among 9 failure modes). Evidence: Polytropic efficiency down (-11 sigma); Discharge temperature up (+3 sigma). At the current trend the machine reaches a trip limit in about 86 days. Priority **P4 Opportunity** (next planned shutdown). Planned intervention avoids roughly USD 1,057,000 versus run-to-failure (illustrative). First action: Validate performance calculation and transmitter calibration.

## 1. Diagnosis

**Impeller / aerodynamic fouling** - Impellers and diffusers  
ISO 14224 failure mode: PDE - Parameter deviation | Mechanism: 5.2 Contamination | Severity 5/10 | Typical P-F interval 90 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM05 Impeller / aerodynamic fouling | 37% | 99% | - |
| 2 | FM04 Rotor imbalance (deposit build-up or loss of material) | 11% | 1% | discharge_temp |
| 3 | FM09 Suction strainer / filter blockage | 1% | 0% | polytropic_eff |
| 4 | FM08 Anti-surge (recycle) valve passing | 1% | 0% | polytropic_eff |
| 5 | FM01 Journal bearing wear (DE) | 0% | 0% | polytropic_eff, discharge_temp |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Polytropic efficiency | down | -11.4 | 1.0 | supports |
| Discharge temperature | up | +3.2 | 0.8 | supports |
| Motor power | up | +1.4 | 0.7 | not seen |
| Export gas flow | down | +0.5 | 0.6 | not seen |

**Likely causes:** Deposits from gas contaminants (salts, hydrocarbons, corrosion products); Poor upstream filtration / separation

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Discharge temperature (degC) | 135.0 | 136.75 | 150.0 | 160.0 | 48.3 | 86.4 |

**Priority P4 - Opportunity: next planned shutdown.**  
Rule inputs: {'severity': 5, 'days_to_trip': 86.4, 'criticality': 'A', 'confidence': 0.37}

## 3. Recommended actions

**Confirm the diagnosis**
- Polytropic efficiency and head trend corrected for operating point (performance curve)
- Rule out instrument drift on temperature transmitters
- Gas analysis for contaminants

**Immediate (protect the machine)**
- Validate performance calculation and transmitter calibration
- Quantify energy and throughput loss per day

**Corrective (fix the defect)**
- Online wash if OEM-approved, otherwise plan offline cleaning

**Defect elimination (stop it coming back)**
- Improve upstream filtration/separation
- Set efficiency-loss threshold that triggers wash economically

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400127 | 2022-11-03 | K-201 | Performance degradation - Head and efficiency loss trend. Fouling confirmed at inspection. Improve inlet separator.... | 0.16 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 1,379,000
- Planned intervention: ~USD 322,000
- **Avoided cost: ~USD 1,057,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 4 - Opportunity |
| Short Text | K-101 suspected Impeller / aerodynamic f |
| Damage Code | FOUL |
| Cause Code | PROC |
| Iso14224 Failure Mode | PDE - Parameter deviation |
| Long Text | Condition-monitoring alert 14-Oct-2026 03:10. Suspected Impeller / aerodynamic fouling (match 37%). Evidence: Discharge temperature 136.75 degC (normal 135.0). Predicted trip in 86.4 days. Recommended: Validate performance calculation and transmitter calibration; Online wash if OEM-approved, otherwise plan offline cleaning. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 14-Oct 03:10 on polytropic_eff. |
| 2 Diagnose | `diagnose.diagnose` | FM05 Impeller / aerodynamic fouling: 99% | FM04 Rotor imbalance (deposit build-up or loss of material): 1% | FM09 Suction strainer / filter blockage: 0% |
| 3 Doubt | `ambiguity check` | Clear leader (98% ahead of next hypothesis). |
| 4 Recall | `history.similar_work_orders + recurrence` | 1 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 86.4 days. |
| 6 Decide | `priority rules` | P4 Opportunity - next planned shutdown. |
| 7 Value | `economics` | Acting now avoids ~USD 1,057,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 8 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*