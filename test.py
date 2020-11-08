# from space_time import space_time
import simulation
import display
from space_time import space_time
import random


random.seed(123)
# random.seed(1)
# sz = simulation.multi_run([0.525 for i in range(10)], num_samples=10, num_iter=10 ** 6)

# for s in sz:
#     plt.plot(s)
# plt.show()
#
# #
t = 1
x = 10
st = space_time(32, 32)
# nds = st.get_all((x, t))
# for n in nds:
#     # print(n)
#     st.data[n[1]][n[0]]["R"] = 2
# pass
# st.data[t][x]["R"] = 1

# st.inverse_move(x, t)
# st.inverse_move(10, 10)
simulation.run(st, 10 ** 6, 0.525, display=True)
# st.save("Success")
display.force_layout(st)
# 872.664
