import Backtesting.TBTLib.tbt_data_manager as t_data
import Backtesting.TBTLib.tbt_order_manager as t_orders
import Backtesting.TBTLib.tbt_event_manager as backtest_events
import TAlgoLib.t_indicators as t_indicators
import TTraderLib.t_event_manager as trader_events
from enum import Enum
import sys


class Strategy:

    class StrategyType(Enum):
        TRADER = 0
        BACKTEST = 1

    #
    strategy_name = ""
    print_log_notes = "Note: "

    # Backtesting
    backtesting_strategy_data = ""

    #
    strategy_type = None  # type: StrategyType

    #
    enable_strategy_logging = None

    # Managers
    indicators = None  # type: t_indicators.IndicatorManager
    data = None  # type: t_data.BacktestData
    orders = None  # type: t_orders.BacktestOrders

    #
    trade_symbol = ""  # "ETHUSDT"
    trade_usd = 0  # 250
    fee = 0.0  # .001

    #
    buy_now = False
    fake_order = True

    # Stop Loss
    stop_loss_percent = 0.0
    base_stop_percent = 0.0
    base_stop_loss_price = 0.0
    current_stop_loss_percent = 0.0


    # Buy Speed
    sum_array = []
    buy_speed_sum_requirement = 4
    buy_speed_periods = 1

    # Sell
    sell_speed_min = .1

    # Trend
    trend_started = False
    trend_ended = True
    trend_set = False
    bought_this_trend = False
    trend_end_speed_requirement = 0

    #
    wait_periods_before_buying_again = 0
    current_wait_period = 0

    killswitch_pnl_threshold = -.025

    # PNL Trail
    pnl_stop_loss = 0
    pnl_stop_loss_percent = 0.0
    pnl_trail_up_triggered = False
    pnl_proportion = .5


    def __init__(self):
        self.strategy_name = self.strategy_name
        self.print_log_notes = self.print_log_notes

    def on_sell_end(self):
        pass

    def on_buy_end(self):
        pass

    def on_end_period(self):
        self.pnl_trail_up_triggered = False

    def buy(self):
        self.log("Buy")
        pass

    def sell(self):
        self.log("Sell")
        pass

    def add_indicators(self):
        self.log("Added indicators")
        pass

    def start_strategy(self, _strategy_type, _data_manager, _indicator_manager, _orders):
        self.strategy_type = _strategy_type
        self.data = _data_manager
        self.indicators = _indicator_manager
        self.orders = _orders
        self.add_indicators()
        self.set_events()

    def set_events(self):
        if self.strategy_type == self.StrategyType.BACKTEST:
            backtest_events.AllBacktestEvents.on_order_buy_end.add_subscriber(self.on_buy_end)
            backtest_events.AllBacktestEvents.on_order_sell_end.add_subscriber(self.on_sell_end)
            backtest_events.AllBacktestEvents.on_period_end.add_subscriber(self.on_end_period)

        if self.strategy_type == self.StrategyType.TRADER:
            trader_events.AllTraderEvents.on_order_buy_end.add_subscriber(self.on_buy_end)
            trader_events.AllTraderEvents.on_order_sell_end.add_subscriber(self.on_sell_end)
            trader_events.AllTraderEvents.on_period_end.add_subscriber(self.on_end_period)

    def log(self, *logg):
        try:
            if self.enable_strategy_logging:
                file_object = open(sys.path[1] + "/Strategies/strategy_log.txt", "a+")
                all_logs = ""

                for l in logg:
                    all_logs += str(l) + " "

                all_logs += "\n"
                file_object.write(all_logs)
                file_object.close()

        except:
            pass

    def get_print_out(self):
        dict_log = vars(self)

        all_str = "\n\nSTRATEGY: \n"

        if type(dict_log) is dict:
            for key in dict_log:
                if type(dict_log[key]) is dict or type(dict_log[key]) is list:
                    for key2 in dict_log[key]:
                        all_str += str(key2) + " : " + str(dict_log[key][key2]) + "\n"
                else:
                    all_str += str(key) + " : " + str(dict_log[key]) + "\n"
        return all_str


