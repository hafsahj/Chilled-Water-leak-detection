"""LSTM autoencoder architecture (Approach 1)."""
from tensorflow.keras.layers import LSTM, Dense, Input, RepeatVector, TimeDistributed
from tensorflow.keras.models import Model


def build_lstm_autoencoder(timesteps: int, num_features: int) -> Model:
    """Two-layer LSTM encoder/decoder trained to reconstruct normal input windows.

    Large reconstruction error on a held-out window signals abnormal system behavior.
    """
    inputs = Input(shape=(timesteps, num_features))

    encoded = LSTM(128, activation="relu", return_sequences=True)(inputs)
    encoded = LSTM(64, activation="relu")(encoded)

    bottleneck = RepeatVector(timesteps)(encoded)

    decoded = LSTM(64, activation="relu", return_sequences=True)(bottleneck)
    decoded = LSTM(128, activation="relu", return_sequences=True)(decoded)
    outputs = TimeDistributed(Dense(num_features))(decoded)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer="adam", loss="mse")
    return model
