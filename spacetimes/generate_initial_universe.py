from core import cdt, space_time
import pickle as pkl

st = space_time.space_time()
st.generate_flat(32, 32)
st = cdt.run(st, 10 ** 6, 0.605, debug=True)

st.save("small_square_2")
