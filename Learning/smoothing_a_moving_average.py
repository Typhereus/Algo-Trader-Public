import numpy
import talib
import sys
from numpy import genfromtxt
import plotly.graph_objects as go
import Backtesting.TBTLib.tbt_engine as t_engine
from typing import List
import Backtesting.TBTLib.tbt_order_manager as t_orders
from plotly.subplots import make_subplots
import random

# region Data
data_sheet = sys.path[1] + "/Data/ethusdt3days.csv"
historical_data = genfromtxt(data_sheet, delimiter=",")

time_stamp_array = numpy.array(historical_data[:, 0])

data_open_array = numpy.array(historical_data[:, 1])
data_high_array = numpy.array(historical_data[:, 2])
data_low_array = numpy.array(historical_data[:, 3])
data_close_array = numpy.array(historical_data[:, 4])

# endregion

#
moving_averages = talib.MA(data_close_array, 100)
simple_moving_averages = talib.SMA(data_close_array, 100)
exponential_moving_averages = talib.EMA(data_close_array, 100)
ma2 = talib.DEMA(data_close_array, 100)
#talib.

# Smoothing
smoothed_array = []
numpy_smoothed_array = numpy.array(smoothed_array)
prices_added_up_so_far = 0.0

for i in range(len(moving_averages)):
    index = i + 1

    price = moving_averages[i]

    prices_added_up_so_far += float(price)

    # print(prices_added_up_so_far)

    smoothed_price = float(prices_added_up_so_far / index)

    # print(smoothed_price)

    numpy_smoothed_array = numpy.append(numpy_smoothed_array, smoothed_price)

#for price in numpy_smoothed_array:
    # print(price)

# Plot
figure = go.Figure()
figure.add_trace(go.Scatter(name="Close",
                    x=time_stamp_array,
                    y=data_close_array,
                    line=dict(color="#919191")))

figure.add_trace(go.Scatter(name="MA", x=time_stamp_array, y=moving_averages))
figure.add_trace(go.Scatter(name="SMA", x=time_stamp_array, y=simple_moving_averages))
figure.add_trace(go.Scatter(name="EMA", x=time_stamp_array, y=exponential_moving_averages))
figure.add_trace(go.Scatter(name="DMA", x=time_stamp_array, y=ma2))
# figure.add_trace(go.Scatter(name="Smoothed MA", x=time_stamp_array, y=smoothed_array))
figure.show()

