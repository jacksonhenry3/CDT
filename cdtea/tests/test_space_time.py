"""Unittests for SpaceTime"""

from cdtea.space_time import SpaceTime
from cdtea.space_time import generate_flat_spacetime


def dummy_space_time(spatial_size: int = 2, temporal_size: int = 1):
    """Helper function for creating SpaceTime for testing"""
    st = generate_flat_spacetime(spatial_size, temporal_size)
    return st


class TestSpaceTime:
    def test_dummy_space_time(self):
        """Coverage ftw"""
        dst = dummy_space_time()
        assert isinstance(dst, SpaceTime)
        assert len(dst.nodes) == 2

# Original Testing Code Below (commented out until migrated into unittests)
# this checks if in a flat space-time each node belongs to 6 simplices
# def is_flat(st):
#     for n in st.nodes:
#         if not (st.get_faces_containing(n) == st.faces_containing[n]):
#             return False
#     return True
#
#
# def is_valid_move(st, node, past, future):
#     pass
#
#
# # make sure there no duplicate faces or nodes
#
#
# def push_pop(st, node):
#     sub_space = st.pop(node)
#     st.push(sub_space)
#     # Check that this is the same as when starting
