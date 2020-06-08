from space_time import space_time
from matplotlib import pyplot as plt
import random as r
import cdt

test = space_time(slice_size=10, num_slices=10)
cumulative_move_prob = []
size = cdt.run(test, 10 ** 5, 0.693, debug=True, debug_interval=1000)
#
# for i in range(30):
#     if i % 1 == 0:
#         print(i)
#     n1 = r.randrange(0, test.num_nodes)
#     test.inverse_move(n1)
#     print(n1)

size = [s / (i + 1) for i, s in enumerate(size)]
plt.plot(size)
plt.show()
