import simulation
import display
from SpaceTime import SpaceTime
import random


random.seed(123)
# random.seed(1)
# sz = simulation.multi_run([0.525 for i in range(10)], num_samples=10, num_iter=10 ** 6)

# for s in sz:
#     plt.plot(s)
# plt.show()
#
# #
t = 4
x = 4

st = SpaceTime(8, 8)
display.force_layout(st)
# nds = st.get_all((x, t))
# for n in nds:
#     # print(n)
#     st.data[n[1]][n[0]]["R"] = 2
# pass
# st.data[t][x]["R"] = 1

# st.move(x, t)
for i in range(18):
    vert = st.random_vertex()
    st.move(*vert)
    if i==17:
        display.force_layout(st)
    # display.force_layout(st)
vert = st.random_vertex()
pschng = st.move(*vert)
for t, slice in enumerate(st.data):
    for x, node in enumerate(slice):
        # st.data[t][x]["R"] = 0.0
        pass


# for n in pschng:
#     tp = n[1]
#     xp = n[0]
    # print(tp)
    # st.data[tp][xp]["R"]  = 5

# st.data[vert[1]][vert[0]]["R"] = 1.0
# con = st.connected_to(vert[0], vert[1])
# st.data[con[1]][con[0]]["R"] = 1.0
    # print(xp,tp)
# simulation.run(st, 2*10**2, 0.525, display=True)
# st.save("Success")
display.force_layout(st)
# 872.664
#todo could the failure be about improperly calcuationg connected simplices?
