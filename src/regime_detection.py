import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


# =====================================
# MARKET REGIME DETECTION (ROBUST)
# =====================================

def detect_regime(df, max_clusters=4):
    """
    Detects market regimes using KMeans clustering.

    Fully robust for:
    - All timeframes (1m → 1mo)
    - All date ranges
    - Small datasets
    - Intraday data limits
    - NaN safety
    """

    # Required features
    feature_cols = ['returns', 'volatility', 'rsi', 'macd']

    # Safety: ensure columns exist
    missing = [col for col in feature_cols if col not in df.columns]

    if missing:
        df['regime'] = 0
        df['confidence'] = 0.0
        return df


    # Drop NaN rows
    df = df.copy()
    df = df.dropna(subset=feature_cols)


    # Count usable samples
    n_samples = len(df)


    # =====================================
    # CASE 1: NO DATA
    # =====================================

    if n_samples == 0:

        df['regime'] = 0
        df['confidence'] = 0.0

        return df


    # =====================================
    # CASE 2: VERY SMALL DATA
    # =====================================

    if n_samples < 4:

        # Assign neutral regime safely
        df['regime'] = 0

        # Confidence low
        df['confidence'] = 25.0

        return df


    # =====================================
    # CASE 3: NORMAL OPERATION
    # =====================================

    # Dynamic cluster count
    n_clusters = min(max_clusters, n_samples)

    features = df[feature_cols].values


    # Fit KMeans safely
    try:

        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )

        labels = kmeans.fit_predict(features)

        df['regime'] = labels


        # =====================================
        # CONFIDENCE SCORE
        # =====================================

        distances = kmeans.transform(features)

        min_dist = np.min(distances, axis=1)
        max_dist = np.max(distances)

        # Avoid division by zero
        if max_dist == 0:
            confidence = np.ones_like(min_dist) * 0.5
        else:
            confidence = 1 - (min_dist / max_dist)


        df['confidence'] = (confidence * 100).round(2)


    except Exception:

        # Absolute fallback safety
        df['regime'] = 0
        df['confidence'] = 25.0


    return df
