from core.cdt import *
from core.space_time import *
from vizualization.visualize3d import visualize3d

st = space_time()
st.generate_flat(32, 32)
st.move(st.get_random_node())
visualize3d(st)

st = space_time()
st.generate_flat(32, 32)
st.inverse_move(st.get_random_node())
visualize3d(st)

st = space_time()
st.generate_flat(32, 32)
run(st, 5000, 0.6)
visualize3d(st)
