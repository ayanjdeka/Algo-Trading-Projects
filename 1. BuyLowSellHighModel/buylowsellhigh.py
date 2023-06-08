from pandas_datareader import data
import yfinance as yf
start_date = '2020-01-01'
end_date = '2023-05-01'
goog_data_frame = yf.download('GOOG', start = start_date, end = end_date)

import numpy as np
import pandas as pd

#calculate between the prices of the previous day and the current day
#if the price is lower today, then we buy, and sell if opposite

goog_data_frame_signal = pd.DataFrame(index=goog_data_frame.index)
goog_data_frame_signal['price'] = goog_data_frame['Adj Close']
goog_data_frame_signal['daily_difference'] = goog_data_frame_signal['price'].diff()
goog_data_frame_signal['signal'] = 0.0
goog_data_frame_signal['signal'][:] = np.where(goog_data_frame_signal['daily_difference'][:] > 0, 1.0, 0.0)

goog_data_frame_signal['positions'] = goog_data_frame_signal['signal'].diff()

import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Google price in $')
goog_data_frame_signal['price'].plot(ax=ax1, color='r', lw=2.)

ax1.plot(goog_data_frame_signal.loc[goog_data_frame_signal.positions == 1.0].index,
         goog_data_frame_signal.price[goog_data_frame_signal.positions == 1.0],
         '^', markersize=5, color='m')

ax1.plot(goog_data_frame_signal.loc[goog_data_frame_signal.positions == -1.0].index,
         goog_data_frame_signal.price[goog_data_frame_signal.positions == -1.0],
         'v', markersize=5, color='k')

#plt.show()


# Set the initial capital
initial_capital= float(1000.0)

positions = pd.DataFrame(index=goog_data_frame_signal.index).fillna(0.0)
portfolio = pd.DataFrame(index=goog_data_frame_signal.index).fillna(0.0)

#backtesting with the initial capital

#store the google positions in the data frame
positions['GOOG'] = goog_data_frame_signal['signal']

#store the amount of google positions we get
portfolio['positions'] = (positions.multiply(goog_data_frame_signal['price'], axis=0))

#calculate the non invested money
portfolio['cash'] = initial_capital - (positions.diff().multiply(goog_data_frame_signal['price'], axis=0)).cumsum()

#calculate the total investment
portfolio['total'] = portfolio['positions'] + portfolio['cash']
portfolio.plot()
plt.show()


fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Portfolio value in $')
portfolio['total'].plot(ax=ax1, lw=2.)
ax1.plot(portfolio.loc[goog_data_frame_signal.positions == 1.0].index,portfolio.total[goog_data_frame_signal.positions == 1.0],'^', markersize=10, color='m')
ax1.plot(portfolio.loc[goog_data_frame_signal.positions == -1.0].index,portfolio.total[goog_data_frame_signal.positions == -1.0],'v', markersize=10, color='k')
plt.show()