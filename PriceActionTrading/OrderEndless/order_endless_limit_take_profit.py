import time
import TTraderLib.t_display_dash_table as display
import TTraderLib.t_client_manager as client
import oe_symbol_manager as symbol_manager_class
import sys
import logging
from typing import List
import threading
from binance.enums import *
import oe_broker as broker_class


class OrderEndlessManager:

    # Config
    fee = .00075
    stay_paused_after_selling_an_order = True
    order_active = False
    paper_trading = False

    #
    total_pnl = 0
    total_pnl_percent = 0
    cli = client.ClientManager()
    symbol_manager = symbol_manager_class.SymbolManager()
    broker = broker_class.Broker()

    # Debug
    debug_price = False

    # Table Header
    header = ["Symbol",
              "Status",
              "Buy Or Sell",
              "Current Price",
              "Limit Price",
              "Quanity USD",
              "Symbol Quantity",
              "Order Type",
              "Purchase Price",
              "Stop Loss Price",
              "Stop Loss %",
              "Take Profit Price",
              "Take Profit %",
              "P&L%",
              "P&L$"
              ]

    class Order:
        buy_or_sell = ""
        symbol_name = ""
        quantity_in_usd = 0
        quantity_in_symbol = 0
        order_type = ""
        limit_price = 0
        stop_loss_percent = 0
        stop_loss_price = 0
        take_profit_percent = 0
        take_profit_price = 0
        purchase_price = 0
        status = ""
        pnl_percent = 0
        pnl = 0

    list_of_set_orders: List[Order] = []

    #
    def __init__(self):
        self.start()

    def start(self):

        # Start Table
        display.DisplayDashTable.start_dash_table("Orders", self.header)

        # Disable logs
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        # Set Update Info
        update_info_thread = threading.Thread(target=self.update_all_loop, args=())
        update_info_thread.start()

        while True:
            # User Input
            the_input = input("Input: ")
            self.handle_all_input(the_input)

    # Input
    def handle_all_input(self, _input):

        try:
            # Format Input
            _input = _input.upper()

            if _input == "":
                print("\nType help for full list of commands.")
                return

            input_array = _input.split(" ")

            # Order Input
            if input_array[0] == "BUY":
                self.handle_order_input(input_array)
                return

            # Sell
            if input_array[0] == "SELL":
                self.handle_sell_input(input_array)

            # GET
            if input_array[0] == "GET":
                self.handle_get_input(input_array)
                return

            # Cancel
            if input_array[0] == "CANCEL":
                self.handle_cancel_input(input_array)
                return

            # Debug Input
            if input_array[0] == "DB":
                self.handle_debug_input(input_array)
                return

            # Edit
            if input_array[0] == "EDIT":
                self.handle_edit_input(input_array)
                return

            # Help
            if input_array[0] == "HELP":
                self.handle_help_input(input_array)
                return

            # Pause
            if input_array[0] == "PAUSE":
                self.handle_pause_input(input_array)
                return

            # Start
            if input_array[0] == "START":
                self.handle_start_input(input_array)
                return

            print("\nType help for full list of commands.")
        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_order_input(self, input_array):
        limit_price = 0
        stop_loss_percent = 0
        take_profit_percent = 0

        # Buy Or Sell
        if input_array[0] == "BUY":
            buy_or_sell = "BUY"
        else:
            print(input_array[0] + ": Command not found.")
            return

        # Quantity
        try:
            quantity_usd = float(input_array[1])

            if quantity_usd <= 0:
                print("Quantity less than or equal to zero.")
                return

        except Exception as e:
            print(str(e) + "  Invalid Quantity.")
            return

        # Symbol
        try:
            text_file = open(sys.path[1] + "/PriceActionTrading/OrderEndless/all_symbols.txt", "r")
            lines = text_file.read().split("\n")
            text_file.close()

            symbol = input_array[2]

            if not lines.__contains__(symbol):
                print("Symbol not found.")
                return

            if any(x.symbol_name == symbol for x in self.list_of_set_orders):
                print("Orders contain symbol already.")
                return

        except Exception as e:
            print(str(e) + "  Invalid Symbol.")
            return

        # Order Type
        try:
            if input_array[3] == "LIMIT":
                order_type = input_array[3]
            elif input_array == "MARKET":
                order_type = input_array[3]
            else:
                print("Invalid order type.")
                return
        except Exception as e:
            print(str(e) + "  Invalid order type.")
            return

        # Price
        if order_type == "LIMIT":
            try:
                limit_price = float(input_array[4])

                if quantity_usd <= 0:
                    print("Price less than or equal to zero.")
                    return

            except Exception as e:
                print(str(e) + "  Invalid price.")
                return

        if order_type == "LIMIT":
            # SL Symbol
            try:
                if not input_array[5] == "SL":
                    print("Stop loss not found.")
                    return
            except Exception as e:
                print(str(e) + "  Invalid stop loss symbol.")
                return

            # Stop loss price
            try:
                stop_loss_percent = float(input_array[6])

                if quantity_usd <= 0:
                    print("Price less than or equal to zero.")
                    return

            except Exception as e:
                print(str(e) + "  Invalid Stop loss price.")
                return

            # Take Profit
            try:
                if not input_array[7] == "TP":
                    print("Take profit not found.")
                    return
            except Exception as e:
                print(str(e) + "  Invalid take profit symbol.")
                return

            # Take Profit Price
            try:
                take_profit_percent = float(input_array[8])

                if quantity_usd <= 0:
                    print("Price less than or equal to zero.")
                    return

            except Exception as e:
                print(str(e) + "  Invalid take profit price.")
                return

        elif order_type == "MARKET":
            pass

        print("\n----- ORDER CREATED -----\n")

        print("\n" + buy_or_sell + " " + str(quantity_usd) + " " + symbol + " " + order_type + " " + str(limit_price) + " SL " + str(stop_loss_percent) + " TP " + str(take_profit_percent) + "\n")

        #
        if self.order_active:
            status = "PAUSED"
        else:
            status = "WAITING"

        # Create Order
        order = self.Order()
        order.stop_loss_percent = stop_loss_percent
        order.take_profit_percent = take_profit_percent
        order.stop_loss_percent /= 100
        order.take_profit_percent /= 100
        order.buy_or_sell = buy_or_sell
        order.status = status
        order.quantity_in_usd = quantity_usd
        order.limit_price = limit_price
        order.quantity_in_symbol = order.quantity_in_usd / order.limit_price
        order.symbol_name = symbol
        order.order_type = order_type
        order.stop_loss_price = limit_price - (order.limit_price * order.stop_loss_percent)
        order.take_profit_price = limit_price + (order.limit_price * order.take_profit_percent)


        # Add Order
        self.add_to_order_list(order)

    def handle_sell_input(self, input_array):
        try:
            symbol_name = input_array[1]

            if input_array[2] == "NOW":
                for order in self.list_of_set_orders:
                    if order.symbol_name == symbol_name:

                        if not order.status == "BOUGHT":
                            print("Order not active.")
                            return

                        self.market_sell(symbol_name)
                        print("Sold " + symbol_name)
                        return

        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_debug_input(self, input_array):
        if input_array[1] == "PRINTSYMBOLS":
            for s in self.symbol_manager.all_symbols:
                print(s)
            return
        print("Command not found.")

    def handle_get_input(self, input_array):
        try:
            if input_array[1] == "MISSING":
                text_file = open(sys.path[1] + "/PriceActionTrading/OrderEndless/all_symbols.txt", "r")
                lines = text_file.read().split("\n")
                text_file.close()

                for o in self.list_of_set_orders:
                    if lines.__contains__(o.symbol_name):
                        lines.remove(o.symbol_name)

                print(lines)
                return

            symbol_name = input_array[1]

            if input_array[2] == "PRICE":
                print(self.symbol_manager.get_symbol_price_with_name(symbol_name))
                return

        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_cancel_input(self, input_array):

        try:
            if input_array[1] == "ALL":
                for o in self.list_of_set_orders:
                    if not o.status == "BOUGHT":
                        self.list_of_set_orders.remove(o)
                return

            input_symbol = input_array[1]

            symbol_to_cancel = None

            for s in self.list_of_set_orders:
                if s.symbol_name == input_symbol:
                    if s.status == "BOUGHT":
                        print("Symbol already bought, cannot cancel.")
                        return

                    symbol_to_cancel = s

            self.list_of_set_orders.remove(symbol_to_cancel)

            print(input_symbol + " removed.")

        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_edit_input(self, input_array):

        try:
            input_symbol = input_array[1]

            symbol_to_edit = None

            for s in self.list_of_set_orders:
                if s.symbol_name == input_symbol:
                    symbol_to_edit = s

            def edit_take_profit():
                if input_array[2] == "TP":
                    symbol_to_edit.take_profit_percent = float(input_array[3]) / 100
                    print(symbol_to_edit.symbol_name + " take profit percent changed to " + str(float(input_array[3])))
                    return True
            if edit_take_profit():
                return

            def edit_stop_loss():
                if input_array[2] == "SL":
                    symbol_to_edit.stop_loss_percent = float(input_array[3]) / 100
                    print(symbol_to_edit.symbol_name + " stop loss percent changed to " + str(float(input_array[3])))
                    return True
            if edit_stop_loss():
                return

            def edit_usd_amount():
                if s.status == "BOUGHT":
                    print("Symbol already bought, cannot edit USD amount.")
                    return True

                if input_array[2] == "USD":
                    symbol_to_edit.quantity_in_usd = float(input_array[3])
                    print(symbol_to_edit.symbol_name + " USD amount changed to " + str(float(input_array[3])))
                    return True
            if edit_usd_amount():
                return

            def edit_limit_price():
                if s.status == "BOUGHT":
                    print("Symbol already bought, cannot edit limit price.")
                    return True

                if input_array[2] == "LIMIT":
                    symbol_to_edit.limit_price = float(input_array[3])

                    print(symbol_to_edit.symbol_name + " limit price changed to " + str(float(input_array[3])))
                    return True
            if edit_limit_price():
                return

            print("\nType help for full list of commands.")

        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_pause_input(self, input_array):
        try:
            if input_array[1] == "ALL":
                for o in self.list_of_set_orders:
                    o.status = "PAUSE"
                print("Paused all orders.")
                return

            for o in self.list_of_set_orders:
                if o.symbol_name == input_array[1]:
                    o.status = "PAUSED"

                print("Paused " + o.symbol_name)
                return

            print("\nType help for full list of commands.")

        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_start_input(self, input_array):
        try:
            for o in self.list_of_set_orders:
                if o.status == "BOUGHT":
                    print("Can't start order. A " + o.symbol_name + " order is active.")
                    return

            if input_array[1] == "ALL":
                for o in self.list_of_set_orders:
                    o.status = "WAITING"
                print("Started all orders.")
                return

            for o in self.list_of_set_orders:
                if o.symbol_name == input_array[1]:
                    o.status = "WAITING"
                    print("Started " + o.symbol_name + ".")
                    return

        except Exception as e:
            print(e)
            print("\nType help for full list of commands.")

    def handle_help_input(self, input_array):
        input_array[0] = 0
        print("BUY 250 ETH LIMIT 3.362 SL .4 TP .8")
        print("GET ETH PRICE")
        print("GET MISSING")
        print("EDIT ETH TP 1.0")
        print("EDIT ETH SL 1.0")
        print("EDIT ETH USD 1.0")
        print("EDIT ETH LIMIT 4211.25")
        print("CANCEL ETH")
        print("CANCEL ALL")
        print("PAUSE ALL")
        print("PAUSE ETH")
        print("START ALL")
        print("START ETH")
        print("SELL ETH NOW")

    # Orders
    def add_to_order_list(self, order):
        self.list_of_set_orders.append(order)

    def update_all_loop(self):
        while True:
            self.update_orders()
            self.check_for_orders()
            time.sleep(.5)

    def update_orders(self):
        nested_array = []

        for o in self.list_of_set_orders:

            current_price = self.symbol_manager.get_symbol_price_with_name(o.symbol_name)

            if o.status == "BOUGHT":
                o.pnl_percent = (current_price - o.purchase_price) / o.purchase_price
                o.pnl = (o.quantity_in_usd * o.pnl_percent)

            string_array = \
                [str(o.symbol_name),
                 str(o.status),
                 str(o.buy_or_sell),
                 str(round(current_price, 8)),
                 str(o.limit_price),
                 "$ " + str(o.quantity_in_usd),
                 str(round(o.quantity_in_symbol, 6)),
                 str(o.order_type),
                 str(round(o.purchase_price, 6)),
                 str(round(o.stop_loss_price, 6)),
                 str(round(o.stop_loss_percent * 100, 2)) + " %",
                 str(round(o.take_profit_price, 6)),
                 str(round(o.take_profit_percent * 100, 2)) + " %",
                 str(round(o.pnl_percent * 100, 2)) + " %",
                 "$ " + str(round(o.pnl, 2))
                 ]

            nested_array.append(string_array)

        display.DisplayDashTable.update_array(nested_array)

    def check_for_orders(self):

        def check_for_triggered_buy_limit_orders():
            bought_in_this_iteration = False

            for order in self.list_of_set_orders:
                if not order.status == "WAITING":
                    continue

                # If not a buy order skip
                if not order.buy_or_sell == "BUY":
                    continue

                #
                current_price = self.symbol_manager.get_symbol_price_with_name(order.symbol_name)

                #
                if current_price <= order.limit_price:

                    if current_price == 0:
                        print(" price is zero.")
                        return

                    # Get quantity
                    order.quantity_in_symbol = order.quantity_in_usd / current_price

                    if self.paper_trading:
                        order_info = self.broker.OrderInfo()
                        order_info.succeeded = True
                        order_info.price = current_price

                    else:
                        order_info = self.broker.order_send_to_broker(self.cli.client, SIDE_BUY, order.quantity_in_symbol, order.symbol_name, ORDER_TYPE_MARKET)

                    # Bought
                    if order_info.succeeded:
                        self.order_active = True
                        order.status = "BOUGHT"
                        order.purchase_price = order_info.price
                        order.stop_loss_price = order.purchase_price - (order.purchase_price * order.stop_loss_percent)
                        order.take_profit_price = order.purchase_price + (order.purchase_price * order.take_profit_percent)
                        bought_in_this_iteration = True

                        # Fee
                        self.total_pnl_percent -= self.fee
                        self.total_pnl -= self.fee * order.quantity_in_usd
                        print("Bought " + str(order.quantity_in_usd) + " of " + order.symbol_name + " at " + str(order.purchase_price))
                        break

            # Pause all other orders
            if bought_in_this_iteration:
                for order in self.list_of_set_orders:
                    if not order.status == "BOUGHT":
                        order.status = "PAUSED"
        check_for_triggered_buy_limit_orders()

        def check_for_sell():
            active_order = None  # type: OrderEndlessManager.Order

            # Get active order
            for o in self.list_of_set_orders:
                if o.status == "BOUGHT":
                    active_order = o

            # if there arent any active orders return
            if active_order is None:
                return

            # Get Current Price
            current_price = self.symbol_manager.get_symbol_price_with_name(active_order.symbol_name)

            # Check Stop Loss or Take Profit
            execute_order = False

            if active_order.pnl_percent <= -active_order.stop_loss_percent:
                execute_order = True

            if active_order.pnl_percent >= active_order.take_profit_percent:
                execute_order = True

            if not execute_order:
                return

            # if paper trading
            if self.paper_trading:
                order_info = self.broker.OrderInfo()
                order_info.succeeded = True
                order_info.price = current_price
            # if not
            else:
                # Sell
                order_info = self.broker.order_send_to_broker(self.cli.client, SIDE_SELL, active_order.quantity_in_symbol, active_order.symbol_name, ORDER_TYPE_MARKET)

            if order_info.succeeded:
                # Set profits
                difference = order_info.price - active_order.purchase_price
                percent = difference / active_order.purchase_price
                profit = active_order.quantity_in_usd * percent

                #
                self.total_pnl_percent += percent
                self.total_pnl += profit

                # Fees
                self.total_pnl_percent -= self.fee
                self.total_pnl -= active_order.quantity_in_usd * self.fee

                print("\nSold " +
                      str(active_order.quantity_in_usd) +
                      " of " + active_order.symbol_name +
                      " at price " + str(order_info.price) +
                      ". \nPurchased at " + str(active_order.purchase_price) +
                      " with a difference of " + str(difference) +
                      " (" + str(percent * 100) + " %)" +
                      "and a profit of " + str(profit))

            else:
                return

            # Delete Order From Array / Display
            self.list_of_set_orders.remove(active_order)

            #
            self.order_active = False

            # Unpause all other orders
            if not self.stay_paused_after_selling_an_order:
                for orders in self.list_of_set_orders:
                    orders.status = "WAITING"

            # Set Info
            print("TOTAL PNL  " + str(self.total_pnl))
            print("TOTAL PNL %  " + str(round(self.total_pnl_percent * 100, 4)))
        check_for_sell()

    def market_sell(self, symbol_name):
        active_order = None  # type: OrderEndlessManager.Order

        # Get active order
        for o in self.list_of_set_orders:
            if o.symbol_name == symbol_name:
                active_order = o

        # if there arent any active orders return
        if active_order is None:
            return

        current_price = self.symbol_manager.get_symbol_price_with_name(active_order.symbol_name)

        # if paper trading
        if self.paper_trading:
            order_info = self.broker.OrderInfo()
            order_info.succeeded = True
            order_info.price = current_price
        # if not
        else:
            # Sell
            order_info = self.broker.order_send_to_broker(self.cli.client, SIDE_SELL, active_order.quantity_in_symbol, active_order.symbol_name,ORDER_TYPE_MARKET)

        if order_info.succeeded:
            # Set profits
            difference = order_info.price - active_order.purchase_price
            percent = difference / active_order.purchase_price
            profit = active_order.quantity_in_usd * percent

            #
            self.total_pnl_percent += percent
            self.total_pnl += profit

            # Fees
            self.total_pnl_percent -= self.fee
            self.total_pnl -= active_order.quantity_in_usd * self.fee

            print("\nSold " +
                  str(active_order.quantity_in_usd) +
                  " of " + active_order.symbol_name +
                  " at price " + str(order_info.price) +
                  ". \nPurchased at " + str(active_order.purchase_price) +
                  " with a difference of " + str(difference) +
                  " (" + str(percent * 100) + " %)" +
                  "and a profit of " + str(profit))

        else:
            print("Order failed to sell.")
            return

        # Delete Order From Array / Display
        self.list_of_set_orders.remove(active_order)

        #
        self.order_active = False

        # Unpause all other orders
        if not self.stay_paused_after_selling_an_order:
            for orders in self.list_of_set_orders:
                orders.status = "WAITING"

        # Set Info
        print("TOTAL PNL  " + str(self.total_pnl))
        print("TOTAL PNL %  " + str(round(self.total_pnl_percent * 100, 4)))

    # TODO: WIP
    def market_buy(self, symbol_name):

        order = None

        for o in self.list_of_set_orders:
            if o.status == "BOUGHT":
                print("Cannot market buy, an order is active.")
                return

        for o in self.list_of_set_orders:
            if o.symbol_name == symbol_name:
                order = o

        current_price = self.symbol_manager.get_symbol_price_with_name(order.symbol_name)

        buy_quantity_from_usd = round(order.quantity_in_usd / current_price, 6)

        if self.paper_trading:
            order_info = self.broker.OrderInfo()
            order_info.succeeded = True
            order_info.price = current_price

        else:
            order_info = self.broker.order_send_to_broker(self.cli.client, SIDE_BUY, buy_quantity_from_usd, order.symbol_name, ORDER_TYPE_MARKET)

        # Bought
        if order_info.succeeded:
            self.order_active = True
            order.status = "BOUGHT"
            order.purchase_price = order_info.price
            order.stop_loss_price = order.purchase_price - (order.purchase_price * order.stop_loss_percent)
            order.take_profit_price = order.purchase_price + (order.purchase_price * order.take_profit_percent)

            # Fee
            self.total_pnl_percent -= self.fee
            self.total_pnl -= self.fee * order.quantity_in_usd
            print("Bought " + str(order.quantity_in_usd) + " of " + order.symbol_name + " at " + str(
                order.purchase_price))


# Start
order_endless_manager = OrderEndlessManager()
