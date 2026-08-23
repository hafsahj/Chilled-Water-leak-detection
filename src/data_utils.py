"""Loading, pivoting, and merging the raw chilled-water sensor data.

Each raw file shares a `Timestamp` column at 2-hourly resolution:
  - weather:            heat index
  - makeup flow:         instantaneous makeup-water flow
  - makeup totalizer:    daily totalizer (MFDT) — used to flag likely leak days
  - building meters:     Flow / DeltaT / MixTemp / StationCO, one row per (building, meter, timestamp)

Kept deliberately thin and un-opinionated about which files a given notebook
merges together — see the load cell in each notebook for that composition.
"""
import os

import pandas as pd

from . import config


def _path(filename: str) -> str:
    return os.path.join(config.DATA_DIR, filename)


def load_csv(filename: str, rename_values_to: str | None = None) -> pd.DataFrame:
    """Load a Timestamp-indexed CSV, drop NAs, optionally rename the `values` column."""
    df = pd.read_csv(_path(filename), parse_dates=["Timestamp"])
    df = df.dropna()
    if rename_values_to:
        df = df.rename(columns={"values": rename_values_to})
    return df


def load_building_meters(filename: str = config.BUILDING_SUMMARY_FILE) -> pd.DataFrame:
    df = pd.read_csv(
        _path(filename),
        names=["Building", "Meter", "Timestamp", "Flow", "DeltaT", "MixTemp", "StationCO"],
    )
    df = df.dropna()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df


def pivot_buildings(buildings: pd.DataFrame) -> pd.DataFrame:
    """Long -> wide: one column per (Building, Meter, Feature) combination, indexed by Timestamp."""
    wide = buildings.pivot_table(
        index="Timestamp", columns=["Building", "Meter"], values=["Flow", "DeltaT", "StationCO"]
    )
    wide.columns = [f"{building}_{meter}_{feature}" for feature, building, meter in wide.columns]
    return wide


def drop_constant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop zero-variance numeric columns (e.g. meters that never reported data).

    Restricted to numeric columns before computing std() — computing std() over the
    whole frame (including the Timestamp column) misaligns the boolean mask against
    df.columns on newer pandas versions and raises an IndexError.
    """
    numeric = df.select_dtypes(include="number")
    constant_cols = numeric.columns[numeric.std() == 0]
    if len(constant_cols):
        print(f"Dropping {len(constant_cols)} constant columns:", list(constant_cols))
    return df.drop(columns=constant_cols)
