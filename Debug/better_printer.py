
def bprint(*args):
    all = ""

    for i in range(len(args)):

        if not i == len(args) - 1:
            all += (str(args[i]) + " ")
        else:
            all += (str(args[i]) + " ")
    print(all)
