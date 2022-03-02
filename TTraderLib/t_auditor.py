import TTraderLib.t_trader_engine as te
import sys

# TODO: Fix One Day
class Auditor:
    trade_engine = None # type: te.TraderEngine

    def start(self, _trade_engine):
        self.trade_engine = _trade_engine
        self.trade_engine.order_manager.on_buy_end.add_subscriber(self.print_buy_order())
        self.trade_engine.order_manager.on_sell_end.add_subscriber(self.print_sell_order())

    def print_buy_order(self):
        self.log(vars(self.trade_engine.order_manager))

    def print_sell_order(self):
        self.log(vars(self.trade_engine.order_manager))

    def log(self, log):
        try:
            file_object = open(sys.path[1] + "/TTraderLib/t_order_manager_log.txt", "a+")
            log = str(log) + "\n"
            file_object.write(log)
            file_object.close()
        except:
            pass
