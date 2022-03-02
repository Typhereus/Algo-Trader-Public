import time
from binance.enums import *
import json
import TTraderLib.t_client_manager as client_mgmt
import TTraderLib.t_websocket_manager as websocket_mgmt
import TTraderLib.t_data_manager as data_mgmt
import TTraderLib.t_event_manager as events
import TAlgoLib.t_indicators as indicator_mgmt
import sys
from tabulate import tabulate
import Strategies.strategies as strategy


class OrderManager:
    # TODO: Short Order History
    client_manager = None  # type: client_mgmt.ClientManager
    data_manager = None  # type: data_mgmt.DataManager
    indicator_manager = None  # type: indicator_mgmt.IndicatorManager
    strategy = None  # type: strategy.Strategy

    # Websocket
    websocket_manager = websocket_mgmt.WebsocketManager()
    websocket_message = {}

    period = 0

    the_current_price = 0.0

    # Orders
    stop_loss_price = 0.0
    anchor_price = 0.0

    order_active = False

    net_profit = 0.0
    net_percent = 0.0

    successful_buy_orders = 0
    successful_sell_orders = 0

    failed_buy_orders = 0
    failed_sell_orders = 0

    # Current order
    purchase_price = 0.0
    quantity_purchased = 0.0

    p_and_l = 0.0
    p_and_l_percent = 0.0

    p_and_l_stop_loss = 0.0
    p_and_l_stop_loss_percent = 0.0

    p_and_l_with_fees = 0.0
    p_and_l_with_fees_percent = 0.0

    order_manager_enabled = True

    # Kill Switch
    kill_switch_triggered = False

    # Debug
    debug_current_price = 0.0

    launch_wait_period = 0
    launch_wait_period_requirement = 0

    def start_order_manager(self, _strategy, _data_manager, _indicator_manager, _client_manager):
        self.data_manager = _data_manager
        self.strategy = _strategy
        self.indicator_manager = _indicator_manager
        self.indicator_manager.set_historical()
        self.client_manager = _client_manager
        self.websocket_manager.start_websocket_manager(self.strategy.trade_symbol, self.set_message)
        self.start_loop()

    def start_loop(self):
        while self.order_manager_enabled:
            time.sleep(1)
            if self.websocket_message:
                self.prospect_message()
            else:
                print("Websocket Message Empty")
        else:
            if self.kill_switch_triggered:
                print("\n\n\n\n\n\n")
                print("KILL SWITCH ENABLED! LOST: " + str(self.p_and_l_percent))
                # TODO: Sell all
                print("\n\n\n\n\n\n")

    def set_message(self, message):

        json_message = json.loads(message)

        raw_candle_data = json_message['k']

        self.websocket_message = raw_candle_data

    def prospect_message(self):
        # Set Current Price
        self.the_current_price = float(self.websocket_message['c'])

        # Debug
        # self.indicator_manager.debug_sum += .1
        if self.order_active:
            # self.debug_current_price += 1
            # self.the_current_price = self.the_current_price - self.debug_current_price
            pass

        # On Close
        if self.websocket_message['x']:
            self.period += 1
            self.data_manager.get_current_candle_with_history()
            self.indicator_manager.set_all_indicators()
            self.launch_wait_period += 1
            events.AllTraderEvents.on_period_end.call()

        # Buy
        if not self.order_active:
            if self.strategy.buy_now or self.strategy.buy():
                self.strategy.buy_now = False
                self.buy_order()

        # Sell
        if self.order_active:
            if self.strategy.sell() or self.p_and_l_percent < self.strategy.killswitch_pnl_threshold:
                self.sell_order()

        self.set_order_info()

        self.print_order_info()

    def set_order_info(self):
        if self.order_active and self.stop_loss_price > 0 and self.purchase_price > 0:
            # Stop loss price
            slp = self.stop_loss_price

            # Trade Amount
            ta = self.strategy.trade_usd

            # Current Price
            cp = self.the_current_price

            # Purchase Price
            pp = self.purchase_price

            # Fee Percent
            fp = self.strategy.fee

            # Buy and Sell Fee amount
            fa = (ta * fp) * 2

            #
            # Price Difference %
            pd = (cp - pp) / pp

            # P & L
            self.p_and_l = ta * pd
            self.p_and_l_percent = pd

            # P & L W/ Sell and Buy Fees
            self.p_and_l_with_fees = (ta * pd) - fa
            self.p_and_l_with_fees_percent = pd - fp - fp

            # P & L Stop Loss
            # P & L Stop Loss Percent Difference
            slpd = (slp - pp) / pp
            self.p_and_l_stop_loss = (slpd * ta) - fa - fa
            self.p_and_l_stop_loss_percent = slpd - fp - fp

    def print_order_info(self):

        print("Prospecting " + self.strategy.trade_symbol + " With $ " + str(self.strategy.trade_usd))
        print("Connection Active: " + str(self.websocket_manager.connection_active))
        print("Periods Passed: {}".format(self.period))
        print("Time: {}".format(self.data_manager.the_current_time))
        print("\n")
        print(tabulate([[str(self.successful_buy_orders), self.successful_sell_orders, self.failed_buy_orders,
                         self.failed_sell_orders]],
                       headers=["Successful Buy Orders", "Successful Sell Orders", "Failed Buy Orders",
                                "Failed Sell Orders"],
                       tablefmt='plain', stralign="left", numalign="left"))
        print("\n")
        print("Total Net Profit: $ {}".format(round(self.net_profit, 2)))
        print("Total Net Percent: {} %".format(round(self.net_percent * 100, 4)))
        print("\n")

        print(tabulate([[self.strategy.buy(), self.strategy.sell()]],
                       headers=['Buy Condition', 'Sell Condition'],
                       tablefmt="plain", stralign="left", numalign="left"))

        print("\n")
        print("Order Active: {}".format(self.order_active))
        print("\n")

        #
        stop_loss_percent_for_printing = round(self.strategy.current_stop_loss_percent, 4)
        base_stop_loss_price_for_printing = round(self.strategy.base_stop_loss_price)
        print(tabulate([[self.the_current_price,
                         self.purchase_price,
                         round(self.stop_loss_price, 4),
                         base_stop_loss_price_for_printing,
                         stop_loss_percent_for_printing,
                         self.quantity_purchased]],
                       headers=['Current Price', 'Purchase Price', 'Stop Loss Price', 'Base Stop Loss Price', 'Stop Loss %', 'Purchase Amount'],
                       tablefmt="plain", stralign="left", numalign="left"))
        print("\n")

        #
        pl = round(self.p_and_l, 2)
        plp = round(self.p_and_l_percent * 100, 4)
        plf = round(self.p_and_l_with_fees, 2)
        plpf = round(self.p_and_l_with_fees_percent * 100, 4)
        plsl = round(self.p_and_l_stop_loss, 2)
        plpsl = round(self.p_and_l_stop_loss_percent * 100, 4)

        print(tabulate([[pl, plp, plf, plpf, plsl, plpsl]],
                       headers=["P&L $", "P&L %", "P&L Fee", "P&L Fee %", "P&L SL", "P&L SL %"],
                       tablefmt='plain', stralign="left", numalign="left"))

        print("\n")
        print("Last Close: {} ".format(self.data_manager.last_close_price))

        print(self.indicator_manager.get_trader_indicator_print_out())

        print("\n\n\n")

    # Order
    def order_send_to_broker(self, side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
        log("Ordering")
        try:
            log("Sending order")

            place_order = self.client_manager.client.create_order(symbol=symbol, side=side, type=order_type,
                                                                  quantity=quantity)
            order_data = place_order['fills']
            result = str(place_order)

            if side == SIDE_BUY:
                self.purchase_price = float(order_data[0]['price'])
                log("Bought at: " + str(self.purchase_price) + " " + str(self.data_manager.the_current_time))

            if side == SIDE_SELL:
                log("Sold at: " + str(float(order_data[0]['price'])) + " " + str(self.data_manager.the_current_time))

            log("Order Result: {}".format(result))

        except Exception as e:
            log("an exception occurred in order sent to broker - {}".format(e))
            return False

        return True

    def buy_order(self):

        if self.launch_wait_period < self.launch_wait_period_requirement:
            return

        self.quantity_purchased = round(self.strategy.trade_usd / self.the_current_price, 4)

        log("Buy: Trying to buy: " + str(self.quantity_purchased) + str(self.strategy.trade_symbol))

        if not self.strategy.fake_order:
            order_succeeded = self.order_send_to_broker(SIDE_BUY, self.quantity_purchased, self.strategy.trade_symbol)

        else:
            order_succeeded = True
            self.purchase_price = self.the_current_price

        #
        if order_succeeded:

            log("Buy at: " + str(self.purchase_price) + " " + str(self.data_manager.the_current_time))

            self.successful_buy_orders += 1

            self.net_profit -= self.strategy.fee * self.strategy.trade_usd
            self.net_percent -= self.strategy.fee

            self.order_active = True

            #
            log_nested_dicts(vars(self))

            # self.strategy.on_order_buy()

            events.AllTraderEvents.on_order_buy_end.call()

        else:
            log("Buy Order Failed" + str(self.data_manager.the_current_time))
            self.failed_buy_orders += 1

    def sell_order(self):
        # Stop loss check
        # Fake or real order
        if not self.strategy.fake_order:
            log("Sell Not Fake")
            order_succeeded = self.order_send_to_broker(SIDE_SELL, self.quantity_purchased,
                                                        self.strategy.trade_symbol)
        else:
            # Fake
            order_succeeded = True

        # Succeeded
        if order_succeeded:

            self.successful_sell_orders += 1

            self.order_active = False

            # Sell fee
            self.net_profit -= self.strategy.fee * self.strategy.trade_usd
            self.net_percent -= self.strategy.fee

            # Profit
            current_order_percent_difference = (self.the_current_price - self.purchase_price) / self.purchase_price

            p_and_l = current_order_percent_difference * self.strategy.trade_usd

            self.net_profit += p_and_l
            self.net_percent += current_order_percent_difference

            #
            log_nested_dicts(vars(self))

            #
            events.AllTraderEvents.on_order_sell_end.call()

            #
            self.close_order_clean_up()

            #
            self.check_for_kill_switch()

        else:
            self.failed_sell_orders += 1
            log("Sell Order Failed " + str(self.data_manager.the_current_time))

    def close_order_clean_up(self):
        self.purchase_price = 0
        self.stop_loss_price = 0
        self.quantity_purchased = 0
        self.p_and_l_stop_loss_percent = 0
        self.p_and_l = 0
        self.p_and_l_percent = 0
        self.p_and_l_with_fees = 0
        self.p_and_l_with_fees_percent = 0
        self.p_and_l_stop_loss = 0
        self.p_and_l_stop_loss_percent = 0

        # Debug
        self.debug_current_price = 0

    def check_for_kill_switch(self):
        if self.net_percent < self.strategy.killswitch_pnl_threshold:
            self.order_manager_enabled = False
            self.kill_switch_triggered = True


def log_nested_dicts(dict_log):
    for key in dict_log:
        if type(dict_log[key]) is dict or type(dict_log[key]) is list:
            for key2 in dict_log[key]:
                log_one((str(key2) + " : " + str(dict_log[key][key2]) + "\n"))
        else:
            log((str(key) + " : " + str(dict_log[key]) + "\n"))


def log_one(one_log):
    try:
        file_object = open(sys.path[1] + "/TTraderLib/t_order_manager_log.txt", "a+")
        one_log = str(one_log) + "\n"
        file_object.write(one_log)
        file_object.close()
    except:
        pass


def log(*logs):
    try:
        all_logs_string = ""

        for l in logs:
            all_logs_string += str(l) + " "

        file_object = open(sys.path[1] + "/TTraderLib/t_order_manager_log.txt", "a+")

        all_logs_string += "\n"

        file_object.write(all_logs_string)

        file_object.close()

    except Exception as e:
        print("LOG ERROR: " + str(e))
