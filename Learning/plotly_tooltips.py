import Broker.config as config
from binance.client import Client
import csv
import numpy
from numpy import genfromtxt
from datetime import datetime
import sys
import os
import Backtesting.TBTLib.tbt_event_manager as t_events
import sys
import plotly.graph_objects as go
import Backtesting.TBTLib.tbt_engine as t_engine
from typing import List
import Backtesting.TBTLib.tbt_order_manager as t_orders


data_sheet = sys.path[1] + "/Data/ETH-10-MINUTES.csv"
historical_data = genfromtxt(data_sheet, delimiter=",")

time_stamp_array = numpy.array(historical_data[:, 0])

data_open_array = numpy.array(historical_data[:, 1])
data_high_array = numpy.array(historical_data[:, 2])
data_low_array = numpy.array(historical_data[:, 3])
data_close_array = numpy.array(historical_data[:, 4])

a = ["A","B","C","D","E","F","G","H","I","J"]
b = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

a_and_b = [a , b]

string_array = []

for i in range(len(a)):
    stringz = ""
    stringz += "<br>" + str(a[i]) + "</b>"
    stringz += "<br>" + str(b[i]) + "</b>"
    string_array.append(stringz)

print(string_array)

candlesticks = go.Candlestick(name="Candlesticks", x=time_stamp_array, open=data_open_array, high=data_high_array, low=data_low_array, close=data_close_array)

fig = go.Figure(data=[candlesticks])
fig.add_trace(go.Scatter(name="Close",
                         x=time_stamp_array,
                         y=data_close_array,
                         text=time_stamp_array,
                         customdata=string_array,
                         hovertemplate='%{customdata}',
                         line=dict(color="#919191")))

fig.show()
