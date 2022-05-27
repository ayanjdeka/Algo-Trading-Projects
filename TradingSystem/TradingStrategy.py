class TradingStrategy:


    #this is an arbritrary strading strategy that just has a simple trading signal if the offer price
    #is greater than the bid price, just built it as a learning tool for an overall trade model

    def __init__(self,order_book_to_trading_strategy = None, trading_strategy_to_order_manager = None, order_manager_to_trading_strategy = None):
        self.orders = []
        self.order_id = 0
        self.position = 0
        self.pnl = 0
        self.cash = 10000
        self.current_bid = 0
        self.current_offer = 0
        self.order_book_to_trading_strategy = order_book_to_trading_strategy
        self.trading_strategy_to_order_manager = trading_strategy_to_order_manager
        self.order_manager_to_trading_strategy = order_manager_to_trading_strategy


    #creates both buy and sell orders
    def create_orders(self,book_event, quantity):
        self.order_id+=1
        ord = {
            'id': self.order_id,
            'price': book_event['bid_price'],
            'quantity': quantity,
            'side': 'sell',
            'action': 'to_be_sent'
        }

        self.orders.append(ord.copy())

        self.order_id+=1
        ord = {
            'id': self.order_id,
            'price': book_event['offer_price'],
            'quantity': quantity,
            'side': 'buy',
            'action': 'to_be_sent'
        }
        self.orders.append(ord.copy())

    #cretes the signal if the bid price is > offer price, and both of the prices are greater than 0
    def signal(self, book_event):
        if book_event is not None:
            if book_event["bid_price"]>book_event["offer_price"]:
                if book_event["bid_price"]>0 and book_event["offer_price"]>0:
                    return True
                else:
                    return False
        else:
            return False

    #executes all the orders that are sent to the TradingStrategy
    def execution(self):
        orders_to_be_removed = []
        for index, order in enumerate(self.orders):
            #update the order action if it needs to be sent
            if order['action'] == 'to_be_sent':
                order['status'] = 'new'
                order['action'] = 'no_action'
                if self.trading_strategy_to_order_manager is None:
                    print('Simulation Mode')
                else:
                    #add it to the list to be sent to the order manager
                    self.trading_strategy_to_order_manager.append(order.copy())

            #in case it is sent back from the order manager, then remove the order
            if order['status'] == 'rejected':
                orders_to_be_removed.append(index)
            if order['status'] == 'filled':
                #if it is filled, then we update the position, pnl, and cash
                orders_to_be_removed.append(index)
                pos = order['quantity'] if order['side'] == 'buy' else -order['quantity']
                self.position+=pos
                self.pnl-= pos* order['price']
                self.cash -= pos * order['price']
        for order_index in sorted(orders_to_be_removed,reverse=True):
            del (self.orders[order_index])

    #handles all orders from the order book
    def handle_input_from_bb(self,book_event=None):
        if self.order_book_to_trading_strategy is None:
            print('simulation mode')
            self.handle_book_event(book_event)
        else:
            if len(self.order_book_to_trading_strategy)>0:
                be=self.handle_book_event(self.order_book_to_trading_strategy.popleft())
                self.handle_book_event(be)
         
    #handles the instance where we have a new book even and have to create the order based off that
    def handle_book_event(self,book_event):
        if book_event is not None:
            self.current_bid = book_event['bid_price']
            self.current_offer = book_event['offer_price']

        if self.signal(book_event):
            self.create_orders(book_event,min(book_event['bid_quantity'],book_event['offer_quantity']))
        self.execution()

    def lookup_orders(self,id):
        count=0
        for o in self.orders:
            if o['id'] ==  id:
                return o, count
            count+=1
        return None, None

    #functionality in case orders are sent back from the order manager
    def handle_response_from_om(self):
        if self.order_manager_to_trading_strategy is not None:
            self.handle_market_response(self.order_manager_to_trading_strategy.popleft())
        else:
            print('simulation mode')

    #this handles the market response for a specific order based on the order manager
    def handle_market_response(self, order_execution):
        order,_=self.lookup_orders(order_execution['id'])
        if order is None:
            print('error not found')
            return
        order['status']=order_execution['status']
        self.execution()

    def get_pnl(self):
        return self.pnl + self.position * (self.current_bid + self.current_offer)/2