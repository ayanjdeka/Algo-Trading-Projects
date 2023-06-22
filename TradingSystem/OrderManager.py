class OrderManager:
    def __init__(self,trading_strategy_to_order_manager = None, order_manager_to_trading_strategy = None,
                 order_manager_to_gateway=None,gateway_to_order_manager=None):
        self.orders=[]
        self.order_id=0
        self.trading_strategy_to_order_manager = trading_strategy_to_order_manager
        self.order_manager_to_gateway = order_manager_to_gateway
        self.gateway_to_order_manager = gateway_to_order_manager
        self.order_manager_to_trading_strategy = order_manager_to_trading_strategy

    #check if the order is valid based on the quantity and price values
    def check_order_valid(self,order):
        if order['quantity'] < 0:
            return False
        if order['price'] < 0:
            return False
        return True

    # create the order based on the price from the trading strategy
    def create_new_order(self,order):
        self.order_id += 1
        neworder = {
            'id': self.order_id,
            'price': order['price'],
            'quantity': order['quantity'],
            'side': order['side'],
            'status': 'new',
            'action': 'New'
        }
        return neworder

    #functions as the function for handling from the trading strategy
    def handle_input_from_ts(self):
        if self.trading_strategy_to_order_manager is not None:
            if len(self.trading_strategy_to_order_manager)>0:
                self.handle_order_from_trading_strategy(self.trading_strategy_to_order_manager.popleft())
        else:
            print('siumlation mode')
    

    def handle_order_from_trading_strategy(self,order):
        #check if the order is valid, create and it to the order manager orders, and add it to be sent to the gateway
        if self.check_order_valid(order):
            order=self.create_new_order(order).copy()
            self.orders.append(order)
            if self.order_manager_to_gateway is None:
                print('simulation mode')
            else:
                self.order_manager_to_gateway.append(order.copy())

    def lookup_order_by_id(self,id):
        for i in range(len(self.orders)):
            if self.orders[i]['id']==id:
                return self.orders[i]
        return None

    #cleans all the filled orders and removes them from the order list
    def clean_traded_orders(self):
        order_traded = []

        for i in range(len(self.orders)):
            if self.orders[i]['status'] == 'filled':
                order_traded.append(i)
        if len(order_traded) > 0:
            for k in sorted(order_traded,reverse=True):
                del (self.orders[k])

    #handles the case in which it monitors the market response of the order
    def handle_input_from_market(self):
        if self.gateway_to_order_manager is not None:
            if len(self.gateway_to_order_manager)>0:
                self.handle_order_from_gateway(self.gateway_to_order_manager.popleft())
        else:
            print('simulation mode')

    #this is the order from the market response that is sent to the trading strategy
    def handle_order_from_gateway(self,order_update):
        order=self.lookup_order_by_id(order_update['id'])
        if order is not None:
            #update the order status, and sent it to the trading strategy
            order['status']=order_update['status']
            if self.order_manager_to_trading_strategy is not None:
                self.order_manager_to_trading_strategy.append(order.copy())
            else:
                print('simulation mode')
            #if the orders are filled, then clean them
            self.clean_traded_orders()
        else:
            print('order not found')

