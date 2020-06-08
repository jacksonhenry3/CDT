# pretty sure all of this importing  is unnsescsary
# from initialization import make_flat_spacetime
import numpy as np
from space_time import space_time


def p_of_move_imove(st, n, lambda_prime, prob_divisor=4):
    """
    This function calculates the probability of making a particular move and the
    corosponding inverse move.

    it takes as argument a space time, a node within that space time,
    and modified cosmological constant
    """

    """
    I believe there is a problem here with the probabilities.
    prob divisor shouldn't effect the location of stability?
    """

    # number of nodes in the space time
    n_n = len(st.nodes)

    # number of past edges of the specified node
    n_p = len(n.past)

    # number of future edges of the specified node
    n_f = len(n.future)

    # these proabbilities are given by equation israel et al 37 and 38
    prob_move = (
        n_n / (n_n + 1) * (n_p * n_f) * np.e ** (-1 * lambda_prime) / prob_divisor
    )
    # prob_move = 4 * np.e ** (-1 * lambda_prime) / prob_divisor
    prob_imove = np.e ** lambda_prime / prob_divisor
    # prob_move = 4 * np.e ** (-1 * lambda_prime) / prob_divisor
    # prob_imove = np.e ** lambda_prime / prob_divisor
    return [prob_move, prob_imove]


def one_iteration(st, lambda_prime, prob_divisor=4):
    """
    This function does one iteration of the monte carlo simulation
    it takes as argument a space time and a cosmological constant
    """

    # select a random vertex and figure out how likely a move or inverse move on
    # the given vertex is
    random_vertex = st.get_random_node()
    p_move, p_imove = p_of_move_imove(
        st, random_vertex, lambda_prime, prob_divisor=prob_divisor
    )

    r1 = np.random.random()
    r2 = np.random.random()

    moveq, imoveq = p_move > r1, p_imove > r2

    # if both a move and inverse move would be accepted instead do nothing.
    if moveq and imoveq:
        return st

    if moveq:
        st.move(random_vertex)

    if imoveq:

        st.inverse_move(random_vertex)
    return st


def run(
    st,
    num_moves,
    lambda_prime,
    debug=False,
    debug_interval=1000,
    max_size=100 * 100 * 10,
    size_cutoff=0,
    prob_divisor=4,
):
    """
        Does num_moves iterations modifying st. If debug is True then progress
        is printed and the state of the universe is recorderd every
        debug_interval iterations.
    """
    st_history = [0]

    # i was told there is something better than a try except here but i dont
    # remember what it was
    try:
        # do num_moves iterations on st.
        for i in range(num_moves):

            if len(st.nodes) == size_cutoff:
                print(len(st.nodes))
                raise ValueError("hit size cutoff")
            st = one_iteration(st, lambda_prime, prob_divisor=prob_divisor)
            # if debugging is turned on and we have reached the debug interval
            if debug and i % debug_interval == 0:
                # print the percent complete.abs(x)
                print(np.round(float(i) / num_moves * 100.0, decimals=2))
                print("there are " + str(len(st.nodes)) + " nodes")

            if np.min(st.space_slice_sizes) == 1:
                raise ValueError(
                    "The universe shrunk to a point at some particular time! "
                )
            if len(st.nodes) >= max_size:
                print(len(st.nodes))
                raise ValueError(
                    "The universe is to big and its slowing down the simulation "
                )
    except Exception as e:
        # pass
        # error return off
        print("universe failed, " + str(e))
        # print(st.space_slice_sizes)
        # print(st_history)
        # import traceback
        #
        # traceback.print_exc()
    return st


def do_sensemble(
    num_samples,
    num_iter,
    i_space_size,
    i_time_size,
    lambda_prime,
    prob_divisor=4,
    max_size=32 * 64 * 3,
):
    """
        this runs num_samples universe each for num_iter iterations.
        It takes as argument
        the number of samples (int)
        the number of iterations (int)
        the spatial and time size of the unvierse (int)
        a modified cosmological constant (float)
        It returns a list of all the simulated unvierses.
    """
    import multiprocessing

    pool = multiprocessing.Pool(multiprocessing.cpu_count())

    promise_ensemble = []
    space_times = []
    for i in range(num_samples):
        st = space_time()
        st.generate_flat(32, 32)
        res = pool.apply_async(run, (st, num_iter, lambda_prime))
        promise_ensemble.append(res)
    i = 0
    for prommise in promise_ensemble:
        space_times.append(prommise.get())
        i += 1
        print(i)
    return space_times
