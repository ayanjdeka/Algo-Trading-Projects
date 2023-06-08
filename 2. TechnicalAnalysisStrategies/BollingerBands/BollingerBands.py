import pandas as pd

from pandas_datareader import data

import yfinance as yf
start_date = '2018-01-01'
end_date = '2023-01-01'
msft_data_frame = yf.download('MSFT', start = start_date, end = end_date)

close = msft_data_frame['Close']

'''
Bollinger Bands incorporate recent price volatality that makes it more 
adaptive to different market conditions. Bands represent the expected 
volatility of the prices by treating the moving average of the price as 
the reference price.

'''

import statistics as stats
import math as math

time_period = 20
stdev_factor = 2
history = []
sma_values = []
upper_band = []
lower_band = []

for close_price in close:
    history.append(close_price)
    if len(history) > time_period:
        del(history[0])

    sma = stats.mean(history)
    sma_values.append(sma)
    variance = 0
    for hist_price in history:
        variance = variance + ((hist_price - sma) ** 2)

    stdev = math.sqrt(variance / len(history))

    upper_band.append(sma + stdev_factor * stdev)
    lower_band.append(sma - stdev_factor * stdev)

msft_data_frame = msft_data_frame.assign(ClosePrice=pd.Series(close, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(MiddleBollingerBand20DaySMA=pd.Series(sma_values, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(UpperBollingerBand20DaySMA2StdevFactor=pd.Series(upper_band, index=msft_data_frame.index))
msft_data_frame = msft_data_frame.assign(LowerBollingerBand20DaySMA2StdevFactor=pd.Series(lower_band, index=msft_data_frame.index))

close_price = msft_data_frame['ClosePrice']
mband = msft_data_frame['MiddleBollingerBand20DaySMA']
uband = msft_data_frame['UpperBollingerBand20DaySMA2StdevFactor']
lband = msft_data_frame['LowerBollingerBand20DaySMA2StdevFactor']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel='MSFT price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
mband.plot(ax=ax1, color='b', lw=2., legend=True)
uband.plot(ax=ax1, color='g', lw=2., legend=True)
lband.plot(ax=ax1, color='r', lw=2., legend=True)
plt.show()


'''
When prices traverse the upper band, it can break out to the upside,
or it can bounce down. When they traverse the lower band, it can break out
to the downside, or it can bounce up. 

'''
