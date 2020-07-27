from collections import Counter
import pickle as pkl
import numpy as np

# test if all items in a list are unique
def all_unique(test_list):
    flag = True
    counter = Counter(test_list)
    for i, values in counter.items():
        if values > 1:
            flag = False
    return flag


def all_unique2(test_list):
    return len(np.unique(test_list)) == len(test_list)


# loads a space_time from a pickled space_time
def load_st(path):
    with open(path, "rb") as file:
        st = pkl.load(file)
    return st


# import timeit
#
# my_list = np.linspace(0, 1, 10 ** 1)
# print(all_unique(my_list))
# print(all_unique2(my_list))
# print(
#     timeit.timeit(
#         "all_unique(my_list)",
#         number=10000,
#         setup="from __main__ import all_unique,all_unique2,my_list",
#     )
# )
#
# print(
#     timeit.timeit(
#         "all_unique2(my_list)",
#         number=10000,
#         setup="from __main__ import all_unique,all_unique2,my_list",
#     )
# )
