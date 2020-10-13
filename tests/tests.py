import core

print(core)
import matplotlib.pyplot as plt
from core import space_time
from core import cdt
import random
from vizualization import visualize3d

#
# random.seed(2)
#
#
st = space_time.space_time()
st.generate_flat(32, 64)
cdt.run(st, int(10 ** 5), 0.62, debug=True)
visualize3d.visualize3d(st)
# plt.imshow(st.adjacency_matrix())
# plt.show()
