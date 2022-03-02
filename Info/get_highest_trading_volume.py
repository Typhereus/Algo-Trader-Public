import time
import TTraderLib.t_client_manager as client_script
import sys

cm = client_script.ClientManager()

time.sleep(1)
text_file = open(sys.path[1] + "/PriceActionTrading/OrderEndless/all_symbols.txt", "r")
lines = text_file.read().split("\n")
text_file.close()

symbols = []
i = 0
for l in lines:
    i += 1
    print(i)
    symbol = l
    symbol = symbol.upper()
    symbol += "USDT"
    info = cm.client.get_ticker(symbol=symbol)
    time.sleep(.25)

    price = float(info["lastPrice"])
    volume = float(info["volume"])

    price_volume = volume / price

    symbol_info = [l, price_volume]

    symbols.append(symbol_info)


# define a sort key
def sort_key(sym):
    return sym[1]

# sort the companies by revenue
symbols.sort(key=sort_key, reverse=True)

print("24 HR")
for s in symbols:
    print(s)

# TODO: get