# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-15 16:50:00 | First alert: 2026-10-12 16:50:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Shaft misalignment (coupling)** (match 42%, likelihood 49% among 9 failure modes). Evidence: Radial vibration DE up (+21 sigma); Radial vibration NDE up (+9 sigma); Axial displacement up (+8 sigma). Diagnosis not yet conclusive - Rotor imbalance (deposit build-up or loss of material) is close behind. Run the discriminating checks first. At the current trend the machine reaches a trip limit in about 18 days. Priority **P3 Planned** (schedule within 30 days). Planned intervention avoids roughly USD 791,000 versus run-to-failure (illustrative). First action: [FM03 Shaft misalignment (coupling)] Vibration spectrum - strong 2x component and high axial vibration.

## 1. Diagnosis

**Shaft misalignment (coupling)** - Coupling / driver-compressor alignment  
ISO 14224 failure mode: VIB - Vibration | Mechanism: 1.3 Clearance/alignment failure | Severity 7/10 | Typical P-F interval 60 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM03 Shaft misalignment (coupling) | 42% | 49% | - |
| 2 | FM04 Rotor imbalance (deposit build-up or loss of material) | 39% | 35% | axial_disp |
| 3 | FM01 Journal bearing wear (DE) | 32% | 15% | axial_disp |
| 4 | FM07 Thrust bearing wear | 18% | 2% | vib_nde |
| 5 | FM02 Lube oil cooler fouling / high oil temperature | 0% | 0% | vib_de, axial_disp, vib_nde |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Radial vibration DE | up | +20.7 | 1.0 | supports |
| Radial vibration NDE | up | +8.7 | 0.6 | supports |
| Axial displacement | up | +8.3 | 0.8 | supports |
| Journal bearing temp DE | up | +2.2 | 0.5 | not seen |

**Likely causes:** Thermal growth not allowed for in cold alignment; Foundation or baseplate settlement, soft foot; Pipe strain from suction/discharge piping

> **Diagnosis not conclusive.** Run these checks to separate the look-alikes:

> - [FM03 Shaft misalignment (coupling)] Vibration spectrum - strong 2x component and high axial vibration
> - [FM03 Shaft misalignment (coupling)] Phase across coupling ~180 degrees
> - [FM04 Rotor imbalance (deposit build-up or loss of material)] Vibration spectrum - dominant 1x at both bearings, similar magnitude
> - [FM04 Rotor imbalance (deposit build-up or loss of material)] 1x phase stable; amplitude changes with speed squared
> - [FM01 Journal bearing wear (DE)] Vibration spectrum on DE probes - rising 1x with sub-synchronous content suggests clearance growth
> - [FM01 Journal bearing wear (DE)] Shaft centreline plot - shift of journal position within bearing clearance

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Radial vibration DE (um) | 18.0 | 21.91 | 50.0 | 75.0 | 12.0 | 18.1 |
| Radial vibration NDE (um) | 15.0 | 17.06 | 50.0 | 75.0 | 17.0 | 23.9 |
| Axial displacement (mm) | 0.1 | 0.12 | 0.4 | 0.6 | 37.8 | 54.0 |

**Priority P3 - Planned: schedule within 30 days.**  
Rule inputs: {'severity': 7, 'days_to_trip': 18.1, 'criticality': 'A', 'confidence': 0.42}

## 3. Recommended actions

**Confirm the diagnosis**
- [FM03 Shaft misalignment (coupling)] Vibration spectrum - strong 2x component and high axial vibration
- [FM03 Shaft misalignment (coupling)] Phase across coupling ~180 degrees
- [FM04 Rotor imbalance (deposit build-up or loss of material)] Vibration spectrum - dominant 1x at both bearings, similar magnitude
- [FM04 Rotor imbalance (deposit build-up or loss of material)] 1x phase stable; amplitude changes with speed squared
- [FM01 Journal bearing wear (DE)] Vibration spectrum on DE probes - rising 1x with sub-synchronous content suggests clearance growth
- [FM01 Journal bearing wear (DE)] Shaft centreline plot - shift of journal position within bearing clearance

**Immediate (protect the machine)**
- Trend 2x vibration component and axial position
- Inspect coupling guard area for heat or abnormal noise

**Corrective (fix the defect)**
- Hot alignment check and correction at next shutdown
- Inspect coupling elements for wear or damage

**Defect elimination (stop it coming back)**
- Verify thermal growth offsets in alignment procedure
- Pipe strain check during next turnaround

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400141 | 2023-05-11 | K-102 | Realign motor-compressor - Alignment correction after baseplate settlement. Soft foot found at NDE motor foot.... | 0.36 |
| WO400199 | 2025-06-19 | K-101 | DE brg high vib + temp - DE journal bearing vibration trending up, bearing temp high. Bearing replaced, babbitt wip... | 0.16 |
| WO400156 | 2023-12-12 | K-201 | High vibration drive end - Vibration alarm DE probes. Shaft centreline shift. Bearing pads scored - replaced. Recomme... | 0.16 |
| WO400109 | 2022-03-14 | K-101 | Seal gas leak NDE - Dry gas seal leakage NDE, faces damaged by liquids in seal gas. Seal replaced, heater repa... | 0.14 |
| WO400162 | 2024-02-02 | K-101 | K brg DE replaced - Radial bearing DE found worn on inspection, clearance above OEM limit. New pads fitted. Lu... | 0.12 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 1,031,000
- Planned intervention: ~USD 241,000
- **Avoided cost: ~USD 791,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 3 - Planned |
| Short Text | K-101 suspected Shaft misalignment (coup |
| Damage Code | MISA |
| Cause Code | INST |
| Iso14224 Failure Mode | VIB - Vibration |
| Long Text | Condition-monitoring alert 12-Oct-2026 16:50. Suspected Shaft misalignment (coupling) (match 42%). Evidence: Radial vibration DE 21.91 um (normal 18.0), Radial vibration NDE 17.06 um (normal 15.0), Axial displacement 0.12 mm (normal 0.1). Predicted trip in 18.1 days. Recommended: Trend 2x vibration component and axial position; Hot alignment check and correction at next shutdown. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 12-Oct 16:50 on vib_de. |
| 2 Diagnose | `diagnose.diagnose` | FM03 Shaft misalignment (coupling): 49% | FM04 Rotor imbalance (deposit build-up or loss of material): 35% | FM01 Journal bearing wear (DE): 15% |
| 3 Doubt | `ambiguity check` | Top hypotheses only 14% apart - recommending discriminating checks before committing. |
| 4 Recall | `history.similar_work_orders + recurrence` | 5 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 18.1 days. |
| 6 Decide | `priority rules` | P3 Planned - schedule within 30 days. |
| 7 Value | `economics` | Acting now avoids ~USD 791,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 12 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*