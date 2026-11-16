"""
detect.py - anomaly detection (the 'alarm').

In the AIQ/ADNOC context this layer is already covered by tools like Neuron 5.
We include a simple, transparent version so the agent has alerts to respond to.

Method: robust z-score per sensor against a healthy baseline period.
  z = (smoothed value - baseline median) / (1.4826 * baseline MAD)
MAD (median absolute deviation) is used instead of standard deviation because it
is not distorted by the occasional spike - same reason we use median voting (2oo3)
instead of averaging in safety systems.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import load_asset

SMOOTH_WINDOW = "6h"     # rolling mean - filters short process upsets
Z_ALERT = 6.0            # deviation (in robust std devs) that counts as abnormal
                         # (healthy-machine tests peak at ~4-5, so 6 keeps false alarms out)
MIN_MARGIN = 0.04       # change must use >= 4 % of the normal-to-alarm margin
BASELINE_DAYS = 21       # first 3 weeks assumed healthy = the "learning" period
PERSISTENCE = 6          # consecutive samples above Z_ALERT before alerting (1 h at 10 min)


@dataclass
class Alert:
    timestamp: pd.Timestamp
    triggered_sensors: list[str]
    z_snapshot: dict[str, float] = field(default_factory=dict)


def sensor_columns(df: pd.DataFrame) -> list[str]:
    tags = load_asset()["sensors"].keys()
    return [c for c in df.columns if c in tags]


def _residuals(df: pd.DataFrame, baseline_days: int) -> tuple[pd.DataFrame, pd.Series]:
    """Smoothed deviation from normal (engineering units) and baseline spread (MAD)."""
    cols = sensor_columns(df)
    smooth = df[cols].rolling(SMOOTH_WINDOW, min_periods=1).mean()
    is_base = smooth.index < smooth.index[0] + pd.Timedelta(days=baseline_days)
    # Remove the normal daily pattern (ambient temperature, day/night load) learned
    # during the baseline - like ambient compensation on a transmitter.
    hour = smooth.index.hour
    profile = smooth[is_base].groupby(hour[is_base]).median()
    resid = smooth - profile.reindex(hour).to_numpy()
    base = resid[is_base]
    resid = resid - base.median()
    mad = (base - base.median()).abs().median() * 1.4826
    return resid, mad.replace(0, np.nan).fillna(1e-9)


def zscores(df: pd.DataFrame, baseline_days: int = BASELINE_DAYS) -> pd.DataFrame:
    """Signed robust z-score: how UNUSUAL is the change (statistics)."""
    resid, mad = _residuals(df, baseline_days)
    return resid / mad


def margin_fraction(df: pd.DataFrame, baseline_days: int = BASELINE_DAYS) -> pd.DataFrame:
    """Signed deviation as a fraction of the normal-to-alarm margin: how MEANINGFUL
    is the change (engineering). E.g. vibration 18 -> 26 um with alarm 50 = 0.25.
    Sensors without an alarm limit use 5 % of normal value as the reference."""
    resid, _ = _residuals(df, baseline_days)
    sens = load_asset()["sensors"]
    ref = {}
    for c in resid.columns:
        s = sens[c]
        ref[c] = abs(s["alarm"] - s["normal"]) if s.get("alarm") is not None else 0.05 * abs(s["normal"])
    return resid / pd.Series(ref)


def health_index(z: pd.DataFrame, frac: pd.DataFrame) -> pd.Series:
    """0-100 health score = 100 minus the largest share of normal-to-alarm margin used
    by any sensor that has moved significantly towards its limit (|z| >= 3).
    100 = everything normal, 0 = a sensor is at its alarm limit."""
    sens = load_asset()["sensors"]
    sign = pd.Series({c: (1 if sens[c]["direction"] == "high" else -1) for c in frac.columns})
    used = (frac * sign).where(z.abs() >= 3, 0).clip(lower=0)
    return (100 * (1 - used.max(axis=1))).clip(0, 100).rename("health_index")


def first_alert(z: pd.DataFrame, frac: pd.DataFrame | None = None,
                baseline_days: int = BASELINE_DAYS) -> Alert | None:
    """First time (after the learning period) any sensor stays abnormal for PERSISTENCE samples.

    Abnormal = statistically unusual (|z| >= Z_ALERT) AND engineering-meaningful
    (has used >= MIN_MARGIN of its margin to alarm) - the second test works like an
    alarm deadband, so tiny-but-unusual wiggles don't raise alerts.
    """
    keep = z.index >= z.index[0] + pd.Timedelta(days=baseline_days)
    z = z[keep]
    above = z.abs() >= Z_ALERT
    if frac is not None:
        # only movement TOWARDS the alarm limit counts as deterioration
        sens = load_asset()["sensors"]
        sign = pd.Series({c: (1 if sens[c]["direction"] == "high" else -1) for c in frac.columns})
        above &= (frac[keep] * sign) >= MIN_MARGIN
    # count consecutive samples above the limit, separately for each sensor
    run = above.apply(lambda col: col.astype(int).groupby((~col).cumsum()).cumsum())
    hit = (run >= PERSISTENCE)
    any_hit = hit.any(axis=1)
    if not any_hit.any():
        return None
    ts = any_hit.idxmax()
    trig = [c for c in z.columns if hit.loc[ts, c]]
    return Alert(timestamp=ts, triggered_sensors=trig, z_snapshot=z.loc[ts].round(2).to_dict())


def time_to_limit(df: pd.DataFrame, tag: str, at: pd.Timestamp, limit: float,
                  direction: str, lookback_days: float = 5, horizon_days: float = 90) -> float | None:
    """Estimate days until 'tag' crosses 'limit', from its recent trend.

    Fits both a straight line and a curve (quadratic) to the last few days and takes
    the EARLIER crossing - deliberately conservative, because degradation usually
    accelerates (the P-F curve bends downward).
    Returns None if no crossing is predicted within the horizon.
    """
    s = df[tag].rolling(SMOOTH_WINDOW, min_periods=1).mean()
    s = s[(s.index > at - pd.Timedelta(days=lookback_days)) & (s.index <= at)]
    if len(s) < 10:
        return None
    x = (s.index - at).total_seconds().to_numpy() / 86400.0       # days, <= 0
    y = s.to_numpy()
    now = y[-12:].mean()
    if (direction == "high" and now >= limit) or (direction == "low" and now <= limit):
        return 0.0

    future = np.linspace(0, horizon_days, int(horizon_days * 24) + 1)
    crossings = []
    for deg in (1, 2):
        coef = np.polyfit(x, y, deg)
        yf = np.polyval(coef, future)
        cross = yf >= limit if direction == "high" else yf <= limit
        if cross.any():
            crossings.append(float(future[np.argmax(cross)]))
    return min(crossings) if crossings else None
