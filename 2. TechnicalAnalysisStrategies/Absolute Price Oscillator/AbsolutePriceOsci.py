import pandas as pd

from pandas_datareader import data

start_date = '2017-01-01'
end_date = '2020-01-01'
SRC_DATA_FILENAME = 'goog_data.pkl'



goog_data = data.DataReader('MSFT', 'yahoo', start_date, end_date)

close = goog_data['Close']

#purpose of the absolute price oscillator is to compute the difference between EMAslow and EMAfast
#large difference can mean instruments are trending or breaking out, or prices are far away from the equillibrium prices

num_periods_fast = 10
K_fast = 2 / (num_periods_fast+1)
ema_fast = 0
ema_fast_values = []

num_periods_slow = 40
K_slow = 2 / (num_periods_slow+1)
ema_slow = 0
ema_slow_values = []

apo_values = []

for price in close:
    if(ema_fast == 0):
        ema_fast = price
        ema_slow = price
    else:
        ema_fast = (price - ema_fast) * K_fast + ema_fast
        ema_slow = (price - ema_slow) * K_slow + ema_slow 
    
    ema_fast_values.append(ema_fast)
    ema_slow_values.append(ema_slow)

    apo_values.append(ema_fast-ema_slow)


#magnitude of the apo values show the severity of the breakout

goog_data = goog_data.assign(ClosePrice=pd.Series(close, index=goog_data.index))
goog_data = goog_data.assign(FastExponential10DayMovingAverage=pd.Series(ema_fast_values, index=goog_data.index))
goog_data = goog_data.assign(SlowExponential40DayMovingAverage=pd.Series(ema_slow_values, index=goog_data.index))
goog_data = goog_data.assign(AbsolutePriceOscillator=pd.Series(apo_values, index=goog_data.index))

close_price = goog_data['ClosePrice']
ema_f = goog_data['FastExponential10DayMovingAverage']
ema_s = goog_data['SlowExponential40DayMovingAverage']
apo = goog_data['AbsolutePriceOscillator']

import matplotlib.pyplot as plt

fig = plt.figure()
ax1 = fig.add_subplot(211, ylabel='Microsoft price in $')
close_price.plot(ax=ax1, color='g', lw=2., legend=True)
ema_f.plot(ax=ax1, color='b', lw=2., legend=True)
ema_s.plot(ax=ax1, color='r', lw=2., legend=True)
ax2 = fig.add_subplot(212, ylabel='APO')
apo.plot(ax=ax2, color='black', lw=2., legend=True)
plt.show()



