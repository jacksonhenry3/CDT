import random

from cdtea import Display
from cdtea.SpaceTime import SpaceTime


def main():
    # move fails when this is executed
    FST = SpaceTime()
    size = 16
    FST.generate_flat(size, size)
    random.seed(9230)
    #
    for i in range(10):
        if i % 100:
            print(i)
        n = FST.get_random_node()
        f = random.choice(n.future)
        p = random.choice(n.past)
        FST.move(n, f, p)
        _ = 1
        # n = FST.get_random_node()
        # FST.imove(n)

    # FST.imove(n)
    print("plottin")
    # Display.get_naive_coords(FST)
    Display.plot_2d(FST)


if __name__ == '__main__':  # import shielding
    main()
