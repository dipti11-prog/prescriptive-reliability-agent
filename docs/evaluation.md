# Evaluation results

90 fault cases (9 failure modes x 10 random seeds) and 10 healthy cases. Held-out seeds (1000+) never used while tuning the method.

| Metric | Result |
|---|---|
| Detection rate | 100% |
| False alarm rate (healthy machines) | 0% |
| Median days from fault onset to alert | 4.0 |
| Median days of warning before conventional alarm limit | 14.9 |
| Diagnosis correct (top-1) at first alert | 91% |
| Diagnosis in top-3 at first alert | 99% |
| Diagnosis correct (top-1) at alert + 3 days | 97% |
| Diagnosis in top-3 at alert + 3 days | 100% |
| Wrong diagnoses the agent itself flagged as uncertain | 3/3 |

## By failure mode

| fault               |   detected |   onset_to_alert_d |   lead_vs_alarm_d |   top1_alert |   top1_3d |   top3_3d |
|:--------------------|-----------:|-------------------:|------------------:|-------------:|----------:|----------:|
| asv_passing         |          1 |               6.2  |             12.6  |          1   |       1   |         1 |
| bearing_wear_de     |          1 |               3.3  |             16.4  |          1   |       1   |         1 |
| dgs_degradation     |          1 |               2.55 |             12.85 |          0.9 |       1   |         1 |
| impeller_fouling    |          1 |               5    |             13.3  |          1   |       1   |         1 |
| lube_cooler_fouling |          1 |               3.85 |             16.65 |          1   |       1   |         1 |
| misalignment        |          1 |               4.15 |             17.9  |          0.3 |       0.7 |         1 |
| rotor_imbalance     |          1 |               3.9  |            nan    |          1   |       1   |         1 |
| strainer_blockage   |          1 |               6.35 |             15.8  |          1   |       1   |         1 |
| thrust_bearing_wear |          1 |               3.35 |             14.9  |          1   |       1   |         1 |

*Lead vs alarm is blank where the fault had not reached the conventional alarm limit within the simulated window - i.e. the agent warned and the plant alarm had still not sounded.*

## Honest limitations

- Synthetic data: fault signatures are engineering-informed but simplified. Real plant data has instrument faults, operating-mode changes and overlapping failures.
- Hardest case is early misalignment vs imbalance vs bearing wear: with only vibration visible, the agent correctly reports uncertainty and asks for a vibration spectrum.
- Next step for real deployment: calibrate on historian + CMMS data from one asset, with engineer feedback on each recommendation.