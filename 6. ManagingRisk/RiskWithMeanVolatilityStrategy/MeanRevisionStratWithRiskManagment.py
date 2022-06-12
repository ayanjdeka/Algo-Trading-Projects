import pandas as pd
from pandas_datareader import data

SYMBOL = 'GOOG'
start_date = '2014-01-01'
end_date = '2018-01-01'
SRC_DATA_FILENAME = SYMBOL + '_data.pkl'

try:
  data = pd.read_pickle(SRC_DATA_FILENAME)
except FileNotFoundError:
  data = data.DataReader(SYMBOL, 'yahoo', start_date, end_date)
  data.to_pickle(SRC_DATA_FILENAME)

NUM_PERIODS_FAST = 10 
K_FAST = 2 / (NUM_PERIODS_FAST + 1)  
ema_fast = 0
ema_fast_values = []  

NUM_PERIODS_SLOW = 40  
K_SLOW = 2 / (NUM_PERIODS_SLOW + 1)  
ema_slow = 0
ema_slow_values = []  

apo_values = [] 

orders = []  
positions = []  
pnls = []  

last_buy_price = 0 
last_sell_price = 0 
position = 0 
buy_sum_price_qty = 0 
buy_sum_qty = 0 
sell_sum_price_qty = 0 
sell_sum_qty = 0
open_pnl = 0 
closed_pnl = 0 


# Constants that define strategy behavior/thresholds
APO_VALUE_FOR_BUY_ENTRY = -10  # APO trading signal value below which to enter buy-orders/long-position
APO_VALUE_FOR_SELL_ENTRY = 10  # APO trading signal value above which to enter sell-orders/short-position
MIN_PRICE_MOVE_FROM_LAST_TRADE = 10  # Minimum price change since last trade before considering trading again, this is to prevent over-trading at/around same prices

MIN_NUM_SHARES_PER_TRADE = 1
MAX_NUM_SHARES_PER_TRADE = 50
INCREMENT_NUM_SHARES_PER_TRADE = 2
num_shares_per_trade = MIN_NUM_SHARES_PER_TRADE
num_shares_history = []
abs_position_history = []

import statistics as stats
import math as math

SMA_NUM_PERIODS = 20  
price_history = []  

risk_limit_weekly_stop_loss = -6000
INCREMENT_RISK_LIMIT_WEEKLY_STOP_LOSS = -12000
risk_limit_monthly_stop_loss = -15000
INCREMENT_RISK_LIMIT_MONTHLY_STOP_LOSS = -30000

risk_limit_max_position = 5
INCREMENT_RISK_LIMIT_MAX_POSITION = 3
max_position_history = [] 
RISK_LIMIT_MAX_POSITION_HOLDING_TIME_DAYS = 120 * 5

risk_limit_max_trade_size = 5
INCREMENT_RISK_LIMIT_MAX_TRADE_SIZE = 2
max_trade_size_history = [] 


risk_violated = False

traded_volume = 0
current_pos = 0
current_pos_start = 0
last_risk_change_index = 0

