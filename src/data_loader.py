import yfinance as yf
import pandas as pd


# ================================
# TIMEFRAME → INTERVAL + PERIOD
# ================================

TIMEFRAME_MAP = {

    "1m":  ("1m", "7d"),
    "5m":  ("5m", "60d"),
    "15m": ("15m", "60d"),

    "1h":  ("1h", "730d"),

    # 4h derived from 1h
    "4h":  ("1h", "730d"),

    "1d":  ("1d", "max"),
    "1w":  ("1wk", "max"),
    "1mo": ("1mo", "max"),

}


# ================================
# SYMBOL MAP (ALL NIFTY 50)
# ================================

SYMBOL_MAP = {

    # Index
    "NIFTY 50": "^NSEI",

    # Stocks
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "APOLLOHOSP": "APOLLOHOSP.NS",
    "ASIANPAINT": "ASIANPAINT.NS",
    "AXISBANK": "AXISBANK.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS",
    "BEL": "BEL.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "BPCL": "BPCL.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "CIPLA": "CIPLA.NS",
    "COALINDIA": "COALINDIA.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "DRREDDY": "DRREDDY.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "GRASIM": "GRASIM.NS",
    "HCLTECH": "HCLTECH.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "HDFCLIFE": "HDFCLIFE.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS",
    "HINDALCO": "HINDALCO.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "INDUSINDBK": "INDUSINDBK.NS",
    "INFY": "INFY.NS",
    "ITC": "ITC.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "LT": "LT.NS",
    "M&M": "M&M.NS",
    "MARUTI": "MARUTI.NS",
    "NESTLEIND": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "POWERGRID": "POWERGRID.NS",
    "RELIANCE": "RELIANCE.NS",
    "SBILIFE": "SBILIFE.NS",
    "SBIN": "SBIN.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TATACONSUM": "TATACONSUM.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "TCS": "TCS.NS",
    "TECHM": "TECHM.NS",
    "TITAN": "TITAN.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "UPL": "UPL.NS",
    "WIPRO": "WIPRO.NS"

}


# ================================
# GET ALL SYMBOL NAMES (for dropdown)
# ================================

def get_all_symbols():

    return list(SYMBOL_MAP.keys())


# ================================
# LOAD DATA FUNCTION
# ================================

def load_data(symbol="NIFTY 50", timeframe="1d"):

    """
    Loads OHLCV market data for given symbol and timeframe.
    """

    # Resolve Yahoo ticker
    ticker = SYMBOL_MAP.get(symbol, symbol)

    # Resolve interval and period
    interval, period = TIMEFRAME_MAP.get(timeframe, ("1d", "max"))


    # Download data
    df = yf.download(
        ticker,
        interval=interval,
        period=period,
        auto_adjust=False,
        progress=False
    )


    # Safety check
    if df.empty:
        return df


    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):

        df.columns = df.columns.get_level_values(0)


    # Keep only required columns
    df = df[["Open", "High", "Low", "Close", "Volume"]]


    # Convert index to datetime
    df.index = pd.to_datetime(df.index)


    # ============================
    # FIXED: 4 HOUR RESAMPLING
    # ============================

    if timeframe == "4h":

        df = df.resample("4h").agg({

            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"

        })

        df.dropna(inplace=True)


    # Remove missing values
    df.dropna(inplace=True)


    return df
