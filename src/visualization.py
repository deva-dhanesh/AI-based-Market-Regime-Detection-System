import matplotlib.pyplot as plt

def plot_regime(df):
    plt.figure(figsize=(14,6))
    plt.scatter(df.index, df['Close'], c=df['regime'], cmap='tab10')
    plt.title("AI-Based Market Regime Detection")
    plt.xlabel("Date")
    plt.ylabel("NIFTY 50")
    plt.show()
