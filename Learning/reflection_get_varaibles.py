class Stuff:
    bird = "big bird"
    dog = "lassie"
    clown = "smokey"
    ants = 300

s = Stuff()

s.bird = "burd"
s.ants = 250

print(dir(s))
print(vars(s))
