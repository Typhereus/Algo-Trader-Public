import plotly.graph_objects as go
import Backtesting.TBTLib.tbt_engine as t_engine
from typing import List
import Backtesting.TBTLib.tbt_order_manager as t_orders
from plotly.subplots import make_subplots
import random

class BacktestPlotter:
    engine = None  # type: t_engine.BacktestEngine
    
    figure = None
    list_of_orders: List[t_orders.BacktestOrders.ListOfOrders] = []
    list_of_indicators = []

    class IndicatorPlot:
        name = ""
        list_of_values = None  # Numpy Array
        color = ""

        def __init__(self, _name, _list_of_values, _color):
            self.name = _name
            self.list_of_values = _list_of_values
            self.color = _color

    def __init__(self, _engine):
        self.engine = _engine
        self.list_of_orders: List[t_orders.BacktestOrders.ListOfOrders] = []
        self.list_of_indicators = []

    def plot_all(self):
        for ma_indicator in self.engine.orders.indicators.moving_average_all_objects:
            r = lambda: random.randint(0, 255)
            s = '#%02X%02X%02X' % (r(), r(), r())
            self.add_indicator(ma_indicator.name, ma_indicator.prices_all, s)

        self.create_chart(
            self.engine.orders.data.time_text_array,
            self.engine.orders.data.all_open,
            self.engine.orders.data.all_high,
            self.engine.orders.data.all_low,
            self.engine.orders.data.all_close,
            self.engine.orders.list_of_orders
        )
        # self.update_tooltips()

        self.figure.show()

    def add_indicator(self, _name, _list_of_values, _color):
        self.list_of_indicators.append(self.IndicatorPlot(_name, _list_of_values, _color))

    def create_chart(self, dates, open_prices, high, low, close, list_of_orders):
        # Create Subplots
        self.figure = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[1, 0])

        def plot_main():

            # Create Candlesticks
            # candlesticks = go.Candlestick(name="Candlesticks", x=dates, open=open_prices, high=high, low=low, close=close)

            trace = go.Scatter(name="Close",
                                             x=self.engine.orders.data.time_text_array,
                                             y=self.engine.orders.data.all_close,
                                             customdata=self.engine.orders.tooltip_info,
                                             hovertemplate='%{customdata}',
                                             line=dict(color="#919191"))
            
            self.figure.append_trace(trace, row=1, col=1)
            #self.figure.add_trace(trace)

            # Indicators
            for item in self.list_of_indicators:
                self.figure.add_trace(go.Scatter(name=item.name, x=dates, y=item.list_of_values, line=dict(color=item.color)))

            # Set Color and Size
            self.figure.update_layout(width=1900, height=900,
                              margin=dict(l=10, r=10, b=10, t=10),
                              font=dict(size=10, color="#e1e1e1"),
                              paper_bgcolor="#1e1e1e",
                              plot_bgcolor="#1e1e1e")

            self.figure.update_xaxes(
                gridcolor="#1f292f",
                showgrid=True, fixedrange=True
            )
            self.figure.update_yaxes(
                gridcolor="#1f292f",
                showgrid=True
            )

            # Set Range slider
            self.figure.update_xaxes(rangeslider_thickness=0.05)
            self.figure.update_yaxes(fixedrange=False)
        plot_main()

        def plot_orders():
            #
            for plotted_order in list_of_orders:
                # Debug
                """
                if plotted_order.buy:
                    print("BUY: " + str(plotted_order.buy) + "  " + plotted_order.date_time)
    
                if plotted_order.sell:
                    print("SELL: " + str(plotted_order.buy) + "  " + plotted_order.date_time)
                """

                #
                date = plotted_order.date_time
                if plotted_order.buy:
                    self.figure.add_vline(x=date, line_color="#ffa600")

                if plotted_order.sell:
                    if plotted_order.gained_profit:
                        self.figure.add_vline(x=date, line_color="#0dff00")
                    else:
                        self.figure.add_vline(x=date, line_color="#ff0000")
        plot_orders()

        def plot_additional():
            #
            print("Plotting additional")
            print(str(len(self.engine.orders.additional_plots)))
            for additional_plots in self.engine.orders.additional_plots:
                if additional_plots.trend_set:
                    self.figure.add_vline(x=additional_plots.date, line_color="#0011ff")
        # plot_additional()

        def plot_additional_indicators():
            # RSI
            rsi = go.Scatter(name="RSI",
                            x=self.engine.orders.data.time_text_array,
                            y=self.engine.indicators.rsi_all[0].all_rsi,
                            line=dict(color="#919191"))
            # rsi.update(layout_xaxis_rangeslider_visible=False)

            # self.figure.update()
            self.figure.append_trace(rsi, row=2, col=1)
        # plot_additional_indicators()

    def update_tooltips(self):
        # Set String
        # Close
        # Percentage Increase
        # Indicator String
        #
        self.figure.add_trace(go.Scatter(name="Close",
                                 x=self.engine.orders.data.time_text_array,
                                 y=self.engine.orders.data.all_close,
                                 customdata=self.engine.orders.tooltip_info,
                                 hovertemplate='%{customdata}',
                                 line=dict(color="#919191")))
