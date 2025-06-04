# Chilled Water Leak Detection – UIowa

This repository contains two core analysis notebooks focused on detecting building-level contributors to chilled water leaks at the University of Iowa. The approaches are based on either anomaly detection using LSTM autoencoders or spike pattern detection via engineered leak signatures.

## Structure

- `CW_Approach_1_(LSTM_Autoencoder).ipynb`  
  Deep learning–based approach using a sequence-to-sequence LSTM autoencoder. Trained to reconstruct normal behavior and flag anomalies via reconstruction error spikes.

- `CW_Approach_2_(Moving_avgs).ipynb`  
  A signal-based method using rolling mean, standard deviation, and multi-signal leak signatures (Flow, DeltaT, StationCO) to detect potential culprits at the start of known leak periods.

## Summary of Approaches

### 1. LSTM Autoencoder
- **Input**: 24-timestep windows of 361 building-level features.
- **Model**: Two-layer LSTM encoder and decoder.
- **Output**: Reconstruction error used to detect abnormal system behavior.
- **Purpose**: Learn normal operating patterns and highlight deviations.

### 2. Leak Signature Scoring
- **Signals**: Flow, DeltaT, StationCO
- **Method**: 7-period rolling mean and standard deviation thresholding.
- **Logic**: Mark timestamp as a leak signature if all three signals spike together.
- **Use**: Detect culprit buildings on the first day of known leak periods.

## Outcomes
- Successfully identified known confirmed leaks (e.g., Boyd Tower and South Wing).
- Signature-based method offers higher interpretability and speed with current data.

## Future Work
- Extend signature analysis across full leak periods.
- Compare leak events across 2022–2025.
- Integrate results into an interactive Power BI dashboard.
