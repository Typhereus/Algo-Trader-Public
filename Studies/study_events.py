import TTraderLib.t_event_system as events

callback_event = events.SimpleEventSystem()
callback_two = events.SimpleEventSystem()


period = 0

class FunctionVariable:

    a_list_of_functions = []

    def __init__(self):
        self.a_list_of_functions = []


def print_period():
    pass
    #print(period)


def print_two():
    f = "124124"

a_function = FunctionVariable()

a_function.a_list_of_functions.append(print_period)

b_function = FunctionVariable()

b_function.a_list_of_functions.append(print_two)

callback_event.add_subscriber(print_period)
callback_two.add_subscriber(print_two)

callback_two.a = 3

for i in range(100):

    period += 1

    callback_event.call()


for i in a_function.a_list_of_functions:
    print(i)



