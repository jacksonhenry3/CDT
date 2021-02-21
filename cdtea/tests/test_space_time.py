"""Unittests for SpaceTime"""
import pytest

from cdtea import event, modifications, space_time
from cdtea.space_time import SpaceTime
from cdtea.space_time import generate_flat_spacetime


def dummy_space_time(spatial_size: int = 2, temporal_size: int = 1):
    """Helper function for creating SpaceTime for testing"""
    st = generate_flat_spacetime(spatial_size, temporal_size)
    return st


class TestSpaceTime:
    """Test SpaceTime classes"""

    def test_dummy_space_time(self):
        """Coverage ftw"""
        dst = dummy_space_time()
        assert isinstance(dst, SpaceTime)
        assert len(dst.nodes) == 2

    def test_pop(self):
        dst = dummy_space_time(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        assert isinstance(dst2, SpaceTime)

    def test_push(self):
        dst = dummy_space_time(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        dst.push(dst2)
        # TODO add real equivalence check
        assert isinstance(dst, SpaceTime)

    def test_equality(self):
        """Test equality"""
        dst = dummy_space_time(3, 3)
        dst_2 = dummy_space_time(3, 3)
        assert dst == dst_2

        e4 = event.Event(dst, 4)
        sub_dst = dst.pop([e4])
        assert dst != dst_2


class TestSpaceTimeSerialize:
    """Serialization tests for spacetime class"""

    SAMPLE_CONFIG_DICT = {'closed': True, 'dead_references': set(),
                          'face_dilation': {frozenset({0, 1, 3}): -1, frozenset({0, 1, 2}): -1, frozenset({1, 2, 3}): -1, frozenset({0, 2, 3}): -1},
                          'face_t': {frozenset({0, 1, 3}): frozenset({0, 1, 2}), frozenset({0, 1, 2}): frozenset({0, 1, 3}), frozenset({1, 2, 3}): frozenset({0, 2, 3}),
                                     frozenset({0, 2, 3}): frozenset({1, 2, 3})},
                          'face_x': {frozenset({0, 1, 3}): [frozenset({0, 2, 3}), frozenset({1, 2, 3})], frozenset({0, 1, 2}): [frozenset({1, 2, 3}), frozenset({0, 2, 3})],
                                     frozenset({1, 2, 3}): [frozenset({0, 1, 2}), frozenset({0, 1, 3})], frozenset({0, 2, 3}): [frozenset({0, 1, 3}), frozenset({0, 1, 2})]},
                          'faces': {frozenset({1, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 2})},
                          'faces_containing': {
                              0: [frozenset({0, 1, 3}), frozenset({0, 1, 3}), frozenset({0, 2, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 2}), frozenset({0, 1, 2})],
                              1: [frozenset({0, 1, 2}), frozenset({0, 1, 2}), frozenset({1, 2, 3}), frozenset({1, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 1, 3})],
                              2: [frozenset({1, 2, 3}), frozenset({1, 2, 3}), frozenset({0, 1, 2}), frozenset({0, 1, 2}), frozenset({0, 2, 3}), frozenset({0, 2, 3})],
                              3: [frozenset({0, 2, 3}), frozenset({0, 2, 3}), frozenset({0, 1, 3}), frozenset({0, 1, 3}), frozenset({1, 2, 3}), frozenset({1, 2, 3})]},
                          'node_future': {0: [2, 3], 1: [3, 2], 2: [0, 1], 3: [1, 0]},
                          'node_left': {0: 1, 1: 0, 2: 3, 3: 2},
                          'node_past': {0: [3, 2], 1: [2, 3], 2: [1, 0], 3: [0, 1]},
                          'node_right': {0: 1, 1: 0, 2: 3, 3: 2},
                          'nodes': {0, 1, 2, 3}}

    def test_to_dict(self):
        """Test serialization to dict"""
        st = dummy_space_time(2, 2)
        config_dict = st.to_dict()
        assert config_dict == self.SAMPLE_CONFIG_DICT

    def test_from_dict(self):
        """Load SpaceTime from dictionary"""
        st_loaded = SpaceTime.from_dict(config_dict=self.SAMPLE_CONFIG_DICT)
        st = dummy_space_time(2, 2)
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        # Test incomplete dict raises error
        incomplete_dict = self.SAMPLE_CONFIG_DICT.copy()
        incomplete_dict.pop('nodes')
        with pytest.raises(space_time.SerializationError):
            SpaceTime.from_dict(incomplete_dict)