close = data['Close']
for close_price in close:
  price_history.append(close_price)
  if len(price_history) > SMA_NUM_PERIODS:  
    del (price_history[0])

  sma = stats.mean(price_history)
  variance = 0 
  for hist_price in price_history:
    variance = variance + ((hist_price - sma) ** 2)

  stdev = math.sqrt(variance / len(price_history))
  stdev_factor = stdev / 15
  if stdev_factor == 0:
    stdev_factor = 1

  
  if (ema_fast == 0):  
    ema_fast = close_price
    ema_slow = close_price
  else:
    ema_fast = (close_price - ema_fast) * K_FAST * stdev_factor + ema_fast
    ema_slow = (close_price - ema_slow) * K_SLOW * stdev_factor + ema_slow

  ema_fast_values.append(ema_fast)
  ema_slow_values.append(ema_slow)

  apo = ema_fast - ema_slow
  apo_values.append(apo)

  
  if num_shares_per_trade > risk_limit_max_trade_size:
    risk_violated = True

  MIN_PROFIT_TO_CLOSE = num_shares_per_trade * 10

  
  if (not risk_violated and
      ((apo > APO_VALUE_FOR_SELL_ENTRY * stdev_factor and abs(close_price - last_sell_price) > MIN_PRICE_MOVE_FROM_LAST_TRADE * stdev_factor)  
       or
       (position > 0 and (apo >= 0 or open_pnl > MIN_PROFIT_TO_CLOSE / stdev_factor)))):  # long and APO has gone positive, so sell to close position
    orders.append(-1)  # mark the sell trade
    last_sell_price = close_price
    if position == 0: # opening a new entry position
      position -= num_shares_per_trade  # reduce position by the size of this trade
      sell_sum_price_qty += (close_price * num_shares_per_trade)  # update vwap sell-price
      sell_sum_qty += num_shares_per_trade
      traded_volume += num_shares_per_trade
      print("Sell ", num_shares_per_trade, " @ ", close_price, "Position: ", position)
    else: # closing an existing position
      sell_sum_price_qty += (close_price * abs(position))  # update vwap sell-price
      sell_sum_qty += abs(position)
      traded_volume += abs(position)
      print("Sell ", abs(position), " @ ", close_price, "Position: ", position)
      position = 0  # reduce position by the size of this trade

  elif (not risk_violated and
        ((apo < APO_VALUE_FOR_BUY_ENTRY * stdev_factor and abs(close_price - last_buy_price) > MIN_PRICE_MOVE_FROM_LAST_TRADE * stdev_factor) 
         or
         (position < 0 and (apo <= 0 or open_pnl > MIN_PROFIT_TO_CLOSE / stdev_factor)))):  # short and APO has gone negative, so buy to close position
    orders.append(+1)  # mark the buy trade
    last_buy_price = close_price
    if position == 0:
      position+=num_shares_per_trade
      buy_sum_price_qty+=(close_price * num_shares_per_trade)
      buy_sum_qty+=num_shares_per_trade
      traded_volume+=num_shares_per_trade
    else:
      buy_sum_price_qty += (close_price * abs(position))
      buy_sum_qty += abs(position)
      traded_volume += abs(position)
      position = 0

  else:
    # No trade since none of the conditions were met to buy or sell
    orders.append(0)

  positions.append(position)

  if current_pos == 0:
    if position!=0:
      current_pos = position
      current_pos_start = len(positions)

  elif current_pos * position <= 0:
    current_pos = position
    position_holding_time = len(positions) - current_pos_start
    current_pos_start = len(positions)

    if position_holding_time > RISK_LIMIT_MAX_POSITION_HOLDING_TIME_DAYS:
      risk_violated = True
  
  if abs(position) > risk_limit_max_position:
    risk_violated = True

  

  # This section updates Open/Unrealized & Closed/Realized positions
  open_pnl = 0
  if position > 0:
    if sell_sum_qty > 0:  # long position and some sell trades have been made against it, close that amount based on how much was sold against this long position
      open_pnl = abs(sell_sum_qty) * (sell_sum_price_qty / sell_sum_qty - buy_sum_price_qty / buy_sum_qty)
    # mark the remaining position to market i.e. pnl would be what it would be if we closed at current price
    open_pnl += abs(sell_sum_qty - position) * (close_price - buy_sum_price_qty / buy_sum_qty)
  elif position < 0:
    if buy_sum_qty > 0:  # short position and some buy trades have been made against it, close that amount based on how much was bought against this short position
      open_pnl = abs(buy_sum_qty) * (sell_sum_price_qty / sell_sum_qty - buy_sum_price_qty / buy_sum_qty)
    # mark the remaining position to market i.e. pnl would be what it would be if we closed at current price
    open_pnl += abs(buy_sum_qty - position) * (sell_sum_price_qty / sell_sum_qty - close_price)
  else:
    # flat, so update closed_pnl and reset tracking variables for positions & pnls
    closed_pnl += (sell_sum_price_qty - buy_sum_price_qty)
    buy_sum_price_qty = 0
    buy_sum_qty = 0
    sell_sum_price_qty = 0
    sell_sum_qty = 0
    last_buy_price = 0
    last_sell_price = 0

  print("OpenPnL: ", open_pnl, " ClosedPnL: ", closed_pnl, " TotalPnL: ", (open_pnl + closed_pnl))
  pnls.append(closed_pnl + open_pnl)

  # Analyze monthly performance and adjust risk up/down
  if len(pnls)>20:
    monthly_pnls = pnls[-1] - pnls[-20]

    if len(pnls) - last_risk_change_index > 20:
      if monthly_pnls>0:
        num_shares_per_trade += INCREMENT_NUM_SHARES_PER_TRADE
        if num_shares_per_trade <= MAX_NUM_SHARES_PER_TRADE:
          risk_limit_weekly_stop_loss += INCREMENT_RISK_LIMIT_WEEKLY_STOP_LOSS
          risk_limit_monthly_stop_loss += INCREMENT_RISK_LIMIT_MONTHLY_STOP_LOSS
          risk_limit_max_position += INCREMENT_RISK_LIMIT_MAX_POSITION
          risk_limit_max_trade_size += INCREMENT_RISK_LIMIT_MAX_TRADE_SIZE
      elif monthly_pnls < 0:
        num_shares_per_trade -= INCREMENT_NUM_SHARES_PER_TRADE
        if num_shares_per_trade >= MIN_NUM_SHARES_PER_TRADE:
          print('Decreasing trade-size and risk')
          risk_limit_weekly_stop_loss -= INCREMENT_RISK_LIMIT_WEEKLY_STOP_LOSS
          risk_limit_monthly_stop_loss -= INCREMENT_RISK_LIMIT_MONTHLY_STOP_LOSS
          risk_limit_max_position -= INCREMENT_RISK_LIMIT_MAX_POSITION
          risk_limit_max_trade_size -= INCREMENT_RISK_LIMIT_MAX_TRADE_SIZE
        else:
          num_shares_per_trade = MIN_NUM_SHARES_PER_TRADE

      last_risk_change_index = len(pnls)

  # Track trade-sizes/positions and risk limits as they evolve over time
  num_shares_history.append(num_shares_per_trade)
  abs_position_history.append(abs(position))
  max_trade_size_history.append(risk_limit_max_trade_size)
  max_position_history.append(risk_limit_max_position)

  if len(pnls) > 5:
    weekly_loss = pnls[-1] - pnls[-6]

    if weekly_loss < risk_limit_weekly_stop_loss:
      print('RiskViolation weekly_loss', weekly_loss, ' < risk_limit_weekly_stop_loss', risk_limit_weekly_stop_loss)
      risk_violated = True

  if len(pnls) > 20:
    monthly_loss = pnls[-1] - pnls[-21]

    if monthly_loss < risk_limit_monthly_stop_loss:
      print('RiskViolation monthly_loss', monthly_loss, ' < risk_limit_monthly_stop_loss', risk_limit_monthly_stop_loss)
      risk_violated = True

