# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-15 12:50:00 | First alert: 2026-10-12 12:50:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Journal bearing wear (DE)** (match 79%, likelihood 85% among 9 failure modes). Evidence: Radial vibration DE up (+25 sigma); Journal bearing temp DE up (+8 sigma); Radial vibration NDE up (+4 sigma). At the current trend the machine reaches a trip limit in about 16 days. This is a repeat failure on K-101 (2 events in 36 months) - a formal RCA is recommended. Priority **P2 Urgent** (act within 7 days). Planned intervention avoids roughly USD 1,420,000 versus run-to-failure (illustrative). First action: Increase monitoring of DE vibration and bearing temperature to hourly review.

## 1. Diagnosis

**Journal bearing wear (DE)** - Radial journal bearing, drive end  
ISO 14224 failure mode: VIB - Vibration | Mechanism: 2.4 Wear | Severity 8/10 | Typical P-F interval 30 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM01 Journal bearing wear (DE) | 79% | 85% | - |
| 2 | FM03 Shaft misalignment (coupling) | 50% | 13% | - |
| 3 | FM04 Rotor imbalance (deposit build-up or loss of material) | 30% | 2% | brg_temp_de |
| 4 | FM02 Lube oil cooler fouling / high oil temperature | 9% | 0% | vib_de, vib_nde |
| 5 | FM07 Thrust bearing wear | 6% | 0% | brg_temp_de, vib_nde |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| Radial vibration DE | up | +25.0 | 1.0 | supports |
| Journal bearing temp DE | up | +7.7 | 1.0 | supports |
| Radial vibration NDE | up | +4.2 | 0.3 | supports |

**Likely causes:** Lube oil contamination or degraded oil (particles, water, varnish); Insufficient oil film from low supply pressure or high oil temperature; Repeated start/stop or slow-roll operation wiping the babbitt

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| Radial vibration DE (um) | 18.0 | 22.9 | 50.0 | 75.0 | 10.6 | 16.4 |
| Journal bearing temp DE (degC) | 85.0 | 88.34 | 110.0 | 120.0 | 17.0 | 21.8 |
| Radial vibration NDE (um) | 15.0 | 15.94 | 50.0 | 75.0 | 21.9 | 29.9 |

**Priority P2 - Urgent: act within 7 days.**  
Rule inputs: {'severity': 8, 'days_to_trip': 16.4, 'criticality': 'A', 'confidence': 0.79}

## 3. Recommended actions

**Confirm the diagnosis**
- Vibration spectrum on DE probes - rising 1x with sub-synchronous content suggests clearance growth
- Shaft centreline plot - shift of journal position within bearing clearance
- Lube oil sample - particle count (ISO 4406), water ppm, elemental (tin/lead = babbitt)

**Immediate (protect the machine)**
- Increase monitoring of DE vibration and bearing temperature to hourly review
- Take lube oil sample for urgent analysis
- Verify lube oil supply pressure and temperature are within limits

**Corrective (fix the defect)**
- Plan bearing inspection and replacement at next opportunity window
- Check bearing clearances against OEM specification during inspection

**Defect elimination (stop it coming back)**
- Initiate formal RCA: 2 'Journal bearing wear (DE)' events on K-101 in 36 months (USD 95,200, 79 h downtime). Fix the cause, not the part.
- Review lube oil cleanliness programme and filter change interval
- Add bearing-temperature-rate-of-change alert to condition monitoring

## 4. Maintenance history

2 event(s) of this failure mode on K-101 in the last 36 months (2 coded, 0 found only by text search). **Bad actor - RCA recommended.**

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400199 | 2025-06-19 | K-101 | DE brg high vib + temp - DE journal bearing vibration trending up, bearing temp high. Bearing replaced, babbitt wip... | 0.46 |
| WO400162 | 2024-02-02 | K-101 | K brg DE replaced - Radial bearing DE found worn on inspection, clearance above OEM limit. New pads fitted. Lu... | 0.28 |
| WO400156 | 2023-12-12 | K-201 | High vibration drive end - Vibration alarm DE probes. Shaft centreline shift. Bearing pads scored - replaced. Recomme... | 0.26 |
| WO400109 | 2022-03-14 | K-101 | Seal gas leak NDE - Dry gas seal leakage NDE, faces damaged by liquids in seal gas. Seal replaced, heater repa... | 0.19 |
| WO400141 | 2023-05-11 | K-102 | Realign motor-compressor - Alignment correction after baseplate settlement. Soft foot found at NDE motor foot.... | 0.12 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 1,861,000
- Planned intervention: ~USD 441,000
- **Avoided cost: ~USD 1,420,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 2 - Urgent |
| Short Text | K-101 suspected Journal bearing wear (DE |
| Damage Code | WEAR |
| Cause Code | LUBE |
| Iso14224 Failure Mode | VIB - Vibration |
| Long Text | Condition-monitoring alert 12-Oct-2026 12:50. Suspected Journal bearing wear (DE) (match 79%). Evidence: Radial vibration DE 22.9 um (normal 18.0), Journal bearing temp DE 88.34 degC (normal 85.0), Radial vibration NDE 15.94 um (normal 15.0). Predicted trip in 16.4 days. Recommended: Increase monitoring of DE vibration and bearing temperature to hourly review; Plan bearing inspection and replacement at next opportunity window. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 12-Oct 12:50 on vib_de. |
| 2 Diagnose | `diagnose.diagnose` | FM01 Journal bearing wear (DE): 85% | FM03 Shaft misalignment (coupling): 13% | FM04 Rotor imbalance (deposit build-up or loss of material): 2% |
| 3 Doubt | `ambiguity check` | Clear leader (72% ahead of next hypothesis). |
| 4 Recall | `history.similar_work_orders + recurrence` | 5 similar past jobs across fleet; 2 on K-101 in 36 months -> BAD ACTOR. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 16.4 days. |
| 6 Decide | `priority rules` | P2 Urgent - act within 7 days. |
| 7 Value | `economics` | Acting now avoids ~USD 1,420,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 11 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*