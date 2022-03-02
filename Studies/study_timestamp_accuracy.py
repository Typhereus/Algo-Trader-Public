import numpy
from numpy import genfromtxt
from datetime import datetime
import sys
import os

DATA_SHEET = sys.path[1] + "/Data/ethusdt30mins.csv"

historical_data = genfromtxt(DATA_SHEET, delimiter=",")

# Time
time_text_array = []

new_close = []
new_open = []
new_high = []
new_low = []

#
time_stamp_array = []

# Data Arrays
data_open_array = []
data_high_array = []
data_low_array = []
data_close_array = []

# Numpy Prices
all_open = numpy.array(new_open)
all_close = numpy.array(new_close)
all_high = numpy.array(new_high)
all_low = numpy.array(new_low)

time_stamp_array = numpy.array(historical_data[:, 0])

data_open_array = numpy.array(historical_data[:, 1])
data_high_array = numpy.array(historical_data[:, 2])
data_low_array = numpy.array(historical_data[:, 3])
data_close_array = numpy.array(historical_data[:, 4])

for i in range(len(data_close_array)):
    the_current_time_unix = int(time_stamp_array[i])
    date_unix = datetime.fromtimestamp(the_current_time_unix)
    the_current_time_text = str(date_unix)
    #time_text_array.append(the_current_time_text)

    #print(time_stamp_array[i])
    print(the_current_time_text)
