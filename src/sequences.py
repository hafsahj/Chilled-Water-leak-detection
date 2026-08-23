"""Windowing utilities for the LSTM autoencoder (Approach 1)."""
import numpy as np
import pandas as pd


def create_sequences(data: pd.DataFrame, window_size: int = 24) -> np.ndarray:
    """Slide a `window_size`-step window over `data`.

    Returns an array of shape (n_windows, window_size, n_features).
    """
    values = data.values
    n_windows = len(values) - window_size
    return np.array([values[i : i + window_size] for i in range(n_windows)])
