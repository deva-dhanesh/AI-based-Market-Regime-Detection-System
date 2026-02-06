import pandas as pd


def compute_regime_statistics(df):
    """
    Compute average return and volatility for each regime.
    """
    stats = df.groupby("regime").agg({
        "returns": "mean",
        "volatility": "mean"
    }).rename(columns={
        "returns": "avg_return",
        "volatility": "avg_volatility"
    })

    return stats


def dynamic_regime_mapping(df):
    """
    Automatically assign meaning to each regime based on statistics.
    """

    stats = compute_regime_statistics(df)

    mapping = {}

    for regime_id, row in stats.iterrows():

        avg_return = row["avg_return"]
        avg_vol = row["avg_volatility"]

        # Logic to determine regime meaning
        if avg_return > 0 and avg_vol < stats["avg_volatility"].mean():
            name = "Bull Market"
            description = "Uptrend with positive returns and controlled volatility"

        elif avg_return < 0 and avg_vol < stats["avg_volatility"].mean():
            name = "Bear Market"
            description = "Downtrend with negative returns"

        elif avg_vol > stats["avg_volatility"].mean():
            name = "High Volatility"
            description = "Large price swings and unstable conditions"

        else:
            name = "Sideways Market"
            description = "Low momentum and range-bound movement"

        mapping[regime_id] = {
            "name": name,
            "description": description
        }

    return mapping


def regime_name(regime_id, mapping):
    return mapping.get(regime_id, {}).get("name", "Unknown")


def strategy_for_regime(regime_id, mapping):

    name = mapping.get(regime_id, {}).get("name", "")

    if name == "Bull Market":
        return "Trend Following (Buy)"

    elif name == "Bear Market":
        return "Capital Protection (Sell / Hedge)"

    elif name == "Sideways Market":
        return "Range Trading / Mean Reversion"

    elif name == "High Volatility":
        return "Reduce exposure / Wait"

    return "No strategy"
