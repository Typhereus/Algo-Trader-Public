import json
from datetime import datetime
from itertools import groupby
import numpy
import talib
import websocket
from binance.client import Client
from binance.enums import *
import Broker.config as config
from typing import List
import time
import threading
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


class SymbolParameters:
    # Symbol Name
    symbol_name = ""

    RSI_PERIODS = 0

    ATR_PERIODS = 0

    ADX_PERIODS = 0

    BB_PERIOD = 0
    BB_STD_DEV_UPPER = 0
    BB_STD_DEV_LOWER = 0

    MA_5 = 0
    MA_15 = 0
    MA_25 = 0
    MA_50 = 0
    MA_100 = 0
    MA_200 = 0

    MAX_ARRAY = 0

    HISTORICAL_DATA_TIMEFRAME = ""

    VOLUME_MIN = 0

    ORDER_FIRST_STOP_LOSS_PERCENT = 0.0
    ORDER_STOP_LOSS_PERCENT = 0.0

    USE_GENERIC_STRATEGY = False


class AllSymbolParameters:
    all_symbol_settings: List[SymbolParameters] = []

    def storj(self):
        storj = SymbolParameters()

        storj.symbol_name = "STORJUSDT"

        storj.ATR_PERIODS = 15
        storj.RSI_PERIODS = 10
        storj.ADX_PERIODS = 30

        storj.BB_PERIOD = 15
        storj.BB_STD_DEV_UPPER = 2
        storj.BB_STD_DEV_LOWER = 2

        storj.MA_5 = 8
        storj.MA_15 = 18
        storj.MA_25 = 28
        storj.MA_50 = 50
        storj.MA_100 = 100
        storj.MA_200 = 200

        storj.MAX_ARRAY = 130

        storj.HISTORICAL_DATA_TIMEFRAME = "200 minutes ago UTC"

        storj.VOLUME_MIN = 0

        storj.ORDER_FIRST_STOP_LOSS_PERCENT = 0.01
        storj.ORDER_STOP_LOSS_PERCENT = 0.01

        storj.USE_GENERIC_STRATEGY = True

        self.all_symbol_settings.append(storj)

    def batusdt(self):
        bat = SymbolParameters()

        bat.symbol_name = "BATUSDT"

        bat.ATR_PERIODS = 15
        bat.RSI_PERIODS = 10
        bat.ADX_PERIODS = 30

        bat.BB_PERIOD = 15
        bat.BB_STD_DEV_UPPER = 2
        bat.BB_STD_DEV_LOWER = 2

        bat.MA_5 = 8
        bat.MA_15 = 18
        bat.MA_25 = 28
        bat.MA_50 = 50
        bat.MA_100 = 100
        bat.MA_200 = 200

        bat.MAX_ARRAY = 130

        bat.HISTORICAL_DATA_TIMEFRAME = "200 minutes ago UTC"

        bat.VOLUME_MIN = 0

        bat.ORDER_FIRST_STOP_LOSS_PERCENT = 0.01
        bat.ORDER_STOP_LOSS_PERCENT = 0.01

        bat.USE_GENERIC_STRATEGY = True

        self.all_symbol_settings.append(bat)

    def atomusdt(self):
        atom = SymbolParameters()

        atom.symbol_name = "ATOMUSDT"

        atom.ATR_PERIODS = 15
        atom.RSI_PERIODS = 10
        atom.ADX_PERIODS = 30

        atom.BB_PERIOD = 15
        atom.BB_STD_DEV_UPPER = 2
        atom.BB_STD_DEV_LOWER = 2

        atom.MA_5 = 8
        atom.MA_15 = 18
        atom.MA_25 = 28
        atom.MA_50 = 50
        atom.MA_100 = 100
        atom.MA_200 = 200

        atom.MAX_ARRAY = 130

        atom.HISTORICAL_DATA_TIMEFRAME = "200 minutes ago UTC"

        atom.VOLUME_MIN = 0

        atom.ORDER_FIRST_STOP_LOSS_PERCENT = 0.01
        atom.ORDER_STOP_LOSS_PERCENT = 0.01

        atom.USE_GENERIC_STRATEGY = True

        self.all_symbol_settings.append(atom)

    def zrxusdt(self):
        zrx = SymbolParameters()

        zrx.symbol_name = "ZRXUSDT"

        zrx.ATR_PERIODS = 15
        zrx.RSI_PERIODS = 10
        zrx.ADX_PERIODS = 30

        zrx.BB_PERIOD = 15
        zrx.BB_STD_DEV_UPPER = 2
        zrx.BB_STD_DEV_LOWER = 2

        zrx.MA_5 = 8
        zrx.MA_15 = 18
        zrx.MA_25 = 28
        zrx.MA_50 = 50
        zrx.MA_100 = 100
        zrx.MA_200 = 200

        zrx.MAX_ARRAY = 130

        zrx.HISTORICAL_DATA_TIMEFRAME = "200 minutes ago UTC"

        zrx.VOLUME_MIN = 0

        zrx.ORDER_FIRST_STOP_LOSS_PERCENT = 0.01
        zrx.ORDER_STOP_LOSS_PERCENT = 0.01

        zrx.USE_GENERIC_STRATEGY = True

        self.all_symbol_settings.append(zrx)

    def ethusdt(self):
        eth = SymbolParameters()

        eth.symbol_name = "ETHUSDT"

        eth.ATR_PERIODS = 15
        eth.RSI_PERIODS = 10
        eth.ADX_PERIODS = 30

        eth.BB_PERIOD = 15
        eth.BB_STD_DEV_UPPER = 2
        eth.BB_STD_DEV_LOWER = 2

        eth.MA_5 = 8
        eth.MA_15 = 18
        eth.MA_25 = 28
        eth.MA_50 = 50
        eth.MA_100 = 100
        eth.MA_200 = 200

        eth.MAX_ARRAY = 130

        eth.HISTORICAL_DATA_TIMEFRAME = "200 minutes ago UTC"

        eth.VOLUME_MIN = 0

        eth.ORDER_FIRST_STOP_LOSS_PERCENT = 0.01
        eth.ORDER_STOP_LOSS_PERCENT = 0.01

        eth.USE_GENERIC_STRATEGY = True

        self.all_symbol_settings.append(eth)

    def grab_symbol_settings_with_name(self, symbol_name):
        for symbol in self.all_symbol_settings:
            if symbol.symbol_name == symbol_name:
                return symbol

    def start_symbol_settings(self):
        self.ethusdt()
        self.zrxusdt()
        self.atomusdt()
        self.batusdt()
        self.storj()


