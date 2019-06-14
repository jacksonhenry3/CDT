from cdt import *
from initialization import make_flat_spacetime
from vizualization import vizualize_space_time_2d
import matplotlib.pyplot as plt


# print(st_hist)
seed = 1
np.random.seed(seed)
st = make_flat_spacetime(64, 32)
dbg_interval = 10 ** 2
st_hist = run(st, 10 ** 3, 0.531, debug=True, debug_interval=dbg_interval)
vizualize_space_time_2d(st, seed)
