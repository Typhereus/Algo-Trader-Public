import Strategies.strategies as strategies
import TTraderLib.t_trader_engine as trader_engine

# Interface
strategy = strategies.PNLTrail()
trader = trader_engine.TraderEngine()
trader.start(strategy)
