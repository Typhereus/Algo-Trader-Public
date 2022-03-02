
cat = 0
bird = 0
birdseed = bird


def loop():
    global bird, birdseed

    while True:
        print(bird)
        print(birdseed)
        birdseed = birdseed
        user_input = input()
        bird += 1

loop()
