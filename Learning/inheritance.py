import Debug.better_printer as bp

class Animal:

    entity = ""
    name = ""
    id = 0
    age = 0

    last_meal = "Nothing"

    def eat(self, food):
        self.last_meal = food

    def __init__(self, _name, _age, _id):
        self.entity = "Animal"
        self.name = _name
        self.age = _age
        self.id = _id


class Dog(Animal):

    def __init__(self, _name, _age, _id, barking):
        Animal.__init__(self, _name, _age, _id)
        #super().__init__(_name, _age, _id)
        self.barking = barking

    def stop_barking(self):
        self.barking = False
        print(self.name + " stopped barking")


fido = Dog("Fido", 6, 1, True)

bp.bprint(fido.entity, fido.name, str("Age: " + str(fido.age)), fido.id, fido.barking)

fido.stop_barking()
