import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Download Data
ticker = "RELIANCE.NS"
data = yf.download(ticker, start="2020-01-01", end="2024-12-31")
close = data["Close"].squeeze()
daily_returns = close.pct_change().squeeze()

#SMA Strategy
ma20_sma = close.rolling(window=20).mean()
ma50_sma = close.rolling(window=50).mean()
signal_sma = (ma20_sma > ma50_sma).astype(int)
returns_sma = daily_returns * signal_sma.shift(1)

#EMA Strategy
ma20_ema = close.ewm(span=20, adjust=False).mean()
ma50_ema = close.ewm(span=50, adjust=False).mean()
signal_ema = (ma20_ema > ma50_ema).astype(int)
returns_ema = daily_returns * signal_ema.shift(1)

#Cumulative Returns
cum_market   = (1 + daily_returns).cumprod()
cum_sma      = (1 + returns_sma).cumprod()
cum_ema      = (1 + returns_ema).cumprod()

#Performance Metrics
def performance(returns, cum_returns, label):
    days = len(returns.dropna())
    ann_return = cum_returns.iloc[-1].item() ** (252 / days) - 1
    sharpe = (returns.mean() / returns.std()).item() * (252 ** 0.5)
    peak = cum_returns.cummax()
    max_dd = ((cum_returns - peak) / peak).min().item()
    print(f"{label:<20} | Annualised Return: {ann_return:>7.2%} | Sharpe: {sharpe:.2f} | Max Drawdown: {max_dd:.2%}")

print("\n---- Performance Summary ----")
performance(daily_returns, cum_market, "Buy & Hold")
performance(returns_sma,   cum_sma,   "SMA Strategy")
performance(returns_ema,   cum_ema,   "EMA Strategy")

#Plot
plt.figure(figsize=(12, 6))
plt.plot(cum_market.index, cum_market.values, label="Buy & Hold",    color="blue")
plt.plot(cum_sma.index,    cum_sma.values,    label="SMA Strategy",  color="orange")
plt.plot(cum_ema.index,    cum_ema.values,    label="EMA Strategy",  color="green")
plt.title("Reliance Industries: SMA vs EMA vs Buy & Hold")
plt.xlabel("Date")
plt.ylabel("Growth of ₹1")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("comparison.png")
print("\nChart saved as comparison.png")