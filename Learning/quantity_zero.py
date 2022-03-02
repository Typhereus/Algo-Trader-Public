class Broker:

    class SymbolDecimals:
        AAVE = "0.00010000"
        ADA = "0.10000000"
        ATOM = "0.00100000"
        AVAX = "0.01000000"
        AXS = "0.01000000"
        BAND = "0.01000000"
        BAT = "0.01000000"
        BCH = "0.00001000"
        BNB = "0.01000000"
        BTC = "0.00000100"
        COMP = "0.00001000"
        CRV = "0.10000000"
        CTSI = "1.00000000"
        DOGE = "1.00000000"
        DOT = "0.01000000"
        EGLD = "0.00100000"
        ETC = "0.01000000"
        ETH = "0.00001000"
        FIL = "0.00010000"
        HNT = "0.10000000"
        KNC = "0.00100000"
        LTC = "0.00001000"
        MKR = "0.00001000"
        NEO = "0.00100000"
        ONE = "0.10000000"
        ONT = "0.01000000"
        OXT = "0.01000000"
        QTUM = "0.00100000"
        SOL = "0.01000000"
        STORJ = "0.01000000"
        UNI = "0.01000000"
        VET = "1.00000000"
        VTHO = "1.00000000"
        XLM = "0.10000000"
        ZEN = "0.00100000"
        ZRX = "0.01000000"

        @staticmethod
        def get_decimal_with_symbol_name(symbol_name):

            symbol_name = symbol_name  # type: str
            symbol_name = symbol_name.upper()

            if symbol_name == "AAVE":
                return Broker.SymbolDecimals.AAVE

            if symbol_name == "ADA":
                return Broker.SymbolDecimals.ADA

            if symbol_name == "ATOM":
                return Broker.SymbolDecimals.ATOM

            if symbol_name == "AVAX":
                return Broker.SymbolDecimals.AVAX

            if symbol_name == "AXS":
                return Broker.SymbolDecimals.AXS

            if symbol_name == "BAND":
                return Broker.SymbolDecimals.BAND

            if symbol_name == "BAT":
                return Broker.SymbolDecimals.BAT

            if symbol_name == "BCH":
                return Broker.SymbolDecimals.BCH

            if symbol_name == "BNB":
                return Broker.SymbolDecimals.BNB

            if symbol_name == "BTC":
                return Broker.SymbolDecimals.BTC

            if symbol_name == "COMP":
                return Broker.SymbolDecimals.COMP

            if symbol_name == "CRV":
                return Broker.SymbolDecimals.CRV

            if symbol_name == "CTSI":
                return Broker.SymbolDecimals.CTSI

            if symbol_name == "DOGE":
                return Broker.SymbolDecimals.DOGE

            if symbol_name == "DOT":
                return Broker.SymbolDecimals.DOT

            if symbol_name == "EGLD":
                return Broker.SymbolDecimals.EGLD

            if symbol_name == "ETC":
                return Broker.SymbolDecimals.ETC

            if symbol_name == "ETH":
                return Broker.SymbolDecimals.ETH

            if symbol_name == "FIL":
                return Broker.SymbolDecimals.FIL

            if symbol_name == "HNT":
                return Broker.SymbolDecimals.HNT

            if symbol_name == "KNC":
                return Broker.SymbolDecimals.KNC

            if symbol_name == "LTC":
                return Broker.SymbolDecimals.LTC

            if symbol_name == "MKR":
                return Broker.SymbolDecimals.MKR

            if symbol_name == "NEO":
                return Broker.SymbolDecimals.NEO

            if symbol_name == "ONE":
                return Broker.SymbolDecimals.ONE

            if symbol_name == "ONT":
                return Broker.SymbolDecimals.ONT

            if symbol_name == "OXT":
                return Broker.SymbolDecimals.ONT

            if symbol_name == "QTUM":
                return Broker.SymbolDecimals.QTUM

            if symbol_name == "SOL":
                return Broker.SymbolDecimals.SOL

            if symbol_name == "STORJ":
                return Broker.SymbolDecimals.STORJ

            if symbol_name == "UNI":
                return Broker.SymbolDecimals.UNI

            if symbol_name == "VET":
                return Broker.SymbolDecimals.VET

            if symbol_name == "VTHO":
                return Broker.SymbolDecimals.VTHO

            if symbol_name == "XLM":
                return Broker.SymbolDecimals.XLM

            if symbol_name == "ZEN":
                return Broker.SymbolDecimals.ZEN

            if symbol_name == "ZRX":
                return Broker.SymbolDecimals.ZRX

    @staticmethod
    def get_symbol_decimals(symbol):
        string = Broker.SymbolDecimals.get_decimal_with_symbol_name(symbol)
        decimal = 0
        is_the_decimal = False

        for char in string:
            if is_the_decimal:
                decimal += 1

            if char == '1':
                break

            if char == '.':
                is_the_decimal = True

        return decimal

usd = 250
price = 0.006821

quantity = usd / price

print(quantity)

quantity = round(quantity, Broker.get_symbol_decimals("VTHO"))

print(quantity)