class Symbol:

    # region Variables
    symbol_specific_parameters = SymbolParameters()

    symbol_name = ""

    counter = 0

    # Websocket
    socket_address = "wss://stream.binance.com:9443/ws/"
    socket_end = "@kline_1m"
    final_socket_name = ""
    start_client = None

    open_array = []
    high_array = []
    low_array = []
    close_array = []

    timestamp_array = []

    timestamp_numpy = numpy.array(timestamp_array)

    open_numpy = numpy.array(open_array)
    high_numpy = numpy.array(high_array)
    low_numpy = numpy.array(low_array)
    close_numpy = numpy.array(close_array)

    # Price
    current_period = 0
    current_time = 0
    current_low = 0.0
    current_open = 0.0
    current_high = 0.0
    current_close = 0.0

    volume = 0.0

    # Indicators
    rsi = 100
    rsi_crossed_down_already = False
    rsi_crossed_up = True
    rsi_previous = 100
    atr = 0.0
    adx = 0
    bbw = 0.0

    # Moving Averages
    ma_5 = 0.0
    ma_15 = 0.0
    ma_25 = 0.0
    ma_50 = 0.0
    ma_100 = 0.0
    ma_200 = 0.0

    buy_condition_met = False
    sell_condition_met = False

    # Order Info
    stop_loss_price = 0.0
    stop_loss_anchor_price = 0.0
    purchase_price = 0.0
    can_place_order = True  # DEF False
    active_order = False

    # endregion

    # region Websocket
    def on_message(self, websocket, message):
        try:
            self.process_message(message)
        except Exception as e:
            db(e)

    def on_open(self, websocket):
        try:
            db(self.symbol_name + str(" Opened Connection"))
        except Exception as e:
            db(e)

    def on_close(self, websocket):
        try:
            db(self.symbol_name + str(" Closed Connection"))
        except Exception as e:
            db(e)

    def on_error(self, websocket):
        try:
            db(self.symbol_name + str(" Connection Error"))
        except Exception as e:
            db(e)

    # endregion

    def start_symbol(self, name, symbol_parameters):
        db("Start Symbol" + str(name))
        self.start_client = ClientManager.client
        self.set_symbol_name(name)
        self.symbol_specific_parameters = symbol_parameters
        self.get_history_for_indicators()
        Broadcaster.add_subscriber_to_broadcaster(self.symbol_loop, 5)

    def set_symbol_name(self, symbol_name):
        db("Set Symbol Name")
        self.symbol_name = symbol_name
        self.final_socket_name = self.socket_address + self.symbol_name.lower() + self.socket_end

    def start_websocket(self):
        try:
            db("Start Websocket " + str(self.final_socket_name))
            ws = websocket.WebSocketApp(
                self.final_socket_name,
                on_open=self.on_open,
                on_message=self.on_message,
                on_close=self.on_close,
                on_error=self.on_error)

            db("Symbol " + str(self.final_socket_name) + " Started")

            ws.run_forever()
        except Exception as e:
            db(e)

    def symbol_loop(self):
        self.set_all_indicators()
        self.check_for_buy_conditions()
        self.check_for_sell_condition()
        self.get_current_candle_with_history()

    def process_message(self, message):

        # db(str(self.final_socket_name) + " Message being processed")

        json_message = json.loads(message)

        raw_candle_data = json_message['k']

        # self.current_time = float(raw_candle_data["T"])
        self.current_open = float(raw_candle_data["o"])
        self.current_close = float(raw_candle_data["c"])
        self.current_high = float(raw_candle_data["h"])
        self.current_low = float(raw_candle_data["l"])

        self.volume = float(raw_candle_data["v"])
        """
        # If Candle Closed
        if raw_candle_data['x']:                
            #
            if len(self.timestamp_numpy) > self.symbol_specific_parameters.MAX_ARRAY:
                self.timestamp_numpy = numpy.delete(self.timestamp_numpy, 0)

            self.timestamp_numpy = numpy.append(self.timestamp_numpy, self.current_time)

            #
            if len(self.open_numpy) > self.symbol_specific_parameters.MAX_ARRAY:
                self.open_numpy = numpy.delete(self.open_numpy, 0)

            self.open_numpy = numpy.append(self.open_numpy, self.current_open)

            #
            if len(self.high_numpy) > self.symbol_specific_parameters.MAX_ARRAY:
                self.high_numpy = numpy.delete(self.high_numpy, 0)

            self.high_numpy = numpy.append(self.high_numpy, self.current_high)

            #
            if len(self.low_numpy) > self.symbol_specific_parameters.MAX_ARRAY:
                self.low_numpy = numpy.delete(self.low_numpy, 0)

            self.low_numpy = numpy.append(self.low_numpy, self.current_low)

            #
            if len(self.close_numpy) > self.symbol_specific_parameters.MAX_ARRAY:
                self.close_numpy = numpy.delete(self.close_numpy, 0)

            self.close_numpy = numpy.append(self.close_numpy, self.current_close)

            db("CANDLE CLOSED AT: " + str(self.close_numpy))

            self.current_period += 1
        """

    def get_current_candle_with_history(self):
        self.counter += 1

        if not self.counter == 60:
            return

        self.counter = 0

        # REPLACE WITH HISTORICAL DATA MAKE SURE THAT YOU DONT ADD SAME PRICES TO ARRAY
        klines = ClientManager.client.get_historical_klines(self.symbol_name, Client.KLINE_INTERVAL_1MINUTE,
                                                            "3 minute ago UTC")

        for kline in klines:
            # Get Time
            unix_time = float(kline[0])
            unix_time_divided = int(kline[0] / 1000)
            date_time = datetime.fromtimestamp(unix_time_divided)

            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])

            if len(self.timestamp_numpy) > 0:
                # Compare previous with current
                if unix_time_divided > self.timestamp_numpy[-1]:
                    self.timestamp_numpy = numpy.append(self.timestamp_numpy, unix_time_divided)

                    # Close
                    self.close_numpy = numpy.append(self.close_numpy, close_price)

                    # High
                    self.high_numpy = numpy.append(self.high_numpy, high_price)

                    # Low
                    self.low_numpy = numpy.append(self.low_numpy, low_price)

                    # Open
                    self.open_numpy = numpy.append(self.open_numpy, open_price)
            else:
                self.timestamp_numpy = numpy.append(self.timestamp_numpy, unix_time_divided)
                self.open_numpy = numpy.append(self.open_numpy, open_price)
                self.low_numpy = numpy.append(self.low_numpy, low_price)
                self.high_numpy = numpy.append(self.high_numpy, high_price)
                self.close_numpy = numpy.append(self.close_numpy, close_price)

        for i in reversed(range(15)):
            db(self.symbol_name
               + "  LAST 15 CANDLES  "
               + str(datetime.fromtimestamp(self.timestamp_numpy[-i]))
               + " PRICE: "
               + str(self.close_numpy[-i]))

    def get_history_for_indicators(self):
        klines = self.start_client.get_historical_klines(
            self.symbol_name, Client.KLINE_INTERVAL_1MINUTE,
            self.symbol_specific_parameters.HISTORICAL_DATA_TIMEFRAME)

        for item in klines:
            self.timestamp_numpy = numpy.append(self.timestamp_numpy, int(float(item[0]) / 1000))
            self.open_numpy = numpy.append(self.open_numpy, float(item[1]))
            self.high_numpy = numpy.append(self.high_numpy, float(item[2]))
            self.low_numpy = numpy.append(self.low_numpy, float(item[3]))
            self.close_numpy = numpy.append(self.close_numpy, float(item[4]))

        klines.clear()

    def set_all_indicators(self):

        # Make sure all arrays are same size...
        min_length = [len(self.close_numpy), len(self.high_numpy), len(self.low_numpy), len(self.open_numpy)]

        minn = min(min_length)

        # RSI
        rsi_array = talib.RSI(self.close_numpy[-minn:], self.symbol_specific_parameters.RSI_PERIODS)
        self.rsi = rsi_array[-1]

        # ADX
        adxp = self.symbol_specific_parameters.ADX_PERIODS
        self.adx = talib.ADX(self.high_numpy[-minn:], self.low_numpy[-minn:], self.close_numpy[-minn:], adxp)[-1]

        """
        handler = TA_Handler(
            symbol=self.symbol_name,
            exchange="BINANCE",
            screener="crypto",
            interval="1m",
            timeout=None
        )
        analysis = handler.get_analysis()
        self.adx = analysis.indicators['ADX']
        """

        # BBW
        upper, middle, lower = talib.BBANDS(
            self.close_numpy[-minn:], self.symbol_specific_parameters.BB_PERIOD,
            self.symbol_specific_parameters.BB_STD_DEV_UPPER,
            self.symbol_specific_parameters.BB_STD_DEV_LOWER, 0)

        last_bb_upper = upper[-1]
        last_bb_lower = lower[-1]
        last_bb_middle = middle[-1]

        self.bbw = (last_bb_upper - last_bb_lower) / last_bb_lower

        # ATR
        atrp = self.symbol_specific_parameters.ATR_PERIODS

        if minn > atrp * 3:
            self.atr = \
            talib.ATR(self.high_numpy[-(atrp * 3):],
                      self.low_numpy[-(atrp * 3):],
                      self.close_numpy[-(atrp * 3):],
                      atrp)[-1]
        else:
            self.atr = \
            talib.ATR(self.high_numpy[-minn:],
                      self.low_numpy[-minn:],
                      self.close_numpy[-minn:],
                      atrp)[-1]

        # MA
        # REMOVE DUPES
        close_numpy_without_duplicates = [i[0] for i in groupby(self.close_numpy)]
        close_numpy_without_duplicates = numpy.array(close_numpy_without_duplicates)

        open_numpy_without_duplicates = [i[0] for i in groupby(self.open_numpy)]
        open_numpy_without_duplicates = numpy.array(open_numpy_without_duplicates)

        low_numpy_without_duplicates = [i[0] for i in groupby(self.low_numpy)]
        low_numpy_without_duplicates = numpy.array(low_numpy_without_duplicates)

        high_numpy_without_duplicates = [i[0] for i in groupby(self.high_numpy)]
        high_numpy_without_duplicates = numpy.array(high_numpy_without_duplicates)

        #
        self.ma_5 = talib.MA(low_numpy_without_duplicates[-minn:], self.symbol_specific_parameters.MA_5)[-1]
        self.ma_15 = talib.MA(low_numpy_without_duplicates[-minn:], self.symbol_specific_parameters.MA_15)[-1]
        self.ma_25 = talib.MA(low_numpy_without_duplicates[-minn:], self.symbol_specific_parameters.MA_25)[-1]
        self.ma_50 = talib.MA(low_numpy_without_duplicates[-minn:], self.symbol_specific_parameters.MA_50)[-1]
        self.ma_100 = talib.MA(high_numpy_without_duplicates[-minn:], self.symbol_specific_parameters.MA_100)[-1]
        self.ma_200 = talib.MA(high_numpy_without_duplicates[-minn:], self.symbol_specific_parameters.MA_200)[-1]

    def check_for_buy_conditions(self):
        self.buy_ma_cross_strategy()
        # Some Other Strategy

    def check_for_sell_condition(self):
        self.sell_ma_cross_strategy()

    def print_buy_parameters(self):
        note("Bought " + self.symbol_name)
        note("MA_25 " + str(self.ma_25))
        note("MA_100 " + str(self.ma_100))
        note(str(self.symbol_name) + " Stop Loss Set At " + str(self.stop_loss_price))

    def print_sell_parameters(self):
        note("Sold " + self.symbol_name)
        note("Stop Loss Anchor " + str(self.stop_loss_anchor_price))
        note("MA_15 " + str(self.ma_15))
        note("MA_25 " + str(self.ma_25))
        note("MA_100 " + str(self.ma_100))

    def broker_buy_settings(self):
        self.active_order = True
        self.can_place_order = False
        self.print_buy_parameters()

    def broker_sell_settings(self):
        self.sell_condition_met = False
        self.active_order = False
        self.purchase_price = 0.0
        self.stop_loss_price = 0.0
        self.print_sell_parameters()

    # region Strategies

    def buy_ma_cross_strategy(self):
        if self.ma_25 > self.ma_100 and self.adx > 30 and self.volume > self.symbol_specific_parameters.VOLUME_MIN:
            if self.can_place_order:
                self.buy_condition_met = True

            # Also
            if self.active_order:
                self.can_place_order = False
                self.buy_condition_met = False
        else:
            if self.active_order:
                self.can_place_order = False
                self.buy_condition_met = False
            else:
                self.buy_condition_met = False
                self.can_place_order = True

    def sell_ma_cross_strategy(self):
        if not self.active_order:
            return

        self.stop_loss_anchor_price = self.ma_15

        # Set stop loss
        if self.stop_loss_price < self.stop_loss_anchor_price - (self.stop_loss_anchor_price * self.symbol_specific_parameters.ORDER_STOP_LOSS_PERCENT):
            self.stop_loss_price = self.stop_loss_anchor_price - (self.stop_loss_anchor_price * self.symbol_specific_parameters.ORDER_STOP_LOSS_PERCENT)

        if self.stop_loss_price == 0.0 or self.purchase_price == 0.0:
            self.sell_condition_met = False
            return

        if self.stop_loss_anchor_price < self.stop_loss_price:
            note("Sell Condition True:  Anchor price is Less than Stop Loss Price")
            self.sell_condition_met = True

        if self.ma_25 < self.ma_100:
            self.sell_condition_met = True

    # endregion


