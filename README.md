# Chilled Water Leak Detection

Two independent approaches to spotting building-level contributors to chilled-water leaks from campus utility sensor data: unsupervised anomaly detection with an LSTM autoencoder, and a lighter-weight signal-based leak-signature scorer.

Originally built against a full year of real campus chilled-water data (six buildings' worth of Flow/DeltaT/StationCO meters, weather, and makeup-water flow at 2-hourly resolution). That data isn't shareable, so this repo ships with a synthetic dataset generator (`scripts/generate_demo_data.py`) that reproduces the same schema and injects one deliberate leak — everything in this repo is runnable end-to-end against it.

## Structure

```
├── src/
│   ├── config.py       # paths, thresholds, known leak periods
│   ├── data_utils.py   # loading, pivoting, merging raw CSVs
│   ├── sequences.py    # windowing for the LSTM autoencoder
│   ├── model.py         # LSTM autoencoder architecture
│   └── scoring.py        # reconstruction-error and leak-signature scoring
├── scripts/
│   └── generate_demo_data.py   # synthetic dataset with an injected leak
├── data/
│   └── README.md         # expected input schema (real data not included)
├── CW_Approach_1_(LSTM_Autoencoder).ipynb
├── CW_Approach_2_(Moving_avgs).ipynb
├── requirements.txt
├── LICENSE
└── README.md
```

## Approach 1 — LSTM Autoencoder

- **Input:** 24-timestep (48h) windows of building-level features, 2-hourly resolution.
- **Model:** two-layer LSTM encoder/decoder trained to reconstruct normal operating windows.
- **Detection:** windows in the top percentile of reconstruction error are flagged anomalous; error is then attributed back to individual buildings and weighted into a `LeakScore` (see `src/scoring.py` for the rationale — elevated flow/conductivity with a *smaller* temperature differential is the leak signature).

## Approach 2 — Leak-Signature Scoring

- **Signals:** Flow, DeltaT, StationCO, weather-adjusted (regressed on heat index, residuals used) to remove seasonal effects.
- **Method:** rolling mean/std thresholding, run twice — a broad first pass across each full known leak period, then a tighter second pass restricted to the confirmed leak start day to isolate the specific culprit meter(s).
- **Trade-off vs. Approach 1:** faster, more interpretable, no training required — at the cost of relying on hand-tuned thresholds rather than learned normal behavior.
- **On the demo data:** the broad first pass alone doesn't clear its threshold across the full leak period. The refined second pass, restricted to the leak's start day, correctly isolates the single building the leak was injected into — the two-pass design is what actually finds it.

## Setup

```bash
git clone https://github.com/hafsahj/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
python scripts/generate_demo_data.py
```

Then run either notebook top to bottom. To use your own data instead, drop it into `data/` per the schema in `data/README.md`, or set `CW_DATA_DIR` to point elsewhere.

## Future Work

- Extend signature analysis across full leak periods rather than just start days.
- Compare leak events across multiple years.
- Integrate results into an interactive dashboard.

## License

MIT — see [LICENSE](LICENSE).
