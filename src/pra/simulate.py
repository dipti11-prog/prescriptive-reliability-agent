"""
simulate.py - synthetic centrifugal compressor data with injected faults.

Why synthetic?  Real compressor failure data is confidential. Synthetic data with
KNOWN injected faults also gives us ground truth, so we can measure whether the
agent diagnoses correctly.

IMPORTANT DESIGN CHOICE: the fault "physics" below is written independently of the
FMEA library. The simulator includes secondary effects and noise that the FMEA does
not list, so the diagnosis is a fair test, not the agent reading its own answer key.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import load_asset

# ---------------------------------------------------------------------------
# Fault physics: change in each sensor when the fault is fully developed (p = 1).
# 'expected_fm' is the FMEA id that a correct diagnosis should return.
# ---------------------------------------------------------------------------
FAULTS: dict[str, dict] = {
    "bearing_wear_de": {
        "expected_fm": "FM01",
        "description": "Drive-end journal bearing wear",
        "effects": {"vib_de": 40, "vib_nde": 5, "brg_temp_de": 22, "lube_oil_temp": 0.8},
    },
    "lube_cooler_fouling": {
        "expected_fm": "FM02",
        "description": "Lube oil cooler fouling",
        "effects": {"lube_oil_temp": 13, "brg_temp_de": 12, "brg_temp_nde": 12,
                    "thrust_brg_temp": 13, "lube_oil_press": -0.12},
    },
    "misalignment": {
        "expected_fm": "FM03",
        "description": "Driver-compressor misalignment",
        "effects": {"vib_de": 30, "vib_nde": 16, "axial_disp": 0.14, "brg_temp_de": 7,
                    "brg_temp_nde": 3},
    },
    "rotor_imbalance": {
        "expected_fm": "FM04",
        "description": "Rotor imbalance from deposit shedding",
        "effects": {"vib_de": 27, "vib_nde": 29, "polytropic_eff": -0.9, "brg_temp_de": 1.5},
    },
    "impeller_fouling": {
        "expected_fm": "FM05",
        "description": "Impeller aerodynamic fouling",
        "effects": {"polytropic_eff": -6.5, "discharge_temp": 11, "power": 750, "flow": -16,
                    "vib_de": 3, "vib_nde": 3},
    },
    "dgs_degradation": {
        "expected_fm": "FM06",
        "description": "Dry gas seal primary stage degradation",
        "effects": {"primary_vent_flow": 7.5, "seal_gas_dp": -1.1},
    },
    "thrust_bearing_wear": {
        "expected_fm": "FM07",
        "description": "Thrust bearing wear",
        "effects": {"axial_disp": 0.42, "thrust_brg_temp": 24, "vib_de": 2.5,
                    "lube_oil_temp": 0.5},
    },
    "asv_passing": {
        "expected_fm": "FM08",
        "description": "Anti-surge recycle valve passing",
        "effects": {"suction_temp": 9, "discharge_temp": 8, "power": 950, "flow": -13,
                    "polytropic_eff": -0.3},
    },
    "strainer_blockage": {
        "expected_fm": "FM09",
        "description": "Suction strainer blockage",
        "effects": {"suction_pressure": -3.6, "flow": -20, "discharge_temp": 6,
                    "power": -150, "polytropic_eff": -0.4},
    },
}


def progression(t_days: np.ndarray, onset: float, end: float, shape: float = 1.8) -> np.ndarray:
    """P-F curve: 0 before onset, accelerating towards 1 at 'end'.

    shape > 1 gives the classic slow-start, fast-finish degradation curve.
    """
    p = (t_days - onset) / (end - onset)
    return np.clip(p, 0, 1) ** shape


def simulate(
    fault: str | None = None,
    days: int = 60,
    onset_day: float = 38.0,
    seed: int = 0,
    freq_min: int = 10,
    start: str = "2026-09-01",
) -> pd.DataFrame:
    """Generate one compressor history.

    fault      : key from FAULTS, or None for a healthy machine
    days       : length of history
    onset_day  : day the fault starts developing (P point)
    """
    rng = np.random.default_rng(seed)
    asset = load_asset()
    sensors = asset["sensors"]

    n = int(days * 24 * 60 / freq_min)
    t_days = np.arange(n) * freq_min / (24 * 60)
    ts = pd.date_range(start, periods=n, freq=f"{freq_min}min")

    # --- Operating context: daily ambient cycle + slow load wander --------------
    ambient = np.sin(2 * np.pi * (t_days - 0.375))            # peaks mid-afternoon
    load = np.zeros(n)
    for i in range(1, n):                                        # AR(1) random walk
        load[i] = 0.995 * load[i - 1] + rng.normal(0, 0.002)
    load = 1 + 0.02 * np.sin(2 * np.pi * t_days) + load          # ~ +/-3 % load swings

    data = {}
    for tag, s in sensors.items():
        base = np.full(n, float(s["normal"]))
        # correlated (smooth) noise looks more like real transmitters than white noise
        white = rng.normal(0, s["noise"], n)
        smooth = pd.Series(white).rolling(3, min_periods=1).mean().to_numpy() * 1.4
        data[tag] = base + smooth

    # Physical couplings with load and ambient
    data["flow"] += 250 * (load - 1)
    data["power"] += 12000 * 1.3 * (load - 1)
    data["discharge_temp"] += 1.5 * ambient + 40 * (load - 1)
    data["suction_temp"] += 2.0 * ambient
    data["lube_oil_temp"] += 0.8 * ambient
    for b in ("brg_temp_de", "brg_temp_nde", "thrust_brg_temp"):
        data[b] += 0.6 * ambient + 20 * (load - 1)

    # --- Occasional process upsets (short, harmless) - tests false alarms -------
    for _ in range(rng.integers(2, 5)):
        c = rng.integers(0, n - 20)
        w = slice(c, c + rng.integers(4, 12))                    # 40 min - 2 h
        data["flow"][w] -= rng.uniform(8, 15)
        data["power"][w] -= rng.uniform(300, 600)

    # --- Inject fault -------------------------------------------------------------
    p = np.zeros(n)
    if fault is not None:
        if fault not in FAULTS:
            raise ValueError(f"Unknown fault '{fault}'. Options: {list(FAULTS)}")
        p = progression(t_days, onset_day, days)
        sev = rng.uniform(0.9, 1.1)                               # fault-to-fault variability
        for tag, delta in FAULTS[fault]["effects"].items():
            data[tag] = data[tag] + delta * sev * p

    df = pd.DataFrame(data, index=ts)
    df.index.name = "timestamp"
    df["fault_true"] = fault or "healthy"
    df["fault_progress"] = p
    return df


if __name__ == "__main__":
    out = simulate("bearing_wear_de", seed=1)
    print(out.tail(3).T)
