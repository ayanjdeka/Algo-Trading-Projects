import pandas as pd

from pandas_datareader import data

import yfinance as yf
start_date = '2018-01-01'
end_date = '2023-01-01'
msft_data_frame = yf.download('MSFT', start = start_date, end = end_date)

close = msft_data_frame['Close']

import statistics as stats
time_period = 20 # number of days over which to average
history = [] # to track a history of prices
sma_values = [] # to track simple moving average values
for close_price in close:
  history.append(close_price)
  if len(history) > time_period: # we remove oldest price because we only average over last 'time_period' prices
    del (history[0])

  sma_values.append(stats.mean(history))

msft_data_frame = msft_data_frame.assign(ClosePrice=pd.Series(close, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(Simple20DayMovingAverage=pd.Series(sma_values, index=msft_data_frame.index))

close_price = msft_data_frame['ClosePrice']
sma = msft_data_frame['Simple20DayMovingAverage']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='MSFT price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
sma.plot(ax=ax1, color='r', lw=2., legend=True)
plt.show()


