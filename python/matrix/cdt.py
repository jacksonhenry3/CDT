# pretty sure all of this importing  is unnsescsary
import numpy as np
from space_time import space_time
import matplotlib.pyplot as plt

global cumulative_move_prob


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
    n_n = st.num_nodes

    # number of past edges of the specified node
    n_p = len(st.get_past(n))

    # number of future edges of the specified node
    n_f = len(st.get_future(n))

    # these proabbilities are given by equation israel et al 37 and 38
    prob_move = (
        n_n / (n_n + 1) * (n_p * n_f) * np.e ** (-1 * lambda_prime) / prob_divisor
    )
    prob_move = 4 * np.e ** (-1 * lambda_prime) / prob_divisor
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
    if moveq and imoveq > r2:
        return p_move

    if moveq:
        st.move(random_vertex)

    if imoveq:
        st.inverse_move(random_vertex)
    return p_move


def run(
    st,
    num_moves,
    lambda_prime,
    debug=False,
    debug_interval=1000,
    max_size=3 * 32 * 64,
    size_cutoff=0,
    prob_divisor=4,
):
    """
        Does num_moves iterations modifying st. If debug is True then progress
        is printed and the state of the universe is recorderd every
        debug_interval iterations.
    """

    """
    I would like to be able to record the full state of the unviverse each debug
    interval but i am having problems copying the state properly.
    """
    st_history = [0]

    # i was told there is something better than a try except here but i dont
    # remember what it was
    try:
        # do num_moves iterations on st.
        for i in range(num_moves):

            if len(st.data) == size_cutoff:
                print(len(st.data))
                raise ValueError("hit size cutoff")
            p_move = one_iteration(st, lambda_prime, prob_divisor=prob_divisor)
            # print(st_history)
            st_history.append(st_history[-1] + p_move)
            # if debugging is turned on and we have reached the debug interval
            if debug and i % debug_interval == 0:
                # print the percent complete.abs(x)
                print(np.round(float(i) / num_moves * 100.0, decimals=2))
                print(i)
                print("there are " + str(st.num_nodes) + " nodes")

                # plt.imshow(st.show())
                # plt.show()
                # print(str(i) + "-----" + str(st.spatial_slice_sizes))

            # if the unviverse gets to small throw an error
            # add checks for to large aswell.
            # are there any other checks you can do?
            if np.min(st.spatial_slice_sizes) == 1:
                raise ValueError(
                    "The universe shrunk to a point at some particular time! "
                )
            if st.num_nodes >= max_size:
                print(len(st.data))
                raise ValueError(
                    "The universe is to big and its slowing down the simulation "
                )
    except Exception as e:
        print(st_history)
        return st_history
        import traceback

        # pass
        # error return off
        print("universe failed, " + str(e))
        traceback.print_exc()
        # print(st.spatial_slice_sizes)
    return st_history


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
    ensemble = []
    for i in range(num_samples):
        st = space_time(slice_size=i_space_size, num_slices=i_time_size)
        run(
            st,
            num_iter,
            lambda_prime,
            debug=False,
            debug_interval=10 ** 3,
            prob_divisor=prob_divisor,
            max_size=max_size,
        )
        ensemble.append(st)
    return ensemble
