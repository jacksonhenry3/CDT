import space_time
from node import node
import vizualization

from unit_tests.has_neighbors import all_have_neighbors

st = space_time.space_time()

st.generate_flat(50, 50)

if all_have_neighbors(st):
    print("passed!")
    vizualization.vizualize_space_time_2d(st)
else:
    print("Failed neighbors Tests")
