"""Unittests for SpaceTime"""
import collections
import itertools
import os
import pathlib
import tempfile
import sys

import networkx
import pandas
import pytest

from cdtea import event, moves, space_time
from cdtea.space_time import SpaceTime
from cdtea.tests import audit
from cdtea.space_time import generate_flat_spacetime

PY_VERSION = sys.version_info


class TestSpaceTime:
    """Test SpaceTime classes"""

    def test_pop(self):
        dst = space_time.generate_flat_spacetime(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        assert isinstance(dst2, SpaceTime)

    def test_push(self):
        dst = space_time.generate_flat_spacetime(3, 3)
        e0 = event.Event(dst, 0)
        dst2 = dst.pop([e0])
        dst.push(dst2)
        # TODO add real equivalence check
        assert isinstance(dst, SpaceTime)

    def test_equality(self):
        """Test equality"""
        dst = space_time.generate_flat_spacetime(3, 3)
        dst_2 = space_time.generate_flat_spacetime(3, 3)
        assert dst == dst_2

        e4 = event.Event(dst, 4)
        sub_dst = dst.pop([e4])
        assert dst != dst_2

    def test_pop_push_unique(self):
        """Test for temporal connection uniqueness, based on Jackson's repro 2021-02-21"""
        st = space_time.generate_flat_spacetime(10, 10)
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        dups = audit.find_duplicate_temporal_connections(st)
        assert dups is None

    def test_push_pop_identity(self):
        """Test that push * pop == identity"""
        base = space_time.generate_flat_spacetime(10, 10)  # to compare against
        st = space_time.generate_flat_spacetime(10, 10)
        assert base == st
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        assert base == st

    def test_push_pop_gluing_points(self):
        st = space_time.generate_flat_spacetime(10, 10)
        node = event.Event(st, 13)
        st.push(st.pop([node]))
        gp_nodes, gp_refs = audit.find_gluing_point_references(st)
        assert gp_nodes == []
        assert gp_refs == []


class TestSpaceTimeSerialize:
    """Serialization tests for spacetime class"""

    SAMPLE_CONFIG_DICT = {'closed': True, 'nodes': {0, 1, 2, 3}, 'node_left': {0: 1, 1: 0, 2: 3, 3: 2}, 'node_right': {0: 1, 1: 0, 2: 3, 3: 2},
                          'node_past': {0: {2, 3}, 1: {2, 3}, 2: {0, 1}, 3: {0, 1}}, 'node_future': {0: {2, 3}, 1: {2, 3}, 2: {0, 1}, 3: {0, 1}},
                          'faces_containing': {0: {0, 1, 2, 5, 6, 7}, 1: {0, 2, 3, 4, 5, 7}, 2: {1, 2, 3, 4, 5, 6}, 3: {0, 1, 3, 4, 6, 7}}, 'faces': {0, 1, 2, 3, 4, 5, 6, 7},
                          'face_dilaton': {0: 1, 1: -1, 2: 1, 3: -1, 4: 1, 5: -1, 6: 1, 7: -1}, 'face_left': {0: 1, 1: 2, 2: 3, 3: 0, 4: 5, 5: 6, 6: 7, 7: 4},
                          'face_right': {0: 3, 1: 0, 2: 1, 3: 2, 4: 7, 5: 4, 6: 5, 7: 6}, 'face_t': {0: 5, 1: 4, 2: 7, 3: 6, 4: 1, 5: 0, 6: 3, 7: 2},
                          'face_type': {0: 0, 1: 1, 2: 0, 3: 1, 4: 0, 5: 1, 6: 0, 7: 1},
                          'face_nodes': {0: frozenset({0, 1, 3}), 1: frozenset({0, 2, 3}), 2: frozenset({0, 1, 2}), 3: frozenset({1, 2, 3}), 4: frozenset({1, 2, 3}),
                                         5: frozenset({0, 1, 2}), 6: frozenset({0, 2, 3}), 7: frozenset({0, 1, 3})}}

    SAMPLE_CONFIG_PICKLE_38 = (b'\x80\x04\x95\xf1\x02\x00\x00\x00\x00\x00\x00\x8c\x10cdtea.space_time\x94\x8c\tSpaceTime\x94\x93\x94)\x81\x94N}\x94('
                               b'\x8c\x0e_ordered_nodes\x94N\x8c\x06closed\x94\x88\x8c\x05nodes\x94\x8f\x94(K\x00K\x01K\x02K\x03\x90\x8c\tnode_left\x94}\x94('
                               b'K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\nnode_right\x94}\x94(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02u\x8c\tnode_past\x94}\x94('
                               b'K\x00\x8f\x94('
                               b'K\x02K\x03\x90K\x01\x8f\x94(K\x02K\x03\x90K\x02\x8f\x94(K\x00K\x01\x90K\x03\x8f\x94(K\x00K\x01\x90u\x8c\x0bnode_future\x94}\x94(K\x00\x8f\x94('
                               b'K\x02K\x03\x90K\x01\x8f\x94(K\x02K\x03\x90K\x02\x8f\x94(K\x00K\x01\x90K\x03\x8f\x94(K\x00K\x01\x90u\x8c\x10faces_containing\x94}\x94('
                               b'K\x00\x8f\x94('
                               b'K\x00K\x01K\x02K\x05K\x06K\x07\x90K\x01\x8f\x94(K\x00K\x02K\x03K\x04K\x05K\x07\x90K\x02\x8f\x94(K\x01K\x02K\x03K\x04K\x05K\x06\x90K\x03\x8f\x94('
                               b'K\x00K\x01K\x03K\x04K\x06K\x07\x90u\x8c\x05faces\x94\x8f\x94(K\x00K\x01K\x02K\x03K\x04K\x05K\x06K\x07\x90\x8c\x0cface_dilaton\x94}\x94('
                               b'K\x00K\x01K\x01J\xff\xff\xff\xffK\x02K\x01K\x03J\xff\xff\xff\xffK\x04K\x01K\x05J\xff\xff\xff\xffK\x06K\x01K\x07J\xff\xff\xff\xffu\x8c\tface_left'
                               b'\x94}\x94('
                               b'K\x00K\x01K\x01K\x02K\x02K\x03K\x03K\x00K\x04K\x05K\x05K\x06K\x06K\x07K\x07K\x04u\x8c\nface_right\x94}\x94('
                               b'K\x00K\x03K\x01K\x00K\x02K\x01K\x03K\x02K\x04K\x07K\x05K\x04K\x06K\x05K\x07K\x06u\x8c\x06face_t\x94}\x94('
                               b'K\x00K\x05K\x01K\x04K\x02K\x07K\x03K\x06K\x04K\x01K\x05K\x00K\x06K\x03K\x07K\x02u\x8c\tface_type\x94}\x94('
                               b'K\x00K\x00K\x01K\x01K\x02K\x00K\x03K\x01K\x04K\x00K\x05K\x01K\x06K\x00K\x07K\x01u\x8c\nface_nodes\x94}\x94(K\x00(K\x00K\x01K\x03\x91\x94K\x01('
                               b'K\x00K\x02K\x03\x91\x94K\x02(K\x00K\x01K\x02\x91\x94K\x03(K\x01K\x02K\x03\x91\x94K\x04(K\x01K\x02K\x03\x91\x94K\x05(K\x00K\x01K\x02\x91\x94K\x06('
                               b'K\x00K\x02K\x03\x91\x94K\x07(K\x00K\x01K\x03\x91\x94uu\x86\x94b.')

    SAMPLE_CONFIG_PICKLE_37 = (b'\x80\x03ccdtea.space_time\nSpaceTime\nq\x00)\x81q\x01N}q\x02('
                               b'X\x0e\x00\x00\x00_ordered_nodesq\x03NX\x06\x00\x00\x00closedq\x04\x88X\x05\x00\x00\x00nodesq\x05cbuiltins\nset\nq\x06]q\x07('
                               b'K\x00K\x01K\x02K\x03e\x85q\x08Rq\tX\t\x00\x00\x00node_leftq\n}q\x0b(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\n\x00\x00\x00node_rightq\x0c}q\r('
                               b'K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\t\x00\x00\x00node_pastq\x0e}q\x0f(K\x00h\x06]q\x10(K\x02K\x03e\x85q\x11Rq\x12K\x01h\x06]q\x13('
                               b'K\x02K\x03e\x85q\x14Rq\x15K\x02h\x06]q\x16(K\x00K\x01e\x85q\x17Rq\x18K\x03h\x06]q\x19('
                               b'K\x00K\x01e\x85q\x1aRq\x1buX\x0b\x00\x00\x00node_futureq\x1c}q\x1d('
                               b'K\x00h\x06]q\x1e(K\x02K\x03e\x85q\x1fRq K\x01h\x06]q!(K\x02K\x03e\x85q"Rq#K\x02h\x06]q$(K\x00K\x01e\x85q%Rq&K\x03h\x06]q\'(K\x00K\x01e\x85q('
                               b'Rq)uX\x10\x00\x00\x00faces_containingq*}q+(K\x00h\x06]q,(K\x00K\x01K\x02K\x05K\x06K\x07e\x85q-Rq.K\x01h\x06]q/('
                               b'K\x00K\x02K\x03K\x04K\x05K\x07e\x85q0Rq1K\x02h\x06]q2('
                               b'K\x01K\x02K\x03K\x04K\x05K\x06e\x85q3Rq4K\x03h\x06]q5(K\x00K\x01K\x03K\x04K\x06K\x07e\x85q6Rq7uX\x05\x00\x00\x00facesq8h\x06]q9('
                               b'K\x00K\x01K\x02K\x03K\x04K\x05K\x06K\x07e\x85q:Rq;X\x0c\x00\x00\x00face_dilatonq<}q=('
                               b'K\x00K\x01K\x01J\xff\xff\xff\xffK\x02K\x01K\x03J\xff\xff\xff\xffK\x04K\x01K\x05J\xff\xff\xff\xffK\x06K\x01K\x07J\xff\xff\xff\xffuX\t\x00\x00'
                               b'\x00face_leftq>}q?('
                               b'K\x00K\x01K\x01K\x02K\x02K\x03K\x03K\x00K\x04K\x05K\x05K\x06K\x06K\x07K\x07K\x04uX\n\x00\x00\x00face_rightq@}qA('
                               b'K\x00K\x03K\x01K\x00K\x02K\x01K\x03K\x02K\x04K\x07K\x05K\x04K\x06K\x05K\x07K\x06uX\x06\x00\x00\x00face_tqB}qC('
                               b'K\x00K\x05K\x01K\x04K\x02K\x07K\x03K\x06K\x04K\x01K\x05K\x00K\x06K\x03K\x07K\x02uX\t\x00\x00\x00face_typeqD}qE('
                               b'K\x00K\x00K\x01K\x01K\x02K\x00K\x03K\x01K\x04K\x00K\x05K\x01K\x06K\x00K\x07K\x01uX\n\x00\x00\x00face_nodesqF}qG(K\x00cbuiltins\nfrozenset\nqH]qI('
                               b'K\x00K\x01K\x03e\x85qJRqKK\x01hH]qL(K\x00K\x02K\x03e\x85qMRqNK\x02hH]qO(K\x00K\x01K\x02e\x85qPRqQK\x03hH]qR(K\x01K\x02K\x03e\x85qSRqTK\x04hH]qU('
                               b'K\x01K\x02K\x03e\x85qVRqWK\x05hH]qX(K\x00K\x01K\x02e\x85qYRqZK\x06hH]q[(K\x00K\x02K\x03e\x85q\\Rq]K\x07hH]q^(K\x00K\x01K\x03e\x85q_Rq`uu\x86qab.')

    def _sample_pickle(self):
        if PY_VERSION.major != 3 or PY_VERSION.minor not in (7, 8):
            raise NotImplementedError('Unsupported Python Version: {}. Supported options 3.7, 3.8'.format(str(PY_VERSION)))
        return {(3, 8): self.SAMPLE_CONFIG_PICKLE_38, (3, 7): self.SAMPLE_CONFIG_PICKLE_37, }[(PY_VERSION.major, PY_VERSION.minor)]

    def test_to_dict(self):
        """Test serialization to dict"""
        st = space_time.generate_flat_spacetime(2, 2)
        config_dict = st.to_dict()
        assert config_dict == self.SAMPLE_CONFIG_DICT

    def test_from_dict(self):
        """Load SpaceTime from dictionary"""
        st_loaded = SpaceTime.from_dict(config_dict=self.SAMPLE_CONFIG_DICT)
        st = space_time.generate_flat_spacetime(2, 2)
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        # Test incomplete dict raises error
        incomplete_dict = self.SAMPLE_CONFIG_DICT.copy()
        incomplete_dict.pop('nodes')
        with pytest.raises(space_time.SerializationError):
            SpaceTime.from_dict(incomplete_dict)

    def test_to_pickle(self):
        """Test conversion of SpaceTime to pickle data"""
        st = space_time.generate_flat_spacetime(2, 2)
        st_s = st.to_pickle()
        assert st_s == self._sample_pickle()

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            st.to_pickle(path=path)
            assert os.path.exists(path.as_posix())  # check file written out

            with open(path.as_posix(), 'rb') as fid:
                content = fid.read()
                assert content == self._sample_pickle()

    def test_from_pickle(self):
        """Test creation of SpaceTime from pickle"""
        st = space_time.generate_flat_spacetime(2, 2)
        st_loaded = SpaceTime.from_pickle(data=self._sample_pickle())
        assert isinstance(st_loaded, SpaceTime)
        assert st_loaded == st

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'test_to_pickle.pkl'
            with open(path.as_posix(), 'wb') as fid:
                fid.write(self._sample_pickle())
            st_loaded = SpaceTime.from_pickle(path=path)
            assert isinstance(st_loaded, SpaceTime)
            assert st_loaded == st

    def test_to_networkx(self):
        """Test conversion to networkx"""
        st = space_time.generate_flat_spacetime(2, 2)
        G = st.to_networkx()
        assert isinstance(G, networkx.Graph)
