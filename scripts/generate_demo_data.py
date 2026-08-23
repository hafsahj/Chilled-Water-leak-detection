"""Generates a synthetic demo dataset matching the schema in data/README.md.

Real campus utility data isn't included in this repo. This script produces a
stand-in dataset with the same shape and column names — normal daily/seasonal
cycles across several buildings, plus one deliberately injected leak (elevated
flow and conductivity, suppressed temperature differential) — so the notebooks
can be run end-to-end and produce real, reproducible output.

Usage:
    python scripts/generate_demo_data.py
"""
import os

import numpy as np
import pandas as pd

from src import config

SEED = 7
START = "2024-01-01"
PERIODS = 24 * 60  # 60 days at 2-hourly resolution
FREQ = "2h"

BUILDINGS = [
    ("North Hall", "CWP_NH_C10"),
    ("Central Library", "CWP_CL_C22"),
    ("Engineering Building", "CWP_EB_C31"),
    ("Recreation Center", "CWP_RC_C44"),
    ("Chemistry Building", "CWP_CB_C57"),
    ("Residence Hall West", "CWP_RHW_C68"),
]

LEAK_BUILDING = "Central Library"
LEAK_START = "2024-02-10"
LEAK_END = "2024-02-14"


def main():
    rng = np.random.default_rng(SEED)
    ts = pd.date_range(START, periods=PERIODS, freq=FREQ, tz="UTC")
    day_frac = (ts.hour + ts.minute / 60) / 24
    season = np.sin(2 * np.pi * (ts.dayofyear / 365))

    heat_index = 45 + 15 * season + 8 * np.sin(2 * np.pi * day_frac) + rng.normal(0, 2, PERIODS)
    weather = pd.DataFrame({"Timestamp": ts, "values": heat_index})

    base_makeup = 2000 + 800 * np.sin(2 * np.pi * day_frac) + rng.normal(0, 150, PERIODS)
    base_totalizer = 4000 + 1500 * np.abs(np.sin(2 * np.pi * day_frac)) + rng.normal(0, 300, PERIODS)

    leak_mask = (ts >= pd.Timestamp(LEAK_START, tz="UTC")) & (ts < pd.Timestamp(LEAK_END, tz="UTC"))
    makeup_flow_vals = base_makeup + np.where(leak_mask, rng.uniform(8000, 14000, PERIODS), 0)
    makeup_totalizer_vals = base_totalizer + np.where(leak_mask, rng.uniform(9000, 16000, PERIODS), 0)

    makeup_flow = pd.DataFrame({"Timestamp": ts, "values": makeup_flow_vals})
    makeup_totalizer = pd.DataFrame({"Timestamp": ts, "values": makeup_totalizer_vals})

    rows = []
    for building, meter in BUILDINGS:
        base_flow = rng.uniform(20, 100)
        base_deltat = rng.uniform(4, 9)
        base_co = rng.uniform(10, 30)

        flow = base_flow + 15 * np.sin(2 * np.pi * day_frac) + rng.normal(0, 3, PERIODS)
        deltat = base_deltat + rng.normal(0, 0.4, PERIODS)
        stationco = base_co + 5 * np.sin(2 * np.pi * day_frac) + rng.normal(0, 1.5, PERIODS)

        if building == LEAK_BUILDING:
            flow = flow + np.where(leak_mask, rng.uniform(40, 70, PERIODS), 0)
            stationco = stationco + np.where(leak_mask, rng.uniform(15, 25, PERIODS), 0)
            deltat = deltat - np.where(leak_mask, rng.uniform(2, 4, PERIODS), 0)

        for t, f, d, c in zip(ts, flow, deltat, stationco):
            rows.append([building, meter, t, max(f, 0), d, 60 + rng.normal(0, 1), max(c, 0)])

    buildings_df = pd.DataFrame(
        rows, columns=["Building", "Meter", "Timestamp", "Flow", "DeltaT", "MixTemp", "StationCO"]
    )

    os.makedirs(config.DATA_DIR, exist_ok=True)
    weather.to_csv(os.path.join(config.DATA_DIR, config.WEATHER_FILE), index=False)
    makeup_flow.to_csv(os.path.join(config.DATA_DIR, config.MAKEUP_FLOW_FILE), index=False)
    makeup_totalizer.to_csv(os.path.join(config.DATA_DIR, config.MAKEUP_TOTALIZER_FILE), index=False)
    buildings_df.to_csv(
        os.path.join(config.DATA_DIR, config.BUILDING_SUMMARY_FILE), index=False, header=False
    )

    print(f"Wrote {PERIODS} timestamps x {len(BUILDINGS)} buildings to {config.DATA_DIR}/")
    print(f"Injected leak: {LEAK_BUILDING}, {LEAK_START} to {LEAK_END}")


if __name__ == "__main__":
    main()
