from binance.client import Client
import Broker.config as config
import threading
import time
import sys


class ClientManager:
    client = None  # type: Client

    period = 0

    def set_client(self):
        self.client = Client(config.API_KEY, config.API_SECRET, tld='us')
        log("Client set: " + str(self.client))

        while True:
            try:
                if self.period > 120:
                    self.client = Client(config.API_KEY, config.API_SECRET, tld='us')
                    self.period = 0

                self.period += 1
            except Exception as e:
                log(e)

            time.sleep(1)

    def __init__(self):
        thread = threading.Thread(target=self.set_client, args=())
        thread.start()


def log(log):
    try:
        file_object = open(sys.path[1] + "/TTraderLib/t_client_manager_log.txt", "a+")
        log = str(log) + "\n"
        file_object.write(log)
        file_object.close()
    except:
        pass