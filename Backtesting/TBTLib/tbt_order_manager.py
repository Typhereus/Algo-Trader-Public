import sys
import Strategies.strategies as t_strategy
import TAlgoLib.t_indicators as t_indicator
import Backtesting.TBTLib.tbt_data_manager as t_data
from typing import List
import Backtesting.TBTLib.tbt_event_manager as tbt_events


class BacktestOrders:

    # Managers
    strategy = None  # type: t_strategy.Strategy
    indicators = None  # type: t_indicator.IndicatorManager
    data = None  # type: t_data.BacktestData

    #
    debugging = False
    enable_logging = None

    # Data
    the_current_price = 0.0
    the_current_time = ""

    # Order Data
    order_active = False
    orders_placed = 0

    # Fees
    total_fees_acquired = 0.0
    total_fees_percent = 0.0

    # Total Net Profit
    total_net = 0.0
    total_net_percent = 0.0

    # Current Order
    purchase_price = 0.0
    stop_loss_price = 0.0

    p_and_l = 0.0
    p_and_l_percent = 0.0

    # Gains
    gain_array = []
    successful_orders_sold = 0
    positive_gains = 0.0
    positive_percent = 0.0

    # Losses
    loss_array = []
    unsuccessful_orders_sold = 0
    negative_losses = 0.0
    negative_percent = 0.0

    # Plotting
    class ListOfOrders:
        date_time = ""
        buy = False
        sell = False
        gained_profit = False

        def __init__(self, _date_time, _buy, _sell):
            self.date_time = _date_time
            self.buy = _buy
            self.sell = _sell

    list_of_orders: List[ListOfOrders] = []

    class AdditionalPlots:
        date = ""
        trend_set = False

        def __init__(self, _trend_set, _date):
            self.trend_set = _trend_set
            self.date = _date

    additional_plots: List[AdditionalPlots] = []

    # Info Array
    tooltip_info = []

    # Trend Switch
    trend_start_set = False
    trend_end_set = False

    def __init__(self, _strategy, _data, _indicators):
        self.strategy = _strategy
        self.data = _data
        self.data.data_csv_name = self.strategy.backtesting_strategy_data
        self.indicators = _indicators
        self.data.initialize_callback(self.on_data_loop)

    def start_orders(self):
        self.data.debugging = self.debugging
        self.data.enable_logging = self.enable_logging
        self.indicators.enable_logging = self.enable_logging

        #
        self.data.start_data()
        self.data.loop_data()

    def on_data_loop(self):
        #
        tbt_events.AllBacktestEvents.on_period_begin.call()

        #
        self.set_data()

        #
        self.manager_order()

        #
        self.indicators.set_all_indicators()

        # Set info
        self.set_plot_info()

        #
        self.buy_order()

        #
        self.sell_order()

        #
        tbt_events.AllBacktestEvents.on_period_end.call()

    def set_data(self):
        # Non Order Data
        # Current Price
        self.the_current_price = self.data.current_close
        self.the_current_time = self.data.the_current_time_text

    def manager_order(self):
        # Order Data
        if not self.order_active:
            return

        # Current Price
        cp = self.data.current_close

        # Purchase Price
        pp = self.purchase_price

        #
        pd = cp - pp

        # Stop loss price
        slp = self.stop_loss_price

        # Trade Amount
        ta = self.strategy.trade_usd

        # Fee Percent
        fp = self.strategy.fee

        # Buy and Sell Fee amount
        fa = (ta * fp) * 2

        #
        # Price Difference %
        pdp = (cp - pp) / pp

        # P & L
        self.p_and_l = ta * pdp
        self.p_and_l_percent = pdp

        # P & L W/ Sell and Buy Fees
        # self.p_and_l_with_fees = (ta * pd) - fa
        # self.p_and_l_with_fees_percent = pd - fp - fp

        # P & L Stop Loss
        # P & L Stop Loss Percent Difference
        # slpd = (slp - pp) / pp
        # self.p_and_l_stop_loss = (slpd * ta) - fa - fa
        # self.p_and_l_stop_loss_percent = slpd - fp - fp

    def buy_order(self):

        if self.order_active:
            return

        if not self.strategy.buy():
            return

        #
        self.log("\n------------------------------------")

        #
        self.purchase_price = self.data.current_close

        # Total Net
        self.add_fees()

        #
        self.orders_placed += 1

        # Plot Info
        self.list_of_orders.append(self.ListOfOrders(self.data.the_current_time_text, True, False))

        #
        self.order_active = True

        # Debug
        self.log("Order Placed At " + str(self.purchase_price))
        self.log("Bought At Time: " + str(self.data.the_current_time_text))

        #
        tbt_events.AllBacktestEvents.on_order_buy_end.call()

    def sell_order(self):

        if not self.order_active:
            return

        if not self.strategy.sell():
            return

        # Set Net Profits
        self.total_net += self.p_and_l

        # Set Net Percent Profits
        self.total_net_percent += self.p_and_l_percent

        # Calculate Fees
        self.add_fees()

        #
        # print(self.p_and_l)
        if self.p_and_l_percent > 0:
            # Gain
            self.gain_array.append(self.p_and_l_percent)
            self.successful_orders_sold += 1
            self.positive_gains += self.p_and_l
            self.positive_percent += self.p_and_l_percent

            # Add To Order List
            order = self.ListOfOrders(self.data.the_current_time_text, False, True)
            order.gained_profit = True
            self.list_of_orders.append(order)

        else:
            # Loss
            # print(self.p_and_l_percent)
            self.loss_array.append(self.p_and_l_percent)
            self.unsuccessful_orders_sold += 1
            self.negative_losses += self.p_and_l
            self.negative_percent += self.p_and_l_percent

            # Add To Order List
            order = self.ListOfOrders(self.data.the_current_time_text, False, True)
            order.gained_profit = False
            self.list_of_orders.append(order)

        #
        self.order_active = False

        #
        tbt_events.AllBacktestEvents.on_order_sell_end.call()

        #
        self.close_order()

    def add_fees(self):

        # Get Fee
        fee_amount = self.strategy.trade_usd * self.strategy.fee

        # Subtract Fee From Profits
        self.total_net -= fee_amount

        # Subtract percent fee from percent profits
        self.total_net_percent -= self.strategy.fee

        # Total fees
        self.total_fees_acquired += fee_amount
        self.total_fees_percent -= self.strategy.fee

    def close_order(self):
        self.the_current_price = 0
        self.purchase_price = 0
        self.p_and_l = 0
        self.p_and_l_percent = 0
        self.stop_loss_price = 0

    def set_plot_info(self):
        # Additional Plots
        if not self.trend_start_set:
            if self.strategy.trend_started:
                self.additional_plots.append(self.AdditionalPlots(True, self.the_current_time))
                self.trend_start_set = True
                self.trend_end_set = False

        if not self.trend_end_set:
            if self.strategy.trend_ended:
                self.additional_plots.append(self.AdditionalPlots(True, self.the_current_time))
                self.trend_end_set = True
                self.trend_start_set = False

        # Tooltip
        current_string = ""
        current_string += "<br>" + str(self.data.the_current_time_text) + "</b>"
        current_string += "<br>Current Period: " + str(self.data.current_period) + "</b>"
        current_string += "<br>Close: " + str(self.data.current_close) + "</b>"
        current_string += "<br>Trend Started: " + str(self.strategy.trend_started) + "</b>"
        current_string += "<br>Bought This Trend: " + str(self.strategy.bought_this_trend) + "</b>"

        if self.order_active:
            current_string += "<br><br>Current Order </b>"
            current_string += "<br>Current P&L %: " + str(round(self.p_and_l_percent * 100, 2)) + "</b>"
            current_string += "<br>P&L SL %: " + str(round(self.strategy.pnl_stop_loss * 100, 2)) + "</b>"
            current_string += "<br>SL %: " + str(round(self.strategy.current_stop_loss_percent * 100, 2)) + "</b>"
            current_string += "<br>SL: " + str(round(self.stop_loss_price, 4)) + "</b>"



        for moving_averages in self.indicators.moving_average_all_objects:
            current_string += "<br><br>" + "MA: " + str(moving_averages.name) + " " + str(moving_averages.period) + "</b>"
            current_string += "<br>" + "Price: " + str(moving_averages.current_price) + "</b>"
            current_string += "<br>" + "Speed: " + str(moving_averages.current_speed) + "</b>"
            current_string += "<br>" + "Speed Sum: " + str(moving_averages.current_speed_sum) + "</b>"

        for adx in self.indicators.all_adx:
            current_string += "<br><br>" + "ADX " + str(adx.period) + ":  " + str(adx.get_adx(1)) + "</b>"

        for rsi in self.indicators.rsi_all:
            current_string += "<br><br>" + "RSI " + str(rsi.period) + ":  " + str(rsi.get_rsi(1)) + "</b>"

        self.tooltip_info.append(current_string)

    def log(self, logg):
        try:
            if self.enable_logging:
                file_object = open(sys.path[1] + "/Backtesting/TBTLib/tbt_order_manager_log.txt", "a+")
                logg = str(logg) + "\n"
                file_object.write(logg)
                file_object.close()

        except:
            pass

    def log_nested_dicts(self, dict_log):
        if type(dict_log) is dict:
            for key in dict_log:
                if type(dict_log[key]) is dict or type(dict_log[key]) is list:
                    for key2 in dict_log[key]:
                        self.log((str(key2) + " : " + str(dict_log[key][key2]) + "\n"))
                else:
                    self.log((str(key) + " : " + str(dict_log[key]) + "\n"))
