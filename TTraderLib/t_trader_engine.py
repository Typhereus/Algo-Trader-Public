import time
import TTraderLib.t_client_manager as client_mgmt
import TTraderLib.t_websocket_manager as websocket_mgmt
import TTraderLib.t_data_manager as data_mgmt
# import TTraderLib.t_indicators as indicator_mgmt
import TTraderLib.t_order_manager as order_mgmt
import TTraderLib.t_auditor as auditor
import TAlgoLib.t_indicators as indicator_manager
import Strategies.strategies as strategies

import Backtesting.TBTLib.tbt_order_manager as tbt_orders


class TraderEngine:

    client_manager = None  # type: client_mgmt.ClientManager
    data_manager = None  # type: data_mgmt.DataManager
    websocket_manager = None  # type: websocket_mgmt.WebsocketManager
    indicator_manager = None  # type: indicator_manager.IndicatorManager
    order_manager = None  # type: order_mgmt.OrderManager
    auditor = None  # type: auditor.Auditor
    strategy = None  # type: strategies.Strategy

    def start(self, _strategy):

        self.strategy = _strategy

        # Client
        self.client_manager = client_mgmt.ClientManager()

        #
        time.sleep(5)

        # Data
        self.data_manager = data_mgmt.DataManager(self.client_manager.client, self.strategy.trade_symbol)

        # Indicator Manager
        self.indicator_manager = indicator_manager.IndicatorManager(self.data_manager)

        # Order Manager
        self.order_manager = order_mgmt.OrderManager()

        # Set Strategy
        self.strategy.start_strategy(self.strategy.StrategyType.TRADER,
                                     self.data_manager,
                                     self.indicator_manager,
                                     self.order_manager)

        #
        # self.auditor = auditor.Auditor()
        # self.auditor.start(self)

        # Start Order Manager
        # End Thread
        self.order_manager.start_order_manager(_strategy, self.data_manager, self.indicator_manager, self.client_manager)