# This section prepares the dataframe from the trading strategy results and visualizes the results
data = data.assign(ClosePrice=pd.Series(close, index=data.index))
data = data.assign(Fast10DayEMA=pd.Series(ema_fast_values, index=data.index))
data = data.assign(Slow40DayEMA=pd.Series(ema_slow_values, index=data.index))
data = data.assign(APO=pd.Series(apo_values, index=data.index))
data = data.assign(Trades=pd.Series(orders, index=data.index))
data = data.assign(Position=pd.Series(positions, index=data.index))
data = data.assign(Pnl=pd.Series(pnls, index=data.index))
data = data.assign(NumShares=pd.Series(num_shares_history, index=data.index))
data = data.assign(MaxTradeSize=pd.Series(max_trade_size_history, index=data.index))
data = data.assign(AbsPosition=pd.Series(abs_position_history, index=data.index))
data = data.assign(MaxPosition=pd.Series(max_position_history, index=data.index))

import matplotlib.pyplot as plt

data['ClosePrice'].plot(color='blue', lw=3., legend=True)
data['Fast10DayEMA'].plot(color='y', lw=1., legend=True)
data['Slow40DayEMA'].plot(color='m', lw=1., legend=True)
plt.plot(data.loc[ data.Trades == 1 ].index, data.ClosePrice[data.Trades == 1 ], color='r', lw=0, marker='^', markersize=4, label='buy')
plt.plot(data.loc[ data.Trades == -1 ].index, data.ClosePrice[data.Trades == -1 ], color='g', lw=0, marker='v', markersize=4, label='sell')
plt.legend()
plt.show()

data['APO'].plot(color='k', lw=3., legend=True)
plt.plot(data.loc[ data.Trades == 1 ].index, data.APO[data.Trades == 1 ], color='r', lw=0, marker='^', markersize=4, label='buy')
plt.plot(data.loc[ data.Trades == -1 ].index, data.APO[data.Trades == -1 ], color='g', lw=0, marker='v', markersize=4, label='sell')
plt.axhline(y=0, lw=0.5, color='k')
for i in range( APO_VALUE_FOR_BUY_ENTRY, APO_VALUE_FOR_BUY_ENTRY*5, APO_VALUE_FOR_BUY_ENTRY ):
  plt.axhline(y=i, lw=0.5, color='r')
for i in range( APO_VALUE_FOR_SELL_ENTRY, APO_VALUE_FOR_SELL_ENTRY*5, APO_VALUE_FOR_SELL_ENTRY ):
  plt.axhline(y=i, lw=0.5, color='g')
plt.legend()
plt.show()

data['Position'].plot(color='k', lw=1., legend=True)
plt.plot(data.loc[ data.Position == 0 ].index, data.Position[ data.Position == 0 ], color='k', lw=0, marker='.', label='flat')
plt.plot(data.loc[ data.Position > 0 ].index, data.Position[ data.Position > 0 ], color='r', lw=0, marker='+', label='long')
plt.plot(data.loc[ data.Position < 0 ].index, data.Position[ data.Position < 0 ], color='g', lw=0, marker='_', label='short')
plt.axhline(y=0, lw=0.5, color='k')
plt.legend()
plt.show()

data['Pnl'].plot(color='k', lw=1., legend=True)
plt.plot(data.loc[ data.Pnl > 0 ].index, data.Pnl[ data.Pnl > 0 ], color='g', lw=0, marker='.')
plt.plot(data.loc[ data.Pnl < 0 ].index, data.Pnl[ data.Pnl < 0 ], color='r', lw=0, marker='.')
plt.legend()
plt.show()

data['NumShares'].plot(color='b', lw=3., legend=True)
data['MaxTradeSize'].plot(color='g', lw=1., legend=True)
plt.legend()
plt.show()

data['AbsPosition'].plot(color='b', lw=1., legend=True)
data['MaxPosition'].plot(color='g', lw=1., legend=True)
plt.legend()
plt.show()