class SymbolManager:

    sell_symbols = []
    buy_symbols = []

    all_symbol_settings = AllSymbolParameters()

    all_symbols: List[Symbol] = []

    period = 0

    def start_symbol_manager(self):
        # Set symbol settings
        self.all_symbol_settings = AllSymbolParameters()
        self.all_symbol_settings.start_symbol_settings()

        file1 = open(r'multiple_symbol_names.txt', 'r')
        all_lines = file1.readlines()
        all_line_length = len(all_lines)

        for line in all_lines:
            symbol_name = str(line).strip()

            print("Initializing " + str(all_line_length) + " " + str(symbol_name))

            symbol_settings = self.all_symbol_settings.grab_symbol_settings_with_name(symbol_name)

            temp_symbol = Symbol()

            temp_symbol.start_symbol(symbol_name, symbol_settings)

            self.all_symbols.append(temp_symbol)

            symbol_thread = threading.Thread(target=self.start_symbol_websocket, args=(temp_symbol,))
            symbol_thread.start()

            all_line_length -= 1
            time.sleep(1)

        Broadcaster.add_subscriber_to_broadcaster(self.loop_read_all_symbols, 8)

    def start_symbol_websocket(self, symbol_object):
        symbol_object.start_websocket()

    def loop_read_all_symbols(self):
        self.check_for_order_signals()

    def check_for_order_signals(self):
        # if the list isn't empty
        if not self.all_symbols:
            db("All symbols list empty")
            return

        temp_all_symbols = sorted(self.all_symbols, key=lambda x: (x.volume, x.bbw))
        temp_all_symbols.reverse()

        for i in range(len(temp_all_symbols)):
            # If buy
            if temp_all_symbols[i].buy_condition_met:
                self.buy_symbols.append(temp_all_symbols[i].symbol_name)
            else:
                if temp_all_symbols[i].symbol_name in self.buy_symbols:
                    self.buy_symbols.remove(temp_all_symbols[i].symbol_name)

            # if sell
            if temp_all_symbols[i].sell_condition_met:
                self.sell_symbols.append(temp_all_symbols[i].symbol_name)
            else:
                if temp_all_symbols[i].symbol_name in self.sell_symbols:
                    self.sell_symbols.remove(temp_all_symbols[i].symbol_name)

    def get_price_with_symbol(self, _symbol_name):
        for s in self.all_symbols:
            if s.symbol_name == _symbol_name:
                return s.current_close

    def get_symbol_with_name(self, _symbol_name):
        for s in self.all_symbols:
            if s.symbol_name == _symbol_name:
                return s


