import backtrader as bt


class CrossOverStrategy(bt.Strategy):
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.period = 0
        #self.time = self.datas[0].Data

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        #self.log(self.period)
        self.period += 1

        if self.period == 2:
            #self.log("Buy~")
            self.buy()

        if self.period == 4:
            #self.log("Close~")
            self.close()
