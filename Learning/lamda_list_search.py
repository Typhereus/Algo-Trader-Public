class Stuff:
    a = 1
    b = "B"


stuff1 = Stuff()

stuff1.b = "C"

stuff2 = Stuff()

stuff_list = []

stuff_list.append(stuff1)
stuff_list.append(stuff2)

#info = filter(lambda x: x., stuff_list)

#print(info)