class BrokerManager:

    # Constants
    TRADE_USD = 250
    FAKE_ORDERS = True
    HAVE_DISCOUNT_FEE = True

    # FEE
    BROKER_FEE = .001
    BROKER_DISCOUNT_FEE = .00075

    # region Variables

    # Messages
    interval = 0

    # Time
    begin_time = datetime.now()
    time_elapsed = datetime.now()

    # Orders
    buy_this_symbol = ""
    sell_this_symbol = ""
    successful_buy_orders = 0
    successful_sell_orders = 0
    failed_buy_orders = 0
    failed_sell_orders = 0

    # USD
    current_quantity_of_symbol_purchased = 0

    # Order Current
    current_symbol = Symbol()
    order_active = False
    last_sold_price = 0.0
    current_profit_and_loss = 0.0
    current_order_profit_and_loss_percent = 0.0

    # Fees
    total_fees_acquired = 0.0

    # Profits and losses
    total_net_profit_and_loss = 0.0
    total_net_percent_profit_and_loss = 0.0

    # Positive Negative
    positive_percent_gains = 0.0
    positive_profits = 0.0
    negative_percent_losses = 0.0
    negative_losses = 0.0

    # endregion

    # Functions
    @staticmethod
    def start_broker():
        db("Composite Bot Started " + str(datetime.now()))

        BrokerManager.begin_time = datetime.now()

        Broadcaster.add_subscriber_to_broadcaster(BrokerManager.broker_loop, 10)

    @staticmethod
    def broker_loop():
        BrokerManager.interval += 1
        BrokerManager.time_elapsed = datetime.now() - BrokerManager.begin_time

        if BrokerManager.interval > 60:
            BrokerManager.check_for_buy_symbols()

            BrokerManager.check_for_sell_symbols()

            if BrokerManager.order_active:
                BrokerManager.update_current_order()

            BrokerManager.sell_under_right_conditions()

            BrokerManager.buy_under_right_condition()
            
    @staticmethod
    def check_for_buy_symbols():
        if not symbol_manager.buy_symbols:
            BrokerManager.buy_this_symbol = ""
            return

        BrokerManager.buy_this_symbol = symbol_manager.buy_symbols[0]

    @staticmethod
    def check_for_sell_symbols():
        if not symbol_manager.sell_symbols:
            BrokerManager.sell_this_symbol = ""
            return

        BrokerManager.sell_this_symbol = symbol_manager.sell_symbols[0]

    # Order
    @staticmethod
    def update_current_order():
        temp_stop_loss = BrokerManager.current_symbol.stop_loss_price

        if not BrokerManager.current_symbol.purchase_price == 0:
            BrokerManager.current_order_profit_and_loss_percent = \
                (temp_stop_loss - BrokerManager.current_symbol.purchase_price) / BrokerManager.current_symbol.purchase_price

        BrokerManager.current_profit_and_loss = BrokerManager.TRADE_USD * BrokerManager.current_order_profit_and_loss_percent
    
    @staticmethod
    def send_order_to_broker(client, side, quantity, symbol, order_type=ORDER_TYPE_MARKET):

        try:
            place_order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)

            if side == client.SIDE_BUY:
                order_info = place_order['fills']
                BrokerManager.current_symbol.purchase_price = float(order_info[0]['price'])
                note("Bought {} {} at: {}".format(symbol, quantity, BrokerManager.current_symbol.purchase_price))

            else:
                order_info = place_order['fills']
                BrokerManager.last_sold_price = float(order_info[0]['price'])
                note("Sold {} {} at: {}".format(symbol, quantity, BrokerManager.current_symbol.purchase_price))

            result = str(place_order)
            note("Order Result: {}".format(result))

        except Exception as e:
            note("an exception occurred - {}".format(e))
            return False

        return True

    # Buy
    @staticmethod
    def buy_under_right_condition():
        if BrokerManager.order_active:
            # db("Buy: Can't buy, order already active")
            return

        if BrokerManager.buy_this_symbol == "":
            # db("No buy signal found")
            return

        BrokerManager.current_symbol = symbol_manager.get_symbol_with_name(BrokerManager.buy_this_symbol)

        # note("Buy signal found")
        BrokerManager.buy()

    @staticmethod
    def buy():
        if BrokerManager.order_active:
            # note("Buy: Can't buy, order already active")
            return

        if BrokerManager.FAKE_ORDERS:
            note("Buy fake order")
            BrokerManager.buy_fake_order()

        else:
            note("Buy real order")
            BrokerManager.buy_real_order()

    @staticmethod
    def buy_fake_order():
        BrokerManager.current_quantity_of_symbol_purchased = \
            round(BrokerManager.TRADE_USD / BrokerManager.current_symbol.current_close, 6)

        #
        BrokerManager.successful_buy_orders += 1

        # Set price the order was set at
        BrokerManager.current_symbol.purchase_price = BrokerManager.current_symbol.current_close

        # Tell symbol it is purchased
        BrokerManager.current_symbol.broker_buy_settings()

        # Fees
        BrokerManager.buy_process_fees()

        #
        BrokerManager.order_active = True

        note("Bought fake order: {} of {} at {} with ${} at {}".format(
            BrokerManager.current_quantity_of_symbol_purchased,
            BrokerManager.current_symbol.symbol_name,
            BrokerManager.current_symbol.purchase_price,
            BrokerManager.TRADE_USD,
            datetime.now()))

    @staticmethod
    def buy_real_order():
        # Round the quantity to avoid errors
        BrokerManager.current_quantity_of_symbol_purchased = \
            round(BrokerManager.TRADE_USD / BrokerManager.current_symbol.current_close, 6)

        order_succeeded = \
            BrokerManager.send_order_to_broker(ClientManager.client, SIDE_BUY, BrokerManager.current_quantity_of_symbol_purchased, BrokerManager.current_symbol.symbol_name)

        # If the order succeeded
        if order_succeeded:
            #
            BrokerManager.order_active = True

            # Tell symbol it is purchased
            BrokerManager.current_symbol.broker_buy_settings()

            #
            BrokerManager.successful_buy_orders += 1

            # Fees
            BrokerManager.buy_process_fees()

        else:
            note("Order failed.")
            BrokerManager.failed_buy_orders += 1

        note("Bought real order: {} of {} at {} with ${} at {}".format(
            BrokerManager.current_quantity_of_symbol_purchased,
            BrokerManager.current_symbol.symbol_name,
            BrokerManager.current_symbol.purchase_price,
            BrokerManager.TRADE_USD,
            datetime.now()))

    @staticmethod
    def buy_process_fees():
        # Later when using different kinds of orders must make conditions e.g. TRADE_USD
        if BrokerManager.HAVE_DISCOUNT_FEE:
            note("Have discount fee")

            # Get Fee
            fee_amount = BrokerManager.TRADE_USD * BrokerManager.BROKER_DISCOUNT_FEE

            # Subtract Fee From Profits
            BrokerManager.total_net_profit_and_loss -= fee_amount

            # Total fees
            BrokerManager.total_fees_acquired += fee_amount

            # Subtract percent fee from percent profits
            BrokerManager.total_net_percent_profit_and_loss -= BrokerManager.BROKER_DISCOUNT_FEE
        else:
            note("Don't have discount fee")

            # Get Fee
            fee_amount = BrokerManager.TRADE_USD * BrokerManager.BROKER_FEE

            # Subtract Fee From Profits
            BrokerManager.total_net_profit_and_loss -= fee_amount

            # Total fees
            BrokerManager.total_fees_acquired += fee_amount

            # Subtract percent fee from percent profits
            BrokerManager.total_net_percent_profit_and_loss -= BrokerManager.BROKER_FEE

    # Sell
    @staticmethod
    def sell_under_right_conditions():

        # note("Sell under the right conditions.")

        if not BrokerManager.order_active:
            # note("Sell: Order is not active.")
            return

        if BrokerManager.sell_this_symbol == "":
            # note("Sell: Don't sell, packet has no sell signal")
            return

        if BrokerManager.FAKE_ORDERS:
            note("Sell fake order.")
            BrokerManager.sell_fake_order()
            return

        note("Sell real order.")
        BrokerManager.sell_real_order()

    @staticmethod
    def sell_real_order():
        order_succeeded = BrokerManager.send_order_to_broker(ClientManager.client, SIDE_SELL, BrokerManager.current_quantity_of_symbol_purchased,
                                                             BrokerManager.current_symbol.symbol_name)

        if order_succeeded:
            # Tell symbol it is purchased
            BrokerManager.current_symbol.broker_sell_settings()

            # Set the difference
            BrokerManager.total_net_percent_profit_and_loss += BrokerManager.current_order_profit_and_loss_percent

            # Set current profits
            BrokerManager.total_net_profit_and_loss += \
                BrokerManager.current_order_profit_and_loss_percent * BrokerManager.last_sold_price * BrokerManager.current_quantity_of_symbol_purchased

            #
            BrokerManager.successful_sell_orders += 1

            #
            if BrokerManager.current_profit_and_loss > 0:
                BrokerManager.positive_profits += BrokerManager.current_profit_and_loss
                BrokerManager.positive_percent_gains += BrokerManager.current_order_profit_and_loss_percent
            else:
                BrokerManager.negative_losses += BrokerManager.current_profit_and_loss
                BrokerManager.negative_percent_losses += BrokerManager.current_order_profit_and_loss_percent

            # Close
            note("Sold real order: {} of {} at {} for a {} profit ({}%) at {}".format(
                BrokerManager.current_quantity_of_symbol_purchased,
                BrokerManager.current_symbol.symbol_name,
                BrokerManager.last_sold_price,
                round(BrokerManager.current_profit_and_loss, 4),
                round(BrokerManager.current_order_profit_and_loss_percent * 100, 4),
                datetime.now()))

            BrokerManager.close_order_on_sell()
            return

        else:
            BrokerManager.failed_sell_orders += 1
            # Try again next message
            return

    @staticmethod
    def sell_fake_order():
        # Tell symbol it is purchased
        BrokerManager.current_symbol.broker_sell_settings()

        # Set the difference
        BrokerManager.total_net_percent_profit_and_loss += BrokerManager.current_order_profit_and_loss_percent

        # Set current profits
        BrokerManager.total_net_profit_and_loss += \
            BrokerManager.current_order_profit_and_loss_percent * BrokerManager.current_symbol.current_close * BrokerManager.current_quantity_of_symbol_purchased

        #
        BrokerManager.successful_sell_orders += 1

        #
        if BrokerManager.current_profit_and_loss > 0:
            BrokerManager.positive_profits += BrokerManager.current_profit_and_loss
            BrokerManager.positive_percent_gains += BrokerManager.current_order_profit_and_loss_percent
        else:
            BrokerManager.negative_losses += BrokerManager.current_profit_and_loss
            BrokerManager.negative_percent_losses += BrokerManager.current_order_profit_and_loss_percent

        note("Sold fake order: {} of {} at {} for a {} profit ({}%) at {}".format(
            BrokerManager.current_quantity_of_symbol_purchased,
            BrokerManager.current_symbol.symbol_name,
            BrokerManager.current_symbol.current_close,
            round(BrokerManager.current_profit_and_loss, 4),
            round(BrokerManager.current_order_profit_and_loss_percent * 100, 4),
            datetime.now()))

        BrokerManager.close_order_on_sell()

    @staticmethod
    def close_order_on_sell():
        BrokerManager.last_sold_price = 0
        BrokerManager.current_profit_and_loss = 0
        BrokerManager.current_order_profit_and_loss_percent = 0
        BrokerManager.order_active = False


