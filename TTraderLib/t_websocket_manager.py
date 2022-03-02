import websocket
import threading
import time
import sys


class WebsocketManager:

    symbol_name = ""
    callback_function = ()

    connection_active = False

    def on_open(self, ws):
        log("Opened connection, receiving " + self.symbol_name + " candlestick data")
        self.connection_active = True

    def on_close(self, ws):
        log('Closed Connection')
        self.connection_active = False

        log('Websocket closed, restarting connection... ')
        self.restart_websocket()

    def on_error(self, ws):
        log('Error Connection')
        self.connection_active = False

        log('Websocket error, restarting connection...')
        self.restart_websocket()

    def on_message(self, ws, message):
        self.callback_function(message)
        # log(message)

    def restart_websocket(self):
        time.sleep(30)
        self.run_websocket()

    def run_websocket(self):
        try:
            socket = "wss://stream.binance.com:9443/ws/" + self.symbol_name.lower() + "@kline_1m"

            log("Connecting on socket: " + socket)

            ws = websocket.WebSocketApp(socket,
                                        on_open=self.on_open,
                                        on_close=self.on_close,
                                        on_message=self.on_message,
                                        on_error=self.on_error)

            ws.run_forever()
        except Exception as e:
            # reconnect
            log("Cannot establish websocket connection, restarting websocket...")
            log(e)
            self.restart_websocket()

    def start_websocket_manager(self, _symbol_name, callback):

        self.symbol_name = _symbol_name

        self.callback_function = callback

        websocket_thread = threading.Thread(target=self.run_websocket, args=())
        websocket_thread.start()


def log(log):
    try:
        file_object = open(sys.path[1] + "/TTraderLib/t_websocket_manager_log.txt", "a+")
        log = str(log) + "\n"
        file_object.write(log)
        file_object.close()
    except:
        pass