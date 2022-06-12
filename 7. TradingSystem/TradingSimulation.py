from TradingSystem.LiquidityProvider import LiquidityProvider
from TradingSystem.TradingStrategy import TradingStrategy
from TradingSystem.MarketSimulator import MarketSimulator
from TradingSystem.OrderManager import OrderManager
from TradingSystem.OrderBook import OrderBook
from collections import deque

def main():
    liquid_provider_to_gateway = deque()
    order_book_to_trading_strategy = deque()
    trading_strategy_to_order_manager = deque()
    market_strategy_to_order_manager = deque()
    order_manager_to_trading_strategy = deque()
    gateway_to_order_manager = deque()
    order_manager_to_gateway = deque()

    lp = LiquidityProvider(liquid_provider_to_gateway)
    ob = OrderBook(liquid_provider_to_gateway, order_book_to_trading_strategy)
    ts = TradingStrategy(order_book_to_trading_strategy, trading_strategy_to_order_manager, order_manager_to_trading_strategy)
    ms = MarketSimulator(order_manager_to_gateway, gateway_to_order_manager)
    om = OrderManager(trading_strategy_to_order_manager, order_manager_to_trading_strategy, order_manager_to_gateway, gateway_to_order_manager)

    lp.read_tick_data_from_data_source()
    while len(liquid_provider_to_gateway)>0:
        ob.handle_order_from_gateway()
        ts.handle_input_from_bb()
        om.handle_input_from_ts()
        ms.handle_order_from_gw()
        om.handle_input_from_market()
        ts.handle_response_from_om()
        lp.read_tick_data_from_data_source()




if __name__ == '__main__':
    main()
    s:str = "Seee"
    s.lower()