class DisplayMonitor:

    # region Variables
    table_headers = ["Symbol", "Close", "Last Close", "100 MA", "50 MA", "28 MA",
                      "18 MA", "5 MA", "ADX", "VOL", "BUY", "SELL", "ACTIVE", "PLACEABLE"]

    app = dash.Dash(__name__)

    app.layout = html.Div(
        children=
        [
            html.H4(children='T Composite Trader'),
            html.Img(src='Assets/Typh.png'),
            html.Div(id="broker_info"),
            html.Div(id='update_metrics'),
            dcc.Interval(id='interval-component', interval=1 * 999, n_intervals=0)
        ]
    )
    # endregion

    @staticmethod
    def make_table_array_with_all_symbols():
        all_columns = []

        if symbol_manager.all_symbols:
            for symbol in symbol_manager.all_symbols:
                name = symbol.symbol_name
                close = round(symbol.current_close, 4)
                last_close = round(float(symbol.close_numpy[-1]), 4)
                ma100 = round(symbol.ma_100, 4)
                ma50 = round(symbol.ma_50, 4)
                ma25 = round(symbol.ma_25, 4)
                ma15 = round(symbol.ma_15, 4)
                ma5 = round(symbol.ma_5, 4)
                adx = round(symbol.adx, 0)
                vol = round(symbol.volume, 0)
                buy = str(symbol.buy_condition_met)
                sell = str(symbol.sell_condition_met)
                active = str(symbol.active_order)
                place = str(symbol.can_place_order)

                symbol_row = [name,
                              close,
                              last_close,
                              ma100,
                              ma50,
                              ma25,
                              ma15,
                              ma5,
                              adx,
                              vol,
                              buy,
                              sell,
                              active,
                              place]
                all_columns.append(symbol_row)

        return all_columns

    @staticmethod
    def order_info_to_string():
        order_info = []

        order_info.append("Time Elapsed: {}".format(BrokerManager.time_elapsed))
        order_info.append("Successful Sell Orders: {}".format(BrokerManager.successful_sell_orders))
        order_info.append("Successful Buy Orders: {}".format(BrokerManager.successful_buy_orders))
        order_info.append("Failed Sell Orders: {}".format(BrokerManager.failed_sell_orders))
        order_info.append("Failed Buy Orders: {}".format(BrokerManager.failed_buy_orders))

        #
        total_net_profit_and_loss_for_printing = round(BrokerManager.total_net_profit_and_loss, 2)
        order_info.append("Total Net Profit and Loss: ${}".format(total_net_profit_and_loss_for_printing))

        total_net_percent_profit_and_loss_for_printing = round(BrokerManager.total_net_percent_profit_and_loss * 100, 4)
        order_info.append("Total Net Percent Profit and Loss: {}%".format(total_net_percent_profit_and_loss_for_printing))

        total_fees_acquired_for_printing = round(BrokerManager.total_fees_acquired, 2)
        order_info.append("Total Fees Acquired: ${}".format(-total_fees_acquired_for_printing))

        # Active Orders
        order_info.append("---------- Active Order Status ----------")
        order_info.append("Active order: {}".format(BrokerManager.order_active))

        if BrokerManager.order_active:
            current_profit_and_loss_percent_for_printing = round((BrokerManager.current_order_profit_and_loss_percent * 100), 6)
            current_profit_and_loss_for_printing = round(BrokerManager.current_profit_and_loss, 2)

            order_info.append("-------- Profit and Loss: $ {} ({}%) ---------".format(
                current_profit_and_loss_for_printing, current_profit_and_loss_percent_for_printing))
            order_info.append("Purchased Symbol: {}".format(BrokerManager.current_symbol.symbol_name))
            order_info.append("Purchase Amount: ${}".format(BrokerManager.TRADE_USD))
            order_info.append("Purchase quantity: {}".format(BrokerManager.current_quantity_of_symbol_purchased))
            order_info.append("Current price : {}".format(BrokerManager.current_symbol.current_close))
            order_info.append("Purchase Price: {}".format(BrokerManager.current_symbol.purchase_price))
            temp_stop_loss = round(BrokerManager.current_symbol.stop_loss_price, 4)
            order_info.append("Stop Loss Price: {}".format(temp_stop_loss))

        return order_info

    @staticmethod
    @app.callback(Output('update_metrics', 'children'),
                  Input('interval-component', 'n_intervals'))
    def update_metrics(interval):
        all_columns = DisplayMonitor.make_table_array_with_all_symbols()

        if len(all_columns) == 0:
            column = [str(0)]
            all_columns = [column]

        # Input array of array and get table
        return html.Table \
                (
                [
                    # Header Array
                    html.Thead(html.Tr([html.Th(header) for header in DisplayMonitor.table_headers])),
                    html.Tbody(
                        [
                            html.Tr
                                (
                                [
                                    html.Td(all_columns[row][column])
                                    for column in range(len(all_columns[row]))
                                ]
                            )
                            # FOR HOW EVER MANY ROWS THERE ARE DO ABOVE
                            for row in range(len(all_columns))
                        ]
                    )
                ]
            )

    @staticmethod
    @app.callback(Output('broker_info', 'children'),
                  Input('interval-component', 'n_intervals'))
    def broker_info(interval):
        order_info_array = DisplayMonitor.order_info_to_string()
        return html.Table \
                (
                [
                    html.Tbody(
                        [
                            html.Tr
                                (
                                [
                                    html.Td(order_info_array[row])
                                ]
                            )
                            # FOR HOW EVER MANY ROWS THERE ARE DO ABOVE
                            for row in range(len(order_info_array))
                        ]
                    )
                ]
            )

    @staticmethod
    def start_display_monitor():
        DisplayMonitor.app.run_server()


