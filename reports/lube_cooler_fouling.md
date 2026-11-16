# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-15 18:20:00 | First alert: 2026-10-12 18:20:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Lube oil cooler fouling / high oil temperature** (match 45%, likelihood 100% among 9 failure modes). Evidence: Lube oil supply temp up (+18 sigma); Journal bearing temp DE up (+4 sigma); Journal bearing temp NDE up (+4 sigma); Thrust bearing temp up (+4 sigma). At the current trend the machine reaches a trip limit in about 15 days. Priority **P3 Planned** (schedule within 30 days). Planned intervention avoids roughly USD 903,000 versus run-to-failure (illustrative). First action: Switch to standby cooler if installed.

## 1. Diagnosis

**Lube oil cooler fouling / high oil temperature** - Lube oil system - cooler  
ISO 14224 failure mode: OHE - Overheating | Mechanism: 5.1 Blockage/plugged | Severity 6/10 | Typical P-F interval 45 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM02 Lube oil cooler fouling / high oil temperature | 45% | 100% | - |
| 2 | FM07 Thrust bearing wear | 5% | 0% | lube_oil_temp, brg_temp_nde, brg_temp_de |
| 3 | FM01 Journal bearing wear (DE) | 5% | 0% | lube_oil_temp, brg_temp_nde, thrust_brg_temp |
| 4 | FM03 Shaft misalignment (coupling) | 2% | 0% | lube_oil_temp, brg_temp_nde, thrust_brg_temp |
| 5 | FM04 Rotor imbalance (deposit build-up or loss of material) | 0% | 0% | lube_oil_temp, brg_temp_nde, brg_temp_de, thrust_brg_temp |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Lube oil supply temp | up | +17.6 | 1.0 | supports |
| Journal bearing temp DE | up | +3.7 | 0.7 | supports |
| Journal bearing temp NDE | up | +3.7 | 0.7 | supports |
| Thrust bearing temp | up | +3.8 | 0.7 | supports |
| Lube oil supply press | down | -0.9 | 0.3 | not seen |

**Likely causes:** Cooler fouling on water or air side; Cooling water flow reduced or temperature control valve stuck; High ambient temperature exceeding cooler design margin

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Lube oil supply temp (degC) | 48.0 | 50.28 | 60.0 | 66.0 | 11.4 | 15.3 |
| Journal bearing temp DE (degC) | 85.0 | 86.71 | 110.0 | 120.0 | 53.4 | 69.7 |
| Journal bearing temp NDE (degC) | 82.0 | 84.09 | 110.0 | 120.0 | 30.9 | 38.1 |
| Thrust bearing temp (degC) | 88.0 | 89.83 | 115.0 | 125.0 | 81.1 | - |

**Priority P3 - Planned: schedule within 30 days.**  
Rule inputs: {'severity': 6, 'days_to_trip': 15.3, 'criticality': 'A', 'confidence': 0.45}

## 3. Recommended actions

**Confirm the diagnosis**
- All bearing temperatures rising together (system-wide, not one bearing)
- Cooler inlet/outlet temperature approach compared with design
- Temperature control valve position and cooling medium flow

**Immediate (protect the machine)**
- Switch to standby cooler if installed
- Check cooling water supply and temperature control valve operation

**Corrective (fix the defect)**
- Clean cooler (tube bundle or fin fan) at next opportunity

**Defect elimination (stop it coming back)**
- Add cooler approach temperature as a monitored KPI
- Review cooling water treatment programme

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400148 | 2023-08-30 | K-101 | LO cooler cleaning - Fin fan lube oil cooler dirty, approach temp high. Cleaned and TCV checked.... | 0.41 |
| WO400199 | 2025-06-19 | K-101 | DE brg high vib + temp - DE journal bearing vibration trending up, bearing temp high. Bearing replaced, babbitt wip... | 0.25 |
| WO400162 | 2024-02-02 | K-101 | K brg DE replaced - Radial bearing DE found worn on inspection, clearance above OEM limit. New pads fitted. Lu... | 0.14 |
| WO400156 | 2023-12-12 | K-201 | High vibration drive end - Vibration alarm DE probes. Shaft centreline shift. Bearing pads scored - replaced. Recomme... | 0.12 |
| WO400109 | 2022-03-14 | K-101 | Seal gas leak NDE - Dry gas seal leakage NDE, faces damaged by liquids in seal gas. Seal replaced, heater repa... | 0.12 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 1,182,000
- Planned intervention: ~USD 279,000
- **Avoided cost: ~USD 903,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 3 - Planned |
| Short Text | K-101 suspected Lube oil cooler fouling  |
| Damage Code | FOUL |
| Cause Code | HEAT |
| Iso14224 Failure Mode | OHE - Overheating |
| Long Text | Condition-monitoring alert 12-Oct-2026 18:20. Suspected Lube oil cooler fouling / high oil temperature (match 45%). Evidence: Lube oil supply temp 50.28 degC (normal 48.0), Journal bearing temp DE 86.71 degC (normal 85.0), Journal bearing temp NDE 84.09 degC (normal 82.0). Predicted trip in 15.3 days. Recommended: Switch to standby cooler if installed; Clean cooler (tube bundle or fin fan) at next opportunity. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 12-Oct 18:20 on lube_oil_temp. |
| 2 Diagnose | `diagnose.diagnose` | FM02 Lube oil cooler fouling / high oil temperature: 100% | FM07 Thrust bearing wear: 0% | FM01 Journal bearing wear (DE): 0% |
| 3 Doubt | `ambiguity check` | Clear leader (100% ahead of next hypothesis). |
| 4 Recall | `history.similar_work_orders + recurrence` | 5 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 15.3 days. |
| 6 Decide | `priority rules` | P3 Planned - schedule within 30 days. |
| 7 Value | `economics` | Acting now avoids ~USD 903,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 8 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*