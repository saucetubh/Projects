import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Downloading historical data for Reliance Industries (NSE)

ticker = "RELIANCE.NS"
data = yf.download(ticker, start="2020-01-01", end="2024-12-31")

print(data.head(10))

# We only need the closing price
close = data["Close"]

# Calculate daily returns — how much did the stock go up or down each day in %
daily_returns = close.pct_change()

print(daily_returns.head(10))

#strategy - moving average

# Calculate 20-day and 50-day moving averages
close = close.squeeze()
daily_returns = daily_returns.squeeze()

ma20 = close.rolling(window=20).mean()
ma50 = close.rolling(window=50).mean()

# Generate signal: 1 means "buy/hold", 0 means "stay out"
# We buy when the 20-day average is above the 50-day average (uptrend)
signal = (ma20 > ma50).astype(int)

print(signal.value_counts())

# output was 1 627 and 0 610, meaning the strategy was in a "buy/hold" position for 627 days and "stay out" for 610 days. NOT CONSECUTIVE DAYS, just the total count of days in each state.

# Strategy returns: only earn the market return on days we have signal=1
# On days signal=0 we are out of the market, so we earn 0
strategy_returns = daily_returns * signal.shift(1)
# Note: we shift signal by 1 day because we can only act on yesterday's signal today

# Cumulative returns: how ₹1 invested would have grown over time
cumulative_market = (1 + daily_returns).cumprod()
cumulative_strategy = (1 + strategy_returns).cumprod()

print("Buy and Hold final return:", round(cumulative_market.iloc[-1].item() - 1, 4)) #if u just bought Reliance in Jan 2020 and held till Dec 2024
print("Momentum Strategy final return:", round(cumulative_strategy.iloc[-1].item() - 1, 4))

plt.figure(figsize=(12, 6))
plt.plot(cumulative_market.index, cumulative_market.values, label="Buy & Hold", color="blue")
plt.plot(cumulative_strategy.index, cumulative_strategy.values, label="Momentum Strategy", color="orange")
plt.title("Reliance Industries: Momentum Strategy vs Buy & Hold")
plt.xlabel("Date")
plt.ylabel("Growth of ₹1")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("results.png")
print("Chart saved as results.png")

# Annualised return
days = len(daily_returns.dropna())
ann_market = cumulative_market.iloc[-1].item() ** (252/days) - 1
ann_strategy = cumulative_strategy.iloc[-1].item() ** (252/days) - 1

# Sharpe Ratio: return per unit of risk (higher is better, >1 is good)
sharpe_market = (daily_returns.mean() / daily_returns.std()).item() * (252**0.5)
sharpe_strategy = (strategy_returns.mean() / strategy_returns.std()).item() * (252**0.5)

# Maximum Drawdown: worst peak-to-trough drop
def max_drawdown(cum_returns):
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    return drawdown.min().item()

print("\n---- Performance Summary ----")
print(f"Annualised Return  |  Market: {ann_market:.2%}  |  Strategy: {ann_strategy:.2%}")
print(f"Sharpe Ratio       |  Market: {sharpe_market:.2f}  |  Strategy: {sharpe_strategy:.2f}")
print(f"Max Drawdown       |  Market: {max_drawdown(cumulative_market):.2%}  |  Strategy: {max_drawdown(cumulative_strategy):.2%}")