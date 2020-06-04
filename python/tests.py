# tests

"""
1. make sure all nodes have a left and right
2. make sure all nodes have a future and past
3. make sure all futures and pasts have only one of each value
4. make sure all future and pasts do not contain an entire spatial slcie
5. make sure all spatial slices are suffeciently large
6. validate that no edges cross
7.
"""

from cdt import *
from initialization import make_flat_spacetime
from vizualization import vizualize_space_time_2d
import matplotlib.pyplot as plt
import numpy as np
import space_time


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1 :] / n


# Test 1, visualize a small space-time after one move
# st = space_time.space_time()
#
# st.generate_flat(16, 32)
# st.move(st.nodes[15])
# plt.imshow(st.adjacency())
# plt.show()


# check_adjacent(st)
# vizualize_space_time_2d(st)

# =======================================================

# Test 2, visualize a small space-time after one inverse move
# st = space_time.space_time()
# st.generate_flat(16, 32)
# st.inverse_move(st.nodes[100])
# # vizualize_space_time_2d(st)
# plt.imshow(st.adjacency())
# plt.show()

# =======================================================

# Test 3, visualize a large space-time after many moves and inverse moves
st = space_time.space_time()
st.generate_flat(32, 32)
# for i in range(10):
#     st.inverse_move(st.get_random_node())
size = run(st, 10 ** 5, 0.6, debug=True, debug_interval=10000)
# size = moving_average(size, n=20000)
# size = [s / (i + 1) for i, s in enumerate(size)]
# plt.plot(size, ".")
# plt.show()
# print("getting mat")
# plt.imshow(st.adjacency())
# plt.axis("off")
# print("disping mat")
# put a red dot, size 40, at 2 locations:
# plt.scatter(x=[30, 40], y=[50, 60], c="r", s=40)
# plt.show()
# vizualize_space_time_2d(st)
# Graph = networkx.from_numpy_matrix(st.adjacency())
# =======================================================

# Test 4, test dependance on cosmological constant (long)
# lambdas = np.linspace(0.6, 0.7, 10)
# sizes = []
# for Lambda in lambdas:
#     print((Lambda - 0.6) / 0.1)
#     ensemble = do_sensemble(10, 10 ** 2, 64, 32, Lambda)
#     ensemble_avg_size = np.mean([len(st.nodes) / (32.0 * 64.0) for st in ensemble])
#     sizes.append(ensemble_avg_size)
# plt.plot(lambdas, sizes, ".")
# plt.xlabel("Lambda prime")
# plt.ylabel("Size of universe")
# plt.title("average size of 10 universes")
# plt.show()

# =======================================================

# Test 5, test how cosmological constant dependance depends on number of iterations (LONG)
# dbg_interval = 1
# lambdas = np.linspace(0.6, 0.7, 10)
# for num_moves_power in [2, 3]:
#     sizes = []
#     for Lambda in lambdas:
#         print((Lambda - 0.6) / 0.1)
#         numIter = 10 ** num_moves_power
#         ensemble = do_sensemble(10, numIter, 64, 32, Lambda)
#         ensemble_avg_size = np.mean([len(st.nodes) / (32.0 * 64.0) for st in ensemble])
#         sizes.append(ensemble_avg_size)
#     plt.plot(lambdas, sizes, ".", label=str(numIter) + " iterations")
#     plt.legend()
# plt.xlabel("Lambda prime")
# plt.ylabel("Size of universe")
# plt.title("average size of 10 universes")
# plt.legend()
# plt.show()

# =======================================================

# Test 6, verify random selection (NOT WORKING)

# st = make_flat_spacetime(8, 8)
# vizualize_space_time_2d(st)
# st.move(st.get_random_node())
# vizualize_space_time_2d(st)

# st = make_flat_spacetime(8, 8)
# st.move(st.get_random_node())
# nodeList = list(st.nodes.values())
# nodeNumMap = {nodeList[i].global_index(): i for i in range(len(nodeList))}
# print(nodeNumMap)

# indices = np.zeros(100000)
#
# for i in range(len(indices)):
#     indices[i] = nodeNumMap[]
#
# plt.hist()

# =======================================================

