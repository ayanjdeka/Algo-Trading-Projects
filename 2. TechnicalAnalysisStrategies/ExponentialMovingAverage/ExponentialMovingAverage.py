import pandas as pd

from pandas_datareader import data

start_date = '2017-01-01'
end_date = '2020-01-01'
SRC_DATA_FILENAME = 'goog_data.pkl'



goog_data = data.DataReader('MSFT', 'yahoo', start_date, end_date)

close = goog_data['Close']

num_periods = 20 # number of days over which to average
K = 2 / (num_periods + 1) # smoothing constant
ema_p = 0

ema_values = [] # to hold computed EMA values
for close_price in close:
  if (ema_p == 0): 
    ema_p = close_price
  else:
    ema_p = (close_price - ema_p) * K + ema_p

  ema_values.append(ema_p)

goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
goog_data = goog_data.assign(Exponential20DayMovingAverage=pd.Series(ema_values, index=goog_data.index))

close_price = goog_data['ClosePrice']
ema = goog_data['Exponential20DayMovingAverage']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='MSFT price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema.plot(ax=ax1, color='b', lw=2., legend=True)
plt.show()

#similar to simple moving average, but reduces the noise in the raw prices
#allows us to control the relative weight placed on new prices (for fast and slow)

