import TTraderLib.t_event_system as e
import TTraderLib.t_order_manager as om
import sys

class Afg:

    alpha = 3
    gamma = "G"
    delta = "D"

    def print_to_order_log(self, *logs):
        self.alpha = 4
        self.gamma = "GG"
        self.delta = "DD"
        try:
            all_logs_string = ""

            for l in logs:
                all_logs_string += str(l) + " "

            # print(all_logs_string)

            file_object = open(sys.path[1] + "/TAlgoLib/t_order_manager_log.txt", "a+")

            all_logs_string += "\n"

            file_object.write(all_logs_string)

            file_object.close()
        except Exception as e:
            print(e)

    def a(self):
        self.print_to_order_log("SELL:", vars(self))

    def b(self):
        self.print_to_order_log("SELL:", vars(self))


afg = Afg()

es = e.SimpleEventSystem()
es.add_subscriber(afg.a)
es.add_subscriber(afg.b)
es.call()