# Test 4, test dependance on cosmological constant (long)
# lambdas = np.linspace(0.69, 0.695, 10)
# sizes = []
# for Lambda in lambdas:
#     print((Lambda - 0.69) / 0.005)
#     ensemble = do_sensemble(
#         10 ** 2, 10 ** 6, 32, 16, Lambda, max_size=32 * 16 * 2, prob_divisor=3.5
#     )
#     ensemble_avg_size = np.mean([len(st.nodes) / (32.0 * 16.0) for st in ensemble])
#     sizes.append(ensemble_avg_size)
# plt.plot(lambdas, sizes, ".")
# plt.xlabel("Lambda prime")
# plt.ylabel("Size of universe")
# plt.ylim(0, 2)
# plt.title("average size of 10 universes")
# plt.show()

# =======================================================

# # # Test 8, correlator for universes of different size
# def get_corelator(ensemble_of_SSSizes, t):
#     # argument should be a list of spatial slice sizes for universes with the same 4 volume
#     # add a check that the all of the same time length
#     # add a check to make sure they are all the same 4 vol
#     T = len(ensemble_of_SSSizes[0])
#     corelator = 0
#     for s in np.arange(1, T):
#         corelator += np.sum(
#             [
#                 v[s] * v[(s + t) % T] / (max(v[s], v[(s + t) % T]) ** 2)
#                 for v in ensemble_of_SSSizes
#             ]
#         )
#     corelator = corelator / float(T - 1)
#     return corelator / len(ensemble_of_SSSizes)
#
#
# def get_corelator(ensemble_of_SSSizes, t):
#     # argument should be a list of spatial slice sizes for universes with the same 4 volume
#     # add a check that the all of the same time length
#     # add a check to make sure they are all the same 4 vol
#     T = len(ensemble_of_SSSizes[0])
#     corelator = 0
#     for s in np.arange(1, T):
#         corelator += np.sum([v[s] * v[(s + t) % T] for v in ensemble_of_SSSizes])
#     divisor = 0
#     for s in np.arange(1, T):
#         divisor += np.sum([v[s] ** 2 for v in ensemble_of_SSSizes])
#     corelator = corelator / divisor
#     return corelator
#
#
# def get_corelator(ensemble_of_SSSizes, t):
#     # argument should be a list of spatial slice sizes for universes with the same 4 volume
#     # add a check that the all of the same time length
#     # add a check to make sure they are all the same 4 vol
#     T = len(ensemble_of_SSSizes[0])
#     corelator = 0
#     for s in np.arange(1, T):
#         corelator += np.sum([v[s] * v[(s + t) % T] for v in ensemble_of_SSSizes])
#     divisor = 0
#     for s in np.arange(1, T):
#         divisor += np.sum([v[s] ** 2 for v in ensemble_of_SSSizes])
#     corelator = corelator / divisor
#     return corelator
#
#
# def get_corelator_not_normed(ensemble_of_SSSizes, t):
#     # argument should be a list of spatial slice sizes for universes with the same 4 volume
#     # add a check that the all of the same time length
#     # add a check to make sure they are all the same 4 vol
#     T = len(ensemble_of_SSSizes[0])
#     corelator = 0
#     for s in np.arange(1, T):
#         corelator += np.sum([v[s] * v[(s + t) % T] for v in ensemble_of_SSSizes])
#     # divisor = 0
#     # for s in np.arange(1, T):
#     #     divisor += np.sum([v[s]**2 for v in ensemble_of_SSSizes])
#     # corelator = corelator / divisor
#     return corelator
#
#
# def get_variation_corelator_not_normed(ensemble_of_SSSizes, t):
#
#     T = len(ensemble_of_SSSizes[0])
#     corelator = 0
#
#     ensemble_average_at = [
#         np.mean([v[t] for v in ensemble_of_SSSizes]) for t in np.arange(0, T)
#     ]
#     for s in np.arange(1, T):
#         corelator += np.mean(
#             [
#                 (v[s] - ensemble_average_at[s])
#                 * (v[(s + t) % T] - ensemble_average_at[(s + t) % T])
#                 for v in ensemble_of_SSSizes
#             ]
#         )
#
#     return corelator / T
#
#
# # (* Note that each iterations is starting from flat, this is bad and innefecient?)
# ensemble_of_SSSizes = []
# for i in range(100):
#     print(i)
#     st = make_flat_spacetime(64, 128)
#     run(st, 100000, 0.65, size_cutoff=int(32 * 64 * 0.5), max_size=int(64 * 128 * 2))
#     ensemble_of_SSSizes.append(st.space_slice_sizes)
#
#
# for s in ensemble_of_SSSizes:
#     print(np.sum(s))
# T = len(ensemble_of_SSSizes[0])
# y = [get_variation_corelator_not_normed(ensemble_of_SSSizes, t) for t in range(T)]
# np.savetxt("VolumeCorrelation1.csv", y)
# y = np.roll(y, int(len(y) / 2))
#
#
# plt.plot(range(T), y, ".")
# plt.show()

