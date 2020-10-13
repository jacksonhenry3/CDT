# from space_time import space_time
import simulation
from display import disp_2d2
from space_time import space_time

# sz = simulation.multi_run([0.525 for i in range(10)], num_samples=10, num_iter=10 ** 6)

# for s in sz:
#     plt.plot(s)
# plt.show()
#
# #
st = space_time(64, 64)
simulation.run(st, 10 ** 6, 0.525, display=True)
st.save("Success")
disp_2d2(st)
