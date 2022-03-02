import Backtesting.TBTLib.tbt_engine as tbt_engine
import sys
import Backtesting.TBTLib.tbt_event_manager as all_events
from Debug.better_printer import *


class BacktestAuditor:
    engine = None  # type: tbt_engine.BacktestEngine

    enable_logging = True

    def __init__(self, _engine):
        self.engine = _engine
        self.set_all_events()

    def set_all_events(self):
        all_events.AllBacktestEvents.on_order_sell_end.add_subscriber(self.log_sell_order)
        all_events.AllBacktestEvents.on_order_buy_end.add_subscriber(self.log_buy_order)
        # all_events.AllEvents.on_period_begin.add_subscriber(self.print_period_end)

    def write_results_to_text_file(self):
        # Strategy
        strategy_print_out = self.engine.strategy.get_print_out()

        # Indicators
        indicator_print_out = self.engine.indicators.get_backtest_indicator_print_out()

        #
        how_many_days = len(self.engine.orders.data.all_close) / 60 / 24

        #
        net_orders = self.engine.orders.successful_orders_sold - self.engine.orders.unsuccessful_orders_sold

        #
        order_ratio = 0
        if self.engine.orders.successful_orders_sold > 0 and self.engine.orders.unsuccessful_orders_sold > 0:
            order_ratio = self.engine.orders.successful_orders_sold / -self.engine.orders.unsuccessful_orders_sold

        #
        if not self.engine.orders.total_net == 0:
            net_profit_to_success_ratio = order_ratio / self.engine.orders.total_net

        #
        risk_reward_ratio = 0
        if self.engine.orders.positive_gains > 0:
            risk_reward_ratio = round((self.engine.orders.positive_gains / abs(
                (self.engine.orders.negative_losses - self.engine.orders.total_fees_acquired))), 2)

        #
        total_net_profit_loss = 0.0
        if not self.engine.orders.total_net == 0:
            total_net_profit_loss = round(self.engine.orders.total_net / how_many_days, 4)

        #
        total_net_percent_day = 0.0
        if not self.engine.orders.total_net == 0:
            total_net_percent_day = round((self.engine.orders.total_net_percent / how_many_days) * 100, 4)

        #
        orders_day = 0.0
        if self.engine.orders.orders_placed > 0 and how_many_days > 0:
            orders_day = self.engine.orders.orders_placed / how_many_days

        # Gain Average
        gain_average_str = "0"
        if len(self.engine.orders.gain_array) > 0:
            gain_average_str = str(round(sum(self.engine.orders.gain_array) / len(self.engine.orders.gain_array) * 100, 2))

        # Loss Average
        loss_array_string = "0"
        if len(self.engine.orders.loss_array) > 0:
            loss_array = self.engine.orders.loss_array
            loss_array_average = sum(loss_array) / len(loss_array)
            loss_array_rounded = round(loss_array_average, 2) * 100
            loss_array_string = str(loss_array_rounded)

        #
        all_results = strategy_print_out + indicator_print_out \
                      + "\nOrders Placed: {}".format(self.engine.orders.orders_placed) + "\n" \
                      + "----------------------------------------------------------------------------------------\n" \
                      + "Total Net Profits: $ {}".format(round(self.engine.orders.total_net, 2)) + "\n" \
                      + "Total Net Percent Gains: {} %".format(
                        round(self.engine.orders.total_net_percent * 100, 4)) + "\n" \
                      + "Total Net Profits A Day: $ {}".format(total_net_profit_loss) + "\n" \
                      + "Total Net Percent A Day: {} %".format(total_net_percent_day) + "\n" \
                      + "----------------------------------------------------------------------------------------\n" \
                      + "Positive Percent Gains: {} %".format(
                        round(self.engine.orders.positive_percent * 100, 4)) + " (AVG " + gain_average_str + " %)\n" \
                      + "Negative Percent Losses: {} %".format(
                        round(self.engine.orders.negative_percent * 100, 4)) + " (AVG " + loss_array_string + " %)\n" \
                      + "Positive Profits: $ {}".format(round(self.engine.orders.positive_gains, 4)) + "\n" \
                      + "Negative Losses: $ {}".format(round(self.engine.orders.negative_losses, 4)) + "\n" \
                      + "Total Fees: $ {}".format(round(self.engine.orders.total_fees_acquired, 4)) + "\n" \
                      + "Total Fees %: {} %".format(round(self.engine.orders.total_fees_percent * 100, 4)) + "\n" \
                      + "Successful Orders: {}".format(self.engine.orders.successful_orders_sold) + "\n" \
                      + "Unsuccessful Orders: {} ".format(self.engine.orders.unsuccessful_orders_sold) + "\n" \
                      + "Risk Reward Ratio: {} : 1".format(risk_reward_ratio) + "\n" \
                      + "Days Passed: {}".format(how_many_days) + "\n" \
                      + "Net Orders: {}".format(net_orders) + "\n" \
                      + "Orders A Day (AVG): {}".format(orders_day) + "\n" \
                      + "------------------------------------------------------------------------------------------" \
                      + "\n\n\n\n\n\n"

        self.log(all_results)

        print(all_results)

    def log_sell_order(self):
        self.engine.orders.log("\n\n\n BUY: \n")
        self.engine.orders.log_nested_dicts(vars(self.engine.orders))
        self.engine.orders.log("\n\n\n")

    def log_buy_order(self):
        self.engine.orders.log("\n\n\n SELL: \n")
        self.engine.orders.log_nested_dicts(vars(self.engine.orders))
        self.engine.orders.log("\n\n\n")

    def print_buy_order(self):
        bprint("Buy: Price",
               self.engine.orders.the_current_price,
               " Time: ",
               self.engine.orders.the_current_time,
               " MA SPEED SUM: ",
               self.engine.indicators.get_ma_speed_sum("200", 1))

    def print_period_end(self):
        bprint(self.engine.data.current_period,
               self.engine.orders.the_current_time,
               # round(self.engine.indicators.get_moving_average_price("200", 3), 2),
               # round(self.engine.indicators.get_moving_average_price("200", 2), 2),
               # round(self.engine.indicators.get_moving_average_price("200", 1), 2),
               "C:",
               round(self.engine.data.current_close, 2),
               "200 MA:",
               round(self.engine.indicators.get_moving_average_price("200"), 2),
               round(self.engine.indicators.get_ma_speed("200", 1), 2),
               round(self.engine.indicators.get_ma_speed_sum("200", 1), 2))

    def log(self, logg):
        try:
            file_object = open(sys.path[1] + "/Backtesting/TBTLib/tbt_backtest_results_log.txt", "a+")
            logg = str(logg) + "\n"
            file_object.write(logg)
            file_object.close()
        except:
            pass

    def debug_log(self, logg):
        try:
            if self.enable_logging:
                file_object = open(sys.path[1] + "/Backtesting/tbt_auditor_log.txt", "a+")
                logg = str(logg) + "\n"
                file_object.write(logg)
                file_object.close()
        except:
            pass
