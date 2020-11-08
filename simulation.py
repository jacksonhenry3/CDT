import sys  # required for saving state
import random
from math import e
from space_time import space_time
import copy

# def run(st, iter, lp=0.529):.525


def run(st, iter, lp, display=False):
    print(
        "Doing {:.2e} iterations on an intial space time of size {:.2e} with {} time slices".format(
            iter, st.length, st.time_size
        )
    )
    sz = []
    sz.append(st.length)
    for i in range(1, iter + 1):
        if i % 1000 == 0 and display is True:
            sz.append(st.length)

            sys.stdout.flush()
            output = """\r {:.2f} percent complete  | with  {}  nodes | having made  {}/{} changes""".format(
                i * 100.0 / iter, st.length, st.totalChanges, i
            )
            sys.stdout.write(output)

        try:
            vert = st.random_vertex()
            r1 = random.random()
            r2 = random.random()
            future = st.get_future(vert)
            past = st.get_past(vert)
            # Probability of a move with NO dilaton
            pm = (
                st.length
                / 2
                / (st.length / 2 + 1)
                * len(future)
                * len(past)
                / (len(future) + len(past))
                * e ** (-lp)
            )
            pim = 1 / (len(future) + len(past)) * e ** (lp)

            # duplicate = copy.deepcopy(st)
            # duplicate.move(*vert)
            # sp = duplicate.action()
            # if sp != st.action():
            #     print("fudge")
            move = pm > r1
            imove = pim > r2
            # print()
            if move and imove:
                pass
            elif move:
                # so = st.action()
                st.move(*vert)
                # print(st.action() - so)
            elif imove:
                # so = st.action()
                st.inverse_move(*vert)
                # print(st.action() - so)
        except:

            # print("error!")
            # print("Unexpected error:", sys.exc_info())
            st.save("errDump")
            raise
            # return sz
    sys.stdout.flush()
    if display is True:
        print()
    print(
        "Final space time has size {:.2e} after {:.2e} changes ".format(
            st.length, st.totalChanges
        )
    )
    return sz


def multi_run(lp, num_iter=10 ** 6, num_samples=10, initial_space_time=None):

    import multiprocessing

    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    promise_ensemble = []
    space_times = []
    for i in range(num_samples):
        if initial_space_time is None:
            st = space_time(32, 64)
        else:
            st = initial_space_time
        # print("begining Sample {}".format(i))
        res = pool.apply_async(run, (st, num_iter, lp[i]))
        promise_ensemble.append(res)
    i = 0
    for prommise in promise_ensemble:
        # print("sample {} generated".format(i))
        space_times.append(prommise.get())
        i += 1

    pool.terminate()
    return space_times
