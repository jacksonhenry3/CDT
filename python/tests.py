from cdt import *
from initialization import make_flat_spacetime
from vizualization import vizualize_space_time_2d
import matplotlib.pyplot as plt
import numpy as np


# Test 1, visualize a small space-time after one move
# st = make_flat_spacetime(8, 8)
# st.move(st.get_random_node())
# vizualize_space_time_2d(st)

# =======================================================

# Test 2, visualize a small space-time after one inverse move
# st = make_flat_spacetime(8, 8)
# st.inverse_move(st.get_random_node())
# vizualize_space_time_2d(st)

# =======================================================

# Test 3, visualize a large space-time after many moves and inverse moves
# st = make_flat_spacetime(64, 32)
# run(st, 10 ** 5, 0.6, debug=False, debug_interval=1000)
# vizualize_space_time_2d(st)

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

# # Test 8, correlator for universes of different size
def get_corelator(ensemble_of_SSSizes, t):
    # argument should be a list of spatial slice sizes for universes with the same 4 volume
    # add a check that the all of the same time length
    # add a check to make sure they are all the same 4 vol
    T = len(ensemble_of_SSSizes[0])
    corelator = 0
    for s in np.arange(1, T):
        corelator += np.sum([v[s] * v[(s + t) % T]/(max(v[s],v[(s + t) % T])**2) for v in ensemble_of_SSSizes])
    corelator = corelator / float(T - 1)
    return corelator/len(ensemble_of_SSSizes)


def get_corelator(ensemble_of_SSSizes, t):
    # argument should be a list of spatial slice sizes for universes with the same 4 volume
    # add a check that the all of the same time length
    # add a check to make sure they are all the same 4 vol
    T = len(ensemble_of_SSSizes[0])
    corelator = 0
    for s in np.arange(1, T):
        corelator += np.sum([v[s] * v[(s + t) % T] for v in ensemble_of_SSSizes])
    divisor = 0
    for s in np.arange(1, T):
        divisor += np.sum([v[s]**2 for v in ensemble_of_SSSizes])
    corelator = corelator / divisor
    return corelator


ensemble_of_SSSizes = []
for i in range(50):
    print(i)
    st = make_flat_spacetime(64, 128)
    run(st, 100000, 0.65, size_cutoff=int(64 * 128 * 0.5),max_size = int(64 * 128 * 2))
    ensemble_of_SSSizes.append(st.space_slice_sizes)


for s in ensemble_of_SSSizes:
    print(np.sum(s))
T = len(ensemble_of_SSSizes[0])
y = [get_corelator(ensemble_of_SSSizes, t) for t in range(T)]
np.savetxt("VolumeCorrelation1.csv",y)
y = np.roll(y,int(len(y)/2))



plt.plot(range(T), y, ".")
plt.show()

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