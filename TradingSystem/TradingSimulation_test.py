import unittest
from TradingSystem.LiquidityProvider import LiquidityProvider
from TradingSystem.TradingStrategy import TradingStrategy
from TradingSystem.MarketSimulator import MarketSimulator
from TradingSystem.OrderManager import OrderManager
from TradingSystem.OrderBook import OrderBook
from collections import deque

class TestTradingSimulation(unittest.TestCase):
    def setUp(self):
        self.liquid_provider_to_gateway=deque()
        self.order_book_to_trading_strategy = deque()
        self.trading_strategy_to_order_manager = deque()
        self.market_strategy_to_order_manager = deque()
        self.order_manager_to_trading_strategy = deque()
        self.gateway_to_order_manager = deque()
        self.order_manager_to_gateway = deque()




        self.lp=LiquidityProvider(self.liquid_provider_to_gateway)
        self.ob=OrderBook(self.liquid_provider_to_gateway, self.order_book_to_trading_strategy)
        self.ts=TradingStrategy(self.order_book_to_trading_strategy,self.trading_strategy_to_order_manager,self.order_manager_to_trading_strategy)
        self.ms=MarketSimulator(self.order_manager_to_gateway,self.gateway_to_order_manager)
        self.om=OrderManager(self.trading_strategy_to_order_manager, self.order_manager_to_trading_strategy,self.order_manager_to_gateway,self.gateway_to_order_manager)



    def test_add_liquidity(self):
        # Order sent from the exchange to the trading system
        order1 = {
            'id': 1,
            'price': 219,
            'quantity': 10,
            'side': 'bid',
            'action': 'new'
        }
        self.lp.insert_manual_order(order1)
        self.assertEqual(len(self.liquid_provider_to_gateway),1)
        self.ob.handle_order_from_gateway()
        self.assertEqual(len(self.order_book_to_trading_strategy), 1)
        self.ts.handle_input_from_bb()
        self.assertEqual(len(self.trading_strategy_to_order_manager), 0)
        order2 = {
            'id': 2,
            'price': 218,
            'quantity': 10,
            'side': 'ask',
            'action': 'new'
        }
        self.lp.insert_manual_order(order2.copy())
        self.assertEqual(len(self.liquid_provider_to_gateway),1)
        self.ob.handle_order_from_gateway()
        self.assertEqual(len(self.order_book_to_trading_strategy), 1)
        self.ts.handle_input_from_bb()
        self.assertEqual(len(self.trading_strategy_to_order_manager), 2)
        self.om.handle_input_from_ts()
        self.assertEqual(len(self.trading_strategy_to_order_manager), 1)
        self.assertEqual(len(self.order_manager_to_gateway), 1)
        self.om.handle_input_from_ts()
        self.assertEqual(len(self.trading_strategy_to_order_manager), 0)
        self.assertEqual(len(self.order_manager_to_gateway), 2)
        self.ms.handle_order_from_gw()
        self.assertEqual(len(self.gateway_to_order_manager), 2)
        self.ms.handle_order_from_gw()
        self.assertEqual(len(self.gateway_to_order_manager), 4)
        self.om.handle_input_from_market()
        self.om.handle_input_from_market()
        self.assertEqual(len(self.order_manager_to_trading_strategy), 2)
        self.ts.handle_response_from_om()
        self.assertEqual(self.ts.get_pnl(),0)
        self.ms.fill_all_orders()
        self.assertEqual(len(self.gateway_to_order_manager), 2)
        self.om.handle_input_from_market()
        self.om.handle_input_from_market()
        self.assertEqual(len(self.order_manager_to_trading_strategy), 3)
        self.ts.handle_response_from_om()
        self.assertEqual(len(self.order_manager_to_trading_strategy), 2)
        self.ts.handle_response_from_om()
        self.assertEqual(len(self.order_manager_to_trading_strategy), 1)
        self.ts.handle_response_from_om()
        self.assertEqual(len(self.order_manager_to_trading_strategy), 0)
        self.assertEqual(self.ts.get_pnl(),10)





