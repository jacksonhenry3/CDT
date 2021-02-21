"""Unittests for SpaceTime"""
import os
import pathlib
import tempfile

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

    SAMPLE_CONFIG_PICKLE = (b'\x80\x04\x95\xc7\x02\x00\x00\x00\x00\x00\x00\x8c\x10cdtea.space_time\x94\x8c\tSpaceTime\x94\x93\x94)\x81\x94}\x94(\x8c\x06closed\x94\x88'
                            b'\x8c\x05nodes\x94\x8f\x94(K\x00K\x01K\x02K\x03\x90\x8c\tnode_left\x94}\x94(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\nnode_right\x94}\x94(K\x00K\x01'
                            b'K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\tnode_past\x94}\x94(K\x00]\x94(K\x03K\x02eK\x01]\x94(K\x02K\x03eK\x02]\x94(K\x01K\x00eK\x03]\x94(K\x00K\x01e'
                            b'u\x8c\x0bnode_future\x94}\x94(K\x00]\x94(K\x02K\x03eK\x01]\x94(K\x03K\x02eK\x02]\x94(K\x00K\x01eK\x03]\x94(K\x01K\x00eu\x8c\x10faces_containin'
                            b'g\x94}\x94(K\x00]\x94((K\x00K\x01K\x03\x91\x94(K\x00K\x01K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x01K\x02\x91\x94('
                            b'K\x00K\x01K\x02\x91\x94eK\x01]\x94((K\x00K\x01K\x02\x91\x94(K\x00K\x01K\x02\x91\x94(K\x01K\x02K\x03\x91\x94(K\x01K\x02K\x03\x91\x94(K\x00K\x01K'
                            b'\x03\x91\x94(K\x00K\x01K\x03\x91\x94eK\x02]\x94((K\x01K\x02K\x03\x91\x94(K\x01K\x02K\x03\x91\x94(K\x00K\x01K\x02\x91\x94(K\x00K\x01K\x02\x91\x94(K'
                            b'\x00K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94eK\x03]\x94((K\x00K\x02K\x03\x91\x94(K\x00K\x02K\x03\x91\x94(K\x00K\x01K\x03\x91\x94(K\x00K\x01K\x03'
                            b'\x91\x94(K\x01K\x02K\x03\x91\x94(K\x01K\x02K\x03\x91\x94eu\x8c\x05faces\x94\x8f\x94(h)h\x1bh0h"\x90\x8c\x0cface_dilaton\x94}\x94(h\x1bJ\xff'
                            b'\xff\xff\xffh"J\xff\xff\xff\xffh)J\xff\xff\xff\xffh0J\xff\xff\xff\xffu\x8c\x06face_x\x94}\x94(h\x1b]\x94(h\x1e(K\x01K\x02K\x03\x91\x94eh"]\x94(h'
                            b'%(K\x00K\x02K\x03\x91\x94eh)]\x94(h,(K\x00K\x01K\x03\x91\x94eh0]\x94(h3(K\x00K\x01K\x02\x91\x94eu\x8c\x06face_t\x94}\x94(h\x1bh h"h\'h)h.h0h5u\x8c\x0fdead_references\x94\x8f\x94ub.')

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

    def test_to_pickle(self):
        """Test conversion of SpaceTime to pickle data"""
        st = dummy_space_time(2, 2)
        st_s = st.to_pickle()
        assert st_s == self.SAMPLE_CONFIG_PICKLE

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            st.to_pickle(path=path)
            assert os.path.exists(path.as_posix())  # check file written out

            with open(path.as_posix(), 'rb') as fid:
                content = fid.read()
                assert content == self.SAMPLE_CONFIG_PICKLE

    def test_from_pickle(self):
        """Test creation of SpaceTime from pickle"""
        st = dummy_space_time(2, 2)
        st_loaded = SpaceTime.from_pickle(data=self.SAMPLE_CONFIG_PICKLE)
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            with open(path.as_posix(), 'wb') as fid:
                fid.write(self.SAMPLE_CONFIG_PICKLE)
            st_loaded = SpaceTime.from_pickle(path=path)
            assert isinstance(st_loaded, SpaceTime)
            assert st_loaded == st
