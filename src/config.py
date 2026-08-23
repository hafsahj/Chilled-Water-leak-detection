"""Central configuration for the chilled-water leak-detection pipeline.

Data files are not included in this repo (see data/README.md for the expected
schema). Point CW_DATA_DIR at your local copy, either via the environment
variable or by editing DATA_DIR below.
"""
import os

DATA_DIR = os.environ.get("CW_DATA_DIR", "data")

WEATHER_FILE = "weather_data_2024.csv"
MAKEUP_FLOW_FILE = "makeup_flow_2024.csv"        # instantaneous makeup flow (used in Approach 2 only)
MAKEUP_TOTALIZER_FILE = "makeup_data_2024.csv"   # daily totalizer (MFDT)
BUILDING_SUMMARY_FILE = "summary_data_2024.csv"

RANDOM_SEED = 42

# --- Approach 1: LSTM autoencoder ---
WINDOW_SIZE = 24            # 2-hourly readings -> 48h lookback window
ANOMALY_PERCENTILE = 60     # reconstruction-error percentile flagged as anomalous

# --- Approach 2: leak-signature scoring ---
ROLLING_WINDOW = 7           # periods used for rolling mean/std
STD_THRESHOLD_BROAD = 2.2    # pass 1: wide net across a full known leak period
STD_THRESHOLD_REFINED = 1.8  # pass 2: tighter, applied only to the leak start day
LEAK_MFDT_THRESHOLD = 10000  # MFDT value above which a day is flagged as a likely leak day

KNOWN_LEAK_PERIODS = {
    "Feb10_Feb14": ("2024-02-08", "2024-02-16"),
}
KNOWN_LEAK_START_DAYS = {
    "Feb10_Feb14": "2024-02-10",
}
