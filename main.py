from src.data_loader import load_data
from src.feature_engineering import add_features
from src.regime_detection import detect_regime
from src.strategy import regime_name, strategy_for_regime
from src.visualization import plot_regime

df = load_data()
df = add_features(df)
df = detect_regime(df)

current_regime = df['regime'].iloc[-1]

print("Current Market Regime:", regime_name(current_regime))
print("Suggested Strategy:", strategy_for_regime(current_regime))

plot_regime(df)
