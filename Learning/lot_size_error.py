import time
import TTraderLib.t_client_manager as client

cm = client.ClientManager()

time.sleep(1)

symbol = "Doge"
symbol = symbol.upper()
symbol += "USDT"
info = cm.client.get_symbol_info(symbol)

# print(info)
# print(info['filters'][2]['minQty'])

def check_decimals(symbol):
    info = cm.client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 1
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal

# print(check_decimals(symbol))
# print(round(1400.00000, check_decimals(symbol)))

print(symbol)