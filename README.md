# Chilled Water Leak Detection

Two approaches to spotting building-level contributors to chilled-water leaks from campus utility sensor data: unsupervised anomaly detection with an LSTM autoencoder, and a simpler signal-based leak-signature scorer.

This was originally built against a full year of real campus chilled-water data: six buildings' worth of Flow, DeltaT, and StationCO meters, plus weather and makeup-water flow, all at 2-hourly resolution. That data isn't shareable, so this repo ships with a synthetic dataset generator (`scripts/generate_demo_data.py`) that matches the same schema and injects one deliberate leak. Everything here runs end to end against it.

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

## Approach 1: LSTM Autoencoder

Takes 24-timestep (48h) windows of building-level features at 2-hourly resolution and feeds them into a two-layer LSTM encoder/decoder trained to reconstruct normal operating windows. Windows with the highest reconstruction error get flagged as anomalies, and that error gets attributed back to individual buildings to produce a `LeakScore` (see `src/scoring.py` for the reasoning: a leak tends to show up as higher flow and conductivity with a smaller temperature differential).

## Approach 2: Leak-Signature Scoring

Weather-adjusts each building's Flow, DeltaT, and StationCO, then uses rolling mean/std thresholding to catch spikes across all three signals at once, pointing to the specific culprit building. It's faster and more interpretable than the autoencoder, no training needed, but it relies on hand-tuned thresholds instead of learned normal behavior.

## Setup

```bash
git clone https://github.com/hafsahj/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
python scripts/generate_demo_data.py
```

Then run either notebook top to bottom. To use your own data instead, drop it into `data/` following the schema in `data/README.md`, or set `CW_DATA_DIR` to point elsewhere.

## Future Work

- Extend signature analysis across full leak periods, not just start days.
- Compare leak events across multiple years.
- Integrate results into an interactive dashboard.

## License

MIT, see [LICENSE](LICENSE).
