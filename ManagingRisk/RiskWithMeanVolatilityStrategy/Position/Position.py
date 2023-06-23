import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv('volatility_adjusted_mean_reversion_strategy_GOOG.csv')

num_days = len(results.index)

pnl = results['Pnl']

#Position holding - how long a position stays open in its state before it closes and returns to 
#flat or opposite position

position = results['Position']
plt.hist(position, 20)
plt.gca().set(title='Position Distribution', xlabel='Shares', ylabel='Frequency')
plt.show()

position_holding_times = []
current_pos = 0
current_pos_start = 0
for i in range(0, num_days):
  pos = results['Position'].iloc[i]

  # flat and starting a new position
  if current_pos == 0:
    if pos != 0:
      current_pos = pos
      current_pos_start = i
    continue

  # going from long position to flat or short position or
  # going from short position to flat or long position
  if current_pos * pos <= 0:
    current_pos = pos
    position_holding_times.append(i - current_pos_start)
    current_pos_start = i

print(position_holding_times)
plt.hist(position_holding_times, 100)
plt.gca().set(title='Position Holding Time Distribution', xlabel='Holding time days', ylabel='Frequency')
plt.show()
