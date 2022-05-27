import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv('volatility_adjusted_mean_reversion.csv')

num_days = len(results.index)

pnl = results['Pnl']

#Variance of PNLs- measure how much PNL varies each week, if they are big
#then the market is very volatile

last_week = 0
weekly_pnls = []
weekly_losses = []
for i in range(0, num_days):
  if i - last_week >= 5:
    pnl_change = pnl[i] - pnl[last_week]
    weekly_pnls.append(pnl_change)
    if pnl_change < 0:
      weekly_losses.append(pnl_change)
    last_week = i

from statistics import stdev, mean
print('PnL Standard Deviation:', stdev(weekly_pnls))

plt.hist(weekly_pnls, 50)
plt.gca().set(title='Weekly PnL Distribution', xlabel='$', ylabel='Frequency')
plt.show()

#measures the performance of these strategies
sharpe_ratio = mean(weekly_pnls) / stdev(weekly_pnls)
sortino_ratio = mean(weekly_pnls) / stdev(weekly_losses)

print('Sharpe ratio:', sharpe_ratio)
print('Sortino ratio:', sortino_ratio)
