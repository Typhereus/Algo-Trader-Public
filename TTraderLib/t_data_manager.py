import numpy
from binance.client import Client
from datetime import datetime
import sys


class DataManager:
    last_close_price = 0.0
    the_current_time = ""

    trade_symbol = ""
    data_client = None  # type: Client

    open_array = []
    high_array = []
    low_array = []
    close_array = []

    timestamp_array = []
    timestamp_numpy = numpy.array(timestamp_array)
    timestamp_strings = []

    all_open = numpy.array(open_array)
    all_high = numpy.array(high_array)
    all_low = numpy.array(low_array)
    all_close = numpy.array(close_array)

    candlestick_max_array = 1000

    def get_history_for_indicators(self):
        try:
            klines = self.data_client.get_historical_klines(
                self.trade_symbol, Client.KLINE_INTERVAL_1MINUTE,
                str(self.candlestick_max_array) + " minutes ago UTC")

            for item in klines:
                unix_time_raw = float(item[0])
                unix_time_seconds = int(unix_time_raw / 1000)
                date_time = datetime.fromtimestamp(unix_time_seconds)
                self.timestamp_strings.append(date_time)

                self.timestamp_numpy = numpy.append(self.timestamp_numpy, unix_time_seconds)

                self.all_open = numpy.append(self.all_open, float(item[1]))
                self.all_high = numpy.append(self.all_high, float(item[2]))
                self.all_low = numpy.append(self.all_low, float(item[3]))
                self.all_close = numpy.append(self.all_close, float(item[4]))

            klines.clear()

        except Exception as e:
            pass
            log(e)
        print("HISTORY")

    def get_current_candle_with_history(self):

        try:
            # Get Data
            klines = self.data_client.get_historical_klines(self.trade_symbol, Client.KLINE_INTERVAL_1MINUTE,
                                                                 "10 minute ago UTC")
            # Append Data
            for kline in klines:

                # Get Time
                unix_time_raw = float(kline[0])
                unix_time_seconds = int(unix_time_raw / 1000)
                date_time = datetime.fromtimestamp(unix_time_seconds)

                # Get Prices
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])

                # If does not contain, append
                if not self.timestamp_strings.__contains__(date_time):
                    self.timestamp_numpy = numpy.append(self.timestamp_numpy, unix_time_seconds)
                    self.all_open = numpy.append(self.all_open, open_price)
                    self.all_low = numpy.append(self.all_low, low_price)
                    self.all_high = numpy.append(self.all_high, high_price)
                    self.all_close = numpy.append(self.all_close, close_price)
                    self.timestamp_strings.append(date_time)

            # Set Limit To Array
            # T
            self.timestamp_numpy = numpy.array(self.timestamp_numpy[-self.candlestick_max_array:])

            # O
            self.all_open = numpy.array(self.all_open[-self.candlestick_max_array:])

            # H
            self.all_high = numpy.array(self.all_high[-self.candlestick_max_array:])

            # L
            self.all_low = numpy.array(self.all_low[-self.candlestick_max_array:])

            # C
            self.all_close = numpy.array(self.all_close[-self.candlestick_max_array:])

            # Set Current Time And Last Close
            self.last_close_price = self.all_close[-1]
            self.the_current_time = self.timestamp_strings[-1]

            self.print_short_history()

        except Exception as e:
            pass
            log(e)

    def print_short_history(self):
        log("\n")
        for i in range(10):
            log(
                "T Len:" + str(len(self.timestamp_numpy))
                + " O Len:" + str(len(self.all_open))
                + " L Len:" + str(len(self.all_low))
                + " H Len:" + str(len(self.all_high))
                + " C Len:" + str(len(self.all_close))
                + " T:" + str(self.timestamp_strings[-(i + 1)])
                + " O:" + str(self.all_open[-(i + 1)])
                + " L:" + str(self.all_low[-(i + 1)])
                + " H:" + str(self.all_high[-(i + 1)])
                + " C:" + str(self.all_close[-(i + 1)])
                )

    def __init__(self, _client, _trade_symbol):
        self.data_client = _client
        self.trade_symbol = _trade_symbol
        self.get_history_for_indicators()
        log("Data MGMT Initialized 1")


def log(log):
    try:
        file_object = open(sys.path[1] + "/TTraderLib/t_data_management_log.txt", "a+")
        log = str(log) + "\n"
        file_object.write(log)
        file_object.close()
    except:
        pass