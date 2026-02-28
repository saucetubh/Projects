import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Load Data
prices = pd.read_excel("data.xlsx")
prices.columns = ["DR REDDY", "NTPC", "PERSISTENT", "BAJAJ AUTO", "KOTAK BANK", "CHAINLINK", "CRUDE OIL"]

# Calculate Daily Returns
returns = prices.pct_change().dropna()

# Annualised Mean Returns and Covariance Matrix
mean_returns = returns.mean() * 252
cov_matrix = returns.cov() * 252
rf = 0.0669  # Risk free rate: 10-year Indian govt bond yield

# Portfolio Performance Function 
def portfolio_performance(weights, mean_returns, cov_matrix):
    ret = np.dot(weights, mean_returns)
    risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe = (ret - rf) / risk
    return ret, risk, sharpe

# Simulate 5000 Random Portfolios
n_assets = len(prices.columns)
n_portfolios = 5000

all_returns = []
all_risks = []
all_sharpes = []
all_weights = []

np.random.seed(42)
for _ in range(n_portfolios):
    w = np.random.random(n_assets)
    w = w / w.sum()  # Normalise so weights sum to 1
    ret, risk, sharpe = portfolio_performance(w, mean_returns, cov_matrix)
    all_returns.append(ret)
    all_risks.append(risk)
    all_sharpes.append(sharpe)
    all_weights.append(w)

all_returns = np.array(all_returns)
all_risks = np.array(all_risks)
all_sharpes = np.array(all_sharpes)

# Find Minimum Variance Portfolio
def neg_sharpe(weights):
    return -portfolio_performance(weights, mean_returns, cov_matrix)[2]

def portfolio_risk(weights):
    return portfolio_performance(weights, mean_returns, cov_matrix)[1]

constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
bounds = tuple((0, 1) for _ in range(n_assets))
init_weights = np.ones(n_assets) / n_assets

mvp_result = minimize(portfolio_risk, init_weights, method="SLSQP",
                      bounds=bounds, constraints=constraints)
mvp_weights = mvp_result.x
mvp_ret, mvp_risk, mvp_sharpe = portfolio_performance(mvp_weights, mean_returns, cov_matrix)

# Find Tangency Portfolio (Max Sharpe)
tangency_result = minimize(neg_sharpe, init_weights, method="SLSQP",
                           bounds=bounds, constraints=constraints)
tan_weights = tangency_result.x
tan_ret, tan_risk, tan_sharpe = portfolio_performance(tan_weights, mean_returns, cov_matrix)

# Capital Allocation Line 
cal_x = np.linspace(0, max(all_risks) * 1.2, 100)
cal_y = rf + tan_sharpe * cal_x

# Print Results 
assets = prices.columns.tolist()

print("\n---- Individual Asset Stats ----")
for asset in assets:
    print(f"{asset:<20} | Return: {mean_returns[asset]:.2%} | Risk: {np.sqrt(cov_matrix.loc[asset,asset]):.2%}")

print("\n---- Minimum Variance Portfolio ----")
for i, asset in enumerate(assets):
    print(f"  {asset:<20}: {mvp_weights[i]:.2%}")
print(f"  Return: {mvp_ret:.2%} | Risk: {mvp_risk:.2%} | Sharpe: {mvp_sharpe:.2f}")

print("\n---- Tangency Portfolio (Max Sharpe) ----")
for i, asset in enumerate(assets):
    print(f"  {asset:<20}: {tan_weights[i]:.2%}")
print(f"  Return: {tan_ret:.2%} | Risk: {tan_risk:.2%} | Sharpe: {tan_sharpe:.2f}")

# Plot Efficient Frontier
plt.figure(figsize=(12, 7))

# Scatter of all simulated portfolios coloured by Sharpe ratio
scatter = plt.scatter(all_risks, all_returns, c=all_sharpes,
                      cmap="viridis", alpha=0.5, s=10)
plt.colorbar(scatter, label="Sharpe Ratio")

# Capital Allocation Line
plt.plot(cal_x, cal_y, color="red", linewidth=2, label="Capital Allocation Line")

# Minimum Variance Portfolio
plt.scatter(mvp_risk, mvp_ret, color="blue", s=200, zorder=5,
            marker="*", label=f"Min Variance (Sharpe: {mvp_sharpe:.2f})")

# Tangency Portfolio
plt.scatter(tan_risk, tan_ret, color="orange", s=200, zorder=5,
            marker="*", label=f"Tangency Portfolio (Sharpe: {tan_sharpe:.2f})")

# Risk-free rate point
plt.scatter(0, rf, color="red", s=100, zorder=5, marker="o", label=f"Risk-Free Rate ({rf:.2%})")

plt.title("Markowitz Efficient Frontier — 7 Asset Portfolio")
plt.xlabel("Portfolio Risk (Standard Deviation)")
plt.ylabel("Portfolio Return")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("efficient_frontier.png")
print("\nChart saved as efficient_frontier.png")