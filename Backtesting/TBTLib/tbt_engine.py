from datetime import datetime
import Backtesting.TBTLib.tbt_plotter as tbt_plot
import Strategies.strategies as tbt_strategy
import Backtesting.TBTLib.tbt_order_manager as tbt_orders
import Backtesting.TBTLib.tbt_auditor as tbt_audit
import TAlgoLib.t_indicators as t_indicator_manager
import Backtesting.TBTLib.tbt_data_manager as tbt_data
import Backtesting.TBTLib.tbt_event_manager as all_events
import Strategies.strategies as strategies


class BacktestEngine:

    strategy = None  # type: tbt_strategy.MASpeedStrategy
    data = None  # type: tbt_data.BacktestData
    orders = None  # type: tbt_orders.BacktestOrders
    indicators = None  # type: t_indicator_manager.IndicatorManager
    plotter = None  # type: tbt_plot.BacktestPlotter
    auditor = None  # type: tbt_audit.BacktestAuditor
    events = None  # type: all_events

    enable_logging = None
    plot = True
    debugging = False

    begin_time = ""

    def __init__(self, _strategy):
        # Initialize All Modules
        self.strategy = _strategy
        self.data = tbt_data.BacktestData()
        self.indicators = t_indicator_manager.IndicatorManager(self.data)
        self.orders = tbt_orders.BacktestOrders(self.strategy, self.data, self.indicators)
        self.auditor = tbt_audit.BacktestAuditor(self)
        self.plotter = tbt_plot.BacktestPlotter(self)

    def start(self):
        self.begin_time = datetime.now()
        print("Begin at " + str(self.begin_time))

        # Debugging
        self.orders.debugging = self.debugging
        self.orders.enable_logging = self.enable_logging

        # Strategy
        self.strategy.start_strategy(strategies.Strategy.StrategyType.BACKTEST, self.data, self.indicators, self.orders)

        # Orders
        self.orders.start_orders()

        # Auditor
        self.auditor.enable_logging = self.enable_logging
        self.auditor.write_results_to_text_file()

        # Plot
        if self.plot:
            self.plotter.plot_all()

        print("Completion Time: {}".format(datetime.now() - self.begin_time))
