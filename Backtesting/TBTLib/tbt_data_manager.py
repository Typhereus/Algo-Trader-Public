import numpy
from numpy import genfromtxt
from datetime import datetime
import sys
import os
import Backtesting.TBTLib.tbt_event_manager as t_events


class BacktestData:

    iteration_callback_function = ()

    enable_logging = None
    debugging = False

    # Data Csv Name
    data_csv_name = ""
    # historical_data = None

    # Period
    current_period = 0

    # Time
    time_text_array = []

    # Prices
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

    # Current
    the_current_time_text = ""
    the_current_time_unix = 0

    current_close = 0
    current_open = 0
    current_low = 0
    current_high = 0

    def __init__(self):
        pass

    def start_data(self):
        self.set_data()

    def set_data(self):
        # TODO: strategy set historical data with days

        if self.debugging:
            debug_data_sheet = os.path.abspath("/Data/ethusdt10days.csv")
            debug_historical_data = genfromtxt(debug_data_sheet, delimiter=",")

            self.time_stamp_array = numpy.array(debug_historical_data[:, 0])

            self.data_open_array = numpy.array(debug_historical_data[:, 1])
            self.data_high_array = numpy.array(debug_historical_data[:, 2])
            self.data_low_array = numpy.array(debug_historical_data[:, 3])
            self.data_close_array = numpy.array(debug_historical_data[:, 4])

        else:
            data_sheet = sys.path[1] + "/Data/" + self.data_csv_name
            historical_data = genfromtxt(data_sheet, delimiter=",")

            self.time_stamp_array = numpy.array(historical_data[:, 0])

            self.data_open_array = numpy.array(historical_data[:, 1])
            self.data_high_array = numpy.array(historical_data[:, 2])
            self.data_low_array = numpy.array(historical_data[:, 3])
            self.data_close_array = numpy.array(historical_data[:, 4])

        #
        self.log("T-len: ", len(self.time_stamp_array),
            "O-len: ", len(self.data_open_array),
            "H-len: ", len(self.data_high_array),
            "L-len: ", len(self.data_low_array),
            "C-len: ", len(self.data_close_array))

    def initialize_callback(self, _iteration_callback_function ):
        #
        self.iteration_callback_function = _iteration_callback_function

    def loop_data(self):
        for i in range(len(self.data_close_array)):
            self.current_period += 1

            #
            self.current_close = self.data_close_array[i]
            self.current_open = self.data_open_array[i]
            self.current_low = self.data_low_array[i]
            self.current_high = self.data_high_array[i]

            # Prices
            self.all_open = numpy.append(self.all_open, self.current_open)
            self.all_close = numpy.append(self.all_close, self.current_close)
            self.all_high = numpy.append(self.all_high, self.current_high)
            self.all_low = numpy.append(self.all_low, self.current_low)

            # Time
            self.the_current_time_unix = int(self.time_stamp_array[i])
            date_unix = datetime.fromtimestamp(self.the_current_time_unix)
            self.the_current_time_text = str(date_unix)
            self.time_text_array.append(self.the_current_time_text)

            self.log("T:", self.the_current_time_text,
                " O:", self.current_open,
                " H:", self.current_open,
                " L:", self.current_low,
                " C:", self.current_close)

            #
            self.iteration_callback_function()

    def log(self, *logg):
        try:
            if self.enable_logging:
                file_object = open(sys.path[1] + "/Backtesting/TBTLib/tbt_data_manager_log.txt", "a+")
                all_logs = ""

                for l in logg:
                    all_logs += str(l) + " "

                all_logs += "\n"
                file_object.write(all_logs)
                file_object.close()

        except:
            pass