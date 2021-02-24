"""Unittests for SpaceTime"""
import collections
import itertools
import os
import pathlib
import tempfile

import networkx
import pandas
import pytest

from cdtea import event, modifications, space_time
from cdtea.space_time import SpaceTime
from cdtea.tests import audit


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

    SAMPLE_CONFIG_DICT = {'closed': True,
                          'face_dilaton': {frozenset({0, 1, 3}): -1, frozenset({0, 1, 2}): -1, frozenset({1, 2, 3}): -1, frozenset({0, 2, 3}): -1},
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
                          'node_future': {0: {2, 3}, 1: {2, 3}, 2: {0, 1}, 3: {0, 1}},
                          'node_left': {0: 1, 1: 0, 2: 3, 3: 2},
                          'node_past': {0: {2, 3}, 1: {2, 3}, 2: {0, 1}, 3: {0, 1}},
                          'node_right': {0: 1, 1: 0, 2: 3, 3: 2},
                          'nodes': {0, 1, 2, 3}}

    SAMPLE_CONFIG_PICKLE = (b'\x80\x03ccdtea.space_time\nSpaceTime\nq\x00)\x81q\x01N}q\x02(X\x06\x00\x00\x00closedq\x03\x88X\x05\x00\x00\x00nodesq\x04cbuiltins\nset\nq\x05]'
                            b'q\x06(K\x00K\x01K\x02K\x03e\x85q\x07Rq\x08X\t\x00\x00\x00node_leftq\t}q\n(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\n\x00\x00\x00node_rightq\x0b'
                            b'}q\x0c(K\x00K\x01K\x01K\x00K\x02K\x03K\x03K\x02uX\t\x00\x00\x00node_pastq\r}q\x0e(K\x00h\x05]q\x0f(K\x02K\x03e\x85q\x10Rq\x11K\x01h\x05]q\x12('
                            b'K\x02K\x03e\x85q\x13Rq\x14K\x02h\x05]q\x15(K\x00K\x01e\x85q\x16Rq\x17K\x03h\x05]q\x18(K\x00K\x01e\x85q\x19Rq\x1auX\x0b\x00\x00\x00node_futureq\x1b'
                            b'}q\x1c(K\x00h\x05]q\x1d(K\x02K\x03e\x85q\x1eRq\x1fK\x01h\x05]q (K\x02K\x03e\x85q!Rq"K\x02h\x05]q#(K\x00K\x01e\x85q$Rq%K\x03h\x05]q&(K\x00K\x01e\x85q'
                            b"'Rq(uX\x10\x00\x00\x00faces_containingq)}q*(K\x00]q+(cbuiltins\nfrozenset\nq,]q-(K\x00K\x01K\x03e\x85q.Rq/h,]q0(K\x00K\x01K\x03e\x85q1Rq2h,]q3(K\x00"
                            b'K\x02K\x03e\x85q4Rq5h,]q6(K\x00K\x02K\x03e\x85q7Rq8h,]q9(K\x00K\x01K\x02e\x85q:Rq;h,]q<(K\x00K\x01K\x02e\x85q=Rq>eK\x01]q?(h,]q@(K\x00K'
                            b'\x01K\x02e\x85qARqBh,]qC(K\x00K\x01K\x02e\x85qDRqEh,]qF(K\x01K\x02K\x03e\x85qGRqHh,]qI(K\x01K\x02K\x03e\x85qJRqKh,]qL(K\x00K\x01K\x03e\x85qMR'
                            b'qNh,]qO(K\x00K\x01K\x03e\x85qPRqQeK\x02]qR(h,]qS(K\x01K\x02K\x03e\x85qTRqUh,]qV(K\x01K\x02K\x03e\x85qWRqXh,]qY(K\x00K\x01K\x02e\x85qZRq[h,]q\\(K'
                            b'\x00K\x01K\x02e\x85q]Rq^h,]q_(K\x00K\x02K\x03e\x85q`Rqah,]qb(K\x00K\x02K\x03e\x85qcRqdeK\x03]qe(h,]qf(K\x00K\x02K\x03e\x85qgRqhh,]qi(K\x00'
                            b'K\x02K\x03e\x85qjRqkh,]ql(K\x00K\x01K\x03e\x85qmRqnh,]qo(K\x00K\x01K\x03e\x85qpRqqh,]qr(K\x01K\x02K\x03e\x85qsRqth,]qu(K\x01K\x02K\x03e\x85qv'
                            b'RqweuX\x05\x00\x00\x00facesqxh\x05]qy(hUh/hhhBe\x85qzRq{X\x0c\x00\x00\x00face_dilatonq|}q}(h/J\xff\xff\xff\xffhBJ\xff\xff\xff\xffhUJ\xff\xff\xff\xffhh'
                            b'J\xff\xff\xff\xffuX\x06\x00\x00\x00face_xq~}q\x7f(h/]q\x80(h8h,]q\x81(K\x01K\x02K\x03e\x85q\x82Rq\x83ehB]q\x84(hKh,]q\x85(K\x00K\x02K\x03e\x85q\x86R'
                            b'q\x87ehU]q\x88(h^h,]q\x89(K\x00K\x01K\x03e\x85q\x8aRq\x8behh]q\x8c(hqh,]q\x8d(K\x00K\x01K\x02e\x85q\x8eRq\x8feuX\x06\x00\x00\x00face_tq\x90}q\x91(h/h>hBhQhUhdhhhwuu\x86q\x92b.')

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
        st = space_time.generate_flat_spacetime(2, 2)
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

    def test_to_networkx(self):
        """Test conversion to networkx"""
        st = space_time.generate_flat_spacetime(2, 2)
        G = st.to_networkx()
        assert isinstance(G, networkx.Graph)