# =======================================================

# Test 9, internal (correlator within each universe) correlator for universes of different size

# timeSize = 64
# spaceSize = 32
# numberofUniverse = 100
# ensemble_of_SSSizes = []
# for i in range(numberofUniverse):
#     print(i)
#     st = make_flat_spacetime(timeSize, spaceSize)
#     run(st, 10**6, 0.64,max_size = int(spaceSize * timeSize * 2), size_cutoff=int(spaceSize * timeSize * 2),debug = True,debug_interval = 100000)
#     ensemble_of_SSSizes.append(st.space_slice_sizes)

# def get_single_instance_correlator(sss):
# 	correlations = []
# 	N = len(sss)
# 	for t in range(N):
# 		correlation = 0
# 		for i in range(N):
# 			m = max(sss[i],sss[(i+t)%N])
# 			correlation+=sss[i]*sss[(i+t)%N]/m**2/N
# 		correlations.append(correlation)
# 	return(correlations)

# # for sss in ensemble_of_SSSizes:
# # 	plt.plot(np.roll(get_single_instance_correlator(sss),9)

# plt.plot(np.roll(np.mean([get_single_instance_correlator(sss) for sss in ensemble_of_SSSizes],axis = 0),timeSize/2),color = (0,0,0),linewidth=3.0)

# plt.tight_layout()
# plt.show()


# =======================================================

# Test 10, deficite angle as a function of space-time position
#
# st = make_flat_spacetime(64, 64)
# run(st, 3 * 10 ** 5, 0.6, debug=True, debug_interval=10000, max_size=64 * 81 * 100)
#
# initial_node = st.get_random_node()
#
#
# T = np.array([])
# X = np.array([])
# z = np.array([])
#
# x = 0
# t = 0
#
# fig = plt.figure()
# ax = fig.gca(projection="3d")
# xline = np.array([])
# tline = np.array([])
# zline = np.array([])
#
# for t in range(st.num_time_slices):
#     initial_node = list(initial_node.future.values())[0]
#     current_node = initial_node.right
#     deficite_angle = []
#     x = 0
#
#     while current_node != initial_node:
#         z = np.append(z, current_node.num_connections() - 6)
#         X = np.append(X, x)
#         T = np.append(T, t)
#         a = 1
#         n = current_node.num_connections()
#         zline = np.append(zline, ((n - 6.0) * np.pi / 3.0) / (1 / 3.0 * n * a))
#         xline = np.append(xline, x)
#         tline = np.append(tline, t)
#         x += 1
#         current_node = current_node.right
#     ax.scatter(xline / len(xline), tline, zline, "gray", alpha=0.2)
#
# # ax.plot_surface(X,T,Z)
# plt.show()

# =======================================================

# Test 11: validating constant total curavture

#
# x_size = 64
# t_size = 64
# num_iterations = 10 ** 5
#
# lamnda_prime = 0.6
#
# st = make_flat_spacetime(x_size, t_size)
#
# run(
#     st,
#     num_iterations,
#     lamnda_prime,
#     debug=True,
#     debug_interval=10000,
#     max_size=64 * 81 * 100,
# )
#
#
# total_curvature = 0
#
# deficite_count = []
# for node in st.nodes.values():
#     total_curvature += node.num_connections() - 6
#     deficite_count.append(node.num_connections() - 6)
# print("=====================")
# print(total_curvature)
#
# plt.hist(
#     deficite_count,
#     [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
#     align="mid",
#     rwidth=0.8,
# )
# plt.xlabel("Number of connections minus 6")
# plt.ylabel("count")
# plt.title(
#     "distribution of defict count for a "
#     + str(x_size)
#     + " "
#     + str(t_size)
#     + " universe \n after "
#     + str(num_iterations)
#     + " width lambda prime = "
#     + str(lamnda_prime)
#     + " iterations"
# )
# plt.show()
