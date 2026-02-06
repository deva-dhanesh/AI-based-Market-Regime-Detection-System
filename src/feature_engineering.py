import pandas as pd

def add_features(df):
    # Returns
    df['returns'] = df['Close'].pct_change()

    # Volatility (20-day rolling std)
    df['volatility'] = df['returns'].rolling(window=20).std()

    # RSI (manual calculation)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD (manual calculation)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26

    df.dropna(inplace=True)
    return df