class PNLTrailNew(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "PNL Trail New November 2021"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .01
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0
        self.killswitch_pnl_threshold = -.03

        # Buy
        self.buy_speed_periods = 1
        self.buy_speed_sum_requirement = .4
        self.pnl_proportion = .01

        # Trend
        self.trend_end_speed_requirement = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Sell", 25, 2)
        self.indicators.add_moving_average("Buy", 400, 2)
        self.indicators.add_moving_average("Trend", 500, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        # If Order Is Active
        if self.orders.order_active:
            return False

        # Buy
        def ma_speed_buy():
            speed_sum = 0

            for i in range(self.buy_speed_periods):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Buy", index))

            if speed_sum > self.buy_speed_sum_requirement:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy Backtesting
        def bt_ignore_first_periods():
            if self.strategy_type == Strategy.StrategyType.BACKTEST:
                 return self.data.current_period > 2000
            else:
                return True
        ignore_first_periods = bt_ignore_first_periods()

        # Buy
        def all_conditions():
            if not self.bought_this_trend:
                if buy_ma_speed_condition and ignore_first_periods:
                    self.bought_this_trend = True
                    return True
            else:
                # Buy Rsi if In Trend
                return self.indicators.get_rsi(120, 1) < 35

        return all_conditions()

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():

            base_stop = -.01
            first_level = 0.005
            second_level = .02
            third_level = .04

            # First Trail
            if first_level <= self.orders.p_and_l_percent < second_level:
                self.pnl_trail_up_triggered = True

                if self.pnl_stop_loss < self.orders.p_and_l_percent * self.pnl_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * self.pnl_proportion

            # Second - if greater than this amount reduce pnl trail propotion even further
            if self.orders.p_and_l_percent >= second_level:

                self.pnl_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * self.pnl_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * self.pnl_proportion

            # Third - if greater than this amount reduce pnl trail propotion even further
            if self.orders.p_and_l_percent >= third_level:

                self.pnl_proportion = .9
                if self.pnl_stop_loss < self.orders.p_and_l_percent * self.pnl_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * self.pnl_proportion

            if self.pnl_trail_up_triggered:
                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # Base Stop
            if self.orders.p_and_l_percent <= base_stop:
                return True

            return False
        pnl_condition = pnl_stop_loss()

        def sell_trailing_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Sell", 1)

            self.stop_loss_percent = .0025

            self.current_stop_loss_percent = self.stop_loss_percent

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        trailing_stop_loss_condition = sell_trailing_stop_loss_condition()

        # Sell Conditions
        if pnl_condition:
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.set_trend()

    def set_trend(self):
        # Start Trend
        """
        if self.trend_ended and not self.trend_started:
            buy_speed_sum = 0
            for i in range(self.buy_speed_periods):
                index = i + 1
                buy_speed_sum += float(self.indicators.get_ma_speed("Buy", index))

            if buy_speed_sum > self.buy_speed_sum_requirement:
                self.trend_started = True
                #print("TREND STARTED " + str(self.data.the_current_time_text))
        """

        # End Trend
        end_trend_speed_sum = 0
        end_trend_periods = 1

        for i in range(end_trend_periods):
            index = i + 1
            end_trend_speed_sum += float(self.indicators.get_ma_speed("Buy", index))

        if end_trend_speed_sum < self.trend_end_speed_requirement:
            self.bought_this_trend = False

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.pnl_trail_up_triggered = False


class RSIPnl(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "PNL Trail New November 2021"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .01
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0
        self.killswitch_pnl_threshold = -.03

        # Buy
        self.buy_speed_periods = 1
        self.buy_speed_sum_requirement = .6
        self.pnl_proportion = .01

        # Trend
        self.trend_end_speed_requirement = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Sell", 25, 2)
        self.indicators.add_moving_average("Buy", 200, 2)
        self.indicators.add_moving_average("Trend", 500, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        # If Order Is Active
        if self.orders.order_active:
            return False

        # Buy Backtesting
        def bt_ignore_first_periods():
            if self.strategy_type == Strategy.StrategyType.BACKTEST:
                 return self.data.current_period > 2000
            else:
                return True
        ignore_first_periods = bt_ignore_first_periods()

        # Buy Rsi
        rsi_condition = self.indicators.get_rsi(120, 1) < 25

        # Buy
        all_conditions = rsi_condition and \
                            ignore_first_periods #and \
                            #not self.bought_this_trend

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():

            base_stop = -.01
            first_level = 0.005
            second_level = .02
            third_level = .04

            # First Trail
            if first_level <= self.orders.p_and_l_percent < second_level:
                self.pnl_trail_up_triggered = True

                if self.pnl_stop_loss < self.orders.p_and_l_percent * self.pnl_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * self.pnl_proportion

            # Second - if greater than this amount reduce pnl trail propotion even further
            if self.orders.p_and_l_percent >= second_level:

                self.pnl_proportion = .75
                if self.pnl_stop_loss < self.orders.p_and_l_percent * self.pnl_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * self.pnl_proportion

            # Third - if greater than this amount reduce pnl trail propotion even further
            if self.orders.p_and_l_percent >= third_level:

                self.pnl_proportion = .9
                if self.pnl_stop_loss < self.orders.p_and_l_percent * self.pnl_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * self.pnl_proportion

            if self.pnl_trail_up_triggered:
                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # Base Stop
            if self.orders.p_and_l_percent <= base_stop:
                return True

            return False
        pnl_condition = pnl_stop_loss()

        def sell_trailing_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Sell", 1)

            self.stop_loss_percent = .0025

            self.current_stop_loss_percent = self.stop_loss_percent

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        trailing_stop_loss_condition = sell_trailing_stop_loss_condition()

        # Sell Conditions
        if trailing_stop_loss_condition:
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.set_trend()

    def set_trend(self):
        # Start Trend
        if self.trend_ended and not self.trend_started:
            buy_speed_sum = 0
            for i in range(self.buy_speed_periods):
                index = i + 1
                buy_speed_sum += float(self.indicators.get_ma_speed("Buy", index))

            if buy_speed_sum > self.buy_speed_sum_requirement:
                self.trend_started = True
                self.trend_ended = False
                #print("TREND STARTED " + str(self.data.the_current_time_text))

        # End Trend
        if self.trend_started:
            end_trend_speed_sum = 0
            end_trend_periods = 1

            for i in range(end_trend_periods):
                index = i + 1
                end_trend_speed_sum += float(self.indicators.get_ma_speed("Buy", index))

            if end_trend_speed_sum < self.trend_end_speed_requirement:
                #print("TREND ENDED " + str(self.data.the_current_time_text))
                self.trend_started = False
                self.trend_ended = True
                self.bought_this_trend = False

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.pnl_trail_up_triggered = False


class PNLTrail(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0
        self.killswitch_pnl_threshold = -.03

    def add_indicators(self):
        self.indicators.add_moving_average("Sell_MA", 75, 2)
        self.indicators.add_moving_average("Large", 200, 2)
        self.indicators.add_moving_average("Trend", 300, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Large", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 1

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum > 1:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        rsi_condition = 40 > self.indicators.get_rsi(120, 1) > 0

        # Backtesting
        def bt_ignore_first_periods():
            if self.strategy_type == Strategy.StrategyType.BACKTEST:
                 return self.data.current_period > 2000
            else:
                return True
        ignore_first_periods = bt_ignore_first_periods()

        # ADX
        adx_condition = self.indicators.get_adx(120, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                            wait_period_condition and \
                            ignore_first_periods and \
                            not self.bought_this_trend # and \
                            #  buy_stayed_position_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():
            if .01 < self.orders.p_and_l_percent < .05:
                self.pnl_trail_up_triggered = True

                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # if greater than 5% reduce pnl trail
            if self.orders.p_and_l_percent >= .05:

                pnl_stop_proportion = .85
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # Base Stop
            if self.orders.p_and_l_percent <= -.025:
                return True

            """
            if self.pnl_trail_up_triggered:
                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            """
            return False
        pnl_condition = pnl_stop_loss()

        # Basic Stop Loss
        basic_stop_loss = self.orders.p_and_l_percent < -.04

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Sell_MA", 1)

            self.stop_loss_percent = .0025

            self.current_stop_loss_percent = self.stop_loss_percent

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        stop_loss_condition = sell_stop_loss_condition()

        # Sell MA Speed
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum < -.6:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if pnl_condition: #or basic_stop_loss:  # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.set_trend()

    def set_trend(self):
        speed_sum = 0
        periods_to_check = 1

        for i in range(periods_to_check):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Trend", index))

        if speed_sum > 1:
            self.trend_started = True

        if speed_sum < 0:
            self.trend_started = False
            self.bought_this_trend = False

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0


class PNLTrail23(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS-Y.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0
        self.killswitch_pnl_threshold = -.03

    def add_indicators(self):
        self.indicators.add_moving_average("Sell_MA", 75, 2)
        self.indicators.add_moving_average("Large", 200, 2)
        self.indicators.add_moving_average("Trend", 300, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Large", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 1

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum > 1:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        rsi_condition = 40 > self.indicators.get_rsi(120, 1) > 0

        # Backtesting
        def bt_ignore_first_periods():
            if self.strategy_type == Strategy.StrategyType.BACKTEST:
                 return self.data.current_period > 2000
            else:
                return True
        ignore_first_periods = bt_ignore_first_periods()

        # ADX
        adx_condition = self.indicators.get_adx(120, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                            wait_period_condition and \
                            ignore_first_periods and \
                            not self.bought_this_trend # and \
                            #  buy_stayed_position_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():
            if .01 < self.orders.p_and_l_percent < .05:
                self.pnl_trail_up_triggered = True

                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # if greater than 5% reduce pnl trail
            if self.orders.p_and_l_percent >= .05:

                pnl_stop_proportion = .85
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # Base Stop
            if self.orders.p_and_l_percent <= -.025:
                return True

            """
            if self.pnl_trail_up_triggered:
                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            """
            return False
        pnl_condition = pnl_stop_loss()

        # Basic Stop Loss
        basic_stop_loss = self.orders.p_and_l_percent < -.04

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Sell_MA", 1)

            self.stop_loss_percent = .0025

            self.current_stop_loss_percent = self.stop_loss_percent

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        stop_loss_condition = sell_stop_loss_condition()

        # Sell MA Speed
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum < -.6:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if pnl_condition: #or basic_stop_loss:  # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.set_trend()

    def set_trend(self):
        speed_sum = 0
        periods_to_check = 1

        for i in range(periods_to_check):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Trend", index))

        if speed_sum > 1:
            self.trend_started = True

        if speed_sum < 0:
            self.trend_started = False
            self.bought_this_trend = False

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0


class PNLTrailWhopping23Percent(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0
        self.killswitch_pnl_threshold = -.03

    def add_indicators(self):
        self.indicators.add_moving_average("Sell_MA", 75, 2)
        self.indicators.add_moving_average("Large", 200, 2)
        self.indicators.add_moving_average("Trend", 300, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Large", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 1

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum > 1:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        rsi_condition = 40 > self.indicators.get_rsi(120, 1) > 0

        # Backtesting
        def bt_ignore_first_periods():
            if self.strategy_type == Strategy.StrategyType.BACKTEST:
                 return self.data.current_period > 2000
            else:
                return True
        ignore_first_periods = bt_ignore_first_periods()

        # ADX
        adx_condition = self.indicators.get_adx(120, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                            wait_period_condition and \
                            ignore_first_periods and \
                            not self.bought_this_trend # and \
                            #  buy_stayed_position_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():
            if .01 < self.orders.p_and_l_percent < .05:
                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # if greater than 5% reduce pnl trail
            if self.orders.p_and_l_percent >= .05:
                pnl_stop_proportion = .85
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True

            # Base Stop
            if self.orders.p_and_l_percent <= -.025:
                return True
            return False
        pnl_condition = pnl_stop_loss()

        # Basic Stop Loss
        basic_stop_loss = self.orders.p_and_l_percent < -.04

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Sell_MA", 1)

            self.stop_loss_percent = .0025

            self.current_stop_loss_percent = self.stop_loss_percent

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        stop_loss_condition = sell_stop_loss_condition()

        # Sell MA Speed
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum < -.6:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if pnl_condition: #or basic_stop_loss:  # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.set_trend()

    def set_trend(self):
        speed_sum = 0
        periods_to_check = 1

        for i in range(periods_to_check):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Trend", index))

        if speed_sum > 1:
            self.trend_started = True

        if speed_sum < 0:
            self.trend_started = False
            self.bought_this_trend = False

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0


class MASpeedStrategy(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Sell MA", 50, 2)
        # self.indicators.add_moving_average("Buy MA", 120, 2)
        self.indicators.add_moving_average("Large", 120, 2)
        self.indicators.add_moving_average("Mega", 960, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        """
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Buy MA", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()
        """

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 1

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            # TODO: if downtrending... use larger
            if speed_sum > 1:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        rsi_condition = 40 > self.indicators.get_rsi(120, 1) > 0

        # Backtesting
        if self.strategy_type == Strategy.StrategyType.BACKTEST:
            ignore_first_periods = self.data.current_period > 2000
        else:
            return True

        # Mega not negative
        mega_condition = self.indicators.get_ma_speed("Mega", 1) > .15

        # ADX
        adx_condition = self.indicators.get_adx(120, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                         wait_period_condition and \
                         ignore_first_periods and \
                         rsi_condition # and \
                         # adx_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():
            self.decrease_stop_loss_percent_by_pnl_threshold = .01

            if self.orders.p_and_l_percent > .005:
                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            elif self.orders.p_and_l_percent < -.005:
                return True
        pnl_condition = pnl_stop_loss()

        # Basic Stop Loss
        basic_stop_loss = self.orders.p_and_l_percent < -.04

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Large", 1)

            self.stop_loss_percent = .02

            self.current_stop_loss_percent = self.stop_loss_percent

            if self.indicators.get_ma_speed("Large", 1) < .5:
                self.current_stop_loss_percent = self.current_stop_loss_percent / 5

            if self.orders.p_and_l_percent > .01:
                self.current_stop_loss_percent = self.current_stop_loss_percent / 5

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        stop_loss_condition = sell_stop_loss_condition()

        # Sell MA Speed
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum < -.6:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if stop_loss_condition: #or basic_stop_loss:  # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        # Trend
        """
        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False
        """
        #if 33824 < self.data.current_period < 34220:
            #print(str(self.indicators.get_ma_speed("Large", 1)) + "   " + str(self.data.current_period))

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.sum_array.clear()


class Percent17point82000(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Large", 2000, 2)
        self.indicators.add_adx(120)
        self.indicators.add_rsi(120)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Large", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 1

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum > .5:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        rsi_condition = 40 > self.indicators.get_rsi(120, 1) > 0

        # Backtesting
        if self.strategy_type == Strategy.StrategyType.BACKTEST:
            ignore_first_periods = self.data.current_period > 2000
        else:
            return True

        # ADX
        adx_condition = self.indicators.get_adx(120, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                         wait_period_condition and \
                         ignore_first_periods # and \
                        # buy_stayed_position_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell PNL Stop Loss
        def pnl_stop_loss():
            self.decrease_stop_loss_percent_by_pnl_threshold = .01

            if self.orders.p_and_l_percent > .005:
                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            elif self.orders.p_and_l_percent < -.005:
                return True
        pnl_condition = pnl_stop_loss()

        # Basic Stop Loss
        basic_stop_loss = self.orders.p_and_l_percent < -.04

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            moving_average_price = self.indicators.get_moving_average_price("Large", 1)

            self.stop_loss_percent = .0025

            self.current_stop_loss_percent = self.stop_loss_percent

            # if self.indicators.get_ma_speed("Large", 1) < .5:
                # self.current_stop_loss_percent = self.current_stop_loss_percent / 5

            # if self.orders.p_and_l_percent > .01:
                # self.current_stop_loss_percent = self.current_stop_loss_percent / 5

            anchor_price = moving_average_price

            if self.orders.stop_loss_price < anchor_price - (anchor_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = anchor_price - (anchor_price * self.current_stop_loss_percent)

            return anchor_price < self.orders.stop_loss_price
        stop_loss_condition = sell_stop_loss_condition()

        # Sell MA Speed
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum < -.6:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if stop_loss_condition: #or basic_stop_loss:  # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        # Trend
        """
        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False
        """
        #if 33824 < self.data.current_period < 34220:
            #print(str(self.indicators.get_ma_speed("Large", 1)) + "   " + str(self.data.current_period))

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.sum_array.clear()


class Percent16Mega960Over2Mo(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Sell MA", 50, 2)
        # self.indicators.add_moving_average("Buy MA", 120, 2)
        self.indicators.add_moving_average("Large", 100, 2)
        self.indicators.add_moving_average("Mega", 960, 2)
        self.indicators.add_adx(200)
        self.indicators.add_rsi(14)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        """
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Buy MA", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()
        """

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 3

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Mega", index))

            # TODO: if downtrending... use larger
            if speed_sum > 1.5:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        # rsi_condition = 35 > self.indicators.get_rsi(14, 1) > 0
        # rsi_condition = True

        # Backtesting
        if self.strategy_type == Strategy.StrategyType.BACKTEST:
            ignore_first_periods = self.data.current_period > 2000
        else:
            return True

        # Mega not negative
        mega_condition = self.indicators.get_ma_speed("Mega", 1) > .15

        # ADX
        adx_condition = self.indicators.get_adx(200, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                         wait_period_condition and \
                         ignore_first_periods and \
                         mega_condition # and \
                         # adx_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        moving_average_price = self.indicators.get_moving_average_price("Large", 1)
        self.decrease_stop_loss_percent_by_pnl_threshold = .01

        # Sell PNL Stop Loss
        def pnl_stop_loss():

            if self.orders.p_and_l_percent > .005:
                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            elif self.orders.p_and_l_percent < -.005:
                return True
        pnl_condition = pnl_stop_loss()

        #
        basic_stop_loss = self.orders.p_and_l_percent < -.04

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            self.stop_loss_percent = .05
            self.current_stop_loss_percent = self.stop_loss_percent

            if self.orders.stop_loss_price < moving_average_price - (moving_average_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = moving_average_price - (moving_average_price * self.current_stop_loss_percent)

            # Stop Loss Condition
            # bp.bprint("MA: ", moving_average_price, " SL:", self.orders.stop_loss_price)
            return moving_average_price < self.orders.stop_loss_price
        # stop_loss_condition = sell_stop_loss_condition()

        # Sell
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Mega", index))

            if speed_sum < -.6:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if speed_condition or basic_stop_loss:  # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        # Trend
        """
        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False
        """
        #if 33824 < self.data.current_period < 34220:
            #print(str(self.indicators.get_ma_speed("Large", 1)) + "   " + str(self.data.current_period))

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.sum_array.clear()


class Percent14WithMega960Over2Mo(Strategy):
    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Sell MA", 50, 2)
        # self.indicators.add_moving_average("Buy MA", 120, 2)
        self.indicators.add_moving_average("Large", 100, 2)
        self.indicators.add_moving_average("Mega", 960, 2)
        self.indicators.add_adx(200)
        self.indicators.add_rsi(14)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        """
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Buy MA", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()
        """

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 3

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Mega", index))

            # TODO: if downtrending... use larger
            if speed_sum > 1.5:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        # rsi_condition = 35 > self.indicators.get_rsi(14, 1) > 0
        # rsi_condition = True

        # Standard
        ignore_first_periods = self.data.current_period > 2000

        # Mega not negative
        mega_condition = self.indicators.get_ma_speed("Mega", 1) > .15

        # ADX
        adx_condition = self.indicators.get_adx(200, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                         wait_period_condition and \
                         ignore_first_periods and \
                         mega_condition # and \
                         # adx_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        moving_average_price = self.indicators.get_moving_average_price("Large", 1)
        self.decrease_stop_loss_percent_by_pnl_threshold = .01

        # Sell PNL Stop Loss
        def pnl_stop_loss():

            if self.orders.p_and_l_percent > .005:
                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            elif self.orders.p_and_l_percent < -.005:
                return True
        pnl_condition = pnl_stop_loss()

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            self.stop_loss_percent = .05
            self.current_stop_loss_percent = self.stop_loss_percent

            if self.orders.stop_loss_price < moving_average_price - (moving_average_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = moving_average_price - (moving_average_price * self.current_stop_loss_percent)

            # Stop Loss Condition
            # bp.bprint("MA: ", moving_average_price, " SL:", self.orders.stop_loss_price)
            return moving_average_price < self.orders.stop_loss_price
        # stop_loss_condition = sell_stop_loss_condition()

        # Sell
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 2

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Mega", index))

            if speed_sum < -.4:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if speed_condition: # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        # Trend
        """
        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False
        """
        #if 33824 < self.data.current_period < 34220:
            #print(str(self.indicators.get_ma_speed("Large", 1)) + "   " + str(self.data.current_period))

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.sum_array.clear()


class Fresh11PercentWithMega960Over2Months(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-60-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 0

    def add_indicators(self):
        self.indicators.add_moving_average("Sell MA", 50, 2)
        # self.indicators.add_moving_average("Buy MA", 120, 2)
        self.indicators.add_moving_average("Large", 100, 2)
        self.indicators.add_moving_average("Mega", 960, 2)
        self.indicators.add_adx(200)
        self.indicators.add_rsi(14)

    def buy(self):
        if self.orders.order_active:
            return False

        # Buy Stayed Positive
        """
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Buy MA", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()
        """

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 3

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Mega", index))

            # TODO: if downtrending... use larger
            if speed_sum > 1.5:
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        # wait_period_condition = self.current_wait_period == 0
        wait_period_condition = True

        # RSI
        # rsi_condition = 35 > self.indicators.get_rsi(14, 1) > 0
        # rsi_condition = True

        # Standard
        ignore_first_periods = self.data.current_period > 2000

        # Mega not negative
        mega_condition = self.indicators.get_ma_speed("Mega", 1) > .15

        # ADX
        adx_condition = self.indicators.get_adx(200, 1) > 35

        # Buy
        all_conditions = buy_ma_speed_condition and \
                         wait_period_condition and \
                         ignore_first_periods and \
                         mega_condition # and \
                         # adx_condition

        if all_conditions:
            return True

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        moving_average_price = self.indicators.get_moving_average_price("Large", 1)
        self.decrease_stop_loss_percent_by_pnl_threshold = .01

        # Sell PNL Stop Loss
        def pnl_stop_loss():

            if self.orders.p_and_l_percent > .005:
                pnl_stop_proportion = .5
                if self.pnl_stop_loss < self.orders.p_and_l_percent * pnl_stop_proportion:
                    self.pnl_stop_loss = self.orders.p_and_l_percent * pnl_stop_proportion

                if self.orders.p_and_l_percent < self.pnl_stop_loss:
                    return True
            elif self.orders.p_and_l_percent < -.005:
                return True
        pnl_condition = pnl_stop_loss()

        # Sell
        # Sell Stop Loss
        def sell_stop_loss_condition():
            self.stop_loss_percent = .05
            self.current_stop_loss_percent = self.stop_loss_percent

            if self.orders.stop_loss_price < moving_average_price - (moving_average_price * self.current_stop_loss_percent):
                self.orders.stop_loss_price = moving_average_price - (moving_average_price * self.current_stop_loss_percent)

            # Stop Loss Condition
            # bp.bprint("MA: ", moving_average_price, " SL:", self.orders.stop_loss_price)
            return moving_average_price < self.orders.stop_loss_price
        # stop_loss_condition = sell_stop_loss_condition()

        # Sell
        def sell_ma_speed():
            speed_sum = 0
            periods_to_check = 1

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Sell MA", index))

            if speed_sum < -3:
                return True
        speed_condition = sell_ma_speed()

        # Sell Condition - Proportionate Stop Loss
        def proportionate_stop_loss():
            speed = self.indicators.get_ma_speed("Large", 1)

        # Sell Conditions
        if speed_condition: # or speed_condition
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        # Trend
        """
        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False
        """
        #if 33824 < self.data.current_period < 34220:
            #print(str(self.indicators.get_ma_speed("Large", 1)) + "   " + str(self.data.current_period))

    def on_buy_end(self):
        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.pnl_stop_loss = 0
        self.sum_array.clear()


class NinePercentWith300(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-30-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 25

    def add_indicators(self):
        self.indicators.add_moving_average("Sell MA", 60, 2)
        self.indicators.add_moving_average("Buy MA", 120, 2)
        self.indicators.add_moving_average("Large", 300, 2)
        self.indicators.add_rsi(14)

    def buy(self):
        # Buy Stayed Positive
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Buy MA", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 2
            #if not len(self.sum_array) >= periods_to_check:
                #return False

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("Large", index))

            if speed_sum > 1.75:
                # print(speed_sum)
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        wait_period_condition = self.current_wait_period == 0

        # RSI
        rsi_condition = 30 > self.indicators.get_rsi(14, 1) > 0

        # Standard
        ignore_first_periods = self.data.current_period > 150

        # Buy
        all_conditions = buy_ma_speed_condition and wait_period_condition and ignore_first_periods
        return all_conditions

    def sell(self):
        if not self.orders.order_active:
            return False

        # Sell
        def sell_ma_speed():
            return float(self.indicators.get_ma_speed_sum("Large", 1)) <= 0.
        speed_condition = sell_ma_speed()

        # Sell Conditions
        if speed_condition:
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False

    def on_buy_end(self):
        # Set Stop Loss
        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        slp = self.stop_loss_percent

        if sl < cp - (cp * slp):
            self.orders.stop_loss_price = cp - (cp * slp)

        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.sum_array.clear()


class ProgressTowards100MAProfitable(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-30-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0
        self.wait_periods_before_buying_again = 25

    def add_indicators(self):
        self.indicators.add_moving_average("Sell MA", 60, 2)
        self.indicators.add_moving_average("Buy MA", 120, 2)
        self.indicators.add_moving_average("Large", 300, 2)
        self.indicators.add_rsi(14)

    def buy(self):
        # Buy Stayed Positive
        def stayed_positive():
            positive_period = 15
            positives = 0
            for i in range(positive_period):
                index = i + 1
                if float(self.indicators.get_ma_speed("Buy MA", index)) > 1:
                    positives += 1

            return positives == positive_period
        buy_stayed_position_condition = stayed_positive()

        # Buy
        def ma_speed_buy():
            speed_sum = 0
            periods_to_check = 2
            #if not len(self.sum_array) >= periods_to_check:
                #return False

            for i in range(periods_to_check):
                index = i + 1
                #speed_sum += float(self.sum_array[-index])
                speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

            if speed_sum > 1.75:
                # print(speed_sum)
                return True
            else:
                return False
        buy_ma_speed_condition = ma_speed_buy()

        # Buy
        def ma_speed_buy_with_large_ma():
            speed_sum = 0
            periods_to_check = 2
            if not len(self.sum_array) >= periods_to_check:
                return False

            for i in range(periods_to_check):
                index = i + 1
                speed_sum += float(self.sum_array[-index])

            # Large Ma
            if speed_sum > 1.75:
                return True
        buy_ma_with_large_ma_speed_condition = ma_speed_buy()

        # Buy
        def price_percentage():
            price_percent_sum = 0
            range_amount = 2

            for i in range(range_amount):
                if len(self.data.all_close) > range_amount:
                    index = i + 1

                    close = float(self.data.all_close[-index])
                    previous_close = float(self.data.all_close[-index - 1])
                    close_percent_difference = (close - previous_close) / previous_close

                    price_percent_sum += close_percent_difference

            if price_percent_sum > .01:
                #print(price_percent_sum)
                return True
            else:
                return False
        price_percentage_condition = price_percentage()

        # Buy
        wait_period_condition = self.current_wait_period == 0

        # RSI
        rsi_condition = 30 > self.indicators.get_rsi(14, 1) > 0

        # Standard
        ignore_first_periods = self.data.current_period > 150

        # Not when downtrending large MA
        large_ma_not_downtrending = self.indicators.get_ma_speed_sum("Large", 1) > 1

        # Buy
        all_conditions = buy_ma_speed_condition and wait_period_condition and ignore_first_periods and large_ma_not_downtrending
        return all_conditions

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        mapr = self.indicators.get_moving_average_price("Sell MA", 1)

        # Sell Stop Loss
        def sell_stop_loss_condition():

            # if self.indicators.get_ma_speed("Large", 1) < .15:
                # self.stop_loss_percent = .0075
            # else:
                # self.stop_loss_percent = .025

            self.stop_loss_percent = .025

            if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
                self.p_and_l_limit_crossed = True

            if self.p_and_l_limit_crossed:
                self.current_stop_loss_percent = self.stop_loss_percent / 5
                #
                if sl < mapr - (mapr * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)
            else:
                self.current_stop_loss_percent = self.stop_loss_percent
                if sl < mapr - (mapr * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)

            # Stop Loss Condition
            return self.orders.the_current_price < self.orders.stop_loss_price
        stop_loss_condition = sell_stop_loss_condition()

        # Sell
        def sell_ma_speed():
            return float(self.indicators.get_ma_speed_sum("Buy MA", 1)) < - 1.
        speed_condition = sell_ma_speed()

        # Sell
        def sell_current_price_stop_loss():
            if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
                self.p_and_l_limit_crossed = True

            if self.p_and_l_limit_crossed:
                self.current_stop_loss_percent = self.stop_loss_percent / 3
                #
                if sl < cp - (cp * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = cp - (cp * self.current_stop_loss_percent)
            else:
                self.current_stop_loss_percent = self.stop_loss_percent
                if sl < cp - (cp * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = cp - (cp * self.current_stop_loss_percent)

            return cp < self.orders.stop_loss_price
        current_price_stop_loss_condition = sell_current_price_stop_loss()

        # Sell
        def sell_base_stop():
            # Base
            self.base_stop_loss_price = pp - (pp * self.base_stop_percent)
            return cp <= self.base_stop_loss_price
        base_stop_condition = sell_base_stop()

        # Sell
        def sell_take_profit():
            return self.orders.p_and_l > .01
        take_profit_condition = sell_take_profit()

        # Sell Conditions
        if stop_loss_condition or speed_condition:
            self.current_wait_period = self.wait_periods_before_buying_again
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        if not self.current_wait_period == 0:
            self.current_wait_period -= 1

        self.sum_array.append(self.indicators.get_ma_speed("Buy MA", 1))

        for i in range(2):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("Buy MA", index))

        if speed_sum > 1.75:
            self.trend_started = True

        if speed_sum < .25:
            self.trend_started = False
            self.bought_this_trend = False

    def on_buy_end(self):
        # Set Stop Loss
        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        slp = self.stop_loss_percent

        if sl < cp - (cp * slp):
            self.orders.stop_loss_price = cp - (cp * slp)

        self.bought_this_trend = True

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0
        self.sum_array.clear()


class ThatWeird16PercentButSuperLowOrderPercentIncrease(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-30-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False
        self.current_speed_sum = 0

    def add_indicators(self):
        self.indicators.add_moving_average("25", 25, 2)
        self.indicators.add_moving_average("300", 50, 2)

    def buy(self):
        def ma_speed_buy():
            speed_sum = 0
            for i in range(5):
                index = i + 1
                speed_sum += float(self.indicators.get_ma_speed("300", index))

            if speed_sum > 3:
                return True

        # if ma_speed_buy():
            #return True
        # else:
            #return False

        def price_percentage():
            price_percent_sum = 0
            range_amount = 2

            for i in range(range_amount):
                if len(self.data.all_close) > range_amount:
                    index = i + 1

                    close = float(self.data.all_close[-index])
                    previous_close = float(self.data.all_close[-index - 1])
                    close_percent_difference = (close - previous_close) / previous_close

                    price_percent_sum += close_percent_difference

            if price_percent_sum > .0125:
                #print(price_percent_sum)
                return True
            else:
                return False

        if price_percentage():
            return True
        else:
            return False

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        mapr = self.indicators.get_moving_average_price("25", 1)

        def ma_speed():
            # if sl < cp - (cp * slp):
            #       self.orders.stop_loss_price = mapr - (mapr * slp)

            # HALF
            if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
                self.p_and_l_limit_crossed = True

            if self.p_and_l_limit_crossed:
                self.current_stop_loss_percent = self.stop_loss_percent / 3
                #
                if sl < mapr - (mapr * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)
            else:
                self.current_stop_loss_percent = self.stop_loss_percent
                if sl < mapr - (mapr * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)

            # Conditions
            # speed_condition = False
            speed_sum = 0

            #
            for i in range(3):
                index = i + 1
                # print(self.indicators.get_ma_speed("425", index))
                speed_sum += float(self.indicators.get_ma_speed("300", index))

            speed_condition = speed_sum < - 1

            stop_loss_condition = False

            # stop_loss_condition = self.orders.the_current_price < self.orders.stop_loss_price

            # self.base_stop_loss_price = pp - (pp * self.base_stop_percent)
            # base_stop_condition = cp <= self.base_stop_loss_price

            base_stop_condition = False

            if stop_loss_condition or speed_condition or base_stop_condition:
                return True
            else:
                return False
        # ma_speed()

        def stop_loss():
            if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
                self.p_and_l_limit_crossed = True

            if self.p_and_l_limit_crossed:
                self.current_stop_loss_percent = self.stop_loss_percent / 3
                #
                if sl < cp - (cp * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = cp - (cp * self.current_stop_loss_percent)
            else:
                self.current_stop_loss_percent = self.stop_loss_percent
                if sl < cp - (cp * self.current_stop_loss_percent):
                    self.orders.stop_loss_price = cp - (cp * self.current_stop_loss_percent)

            stop_loss_condition = cp < self.orders.stop_loss_price

            if stop_loss_condition:
                # print("Sell")
                return True
            else:
                return False
        if stop_loss():
            return True
        else:
            return False

    def on_end_period(self):
        speed_sum = 0

        for i in range(5):
            index = i + 1
            speed_sum += float(self.indicators.get_ma_speed("300", index))

        if speed_sum > 3:
            self.trend_started = True
            self.trend_ended = False

        if speed_sum < - 2:
            self.trend_ended = True
            self.trend_started = False

    def on_buy_end(self):
        # Set Stop Loss
        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        slp = self.stop_loss_percent

        if sl < cp - (cp * slp):
            self.orders.stop_loss_price = cp - (cp * slp)

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
        self.current_stop_loss_percent = 0


class MASpeedStrategy12point5LowOrders(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-30-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False

    def add_indicators(self):
        self.indicators.add_moving_average("25", 25, 2)
        self.indicators.add_moving_average("425", 425, 2)

    def buy(self):

        # period_amount = 5
        # periods_positive = 0

        #for i in range(period_amount):
            #if self.indicators.get_ma_speed_sum("425", i) > .1:
                #periods_positive += 1

        #if periods_positive == (period_amount - 1):
            #return True
        #else:
            #return False

        speed_sum = 0
        for i in range(2):
            index = i + 1
            # print(self.indicators.get_ma_speed("425", index))
            speed_sum += float(self.indicators.get_ma_speed("425", index))

        # print(float(self.indicators.get_ma_speed("425", 1)))

        if speed_sum > 2:
            return True
        else:
            return False


        #if not self.indicators.get_ma_speed_sum("425", 1) > self.buy_speed_sum_requirement:
            #return False

        #
        # return True

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        mapr = self.indicators.get_moving_average_price("25", 1)

        # if sl < cp - (cp * slp):
        #       self.orders.stop_loss_price = mapr - (mapr * slp)

        # HALF
        if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
            self.p_and_l_limit_crossed = True

        if self.p_and_l_limit_crossed:
            self.current_stop_loss_percent = self.stop_loss_percent / 3
            #
            if sl < cp - (cp * self.current_stop_loss_percent):
                self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)
        else:
            self.current_stop_loss_percent = self.stop_loss_percent
            if sl < cp - (cp * self.current_stop_loss_percent):
                self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)

        # Conditions
        # speed_condition = False
        speed_sum = 0
        for i in range(3):
            index = i + 1
            # print(self.indicators.get_ma_speed("425", index))
            speed_sum += float(self.indicators.get_ma_speed("425", index))

        speed_condition = speed_sum < - 1

        stop_loss_condition = False
        # stop_loss_condition = self.orders.the_current_price < self.orders.stop_loss_price

        # self.base_stop_loss_price = pp - (pp * self.base_stop_percent)
        # base_stop_condition = cp <= self.base_stop_loss_price
        base_stop_condition = False

        if stop_loss_condition or speed_condition or base_stop_condition:
            return True
        else:
            return False

    def on_buy_end(self):
        # Set Stop Loss
        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        slp = self.stop_loss_percent

        if sl < cp - (cp * slp):
            self.orders.stop_loss_price = cp - (cp * slp)

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False


class MASpeedStrategyNew11Point6(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.backtesting_strategy_data = "ETH-30-DAYS.csv"
        self.print_log_notes = ""
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .02
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False

    def add_indicators(self):
        self.indicators.add_moving_average("25", 25, 2)
        self.indicators.add_moving_average("425", 425, 2)

    def buy(self):

        # period_amount = 5
        # periods_positive = 0

        #for i in range(period_amount):
            #if self.indicators.get_ma_speed_sum("425", i) > .1:
                #periods_positive += 1

        #if periods_positive == (period_amount - 1):
            #return True
        #else:
            #return False

        speed_sum = 0
        for i in range(10):
            index = i + 1
            # print(self.indicators.get_ma_speed("425", index))
            speed_sum += float(self.indicators.get_ma_speed("425", index))

        # print(float(self.indicators.get_ma_speed("425", 1)))

        if speed_sum > 8:
            return True


        #if not self.indicators.get_ma_speed_sum("425", 1) > self.buy_speed_sum_requirement:
            #return False

        #
        # return True

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        mapr = self.indicators.get_moving_average_price("25", 1)

        # if sl < cp - (cp * slp):
        #       self.orders.stop_loss_price = mapr - (mapr * slp)

        # HALF
        if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
            self.p_and_l_limit_crossed = True

        if self.p_and_l_limit_crossed:
            self.current_stop_loss_percent = self.stop_loss_percent / 3
            #
            if sl < cp - (cp * self.current_stop_loss_percent):
                self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)
        else:
            self.current_stop_loss_percent = self.stop_loss_percent
            if sl < cp - (cp * self.current_stop_loss_percent):
                self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)

        # Conditions
        # speed_condition = False
        speed_sum = 0
        for i in range(3):
            index = i + 1
            # print(self.indicators.get_ma_speed("425", index))
            speed_sum += float(self.indicators.get_ma_speed("425", index))

        speed_condition = speed_sum < - 1

        stop_loss_condition = False
        # stop_loss_condition = self.orders.the_current_price < self.orders.stop_loss_price

        # self.base_stop_loss_price = pp - (pp * self.base_stop_percent)
        # base_stop_condition = cp <= self.base_stop_loss_price
        base_stop_condition = False

        if stop_loss_condition or speed_condition or base_stop_condition:
            return True
        else:
            return False

    def on_buy_end(self):
        # Set Stop Loss
        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        slp = self.stop_loss_percent

        if sl < cp - (cp * slp):
            self.orders.stop_loss_price = cp - (cp * slp)

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False


class MASpeedStrategy11(Strategy):

    def __init__(self):
        super().__init__()
        self.strategy_name = "MA Speed Trailing Stop"
        self.print_log_notes = ""
        self.backtesting_strategy_data = "ETH-30-Days-Sept.csv"
        self.trade_symbol = "ETHUSDT"
        self.trade_usd = 250
        self.fee = .00075
        self.stop_loss_percent = .025
        self.buy_speed_sum_requirement = 1.75
        self.sell_speed_min = -0.1
        self.base_stop_percent = .015
        self.decrease_stop_loss_percent_by_pnl_threshold = .0075
        self.buy_now = False
        self.fake_order = False
        self.p_and_l_limit_crossed = False

    def add_indicators(self):
        self.indicators.add_moving_average("25", 25, 2)
        self.indicators.add_moving_average("425", 425, 2)

    def buy(self):

        if not self.indicators.get_ma_speed_sum("425", 1) > self.buy_speed_sum_requirement:
            return False

        #
        return True

    def sell(self):
        if not self.orders.order_active:
            return False

        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        pp = self.orders.purchase_price
        mapr = self.indicators.get_moving_average_price("25", 1)

        # if sl < cp - (cp * slp):
            # self.orders.stop_loss_price = mapr - (mapr * slp)

        # HALF
        if self.orders.p_and_l_percent > self.decrease_stop_loss_percent_by_pnl_threshold:
            self.p_and_l_limit_crossed = True

        if self.p_and_l_limit_crossed:
            self.current_stop_loss_percent = self.stop_loss_percent / 3
            #
            if sl < cp - (cp * self.current_stop_loss_percent):
                self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)
        else:
            self.current_stop_loss_percent = self.stop_loss_percent
            if sl < cp - (cp * self.current_stop_loss_percent):
                self.orders.stop_loss_price = mapr - (mapr * self.current_stop_loss_percent)

        # Conditions
        # speed_condition = False
        speed_condition = self.indicators.get_ma_speed_sum("425", 1) < self.sell_speed_min

        stop_loss_condition = False
        # stop_loss_condition = self.orders.the_current_price < self.orders.stop_loss_price

        self.base_stop_loss_price = pp - (pp * self.base_stop_percent)
        base_stop_condition = cp <= self.base_stop_loss_price

        if stop_loss_condition or speed_condition or base_stop_condition:
            return True
        else:
            return False

    def on_buy_end(self):
        # Set Stop Loss
        sl = self.orders.stop_loss_price
        cp = self.orders.the_current_price
        slp = self.stop_loss_percent

        if sl < cp - (cp * slp):
            self.orders.stop_loss_price = cp - (cp * slp)

    def on_sell_end(self):
        self.p_and_l_limit_crossed = False
