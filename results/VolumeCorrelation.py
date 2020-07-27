from core import cdt, space_time
import pickle as pkl
import numpy as np


def get_corelator_not_normed(ensemble_of_SSSizes, t):
    # argument should be a list of spatial slice sizes for universes with the same 4 volume
    # add a check that the all of the same time length
    # add a check to make sure they are all the same 4 vol
    T = len(ensemble_of_SSSizes[0])
    corelator = 0
    for s in np.arange(1, T):
        corelator += np.sum([v[s] * v[(s + t) % T] for v in ensemble_of_SSSizes])
    # divisor = 0
    # for s in np.arange(1, T):
    #     divisor += np.sum([v[s]**2 for v in ensemble_of_SSSizes])
    # corelator = corelator / divisor
    return corelator


def get_variation_corelator_not_normed(ensemble_of_SSSizes, t):

    T = len(ensemble_of_SSSizes[0])
    corelator = 0

    ensemble_average_at = [
        np.mean([v[t] for v in ensemble_of_SSSizes]) for t in np.arange(0, T)
    ]
    for s in np.arange(1, T):
        print(s)
        corelator += np.mean(
            [
                (v[s] - ensemble_average_at[s])
                * (v[(s + t) % T] - ensemble_average_at[(s + t) % T])
                for v in ensemble_of_SSSizes
            ]
        )

    return corelator / T


def stat_var(ensemble_of_SSSizes, t):
    T = len(ensemble_of_SSSizes[0])
    ensemble_average_at = [
        np.mean([v[t] for v in ensemble_of_SSSizes]) for t in np.arange(0, T)
    ]
    autocorelation_at = [
        np.mean([v[s] * v[(s + t) % T] for v in ensemble_of_SSSizes])
        for s in np.arange(0, T)
    ]
    return np.mean(
        [
            autocorelation_at[s]
            - ensemble_average_at[s] * ensemble_average_at[(s + t) % T]
            for s in np.arange(1, T)
        ]
    )


with open("./spacetimes/medium_square/medium_square.st", "rb") as file:
    st = pkl.load(file)
print("begin")
ensemble = cdt.do_sensemble(12 * 8, 10 ** 6, 0.605, initial_space_time=st)
ensemble_of_SSSizes = [st.SSS for st in ensemble]
T = len(ensemble_of_SSSizes[0])
y = [stat_var(ensemble_of_SSSizes, t) for t in range(T)]
np.savetxt("VolumeCorrelation1.csv", y)
y = np.roll(y, int(len(y) / 2))

import matplotlib.pyplot as plt

plt.plot(range(T), y, ".")

y = [get_variation_corelator_not_normed(ensemble_of_SSSizes, t) for t in range(T)]
np.savetxt("VolumeCorrelation2.csv", y)
y = np.roll(y, int(len(y) / 2))

plt.plot(range(T), y, ".")
plt.show()
