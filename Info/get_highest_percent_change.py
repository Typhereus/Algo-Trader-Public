import Broker.config as config
from binance.client import Client
import csv
import sys
import time

client = Client(config.API_KEY, config.API_SECRET)

text_file = open(sys.path[1] + "/PriceActionTrading/OrderEndless/all_symbols.txt", "r")
symbol_names = text_file.read().split("\n")
text_file.close()

# Config
how_many_hours_ago = "72 hour ago UTC"


#
def get_highest_percentage():
    current_symbol_closes = []
    current_symbol_percentages = []

    all_symbols_and_percent = []

    candle_index = 0

    for symbol_name in symbol_names:
        print("Reading " + symbol_name)

        symbol_name += "USDT"
        candles = client.get_historical_klines(symbol_name, Client.KLINE_INTERVAL_1MINUTE, how_many_hours_ago)

        for c in candles:
            if candle_index == 0:
                candle_index += 1
                current_symbol_closes.append(float(c[4]))
                continue

            current_close = float(c[4])
            print(float(c[5]))

            percentage_change = 0
            # Get percent change
            if current_close > current_symbol_closes[-1]:
                starting_value = current_symbol_closes[-1]

                diff = current_close - starting_value

                percentage_change = (diff / starting_value)

            elif current_close < current_symbol_closes[-1]:
                starting_value = current_symbol_closes[-1]

                diff = starting_value - current_close

                percentage_change = (diff / starting_value)
            else:
                pass

            # print(percentage_change)
            current_symbol_percentages.append(percentage_change)
            current_symbol_closes.append(current_close)

        sum_all = sum(current_symbol_percentages) * 100
        all_symbols_and_percent.append([symbol_name, round(sum_all)])
        candle_index = 0
        current_symbol_percentages.clear()
        current_symbol_closes.clear()

        time.sleep(1)

    # define a sort key
    def sort_key(sym):
        return sym[1]


    # sort
    all_symbols_and_percent.sort(key=sort_key, reverse=True)

    print(how_many_hours_ago)
    for s in all_symbols_and_percent:
        print(s[0] + " " + str(s[1]) + " %")


def get_highest_percentage_volume_ratio():
    current_symbol_closes = []
    current_symbol_percentages = []
    current_symbol_volume = []

    all_symbols_and_percent_and_volume = []

    candle_index = 0

    for symbol_name in symbol_names:
        print("Reading " + symbol_name)

        symbol_name += "USDT"
        candles = client.get_historical_klines(symbol_name, Client.KLINE_INTERVAL_1MINUTE, how_many_hours_ago)

        for c in candles:
            if candle_index == 0:
                candle_index += 1
                current_symbol_closes.append(float(c[4]))
                continue

            current_close = float(c[4])

            # Vol
            volume = round(float(c[5]))
            current_symbol_volume.append(volume)

            percentage_change = 0
            # Get percent change
            if current_close > current_symbol_closes[-1]:
                starting_value = current_symbol_closes[-1]

                diff = current_close - starting_value

                percentage_change = (diff / starting_value)

            elif current_close < current_symbol_closes[-1]:
                starting_value = current_symbol_closes[-1]

                diff = starting_value - current_close

                percentage_change = (diff / starting_value)
            else:
                pass

            # print(percentage_change)
            current_symbol_percentages.append(percentage_change)
            current_symbol_closes.append(current_close)

        # Iteration Over

        #
        all_percent_sum = sum(current_symbol_percentages)
        all_volume_sum = sum(current_symbol_volume)
        ratio = (all_percent_sum / all_volume_sum)
        #print(ratio)
        #print(ratio * 10000000)
        ratio *= 100000
        # print(ratio)
        all_symbols_and_percent_and_volume.append([symbol_name, round(all_percent_sum, 2), all_volume_sum, ratio])

        # print(all_symbols_and_percent_and_volume[-1])
        #
        candle_index = 0

        # Clear
        current_symbol_percentages.clear()
        current_symbol_closes.clear()
        current_symbol_volume.clear()

        time.sleep(.5)

    # define a sort key
    def sort_key(sym):
        return sym[3]

    # sort
    all_symbols_and_percent_and_volume.sort(key=sort_key, reverse=False)

    print(how_many_hours_ago)
    for s in all_symbols_and_percent_and_volume:
        #ratio_rounded = round(s[3], 4)
        print(s[0] + " " + str(round(s[1] * 100)) + " %" + " VOL: " + f'{s[2]:,}' + " Ratio: " + f"{s[3]:.6f}")


# get_highest_percentage()
get_highest_percentage_volume_ratio()
