import pandas as pd
import numpy as np
from pandas_datareader import data
import yfinance as yf
start_date = '2018-01-01'
end_date = '2023-01-01'
goog_data_frame = yf.download('GOOG', start = start_date, end = end_date)

goog_data_frame_signal = pd.DataFrame(index=goog_data_frame.index)
goog_data_frame_signal['price'] = goog_data_frame['Adj Close']

#calculates the support and resistance lines within moving time windows
#takes max and min price, and also substracting and adding the prices to get support and resistance
#buy order is sent when price is in the resistance line for more than 2 consecutive days, and opposite when price is in the support line for more than 2 consecutive days
def trading_support_resistance(data, bin_width=20):
    data['sup_tolerance'] = pd.Series(np.zeros(len(data)))
    data['res_tolerance'] = pd.Series(np.zeros(len(data)))
    data['sup_count'] = pd.Series(np.zeros(len(data)))
    data['res_count'] = pd.Series(np.zeros(len(data)))
    data['sup'] = pd.Series(np.zeros(len(data)))
    data['res'] = pd.Series(np.zeros(len(data)))
    data['positions'] = pd.Series(np.zeros(len(data)))
    data['signal'] = pd.Series(np.zeros(len(data)))
    in_support=0
    in_resistance=0
    for x in range((bin_width - 1) + bin_width, len(data)):
        data_section = data[x - bin_width:x + 1]
        support_level=min(data_section['price'])
        resistance_level=max(data_section['price'])
        range_level=resistance_level-support_level
        data['res'][x]=resistance_level
        data['sup'][x]=support_level
        data['sup_tolerance'][x]=support_level + 0.2 * range_level
        data['res_tolerance'][x]=resistance_level - 0.2 * range_level
        if data['price'][x]>=data['res_tolerance'][x] and\
                                    data['price'][x] <= data['res'][x]:
            in_resistance+=1
            data['res_count'][x]=in_resistance
        elif data['price'][x] <= data['sup_tolerance'][x] and \
                                    data['price'][x] >= data['sup'][x]:
            in_support += 1
            data['sup_count'][x] = in_support
        else:
            in_support=0
            in_resistance=0
        if in_resistance>2:
            data['signal'][x]=1
        elif in_support>2:
            data['signal'][x]=0
        else:
            data['signal'][x] = data['signal'][x-1]
    data['positions']=data['signal'].diff()
trading_support_resistance(goog_data_frame_signal)

import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Google price in $')
goog_data_frame_signal['sup'].plot(ax=ax1, color='g', lw=2.)
goog_data_frame_signal['res'].plot(ax=ax1, color='b', lw=2.)
goog_data_frame_signal['price'].plot(ax=ax1, color='r', lw=2.)
ax1.plot(goog_data_frame_signal.loc[goog_data_frame_signal.positions == 1.0].index,
       goog_data_frame_signal.price[goog_data_frame_signal.positions == 1.0],
       '^', markersize=7, color='k',label='buy')
ax1.plot(goog_data_frame_signal.loc[goog_data_frame_signal.positions == -1.0].index,
       goog_data_frame_signal.price[goog_data_frame_signal.positions == -1.0],
       'v', markersize=7, color='k',label='sell')
plt.legend()
plt.show()


