from random import randrange

#this is the last part of the trading system, which is the market simulator, which validates our trading strategy
#acknolwedges and fills all new orders in our system
class MarketSimulator:
    def __init__(self, order_manager_to_gateway=None,gateway_to_order_manager=None):
        self.orders = []
        self.order_manager_to_gateway = order_manager_to_gateway
        self.gateway_to_order_manager = gateway_to_order_manager


    def lookup_orders(self,order):
        count=0
        for o in self.orders:
            if o['id'] ==  order['id']:
                return o, count
            count+=1
        return None, None

    #handle the order from the gateway leading to the order manager
    def handle_order_from_gw(self):
        if self.order_manager_to_gateway is not None:
            if len(self.order_manager_to_gateway)>0:
                self.handle_order(self.order_manager_to_gateway.popleft())
        else:
            print('simulation mode')

    #fill all new orders placed in market simulator and remove them
    def fill_all_orders(self,ratio = 100):
        orders_to_be_removed = []
        for index, order in enumerate(self.orders):
            if randrange(100)<=ratio:
                order['status'] = 'filled'
            else:
                order['status'] = 'cancelled'
            orders_to_be_removed.append(index)
            if self.gateway_to_order_manager is not None:
                self.gateway_to_order_manager.append(order.copy())
            else:
                print('simulation mode')
        for i in sorted(orders_to_be_removed,reverse=True):
            del(self.orders[i])

    #code for handling the order passed on the market simulator
    def handle_order(self, order):
        #gets the counter and offset of the order
        o,offset=self.lookup_orders(order)
        if o is None:
            #if the order is new and o is non, then we set the status as accepted, add it to oders, and sent it to the order manager
            if order['action'] == 'New':
                order['status'] = 'accepted'
                self.orders.append(order)
                if self.gateway_to_order_manager is not None:
                    self.gateway_to_order_manager.append(order.copy())
                    self.fill_all_orders(100)
                else:
                    print('simulation mode')
                return
            #if we want to cancel it or amend it, then add it to just the manager's list of orders
            elif order['action'] == 'Cancel' or order['action'] == 'Amend':
                print('Order id - not found - Rejection')
                if self.gateway_to_order_manager is not None:
                    self.gateway_to_order_manager.append(order.copy())
                else:
                    print('simulation mode')
                return
        elif o is not None:
            #will not add any duplicate orders
            if order['action'] == 'New':
                print('Duplicate order id - Rejection')
                return
            elif order['action'] == 'Cancel':
                #if the action is cancel, then the status will be cancelled, and send it to the order manager
                o['status']='cancelled'
                if self.gateway_to_order_manager is not None:
                    self.gateway_to_order_manager.append(o.copy())
                else:
                    print('simulation mode')
                #delete it from the orders
                del (self.orders[offset])
                print('Order cancelled')
            elif order['action'] == 'Amend':
                #otherwise, state as accepted and send it to the order manager
               o['status'] = 'accepted'
               if self.gateway_to_order_manager is not None:
                   self.gateway_to_order_manager.append(o.copy())
               else:
                   print('simulation mode')
               print('Order amended')



