import finplot as fplt
import yfinance
import pandas as pd

dataframe = pd.read_csv('../oracle.csv')

# format it in pandas
dataframe = dataframe.astype({'Date':'datetime64[ns]'})

# create two axes
#ax,ax2 = fplt.create_plot(symbol, rows=2)

# plot candle sticks
candles = dataframe[['Date','Open','Close','High','Low']]

# place some dumb markers on low wicks
wick_location = dataframe[['Open', 'Close']].T.min() - dataframe['Low']
dataframe.loc[(wick_location > wick_location.quantile(0.99)), 'marker'] = dataframe['Low']

dates2 = ["1995-01-09"]

s = pd.Series(dates2)

print(type(s))

fplt.plot(wick_location, dataframe['marker'], color='#4a5', style='^', legend='dumb mark')

fplt.candlestick_ochl(dataframe[['Date', 'Open', 'Close', 'High', 'Low']])

fplt.show()
