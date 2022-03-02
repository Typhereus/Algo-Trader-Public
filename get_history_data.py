import Broker.config as config
from binance.client import Client
import csv
import sys


def get_standard_data():
    client = Client(config.API_KEY, config.API_SECRET)

    csvfile = open(sys.path[1] + "/Data/ETH-60-DAYS.csv", "w", newline="")

    candlestick_writer = csv.writer(csvfile, delimiter=",")

    # forty_day_candles = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1MINUTE, "12 September, 2021", "15 September, 2021")

    candles = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1MINUTE, "86400 minute ago UTC")

    for candlestick in candles:
        candlestick[0] = candlestick[0] / 1000
        candlestick_writer.writerow(candlestick)

    csvfile.close()

get_standard_data()
