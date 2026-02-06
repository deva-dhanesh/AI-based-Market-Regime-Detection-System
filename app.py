from flask import Flask, render_template, request
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_loader import load_data, get_all_symbols
from src.feature_engineering import add_features
from src.regime_detection import detect_regime
from src.strategy import (
    dynamic_regime_mapping,
    regime_name,
    strategy_for_regime
)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    # =====================================
    # LOAD SYMBOL LIST
    # =====================================

    symbols = get_all_symbols()


    # =====================================
    # USER INPUTS
    # =====================================

    symbol = request.form.get("symbol", "NIFTY 50")

    timeframe = request.form.get("timeframe", "1d")

    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")


    # =====================================
    # LOAD DATA
    # =====================================

    try:

        df = load_data(symbol=symbol, timeframe=timeframe)

    except Exception:

        return render_template(
            "index.html",
            graph=None,
            regime="Data loading error",
            strategy="Try different timeframe",
            explanation="Unable to fetch market data",
            confidence=None,
            symbols=symbols,
            symbol=symbol,
            timeframe=timeframe,
            regime_map={},
            current_regime_id=None,
            start_date=start_date,
            end_date=end_date
        )


    # =====================================
    # DATE FILTER
    # =====================================

    if start_date:

        df = df[df.index >= start_date]

    if end_date:

        df = df[df.index <= end_date]


    # =====================================
    # SAFETY CHECK: EMPTY DATA
    # =====================================

    if df.empty:

        return render_template(
            "index.html",
            graph=None,
            regime="No Data Available",
            strategy="Increase timeframe or date range",
            explanation="Selected timeframe/date range has insufficient market data",
            confidence=None,
            symbols=symbols,
            symbol=symbol,
            timeframe=timeframe,
            regime_map={},
            current_regime_id=None,
            start_date=start_date,
            end_date=end_date
        )


    # =====================================
    # FEATURE ENGINEERING
    # =====================================

    df = add_features(df)


    # =====================================
    # SAFETY CHECK: MINIMUM DATA FOR ML
    # =====================================

    usable_rows = df.dropna().shape[0]

    if usable_rows < 4:

        # fallback safe output
        fallback_regime = "Insufficient Data"

        fallback_strategy = "Increase date range"

        fallback_explanation = (
            "Not enough market data available for reliable regime detection."
        )

        fallback_confidence = 0


        return render_template(
            "index.html",
            graph=None,
            regime=fallback_regime,
            strategy=fallback_strategy,
            explanation=fallback_explanation,
            confidence=fallback_confidence,
            symbols=symbols,
            symbol=symbol,
            timeframe=timeframe,
            regime_map={},
            current_regime_id=None,
            start_date=start_date,
            end_date=end_date
        )


    # =====================================
    # REGIME DETECTION
    # =====================================

    df = detect_regime(df)


    # =====================================
    # RESET INDEX
    # =====================================

    df = df.reset_index()

    if "Datetime" in df.columns:
        df.rename(columns={"Datetime": "Date"}, inplace=True)

    if "index" in df.columns:
        df.rename(columns={"index": "Date"}, inplace=True)


    # =====================================
    # REGIME MAPPING
    # =====================================

    regime_map = dynamic_regime_mapping(df)


    # =====================================
    # CURRENT REGIME INFO
    # =====================================

    current_regime_id = df["regime"].iloc[-1]

    current_confidence = float(df["confidence"].iloc[-1])

    current_regime_name = regime_name(current_regime_id, regime_map)

    current_strategy = strategy_for_regime(current_regime_id, regime_map)

    current_explanation = regime_map[current_regime_id]["description"]


    # =====================================
    # CREATE CHART
    # =====================================

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.75, 0.25]
    )


    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        ),
        row=1, col=1
    )


    # Volume colors
    volume_colors = [
        "green" if close >= open else "red"
        for close, open in zip(df["Close"], df["Open"])
    ]


    # Volume bars
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Volume"],
            marker_color=volume_colors,
            name="Volume"
        ),
        row=2, col=1
    )


    # Layout
    fig.update_layout(

        xaxis_rangeslider_visible=False,

        template="plotly_white",

        height=700,

        yaxis=dict(title="Price", tickformat=",.2f"),

        yaxis2=dict(title="Volume"),

        xaxis=dict(showticklabels=False),

        xaxis2=dict(title="Date")

    )


    graph_html = fig.to_html(full_html=False, include_plotlyjs="cdn")


    # =====================================
    # FINAL RENDER
    # =====================================

    return render_template(
        "index.html",

        graph=graph_html,

        regime=current_regime_name,

        strategy=current_strategy,

        explanation=current_explanation,

        confidence=current_confidence,

        symbols=symbols,

        symbol=symbol,

        timeframe=timeframe,

        regime_map=regime_map,

        current_regime_id=current_regime_id,

        start_date=start_date,

        end_date=end_date
    )


# =====================================
# RUN APP
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
