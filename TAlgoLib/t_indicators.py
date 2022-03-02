import Backtesting.TBTLib.tbt_data_manager as t_data
from typing import List
import talib
import numpy
from itertools import groupby
import sys
import Backtesting.TBTLib.tbt_event_manager as tbt_events


class IndicatorManager:
    data = None  # type: t_data.BacktestData

    #
    enable_logging = None

    # Gets set from strategy

    # BBANDS
    bbw_condition_minimum_requirement = 0
    bb_period = 0
    bb_standard_deviation_upper = 2
    bb_standard_deviation_lower = 2

    # ATR

    # adx
    adx_requirement = 0
    adx_time_period = 0

    # rsi
    use_rsi_reversal = False
    use_rsi_transition = False
    use_rsi_min = False
    rsi_ma = 0
    rsi_min = 0

    # sar
    sar_uptrend_name = "uptrend"
    sar_downtrend_name = "downtrend"
    sar_check_for = "downtrend"
    sar_counter_minimum = 0
    sar_acceleration = 0
    sar_maximum = 0

    # sar counter
    sar_counter_check_for_down = False
    sar_use_counter = False

    # Debug
    debug_sum = 0

    # RSI
    class ADX:
        period = 0
        all_adx = []

        def __init__(self, _period):
            self.period = _period

        def set_adx(self, _high, _low, _close):
            self.all_adx = talib.ADX(_high, _low, _close)

        def get_adx(self, _index):
            if len(self.all_adx) > _index:
                return self.all_adx[-_index]
            else:
                return -1

    all_adx: List[ADX] = []

    class RSI:
        period = 0
        all_rsi = []

        def __init__(self, _period):
            self.period = _period

        def set_rsi(self, _close_prices):
            self.all_rsi = talib.RSI(_close_prices)

        def get_rsi(self, _index):
            if len(self.all_rsi) > _index:
                return self.all_rsi[-_index]
            else:
                return -1

    rsi_all: List[RSI] = []

    class MovingAverage:
        name = ""
        period = 0
        speed_period = 3
        prices_all = []
        speed_all = []
        speed_sum_all = []
        plot_color = ""
        current_price = 0
        current_speed = 0
        current_speed_sum = 0

        def __init__(self, _name, _period, _speed_period):
            self.name = _name
            self.speed_period = _speed_period
            self.period = _period
            self.prices_all = []
            self.speed_all = []
            self.speed_sum_all = []
            self.plot_color = ""

        # Get
        def get_ma_price(self, _index):
            if len(self.prices_all) > _index:
                return self.prices_all[-_index]
            else:
                return 0

        def get_ma_speed(self, _index):
            if len(self.speed_all) > _index:
                return self.speed_all[-_index]
            else:
                return 0

        def get_ma_speed_sum(self, _index):
            if len(self.speed_sum_all) > _index:
                return self.speed_sum_all[-_index]
            else:
                return 0

        # Set
        def set_this_moving_average(self):
            self.set_ma_speed()
            self.set_ma_speed_sum()
            self.current_speed = self.get_ma_speed(1)
            self.current_speed_sum = self.get_ma_speed_sum(1)
            self.current_price = self.get_ma_price(1)

        def set_ma_speed(self):
            if len(self.prices_all) > 2:
                division = ((self.prices_all[-1] / self.prices_all[-2]) - 1)
                speed = division * 10000
                self.speed_all.append(speed)

        def set_ma_speed_sum(self):
            if len(self.speed_all) > self.speed_period:
                speed_sum = sum(self.speed_all[-self.speed_period:])
                self.speed_sum_all.append(speed_sum)

        def set_historical(self):
            # print("set-------------------------------------------------------")
            # print("length: " + str(len(self.prices_all)))

            # Add Speed
            for i in range(len(self.prices_all)):
                if i >= 1:
                    division = ((self.prices_all[i] / self.prices_all[(i-1)]) - 1)
                    speed = division * 10000

                    self.speed_all.append(speed)
                    # print("Append: " + str(speed))

            # Add
            for i in range(len(self.speed_all) + 1):    
                if i >= self.speed_period:
                    starting_index = i - self.speed_period
                    ending_index = i
                    self.speed_sum_all.append(sum(self.speed_all[starting_index:ending_index]))

        # Print
        def get_print_out(self):
            return vars(self)

    #
    moving_average_all_objects: List[MovingAverage] = []

    # INDICATOR FUNCTIONS
    def __init__(self, _data):
        self.data = _data

    # Add
    def add_adx(self, _period):
        new_adx = self.ADX(_period)
        self.all_adx.append(new_adx)

    def add_rsi(self, _period):
        rsi = self.RSI(_period)
        self.rsi_all.append(rsi)

    def add_bbw(self):
        pass

    def add_moving_average(self, _name, _period, _speed_period):
        ma = self.MovingAverage(_name, _period, _speed_period)
        self.moving_average_all_objects.append(ma)
        # print("ADDED MOVING AVERAGE")

    # Set
    def set_all_indicators(self):
        self.set_moving_average()
        self.set_rsi()
        self.set_adx()

    def set_moving_average(self):
        # print("Set Moving Average")
        for ma in self.moving_average_all_objects:

            """
            if ma.period > 75:
                close_numpy_without_duplicates = [i[0] for i in groupby(self.data.all_close)]
                close_numpy_without_duplicates = numpy.array(close_numpy_without_duplicates)

                ma.prices_all = talib.MA(close_numpy_without_duplicates, ma.period)
                #print(" GREATER THAN 75 NUMPY CLOSE LENGTHL " + str(len(close_numpy_without_duplicates))
                      #+ " : MA: "
                      #+ str(len(ma.prices_all)))
            else:
            """
            ma.prices_all = talib.MA(self.data.all_close, ma.period)

            ma.set_this_moving_average()

    def set_historical(self):
        # print("SET HISTORY")
        self.set_moving_average()
        for moving_averages in self.moving_average_all_objects:
            moving_averages.set_historical()

    def set_rsi(self):
        for rsi in self.rsi_all:
            rsi.set_rsi(self.data.all_close)

    def set_adx(self):
        for adx in self.all_adx:
            adx.set_adx(self.data.all_high, self.data.all_low, self.data.all_close)

    # Get
    def get_moving_average_price(self, _name, _index):
        for moving_average in self.moving_average_all_objects:
            if moving_average.name == _name:
                return moving_average.get_ma_price(_index)

    def get_ma_speed(self, _name, _index):
        for moving_average in self.moving_average_all_objects:
            if moving_average.name == _name:
                return moving_average.get_ma_speed(_index)

    def get_ma_speed_sum(self, _name, _index):
        for moving_average in self.moving_average_all_objects:
            if moving_average.name == _name:
                return moving_average.get_ma_speed_sum(_index)  + self.debug_sum

    def get_rsi(self, _period, _index):
        for rsi in self.rsi_all:

            if rsi.period == _period:
                return rsi.get_rsi(_index)

    def get_adx(self, _period, _index):
        for adx in self.all_adx:
            if adx.period == _period:
                return adx.get_adx(_index)

    # Logging
    def get_backtest_indicator_print_out(self):
        dict_log = vars(self)

        all_str = "\n\nINDICATOR PARAMETERS: \n"

        if type(dict_log) is dict:
            for key in dict_log:
                if type(dict_log[key]) is dict or type(dict_log[key]) is list:
                    for key2 in dict_log[key]:
                        all_str += str(key2) + " : " + str(dict_log[key][key2]) + "\n"
                else:
                    all_str += str(key) + " : " + str(dict_log[key]) + "\n"

        for ma in self.moving_average_all_objects:
            all_str += "\nMoving Average: Period Name: " + ma.name \
                       + "  Period: " + str(ma.period) \
                       + "  Array Length: " + str(len(ma.prices_all)) \
                       + "  Speed Period: " + str(ma.speed_period) \
                       + "\n"
        return all_str

    def get_trader_indicator_print_out(self):
        all_str = ""
        for moving_averages in self.moving_average_all_objects:
            all_str += "MA Period: " + str(moving_averages.period) + \
                       " Price: " + str(round(moving_averages.get_ma_price(1), 4)) +\
                       " Speed Period: " + str(moving_averages.speed_period) + \
                       " Speed: " + str(round(moving_averages.get_ma_speed(1), 4)) + \
                       " Speed Sum: " + str(round(moving_averages.get_ma_speed_sum(1) + self.debug_sum, 4))
            all_str += "\n"

        return all_str

    def log_on_buy(self):
        self.log_to_orders("BUY INDICATORS")
        self.log_nested_dicts_to_orders(vars(self))
        for ma in self.moving_average_all_objects:
            self.log_nested_dicts_to_orders(ma.get_print_out())

    def log_on_sell(self):
        self.log_to_orders("SELL INDICATORS")
        self.log_nested_dicts_to_orders(vars(self))
        for ma in self.moving_average_all_objects:
            self.log_nested_dicts_to_orders(ma.get_print_out())

    def log_nested_dicts_to_orders(self, dict_log):
        if type(dict_log) is dict:
            for key in dict_log:
                if type(dict_log[key]) is dict or type(dict_log[key]) is list:
                    for key2 in dict_log[key]:
                        self.log_to_orders((str(key2) + " : " + str(dict_log[key][key2]) + "\n"))
                else:
                    self.log_to_orders((str(key) + " : " + str(dict_log[key]) + "\n"))

    def log(self, logg):
        try:
            if self.enable_logging:
                file_object = open(sys.path[1] + "/TAlgoLib/t_indicator_log.txt", "a+")
                logg = str(logg) + "\n"
                file_object.write(logg)
                file_object.close()
        except:
            pass

    def log_to_orders(self, logg):
        try:
            if self.enable_logging:
                file_object = open(sys.path[1] + "/Backtesting/TBTLib/tbt_order_manager_log.txt", "a+")
                logg = str(logg) + "\n"
                file_object.write(logg)
                file_object.close()
        except:
            pass
