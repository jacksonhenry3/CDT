import random

from cdtea.visualization import plot_st
from cdtea.space_time import SpaceTime
from cdtea.space_time import generate_flat_spacetime
from cdtea.moves import increase,decrease
from cdtea.event import Event
def main():

    size = 40
    FST = generate_flat_spacetime(size, size)
    random.seed(9230)
    #
    for i in range(50):
        if i % 100:
            print(i)
        n = FST.get_random_node()
        f = random.choice(list(n.future))
        p = random.choice(list(n.past))
        increase(FST, n, f, p)
    # n = FST.get_random_node()
    # print(n)
    # imove(FST,n)

    # FST.imove(n)
    print("plottin")
    # display.get_naive_coords(FST)
    plot_st.plot_2d(FST)
    # plot_st.plot_3d(FST,type = "cylinder")


if __name__ == '__main__':  # import shielding
    main()
