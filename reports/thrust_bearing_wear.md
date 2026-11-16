# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-14 20:50:00 | First alert: 2026-10-11 20:50:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Thrust bearing wear** (match 67%, likelihood 100% among 9 failure modes). Evidence: Axial displacement up (+18 sigma); Thrust bearing temp up (+6 sigma). At the current trend the machine reaches a trip limit in about 16 days. Priority **P2 Urgent** (act within 7 days). Planned intervention avoids roughly USD 1,450,000 versus run-to-failure (illustrative). First action: Review recent surge events and anti-surge controller behaviour.

## 1. Diagnosis

**Thrust bearing wear** - Thrust bearing  
ISO 14224 failure mode: OHE - Overheating | Mechanism: 2.4 Wear | Severity 9/10 | Typical P-F interval 21 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM07 Thrust bearing wear | 67% | 100% | - |
| 2 | FM03 Shaft misalignment (coupling) | 17% | 0% | thrust_brg_temp |
| 3 | FM02 Lube oil cooler fouling / high oil temperature | 6% | 0% | axial_disp |
| 4 | FM01 Journal bearing wear (DE) | 0% | 0% | axial_disp, thrust_brg_temp |
| 5 | FM04 Rotor imbalance (deposit build-up or loss of material) | 0% | 0% | axial_disp, thrust_brg_temp |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Axial displacement | up | +18.5 | 1.0 | supports |
| Thrust bearing temp | up | +6.0 | 1.0 | supports |
| Radial vibration DE | up | +3.0 | 0.2 | not seen |

**Likely causes:** Excessive thrust load from balance piston seal wear or process upsets; Liquid slugging or surge events; Lube oil contamination

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Axial displacement (mm) | 0.1 | 0.14 | 0.4 | 0.6 | 10.7 | 15.7 |
| Thrust bearing temp (degC) | 88.0 | 90.57 | 115.0 | 125.0 | 17.3 | 21.8 |

**Priority P2 - Urgent: act within 7 days.**  
Rule inputs: {'severity': 9, 'days_to_trip': 15.7, 'criticality': 'A', 'confidence': 0.67}

## 3. Recommended actions

**Confirm the diagnosis**
- Axial position trend vs thrust pad temperatures (active vs inactive side)
- Balance line differential pressure / flow
- Event log - surge or liquid ingestion events before onset

**Immediate (protect the machine)**
- Review recent surge events and anti-surge controller behaviour
- Increase monitoring; confirm axial position probes are healthy

**Corrective (fix the defect)**
- Plan thrust bearing inspection; check balance piston labyrinth clearance

**Defect elimination (stop it coming back)**
- Anti-surge controller tuning review
- Balance piston seal condition monitoring via balance line DP

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400179 | 2024-09-22 | K-102 | Axial displacement alarm - Axial position trending towards alarm. Thrust bearing wear found, pads replaced.... | 0.31 |
| WO400199 | 2025-06-19 | K-101 | DE brg high vib + temp - DE journal bearing vibration trending up, bearing temp high. Bearing replaced, babbitt wip... | 0.14 |
| WO400162 | 2024-02-02 | K-101 | K brg DE replaced - Radial bearing DE found worn on inspection, clearance above OEM limit. New pads fitted. Lu... | 0.10 |
| WO400156 | 2023-12-12 | K-201 | High vibration drive end - Vibration alarm DE probes. Shaft centreline shift. Bearing pads scored - replaced. Recomme... | 0.10 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 1,939,000
- Planned intervention: ~USD 490,000
- **Avoided cost: ~USD 1,450,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 2 - Urgent |
| Short Text | K-101 suspected Thrust bearing wear |
| Damage Code | WEAR |
| Cause Code | OPER |
| Iso14224 Failure Mode | OHE - Overheating |
| Long Text | Condition-monitoring alert 11-Oct-2026 20:50. Suspected Thrust bearing wear (match 67%). Evidence: Axial displacement 0.14 mm (normal 0.1), Thrust bearing temp 90.57 degC (normal 88.0). Predicted trip in 15.7 days. Recommended: Review recent surge events and anti-surge controller behaviour; Plan thrust bearing inspection; check balance piston labyrinth clearance. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 11-Oct 20:50 on axial_disp. |
| 2 Diagnose | `diagnose.diagnose` | FM07 Thrust bearing wear: 100% | FM03 Shaft misalignment (coupling): 0% | FM02 Lube oil cooler fouling / high oil temperature: 0% |
| 3 Doubt | `ambiguity check` | Clear leader (99% ahead of next hypothesis). |
| 4 Recall | `history.similar_work_orders + recurrence` | 4 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 15.7 days. |
| 6 Decide | `priority rules` | P2 Urgent - act within 7 days. |
| 7 Value | `economics` | Acting now avoids ~USD 1,450,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 8 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*