import Strategies.strategies as t_strategy
import Backtesting.TBTLib.tbt_engine as t_engine

# Interface

# Debugging
data = ""
enable_logging = False
plot = True
debugging = False
strategy = t_strategy.PNLTrailNew()


def start():
    strategy.enable_logging = enable_logging
    engine = t_engine.BacktestEngine(strategy)
    engine.debugging = debugging
    engine.enable_logging = enable_logging
    engine.plot = plot
    engine.start()


start()


