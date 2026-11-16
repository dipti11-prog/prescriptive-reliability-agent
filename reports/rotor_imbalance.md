# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-15 20:50:00 | First alert: 2026-10-12 20:50:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Rotor imbalance (deposit build-up or loss of material)** (match 61%, likelihood 74% among 9 failure modes). Evidence: Radial vibration DE up (+19 sigma); Radial vibration NDE up (+16 sigma). At the current trend the machine reaches a trip limit in about 19 days. Priority **P3 Planned** (schedule within 30 days). Planned intervention avoids roughly USD 2,223,000 versus run-to-failure (illustrative). First action: Review upstream scrubber/separator level and drain operation.

## 1. Diagnosis

**Rotor imbalance (deposit build-up or loss of material)** - Rotor / impellers  
ISO 14224 failure mode: VIB - Vibration | Mechanism: 1.2 Vibration | Severity 7/10 | Typical P-F interval 45 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM04 Rotor imbalance (deposit build-up or loss of material) | 61% | 74% | - |
| 2 | FM01 Journal bearing wear (DE) | 40% | 14% | - |
| 3 | FM03 Shaft misalignment (coupling) | 39% | 12% | - |
| 4 | FM07 Thrust bearing wear | 4% | 0% | vib_nde |
| 5 | FM02 Lube oil cooler fouling / high oil temperature | 0% | 0% | vib_de, vib_nde |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Radial vibration DE | up | +18.8 | 1.0 | supports |
| Radial vibration NDE | up | +16.2 | 1.0 | supports |
| Polytropic efficiency | down | -2.4 | 0.3 | not seen |

**Likely causes:** Uneven deposit build-up on impellers (salts, polymers, liquids carry-over); Deposit shedding from one part of rotor; Erosion or loss of a rotor component

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Radial vibration DE (um) | 18.0 | 21.55 | 50.0 | 75.0 | 13.4 | 20.0 |
| Radial vibration NDE (um) | 15.0 | 18.78 | 50.0 | 75.0 | 13.0 | 19.0 |

**Priority P3 - Planned: schedule within 30 days.**  
Rule inputs: {'severity': 7, 'days_to_trip': 19.0, 'criticality': 'A', 'confidence': 0.61}

## 3. Recommended actions

**Confirm the diagnosis**
- Vibration spectrum - dominant 1x at both bearings, similar magnitude
- 1x phase stable; amplitude changes with speed squared
- Check upstream separator performance for liquid carry-over

**Immediate (protect the machine)**
- Review upstream scrubber/separator level and drain operation
- Trend 1x amplitude and phase at both ends

**Corrective (fix the defect)**
- Consider online wash if deposit-related and OEM-approved
- Plan rotor inspection / high-speed balance at next shutdown

**Defect elimination (stop it coming back)**
- Gas composition and liquid carry-over study
- Review scrubber design margin and level control

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400186 | 2025-01-09 | K-102 | Rotor 1x vib high - 1x vibration high both ends after scrubber upset. Rotor removed, deposits found on impelle... | 0.32 |
| WO400109 | 2022-03-14 | K-101 | Seal gas leak NDE - Dry gas seal leakage NDE, faces damaged by liquids in seal gas. Seal replaced, heater repa... | 0.13 |
| WO400156 | 2023-12-12 | K-201 | High vibration drive end - Vibration alarm DE probes. Shaft centreline shift. Bearing pads scored - replaced. Recomme... | 0.12 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 2,914,000
- Planned intervention: ~USD 691,000
- **Avoided cost: ~USD 2,223,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 3 - Planned |
| Short Text | K-101 suspected Rotor imbalance (deposit |
| Damage Code | IMBL |
| Cause Code | PROC |
| Iso14224 Failure Mode | VIB - Vibration |
| Long Text | Condition-monitoring alert 12-Oct-2026 20:50. Suspected Rotor imbalance (deposit build-up or loss of material) (match 61%). Evidence: Radial vibration DE 21.55 um (normal 18.0), Radial vibration NDE 18.78 um (normal 15.0). Predicted trip in 19.0 days. Recommended: Review upstream scrubber/separator level and drain operation; Consider online wash if deposit-related and OEM-approved. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 12-Oct 20:50 on vib_de. |
| 2 Diagnose | `diagnose.diagnose` | FM04 Rotor imbalance (deposit build-up or loss of material): 74% | FM01 Journal bearing wear (DE): 14% | FM03 Shaft misalignment (coupling): 12% |
| 3 Doubt | `ambiguity check` | Clear leader (60% ahead of next hypothesis). |
| 4 Recall | `history.similar_work_orders + recurrence` | 3 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 19.0 days. |
| 6 Decide | `priority rules` | P3 Planned - schedule within 30 days. |
| 7 Value | `economics` | Acting now avoids ~USD 2,223,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 9 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*