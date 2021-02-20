import random

from cdtea.visualization import plot_st
from cdtea.space_time import SpaceTime


def main():
    # move fails when this is executed
    FST = SpaceTime()
    size = 10
    FST.generate_flat(size, size)
    random.seed(923340)
    #
    # for i in range(10):
    #     if i % 100:
    #         print(i)
    n = FST.get_random_node()
    f = random.choice(n.future)
    p = random.choice(n.past)
    FST.move(n, f, p)
    #     _ = 1
        # n = FST.get_random_node()
        # FST.imove(n)

    # FST.imove(n)
    print("plottin")
    # display.get_naive_coords(FST)
    plot_st.plot_3d(FST,type = "cylinder")


if __name__ == '__main__':  # import shielding
    main()
