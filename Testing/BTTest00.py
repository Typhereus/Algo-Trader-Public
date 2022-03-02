import backtrader

class TheStrategy(backtrader.Strategy):
    def __init__(self):
        self.period = 0

    def next(self):
        self.period += 1

        if self.period == 3:
            print("buy")
            self.buy()

        if self.period == 7:
            print("close")
            self.close()

cerebro = backtrader.Cerebro()

cerebro.broker.setcash(1000)

print("Starting $ %.2f" % cerebro.broker.getvalue())

# Get Data
data = backtrader.feeds.GenericCSVData(dataname='ethusdt.csv', dtformat='%Y-%m-%d', openinterest=-1, volume=-1)
#data = backtrader.feeds.GenericCSVData(dataname='oracle.csv', dtformat='%Y-%m-%d', openinterest=-1, volume=-1)

# Add Data
cerebro.adddata(data)

# Add Strategy
cerebro.addstrategy(TheStrategy)

# Run
cerebro.run()

print("Final $ %.2f" % cerebro.broker.getvalue())

cerebro.plot(volume=False)
