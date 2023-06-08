import pandas as pd

from pandas_datareader import data

import yfinance as yf
start_date = '2018-01-01'
end_date = '2023-01-01'
msft_data_frame = yf.download('MSFT', start = start_date, end = end_date)

close = msft_data_frame['Close']

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

msft_data_frame = msft_data_frame.assign(ClosePrice=pd.Series(close, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(Exponential20DayMovingAverage=pd.Series(ema_values, index=msft_data_frame.index))

close_price = msft_data_frame['ClosePrice']
ema = msft_data_frame['Exponential20DayMovingAverage']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='MSFT price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema.plot(ax=ax1, color='b', lw=2., legend=True)
plt.show()

#similar to simple moving average, but reduces the noise in the raw prices
#allows us to control the relative weight placed on new prices (for fast and slow)

