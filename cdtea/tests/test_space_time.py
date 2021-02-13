"""Unittests for SpaceTime"""

from cdtea.SpaceTime import SpaceTime


def dummy_space_time(spatial_size: int = 2, temporal_size: int = 1):
    """Helper function for creating SpaceTime for testing"""
    st = SpaceTime()
    st.generate_flat(space_size=spatial_size, time_size=temporal_size)
    return st


class TestSpaceTime:
    def test_dummy_space_time(self):
        """Coverage ftw"""
        dst = dummy_space_time()
        assert isinstance(dst, SpaceTime)
        assert len(dst.nodes) == 2
