import pandas as pd

from pandas_datareader import data

import yfinance as yf
start_date = '2018-01-01'
end_date = '2023-01-01'
msft_data_frame = yf.download('MSFT', start = start_date, end = end_date)

close = msft_data_frame['Close']

time_period = 20 
history = [] 
mom_values = []

for close_price in close:
  history.append(close_price)
  if len(history) > time_period: 
    del (history[0])

  mom = close_price - history[0]
  mom_values.append(mom)

msft_data_frame = msft_data_frame.assign(ClosePrice=pd.Series(close, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(MomentumFromPrice20DaysAgo=pd.Series(mom_values, index=msft_data_frame.index))

close_price = msft_data_frame['ClosePrice']
mom = msft_data_frame['MomentumFromPrice20DaysAgo']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(211, ylabel='MSFT price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ax2 = fig.add_subplot(212, ylabel='Momentum in $')
mom.plot(ax=ax2, color='b', lw=2., legend=True)
plt.show()
