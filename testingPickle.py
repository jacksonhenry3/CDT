import pickle as pkl
import space_time
from cdt import run


st = space_time.space_time()
st.generate_flat(64,64)
st = run(st, 10**5, .62)

# with open('64x64_10moves_lambda.62', 'wb') as file:
#     pkl.dump(st, file)
#
# # Step 2
# with open('64x64_10moves_lambda.62', 'rb') as file:
#
#     # Step 3
#     config_dictionary = pkl.load(file)
#
#     # After config_dictionary is read from file
#     print(config_dictionary.nodes)
