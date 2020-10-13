from core import cdt, space_time
import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt


lambdas = np.linspace(0.5, 0.54, 10)
# for i in range(2, 5):
#     with open("./spacetimes/small_square/small_square.st", "rb") as file:
#         st = pkl.load(file)
#     initial_size = len(st.nodes)
#     growth = []
#     for l in lambdas:
#         print(l)
#         ensemble = cdt.do_sensemble(12, 10 ** i, l, initial_space_time=st)
#         ensemble_of_SSSizes = [len(st.nodes) / initial_size for st in ensemble]
#         growth.append(np.mean(ensemble_of_SSSizes))
#     plt.plot(lambdas, growth, ".")
#
#     with open("./spacetimes/medium_square/medium_square.st", "rb") as file:
#         st = pkl.load(file)
#     initial_size = len(st.nodes)
#     growth = []
#     for l in lambdas:
#         print(l)
#         ensemble = cdt.do_sensemble(12, 10 ** i, l, initial_space_time=st)
#         ensemble_of_SSSizes = [len(st.nodes) / initial_size for st in ensemble]
#         growth.append(np.mean(ensemble_of_SSSizes))
#     plt.plot(lambdas, growth, ".")
#
#     with open("./spacetimes/Large_square/Large_square.st", "rb") as file:
#         st = pkl.load(file)


# st = space_time.space_time()
# st.generate_flat(32, 32)
st = space_time.space_time()
st.generate_flat(32, 32)
initial_size = len(st.nodes)
growth = []
for l in lambdas:
    print(l)
    st = space_time.space_time()
    st.generate_flat(32, 32)
    ensemble = [cdt.run(st, 10 ** 6, l, debug=True)]
    ensemble_of_SSSizes = [len(st.nodes) / initial_size for st in ensemble]
    growth.append(np.mean(ensemble_of_SSSizes))
plt.plot(lambdas, growth, ".")


plt.plot(lambdas, np.ones(len(lambdas)))
plt.show()