class Broadcaster:

    all_listeners = []

    class BroadcasterListener:

        method = None
        priority = 0

        def __init__(self, _method, _priority):
            self.method = _method
            self.priority = _priority

    @staticmethod
    def start_broadcaster():
        while True:
            if Broadcaster.all_listeners:
                Broadcaster.all_listeners = sorted(Broadcaster.all_listeners, key=lambda x: x.priority)
                for listener in Broadcaster.all_listeners:
                    listener.method()

            time.sleep(1)

    @staticmethod
    def add_subscriber_to_broadcaster(method, priority):
        listener = Broadcaster.BroadcasterListener(method, priority)

        Broadcaster.all_listeners.append(listener)


class ClientManager:
    client = Client(config.API_KEY, config.API_SECRET)
    counter = 0

    @staticmethod
    def start_client_manager():
        Broadcaster.add_subscriber_to_broadcaster(ClientManager.renew_client_every_minute, 33)

    @staticmethod
    def renew_client_every_minute():
        ClientManager.counter += 1
        if ClientManager.counter == 60:
            ClientManager.client = Client(config.API_KEY, config.API_SECRET)
            ClientManager.counter = 0



# region Debug

def note(log):
    file_object = open(r"composite_bot_order_log.txt", "a+")
    file_object.write("\n" + log)
    file_object.close()

def db(log):
    file_object = open(r"composite_bot_log.txt", "a+")
    file_object.write("\n" + log)
    file_object.close()

# endregion


# Start Broadcaster
broadcaster_thread = threading.Thread(target=Broadcaster.start_broadcaster, args=())
broadcaster_thread.start()

# Start Broker
broker = BrokerManager()
broker.start_broker()

# Start Symbol Manager
symbol_manager = SymbolManager()
symbol_manager.start_symbol_manager()


# Start Display Monitor
dm = DisplayMonitor()
dm_thread = threading.Thread(target=dm.start_display_monitor, args=())
dm_thread.start()
