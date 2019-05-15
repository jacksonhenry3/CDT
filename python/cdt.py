from initialization import make_flat_spacetime
from vizualization import vizualize_space_time, vizualize_space_time_flattened
import numpy as np
import matplotlib.pyplot as plt


def p_of_move_imove(st, n, gamma_prime):
    n_v = len(st.nodes)
    n_p = len(n.past)
    n_f = len(n.future)

    # l = 1
    # am = l ** 2 * np.sqrt(5) / 4
    # this is not the real value of gamma. I should probs get it in natural untis
    # gamma = 10 ** (-52)
    # gamma_prime = gamma * am / (8 * np.pi) * np.sqrt(3 / 5)
    # gamma_prime = 0.6
    non_normd_prob_move = n_v / (n_v + 1) * (n_p * n_f) * np.e ** (-1 * gamma_prime)
    non_normd_prob_imove = np.e ** gamma_prime
    normd_prob_move = non_normd_prob_move / (non_normd_prob_move + non_normd_prob_imove)
    normd_prob_imove = non_normd_prob_imove / (
        non_normd_prob_move + non_normd_prob_imove
    )
    return [normd_prob_move, normd_prob_imove]


def chose_random_vertex(space_time):
    num_nodes = np.sum(space_time.space_slice_sizes)
    random_node_list_index = np.random.randint(num_nodes)
    random_index = list(space_time.nodes.keys())[random_node_list_index]
    return space_time.nodes[random_index]


def run(initial_universe, total_num_moves):

    initial_universe_size = np.sum(initial_universe.space_slice_sizes)
    number_moves = 0
    number_imoves = 0

    p_move_history = []
    p_imove_history = []

    try:
        for i in range(total_num_moves):

            random_vertex = chose_random_vertex(initial_universe)
            p_move, p_imove = p_of_move_imove(
                initial_universe, random_vertex, gamma_prime
            )

            r1 = np.random.random()
            r2 = np.random.random()

            if p_move > r1:
                number_moves += 1
                initial_universe.move(random_vertex)

            if p_imove > r2:
                number_imoves += 1
                initial_universe.inverse_move(random_vertex)

            p_move_history.append(p_move)
            p_imove_history.append(p_imove)

            if i % 100 == 0:
                universe_size = np.sum(initial_universe.space_slice_sizes)

                if universe_size > 10000:
                    print("universe exploded")
                    raise Exception(
                        "Universe size exceeded reasonable simulation parameter of 10000"
                    )
                gamma_history.append(gamma_prime)
                universe_size_history.append(universe_size)

                """
                gamma_prime = modify_gamma_prime_based_on_move_probability(
                    gamma_prime, p_move_history, p_imove_history
                )
                """

                """
                gamma_prime = modify_gamma_prime_based_on_universe_Size(
                    gamma_prime, universe_size, initial_universe_size
                )
                """

                if i % 10000 == 0:
                    print("gamma prime is " + str(gamma_prime))
                    print(
                        str(100 * i / total_num_moves)
                        + ", spacetime size is : "
                        + str(universe_size)
                    )
                    print()
    except:
        print("universe imploded (or other)")
        pass


def modify_gamma_prime_based_on_move_probability(
    gamma_prime, p_move_history, p_imove_history
):
    if np.mean(p_move_history) > 0.5:
        print(np.mean(p_move_history))
        gamma_prime += 0.05 * (np.mean(p_move_history) - 0.5)
    p_move_history = []
    if np.mean(p_imove_history) > 0.5:
        print(np.mean(p_imove_history))
        gamma_prime -= 0.05 * (np.mean(p_imove_history) - 0.5)
    p_imove_history = []
    return gamma_prime


def modify_gamma_prime_based_on_universe_Size(
    gamma_prime, universe_size, initial_universe_size
):
    sep = universe_size - initial_universe_size
    gamma_prime += 0.05 * sep / 10000
    return gamma_prime


print("start")
print()
# for gamma_prime in np.linspace(0.52, 0.53, 4):
for j in range(1):
    gamma_prime = 0.5233333
    fig, ax1 = plt.subplots()
    # ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    for i in range(1):
        simple_st = make_flat_spacetime(16, 8)
        initial_size = np.sum(simple_st.space_slice_sizes)

        gamma_history = []
        universe_size_history = []

        run(simple_st, 10 ** 6)

        """
        color = "tab:red"
        ax1.set_xlabel("time (s)")
        ax1.set_ylabel("gamma", color=color)
        ax1.plot(gamma_history, color=color)
        ax1.tick_params(axis="y", labelcolor=color)
        """

        # color = "tab:blue"
        ax1.set_ylabel(
            "size"
        )  # , color=color)  # we already handled the x-label with ax1
        ax1.plot(np.array(universe_size_history) / initial_size)  # , color=color)
        ax1.tick_params(axis="y")  # , labelcolor=color)

        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        print("completed iteration " + str(i))

    plt.title(
        "Size history of the universe for effective cosmological constant "
        + str(np.round(gamma_prime, 2))
    )
    ax1.set_xlim(0, 10 ** 4)
    ax1.set_ylim(0, 10000.0 / initial_size)
    plt.savefig("5_universe_histories_with_gamma_prime_" + str(gamma_prime) + ".svg")
    print()

vizualize_space_time_flattened(simple_st)
# vizualize_space_time(simple_st)
print()
print("end")
