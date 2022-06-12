import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv('volatility_adjusted_mean_reversion.csv')


#Stop loss, which is the maximum amount of money a strategy is allowed to lose
num_days = len(results.index)
pnl = results['Pnl']

week_losses = []
monthly_losses = []

for i in range(0,num_days):
    if i>=5 and pnl[i-5] > pnl[i]:
        week_losses.append(pnl[i] - pnl[i-5])
    if i>=20 and pnl[i-20] > pnl[i]:
        monthly_losses.append (pnl[i] - pnl[i-20])

plt.hist(week_losses, 50)
plt.gca().set(title='Weekly Loss Distribution', xlabel='$', ylabel='Frequency')
plt.show()

plt.hist(monthly_losses, 50)
plt.gca().set(title='Monthly Loss Distribution', xlabel='$', ylabel='Frequency')
plt.show()

