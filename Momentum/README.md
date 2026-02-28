# Momentum Trading Strategy — Backtest on Reliance Industries (NSE)

A quantitative backtest comparing SMA and EMA-based momentum strategies
against a Buy & Hold benchmark on Reliance Industries (RELIANCE.NS) from 2020–2024.

## Strategy Logic
- Generate a buy signal when the short-term moving average (20-day) crosses 
  above the long-term moving average (50-day)
- Stay out of the market when the short-term average is below the long-term average
- Compare Simple Moving Average (SMA) vs Exponential Moving Average (EMA) signals

## Results

| Strategy   | Annualised Return | Sharpe Ratio | Max Drawdown |
|------------|-------------------|--------------|--------------|
| Buy & Hold | 12.55%            | 0.55         | -44.08%      |
| SMA        | 5.17%             | 0.37         | -41.78%      |
| EMA        | 6.91%             | 0.44         | -25.72%      |

## Key Finding
EMA outperforms SMA on every metric. While neither momentum strategy beats 
Buy & Hold on raw returns, EMA significantly reduces maximum drawdown 
(-25.72% vs -44.08%), demonstrating superior risk-adjusted performance.
