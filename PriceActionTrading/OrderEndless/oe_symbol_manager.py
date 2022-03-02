import PriceActionTrading.OrderEndless.oe_symbol as symbol_class
import time
from typing import List
import sys


class SymbolManager:

    all_symbols: List[symbol_class.Symbol] = []

    def __init__(self):
        self.start_all_symbols()

    def get_symbol_price_with_name(self, symbol_name):
        if not any(x.symbol_name == symbol_name for x in self.all_symbols):
            print(symbol_name + " not found.")
            return

        for s in self.all_symbols:
            if s.symbol_name == symbol_name:
                return s.close_price

    def start_all_symbols(self):

        text_file = open(sys.path[1] + "/PriceActionTrading/OrderEndless/all_symbols.txt", "r")
        text_file_lines_array = text_file.read().split("\n")
        text_file.close()

        for symbol_name_text in text_file_lines_array:
            #
            symbol = symbol_class.Symbol(symbol_name_text)
            symbol.symbol_name = symbol_name_text

            self.all_symbols.append(symbol)

            print("Starting " + symbol_name_text)

            time.sleep(1)
