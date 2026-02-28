# Markowitz Efficient Frontier — 7 Asset Portfolio

An implementation of **Harry Markowitz's Modern Portfolio Theory** to construct an optimal portfolio across 7 assets spanning equities, crypto, and commodities.

## Assets

| # | Asset |
|---|-------|
| 1 | Dr Reddy's Laboratories |
| 2 | NTPC |
| 3 | Persistent Systems |
| 4 | Bajaj Auto |
| 5 | Kotak Mahindra Bank |
| 6 | Chainlink (LINK) |
| 7 | Crude Oil |

## What It Does

1. **Loads historical price data** from `data.xlsx`.
2. **Computes annualised returns and covariance matrix** from daily returns.
3. **Simulates 5 000 random portfolios** to map the risk–return space.
4. **Finds the Minimum Variance Portfolio** — lowest possible risk for a long-only portfolio.
5. **Finds the Tangency Portfolio** — maximum Sharpe ratio (best risk-adjusted return).
6. **Plots the Efficient Frontier** with the Capital Allocation Line and saves it as `efficient_frontier.png`.

## Output

- Console printout of individual asset stats, MVP weights, and tangency portfolio weights.
- A chart (`efficient_frontier.png`) showing:
  - Simulated portfolios coloured by Sharpe ratio
  - Minimum Variance Portfolio (blue star)
  - Tangency Portfolio (orange star)
  - Capital Allocation Line (red)
  - Risk-free rate point

## Assumptions

| Parameter | Value |
|-----------|-------|
| Risk-free rate | 6.69 % (10-year Indian govt bond yield) |
| Return frequency | Daily → annualised (×252) |
| Short selling | Not allowed (weights ∈ [0, 1]) |

## Requirements

```
pandas
numpy
matplotlib
scipy
openpyxl
```

Install with:

```bash
pip install pandas numpy matplotlib scipy openpyxl
```
