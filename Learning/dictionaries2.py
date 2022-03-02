
dic = {"Algo-Trader A:": "A", "Algo-Trader B:": "B", "Algo-Trader C:": ["C1", "C2"]}
#dic = {"Algo-Trader A:": "A", "Algo-Trader B:": "B"}

period = 0

for key in dic:
    print(period)

    if type(dic[key]) is dict or type(dic[key]) is list:
        print("")
        #for key2 in key:
            #print(key2 + " : " + str(key[key2]))
    else:
        print("Types: " + str(type(key)) + " " + str(type(dic[key])))

        print(key + " : " + str(dic[key]))

    period += 1