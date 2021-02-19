import random

from cdtea import display
from cdtea.space_time import SpaceTime
from cdtea.space_time import generate_flat_spacetime
from cdtea.modifications import move,imove
from cdtea.event import Event
def main():

    size = 40
    FST = generate_flat_spacetime(size, size)
    random.seed(9230)
    #
    # for i in range(10):
    #     if i % 100:
    #         print(i)
    #     n = FST.get_random_node()
    #     f = random.choice(n.future)
    #     p = random.choice(n.past)
    #     move(FST,n, f, p)
    n = FST.get_random_node()
    print(n)
    imove(FST,n)

    # FST.imove(n)
    print("plottin")
    # display.get_naive_coords(FST)
    display.plot_2d(FST)


if __name__ == '__main__':  # import shielding
    main()
