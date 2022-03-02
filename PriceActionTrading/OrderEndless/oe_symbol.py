import TTraderLib.t_websocket_manager as websocket_manager
import json


class Symbol:

    websocket = None

    """
      "e": "kline",     // Event type
      "E": 123456789,   // Event time
      "s": "BNBBTC",    // Symbol
      "k":
            "t": 123400000, // Kline start time
            "T": 123460000, // Kline close time
            "s": "BNBBTC",  // Symbol
            "i": "1m",      // Interval
            "f": 100,       // First trade ID
            "L": 200,       // Last trade ID
            "o": "0.0010",  // Open price
            "c": "0.0020",  // Close price
            "h": "0.0025",  // High price
            "l": "0.0015",  // Low price
            "v": "1000",    // Base asset volume
            "n": 100,       // Number of trades
            "x": false,     // Is this kline closed?
            "q": "1.0000",  // Quote asset volume
            "V": "500",     // Taker buy base asset volume
            "Q": "0.500",   // Taker buy quote asset volume
            "B": "123456"   // Ignore

    """

    symbol_name = ""
    close_price = 0

    def __init__(self, symbol_name):
        symbol_name += "usdt"
        self.websocket = websocket_manager.WebsocketManager()
        self.websocket.start_websocket_manager(symbol_name, self.receive_json_message)

    def receive_json_message(self, message):
        json_message = json.loads(message)

        raw_candle_data = json_message['k']

        self.close_price = float(raw_candle_data['c'])

