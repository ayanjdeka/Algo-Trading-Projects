import pandas as pd

from pandas_datareader import data
import yfinance as yf

start_date = '2018-01-01'
end_date = '2023-05-01'
SRC_DATA_FILENAME = 'msft_data_frame.pkl'



msft_data_frame = yf.download('MSFT', start = start_date, end = end_date)

close = msft_data_frame['Close']
num_periods_fast = 10 # fast EMA time period
K_fast = 2 / (num_periods_fast + 1) # fast EMA smoothing factor
ema_fast = 0
num_periods_slow = 40 # slow EMA time period
K_slow = 2 / (num_periods_slow + 1) # slow EMA smoothing factor
ema_slow = 0
num_periods_macd = 20 # MACD EMA time period
K_macd = 2 / (num_periods_macd + 1) # MACD EMA smoothing factor
ema_macd = 0

ema_fast_values = [] 
ema_slow_values = [] 
macd_values = [] 
macd_signal_values = [] 
macd_historgram_values = [] 
for close_price in close:
  if (ema_fast == 0): # first observation
    ema_fast = close_price
    ema_slow = close_price
  else:
    ema_fast = (close_price - ema_fast) * K_fast + ema_fast
    ema_slow = (close_price - ema_slow) * K_slow + ema_slow

  ema_fast_values.append(ema_fast)
  ema_slow_values.append(ema_slow)

  macd = ema_fast - ema_slow # MACD is fast_MA - slow_EMA
  if ema_macd == 0:
    ema_macd = macd
  else:
    ema_macd = (macd - ema_macd) * K_slow + ema_macd # signal is EMA of MACD values

  macd_values.append(macd)
  macd_signal_values.append(ema_macd)
  macd_historgram_values.append(macd - ema_macd)

msft_data_frame = msft_data_frame.assign(ClosePrice=pd.Series(close, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(MovingAverageConvergenceDivergence=pd.Series(macd_values, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(Exponential20DayMovingAverageOfMACD=pd.Series(macd_signal_values, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(MACDHistorgram=pd.Series(macd_historgram_values, index=msft_data_frame.index))

close_price = msft_data_frame['ClosePrice']
ema_f = msft_data_frame['FastExponential10DayMovingAverage']
ema_s = msft_data_frame['SlowExponential40DayMovingAverage']
macd = msft_data_frame['MovingAverageConvergenceDivergence']
ema_macd = msft_data_frame['Exponential20DayMovingAverageOfMACD']
macd_histogram = msft_data_frame['MACDHistorgram']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(311, ylabel='MSFT price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema_f.plot(ax=ax1, color='b', lw=2., legend=True)
ema_s.plot(ax=ax1, color='r', lw=2., legend=True)
ax2 = fig.add_subplot(312, ylabel='MACD')
macd.plot(ax=ax2, color='black', lw=2., legend=True)
ema_macd.plot(ax=ax2, color='g', lw=2., legend=True)
ax3 = fig.add_subplot(313, ylabel='MACD')
macd_histogram.plot(ax=ax3, color='r', kind='bar', legend=True, use_index=False)
plt.show()