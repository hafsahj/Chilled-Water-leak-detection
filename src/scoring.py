"""Turning reconstruction error / rolling statistics into building-level leak suspects."""
from collections import defaultdict

import numpy as np
import pandas as pd


def per_feature_reconstruction_error(X_true: np.ndarray, X_pred: np.ndarray, columns) -> pd.DataFrame:
    """Per-window, per-feature MSE (averaged over the timestep axis). One row per window."""
    errors = np.mean((X_pred - X_true) ** 2, axis=1)  # (n_windows, n_features)
    return pd.DataFrame(errors, columns=columns)


def score_buildings(period_errors: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-feature reconstruction error (Approach 1) into a per-building leak score.

    LeakScore = normalized(FlowError) + normalized(StationCOError) - normalized(DeltaTError)

    Rationale: a real leak tends to show up as elevated flow and station conductivity
    alongside a *smaller* temperature differential (make-up water dilutes the loop), so
    DeltaT error is subtracted rather than added.
    """
    flow_err, deltat_err, co_err = defaultdict(float), defaultdict(float), defaultdict(float)

    for col in period_errors.columns:
        if col in ("Timestamp", "values", "makeupFlow"):
            continue
        building = col.split("_")[0]
        if col.endswith("Flow"):
            flow_err[building] += period_errors[col].mean()
        elif col.endswith("DeltaT"):
            deltat_err[building] += period_errors[col].mean()
        elif col.endswith("StationCO"):
            co_err[building] += period_errors[col].mean()

    buildings = set(flow_err) | set(deltat_err) | set(co_err)
    score_df = pd.DataFrame({"Building": list(buildings)})
    score_df["FlowError"] = score_df["Building"].map(flow_err)
    score_df["DeltaTError"] = score_df["Building"].map(deltat_err)
    score_df["StationCOError"] = score_df["Building"].map(co_err)

    for col in ("FlowError", "DeltaTError", "StationCOError"):
        score_df[col] = score_df[col] / score_df[col].max()

    score_df["LeakScore"] = score_df["FlowError"] + score_df["StationCOError"] - score_df["DeltaTError"]
    return score_df.sort_values("LeakScore", ascending=False)


def flag_signature_spikes(
    df: pd.DataFrame, signal_cols, rolling_window: int, std_threshold: float
) -> pd.DataFrame:
    """Add a `<col>_sig_spike` flag per signal: a rolling-window z-score spike (Approach 2).

    Flow / StationCO: spike = value > rolling_mean + k*rolling_std (leak raises flow/conductivity).
    DeltaT: spike = value < rolling_mean - k*rolling_std (leak lowers the temperature differential).
    """
    df = df.copy()
    for col in signal_cols:
        rolling_mean = df[col].rolling(rolling_window, min_periods=1).mean()
        rolling_std = df[col].rolling(rolling_window, min_periods=1).std()
        if "_DeltaT" in col:
            spike = df[col] < (rolling_mean - std_threshold * rolling_std)
        else:
            spike = df[col] > (rolling_mean + std_threshold * rolling_std)
        df[f"{col}_sig_spike"] = spike.astype(int)
    return df


def find_leak_signature_culprits(df: pd.DataFrame, flow_cols) -> list:
    """A (timestamp, meter) is a 'culprit' when Flow, DeltaT, and StationCO all spike together."""
    records = []
    for _, row in df.iterrows():
        for flow_col in flow_cols:
            meter = "_".join(flow_col.split("_")[:4])
            deltat_col, co_col = f"{meter}_DeltaT", f"{meter}_StationCO"
            spike_cols = [f"{c}_sig_spike" for c in (flow_col, deltat_col, co_col)]
            if all(c in df.columns for c in spike_cols) and all(row.get(c, 0) for c in spike_cols):
                records.append((row["Timestamp"], meter))
    return records
