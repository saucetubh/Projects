import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load Data
df = pd.read_excel("data.xlsx")
df.columns = ["Date", "Open", "High", "Low", "Close", "VWAP",
              "52W_H", "52W_L", "Volume", "Value", "Trades"]
df["Date"] = pd.to_datetime(df["Date"])
df = df.set_index("Date")

# MACD Calculation
sma12 = df["Close"].rolling(window=12).mean()
sma26 = df["Close"].rolling(window=26).mean()
macd_line = sma12 - sma26

# Signal line: seed = simple average of first 9 MACD values
# then EMA with multiplier 2/10 (smoothing factor for 9-day EMA)
first_pos = macd_line.first_valid_index()
first_idx = df.index.get_loc(first_pos)
signal_line = pd.Series(np.nan, index=df.index)
seed_idx = first_idx + 8
signal_line.iloc[seed_idx] = macd_line.iloc[first_idx:seed_idx+1].mean()
for i in range(seed_idx + 1, len(df)):
    signal_line.iloc[i] = (macd_line.iloc[i] - signal_line.iloc[i-1]) * (2/10) + signal_line.iloc[i-1]

histogram = macd_line - signal_line

# MACD Buy/Sell Signals
# Buy when MACD crosses above signal, Sell when MACD crosses below
macd_signal = pd.Series(0, index=df.index)
for i in range(1, len(macd_line)):
    if macd_line.iloc[i] > signal_line.iloc[i] and macd_line.iloc[i-1] <= signal_line.iloc[i-1]:
        macd_signal.iloc[i] = 1   # Buy
    elif macd_line.iloc[i] < signal_line.iloc[i] and macd_line.iloc[i-1] >= signal_line.iloc[i-1]:
        macd_signal.iloc[i] = -1  # Sell

# RSI Calculation 
delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = pd.Series(np.nan, index=df.index)
avg_loss = pd.Series(np.nan, index=df.index)

# For every day from row 14 onwards, take simple average of previous 14 rows
for i in range(14, len(df)):
    avg_gain.iloc[i] = gain.iloc[i-13:i+1].mean()
    avg_loss.iloc[i] = loss.iloc[i-13:i+1].mean()

rs = avg_gain / avg_loss.replace(0, np.nan)
rsi = 100 - (100 / (1 + rs))
rsi = rsi.fillna(100)

# RSI Buy/Sell Signals 
# Buy when RSI crosses below 30, Sell when RSI crosses above 70
rsi_signal = pd.Series(0, index=df.index)
in_position = False
for i in range(1, len(rsi)):
    if rsi.iloc[i] < 30 and rsi.iloc[i-1] >= 30 and not in_position:
        rsi_signal.iloc[i] = 1
        in_position = True
    elif rsi.iloc[i] > 70 and rsi.iloc[i-1] <= 70 and in_position:
        rsi_signal.iloc[i] = -1
        in_position = False

# Backtest Function
def backtest(signals, prices, initial_capital=1_000_000):
    capital = initial_capital
    shares = 0
    portfolio_values = []
    in_position = False

    for i in range(len(prices)):
        price = prices.iloc[i]
        sig = signals.iloc[i]

        if sig == 1 and not in_position:      # Buy signal
            shares = capital // price
            capital -= shares * price
            in_position = True
        elif sig == -1 and in_position:        # Sell signal
            capital += shares * price
            shares = 0
            in_position = False

        portfolio_values.append(capital + shares * price)

    # Close any open position at end
    if in_position:
        capital += shares * prices.iloc[-1]

    return pd.Series(portfolio_values, index=prices.index), capital

macd_portfolio, macd_final = backtest(macd_signal, df["Close"])
rsi_portfolio, rsi_final = backtest(rsi_signal, df["Close"])

# Print Results
print("\n---- Backtest Results (Initial: ₹10,00,000) ----")
print(f"MACD Strategy | Final: ₹{macd_final:,.0f} | Return: {(macd_final/1_000_000 - 1):.2%}")
print(f"RSI Strategy  | Final: ₹{rsi_final:,.0f} | Return: {(rsi_final/1_000_000 - 1):.2%}")

# Plot 
fig, axes = plt.subplots(4, 1, figsize=(14, 16),
                         gridspec_kw={"height_ratios": [3, 1.5, 1.5, 2]})
fig.suptitle("Kalyan Jewellers — Technical Analysis (Jan 2023 – Dec 2024)",
             fontsize=14, fontweight="bold")

# Panel 1: Price with buy/sell signals
ax1 = axes[0]
ax1.plot(df.index, df["Close"], color="black", linewidth=1, label="Close Price")
macd_buys  = df.index[macd_signal == 1]
macd_sells = df.index[macd_signal == -1]
rsi_buys   = df.index[rsi_signal == 1]
rsi_sells  = df.index[rsi_signal == -1]
ax1.scatter(macd_buys,  df["Close"][macd_buys],  marker="^", color="green",
            s=80, zorder=5, label="MACD Buy")
ax1.scatter(macd_sells, df["Close"][macd_sells], marker="v", color="red",
            s=80, zorder=5, label="MACD Sell")
ax1.scatter(rsi_buys,   df["Close"][rsi_buys],   marker="^", color="lime",
            s=80, zorder=5, label="RSI Buy", alpha=0.7)
ax1.scatter(rsi_sells,  df["Close"][rsi_sells],  marker="v", color="orange",
            s=80, zorder=5, label="RSI Sell", alpha=0.7)
ax1.set_ylabel("Price (₹)")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Panel 2: MACD
ax2 = axes[1]
ax2.plot(df.index, macd_line,   color="blue",   linewidth=1, label="MACD Line")
ax2.plot(df.index, signal_line, color="orange", linewidth=1, label="Signal Line")
ax2.bar(df.index, histogram, color=["green" if h >= 0 else "red" for h in histogram],
        alpha=0.4, label="Histogram")
ax2.axhline(0, color="black", linewidth=0.5)
ax2.set_ylabel("MACD")
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

# Panel 3: RSI
ax3 = axes[2]
ax3.plot(df.index, rsi, color="purple", linewidth=1, label="RSI (14)")
ax3.axhline(70, color="red",   linewidth=1, linestyle="--", label="Overbought (70)")
ax3.axhline(30, color="green", linewidth=1, linestyle="--", label="Oversold (30)")
ax3.fill_between(df.index, 70, rsi, where=(rsi >= 70), alpha=0.2, color="red")
ax3.fill_between(df.index, 30, rsi, where=(rsi <= 30), alpha=0.2, color="green")
ax3.set_ylim(0, 100)
ax3.set_ylabel("RSI")
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# Panel 4: Portfolio Value
ax4 = axes[3]
ax4.plot(df.index, macd_portfolio, color="blue",   linewidth=1.5, label=f"MACD (Final: ₹{macd_final:,.0f})")
ax4.plot(df.index, rsi_portfolio,  color="purple", linewidth=1.5, label=f"RSI  (Final: ₹{rsi_final:,.0f})")
ax4.axhline(1_000_000, color="gray", linewidth=1, linestyle="--", label="Initial: ₹10,00,000")
ax4.set_ylabel("Portfolio Value (₹)")
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig("technical_analysis.png", dpi=150)
print("\nChart saved as technical_analysis.png")