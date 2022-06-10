from TradingSystem.LiquidityProvider import LiquidityProvider
from Backtesting.TradingStrategyDualMA import TradingStrategyDualMA
from TradingSystem.MarketSimulator import MarketSimulator
from TradingSystem.OrderManager import OrderManager
from TradingSystem.OrderBook import OrderBook
from collections import deque

import pandas as pd
from pandas_datareader import data
import matplotlib.pyplot as plt


def call_if_not_empty(deq, fun):
    while (len(deq) > 0):
        fun()


class EventBasedBackTester:
    def __init__(self):
        self.liquidity_provider_to_gateway = deque()
        self.order_book_to_trading_strategy = deque()
        self.trading_strategy_to_order_manager = deque()
        self.market_strategy_to_order_manager = deque()
        self.order_manager_to_trading_strategy = deque()
        self.gateway_to_order_manager = deque()
        self.order_manager_to_gateway = deque()


        self.lp = LiquidityProvider(self.liquidity_provider_to_gateway)
        self.ob = OrderBook(self.liquidity_provider_to_gateway, self.order_book_to_trading_strategy)
        self.ts = TradingStrategyDualMA(self.order_book_to_trading_strategy, self.trading_strategy_to_order_manager,\
                                  self.order_manager_to_trading_strategy)
        self.ms = MarketSimulator(self.order_manager_to_gateway, self.gateway_to_order_manager)
        self.om = OrderManager(self.trading_strategy_to_order_manager, self.order_manager_to_trading_strategy,\
                               self.order_manager_to_gateway, self.gateway_to_order_manager)


    def process_data_from_yahoo(self,price):

        order_bid = {
            'id': 1,
            'price': price,
            'quantity': 1000,
            'side': 'bid',
            'action': 'new'
        }
        order_ask = {
            'id': 1,
            'price': price,
            'quantity': 1000,
            'side': 'ask',
            'action': 'new'
        }
        self.liquidity_provider_to_gateway.append(order_ask)
        self.liquidity_provider_to_gateway.append(order_bid)
        self.process_events()
        order_ask['action']='delete'
        order_bid['action'] = 'delete'
        self.liquidity_provider_to_gateway.append(order_ask)
        self.liquidity_provider_to_gateway.append(order_bid)

    def process_events(self):
        while len(self.liquidity_provider_to_gateway)>0:
            call_if_not_empty(self.liquidity_provider_to_gateway,\
                                   self.ob.handle_order_from_gateway)
            call_if_not_empty(self.order_book_to_trading_strategy, \
                                   self.ts.handle_input_from_bb)
            call_if_not_empty(self.trading_strategy_to_order_manager, \
                                   self.om.handle_input_from_ts)
            call_if_not_empty(self.order_manager_to_gateway, \
                                   self.ms.handle_order_from_gw)
            call_if_not_empty(self.gateway_to_order_manager, \
                                   self.om.handle_input_from_market)
            call_if_not_empty(self.order_manager_to_trading_strategy, \
                                   self.ts.handle_response_from_om)



eb=EventBasedBackTester()


def load_financial_data(start_date, end_date,output_file):
    try:
        df = pd.read_pickle(output_file)
        print('File data found...reading GOOG data')
    except FileNotFoundError:
        print('File not found...downloading the GOOG data')
        df = data.DataReader('GOOG', 'yahoo', start_date, end_date)
        df.to_pickle(output_file)
    return df

goog_data=load_financial_data(start_date='2001-01-01',
                    end_date = '2018-01-01',
                    output_file='goog_data.pkl')


for line in zip(goog_data.index,goog_data['Adj Close']):
    date=line[0]
    price=line[1]
    price_information={'date' : date,
                      'price' : float(price)}
    eb.process_data_from_yahoo(price_information['price'])
    eb.process_events()


plt.plot(eb.ts.list_paper_total,label="Paper Trading using Event-Based BackTester")
plt.plot(eb.ts.list_total,label="Trading using Event-Based BackTester")
plt.legend()
plt.show()

