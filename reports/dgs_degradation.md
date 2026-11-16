# K-101 Export Gas Compressor - Prescriptive Reliability Assessment

*Analysis time: 2026-10-14 09:50:00 | First alert: 2026-10-11 09:50:00 | Criticality A | Status: **PENDING ENGINEER REVIEW***

## Summary

K-101 Export Gas Compressor: suspected **Dry gas seal degradation** (match 79%, likelihood 100% among 9 failure modes). Evidence: DGS primary vent flow up (+25 sigma); Seal gas diff. pressure down (-8 sigma). At the current trend the machine reaches a trip limit in about 16 days. Priority **P2 Urgent** (act within 7 days). Planned intervention avoids roughly USD 1,730,000 versus run-to-failure (illustrative). First action: Check seal gas supply, filter DP and seal gas heater.

## 1. Diagnosis

**Dry gas seal degradation** - Dry gas seal (primary stage)  
ISO 14224 failure mode: ELP - External leakage, process medium | Mechanism: 1.1 Leakage | Severity 9/10 | Typical P-F interval 21 days

| Rank | Failure mode | Match | Likelihood | Unexplained symptoms |
|---|---|---|---|---|
| 1 | FM06 Dry gas seal degradation | 79% | 100% | vib_de, brg_temp_de |
| 2 | FM02 Lube oil cooler fouling / high oil temperature | 0% | 0% | primary_vent_flow, seal_gas_dp, vib_de |
| 3 | FM01 Journal bearing wear (DE) | 0% | 0% | primary_vent_flow, seal_gas_dp |
| 4 | FM03 Shaft misalignment (coupling) | 0% | 0% | primary_vent_flow, seal_gas_dp |
| 5 | FM04 Rotor imbalance (deposit build-up or loss of material) | 0% | 0% | primary_vent_flow, seal_gas_dp, brg_temp_de |

**Evidence for the leading hypothesis**

| Symptom | Expected | Observed (sigma) | Weight | Verdict |
|---|---|---|---|---|
| DGS primary vent flow | up | +25.0 | 1.0 | supports |
| Seal gas diff. pressure | down | -8.4 | 1.0 | supports |

**Likely causes:** Contaminated or wet seal gas (liquids, particles) damaging seal faces; Seal gas filter differential pressure high / filter bypass; Reverse pressurisation or slow-roll operation

## 2. Time to act

| Sensor | Normal | Now | Alarm | Trip | Days to alarm | Days to trip |
|---|---|---|---|---|---|---|
| DGS primary vent flow (Nm3/h) | 2.0 | 2.63 | 6.0 | 10.0 | 9.5 | 16.1 |
| Seal gas diff. pressure (bar) | 3.0 | 2.9 | 2.0 | 1.5 | 11.8 | 15.5 |

**Priority P2 - Urgent: act within 7 days.**  
Rule inputs: {'severity': 9, 'days_to_trip': 15.5, 'criticality': 'A', 'confidence': 0.79}

## 3. Recommended actions

**Confirm the diagnosis**
- Primary vent flow trend and step changes
- Seal gas filter differential pressure and conditioning skid heater status
- Secondary vent flow - rising too suggests progression to outer seal

**Immediate (protect the machine)**
- Check seal gas supply, filter DP and seal gas heater
- Increase frequency of vent flow review; prepare for controlled shutdown if trip limit approached

**Corrective (fix the defect)**
- Plan seal cartridge replacement - long lead item, check spares availability now

**Defect elimination (stop it coming back)**
- Seal gas conditioning review (dew point margin, filtration)
- Add seal gas quality monitoring

## 4. Maintenance history

0 event(s) of this failure mode on K-101 in the last 36 months (0 coded, 0 found only by text search). 

| WO | Date | Equipment | Text | Similarity |
|---|---|---|---|---|
| WO400219 | 2026-03-03 | K-102 | DGS primary vent high - Primary vent flow increasing, seal gas DP dropping. DGS cartridge replaced. Seal gas filte... | 0.49 |
| WO400109 | 2022-03-14 | K-101 | Seal gas leak NDE - Dry gas seal leakage NDE, faces damaged by liquids in seal gas. Seal replaced, heater repa... | 0.19 |
| WO400166 | 2024-04-17 | K-201 | Suction strainer DP high - Suction pressure low, strainer blocked with scale. Element cleaned.... | 0.12 |

## 5. Value of acting now (illustrative)

- Run-to-failure: ~USD 2,292,000
- Planned intervention: ~USD 562,000
- **Avoided cost: ~USD 1,730,000**
- Basis: Illustrative: unplanned = 2x repair + 1.8x outage at full production loss; planned = 1x repair + 40% of outage production loss.

## 6. Draft CMMS notification

| Field | Value |
|---|---|
| Notification Type | M2 - Malfunction report |
| Functional Location | GP-01-COMP-K101 |
| Equipment | K-101 |
| Priority | 2 - Urgent |
| Short Text | K-101 suspected Dry gas seal degradation |
| Damage Code | LEAK |
| Cause Code | CONT |
| Iso14224 Failure Mode | ELP - External leakage, process medium |
| Long Text | Condition-monitoring alert 11-Oct-2026 09:50. Suspected Dry gas seal degradation (match 79%). Evidence: DGS primary vent flow 2.63 Nm3/h (normal 2.0), Seal gas diff. pressure 2.9 bar (normal 3.0). Predicted trip in 15.5 days. Recommended: Check seal gas supply, filter DP and seal gas heater; Plan seal cartridge replacement - long lead item, check spares availability now. |
| Status | DRAFT - requires engineer approval |

## 7. Agent reasoning trace

| Step | Tool | Result |
|---|---|---|
| 1 Check | `detect.first_alert` | Persistent anomaly since 11-Oct 09:50 on primary_vent_flow. |
| 2 Diagnose | `diagnose.diagnose` | FM06 Dry gas seal degradation: 100% | FM02 Lube oil cooler fouling / high oil temperature: 0% | FM01 Journal bearing wear (DE): 0% |
| 3 Doubt | `ambiguity check` | Clear leader (100% ahead of next hypothesis). |
| 4 Recall | `history.similar_work_orders + recurrence` | 3 similar past jobs across fleet; 0 on K-101 in 36 months. |
| 5 Forecast | `detect.time_to_limit` | Earliest predicted trip in 15.5 days. |
| 6 Decide | `priority rules` | P2 Urgent - act within 7 days. |
| 7 Value | `economics` | Acting now avoids ~USD 1,730,000 (illustrative). |
| 8 Prescribe | `FMEA actions` | 8 actions across 4 horizons. |
| 9 Draft | `CMMS notification` | Draft M2 notification prepared (not submitted). |
| 10 Hand over | `narrative` | Summary written. Awaiting engineer approval - nothing executed. |

---
*Generated by the Prescriptive Reliability Agent on synthetic data. Recommendations require approval by a competent engineer.*