
class SimpleEventSystem:

    list_of_functions = []

    def call(self):
        for f in self.list_of_functions:
            f()

    def add_subscriber(self, function):
        self.list_of_functions.append(function)

    def remove_subscriber(self, function):
        self.list_of_functions.remove(function)

    def __init__(self):
        self.list_of_functions = []