
import pandas as pd
import numpy as np
from pandas_datareader import data
import matplotlib.pyplot as plt
import yfinance as yf

def load_financial_data(symbol, start_date, end_date,output_file):
    

    df = yf.download(symbol, start = start_date, end = end_date)
    df.to_pickle(output_file)
    return df

data=load_financial_data('GOOG',start_date='2018-01-01',
                    end_date = '2023-01-01',
                    output_file='multi_data_large.pkl')

def turtle_trading(financial_data, window_size):
    signals = pd.DataFrame(index = financial_data.index)
    signals['orders'] = 0
    signals['high'] = financial_data['Adj Close'].shift(1).\
        rolling(window = window_size).max()
    signals['low'] = financial_data['Adj Close'].shift(1).\
        rolling(window = window_size).min()
    signals['avg'] = financial_data['Adj Close'].shift(1).\
        rolling(window = window_size).mean()

    #entry rule
    signals['long_entry'] = financial_data['Adj Close'] > signals.high
    signals['short_entry'] = financial_data['Adj Close'] < signals.low

    signals['long_exit'] = financial_data['Adj Close'] < signals.avg
    signals['short_exit'] = financial_data['Adj Close'] > signals.avg

    init = True
    position = 0

    for k in range(len(signals)):
        if signals['long_entry'][k] and position==0:
            signals.orders.values[k] = 1
            position=1
        elif signals['short_entry'][k] and position==0:
            signals.orders.values[k] = -1
            position=-1
        elif signals['short_exit'][k] and position>0:
            signals.orders.values[k] = -1
            position = 0
        elif signals['long_exit'][k] and position < 0:
            signals.orders.values[k] = 1
            position = 0
        else:
            signals.orders.values[k] = 0

    return signals

ts=turtle_trading(data, 50)

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='Google price in $')
data["Adj Close"].plot(ax=ax1, color='g', lw=.5)
ts["high"].plot(ax=ax1, color='g', lw=.5)
ts["low"].plot(ax=ax1, color='r', lw=.5)
ts["avg"].plot(ax=ax1, color='b', lw=.5)

ax1.plot(ts.loc[ts.orders == 1.0].index,
data["Adj Close"][ts.orders == 1.0],
'^', markersize = 7, color = 'k')

ax1.plot(ts.loc[ts.orders == -1.0].index,
data["Adj Close"][ts.orders == -1.0],
'v', markersize = 7, color = 'k')

plt.legend(["Price","Highs","Lows","Average","Buy","Sell"])
plt.title("Turtle Trading Strategy")

plt.show()


