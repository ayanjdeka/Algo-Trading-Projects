import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv('volatility_adjusted_mean_reversion_strategy_GOOG.csv')

num_days = len(results.index)

pnl = results['Pnl']


#Maximum Executions - Makes sure the strategy does not over trade within a time period

executions_this_week = 0
executions_per_week = []
last_week = 0
for i in range(0, num_days):
  if results['Trades'].iloc[i] != 0:
    executions_this_week += 1

  if i - last_week >= 5:
    executions_per_week.append(executions_this_week)
    executions_this_week = 0
    last_week = i

plt.hist(executions_per_week, 10)
plt.gca().set(title='Weekly number of executions Distribution', xlabel='Number of executions', ylabel='Frequency')
plt.show()

executions_this_month = 0
executions_per_month = []
last_month = 0
for i in range(0, num_days):
  if results['Trades'].iloc[i] != 0:
    executions_this_month += 1

  if i - last_month >= 20:
    executions_per_month.append(executions_this_month)
    executions_this_month = 0
    last_month = i

plt.hist(executions_per_month, 20)
plt.gca().set(title='Monthly number of executions Distribution', xlabel='Number of executions', ylabel='Frequency')
plt.show()