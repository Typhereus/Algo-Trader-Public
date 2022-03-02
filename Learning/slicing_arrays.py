data = [5, 6, 7, 8, 9, 10]

suall = []


amount = 3

for i in range(len(data) + 1):
    if i >= amount:
        # print(i)
        starting_index = i - amount
        ending_index = i

        sumumumbabitch = sum(data[starting_index:ending_index])

        print("INDEX: " + str(i)
              + "  Starting at: "
              + str(starting_index)
              + " Ending at: "
              + str(ending_index)
              + "  SUM: " + str(sumumumbabitch))

        suall.append(sumumumbabitch)

print(suall)
