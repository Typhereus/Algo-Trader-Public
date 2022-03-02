import time
import TTraderLib.t_client_manager as client_script
import sys

cm = client_script.ClientManager()

time.sleep(1)
text_file = open(sys.path[1] + "/PriceActionTrading/OrderEndless/all_symbols.txt", "r")
lines = text_file.read().split("\n")
text_file.close()

for l in lines:
    symbol = l
    symbol = symbol.upper()
    symbol += "USDT"
    info = cm.client.get_symbol_info(symbol)

    print(l + info['filters'][2]['minQty'])