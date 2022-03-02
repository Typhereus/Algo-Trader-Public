a_list = ["A", "X"]
b_list = ["C", "X"]

for b in b_list:
    if a_list.__contains__(b):
        a_list.remove(b)

print(a_list)