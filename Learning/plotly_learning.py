import numpy
from numpy import genfromtxt
import sys
import plotly.graph_objects as graph_object
from plotly.subplots import make_subplots

# region Data
data_sheet = sys.path[1] + "/Data/ETH-10-MINUTES.csv"
historical_data = genfromtxt(data_sheet, delimiter=",")

time_stamp_array = numpy.array(historical_data[:, 0])

data_open_array = numpy.array(historical_data[:, 1])
data_high_array = numpy.array(historical_data[:, 2])
data_low_array = numpy.array(historical_data[:, 3])
data_close_array = numpy.array(historical_data[:, 4])
# endregion

fig = make_subplots(rows=2, cols=1)

candlesticks = graph_object.Candlestick(name="Candlesticks",
                                        x=time_stamp_array,
                                        open=data_open_array,
                                        high=data_high_array,
                                        low=data_low_array,
                                        close=data_close_array)

fig.append_trace(candlesticks, row=1, col=1)
fig.append_trace(candlesticks, row=2, col=1)

fig.show()
