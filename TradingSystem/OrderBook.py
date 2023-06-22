class OrderBook:
    def __init__(self,gt_2_ob = None,orderbook_to_trading_strategy = None):
        self.list_asks = []
        self.list_bids = []
        self.gateway_to_orderbook=gt_2_ob
        self.orderbook_to_trading_strategy = orderbook_to_trading_strategy
        self.current_bid = None
        self.current_ask = None


    
    #create the bid and offer prices and quantities if there exists one
    def create_book_event(self,bid,offer):
        book_event = {
            "bid_price": bid['price'] if bid else -1,
            "bid_quantity": bid['quantity'] if bid else -1,
            "offer_price": offer['price'] if offer else -1,
            "offer_quantity": offer['quantity'] if offer else -1
        }
        return book_event

    #this is to check the current book event of the order book, and whether to send it to the trading strategy
    def check_generate_top_of_book_event(self):
        changed = False

        current_list = self.list_bids
        #check if there exists a bid or ask, and update the bid and ask prices and indicate that it is changed
        if len(current_list)==0:
            if self.current_bid is not None:
                changed=True
                self.current_bid = None
        else:
            if self.current_bid!=current_list[0]:
                changed=True
                self.current_bid=current_list[0]

        current_list = self.list_asks
        if len(current_list)==0:
            if self.current_ask is not None:
                changed=True
                self.current_ask = None
        else:
            if self.current_ask!=current_list[0]:
                changed=True
                self.current_ask=current_list[0]

        #if any of these prices changed, then create a new book event and append it to be sent to the trading strategy
        if changed:
            be=self.create_book_event(self.current_bid,
                                      self.current_ask)
            if self.orderbook_to_trading_strategy is not None:
                self.orderbook_to_trading_strategy.append(be)
            else:
                return be

    #function provides the logic for handling the order from the gateway provided by the liquid provider
    def handle_order_from_gateway(self,order = None):
        if self.gateway_to_orderbook is None:
            print('simulation mode')
            self.handle_order(order)
        elif len(self.gateway_to_orderbook)>0:
            #keep handling each order in the list of gateway to orderbook
            self.handle_order(self.gateway_to_orderbook.popleft())
    
    #different instances of handling orders
    def handle_order(self,o):
        if o['action']=='new':
            self.handle_new(o)
        elif o['action']=='modify':
            self.handle_modify(o)
        elif o['action']=='delete':
            self.handle_delete(o)
        else:
            print('Error-Cannot handle this action')

        #After we handle the orders, then we generate what is sent to the trading strategy
        return self.check_generate_top_of_book_event()

    #handles new orders and sorts them
    def handle_new(self,o):
        if o['side']=='bid':
            self.list_bids.append(o)
            self.list_bids.sort(key=lambda x: x['price'],reverse=True)
        elif o['side']=='ask':
            self.list_asks.append(o)
            self.list_asks.sort(key=lambda x: x['price']) 


    #handles modified orders and updates the quantity
    def handle_modify(self,o):
        order = self.find_order_in_a_list(o)
        if order['quantity'] > o['quantity']:
            order['quantity'] = o['quantity']

        return    

    #looks up what type of order it is, finds the specific order, and then removes it
    def handle_delete(self,o):
        lookup_list = self.get_list(o)
        order = self.find_order_in_a_list(o,lookup_list)
        if order is not None:
            lookup_list.remove(order)
        return None


    #gets the list if the order is in the bid or ask list
    def get_list(self,o):
        if 'side' in o:
            if o['side']=='bid':
                lookup_list = self.list_bids
            elif o['side'] == 'ask':
                lookup_list = self.list_asks
            else:
                print('incorrect side')
                return None
            return lookup_list
        else:
            for order in self.list_bids:
                if order['id']==o['id']:
                    return self.list_bids
            for order in self.list_asks:
                if order['id'] == o['id']:
                    return self.list_asks
            return None

    #finds the actual order in the list
    def find_order_in_a_list(self, o, lookup_list = None):
        if lookup_list is None:
            lookup_list = self.get_list(o)
        if lookup_list is not None:
            for order in lookup_list:
                if order['id'] == o['id']:
                    return order
        
        return None


