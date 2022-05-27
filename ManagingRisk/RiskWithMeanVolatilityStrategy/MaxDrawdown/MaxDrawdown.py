import pandas as pd
import matplotlib.pyplot as plt


#Maximum amount of losses over a series of days
results = pd.read_csv('volatility_adjusted_mean_reversion.csv')

num_days = len(results.index)

pnl = results["Pnl"]

max_pnl = 0
max_drawdown = 0
drawdown_max_pnl = 0
drawdown_min_pnl = 0

for i in range(0, num_days):
  max_pnl = max(max_pnl, pnl[i])
  drawdown = max_pnl - pnl[i]

  if drawdown > max_drawdown:
    max_drawdown = drawdown
    drawdown_max_pnl = max_pnl
    drawdown_min_pnl = pnl[i]

print('Max Drawdown:', max_drawdown)

results['Pnl'].plot(x='Date', legend=True)
plt.axhline(y=drawdown_max_pnl, color='g')
plt.axhline(y=drawdown_min_pnl, color='r')
plt.show()

