def compute_range(i, nbj):
    # miny = (20 / nbj) * i
    # maxy = miny + 20/nbj
    miny = 21/nbj * i
    maxy = 21/nbj * (i+1) - 1
    return int(miny), int(maxy)


for nbj in range(3):
    nbj+=1
    print("-- {} --".format(nbj))
    for i in range(nbj):
        print(compute_range(i, nbj))