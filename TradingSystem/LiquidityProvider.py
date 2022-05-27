from random import randrange
from random import sample,seed

class LiquidityProvider:

    #class will generate orders with random prices and quantities for testing purposes
    def __init__(self, liquid_provider_to_gateway = None):
        #initialize the array of orders, specific order id, and array for sending the orders to the gateway
        self.orders = []
        self.order_id = 0
        seed(0)
        self.liquid_provider_to_gateway = liquid_provider_to_gateway

    #lookup order by id passed in this method
    def lookup_orders(self,id):
        count = 0
        for order in self.orders:
            if order['id'] == id:
                return order, count
            count+=1
        return None,None
    
    # inser the order into the gateway 
    def insert_manual_order(self,order):
        if self.liquid_provider_to_gateway is None:
            return order
        self.liquid_provider_to_gateway.append(order.copy())


    def read_tick_data_from_data_source(self):
        pass

    #generate order with the random values of quantity, price, buy/sell, and order id
    def generate_random_order(self):
        price = randrange(8,12)
        quantity = randrange(1,10) * 100
        side=sample(['buy','sell'],1)[0]
        order_id=randrange(0,self.order_id + 1)
        order = self.lookup_orders(order_id)

        #account if it is a new oeder or not
        new_order = False
        if order is None:
            action = 'new'
            new_order = True
        else:
            action = sample(['modify','delete'],1)[0]

        ord = {
            'id': self.order_id,
            'price': price,
            'quantity': quantity,
            'side': side,
            'action': action
        }

        #list of orders should append this order
        if not new_order:
            self.order_id+=1
            self.orders.append(ord)
        
        if not self.liquid_provider_to_gateway:
            print('simulation mode')
            return ord
        #append to the list of orders sent to the gateway
        self.liquid_provider_to_gateway.append(ord.copy())