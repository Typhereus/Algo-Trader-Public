my_dict = {}

# Add key with value
my_dict["Boners"] = 55
my_dict["Boobies"] = 69

# Add key without value
my_dict["Poop"] = None

for key in my_dict:
    #print(key + " " + str(my_dict[key]))
    pass

# Dict with numbers as keys
my_dict2 = {}

my_dict2[4] = [2,4,2]
my_dict2[1] = [1,5,4,3]

print(sum(my_dict2[1][-2:]))